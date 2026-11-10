# ADR rubric

Each check passes or fails. `/adr` reads this while writing; the ADR reviewer reads it while
checking, and quotes the ADR as evidence for every failure.

An ADR reads from plain to technical. Its plain part, for a person deciding or checking the
decision, runs from the title down to Technical detail; Technical detail holds what an agent or
reviewer needs to build and check it. Footnotes explaining terms come last, after Technical detail.

1. **Shape.** The file is `docs/adrs/NNNN-<subject>.md`, with a four-digit number no other ADR in
   the folder uses. The subject is three to five lowercase words joined by hyphens, naming what
   the decision is about, such as `0004-session-data-storage.md`, not the decision itself. Its
   frontmatter has `type: ADR` and `status:` set to `📝 Draft`, `👍 Accepted`, `❌ Rejected` or `↪️ Superseded`,
   emoji included, and `date:` as YYYY-MM-DD. The sections are Question, Decision, Background,
   Options, Consequences, Out of scope, How we'll check, Open questions and Technical detail, in
   that order, and no `<!-- -->` comment from the template is left in; the frontmatter's `#` line
   stays.
2. **Plain title.** The title names the option chosen, in plain words, such as "Keep session data
   in Redis", not the topic, such as "Session storage". While no option is chosen, a title naming
   the question passes. It holds no versions, flags or command names, unless the decision is about
   one of them.
3. **One decision.** The ADR makes exactly one choice. If one part of it could be superseded
   while the rest stands, it holds two decisions; that includes a second choice slipped into
   Consequences, How we'll check or Technical detail, such as "we will also use X". An open
   question asking whether part of the ADR should be an ADR of its own also fails: the ADR is split
   instead.
4. **Question.** Question names the one choice to make, in at most three sentences, and describes
   no option, method, version or setting.
5. **Decision stands alone.** While the person has not chosen, Decision says only "Not chosen yet;
   see Open questions.", Open questions asks for the choice, and the ADR stays `📝 Draft`. Once they
   have, its first sentence opens "Chosen:" and names the option in full, so that it makes sense
   with the rest of the ADR hidden, and the reason follows in at most two sentences. A bare option
   name fails.
6. **Background states the need.** Background says what forces the choice now, in one paragraph
   a newcomer can follow, and does not argue for an option. Each earlier ADR it builds on is named
   by number, linked to its file as check 14 says, with what it decided in a few words, not retold.
7. **Real options.** Options is a table with the columns Option, Outcome and Why, and at least two
   rows that could each meet the need. Each row's Outcome is Chosen, Rejected or Open, and its Why
   is one line. Once Decision names a choice, exactly one row is Chosen, it is that choice, and
   every other row is Rejected with why; before, every row is Open.
8. **Consequences.** Consequences names at least one good and one bad result of the choice, one
   line each. A limit or a decision left for later is not a consequence: it goes under Out of
   scope.
9. **Limits stated once.** Out of scope names every limit the decision relies on, something it
   does not cover that would not change the choice whichever way it turned out, such as an
   untested case whose worst outcome the person has already accepted, and each decision
   left to another ADR, or says only "None.". No other section states a limit again. An untried
   claim the choice depends on, one that would make another option win were it false, is not a
   limit: it comes first in Open questions, proposing a spike, unless a `Bad:` line under
   Consequences says the person chose to go ahead without one. No section leaves it to be proven
   later.
10. **How we'll check.** It says what the decision applies to, as a concern such as "any code that
    stores or reads session data", never as file paths, then lists numbered checks, one line each,
    each by test, demonstration, inspection or analysis. Each check can really be carried out;
    Technical detail gives it in full when one line is not enough.
11. **Readable.** In the plain part, each section opens with its point; sentences are under 25
    words and paragraphs at most three sentences; versions, flags, settings, file names and
    command names appear only when the decision is about one of them; each domain term the Plain
    words rule footnotes is explained once, in a footnote at its first use, while computing terms,
    such as "Redis", need none; every sentence names its subject, never a bare "it" with nothing
    before it to point to; options, steps and checks are tables or lists, not sentences.
12. **Detail at the foot.** Technical detail holds the exact mechanism, rules and settings the
    decision needs, and any evidence in the ADR's own words, or says only "None.". It makes no
    choice that the sections above do not state.
13. **Supersede fields agree.** An ADR that replaces another has `supersedes:` with that ADR's
    four-digit number; a `↪️ Superseded` ADR has `superseded-by:` with the four-digit number of its
    replacement. Each number exists in `docs/adrs/`, and an ADR is `↪️ Superseded` only when its
    replacement is `👍 Accepted`, with both ends then naming each other. While the replacement is
    still `📝 Draft`, the ADR it replaces stays `👍 Accepted` with no `superseded-by:`; that passes.
14. **References.** Of the lifecycle's documents, the ADR refers only to other ADRs. Each time its
    text names one by number, the number is a link to that ADR's file by its name alone, such as
    `[ADR 0003](0003-message-queue.md)`, and the file exists in `docs/adrs/`; a bare number fails.
    The `supersedes:` and `superseded-by:` fields hold bare numbers. The ADR does not refer to a
    spec, the brief, a plan or a spike record in any way: no hyperlink, path or title; a spike's
    measurements are stated in the ADR's own words. Those change while an ADR does not, so the
    reference would go stale. The ADR refers to outside material only by a web link. It never
    refers, by hyperlink, path or title, to material handed over in the conversation, to anything
    outside the repository, or to a file under `docs/` that is not a brief, spec, ADR, plan or spike
    record: such material can change or vanish without the ADR being touched, so what matters from
    it is stated in the ADR's own words. References to code are not part of this check.
15. **No overlap.** No other `📝 Draft` or `👍 Accepted` ADR in `docs/adrs/` decides the same thing or
    contradicts this one, unless this one supersedes it.
16. **Accepted means settled.** A `👍 Accepted` or `↪️ Superseded` ADR has no open questions: its
    Open questions section is empty or says only "None." A `📝 Draft` or `❌ Rejected` ADR may
    have some.
17. **Proposed answers.** Each open question ends with "Proposed:" and the answer the writer
    would choose, such as the option they would recommend, so the person can accept it in a word or
    give another. A question only the person can answer, such as why they rejected an option,
    proposes no guess: its "Proposed:" says what would settle it, such as "tell me what ruled
    Postgres out".

The plain part's size, at most 500 words, tables included, is checked by the skill's `words`
command and by the status hook, not by the reviewer. So is a `👍 Accepted` ADR whose Decision does
not open with "Chosen:".
