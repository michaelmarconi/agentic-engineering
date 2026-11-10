---
type: regex
target: { source: file, path: docs/spikes/2026-11-02-importer-reads-bank-file.md }
pattern: '^status: 📝️? Draft\s*\ndate: (?!2026-11-02)\d{4}-\d{2}-\d{2}\s*$'
flags: m
weight: 1
---
The status line changed and, beside it, the date moved on from 2026-11-02 to the day of the change.
