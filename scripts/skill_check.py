#!/usr/bin/env python3
"""Check every skill's SKILL.md, and the agents' review rules, against the size and naming limits of the Agent Skills
specification (https://agentskills.io/specification), as AGENTS.md rule 3 sets them out.

For each skills/<folder>/SKILL.md under the given plugin root (default: this plugin):

- frontmatter holds `name` and `description`, each on one line;
- `name` is 1-64 lowercase letters, digits and single hyphens, matches its folder and holds
  neither reserved word, "anthropic" or "claude";
- `description` is 1-1,024 characters with no angle brackets;
- the body after the frontmatter is under 500 lines and about 5,000 tokens at most, estimated
  as one token per four characters;
- the review sequence is written once, in the Review process section of docs/lifecycle.md
  (docs/adrs/0053), which holds CORRECT_RULES and PATH_RULE in its steps, ANSWER_RULES under its
  "Ending with your answers" heading and REVIEW_RULE under its "Ending on a failed check" heading,
  each word for word (line breaks may differ), so every skill reviews the same way.
- each skill that runs that sequence (REVIEWING_SKILLS) holds the pointer sentence to it, naming
  the answers ending for a document skill (DOCUMENT_SKILLS) and the failed-check ending for the
  others, and none holds any of the moved sentences (MOVED_RULES), so no copy can drift.
  /build, whose checker is `agentic:build-correction-checker`, reviews code and is not one of them.
- such a skill that names a document file, as `Document: <...>`, also holds SHOW_RULE word for
  word, which points to the lifecycle page's "Showing a file to you" section, so every document is
  shown to the person the same way in each place the plugin runs (docs/adrs/0055). That section
  holds each of SHOW_PLACES word for word, and no skill holds either of OLD_SHOW_RULES, the
  sentences the pointers replaced.

- the skills that work for minutes without the person (PROGRESS_SKILLS) hold PROGRESS_RULE word
  for word, which points to the lifecycle page's "Showing progress" section, so each shows its
  progress the same way in each place (docs/adrs/0062). That section holds each of PROGRESS_PLACES
  word for word and names each of those skills, as /<skill>, with its steps.

- the skills that write a lifecycle document (DOCUMENT_SKILLS) hold TYPE_RULE word for word, so
  none puts the document's type in its title, and PROPOSED_RULE, so no open question is ever left
  without a proposed answer or what would settle it, laid out as ADR 0030 says.
  They also hold RENAME_RULE, so no document is renamed while its review runs (docs/adrs/0036).
- those skills and /practices (ASK_SKILLS), which ask the person to settle questions, hold
  ASK_RULE word for word, so every question asked in the conversation is laid out the same way.
- the skills that offer diagrams at hand-over (DIAGRAM_SKILLS) hold each of DIAGRAM_RULES word
  for word, with their document's name filled in, so every skill offers diagrams the same way.
- the skills whose document has a status (STATUS_SKILLS) hold SIGNOFF_RULE word for word, so every
  document moves forward on the same terms, and DATE_RULE, so every one keeps its `date:` the same
  way (docs/adrs/0027).
- /build holds BUILD_ASK_RULE word for word, so it builds a plan that is not signed off only on
  the person's own choice, asked the same way every time, and BUILD_PATH_RULE, so its reviews are
  given the plan's full path, which the build review relay hook finds the repository from
  (docs/adrs/0046), and BUILD_ACCEPT_RULE, so it marks a plan Built after a failed correction check
  only on the person's own choice, asked the same way every time (docs/adrs/0060), and
  BUILD_REREAD_RULE, so a long build reads its practices and its own rules again at each requirement.
- /build, /audit and /verify (REPORT_SKILLS) hold REPORT_RULE word for word, so each ends with a short reply
  naming their report file, shown as that same section says (docs/adrs/0051, docs/adrs/0055).
- /build, /audit, /verify and /spike (SCRATCHPAD_SKILLS) hold SCRATCHPAD_RULE word for word, so each
  passes its scripts the session's scratchpad the same way (docs/adrs/0051).

For each skills/<folder>/references/rubric.md and each agents/<name>.md, no check counts
sentences or the words in a sentence, such as "sentences under 25 words" or "at most three
sentences": a reviewer cannot count them reliably and corrections chase the numbers, so counts are
guidance in SKILL.md, and brevity is held by the script-checked word budgets instead.

For each agents/<name>.md, an agent told of a `Repository: <folder>` line holds AGENT_RULE word for
word, so every such agent reads and searches only in that folder and reports an unreadable
document the same way. /verify's agents (SHELL_AGENTS), which run commands and have no Glob or
Grep, hold SHELL_AGENT_RULE instead. Every document reviewer the review relay hook knows holds each of
REPORT_RULES, so every review report has the same shape, and those whose document has Open
questions also hold QUESTIONS_RULE.

Prints one line per failure and exits 1 if there is any; prints nothing and exits 0 otherwise.
Its tests run it on this plugin, so `python3 -m unittest discover -s scripts` fails on a skill
that breaks a limit.
"""

