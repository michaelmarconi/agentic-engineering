---
type: regex
target: trace
pattern: '"name":"(Write|Edit)"[^\n]*"file_path":\s*"[^"]*docs/practices/ci[^\n]*\.github/workflows/ci\.yml'
weight: 1
---
The topic file names the pipeline's file.
