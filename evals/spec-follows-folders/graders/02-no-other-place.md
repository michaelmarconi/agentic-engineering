---
type: tool_used
tool: Write
input_match: "file_path[^,]*(docs/specs/[a-z0-9-]+\\.spec\\.md|apps/[a-z]+/docs/|docs/specs/(web|rate[a-z-]*)/)"
max: 0
weight: 1
---
No spec is written flat in docs/specs/, in another app's folder, in a new folder of its own, or in a docs/ folder inside an app.
