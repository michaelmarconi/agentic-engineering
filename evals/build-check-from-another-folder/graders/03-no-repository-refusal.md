---
type: regex
target: trace
pattern: 'There is no git repository holding|Nothing has been committed since the reviews|No (code|security|build) review.* report of the reviewed commit'
match: not_contains
weight: 1
---
The build hook never refused the correction check, neither for want of a repository nor for a missing review.
