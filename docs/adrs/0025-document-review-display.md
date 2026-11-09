---
# Change status only through the sdlc plugin's skills, which check each change; a change made by hand is not checked.
status: 📝 Draft
date: 2026-11-09
---

# Show each finished document in the app's file viewer, or name its path

## Question

When a skill[^skill] finishes writing or changing a document, how does it show that document to the
person for review?

## Decision

Chosen: show the document in the app's file viewer where the app offers one, and always name its
full path, never a website such as GitHub. The person reads it where they already work and answers
in the same conversation.

## Background

This repository is a plugin for Claude Code, Anthropic's AI coding assistant, whose skills write a
project's documents as files in its repository. No skill says how to show the finished document,
so Claude improvises, and has sent the person to GitHub, which they do not want. Claude's apps now
show a file beside the conversation, and let the person send feedback on lines selected in it.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Leave each skill to improvise | Rejected | Claude has sent the person to GitHub links |
| A separate skill for marking up a document in a GitHub pull request | Rejected | The person does not want GitHub, and needs no lasting comments |
| A copy of the document in Claude Docs, claude.ai's shared documents | Rejected | A copy outside the repository; each comment took minutes to handle |
| The app's file viewer where offered, the path always, no website | Chosen | Feedback reaches Claude at once, with the lines it is about |

## Consequences

- Good: every document skill hands over the same way, wherever it runs.
- Good: feedback is a change the person asks for, which a reviewer agent checks once made.
- Bad: the plugin cannot make a viewer appear; the app must offer one.
- Bad: where the viewer shows a copy, Claude shows a fresh copy after each change.

## Out of scope

- Environments other than a Claude Desktop code session, a claude.ai project thread and the
  Claude Code command line, such as the editor extensions.
- Which tool shows the file in each app; the app decides, and the skills name none.

## How we'll check

Applies to: how every skill that writes a document shows it to the person.

1. Inspection: the plugin's skill checker finds the same hand-over sentence in every document skill.
2. Test: when a skill presents a document, it names the full path and links to no website.
3. Demonstration: in each of the three environments, a skill shows the document, or names its path where no viewer exists.

## Open questions

- The evidence below mentions Remote Control. Proposed footnote: "Remote Control is a Claude Code setting that lets the Claude app follow and drive a session running on the person's computer." Is that right?

## Technical detail

**The sentence.** Each skill that writes a document carries one identical sentence in the part that
tells Claude how to present the finished document: "Show the person the document: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name the document's full path; never send them to a website, such as GitHub, to
read it." `scripts/skill_check.py` checks it is present, as it checks the sentence that says when a
document is reviewed.

**Feedback.** What the person sends back is a change they ask for, so the skill makes it and
has a separate reviewer agent check it once it is made, as each skill already says.

**Evidence.** On 9 November 2026 one prompt, naming no tool, asked Claude to write a short file and
show it for review, or give its path, and never link to a website:

- A Claude Desktop code session opened the file itself in its Files pane. Selecting a line there
  queued feedback in the message box, carrying the file, line and quoted text.
- A claude.ai project thread attached a copy from the project's shared files folder. Feedback
  arrived as a message carrying the file, lines and quoted text.
- The Claude Code command line, with Remote Control off, found no viewer and gave the full path.
  It declined to publish the file to claude.ai, since that is a website. With Remote Control on,
  the Desktop app showed the file.

[^skill]: A skill is one step of the plugin, such as `/sdlc:spec`, which writes and accepts specs.
