# Agent instructions

This repo is a Claude Code plugin that encodes a software development lifecycle. Read
[README.md](README.md) for the lifecycle itself and [context/sdlc.md](context/sdlc.md) for its
principles; this file holds the rules for building the plugin. They apply to every change. Where
a rule names a number, it is a hard limit; everything else is judgement.

## Principles

1. **Independent in spirit.** The plugin is the unit of distribution, not the skill. A skill
   does one job and never invokes or assumes a prior run of another skill; it may use a document
   another skill produces when one is present, but must work when it is not. Skills may share
   what the plugin provides: its agents, hooks, scripts and `context/sdlc.md`.
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
4. **Reviewed.** Agents don't mark their own homework. Every skill that writes a document has
   it reviewed before a person sees it:
   - A rubric at `skills/<name>/references/rubric.md`: a short list of named checks, each pass
     or fail. The skill reads it while writing; the reviewer reads it while checking.
   - A reviewer agent at `agents/<name>-reviewer.md`, with read-only tools. It starts fresh,
     reads the rubric through `${CLAUDE_PLUGIN_ROOT}`, and reads only the files its own
     definition names. The skill passes it paths, never pasted content.
   - The reviewer reports pass or fail for each check, with evidence for each failure, plus
     findings beyond the rubric. The skill fixes what it can and asks again, for up to n reviews
     in all, counting the first (the plugin setting that `/build` also uses); after that it
     stops and asks the person, showing the report. Only a decision the skill cannot make goes
     to the person, with optional suggestions passed on but never holding the document back.
   - The person gets the document and the final report.
5. **Evaluated.** Every skill ships with evals under the plugin's `evals/`, in the case-folder
   layout that skill-creator writes and `claude plugin eval` runs. Write the rubric first, then
   the evals: each rubric check is also an eval assertion, so one rubric both tests the skill and
   reviews its output. Case folder names start with the skill's name (`<name>-<what-it-checks>`)
   so cases stay unique across the library. At minimum:
   - One case per distinct behaviour the skill promises.
   - Trigger cases for the description: prompts that should and should not invoke it.
   - Each case must pass with the skill and fail, or score clearly worse, without it. A case
     that passes either way tests nothing. Cases that should not trigger the skill are the
     exception: they pass without it by design.
6. **Built with skill-creator.** Create, change and tune skills, and their descriptions, with
   Anthropic's `skill-creator` skill, following its draft, eval, review and iterate loop.
7. **Deterministic where it earns its place.** Use a script only when it must be exact every
   time, as with the status rules, or when evals show Claude getting the job wrong or wasting
   effort on it. Otherwise leave it to Claude and the reviewer, whose judgement copes with cases
   a script can't foresee. A script lives in the skill's `scripts/`, or the plugin's `scripts/`
   when a hook runs it. Scripts are
   self-contained: standard-library Python 3 or POSIX shell, no install step, no network unless
   the task needs it, and runnable on macOS, Linux and in Claude Code on the web.
   - **Test-driven.** Write a failing test before each behaviour. Tests use the standard-library
     `unittest` module and live beside the script as `scripts/test_<script>.py`.
   - **Documented.** Each script has a module docstring saying what it does, and every command
     has `--help` text covering its arguments, output and exit codes. `SKILL.md` names each
     command Claude should run and when.
8. **Fix with evidence, not rules.** A bug report becomes a failing eval case first, then the
   smallest change that makes it pass. Skills carry no incident logs, rationalization tables or
   red-flag lists: lessons live in evals, where they are checked, not in prose, where they
   accumulate.
9. **Explain, don't shout.** Give the reason behind an instruction instead of stacking MUST and
   NEVER. Reserve those words for hard limits.
10. **Safe by default.** A skill never commits, pushes, publishes, deletes or sends anything
   outside the working tree unless the user asks for it in that session. Running `/build` is
   that request for its merge.
11. **Generic.** Skills assume no particular language, framework, repo layout or host, beyond
    the lifecycle's own folders under `docs/`. Paths a skill writes to are stated in the skill
    and kept to a minimum.

## Repository layout

```
.claude-plugin/
  plugin.json          # plugin manifest; version gates updates for users
  marketplace.json     # makes this repo installable as its own marketplace
skills/
  <name>/
    SKILL.md
    scripts/           # optional, deterministic helpers and their tests
    references/        # rubric.md (required for skills that write documents), others on demand
    assets/            # optional, templates and static files
evals/
  <name>-<case>/       # required, one folder per test case, run by `claude plugin eval`
agents/
  <name>-reviewer.md   # one reviewer per skill that writes documents
hooks/
  hooks.json           # session map and status checks
scripts/               # plugin-wide scripts the hooks run, and their tests
context/
  sdlc.md              # the map Claude gets at session start; the lifecycle's principles
docs/
  skills/<name>.md     # one page per skill, linked from README.md
AGENTS.md              # this file
README.md              # user-facing: the lifecycle, and how to install the plugin
```

Nothing else belongs at the root without a reason recorded in the change that adds it.

## Workflow

- Work on a branch and merge it to main once every check below passes. No pull requests needed.
- Before merging, run `claude plugin validate . --strict` and fix every finding.
- Run the script tests for each skill you changed:
  `python3 -m unittest discover -s skills/<name>/scripts`, and for the plugin's own scripts if
  you changed them: `python3 -m unittest discover -s scripts`. All must pass.
- Run the evals for each skill you changed:
  `claude plugin eval . --case '<name>-*'`, adding `--scaffold` for cases with input files. Evals are billed model runs: run
  the ones you touched, never the whole suite unprompted.
- Bump `version` in `.claude-plugin/plugin.json` (semver) in any change that alters what users
  receive. Installed copies only update when the version string changes.
- Add a skill to the table in `README.md`, and give it a page under `docs/skills/`, in the same
  change that adds it.
