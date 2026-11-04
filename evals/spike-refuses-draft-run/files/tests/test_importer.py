import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from importer import read_statement  # noqa: E402


class ReadStatement(unittest.TestCase):
    def test_reads_rows_without_the_header(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("date;payee;amount\n2026-10-01;Mill;-120,00\n")
        self.addCleanup(os.remove, f.name)
        self.assertEqual(read_statement(f.name), [["2026-10-01", "Mill", "-120,00"]])


if __name__ == "__main__":
    unittest.main()
