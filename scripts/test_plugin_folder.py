"""Tests for plugin_folder.py, which says where the plugin keeps the files it writes outside the
repository: the session's scratchpad (docs/adrs/0051)."""

import os
import stat
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plugin_folder  # noqa: E402

SESSION = "2f1c0a4e-1111-4222-8333-944455556666"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temp = os.path.join(self.tmp.name, "system-temp")
        os.makedirs(self.temp)
        patcher = mock.patch.object(plugin_folder.tempfile, "gettempdir", return_value=self.temp)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.scratchpad = os.path.join(self.tmp.name, "claude-0", "-work-repo", SESSION, "scratchpad")
        os.makedirs(self.scratchpad)
        plugin_folder.reset()
        self.addCleanup(plugin_folder.reset)


class Given(Base):
    """A scratchpad path that Claude passes to a script."""

    def test_scratchpad_of_this_session(self):
        root = plugin_folder.root(self.scratchpad, SESSION)
        self.assertEqual(root, os.path.join(self.scratchpad, "agentic"))
        self.assertTrue(os.path.isdir(root))

    def test_trailing_slash_accepted(self):
        self.assertEqual(plugin_folder.root(self.scratchpad + "/", SESSION),
                         os.path.join(self.scratchpad, "agentic"))

    def test_another_sessions_scratchpad_refused(self):
        with self.assertRaises(plugin_folder.FolderError) as caught:
            plugin_folder.root(self.scratchpad, "another-session")
        self.assertIn("another-session", str(caught.exception))

    def test_mistyped_path_refused(self):
        mistyped = self.scratchpad.replace("/claude-0/", "/claude-0-")
        with self.assertRaises(plugin_folder.FolderError) as caught:
            plugin_folder.root(mistyped, SESSION)
        self.assertIn("does not exist", str(caught.exception))

    def test_folder_not_named_scratchpad_refused(self):
        other = os.path.join(self.tmp.name, SESSION, "notes")
        os.makedirs(other)
        with self.assertRaises(plugin_folder.FolderError):
            plugin_folder.root(other, SESSION)

    def test_no_session_refused(self):
        with self.assertRaises(plugin_folder.FolderError):
            plugin_folder.root(self.scratchpad, "")

    def test_none_given_falls_back_to_private_folder(self):
        root = plugin_folder.root("", SESSION)
        self.assertEqual(root, os.path.join(self.temp, f"agentic-{os.getuid()}"))
        self.assertTrue(plugin_folder.is_fallback(root))
        self.assertEqual(stat.S_IMODE(os.stat(root).st_mode) & 0o077, 0)

    def test_scratchpad_is_not_the_fallback(self):
        self.assertFalse(plugin_folder.is_fallback(plugin_folder.root(self.scratchpad, SESSION)))

    def test_fallback_others_can_open_is_refused(self):
        os.makedirs(plugin_folder.fallback_root())
        os.chmod(plugin_folder.fallback_root(), 0o755)
        with self.assertRaises(plugin_folder.FolderError):
            plugin_folder.root("", SESSION)

    def test_fallback_symlink_is_refused(self):
        elsewhere = os.path.join(self.tmp.name, "elsewhere")
        os.makedirs(elsewhere, mode=0o700)
        os.symlink(elsewhere, plugin_folder.fallback_root())
        with self.assertRaises(plugin_folder.FolderError):
            plugin_folder.root("", SESSION)


class FromEvent(Base):
    """A hook's event, whose scratchpad Claude Code itself names."""

    def test_event_scratchpad_used(self):
        plugin_folder.use_event({"scratchpad_dir": self.scratchpad, "session_id": SESSION})
        self.assertEqual(plugin_folder.current(), os.path.join(self.scratchpad, "agentic"))

    def test_event_scratchpad_not_checked_against_the_session(self):
        # Claude Code names it, so it needs no check, and an agent's event carries the main session's.
        plugin_folder.use_event({"scratchpad_dir": self.scratchpad, "session_id": "other"})
        self.assertEqual(plugin_folder.current(), os.path.join(self.scratchpad, "agentic"))

    def test_event_without_scratchpad_falls_back(self):
        plugin_folder.use_event({"session_id": SESSION})
        self.assertEqual(plugin_folder.current(), plugin_folder.fallback_root())

    def test_unusable_fallback_keeps_nothing(self):
        os.makedirs(plugin_folder.fallback_root())
        os.chmod(plugin_folder.fallback_root(), 0o755)
        plugin_folder.use_event({"session_id": SESSION})
        self.assertIsNone(plugin_folder.current())

    def test_nothing_used_yet_keeps_nothing(self):
        self.assertIsNone(plugin_folder.current())


if __name__ == "__main__":
    unittest.main()
