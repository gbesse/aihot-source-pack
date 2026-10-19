"""Synthetic timestamp-policy comparison without a network request."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_pack import inspect_atom

raw = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><published>2020-01-01T00:00:00Z</published><updated>2026-10-19T11:00:00Z</updated></entry></feed>'
now = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
print(json.dumps({'synthetic': True, 'description': {'fr': 'Une ancienne publication modifiée récemment : activité récente, publication ancienne.', 'en': 'An old publication edited recently: recent activity, old publication.', 'es': 'Una publicación antigua editada recientemente: actividad reciente, publicación antigua.'}, 'updated_basis': inspect_atom(raw, 30, 'updated', now), 'published_basis': inspect_atom(raw, 30, 'published', now)}, ensure_ascii=False, indent=2))
