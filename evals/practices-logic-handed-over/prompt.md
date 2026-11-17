---
tags: [practices]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent, Bash]
---

/practices deploying. There is one environment, production, at https://notes.example.com. Any release tagged on main may go there. To deploy: build the image with `docker build -t registry.example.com/notes .`, push it with `docker push registry.example.com/notes`, run `python3 -m notes.migrate` only if `python3 -m notes.migrate --pending` prints anything, then check `curl -fsS https://notes.example.com/health`, retrying up to three times, ten seconds apart. Check: that same health URL. Roll back: none, stop and tell me. Deploys are by hand, by me. Don't ask me anything.
