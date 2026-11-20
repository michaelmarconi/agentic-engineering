---
type: llm
focus: { source: file, path: docs/plans/2026-10-20-customs-hold-release.md }
weight: 1
---
The mermaid diagram adds nothing the plan's text does not say. Its boxes may name, in any
wording, the customs broker, src/broker/updates.py, record_status() in src/shipments.py, the
container's status history or status events, the list of held containers in src/holds/list.py,
summary() in src/page.py, and outcomes the text states, such as a cleared container leaving the
list or the page showing "cleared since <time>"; it need not show them all. It fails only if a
box or arrow names a part, step or decision the text never mentions, such as a database, a
queue, a retry, a check or an email.
