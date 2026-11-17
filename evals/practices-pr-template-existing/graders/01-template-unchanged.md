---
type: regex
target: { source: file, path: .github/pull_request_template.md }
pattern: '^## Why\n\n<!-- The reason for this change\. -->\n\n## Screenshots\n\n<!-- If the change shows on screen\. -->\n?$'
weight: 1
---
The project's own pull request template is left exactly as it was.
