import unittest

from src.attachments import TooLarge, attach


class AttachTest(unittest.TestCase):
    def test_at_limit_is_stored(self):
        invoice = {"number": 17}
        attach(invoice, b"x" * 10_000_000)
        self.assertEqual(len(invoice["attachments"]), 1)

    def test_over_limit_is_refused(self):
        invoice = {"number": 17}
        with self.assertRaises(TooLarge):
            attach(invoice, b"x" * 10_000_001)
        self.assertNotIn("attachments", invoice)


if __name__ == "__main__":
    unittest.main()
