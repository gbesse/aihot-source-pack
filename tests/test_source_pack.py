import unittest

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
