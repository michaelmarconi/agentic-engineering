---
type: regex
target: { source: file, path: docs/adrs/0001-session-data-storage.md }
pattern: "So\\s+every\\s+deploy\\s+logs\\s+everyone\\s+out,\\s+and\\s+when\\s+a\\s+second\\s+server\\s+joins\\s+behind\\s+the\\s+load\\s+balancer(?:\\[\\^\\d+\\])?\\s+it\\s+cannot\\s+see\\s+any\\s+session\\s+that\\s+a\\s+person\\s+started\\s+on\\s+the\\s+first\\s+one\\."
weight: 1
---
The clear 29-word sentence is left as written, apart from line wrapping or a footnote marker: a sentence over 25 words that reads easily is not a failure.
