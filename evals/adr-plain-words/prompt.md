---
tags: [adr]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Agent]
---

Record this decision as docs/adrs/0001-settlement-file-import.md. Each night our card processor sends a settlement file listing every card payment it paid us for. We import it row by row, and when the import fails halfway it keeps tripping over itself: the rerun imports the first half again and we get duplicate payments. The team calls this the 2 a.m. pile-up. Options: import the whole file in one database transaction, so a failure leaves nothing imported; or keep row-by-row and skip rows already imported, which we rejected because two payments can legitimately look identical. We chose the single transaction. Good: a failed import can simply be rerun. Bad: a very large file holds the transaction open for minutes. We'll check it with a test that fails an import halfway and reruns it. Just draft it, don't ask me anything.
