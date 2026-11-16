import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import wordcount  # noqa: E402


class Words(unittest.TestCase):
    def test_three_words(self):
        self.assertEqual(wordcount.words("the cat sat"), 3)


if __name__ == "__main__":
    unittest.main()
