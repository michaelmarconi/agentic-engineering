---
type: regex
target: last_message
pattern: "(^|\\n)(> *)?#{1,6} *What happened *\\n[\\s\\S]*\\n(> *)?#{1,6} *What I expected *\\n[\\s\\S]*\\n(> *)?#{1,6} *Steps to reproduce[^\\n]*\\n[\\s\\S]*\\n(> *)?#{1,6} *Context *\\n[\\s\\S]*\\n(> *)?#{1,6} *Proposed eval"
weight: 1
---