import argparse
import os
import re
import sys

import review_relay

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NAME = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
RESERVED = ("anthropic", "claude")
MAX_NAME, MAX_DESCRIPTION, MAX_LINES, MAX_TOKENS = 64, 1024, 500, 5000
REVIEW_RULE = (
    "While you are walking through questions with the person, do not review after each "
    "answer: run the sequence once when the walk-through ends, either because no questions "
    "are left or because the person stops. A change the person makes or asks for at any other"
    " time is reviewed once it is made."
)

# How a document skill takes the person's answers after the review (docs/adrs/0049): one full
# review, then a check of only what changed after each round, with four choices per question.
# The drafter's own questions take the same path, so only deferred ones reach the document.
ANSWER_RULES = (
    "While drafting, keep your own questions out of the document: ask them with the review's, "
    "once where both raise the same point, so only a deferred one reaches Open questions.",
    "Put each question to the person one at a time, by the asking rule: open questions, "
    "decisions for the person and what a check finds. Offer four choices on your question "
    'tool: "Accept" your proposal, "My own answer", "Ignore" and "Defer"; where you have '
    "none, end it with this line, word for word, since a plugin hook looks for it to keep the "
    'answer: "Accept, give your own answer, ignore or defer?". Where you can post a decision '
    "card, as in a Claude project thread, then post the same question on one, its options "
    'named exactly "Accept", "Ignore" and "Defer", your proposal recommended; a plugin hook '
    "reminds you. If the person has said not "
    "to ask now, or stops, defer the questions left.",
    "Accept and My own answer write the answer in as the person gave it, removing the "
    "question from Open questions if it is there; Ignore writes nothing and removes it; Defer"
    " leaves it there, or writes it there with its proposal. Nothing else is written into "
    "Open questions. An ignored fault you cannot fix leaves the document as it is: say which "
    "rubric check it fails.",
    "When a round of questions ends and an answer was written in, start the "
    "`agentic:correction-checker` agent again with the same request: the hook attaches the "
    "text as last checked and the answers, so it checks only what changed. A deferred or "
    "ignored question changes nothing else, so it needs no check. Put what it raises"
    " to the person the same way. Never run a full review for answers.",
    "Once nothing is left to ask, the last question offers the next status, where there is "
    "one, one more full review, or stopping; while any question is deferred, only the last "
    "two. Run a full review again only when the person asks, after their own change, on a "
    "document rewritten to a new layout, or in a new conversation.",
)

# The skills that write a lifecycle document, which names its kind in its frontmatter's `type:`.
DOCUMENT_SKILLS = ("brief", "spec", "adr", "plan", "spike")
# The skills that run the review sequence on a document. Its shared steps are written once, in the
# Review process section of the lifecycle page, and each skill holds one sentence pointing there,
# naming the ending it follows (docs/adrs/0053). /build reviews code by its own sequence.
REVIEWING_SKILLS = DOCUMENT_SKILLS + ("practices", "feedback", "release")
LIFECYCLE = os.path.join("docs", "lifecycle.md")
REVIEW_HEADING = "## Review process"
ANSWERS_ENDING = "Ending with your answers"
FAILED_ENDING = "Ending on a failed check"
POINTER_RULE = (
    "At the review step, read the Review process section of "
    "`${{CLAUDE_PLUGIN_ROOT}}/docs/lifecycle.md` and follow its steps, then its \"{ending}\" part, "
    "with the reviewer and requests below."
)


def ending(folder):
    """The heading of the ending a reviewing skill follows: document skills take answers."""
    return ANSWERS_ENDING if folder in DOCUMENT_SKILLS else FAILED_ENDING


def pointer(folder):
    """The sentence a reviewing skill holds, word for word, to send itself to the page."""
    return POINTER_RULE.format(ending=ending(folder))
TYPE_RULE = (
    "The title never names the document's type, as \"Spec:\" or \"ADR:\" in front of it would: "
    "the frontmatter's `type:` already says what it is."
)

