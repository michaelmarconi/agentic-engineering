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

Chosen: show the document in the app's file viewer where one exists, and always name its path,
never a website. The person reads it where they already work and answers
in the same conversation.

## Background

This repository is a plugin for Claude Code, Anthropic's AI coding assistant, whose skills write a
project's documents as files in its repository. No skill says how to show the finished document,
so Claude has sent the person to a website, which they do not want.
The person works in three places: a Claude Desktop code session, a claude.ai project thread and
the Claude Code command line.

## Options

| Option | Outcome | Why |
| --- | --- | --- |
| Leave Claude to choose a way each time | Rejected | Claude has sent the person to websites |
| A separate skill for marking up a document on a code-hosting website | Rejected | Takes the person out of the app, and they need no lasting comments |
| A copy of the document in Claude Docs, claude.ai's shared documents | Rejected | Publishes a separate document outside the repository |
| The app's file viewer where offered, the path always, no website | Chosen | Feedback reaches Claude at once, with the lines it is about |

## Consequences

- Good: every document skill shows its document the same way in each of the three places.
- Good: where a viewer exists, the person comments on lines without leaving the conversation.
- Bad: the plugin cannot make a viewer appear; the app must offer one.
- Bad: where the viewer shows a copy, Claude shows a fresh copy after each change.

## Out of scope

- Places other than those three, such as the editor extensions.
- Which tool shows the file in each app; the app decides, and the skills name none.

## How we'll check

Applies to: how every skill that writes a document shows it to the person.

1. Inspection: the plugin's script that checks each skill's instructions finds the same sentence on showing documents in every document skill.
2. Test: when a skill presents a document, it names the full path and links to no website.
3. Demonstration: in each of the three places, a skill shows the document, or names its path where no viewer exists.

## Open questions

- None.

## Technical detail

**The sentence.** Each skill that writes a document carries one identical sentence in the part that
tells Claude how to present the finished document: "Show the person the document: if the app you run in
can show them a file in a viewer, use it, and show a fresh copy after each change if what it shows
is a copy; always name the document's full path; never send them to a website to
read it." `scripts/skill_check.py` checks it is present, as it checks the sentence that says when a
document is reviewed.

**Feedback.** What the person sends back is a change they ask for, so the skill makes it and
has a separate Claude, started without this conversation, check it once it is made, as each skill already says.

**Evidence.** On 9 November 2026 one prompt, naming no tool, asked Claude to write a short file and
show it for review, or give its path, and never link to a website:

- A Claude Desktop code session opened the file itself in its Files pane. Selecting a line there
  queued feedback in the message box, carrying the file, line and quoted text.
- A claude.ai project thread attached a copy from the project's shared files folder. Feedback
  arrived as a message carrying the file, lines and quoted text.
- The Claude Code command line found no viewer and gave the full path. It declined to publish the
  file to claude.ai, since that is a website.

[^skill]: A skill is one step of the plugin, such as the one that writes a spec, a document describing what one capability of the product should do.
