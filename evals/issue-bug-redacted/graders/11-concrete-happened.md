---
type: regex
target: last_message
pattern: "What happened[^\\n]*\\n(?=(?:(?!What I expected)[\\s\\S])*(Kafka|broker))(?=(?:(?!What I expected)[\\s\\S])*\\btopics?\\b)(?=(?:(?!What I expected)[\\s\\S])*\\bhosts?\\b)"
weight: 1
---
