---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record our decision as docs/adrs/0001-money-amounts.md. Prices and totals are stored as floating-point numbers today, and sums drift by a penny now and then. We will store every amount as a whole number of the smallest unit of its currency, such as 1999 pence for 19.99 pounds. We rejected decimal columns, because our two languages read them differently, and keeping floats with rounding, because it hides the drift instead of ending it. The good: sums are exact. The bad: every screen must divide by 100 to show an amount. We will check in code review that no amount is stored as a float.
