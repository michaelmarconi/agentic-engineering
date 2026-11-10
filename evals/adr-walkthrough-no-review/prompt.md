---
tags: [adr]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

We're walking through the open questions in docs/adrs/0003-how-email-is-sent.md. It was reviewed already, and you told me it has 3 open questions and asked me the first: why was sending in a background thread rejected? My answer: emails waiting in memory are lost whenever the web process restarts, and we deploy several times a day. Go on to the next question.
