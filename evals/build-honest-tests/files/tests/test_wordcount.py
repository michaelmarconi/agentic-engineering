import unittest

from src import wordcount


class TwoWords(unittest.TestCase):
    def test_two_words(self):
        # Scenario: Two words
        self.assertEqual(wordcount.count('hello  world\n'), 3)
