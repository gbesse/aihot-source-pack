import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
from unittest.mock import patch
from source_pack import inspect_atom, main

NOW = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
def feed(entries): return ('<feed xmlns="http://www.w3.org/2005/Atom">'+entries+'</feed>').encode()

class FreshnessTests(unittest.TestCase):
    def test_entry_updated_and_published_have_explicit_different_meanings(self):
        raw=feed('<entry><published>2020-01-01T00:00:00Z</published><updated>2026-10-19T11:00:00Z</updated></entry>')
        self.assertTrue(inspect_atom(raw,30,'updated',NOW)['policy_passed'])
        self.assertEqual(inspect_atom(raw,30,'published',NOW)['freshness_status'],'stale')
    def test_root_updated_cannot_make_an_old_or_undated_entry_fresh(self):
        raw=feed('<updated>2026-10-19T12:00:00Z</updated><entry/>')
        result=inspect_atom(raw,30,now=NOW);self.assertEqual(result['freshness_status'],'unknown_date');self.assertFalse(result['policy_passed'])
    def test_empty_structurally_valid_feed_is_not_recent_activity(self):
        result=inspect_atom(feed(''),30,now=NOW);self.assertTrue(result['valid']);self.assertEqual(result['freshness_status'],'empty');self.assertFalse(result['policy_passed'])
    def test_missing_or_naive_dates_cannot_establish_staleness(self):
        raw=feed('<entry><updated>2020-01-01T00:00:00Z</updated></entry><entry><updated>2026-10-19T10:00:00</updated></entry>')
        self.assertEqual(inspect_atom(raw,30,now=NOW)['freshness_status'],'unknown_date')
    def test_future_timestamp_is_not_reported_as_recent(self):
        result=inspect_atom(feed('<entry><updated>2027-01-01T00:00:00Z</updated></entry>'),30,now=NOW)
        self.assertEqual(result['freshness_status'],'future_timestamp');self.assertFalse(result['policy_passed'])
    def test_offset_normalization_and_boundary_age(self):
        raw=feed('<entry><updated>2026-10-18T14:00:00+02:00</updated></entry>')
        self.assertTrue(inspect_atom(raw,1,now=NOW)['policy_passed']);self.assertFalse(inspect_atom(raw,.99,now=NOW)['policy_passed'])
    def test_cli_enforces_age_policy_instead_of_xml_validity(self):
        with patch('source_pack.feed_receipt',return_value={'valid':True,'policy_passed':False,'freshness_status':'stale'}):
            for lang in ('fr','en','es'):
                with redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(['check-live','--topic','memory','--max-age-days','30','--lang',lang]),1)
                self.assertNotIn('invalid',output.getvalue())
    def test_invalid_policy_fails_without_contacting_any_feed(self):
        with patch('source_pack.feed_receipt') as fetch:
            for command in (['export','--max-age-days','30'],['check-live','--max-age-days','nan']):
                with redirect_stderr(io.StringIO()):self.assertEqual(main(command),2)
            fetch.assert_not_called()