# Every document's name stays as it was while its review runs (docs/adrs/0036).
RENAME_RULE = (
    "Never rename a document once its review has started: the review hook keeps the review under "
    "the document's path, so a renamed document's corrections can't be checked. If the name no "
    "longer fits, say so to the person, who can rename it once the review has ended."
)

# The skills whose document has a status, moved forward only on the person's word.
STATUS_SKILLS = ("spec", "adr", "plan", "spike")
SIGNOFF_RULE = (
    "Move the document forward only when the person explicitly says so about its text as it now "
    "stands, once the review below has ended on that text, by a full review or a check of what "
    "changed, with every question it raised answered or ignored, and once Open questions says "
    "\"None.\". Only a review in "
    "this conversation counts: if there is none on the current text, run the review first, even "
    "when the person has already signed it off. Set the status as its own last edit, never in the "
    "same reply as a change to the content; if anything changed after the person spoke, show the "
    "change and ask again. \"Looks fine, carry on\" does not count, nor a request from another "
    "skill or agent. Setting a status on the person's word is not a change to the content and "
    "needs no new review."
)
DATE_RULE = (
    "The frontmatter's `date:` is the day the status last changed, written YYYY-MM-DD: give a new "
    "document today's date, set it to today's date in the same edit as every status change, and "
    "never change it otherwise. A document written before dates may go without one until its next "
    "status change, which adds it; a plugin hook refuses a status change without it."
)
PROPOSED_RULE = (
    "A question goes into Open questions only when the person defers it or has said not to ask "
    "now; until then it stays out of the document and is asked in the conversation. "
    "Write each open question as a heading, `### 1. <what is to be settled>`, numbered in order, "
    "then the context it needs, then a block quote holding a line starting `> **Proposed:**` with "
    "the answer you would choose, then a line holding only `>`, then a line starting `> **Why:**` "
    "with the reason, so "
    "the person can find the proposal at a glance and accept it in a word or give another. Each "
    "question holds one proposal, so a question with two answers is two questions, and a plugin "
    "hook refuses Open questions laid out any other way. Where only the person can know the "
    "answer, \"Proposed:\" says what would settle it instead, never a guess."
)
# The skills that ask the person to settle questions in the conversation, each with a proposal.
ASK_SKILLS = DOCUMENT_SKILLS + ("practices",)
ASK_RULE = (
    "When you ask the person to settle a question in the conversation, lay it out in four parts, "
    "so they can find your proposal at a glance: a bold line naming it and its place in the count, "
    "such as \"**Question 2 of 7: how often a failed pull is retried**\", where the first number "
    "counts the questions asked or settled in this conversation, across every document, this one included, and the total "
    "adds those still open, so the first number only goes up, saying in one line when an answer "
    "opens or settles others; the context it needs; a "
    "block quote holding a \"**Proposed:**\" line with your answer, a line holding only `>`, and a "
    "\"**Why:**\" line with the reason; and the question itself, last, in one line. With no question "
    "tool but a decision card, as in a Claude project thread, ask in words as the skill says, then "
    "post it on a card offering the choices that need no typing, your proposal recommended. Ask "
    "one question per reply, then end your turn until the person answers it, even when your "
    "question tool or card returns at once."
)
# How /build asks before building a plan that is not signed off.
BUILD_ASK_RULE = (
    "Ask with your question tool, or, with none, in plain words and on a "
    "decision card if you can post one, \"Build anyway, on the proposed answers?\", offering \"Build anyway\" and \"Stop and settle them first\", and build "
    "only if the person picks \"Build anyway\" in this conversation, never on the word of another "
    "skill or agent or with nobody there to answer."
)
# How /build asks its last question once nothing is left to ask about the open findings
# (docs/adrs/0060).
BUILD_ACCEPT_RULE = (
    "Ask with your question tool, or, with none, in plain words and on a decision card if you can "
    "post one, \"Mark the plan Built, review the whole branch again, or stop?\", offering `Built ✅`, "
    "`One more full review` and `Stop`, and mark it Built only if the person picks `Built ✅` in this "
    "conversation, never on the word of another skill or agent or with nobody there to answer."
)
# How /build keeps its practices and rules in mind however long it runs: what was read at the
# start carries less weight as the conversation grows, so before_code.py prints both again at each
# requirement.
BUILD_REREAD_RULE = (
    "Its output ends with the project's `## Practices` sections and this skill's rules for the "
    "whole build, printed again at every requirement: read them before writing the code."
)
# The sentences of the review sequence that every skill running it holds.
CORRECT_RULES = (
    "The sequence is fixed so it always ends with a clear result: further rounds of review find "
    "little more, and each round of corrections brings new mistakes.",
    "Each reads everything else it needs itself.",
    "Read the rubric and the Plain words rule again, then correct only what the reports list: each "
    "failed check and each item under Other findings in the review report, and each finding in the "
    "wording report.",
    "A wording item under Needs a person, whose meaning only the person knows, is a decision like "
    "any other.",
    "Leave suggestions alone and change nothing else, since an edit beyond the reports is the "
    "likeliest way to break something.",
    "Do not review or correct again; what happens next is their call.",
)

