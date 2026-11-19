---
type: regex
target: trace
pattern: 'Report written: [^"\\]*(?:/scratchpad/agentic|/agentic-\d+/[^/"\\]+)/reports/[^"\\]*-build-'
weight: 1
---
The build report was written in the session's scratchpad, where every app can open it, or, as in these test runs, which give no scratchpad, in this session's private folder (docs/adrs/0051).
