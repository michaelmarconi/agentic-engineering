---
type: regex
target: { source: file, path: .git/commits.log }
pattern: '^=== (?:(?!\n=== )[\s\S])*?(?:[Ss]ign-off|[Ss]igned off)'
weight: 1
---
The first commit pushed for the build says, in its message, that the plan was built before sign-off.
