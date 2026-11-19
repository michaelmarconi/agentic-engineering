"""Where the plugin keeps the files it writes outside the repository (docs/adrs/0051).

Every such file, a build's, audit's or verify run's report and every record a hook keeps during a
session, goes under `agentic/` in the session's scratchpad: the folder Claude Code gives each
session for temporary files, which it clears when it chooses. Nothing the plugin writes there is
meant to last beyond the session.

Hooks are told the scratchpad by Claude Code, as `scratchpad_dir` in their event: each hook's
`main` calls `use_event(event)` once, and the code it runs asks `current()`. Scripts that Claude
runs are told it by Claude, as `--scratchpad`, and call `root(path, session)`, which refuses a path
that is not this session's scratchpad, since Claude can mistype a long path. With no scratchpad,
as in sessions that have none and in the plugin's own tests, both use `agentic-<user id>` in the
system's temporary folder, made so only this user can open it, so other users can neither read a
file there nor put one in its place.

This module has no command; the hooks and scripts import it.
"""

import os
import tempfile

FOLDER = "agentic"
_current = None


class FolderError(Exception):
    """The folder can't be used; the message says why."""


def fallback_root():
    return os.path.join(tempfile.gettempdir(), f"agentic-{os.getuid()}")


def trusted(folder):
    """Whether `folder` is a real folder that only this user can open."""
    try:
        info = os.lstat(folder)
    except OSError:
        return False
    return os.path.isdir(folder) and not os.path.islink(folder) and info.st_uid == os.getuid() \
        and not info.st_mode & 0o077


def is_fallback(root):
    return os.path.normpath(root) == os.path.normpath(fallback_root())


def private():
    folder = fallback_root()
    try:
        os.makedirs(folder, mode=0o700, exist_ok=True)
    except OSError as error:
        raise FolderError(f"{folder} can't be made ({error.strerror or error})")
    if not trusted(folder):
        raise FolderError(f"{folder} is not a folder only you can open; delete it and run again")
    return folder


def made(folder):
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError as error:
        raise FolderError(f"{folder} can't be made ({error.strerror or error})")
    return folder


def root(scratchpad, session):
    """The plugin's folder for a script Claude runs: `agentic/` in `scratchpad`, which must be this
    session's, or the private fallback when no scratchpad is given."""
    if not scratchpad:
        return private()
    path = os.path.normpath(scratchpad)
    if not session:
        raise FolderError("no session id was given, so the scratchpad can't be checked")
    if not os.path.isdir(path):
        raise FolderError(f"the scratchpad {scratchpad} does not exist; pass the folder your instructions name")
    if not path.endswith(os.sep + os.path.join(str(session), "scratchpad")):
        raise FolderError(f"{scratchpad} is not the scratchpad of session {session}: its path must end "
                          f"in /{session}/scratchpad")
    return made(os.path.join(path, FOLDER))


def reset():
    global _current
    _current = None


def use_event(event):
    """Take the folder from a hook's event; with none usable, `current()` gives None."""
    global _current
    scratchpad = event.get("scratchpad_dir") if isinstance(event, dict) else None
    try:
        if isinstance(scratchpad, str) and scratchpad:
            _current = made(os.path.join(os.path.normpath(scratchpad), FOLDER))
        else:
            _current = private()
    except FolderError:
        _current = None


def current():
    """The plugin's folder for this hook run, or None when it has none."""
    return _current
