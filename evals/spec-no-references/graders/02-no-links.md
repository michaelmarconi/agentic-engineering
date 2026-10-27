---
type: regex
target: { source: file, path: docs/specs/auth/account-lockout.spec.md }
pattern: '\]\(|docs/|\.spec\.md|brief\.md|0002|postmark'
flags: i
match: not_contains
weight: 1
---
The spec has no Markdown link, no path to another document and no mention of ADR 0002 or Postmark.
