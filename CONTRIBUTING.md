# Contributing

Thank you for helping improve the plugin. Feedback comes in as issues, and changes are made by
the maintainer.

## Report a bug or suggest an improvement

Run `/agentic:feedback` in Claude Code, in the repository where you met the problem. It drafts an
issue from the [bug](.github/ISSUE_TEMPLATE/bug.md) or
[improvement](.github/ISSUE_TEMPLATE/improvement.md) template, swaps anything from your
repository for stand-ins, shows you the draft and files it only when you agree.

You can also [open an issue](https://github.com/michaelmarconi/agentic-engineering/issues/new/choose) by hand
from the same templates. Quote nothing from your own project that you would not publish: issues
are public.

## Pull requests

Pull requests are not accepted from outside the project. Every change starts as a failing eval
case written from an issue, and is released only once the evals pass, so an issue is the
quickest way to get something changed.

## Working on the plugin

[AGENTS.md](AGENTS.md) holds the rules every skill is built to and the checks a change must
pass, for the maintainer and the coding agents working on the plugin. The plugin's design
decisions are recorded in [docs/adrs/](docs/adrs/).
