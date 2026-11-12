import unittest,json,tempfile
from pathlib import Path
from source_pack import feed_identity_receipt
class FeedIdentity(unittest.TestCase):
 def test_duplicate_ids_not_silently_same_release(self):
  xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id></entry><entry><id>x</id></entry></feed>';self.assertEqual(feed_identity_receipt(xml)['findings'][0]['code'],'duplicate_entry_id')
 def test_foreign_or_credentialed_link(self):
  xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id><link href="https://github.com.evil.invalid/x"/></entry></feed>';self.assertEqual(feed_identity_receipt(xml)['findings'][0]['code'],'unexpected_link_origin')
 def test_valid_feed_not_authenticated_content(self):
  xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id><link href="https://github.com/example/repo/releases/tag/v1"/></entry></feed>';x=feed_identity_receipt(xml);self.assertTrue(x['valid']);self.assertFalse(x['publisher_authenticated'])
