---
tags: [spec]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Write a spec for rate limiting in our API: one API key may make at most 100 requests a minute, and requests over that are refused until the minute is up. I'm heading into meetings, so don't interview me: write the spec from this and flag anything you can't decide.
