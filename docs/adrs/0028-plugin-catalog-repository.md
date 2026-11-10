---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-10
supersedes: 0001
---

# List the plugin in a catalog repository of its own, named after the maintainer

## Question

Where is the plugin[^plugin] listed for people to install it, and under what catalog[^catalog] name?

## Decision

Chosen: the skills[^skill] stay one plugin, listed in a separate repository, `michaelmarconi/marketplace`.
Its catalog is named `michaelmarconi` and lists each of the maintainer's plugins from its own
repository. A catalog named after its publisher gives every later plugin the same install address,
so nobody has to move again.

## Background

[ADR 0001](0001-single-plugin.md)[^adr] chose to ship the skills as one plugin, with this repository as its
own catalog. That catalog is named after the product, so the install name repeats it, and it leaves
no place for the maintainer's later plugins.
Moving a catalog costs each person a step by hand, so the choice is best made while few people
use it.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Each skill installed on its own | Rejected | A lone skill cannot bring the agents[^agent], hooks[^hook] and scripts it shares with the others |
| This repository as its own catalog, named after the product, as [ADR 0001](0001-single-plugin.md) chose | Rejected | Each later plugin needs its own catalog, and the install name repeats the product |
| This repository as the catalog, renamed after the maintainer | Rejected | Later plugins sit inside one plugin's repository, and moving out costs everyone a step |
| Each plugin's repository as its own catalog, all named after the maintainer | Rejected | Claude Code keeps one catalog per name, so a person could add only one of them |
| A separate catalog repository named after the maintainer, listing each plugin from its own repository | Chosen | One address for every plugin, never moved |

## Consequences

- Good: a person adds one catalog once, then installs any plugin the maintainer publishes.
- Good: the install name says who publishes the plugin, and what it is.
- Good: one install brings every skill with the agents, hooks and scripts they share.
- Bad: a second repository to keep in step.
- Bad: people who installed from this repository's catalog must move to the new one by hand.
- Bad: a person cannot take one skill without the rest.

## Out of scope

- The plugin's own name, a naming choice rather than a technical one.
- How installs made from this repository's catalog keep working until they move: [ADR 0029](0029-old-catalog-rename-entry.md).
- Untested: fetching the catalog from its own repository. The trial used a folder standing in for it.

## How we'll check

Applies to: how the plugin is listed, published and installed.

1. Demonstration: in a clean Claude Code setup, installing from the catalog repository makes every skill available.
2. Inspection: the catalog lists each plugin from its own repository, fetched over HTTPS.
3. Test: Claude Code's plugin validator reports no problem with the catalog or the plugin's manifest.

## Open questions

- None.

## Technical detail

**The catalog.** `michaelmarconi/marketplace` holds `.claude-plugin/marketplace.json` with
`"name": "michaelmarconi"` and one entry per plugin. For this plugin:

```json
{
  "name": "agentic",
  "description": "Skills for Agentic Engineering.",
  "source": { "source": "url", "url": "https://github.com/michaelmarconi/agentic-engineering.git" }
}
```

The entry has no `version`: `plugin.json` holds it. The source is fetched over HTTPS, as How we'll
check requires. A person installs with:

```
claude plugin marketplace add michaelmarconi/marketplace
claude plugin install agentic@michaelmarconi
```

**One catalog per name.** Adding a second catalog with a name already added fails with
"already added from a different source"
([Claude Code: plugin troubleshooting](https://code.claude.com/docs/en/plugins/troubleshooting.md)).

**Evidence.** On 2026-11-10, with Claude Code 2.1.322 and a clean configuration, a local folder
standing in for the catalog, with a `url` source and a branch `ref`, installed `agentic@michaelmarconi`
at project scope in a test repository. New sessions loaded all 9 skills and 14 agents, and a skill
ran to the end.

[^plugin]: A plugin is a package of skills, agents and hooks that Claude Code installs and updates as one.
[^catalog]: A catalog, which Claude Code calls a marketplace, is a file listing plugins and where to fetch each one; its name is the part of an install name after the `@`.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^adr]: ADR stands for architecture decision record: a document that records one technical decision and why it was made.
[^agent]: An agent is a separate instance of Claude started to do one task, such as checking a document.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as just before Claude edits a file.
