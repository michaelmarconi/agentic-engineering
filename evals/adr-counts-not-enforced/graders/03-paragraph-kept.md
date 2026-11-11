---
type: llm
focus: { source: file, path: docs/adrs/0001-session-data-storage.md }
weight: 1
---
The Background section is still a single paragraph holding these four sentences, in this order, with no sentence split in two and no two sentences merged into one: "Sessions live in each web server's memory today." / "So every deploy logs everyone out, and when a second server joins behind the load balancer it cannot see any session that a person started on the first one." / "We are adding a second server next month to handle evening traffic." / "So sessions need a home that every server can reach and that survives a deploy." Line wrapping, an added footnote marker or a changed word or two inside a sentence do not matter; only the paragraph and sentence boundaries do.
