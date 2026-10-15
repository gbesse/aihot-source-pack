import unittest
import io
from contextlib import redirect_stdout
from source_pack import main

from source_pack import export, load_sources


class SourcePackTests(unittest.TestCase):
    def test_exports_valid_aihot_source_shape(self):
        data = export(load_sources(), "memory")
        self.assertEqual(len(data["sources"]), 1)
        item = data["sources"][0]
        self.assertEqual(item["kind"], "rss")
        self.assertTrue(item["config"]["feedUrl"].endswith("/releases.atom"))
        self.assertFalse(item["site_fulltext"])

    def test_rejects_duplicate_source_ids(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sources.json"
            path.write_text('[{"id":"a","name":"A","repo":"x/y","topic":["a"]},{"id":"a","name":"B","repo":"x/z","topic":["a"]}]')
            with self.assertRaises(ValueError):
                load_sources(path)

    def test_preview_filters_feeds_without_network(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["preview", "--topic", "memory"]), 0)
        self.assertIn("gh-hindsight [memory] -> https://github.com/", output.getvalue())
        self.assertNotIn("gh-qdrant", output.getvalue())

    def test_export_keeps_all_declared_topics(self):
        source = {"id": "sample", "name": "Sample", "repo": "example/sample", "topic": ["agents", "protocols"]}
        self.assertEqual(export([source])["sources"][0]["tags"], ["agents", "protocols"])


class FeedReceiptTests(unittest.TestCase):
    def test_exact_atom_namespace_required(self):
        from source_pack import inspect_atom
        for value in (b'<evilfeed/>', b'<feed/>', b'<rss/>', b'<feed xmlns="https://evil.test"/>'):
            with self.assertRaises(ValueError): inspect_atom(value)

    def test_empty_and_nonempty_feeds_have_honest_receipts(self):
        from source_pack import inspect_atom
        empty=inspect_atom(b'<feed xmlns="http://www.w3.org/2005/Atom"/>')
        self.assertEqual(empty['entry_count'],0);self.assertEqual(len(empty['content_sha256']),64)
        full=inspect_atom(b'<feed xmlns="http://www.w3.org/2005/Atom"><entry/><entry/></feed>')
        self.assertEqual(full['entry_count'],2)
        self.assertNotEqual(empty['content_sha256'],full['content_sha256'])

    def test_transport_failure_has_no_raw_stderr(self):
        from source_pack import feed_receipt
        from unittest.mock import patch
        from subprocess import CompletedProcess
        with patch('source_pack.subprocess.run',return_value=CompletedProcess([],22,b'',b'private error')):
            result=feed_receipt('https://github.com/example/repo/releases.atom')
        self.assertFalse(result['valid']);self.assertEqual(result['error_code'],'transport_failed')
        self.assertNotIn('private error',str(result))

    def test_manifest_field_types_fail_cleanly(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        import json
        for field,value in (('id',[]),('repo',None),('name',' ')):
            row=dict(id='one',name='Name',repo='owner/repo',topic=['agents']);row[field]=value
            with TemporaryDirectory() as d:
                p=Path(d)/'sources.json';p.write_text(json.dumps([row]))
                with self.assertRaises(ValueError):load_sources(p)

    def test_cli_json_check_and_localized_invalid_manifest(self):
        from unittest.mock import patch
        import json
        with patch('source_pack.feed_receipt',return_value={'valid':True,'entry_count':0}):
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(['check-live','--topic','memory','--json']),0)
            self.assertTrue(json.loads(out.getvalue())['valid'])
