"""Tests for saved_records.py. File ages are set with os.utime, so no test depends on timing."""

import os
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import saved_records  # noqa: E402

DAY = 24 * 60 * 60


class Prune(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = self.tmp.name

    def entry(self, name, days_old, folder=False):
        path = os.path.join(self.folder, name)
        if folder:
            os.makedirs(path)
            with open(os.path.join(path, "record.json"), "w") as f:
                f.write("{}")
        else:
            with open(path, "w") as f:
                f.write("{}")
        when = time.time() - days_old * DAY
        os.utime(path, (when, when))
        return path

    def test_an_entry_older_than_the_limit_is_deleted(self):
        old = self.entry("old.json", saved_records.DAYS + 1)
        saved_records.prune(self.folder)
        self.assertFalse(os.path.exists(old))

    def test_a_newer_entry_is_kept(self):
        new = self.entry("new.json", saved_records.DAYS - 1)
        saved_records.prune(self.folder)
        self.assertTrue(os.path.exists(new))

    def test_an_old_session_folder_is_deleted_with_its_files(self):
        old = self.entry("s-old", saved_records.DAYS + 1, folder=True)
        new = self.entry("s-new", 0, folder=True)
        saved_records.prune(self.folder)
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(new))

    def test_a_missing_folder_does_nothing(self):
        saved_records.prune(os.path.join(self.folder, "missing"))
        saved_records.prune(None)

    def test_an_entry_that_cannot_be_deleted_is_skipped(self):
        stuck = self.entry("stuck.json", saved_records.DAYS + 1)
        old = self.entry("old.json", saved_records.DAYS + 1)
        real = os.remove

        def refuse(path, *args, **kwargs):
            if path == stuck:
                raise PermissionError(path)
            return real(path, *args, **kwargs)

        with mock.patch("os.remove", side_effect=refuse):
            saved_records.prune(self.folder)
        self.assertTrue(os.path.exists(stuck))
        self.assertFalse(os.path.exists(old))


if __name__ == "__main__":
    unittest.main()
