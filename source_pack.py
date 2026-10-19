#!/usr/bin/env python3
"""Export checked public release feeds to AIHOT's industry/sources.json format."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
import math
import re
import os
import tempfile
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MANIFEST = Path(__file__).parent / "sources.json"
ERRORS = {
    "en": "Invalid source manifest or topic.",
    "fr": "Manifeste de sources ou thème invalide.",
    "es": "Manifiesto de fuentes o tema no válido.",
}
ATOM = "{http://www.w3.org/2005/Atom}"
LABELS = {
    "en": ("sources", "valid", "invalid"),
    "fr": ("sources", "valides", "invalides"),
    "es": ("fuentes", "válidas", "inválidas"),
}
AGE_LABELS = {
    'fr': {'fresh': 'récent', 'stale': 'ancien', 'unknown_date': 'date inconnue', 'empty': 'flux vide', 'future_timestamp': 'date future incohérente'},
    'en': {'fresh': 'recent', 'stale': 'stale', 'unknown_date': 'unknown date', 'empty': 'empty feed', 'future_timestamp': 'inconsistent future date'},
    'es': {'fresh': 'reciente', 'stale': 'antiguo', 'unknown_date': 'fecha desconocida', 'empty': 'flujo vacío', 'future_timestamp': 'fecha futura incoherente'},
}


def load_sources(path=MANIFEST):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("source manifest must be an array")
    ids = set()
    for source in data:
        if not isinstance(source, dict) or not all(k in source for k in ("id", "name", "repo", "topic")):
            raise ValueError("every source needs id, name, repo and topic")
        if not all(isinstance(source[k], str) and source[k].strip() for k in ("id", "name", "repo")):
            raise ValueError("invalid_source_fields")
        if source["id"] in ids or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source["repo"]):
            raise ValueError("duplicate source id or invalid repository")
        if not isinstance(source["topic"], list) or not source["topic"] or not all(isinstance(x, str) and x for x in source["topic"]):
            raise ValueError("every source needs at least one topic")
        ids.add(source["id"])
    return data


def export(sources, topic="all"):
    if topic != "all":
        sources = [s for s in sources if topic in s["topic"]]
    return {"sources": [
        {"id": s["id"], "name": s["name"], "kind": "rss",
         "config": {"feedUrl": f"https://github.com/{s['repo']}/releases.atom", "_aihot": {"initialBackfillLimit": 5}},
         "tier": "T1", "first_party": True, "owner_entity_id": s["repo"].split("/")[0],
         "participation_mode": "editorial", "interval_minutes": 180,
          "tags": list(s["topic"]), "site_fulltext": False, "syndicate_fulltext": False}
        for s in sources]}


def inspect_atom(content, max_age_days=None, timestamp_field='updated', now=None):
    if not isinstance(content, bytes) or len(content) > 1_000_000:
        raise ValueError("invalid_feed_size")
    root = ET.fromstring(content)
    if root.tag != ATOM + "feed":
        raise ValueError("not_atom_feed")
    entries = root.findall(ATOM + "entry")
    result = {"valid": True, "entry_count": len(entries), "content_sha256": hashlib.sha256(content).hexdigest()}
    if max_age_days is not None:
        if type(max_age_days) not in (int, float) or not math.isfinite(max_age_days) or max_age_days <= 0 or timestamp_field not in ('published', 'updated'):
            raise ValueError('invalid_freshness_policy')
        clock = now or datetime.now(timezone.utc)
        if not isinstance(clock, datetime) or clock.tzinfo is None or clock.utcoffset() is None:
            raise ValueError('timezone_qualified_clock_required')
        dates = []
        for entry in entries:
            value = entry.findtext(ATOM + timestamp_field)
            try:
                date = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
                if date.tzinfo is None or date.utcoffset() is None:
                    raise ValueError('naive_entry_date')
                dates.append(date.astimezone(timezone.utc))
            except (ValueError, TypeError, AttributeError):
                continue
        latest = max(dates) if dates else None
        age = (clock - latest).total_seconds() / 86400 if latest else None
        if not entries:
            status = 'empty'
        elif latest and age < -300 / 86400:
            status = 'future_timestamp'
        elif latest and age <= max_age_days:
            status = 'fresh'
        elif len(dates) != len(entries):
            status = 'unknown_date'
        else:
            status = 'stale'
        result.update(freshness_status=status, freshness_basis=timestamp_field,
                      latest_entry_at=latest.isoformat() if latest else None,
                      dated_entries=len(dates), undated_entries=len(entries)-len(dates),
                      age_days=max(0, age) if age is not None else None,
                      max_age_days=max_age_days, policy_passed=status == 'fresh')
    return result


def feed_receipt(url, timeout=12, max_age_days=None, timestamp_field='updated'):
    observed = datetime.now(timezone.utc).isoformat()
    result = {"url": url, "observed_at": observed, "valid": False}
    if max_age_days is not None:
        result['policy_passed'] = False
    try:
        response = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https", "--max-time", str(timeout), "--max-filesize", "1000000", url], capture_output=True, timeout=timeout + 2)
        if response.returncode:
            result["error_code"] = "transport_failed"
        else:
            result.update(inspect_atom(response.stdout, max_age_days=max_age_days, timestamp_field=timestamp_field))
    except (OSError, subprocess.TimeoutExpired):
        result["error_code"] = "transport_failed"
    except (ET.ParseError, ValueError):
        result["error_code"] = "invalid_atom"
    return result


def check_feed(url, timeout=12):
    return feed_receipt(url, timeout)["valid"]


def write_export(data, path):
    """Publish a complete UTF8 export without replacing an existing destination."""
    path = Path(path)
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=".source-pack-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("export", "validate", "preview", "check-live"))
    parser.add_argument("--topic", default="all")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--lang", choices=LABELS, default="en")
    parser.add_argument("--json", action="store_true")
    parser.add_argument('--max-age-days', type=float, help='Âge maximal des entrées / Maximum entry age / Edad máxima de entradas')
    parser.add_argument('--timestamp-field', choices=('updated', 'published'), default='updated', help='Champ de date des entrées / Entry timestamp field / Campo de fecha de entradas')
    parser.add_argument("--output", type=Path, help="FR : export exclusif dans un fichier / EN: exclusive file export / ES: exportación exclusiva a archivo")
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.command != "export":
            raise ValueError("output_requires_export")
        if args.max_age_days is not None and (args.command != 'check-live' or not math.isfinite(args.max_age_days) or args.max_age_days <= 0):
            raise ValueError('freshness_requires_check_live_and_positive_age')
        sources = load_sources(args.manifest)
        topics = {topic for source in sources for topic in source["topic"]}
        if args.topic != "all" and args.topic not in topics:
            raise ValueError("unknown_topic")
        data = export(sources, args.topic)
        if args.command == "export":
            if args.output is not None:
                write_export(data, args.output)
            else:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        if args.command == "preview":
            for source in sources:
                if args.topic == "all" or args.topic in source["topic"]:
                    print(f"{source['id']} [{', '.join(source['topic'])}] -> https://github.com/{source['repo']}/releases.atom")
            return 0
        if args.command == "validate":
            print(f"{len(data['sources'])} {LABELS[args.lang][0]}, {LABELS[args.lang][1]}")
            return 0
        results = [dict(feed_receipt(s["config"]["feedUrl"], max_age_days=args.max_age_days, timestamp_field=args.timestamp_field), id=s["id"]) for s in data["sources"]]
        accepted = all(row.get('policy_passed', row['valid']) for row in results)
        if args.json:
            print(json.dumps({"sources": results, "valid": accepted}, ensure_ascii=False, indent=2))
        else:
            for row in results:
                label = AGE_LABELS[args.lang][row['freshness_status']] if row['valid'] and 'freshness_status' in row else LABELS[args.lang][1] if row['valid'] else LABELS[args.lang][2]
                print(f"{row['id']}: {label}")
        return 0 if accepted else 1
    except (OSError, ValueError, TypeError) as error:
        print(ERRORS[args.lang], file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
