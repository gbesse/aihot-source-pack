#!/usr/bin/env python3
"""Export checked public release feeds to AIHOT's industry/sources.json format."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
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


def inspect_atom(content):
    if not isinstance(content, bytes) or len(content) > 1_000_000:
        raise ValueError("invalid_feed_size")
    root = ET.fromstring(content)
    if root.tag != ATOM + "feed":
        raise ValueError("not_atom_feed")
    entries = root.findall(ATOM + "entry")
    return {"valid": True, "entry_count": len(entries), "content_sha256": hashlib.sha256(content).hexdigest()}


def feed_receipt(url, timeout=12):
    observed = datetime.now(timezone.utc).isoformat()
    result = {"url": url, "observed_at": observed, "valid": False}
    try:
        response = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https", "--max-time", str(timeout), "--max-filesize", "1000000", url], capture_output=True, timeout=timeout + 2)
        if response.returncode:
            result["error_code"] = "transport_failed"
        else:
            result.update(inspect_atom(response.stdout))
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
    parser.add_argument("--output", type=Path, help="FR : export exclusif dans un fichier / EN: exclusive file export / ES: exportación exclusiva a archivo")
    args = parser.parse_args(argv)
    try:
        if args.output is not None and args.command != "export":
            raise ValueError("output_requires_export")
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
        results = [dict(feed_receipt(s["config"]["feedUrl"]), id=s["id"]) for s in data["sources"]]
        if args.json:
            print(json.dumps({"sources": results, "valid": all(row["valid"] for row in results)}, ensure_ascii=False, indent=2))
        else:
            for row in results:
                print(f"{row['id']}: {LABELS[args.lang][1] if row['valid'] else LABELS[args.lang][2]}")
        return 0 if all(row["valid"] for row in results) else 1
    except (OSError, ValueError, TypeError) as error:
        print(ERRORS[args.lang], file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
