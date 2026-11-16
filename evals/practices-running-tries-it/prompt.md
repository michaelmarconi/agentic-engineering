---
tags: [practices]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

/practices running the product. It runs on any machine with Python 3. Each run is one command: `bin/wordcount <file>`, with `--lines` for lines or `--url <address>` for a web page. Test pages come from the stand-in `sh tools/page-server.sh` on localhost:8765, which is safe; never touch any other web address or the internet. Don't ask me anything.
