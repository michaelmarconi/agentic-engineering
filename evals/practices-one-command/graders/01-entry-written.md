---
type: regex
target: { source: file, path: package.json }
pattern: '"[\w:.-]+"\s*:\s*"(?:sh |bash )?(?:\./)?script/[\w.-]+"'
weight: 1
---
package.json has an entry that only calls a script in the script/ folder.
