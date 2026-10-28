---
status: Draft
date: 2026-10-28
---

# Write helper scripts in standard-library Python or POSIX shell

## Context and Problem Statement

This repository is a plugin for Claude Code, Anthropic's AI coding assistant. Some of its work
must come out exactly the same every time, such as refusing a document status change the
lifecycle does not allow, so it is done by scripts rather than left to Claude. Hooks, scripts
that Claude Code runs automatically at set moments, run these scripts on the person's own
computer, which may be a Mac, a Linux machine or Claude Code on the web.

The plugin has no install step of its own: Claude Code copies its files and nothing more. So a
script can rely only on what is already present on the person's computer. This records a decision
made on 2026-10-22, when the repository's rules were first written, and first applied to hooks on
2026-10-26.

## Considered Options

- **JavaScript on Node.js.** Rejected: Node.js is not part of a standard Mac or Linux system, and
  Claude Code does not need it, so it is missing from more computers than Python 3.
- **Python with packages from outside its standard library.** Rejected: someone would have to
  install the packages, and the plugin has no install step to do it.
- **A compiled program**, such as one written in Go. Rejected: it needs a separate build for each
  operating system and processor, and a release step to publish them.
- **Python 3 using only its standard library, or POSIX shell**, the shell language common to
  macOS and Linux. Chosen, below.

## Decision Outcome

Chosen option: Python 3 using only its standard library, or POSIX shell, because they are the
languages most likely to be present already. POSIX shell is on every Mac and Linux machine.
Python 3 is on Claude Code on the web and most Linux systems, and on a Mac once Apple's developer
tools are installed, which most developers have done. So on most developers' computers the
scripts run with nothing more to install. We accept that a person without Python 3 has to install
it.

### Consequences

- Good: installing the plugin is all a person does; no script fails for want of a package.
- Good: the scripts' tests run with a bare Python 3, using its built-in test module.
- Bad: a person without Python 3, such as someone on a Mac without Apple's developer tools,
  cannot use the hooks until they install it, so the README has to say they need it.
- Bad: without packages, some work is written by hand, such as reading a document's frontmatter,
  the block of fields at its top, which a package would otherwise parse.

### Confirmation

Applies to: every script the plugin's hooks or skills run.
Checked by: inspection. A reviewer of each change that adds or changes a script checks that it
imports nothing outside Python's standard library, or uses only POSIX shell, and that its tests
pass on a Python 3 with no packages installed.