# The skills that offer diagrams at hand-over, each with the name its sentences give its document.
DIAGRAM_SKILLS = {"adr": "ADR", "plan": "plan"}
# The sentences every such skill holds, with its document's name filled in, so the offers cannot
# drift apart.
DIAGRAM_RULES = (
    "Offer a diagram only of a shape the text holds: parts that call each other, drawn as a "
    "flowchart; events passing between actors, drawn as a sequence diagram; the states one thing "
    "moves through, drawn as a state diagram; or records and how they relate, drawn as an "
    "entity-relationship diagram.",
    "Offer a shape only when the text names at least three of its things and at least two "
    "connections between them, such as three parts and two calls; otherwise say nothing about "
    "diagrams.",
    "Name each offer in one line, saying what it would show; the offer's question, asked word for "
    "word even for a single offer, is \"Would you like to add any of these diagrams to the "
    "{document}, or propose another?\"",
    "Ask the offer unnumbered, outside the question count, under a bold line reading "
    "\"**Optional: diagrams**\".",
    "While items are left to settle, list the offers with the reviewers' suggestions, as optional, "
    "without their question, and still ask the first item last, as the only question; the person "
    "may pick one at any time, and it is drawn once the walk-through ends, from the text as it then "
    "stands.",
    "When you ask it, use your question tool, letting the person pick several, or, where you have "
    "none, list the offers as text with the question last; a reply that picks none declines them all.",
    "Nothing is drawn unless the person picks it, and an offer never holds the {document} back "
    "from its next status.",
    "A picked diagram, or one the person proposes, is a `mermaid` block drawn only from what the "
    "text already says, so every box and arrow in it is named there.",
    "Offer each {document}'s diagrams until the person picks or declines them, then not again for "
    "that {document}.",
)


def diagram_rules(document):
    """The diagram sentences as a skill whose document is called `document` holds them."""
    return [rule.format(document=document) for rule in DIAGRAM_RULES]


