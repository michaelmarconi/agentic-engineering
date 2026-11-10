---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 📝 Draft
date: 2026-11-10
---

# Keep this repository's catalog so existing installs move to the plugin's new name by themselves

## Question

When the plugin[^plugin] is renamed, how do people who installed it under the old name keep working?

## Decision

Chosen: this repository keeps its own catalog[^catalog], still named `sdlc`, listing the plugin under
its new name with a rename entry from the old one. The catalog stays until no known install uses it.
Claude Code then moves each install to the new name on its next update, and one install command
tidies its record.

## Background

[ADR 0028](0028-plugin-catalog-repository.md) moves the plugin to a catalog of its own, and the
plugin is being renamed, so its skills[^skill] change their names too. Everyone who installed it
did so from this repository's catalog, by the old names. Claude Code can move an install across a
rename within one catalog, but not from one catalog to another.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Remove this repository's catalog and let people move by hand | Rejected | Every install not yet moved fails at its next update with "plugin not found" |
| Keep the catalog, listing the plugin under its old name | Rejected | Old installs would never get the new skill names |
| Keep the catalog, mark the old name removed and uninstall it | Rejected | A clean failure, but every person still moves by hand |
| Keep the catalog, listing the plugin under its new name with a rename entry from the old one | Chosen | An update moves the install and its settings, as a trial showed |

## Consequences

- Good: an update moves an install to the new skill names, including settings a team stored in its repository.
- Good: when the maintainer works in this repository, Claude Code loads the plugin from the files checked out here, listed in this same catalog.
- Bad: after the update, a person still runs one install command so Claude Code's list of installed plugins matches.
- Bad: two catalogs list the same plugin, and enabling it from both silently drops one copy's hooks[^hook].
- Bad: what the plugin saved about work in progress, such as reviews and builds, is not carried to the new name.

## Out of scope

- When this repository's catalog is removed: a later decision, once no known install uses it.
- Moving from this catalog to the new one, which stays a step by hand.
- Untested: updates after this repository is renamed, which rely on GitHub sending the old address to the new one.
- Untested: what an interactive session shows during the update.

## How we'll check

Applies to: this repository's own catalog, and any change to the plugin's name.

1. Test: a unit test checks the catalog is named `sdlc`, lists the plugin from this repository under its current name, and maps each earlier name to it.
2. Demonstration: an install made under the old name, once updated and installed again under the new name, loads with all its skills.

## Open questions

- Where do old installs find the update steps? Proposed: the rename's changelog entry.

## Technical detail

**The catalog.** `.claude-plugin/marketplace.json` in this repository:

```json
{
  "name": "sdlc",
  "description": "Kept so installs made under the old name move to the new one.",
  "owner": { "name": "Michael Marconi" },
  "plugins": [{ "name": "agentic", "source": "." }],
  "renames": { "sdlc": "agentic" }
}
```

Entries under `renames` are only ever added, never removed, while the catalog exists. On update,
Claude Code loads the plugin under its new name and rewrites `sdlc@sdlc` to `agentic@sdlc` in the
user, project and local settings
([Claude Code: rename or remove a plugin](https://code.claude.com/docs/en/plugins/host-marketplace.md)).

**Evidence.** On 2026-11-10, with Claude Code 2.1.322 and a clean configuration, a test repository
with `"sdlc@sdlc": true` in its stored project settings had the plugin installed from a branch of this
repository, then that branch renamed the plugin as above:

- `claude plugin marketplace update sdlc` alone rewrote the stored setting to `"agentic@sdlc": true`.
- The next session loaded 9 `agentic:` skills and 14 `agentic:` agents and no `sdlc:` ones, and a skill ran to the end.
- `claude plugin list` showed nothing installed until `claude plugin install agentic@sdlc` ran.
- The plugin's data folder is named after the plugin: a new `agentic-sdlc` folder started empty, and `sdlc-sdlc` was left behind.

**Two copies.** When two enabled plugins share a name, Claude Code drops one copy's hooks
([Claude Code: plugin loading](https://code.claude.com/docs/en/plugins/loading.md)).

[^plugin]: A plugin is a package of skills, agents and hooks that Claude Code installs and updates as one.
[^catalog]: A catalog, which Claude Code calls a marketplace, is a file listing plugins and where to fetch each one; its name is the part of an install name after the `@`.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as just before Claude edits a file.
