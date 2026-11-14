import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import repository  # noqa: E402


class Layout(unittest.TestCase):
    """A session folder that is not a repository, holding `app/` as a git repository, as in a
    Claude project thread."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        # realpath: on macOS the temporary folder is reached through a link (/var -> /private/var).
        self.session = os.path.realpath(tmp.name)
        self.app = os.path.join(self.session, "app")
        os.makedirs(os.path.join(self.app, "docs", "plans"))
        subprocess.run(["git", "init", "-q", self.app], check=True)
        env = mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.session})
        env.start()
        self.addCleanup(env.stop)

    def test_full_path_inside_a_repository_one_level_down(self):
        plan = os.path.join(self.app, "docs", "plans", "x.md")
        self.assertEqual(repository.repository_of(plan), self.app)

    def test_relative_path_counts_from_the_session_folder(self):
        self.assertEqual(repository.repository_of("app/docs/plans/x.md"), self.app)

    def test_relative_path_counts_from_the_given_folder_first(self):
        self.assertEqual(repository.repository_of("docs/plans/x.md", base=self.app), self.app)

    def test_a_relative_path_missing_from_the_given_folder_is_read_from_the_session_folder(self):
        # The shell may have moved into a subfolder; a path that exists from the session folder wins.
        plan = os.path.join(self.app, "docs", "plans", "x.md")
        with open(plan, "w") as f:
            f.write("x")
        docs = os.path.join(self.app, "docs")
        self.assertEqual(repository.full_path("app/docs/plans/x.md", base=docs), plan)

    def test_a_relative_path_found_nowhere_is_read_from_the_given_folder(self):
        self.assertEqual(repository.full_path("new.md", base=self.app), os.path.join(self.app, "new.md"))

    def test_without_a_session_variable_the_working_folder_is_the_session_folder(self):
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": ""}), \
                mock.patch("os.getcwd", return_value=self.session):
            self.assertEqual(repository.session_folder(), self.session)
            self.assertEqual(repository.repository_of("app/docs/plans/x.md"), self.app)

    def test_a_git_file_counts_as_a_repository(self):
        worktree = os.path.join(self.session, "worktree")
        os.makedirs(worktree)
        with open(os.path.join(worktree, ".git"), "w") as f:
            f.write("gitdir: elsewhere\n")
        self.assertEqual(repository.repository_of(os.path.join(worktree, "a.md")), worktree)

    def test_a_file_in_no_repository_falls_back_to_the_session_folder(self):
        self.assertEqual(repository.repository_of(os.path.join(self.session, "notes", "a.md")),
                         self.session)
        self.assertIsNone(repository.top(os.path.join(self.session, "notes", "a.md")))

    def test_a_linked_folder_gives_the_real_folder(self):
        link = os.path.join(self.session, "link")
        os.symlink(self.app, link)
        self.assertEqual(repository.repository_of(os.path.join(link, "docs", "a.md")), self.app)

    def test_relative_parts_are_counted_from_the_file_s_repository(self):
        plan = os.path.join(self.app, "docs", "plans", "x.md")
        self.assertEqual(repository.relative_parts(plan), ["docs", "plans", "x.md"])
        self.assertEqual(repository.relative_parts("app/docs/plans/x.md"), ["docs", "plans", "x.md"])

    def test_relative_parts_in_no_repository_count_from_the_session_folder(self):
        self.assertEqual(repository.relative_parts(os.path.join(self.session, "docs", "brief.md")),
                         ["docs", "brief.md"])

    def test_session_folders_are_the_session_folder_and_repositories_inside_it(self):
        other = os.path.join(self.session, "other")
        os.makedirs(other)
        subprocess.run(["git", "init", "-q", other], check=True)
        os.makedirs(os.path.join(self.session, "plain"))
        self.assertEqual(repository.session_folders(), [self.session, self.app, other])

    def test_session_folders_when_the_session_folder_is_a_repository(self):
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.app}):
            self.assertEqual(repository.session_folders(), [self.app])

    def test_session_folders_with_no_repository_at_all(self):
        empty = tempfile.TemporaryDirectory()
        self.addCleanup(empty.cleanup)
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": empty.name}):
            self.assertEqual(repository.session_folders(), [os.path.realpath(empty.name)])

    def test_a_project_started_in_a_subfolder_of_a_repository_counts_from_the_session_folder(self):
        # A package of a larger repository, with the session started in the package.
        package = os.path.join(self.app, "pkg")
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": package}):
            spec = os.path.join(package, "docs", "specs", "x.spec.md")
            self.assertEqual(repository.relative_parts(spec), ["docs", "specs", "x.spec.md"])
            # A file of the repository outside the package still counts from the repository.
            self.assertEqual(repository.relative_parts(os.path.join(self.app, "docs", "brief.md")),
                             ["docs", "brief.md"])

    def test_session_folders_skip_repositories_inside_one_that_is_a_repository(self):
        # Such as a submodule or a checkout kept inside the project.
        nested = os.path.join(self.app, "vendor")
        os.makedirs(nested)
        subprocess.run(["git", "init", "-q", nested], check=True)
        with mock.patch.dict(os.environ, {"CLAUDE_PROJECT_DIR": self.app}):
            self.assertEqual(repository.session_folders(), [self.app])

    def test_a_named_folder_is_kept_even_when_the_path_is_missing_there(self):
        os.makedirs(os.path.join(self.session, "docs"))
        with open(os.path.join(self.session, "docs", "x.md"), "w") as f:
            f.write("x")
        self.assertEqual(repository.full_path("docs/x.md", base=self.app, fallback=False),
                         os.path.join(self.app, "docs", "x.md"))

    def test_the_main_script_runs(self):
        done = subprocess.run([sys.executable, os.path.join(HERE, "repository.py"), "--help"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