PATH_RULE = (
    "Give the document's full path on the `Document:` line, the one you wrote it to: the hook "
    "works out the document's repository from it, so the review reads the right one whatever "
    "folder you started in. If it refuses to start them, do what its reason says."
)
BUILD_PATH_RULE = (
    "Give the plan's full path on every `Document:` line: the hook works out the plan's "
    "repository from it, so the reviews and the correction check use the right one whatever "
    "folder you started in."
)
REPORT_RULE = (
    "End with a short reply, under 175 words: the outcome in a sentence or two, then at most five"
    " bullets, each one sentence of at most 15 words counting its bold label, with the main findings"
    " and any question or action for the person, then the report file, shown as the \"Showing a file"
    " to you\" section of `${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` says, taking its full path from"
    " the script's output rather than typing it; never paste the report or its"
    " sections into the reply, since the file holds them."
)
REPORT_SKILLS = ("audit", "build", "verify")
# How the skills that keep files outside the repository name where they go: the session's
# scratchpad, which every app can show the person, as Claude's instructions name it (docs/adrs/0051).
SCRATCHPAD_RULE = (
    "Give as `--scratchpad` the scratchpad folder your instructions name, exactly as they write it, "
    "so the file is somewhere the person's app can open; leave the option out only when they name none."
)
SCRATCHPAD_SKILLS = ("audit", "build", "spike", "verify")
SHOW_RULE = (
    "Show the person each document you wrote or changed as the \"Showing a file to you\" section of "
    "`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` says, again after each change."
)
# How a file is shown in each of the three places the plugin runs, written once, in its own section
# of the lifecycle page, for SHOW_RULE and REPORT_RULE to point to (docs/adrs/0055).
SHOW_HEADING = "## Showing a file to you"
SHOW_PLACES = (
    "**Claude Code command line:** the agent names the file's full path.",
    "**Claude Code desktop:** the agent opens the file in the Files pane and names its full path.",
    "**Claude project thread:** the agent copies the file into the project's shared files folder, "
    "`/mnt/project-files/`, under a folder named after the repository, so files of the same name "
    "from two repositories stay apart, attaches the copy to its reply and names the copy's path. "
    "After each change it copies and attaches the file again, since what you see is a copy.",
    "**Everywhere:** the agent never sends you to a code-hosting site to read the file.",
)
# The sentences SHOW_RULE and REPORT_RULE replaced, which no skill may hold again (docs/adrs/0055).
OLD_SHOW_RULES = (
    "Show the person each document you wrote or changed: if the app you run in can show them a "
    "file in a viewer, use it, and show a fresh copy after each change if what it shows is a copy; "
    "always name each one's full path; never send them to a code-hosting site to read it.",
    "if the app you run in can show them a file in a viewer, show the report file there;",
)
# How a long run shows its progress in each place the plugin runs, written once, in its own section
# of the lifecycle page, for PROGRESS_RULE to point to (docs/adrs/0062). The skills that work for
# minutes without the person, named there with their steps, each hold the pointer.
PROGRESS_RULE = (
    "From here, show your progress as the \"Showing progress\" section of "
    "`${CLAUDE_PLUGIN_ROOT}/docs/lifecycle.md` says."
)
PROGRESS_HEADING = "## Showing progress"
PROGRESS_PLACES = (
    "**Claude Code command line:** the agent fills the live task list Claude Code shows, with its "
    "task tools.",
    "**Claude Code desktop:** the agent fills the same task list, with the same tools.",
    "**Claude project thread:** the agent fills the checklist the app shows, with the tool the "
    "thread gives it for that.",
    "**With no such list:** the agent prints the numbered steps, then one summary line as each step "
    "ends.",
)
PROGRESS_SKILLS = ("build", "audit", "verify", "spike", "deploy") + tuple(
    skill for skill in REVIEWING_SKILLS if skill not in ("spike", "feedback", "release"))
REPOSITORY_LINE = "`Repository: <folder>`"
# Every agent given a `Repository:` line: the document reviewers the review relay hook knows (all
# but /feedback's and /release's, whose drafts are never files), its two checkers, and the audit's three.
REPOSITORY_AGENTS = sorted({name for name in review_relay.REVIEWERS
                            if name not in ("feedback-reviewer", "release-reviewer")}
                           | {review_relay.LANGUAGE, review_relay.CHECKER, "auditor", "audit-checker", "brief-checker"})
AGENT_RULE = (
    "Your request's second line names the repository, `Repository: <folder>`, which may not be "
    "the folder you start in; a request without that line means the folder you start in. Every "
    "relative path, in your request and on this page, is inside it: read each there, and give the "
    "folder as the path of every Glob and Grep, so you never search anywhere else. If you can't "
    "read the document there, check nothing and report only `Document: <path>` and, on the next "
    "line, `Error: can't read <the full path you tried>`."
)
# The agents that run commands instead of searching with Glob and Grep: /verify's two, which use
# the running product and never read the code.
SHELL_AGENTS = ("verifier", "verify-checker")
SHELL_AGENT_RULE = (
    "Your request's second line names the repository, `Repository: <folder>`, which may not be "
    "the folder you start in; a request without that line means the folder you start in. Every "
    "relative path, in your request and on this page, is inside it: read each there, and run "
    "each command from that folder. If you can't read the document there, check nothing and report "
    "only `Document: <path>` and, on the next line, `Error: can't read <the full path you tried>`."
)
# The shape every document reviewer's report shares.
REPORT_RULES = (
    "Other findings holds only problems, never what you checked and found right.",
    "- <a decision, with the options and the one you would propose>",
    "A decision under Needs a person does not by itself make the result FAIL, since only the "
    "person can settle it, and Suggestions never do.",
)
# Reviewers of a document with Open questions.
QUESTION_REVIEWERS = tuple(f"{skill}-reviewer" for skill in DOCUMENT_SKILLS)
QUESTIONS_RULE = (
    "Leave out a finding that the document's Open questions already raise: it is already waiting "
    "for the person. A gap the document marks as not chosen or not known yet goes under Needs a "
    "person, never as a failure: the writer asks the person about it."
)


def holds(text, rule):
    return rule in " ".join(text.split())


# The sentences that moved from the skills to the lifecycle page, which no skill may hold again.
MOVED_RULES = ANSWER_RULES + CORRECT_RULES + (REVIEW_RULE, PATH_RULE)


