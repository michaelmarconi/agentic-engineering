import unittest


class Placeholder(unittest.TestCase):
    def test_imports(self):
        import notes.server  # noqa: F401
