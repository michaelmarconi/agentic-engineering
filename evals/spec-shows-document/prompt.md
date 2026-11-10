---
tags: [spec]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Here's the conversation we've been having about workspace invites, pasted from earlier today:

> **Me:** Our invites never expire. Last month Sam, who'd left the company, found an old invite email and joined the workspace with it. Nobody noticed for three weeks.
> **You:** So an invite should stop working after some time. How long?
> **Me:** Seven days feels right.
> **You:** Should an admin be able to cancel an invite before then?
> **Me:** Yes, an admin can cancel any pending invite, and the link stops working straight away.
> **Me:** Actually, people on holiday miss a week easily. Make it 14 days, not 7.
> **You:** What should someone see if they open an expired or cancelled link?
> **Me:** A page saying the invite is no longer valid and to ask an admin for a new one.
> **Me:** We'll run the expiry check as a job on our Redis queue, by the way.
> **You:** Should the person who sent the invite be told when it expires?
> **Me:** Not sure yet, I'll think about it.

I think we've covered it. Please write the spec now and save it as docs/specs/invite-expiry.spec.md.
