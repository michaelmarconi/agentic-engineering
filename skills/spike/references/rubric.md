# Spike record rubric

Each check passes or fails. `/spike` reads this while writing; the spike reviewer reads it while
checking, and quotes the record as evidence for every failure. A spike record is reviewed twice:
the design review, before `🟢 Ready to run`, applies the checks marked *design*; the verdict
review, before `💡 Answered` or `❔ Not answered`, applies every check.

1. **Shape** (design). The file is `docs/spikes/YYYY-MM-DD-<a-few-words-naming-the-question>.md`, in lowercase with hyphens,
   directly in that folder. Its frontmatter has `status:` set to `📝 Draft`, `🟢 Ready to run`,
   `💡 Answered` or `❔ Not answered`, emoji included. Under a `# ` title that is the question in
   plain words, the sections are Question, What would answer it, Experiment, Answer, Surprises,
   Where it goes, Open questions, Code and Runs, in that order, and no template comment is left in.
2. **One question** (design). Question asks one question, the one the title asks, which one
   experiment can answer. A question with parts that could each be answered without the others
   fails, naming the parts.
3. **References** (design). The record refers to no document but the spec or ADR whose question it
   answers, which Question names if there is one. It never refers to the brief, a plan or another
   spike record.
4. **What would answer it** (design). It states, before any run, a result that the runs' output
   can show held or did not, such as a count, a threshold with its unit, or an exact message. "It
   works" or "fast enough" fails.
5. **Experiment answers it** (design). Run as described, the experiment would show whether What
   would answer it holds, for the question as asked, not for an easier stand-in, such as a sample
   file in another format or a test system that lacks the feature asked about.
6. **Settings** (design). The Experiment ends with the template's lines, each filled in: `- Runs:`
   a whole number, `- Stop early if:` a result named in advance or "None.", `- Starts from
   commit:`, `- Inputs:` and `- Secrets:` each a value in backticks or "None.", and `- Command:`
   the command in backticks, with any install step.
7. **Enough runs** (design). A result that can vary from run to run, such as anything over a
   network, anything timed, or anything that calls an AI model, runs more than once, with the
   reason for the count given. One run is enough only when the result cannot vary, and the
   Experiment says why.
8. **Inputs named** (design). Every file or web address the code or command reads that is not
   written by the Code section is named under Inputs: a path in the commit the experiment starts
   from, or a web address. A path in the repository, and any diff block, come with a commit under
   `- Starts from commit:`.
9. **Code** (design). Each code block names its file on its first line, such as `# file: check.py`,
   or is a `diff` block changing the product's own files; the Command runs that code; nothing the
   experiment needs is missing from the record.
10. **No secret shown** (design). No code or command prints, logs, writes to a file or sends
    anywhere but its own service the value of a secret, in any form, encoded or in part. Secrets
    are named under `- Secrets:` by their environment variable names only, and no secret's value
    appears anywhere in the record.
11. **Every run recorded** (verdict). Each result the Answer uses is in Runs, as a `### Run N`
    entry the run script wrote. The runs of the latest code, those whose code hash matches the
    last run's, number at least `- Runs:`, or the last of them shows the result named under
    `- Stop early if:`. A record that is `❔ Not answered` may have fewer, when Runs shows why it
    could not run. A run marked as the person's observation is for a step only a person can do.
12. **Answer follows** (verdict). The Answer starts with Yes, No, or Yes provided that a stated
    condition holds, and compares the runs of the latest code, by run number, with What would
    answer it. It rests on nothing but those runs: documentation, other people's reports and
    reasoning are not evidence. A spike that settled nothing says what was learned and what is
    still unknown, and is `❔ Not answered`, never `💡 Answered`.
13. **Surprises** (verdict). Surprises lists what the runs showed that the question did not ask
    about, or says only "None."
14. **Where it goes** (verdict). Where it goes has a `- Spec:` and an `- ADR:` line. A fact the
    spike found goes to the spec, a choice between ways of building something to an ADR, and
    each line says what should change or only "Nothing". A spec or ADR named by title exists
    under `docs/specs/` or `docs/adrs/`. It never asks a document to refer to this record.
15. **Ready means ready** (design). A record that is `🟢 Ready to run`, `💡 Answered` or
    `❔ Not answered` has an Open questions section that says only "None."
