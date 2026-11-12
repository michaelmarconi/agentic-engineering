# Spike record rubric

Each check passes or fails. `/spike` reads this while writing; the spike reviewer reads it while
checking, and quotes the record as evidence for every failure. A spike record is reviewed twice:
the design review, before `🟢 Ready to run`, applies the checks marked *design*; the verdict
review, before `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled`, applies the checks marked
*verdict*, and the design checks only to what can still change after the runs: the title, Code and
Open questions. The rest of the design was reviewed and signed off before the runs and is fixed
now, so the verdict review reads it to judge the verdict but never fails it.

A record reads from plain to technical. Its plain part, for people, runs from the title down to
Experiment; its technical part, for agents and reviewers, is Experiment, Code and Runs.

1. **Shape** (design). The file is `docs/spikes/YYYY-MM-DD-<a-few-words-naming-the-hypothesis>.md`, in lowercase with hyphens,
   directly in that folder. Its frontmatter has `type: Spike` and `status:` set to `📝 Draft`, `🟢 Ready to run`,
   `💡 Confirmed`, `🚫 Refuted` or `❔ Not settled`, emoji included, and `date:` as YYYY-MM-DD if it has one (a missing date passes: a plugin hook requires it with the next
   status change). Under a `# ` title that is
   the hypothesis in plain words, the sections are Hypothesis, Finding, Next steps, How we'll know,
   Out of scope, How the test works, Risks and safeguards, Results, Surprises, Open questions,
   Experiment, Code and Runs, in that order, and no `<!-- -->` comment from the template is left
   in; the frontmatter's `#` line stays. In a design, Finding, Next steps, Results and Surprises
   are empty.
2. **One hypothesis** (design). Hypothesis states one claim, the one the title states, that one
   experiment can confirm or refute, briefly, without describing the method.
   A claim with parts that could each be tested without the others fails, naming the parts.
3. **References** (design). The record refers to no document but the spec or ADR waiting on its
   hypothesis, which Hypothesis names if there is one. It never refers to the brief, a plan or
   another spike record.
4. **How we'll know** (design). It states, before any run, a result that the runs' output can
   show held or did not, such as a count, a threshold with its unit, or an exact message. "It
   works" or "fast enough" fails. Experiment may give the exact output each result prints.
5. **Experiment tests it** (design). Run as described, the experiment would show whether How
   we'll know holds, for the hypothesis as stated, not for an easier stand-in, such as a sample
   file in another format or a test system that lacks the feature in question. How the test works
   says, in plain words, what it does and why that tests the hypothesis.
6. **Settings** (design). Experiment ends with the template's lines, each filled in: `- Runs:`
   a whole number, `- Stop early if:` a result named in advance or "None.", `- Starts from
   commit:`, `- Inputs:` and `- Secrets:` each a value in backticks or "None.", and `- Command:`
   the command in backticks, with any install step.
7. **Enough runs** (design). A result that can vary from run to run, such as anything over a
   network, anything timed, or anything that calls an AI model, runs more than once, with the
   reason for the count given. One run is enough only when the result cannot vary, and the
   record says why.
8. **Inputs named** (design). Every file the code or command reads that is not written by the Code
   section is named under Inputs: a path in the commit the experiment starts from, or the web
   address of a file the run downloads a copy of. An address the experiment talks to, such as a site
   or service it tests, is not an input, and is not listed there, since the run script downloads
   every Input before the run starts. A path in the repository, and any diff block, come with a
   commit under `- Starts from commit:`.
9. **Code** (design). Each code block names its file on its first line, such as `# file: check.py`,
   or is a `diff` block changing the product's own files; the Command runs that code; nothing the
   experiment needs is missing from the record.
10. **No secret shown** (design). No code or command prints, logs, writes to a file or sends
    anywhere but its own service the value of a secret, in any form, encoded or in part. Secrets
    are named under `- Secrets:` by their environment variable names only, and no secret's value
    appears anywhere in the record.
11. **Limits** (design). Out of scope names each limit of what the experiment can show, or says
    only "None.". No other section states a limit again; it refers to Out of scope instead. A
    limit the runs uncover is under Surprises, since Out of scope is fixed once the design is
    signed off.
12. **Safeguards** (design). An experiment that changes or reads anything real, such as a live
    account, real data, money or someone else's system, has Risks and safeguards naming each way
    it could do harm and what stops it, with the details in Experiment. One that touches nothing
    real says only "None.".
13. **Readable** (design). In the plain part, each section opens with its point; each paragraph
    makes one point; no sentence is one a newcomer would have to read twice to follow, and a finding
    quotes that sentence; versions, flags, settings, file names and code names appear only when the
    hypothesis is about one of them; each domain term the Plain words rule footnotes is explained
    once, in a footnote at its first use, while computing terms need none; steps and runs are lists
    or tables, not sentences.
14. **Every run recorded** (verdict). Each result the Finding uses is in Runs, as a `### Run N`
    entry the run script wrote. The runs of the latest code, those whose code hash matches the
    last run's, number at least `- Runs:`, or the last of them shows the result named under
    `- Stop early if:`. A record that is `❔ Not settled` may have fewer, when Runs shows why it
    could not run. A run marked as the person's observation is for a step only a person can do.
15. **Finding follows** (verdict). The Finding's first sentence is Confirmed, Refuted or Not
    settled, then what was found, in full, so that it makes sense with the rest of the record
    hidden; a bare status word fails. It compares the runs of the latest code, by run number,
    with How we'll know, and rests on nothing but those runs: documentation, other people's
    reports and reasoning are not evidence. A spike that settled nothing says what was learned
    and what is still unknown, and is `❔ Not settled`.
16. **Results agree** (verdict). Results is a table with the columns Run, Date, Outcome and
    Note, with a row for every run in Runs, by its number, with the same outcome, and says which
    runs count.
17. **Surprises** (verdict). Surprises lists what the runs showed that the hypothesis did not
    cover, or says only "None."
18. **Next steps** (verdict). Next steps has a `- Spec:` and an `- ADR:` line. A fact the spike
    found goes to the spec, a choice between ways of building something to an ADR, a finding that
    settles an ADR's open question to that ADR, and each line
    says what should change or only "Nothing". A spec or ADR named by title exists under
    `docs/specs/` or `docs/adrs/`. It never asks a document to refer to this record.
19. **Ready means ready** (design). A record that is `🟢 Ready to run`, `💡 Confirmed`,
    `🚫 Refuted` or `❔ Not settled` has an Open questions section that says only "None."
20. **Proposed answers** (design). Each open question's "**Proposed:**" line makes one proposal, a
    single decision the person can accept in a word or replace, and its "**Why:**" line gives the
    reason, which the proposal does not repeat; a second proposal hidden in either line fails, since
    it belongs in a question of its own. The layout itself, a numbered heading, the context and a
    block quote holding both lines, is checked by the status hook, not here. The proposal is the
    answer the writer would choose, such as a threshold for How we'll know. A question only the
    person can answer, such as whether a sample input stands for the real thing, proposes no guess:
    its "Proposed:" says what would settle it.

The plain part's size, at most 600 words for the design and 400 for the verdict (Finding, Next
steps, Results and Surprises), tables included, is checked by the run script's `words`
command and by the status hook, not by the reviewer. So is a finishing status that the Finding
does not open with, such as `💡 Confirmed` for a Finding that opens "Refuted:".

Sentence and paragraph lengths are guidance in the skill, not checks: a reviewer may list a long
one under Suggestions, which never fail the review, but never as a failed check.