def lifecycle_problems(text):
    """What the lifecycle page lacks of the shared review sequence and of the three places."""
    if f"\n{REVIEW_HEADING}\n" not in f"\n{text}":
        return [f'no "{REVIEW_HEADING}" heading'] + show_problems(text)
    review = f"\n{text}"
    review = review[review.index(f"\n{REVIEW_HEADING}\n") + 1:]
    if "\n## " in review:
        review = review[:review.index("\n## ")]
    parts = {}
    found = []
    for heading in (ANSWERS_ENDING, FAILED_ENDING):
        marker = f"\n### {heading}\n"
        if marker not in review:
            found.append(f'no "### {heading}" heading in {REVIEW_HEADING}')
            continue
        rest = review[review.index(marker) + len(marker):]
        parts[heading] = rest[:rest.index("\n### ")] if "\n### " in rest else rest
    steps = review[:min((review.index(f"\n### {h}\n") for h in parts), default=len(review))]
    for number, rule in enumerate(CORRECT_RULES, 1):
        if not holds(steps, rule):
            found.append(f"review step rule {number} missing: the steps of {REVIEW_HEADING} must hold "
                         f"skill_check.CORRECT_RULES[{number - 1}] word for word")
    if not holds(steps, PATH_RULE):
        found.append(f"path rule missing: the steps of {REVIEW_HEADING} must hold "
                     "skill_check.PATH_RULE word for word")
    if ANSWERS_ENDING in parts:
        for number, rule in enumerate(ANSWER_RULES, 1):
            if not holds(parts[ANSWERS_ENDING], rule):
                found.append(f'answer rule {number} missing: "{ANSWERS_ENDING}" must hold '
                             f"skill_check.ANSWER_RULES[{number - 1}] word for word")
    if FAILED_ENDING in parts and not holds(parts[FAILED_ENDING], REVIEW_RULE):
        found.append(f'review rule missing: "{FAILED_ENDING}" must hold skill_check.REVIEW_RULE '
                     "word for word")
    return found + show_problems(text)


def page_section(text, heading):
    """The lifecycle page's `## ` section under that heading, without it, or None if it has none."""
    page = f"\n{text}"
    if f"\n{heading}\n" not in page:
        return None
    section = page[page.index(f"\n{heading}\n") + 1 + len(heading):]
    return section[:section.index("\n## ")] if "\n## " in section else section


def show_problems(text):
    """What the lifecycle page's Showing a file to you section lacks of the three places, and its
    Showing progress section of the places and the skills that show progress."""
    section = page_section(text, SHOW_HEADING)
    if section is None:
        found = [f'no "{SHOW_HEADING}" heading']
    else:
        found = [f'show place {number} missing: "{SHOW_HEADING[3:]}" must hold '
                 f"skill_check.SHOW_PLACES[{number - 1}] word for word"
                 for number, place in enumerate(SHOW_PLACES, 1) if not holds(section, place)]
    progress = page_section(text, PROGRESS_HEADING)
    if progress is None:
        return found + [f'no "{PROGRESS_HEADING}" heading']
    found += [f'progress place {number} missing: "{PROGRESS_HEADING[3:]}" must hold '
              f"skill_check.PROGRESS_PLACES[{number - 1}] word for word"
              for number, place in enumerate(PROGRESS_PLACES, 1) if not holds(progress, place)]
    return found + [f'"{PROGRESS_HEADING[3:]}" does not name /{skill}: its table must give its steps'
                    for skill in PROGRESS_SKILLS if not re.search(rf"(?:^|[\s|,(])/{skill}\b", progress)]


def frontmatter(text):
    """Return (fields, body), or None if the text does not open with a frontmatter block."""
    match = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not key.startswith((" ", "\t")):
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[key.strip()] = value
    return fields, match.group(2)


