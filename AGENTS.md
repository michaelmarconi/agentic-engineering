# Agent instructions

This repo is a Claude Code plugin: a library of software-development-lifecycle skills. These
rules apply to every change. Where a rule names a number, it is a hard limit; everything else is
judgement.

## Principles

1. **Independent.** A skill works on its own. It never invokes, reads files from, or assumes a
   prior run of another skill. It may use an artifact another skill produces when one is present,
   but must work when it is not. Shared conventions are duplicated, not referenced: some
   repetition is the price of zero coupling.
2. **Small.** Every word earns its place. Write only what Claude would not do unaided, and say it
   once: no restating a rule in a summary, checklist or table.
3. **Standard format.** Each skill is a folder that follows the
   [Agent Skills specification](https://agentskills.io/specification):
   - `skills/<name>/SKILL.md` with YAML frontmatter holding `name` and `description`.
   - `name`: 1–64 characters, lowercase letters, digits and single hyphens; matches the folder.
   - `description`: at most 1,024 characters; says what the skill does and when to use it.
   - Body under 500 lines and about 5,000 tokens.
   - Optional `scripts/`, `references/` and `assets/`. References sit one level deep, and
     `SKILL.md` says when to read each one.
4. **Evaluated.** Every skill ships with evals under `skills/<name>/evals/`, in the case-folder
   layout that skill-creator writes and `claude plugin eval` runs. Case folder names start with
   the skill's name (`<name>-<what-it-checks>`) so cases stay unique across the library. At
   minimum:
   - One case per distinct behaviour the skill promises.
   - Trigger cases for the description: prompts that should and should not invoke it.
   - Each case must pass with the skill and fail, or score clearly worse, without it. A case
     that passes either way tests nothing.
5. **Built with skill-creator.** Create, change and tune skills, and their descriptions, with
   Anthropic's `skill-creator` skill, following its draft, eval, review and iterate loop.
6. **Deterministic where possible.** Anything a program can do reliably (parsing, validation,
   counting, file layout, templating) lives in the skill's `scripts/`, not in prose. Scripts are
   self-contained: standard-library Python 3 or POSIX shell, no install step, no network unless
   the task needs it, and runnable on macOS, Linux and in Claude Code on the web.
7. **Fix with evidence, not rules.** A bug report becomes a failing eval case first, then the
   smallest change that makes it pass. Skills carry no incident logs, rationalization tables or
   red-flag lists: lessons live in evals, where they are checked, not in prose, where they
   accumulate.
8. **Explain, don't shout.** Give the reason behind an instruction instead of stacking MUST and
   NEVER. Reserve those words for hard limits.
9. **Safe by default.** A skill never commits, pushes, publishes, deletes or sends anything
   outside the working tree unless the user asks for it in that session.
10. **Generic.** Skills assume no particular language, framework, repo layout or host. Paths a
    skill writes to are stated in the skill and kept to a minimum.

## Repository layout

```
.claude-plugin/
  plugin.json          # plugin manifest; version gates updates for users
  marketplace.json     # makes this repo installable as its own marketplace
skills/
  <name>/
    SKILL.md
    scripts/           # optional, deterministic helpers
    references/        # optional, loaded on demand
    assets/            # optional, templates and static files
    evals/<case>/      # required, one folder per test case
AGENTS.md              # this file
README.md              # user-facing: what the plugin is and how to install it
```

Nothing else belongs at the root without a reason recorded in the change that adds it.

## Workflow

- Work on a branch and land changes through a pull request.
- Before opening a PR, run `claude plugin validate . --strict` and fix every finding.
- Run the evals for each skill you changed:
  `claude plugin eval . --eval-dir skills --case '<name>-*'`. Evals are billed model runs: run
  the ones you touched, never the whole suite unprompted.
- Bump `version` in `.claude-plugin/plugin.json` (semver) in any PR that changes what users
  receive. Installed copies only update when the version string changes.
- Add a skill to the table in `README.md` in the same PR that adds it.
