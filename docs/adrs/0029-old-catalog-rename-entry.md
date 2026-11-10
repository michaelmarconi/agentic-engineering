---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
type: ADR
status: 👍 Accepted
date: 2026-11-10
---

# Keep this repository's catalog so existing installs can switch to the plugin's new name without editing settings

## Question

When the plugin[^plugin] is renamed, how do people who installed it under the old name keep working?

## Decision

Chosen: this repository keeps its catalog[^catalog], named `sdlc`, listing the plugin under its new
name with a rename entry[^rename]. When this catalog is next updated, Claude Code rewrites an install's settings[^settings] and skill[^skill] names to the new name. One install command then records the install's new name.

## Background

[ADR 0028](0028-plugin-catalog-repository.md)[^adr] moves the plugin to a catalog of its own, and the
plugin and its skills are being renamed. Every existing install came from this repository's
catalog. Claude Code can move an install across a rename within one catalog, but not between catalogs.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Remove this repository's catalog and let people move by hand | Rejected | Every install not yet moved fails at its next update |
| Keep the catalog, listing the plugin under its old name | Rejected | Old installs would never get the new skill names |
| Keep the catalog, mark the old name removed and uninstall it | Rejected | The old install fails with a clear message, and everyone reinstalls by hand |
| Keep the catalog, listing the plugin under its new name with a rename entry | Chosen | An update rewrites settings and skill names, leaving one install command, as a trial showed |

## Consequences

- Good: an update moves an install to the new skill names, including settings a team stored in its repository.
- Good: keeping the catalog also lets the maintainer's own sessions load the plugin from this repository's files.
- Bad: a person runs one install command after the update.
- Bad: moved installs stay on this catalog, under the new plugin name, until each person switches to the plugin's new catalog by hand.
- Bad: each rename entry stays for as long as the catalog does.
- Bad: two catalogs list the same plugin, so a person must not enable it from both.
- Bad: what the plugin saved about work in progress is not carried to the new name.

## Out of scope

- When this repository's catalog is removed: a later decision, once no known install uses it.
- Untested: updates after this repository is renamed, which rely on GitHub's redirect from the old address.
- Untested: what an interactive session shows.
- Untested: the rewrite of user and local settings; the trial covered settings stored in the repository.
- Untested: two enabled copies dropping one copy's hooks[^hook], which comes from Claude Code's documentation.

## How we'll check

Applies to: this repository's own catalog, and any change to the plugin's name.

1. Test: a unit test checks the catalog is named `sdlc`, lists the plugin from this repository under its current name, and maps each earlier name to it.
2. Demonstration: an install made under the old name, once updated and installed again under the new name, loads with all its skills.
3. Inspection: the rename's changelog entry gives people with old installs the update steps, including the install command.

## Open questions

- None.

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
- Before any install command, the next session loaded 9 `agentic:` skills and 14 `agentic:` agents and no `sdlc:` ones, and a skill ran to the end.
- `claude plugin list` showed nothing installed until `claude plugin install agentic@sdlc` ran. The install command records the install under its new name; nothing else was seen to fail without it.
- The plugin's data folder is named after the plugin: a new `agentic-sdlc` folder started empty, and `sdlc-sdlc` was left behind.

**Two copies.** When two enabled plugins share a name, Claude Code drops one copy's hooks
([Claude Code: plugin loading](https://code.claude.com/docs/en/plugins/loading.md)).

[^plugin]: A plugin is a package of skills, agents (separate instances of Claude, each started for one task) and hooks that Claude Code installs and updates as one.
[^catalog]: A catalog, which Claude Code calls a marketplace, is a file listing plugins and where to fetch each one; its name is the part of an install name after the `@`.
[^adr]: ADR stands for architecture decision record: a document that records one technical decision and why it was made.
[^rename]: A rename entry is a line in the catalog saying that the plugin's old name now means its new one.
[^settings]: Claude Code keeps settings in three places: user settings, a person's own for every project; project settings, shared through the project's repository; and local settings, a person's private ones for one project.
[^skill]: A skill is a set of instructions Claude follows for one step, run as a slash command.
[^hook]: A hook is a script Claude Code runs automatically at set moments, such as just before Claude edits a file.
