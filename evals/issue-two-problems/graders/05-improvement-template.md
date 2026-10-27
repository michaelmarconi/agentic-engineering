---
type: regex
target: last_message
pattern: "(^|\\n)(> *)?#{1,6} *What got in the way *\\n[\\s\\S]*\\n(> *)?#{1,6} *What would be better *\\n[\\s\\S]*\\n(> *)?#{1,6} *Context *\\n[\\s\\S]*\\n(> *)?#{1,6} *Proposed eval"
weight: 1
---
