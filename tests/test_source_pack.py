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
