---
type: regex
target: { source: file, path: package.json }
pattern: '"[\w:.-]+"\s*:\s*"[^"]*npm ci[^"]*npm run build[^"]*"'
weight: 1
---
package.json has a script that runs npm ci and then npm run build.
