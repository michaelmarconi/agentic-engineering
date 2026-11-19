---
type: regex
target: last_message
pattern: '\*\*Question \d+ of \d+[^\n]*\*\*(?:(?!\n\s*-{3}\s*\n)[\s\S])*?(?:0001|[Ss]earch|Meilisearch|Postgres)(?:(?!\n\s*-{3}\s*\n)[\s\S])*\n\s*-{3}\s*\n\s*\*\*Question \d+ of \d+(?:(?!\n\s*-{3}\s*\n)[\s\S])*?(?:0002|API|OAuth|[Cc]aller)|\*\*Question \d+ of \d+[^\n]*\*\*(?:(?!\n\s*-{3}\s*\n)[\s\S])*?(?:0002|API|OAuth|[Cc]aller)(?:(?!\n\s*-{3}\s*\n)[\s\S])*\n\s*-{3}\s*\n\s*\*\*Question \d+ of \d+(?:(?!\n\s*-{3}\s*\n)[\s\S])*?(?:0001|[Ss]earch|Meilisearch|Postgres)'
weight: 1
---
One question belongs to the search ADR (0001, Postgres or Meilisearch) and the other, after the rule, to the API caller ADR (0002, API keys or OAuth), or the other way round.
