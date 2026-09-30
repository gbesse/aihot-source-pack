#!/usr/bin/env python3
"""Export checked public release feeds to AIHOT's industry/sources.json format."""
import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MANIFEST = Path(__file__).parent / "sources.json"
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
         "tags": [s["topic"][0]], "site_fulltext": False, "syndicate_fulltext": False}
        for s in sources]}


def check_feed(url, timeout=12):
    try:
        response = subprocess.run(["curl", "-fsSL", "--max-time", str(timeout), "--max-filesize", "1000000", url], capture_output=True, timeout=timeout + 2)
        if response.returncode:
            return False
        root = ET.fromstring(response.stdout)
        return root.tag.endswith("feed") or root.tag.endswith("rss")
    except (OSError, subprocess.TimeoutExpired, ET.ParseError, ValueError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("export", "validate", "check-live"))
    parser.add_argument("--topic", default="all")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--lang", choices=LABELS, default="en")
    args = parser.parse_args(argv)
    try:
        sources = load_sources(args.manifest)
        topics = {topic for source in sources for topic in source["topic"]}
        if args.topic != "all" and args.topic not in topics:
            parser.error("unknown topic: " + args.topic)
        data = export(sources, args.topic)
        if args.command == "export":
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        if args.command == "validate":
            print(f"{len(data['sources'])} {LABELS[args.lang][0]}, {LABELS[args.lang][1]}")
            return 0
        results = [(s["id"], check_feed(s["config"]["feedUrl"])) for s in data["sources"]]
        for name, okay in results:
            print(f"{name}: {'OK' if okay else 'FAIL'}")
        return 0 if all(okay for _, okay in results) else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