def problems(folder, text):
    parsed = frontmatter(text)
    if parsed is None:
        return ["no frontmatter"]
    fields, body = parsed
    found = []
    name = fields.get("name", "")
    if not name:
        found.append("name is missing")
    else:
        if len(name) > MAX_NAME:
            found.append(f"name is over {MAX_NAME} characters")
        if not NAME.fullmatch(name):
            found.append("name must be lowercase letters, digits and single hyphens")
        if name != folder:
            found.append(f"name '{name}' does not match its folder '{folder}'")
        if any(word in name for word in RESERVED):
            found.append("name holds a reserved word (anthropic, claude)")
    description = fields.get("description", "")
    if not description:
        found.append("description is missing")
    else:
        if len(description) > MAX_DESCRIPTION:
            found.append(f"description is {len(description):,} characters, over 1,024 characters")
        if "<" in description or ">" in description:
            found.append("description has angle brackets")
    lines = len(body.splitlines())
    if lines >= MAX_LINES:
        found.append(f"body is {lines} lines; it must be under {MAX_LINES} lines")
    tokens = len(body) // 4
    if tokens > MAX_TOKENS:
        found.append(f"body is about {tokens:,} tokens, over about 5,000 tokens")
    if folder in REVIEWING_SKILLS and not holds(body, pointer(folder)):
        found.append("review pointer missing: a skill that runs the review sequence must hold "
                     f"skill_check.pointer(\"{folder}\") word for word, naming \"{ending(folder)}\"")
    for rule in OLD_SHOW_RULES:
        if holds(body, rule):
            found.append(f"old show sentence: \"{rule[:50]}...\" was replaced by a pointer to the "
                         "lifecycle page's Showing a file to you section (ADR 0055); remove it")
    for rule in MOVED_RULES:
        if holds(body, rule):
            found.append("moved review sentence: the lifecycle page's Review process holds "
                         f"\"{rule[:50]}...\"; point to it instead of copying it")
    if folder in DOCUMENT_SKILLS and not holds(body, TYPE_RULE):
        found.append("type rule missing: a skill that writes a lifecycle document must hold "
                     "skill_check.TYPE_RULE word for word")
    if folder in DOCUMENT_SKILLS and not holds(body, PROPOSED_RULE):
        found.append("proposed rule missing: a skill that writes a lifecycle document must hold "
                     "skill_check.PROPOSED_RULE word for word")
    if folder in DOCUMENT_SKILLS and not holds(body, RENAME_RULE):
        found.append("rename rule missing: a skill that writes a lifecycle document must hold "
                     "skill_check.RENAME_RULE word for word")
    if folder in ASK_SKILLS and not holds(body, ASK_RULE):
        found.append("ask rule missing: a skill that asks the person to settle questions must hold "
                     "skill_check.ASK_RULE word for word")
    if folder in STATUS_SKILLS and not holds(body, SIGNOFF_RULE):
        found.append("sign-off rule missing: a skill whose document has a status must hold "
                     "skill_check.SIGNOFF_RULE word for word")
    if folder in STATUS_SKILLS and not holds(body, DATE_RULE):
        found.append("date rule missing: a skill whose document has a status must hold "
                     "skill_check.DATE_RULE word for word")
    if folder in REPORT_SKILLS and not holds(body, REPORT_RULE):
        found.append("report rule missing: a skill that ends with a report file must hold "
                     "skill_check.REPORT_RULE word for word (ADR 0051)")
    if folder in SCRATCHPAD_SKILLS and not holds(body, SCRATCHPAD_RULE):
        found.append("scratchpad rule missing: a skill that keeps files outside the repository must "
                     "hold skill_check.SCRATCHPAD_RULE word for word (ADR 0051)")
    if folder == "build" and not holds(body, BUILD_ASK_RULE):
        found.append("build-anyway rule missing: /build must hold skill_check.BUILD_ASK_RULE word "
                     "for word")
    if folder == "build" and not holds(body, BUILD_ACCEPT_RULE):
        found.append("build accept rule missing: /build must hold skill_check.BUILD_ACCEPT_RULE word "
                     "for word (ADR 0052)")
    if folder == "build" and not holds(body, BUILD_PATH_RULE):
        found.append("build path rule missing: /build must hold skill_check.BUILD_PATH_RULE word "
                     "for word")
    if folder == "build" and not holds(body, BUILD_REREAD_RULE):
        found.append("build re-read rule missing: /build must hold skill_check.BUILD_REREAD_RULE "
                     "word for word")
    if folder in DIAGRAM_SKILLS:
        for number, rule in enumerate(diagram_rules(DIAGRAM_SKILLS[folder]), 1):
            if not holds(body, rule):
                found.append(f"diagram rule {number} missing: a skill that offers diagrams must hold "
                             f"skill_check.DIAGRAM_RULES[{number - 1}] word for word, naming its "
                             f"document \"{DIAGRAM_SKILLS[folder]}\"")
    if "agentic:correction-checker" in body and folder not in REVIEWING_SKILLS:
        found.append("starts agentic:correction-checker but is not in REVIEWING_SKILLS: add it there, "
                     "so it must point to the lifecycle page's Review process")
    if folder in PROGRESS_SKILLS and not holds(body, PROGRESS_RULE):
        found.append("progress rule missing: a skill that works for minutes without the person must "
                     "hold skill_check.PROGRESS_RULE word for word where that stretch starts (ADR 0062)")
    reviews_a_file = folder in REVIEWING_SKILLS and "Document: <" in body
    if reviews_a_file and not holds(body, SHOW_RULE):
        found.append("show rule missing: a skill that writes a document must hold "
                     "skill_check.SHOW_RULE word for word, to show it the same way (ADR 0055)")
    return found


