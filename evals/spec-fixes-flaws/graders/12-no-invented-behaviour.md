---
type: regex
target: { source: file, path: docs/specs/invoice-export.spec.md }
pattern: '^(?:\| (?:Then|And) \|[^\n]*\b(?:no|not|without)\b(?!\.)[^\n]*\bstamp\b|\| (?:Then|And) \|[^\n]*\b(?:[Uu]npaid|not (?:yet )?paid|[Pp]artly|[Pp]artial(?:ly)?|[Pp]ermission|not allowed|may not|cannot|[Ee]rrors?|[Ff]ail(?:s|ed|ure)?|[Ll]imits?|[Rr]efus\w*|[Rr]eject\w*)\b|### \d+\. [^\n]*\n(?:(?!#### |\| |### |## )[^\n]*\n)*?(?!#### |\| |### |## )[^\n]*\b(?:[Uu]npaid|not (?:yet )?paid|[Pp]artly|[Pp]artial(?:ly)?|[Pp]ermission|not allowed|may not|cannot|[Ee]rrors?|[Ff]ail(?:s|ed|ure)?|[Ll]imits?|[Rr]efus\w*|[Rr]eject\w*)\b)(?=[\s\S]*^## Constraints)'
flags: m
match: not_contains
weight: 1
---
No rule, and no example Then or And row, above Constraints adds behaviour the original never
described: what an unpaid or partly paid invoice shows, who may not export, errors, failures,
limits or rejections. These belong in Open questions, where the pattern does not look. A regex
rather than a judge, because judges split their votes on this check for the same correct spec.
