---
type: regex
target: { source: file, path: docs/adrs/0001-payment-event-handling.md }
pattern: '(?:prove[dn]?|confirm(?:ed)?|check(?:ed)?|verif(?:y|ied))\b[^\n.]{0,40}\b(?:in|during|while)\b[^\n.]{0,20}\bbuild'
flags: i
match: not_contains
weight: 1
---
No section leaves the claim to be proven during the build.
