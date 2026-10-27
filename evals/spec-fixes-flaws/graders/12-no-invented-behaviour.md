---
type: regex
target: { source: file, path: docs/specs/invoice-export.spec.md }
pattern: '^(?:- (?:THEN|AND)\b.*\b(?:no|not|without)\b.*\bstamp\b|(?:- (?:THEN|AND)\b|.*\bSHALL\b).*\b(?:unpaid|not (?:yet )?paid|partly|partial|permission|not allowed|may not|cannot|error|fails?|failed|limit|refus\w*)\b)'
flags: mi
match: not_contains
weight: 1
---
No rule or scenario outcome adds behaviour the original never described: what an unpaid or
partly paid invoice shows, who may not export, errors, failures or limits. These belong in Open
questions. A regex rather than a judge, because judges split their votes on this check for the
same correct spec.
