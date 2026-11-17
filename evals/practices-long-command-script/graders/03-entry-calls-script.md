---
type: regex
target: { source: file, path: package.json }
pattern: '"[\w:.-]+"\s*:\s*"(?:sh |bash )?(?:\./)?script/[\w.-]+"'
weight: 1
---
package.json gains an entry that only calls the script.
