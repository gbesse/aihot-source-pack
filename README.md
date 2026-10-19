# AIHOT Source Pack

**Start an AIHOT instance with public release feeds you can inspect and import.**

[English](README.md) · [Français](README.fr.md) · [Español](README.es.md)

## Related projects

- [AIHOT](https://github.com/KKKKhazix/AIHOT) — Imports the JSON source format on first startup; this pack is independent.
- [Source request #13](https://github.com/KKKKhazix/AIHOT/issues/13) — Asks for usable sources beyond the demonstration list.
- [AIHOT source format](https://github.com/KKKKhazix/AIHOT/blob/main/industry/sources.json) — The exact example schema matched by this exporter.

Links describe technical neighbors, not an affiliation.

## Try it

```sh
python3 source_pack.py validate --lang en
```

## What this checks

Exports ten official GitHub release Atom feeds in AIHOT’s `industry/sources.json` schema. Filter by `agents`, `memory`, `retrieval`, or `protocols`; `check-live` verifies each feed with TLS and XML parsing.

Run `python3 source_pack.py preview --topic memory` to inspect feed IDs, topics and exact Atom URLs before export. Preview reads only the bundled manifest; it performs no network request.

## Use with your data

```sh
python3 source_pack.py export --topic memory > sources.generated.json
python3 source_pack.py check-live --topic memory
```

Review `sources.generated.json`, merge the entries you want into a fresh AIHOT instance’s `industry/sources.json`, then run AIHOT’s seed process. The alpha export has been validated against the published schema, not against a running AIHOT import.

## Scope and limits

Ten GitHub release feeds only. This is not AIHOT’s private production source list. Feed availability changes; `check-live` is a point-in-time check. No article content is copied.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

MIT · v0.3.1

## Multiple topics

A source can list several topics in `sources.json`; `export` now preserves every topic in its AIHOT `tags`. Run `python3 source_pack.py export` to inspect the JSON offline.

## Contrôle d’adoption · Adoption check · Comprobación de adopción

[Français : essayer un cas concret](examples/adoption-check.md) · [English: try a concrete case](examples/adoption-check.md) · [Español: pruebe un caso concreto](examples/adoption-check.md).

## Inspectable feed checks

`python3 source_pack.py check-live --topic memory --json` emits one receipt per feed: observation time, exact Atom namespace validation, entry count and SHA256 of the received bytes. Empty feeds are valid with zero entries. A hash identifies this capture; it is not a signature, proof of release quality or evidence of human adoption. XML with a misleading `*feed` suffix is rejected. HTTPS is required for the request and redirects. Failed checks contain generic error codes, without transport stderr. Strict string fields also prevent malformed manifests from crashing before validation.


Export a complete file without replacing existing configuration: `python3 source_pack.py export --topic memory --lang en --output sources-export.json`. The UTF8 file is published in one step with mode 600; an existing or unavailable destination fails with exit 2 and remains unchanged. Without `--output`, existing stdout behavior remains. This option belongs only to `export` and performs no remote import.

## Valid feed does not mean recent activity

`check-live --max-age-days 90` adds an Atom-entry age policy. Default `--timestamp-field updated` measures edit activity, not necessarily a new publication; choose `published` to require that field without silent fallback. Receipts distinguish recent, stale, unknown date, empty feed and inconsistent future date. Timestamps require timezones; feed-level dates never replace entry dates. Dates over five minutes in the future fail. Structurally valid XML that fails policy exits 1. Omitting an age limit preserves structural validation. Publisher-declared dates establish neither quality nor human adoption.

```sh
python3 source_pack.py check-live --topic memory --max-age-days 90 --timestamp-field updated --lang en --json
python3 examples/feed-freshness.py
```

The second command compares an old release edited recently, using an offline synthetic feed and clock. New tests make no remote requests.
