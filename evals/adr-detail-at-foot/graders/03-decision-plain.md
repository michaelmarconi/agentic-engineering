---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "^## Decision\\s*\\n\\s*Chosen:(?=(?:(?!^## )[\\s\\S])*?Redis)(?:(?!^## )(?!appendonly|maxmemory|volatile-|allkeys-|session:|sess:)[\\s\\S])*(?:^## |(?![\\s\\S]))"
flags: m
weight: 1
---
The Decision opens "Chosen:" and says sessions are kept in Redis, without naming any Redis
setting, such as appendonly or maxmemory-policy, or the session key format.