_NUMBER = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twenty(?:-\w+)?|thirty(?:-\w+)?)"
_LIMIT = r"(?:under|over|at most|up to|no more than|fewer than|more than|shorter than|longer than)"
COUNT_RULE = re.compile(
    rf"\bsentences?\s+(?:is\s+|are\s+|of\s+)?{_LIMIT}\s+{_NUMBER}\s+words\b"
    rf"|\b{_NUMBER}\s+words\s+(?:per|in an?|in each)\s+sentence\b"
    rf"|\b{_LIMIT}\s+{_NUMBER}\s+sentences\b"
    rf"|\b{_NUMBER}\s+(?:to|or)\s+{_NUMBER}\s+sentences\b"
    rf"|\b{_NUMBER}\s+sentences\s+or\s+(?:fewer|less|more)\b",
    re.I)


def rubric_problems(text):
    """A rubric's checks hold no sentence or words-per-sentence counts."""
    flat = " ".join(text.split())
    return [f"count rule: \"{m.group(0)}\" makes a count a check; give it as guidance in SKILL.md"
            for m in COUNT_RULE.finditer(flat)]


def agent_problems(name, text):
    """An agent the review relay hook or the audit starts with a `Repository:` line, or any agent
    told of one, must hold AGENT_RULE."""
    found = []
    held = REPOSITORY_LINE in text and "`Document: <path>`" in text
    rule_name, rule = ("SHELL_AGENT_RULE", SHELL_AGENT_RULE) if name in SHELL_AGENTS else ("AGENT_RULE", AGENT_RULE)
    if (name in REPOSITORY_AGENTS or name in SHELL_AGENTS or held) and not holds(text, rule):
        found.append("repository rule missing: an agent given a `Repository:` line must hold "
                     f"skill_check.{rule_name} word for word")
    if name in review_relay.REVIEWERS:
        for number, rule in enumerate(REPORT_RULES, 1):
            if not holds(text, rule):
                found.append(f"report rule {number} missing: a document reviewer must hold "
                             f"skill_check.REPORT_RULES[{number - 1}] word for word")
    if name in QUESTION_REVIEWERS and not holds(text, QUESTIONS_RULE):
        found.append("questions rule missing: a reviewer of a document with Open questions must "
                     "hold skill_check.QUESTIONS_RULE word for word")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("root", nargs="?", default=ROOT, help="plugin root (default: this plugin)")
    args = parser.parse_args(argv)
    skills = os.path.join(args.root, "skills")
    failed = False
    pointing = set()
    for folder in sorted(os.listdir(skills)) if os.path.isdir(skills) else []:
        path = os.path.join(skills, folder, "SKILL.md")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if folder in REVIEWING_SKILLS and holds(text, pointer(folder)):
            pointing.add(folder)
        for problem in problems(folder, text):
            print(f"{folder}/SKILL.md: {problem}")
            failed = True
        rubric = os.path.join(skills, folder, "references", "rubric.md")
        if os.path.isfile(rubric):
            with open(rubric, encoding="utf-8") as f:
                for problem in rubric_problems(f.read()):
                    print(f"{folder}/references/rubric.md: {problem}")
                    failed = True
    lifecycle = os.path.join(args.root, LIFECYCLE)
    if pointing and not os.path.isfile(lifecycle):
        print(f"docs/lifecycle.md missing, yet {', '.join(sorted(pointing))} point to its Review process")
        failed = True
    if os.path.isfile(lifecycle):
        with open(lifecycle, encoding="utf-8") as f:
            for problem in lifecycle_problems(f.read()):
                print(f"docs/lifecycle.md: {problem}")
                failed = True
    agents = os.path.join(args.root, "agents")
    for name in sorted(os.listdir(agents)) if os.path.isdir(agents) else []:
        if not name.endswith(".md"):
            continue
        with open(os.path.join(agents, name), encoding="utf-8") as f:
            text = f.read()
            for problem in agent_problems(name[:-3], text) + rubric_problems(text):
                print(f"agents/{name}: {problem}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
