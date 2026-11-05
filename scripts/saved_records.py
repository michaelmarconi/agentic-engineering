#!/usr/bin/env python3
"""Delete records the plugin's hooks saved for sessions that have long gone quiet.

The review relay, the build relay and the fresh-session hook keep a record per session under
$CLAUDE_PLUGIN_DATA. A session that ends can come back: `claude --resume`, or a cloud container
restarting, continues the same conversation under the same session id, so a record is not deleted
when the session ends (issue #37). Instead, each hook calls `prune` on its own folder whenever it
saves a record, and every entry there, a file or a session's folder, not changed for DAYS days is
deleted. DAYS matches Claude Code's default `cleanupPeriodDays`, after which it deletes the
conversation itself, so it can no longer be resumed.

This module has no command; the hooks import it.
"""

import os
import shutil
import time

DAYS = 30


def prune(folder, days=DAYS):
    """Delete the entries of `folder` not changed for `days` days; skip any that can't be."""
    if not folder:
        return
    try:
        names = os.listdir(folder)
    except OSError:
        return
    limit = time.time() - days * 24 * 60 * 60
    for name in names:
        path = os.path.join(folder, name)
        try:
            if os.path.getmtime(path) >= limit:
                continue
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError:
            pass
