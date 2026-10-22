# sdlc

A Claude Code plugin of small, independent skills for the software development lifecycle.
Each skill does one job, works without the others, and ships with evals that prove it does
that job better than Claude does without it.

## Install

In Claude Code:

```
/plugin marketplace add michaelmarconi/sdlc
/plugin install sdlc@sdlc
```

Or from a terminal:

```bash
claude plugin marketplace add michaelmarconi/sdlc
claude plugin install sdlc@sdlc
```

Add `--scope project` to the `install` command to share the plugin with everyone working in a
repository.

## Update

```bash
claude plugin marketplace update sdlc
claude plugin update sdlc@sdlc
```

To update automatically, run `/plugin`, open **Marketplaces**, select `sdlc` and choose
**Enable auto-update**. New versions load on the next session or after `/reload-plugins`.

## Skills

| Skill | What it does |
| --- | --- |
| _None yet_ | |

## Contributing

Read [AGENTS.md](AGENTS.md) first. It holds the principles every skill follows and the checks a
change must pass.
