# Changelog

What changed in each version of the plugin, newest first. Versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html), and this file follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Read the entry before you update
past a major version: it says what you need to change in your documents. Before 1.0.0, a
minor version could need such a change, and its entry said so.

## [1.14.0] - 2026-11-26

### Changed

- You can answer a question by writing in chat instead of picking a choice or tapping a card.
  Once a correction check has run, every message you write reaches the next check, word for word
  and in order, so `/build` and the document skills no longer lose an answer typed in chat.
- `/build` lists every open finding in one message before asking about them one at a time.

### Fixed

- A question left unanswered on the question tool, because you replied in chat, no longer saves
  the tool's stand-in text as your answer.
- The correction checkers take your choices only from your answers, never from a file in the
  repository, so a check can no longer pass on a note that happens to mention a finding.
- Messages from other agents in a project thread, background notices and command echoes are never
  taken as your answers.
## [1.13.0] - 2026-11-26

### Added

- Skills that work for minutes without you, `/build`, `/audit`, `/verify`, `/spike`, `/deploy`
  and the review of a document in `/brief`, `/spec`, `/adr`, `/plan` and `/practices`, now show
  their steps on the list your place shows live: Claude Code's task list on the command line and
  desktop, and the checklist in a Claude project thread. Each step is marked done with a one-line
  summary of what it found, so you can tell which step a run is on.
- `/build` lists its steps from the plan, one per requirement and then the reviews, corrections,
  correction check and hand-over, numbered the same way every run, and names each requirement's
  step, such as "Step 2 of 7", before writing its code.
- A plugin hook reminds Claude to update its progress list each time a helper agent finishes.

## [1.12.1] - 2026-11-26

### Fixed

- A correction check that was interrupted or reported nothing can now be run again, and the
  person's answers wait until a check actually reports, rather than being lost when its start is
  refused.
- The lines a build changed are read correctly when a changed line itself looks like a diff
  header, when git is set to leave out its `a/` and `b/` prefixes, or when a file name holds a
  space; a diff that can't be read no longer leaves the checker without its reports.
- Answers to a build's open findings and answers to a document's questions no longer end up in
  each other's record when both run in one session.
- The reviews kept for a recheck are cleared once no check needs them, so an earlier round's
  reports never appear in a later report.

## [1.12.0] - 2026-11-26

### Changed

- When a build's correction check leaves findings open, `/build` now goes through them with you one
  at a time, each with a proposal and the choices Accept, your own answer, Ignore and Defer, makes
  the fixes you choose on the same branch, and has the correction checker look again at only what
  changed, with your answers, rather than offering only "accept as it stands" or a full fresh
  review. Its last question offers `Built ✅`, one more full review, or stopping. A plan can now be
  marked `Built ✅` however many commits your answers added (ADR 0060, superseding ADR 0052).
- Findings in older code the build did not change, which the code review reports because it reads
  whole files, are listed apart under "Outside this build", graded high, medium or low, and never
  fail the check on their own. `/build` gives their count by grade and asks once whether to go
  through them or carry on (ADR 0061).

## [1.11.0] - 2026-11-26

### Fixed

- In a Claude project thread, a tap on a decision card whose option starts with one of the four
  choices, such as "Accept: undo within 24 hours", is now kept as the answer to the card's
  question, so the correction checker no longer reports that question as unanswered. Before, only
  an option named exactly Accept, My own answer, Ignore or Defer was kept.

## [1.10.0] - 2026-11-26

### Fixed

- In a Claude project thread, a question asked at a skill's hand-over is now also posted on a
  decision card, with options named exactly Accept, Ignore and Defer and the proposal recommended.
  The lifecycle page's "Ending with your answers" says so, and a new plugin hook
  (`scripts/card_nudge.py`) reminds the agent the moment it posts a question ending "Accept, give
  your own answer, ignore or defer?". The hook keys on that line, not on a skill, so every skill
  that asks this way is covered; the CLI and the desktop app are unchanged.

## [1.9.0] - 2026-11-25

### Fixed

- `/agentic:audit` of one named document now reports only that document's own problems under
  "Problems with the documents", instead of every problem in the repository, and leaves out the
  documents to consider deleting and the unfinished spike records, which belong to a full audit
  or a window. A named path that is no lifecycle document is refused when the report is written.

## [1.8.0] - 2026-11-25

### Fixed

- `/agentic:audit`'s report puts checks that need a run under `## Checks that need a run`, each
  named by its spec or ADR and its requirement, in place of `## ADR checks that need a run`, so a
  spec's run items no longer sit under a heading that names ADRs. A spec's auditor now lists a
  requirement as needing a run only when reading the code can't settle it, such as a measured
  time, taking what to run from the requirement's How we'll check, and judges every other
  requirement by reading.

## [1.6.0] - 2026-11-24

### Changed

- `/agentic:verify`'s report is easier to scan. It opens with a short header and one table with a
  row for each example, giving its requirement, its name and its result (✅ Pass, ❌ Fail,
  ⚠️ Disputed or ⚠️ Not checked), under one line of counts. When the repository is on GitHub,
  each requirement and example links to its place in the spec at the commit checked; elsewhere
  each gives its line number in the spec. Then come what needs doing, grouped by cause, any
  caveats, and each example's evidence from both agents together. The commands the agents ran
  are kept last, folded away.

## [1.5.0] - 2026-11-22

### Changed

- The spec reviewer now fails a spec in which two requirements decide the same thing, such as two
  that say in other words who is sent a reminder (check 10, "No overlap", which looked only at
  other specs). A requirement that says how another's outcome holds in a particular case still
  passes. It also fails the same example given under two requirements (check 6, "Examples add
  cases"): each example sits only under the requirement it is about, so changing one requirement
  can't leave a copy elsewhere contradicting it. Specs that passed review before may fail it now.
## [1.4.0] - 2026-11-22

### Added

- Pull request descriptions keep their links working. Before an agent creates or edits a pull
  request, with a GitHub tool or with `gh pr create` or `gh pr edit`, a plugin hook refuses a
  description holding a link longer than 150 characters, which GitHub can show as plain text
  instead of a link, and says how to shorten it: pin file links to the commit's 7-character id.
  It also refuses a `gh` description it cannot check because it is not written out yet, such as a
  file the same command writes, so the agent writes the description first and then sends it.
- The default pull request template that `/agentic:practices` offers says to pin links to the
  7-character commit id. A template you already have is left alone.

## [1.3.0] - 2026-11-22

### Changed

- Every skill now shows you the files it writes the way the place you work in needs. On the
  Claude Code command line it names the file's full path; in Claude Code desktop it also opens the
  file in the Files pane; in a Claude project thread it copies the file into the project's shared
  files folder, `/mnt/project-files/`, under a folder named after the repository, and attaches the
  copy to its reply, so you can open it. This covers each document at hand-over and the reports
  of `/build`, `/verify` and `/audit`. The rule is written once, in the lifecycle page's new
  "Showing a file to you" section.

## [1.1.0] - 2026-11-20

### Changed

- The brief, specs, ADRs, plans and spike records now link only to each other and to the web.
  A plugin hook refuses a new link to code, a folder or any other file in your repository, since
  those can change or vanish without the document being edited; name a code file as plain text,
  such as a path in backticks, instead. Links your documents already hold are left alone.
- Other files may live under `docs/` beside the lifecycle's documents: the lifecycle leaves them
  alone. It no longer says `docs/` must hold only its own documents.

## [1.0.0] - 2026-11-20

### Changed

- The plugin is now stable. Nothing changes in how the skills work since 0.79.0, and nothing in
  your documents needs to change.

## [0.79.0] - 2026-11-20

### Changed

- Document skills keep their questions out of the document until you defer them: the rule now
  sits beside the step that writes a gap as a question, and the templates' Open questions
  placeholder names a deferred question.
- A deferred or ignored question needs no correction check; only an answer you give is checked.
- After a failed correction check, the skill quotes each of the check's findings as given, even
  when you said not to ask, and writing in what you defer is the one change it still makes.
- /spike corrects crashing experiment code once a run shows the fault, and never before, ahead of
  the next run; a design leaves Next steps empty.
- The /build, /audit and /verify hand-over reply may run to 175 words, up from 150, and each
  bullet's bold label counts toward its 15 words.

## [0.78.0] - 2026-11-19

### Changed

- The lifecycle page, `docs/lifecycle.md`, is rewritten in two parts: how it works, for reading
  top to bottom, then the rules in full. The rules are the same; nothing you need to change.
- The review steps that /brief, /spec, /adr, /plan, /spike, /practices, /feedback and /release
  share are written once, in the lifecycle page's Review process section, and each skill reads
  them there, keeping only its own reviewer and requests. Reviews run as before (ADR 0053),
  with two points made explicit: /feedback's and /release's drafts, never saved as files, keep
  their own `Document:` line, and each of a spike's two reviews is a full review.
- When you tell a document skill not to ask you anything until the review passes, it writes each
  question into Open questions with its proposed answer, even after a failed correction check, and
  tells you how many there are.
- The README says what /release, /deploy and /practices change in your repository, its skills
  diagram follows the lifecycle's, and the steps for moving from an `sdlc@sdlc` install are
  shorter.
- Each skill's page links the lifecycle page, names the files of the agents it starts, and points
  to the Review process section instead of repeating it.

## [0.77.1] - 2026-11-19

### Fixed

- /adr and /plan ask their offer of diagrams under a bold "Optional: diagrams" line, outside the
  question count. Before, the offer could come as a fourth question after the count had said
  "of 3".

## [0.77.0] - 2026-11-19

### Changed

- /brief, /spec, /adr, /plan, /spike and /practices ask one question per reply, then end their
  turn and wait for your answer before asking the next, even where the question tool or decision
  card returns at once, as in a Claude project thread. Until now they could post the next question
  straight after the first. A reply no longer lays out several questions with a rule between
  them (issue #125).

## [0.76.0] - 2026-11-19

### Changed

- Every file the plugin writes outside your repository now goes in the session's scratchpad, the
  temporary folder Claude Code gives each session, under `agentic/`: the build, audit and verify
  reports, spike runs and the records the hooks keep. The desktop app's file pane can open the
  reports, which it could not do in the plugin's data folder. They are temporary: Claude Code
  clears the scratchpad when it chooses, so keep anything you need elsewhere. Where a session has
  no scratchpad, they go in a folder of the session's own that only you can open, inside the
  system's temporary folder (ADR 0051, superseding ADR 0033).
- When a build's correction check fails, /build asks at once, in the same conversation, whether
  to accept the build as it stands or leave it. Running `/build` again on the branch no longer
  offers to accept an earlier failed build: it reviews afresh (ADR 0052, superseding ADR 0038).

## [0.75.0] - 2026-11-19

### Changed

- /brief, /spec, /adr, /plan and /spike keep the questions they raise while drafting out of the
  document. They ask them one at a time with the review's questions, asking once where both raise
  the same point, and write a question into Open questions only when you defer it, as ADR 0049
  already says. An ADR whose choice isn't made yet says "Not chosen yet." in Decision. Reviewers
  report a gap the document marks as not chosen or not known yet as a question for you, not a
  failure. A plan still lists the ADRs, spec changes and practices it waits on under Open
  questions. Nothing in your documents needs changing: an older ADR's "Not chosen yet; see Open
  questions." still passes, and is shortened the next time the skill edits it.

## [0.73.1] - 2026-11-19

### Fixed

- When one reply asks questions about several documents, such as the first open question of each
  of two ADRs, the "Question N of M" count runs across all of them, so each question has its own
  number.

## [0.73.0] - 2026-11-19

### Changed

- Where Claude has no question tool but can post a decision card, as in a Claude project thread,
  /brief, /spec, /adr, /plan, /spike and /practices now ask each question in words as before and
  then post it on a card, with the proposal recommended, so you can answer with a tap. /build does
  the same for its "Build anyway" and "Accept the build" questions.
- When one reply asks several questions, such as the first open question of each of two ADRs,
  each question is followed straight away by its own card, or the question tool, with a
  horizontal rule before the next, so it is clear which card answers which question.
- The answer you tap on a card is kept for the check of what changed against that card's own
  question, so each of several cards keeps its own answer.

## [0.72.0] - 2026-11-19

### Changed

- A document is now reviewed in full once. After that, only what changes is checked. /brief,
  /spec, /adr, /plan and /spike put each question to you with four choices: accept the proposal,
  give your own answer, ignore it, or defer it. Only deferred questions are written into Open
  questions. After each round of answers, a check reads only what your answers changed, and any
  situation a change leaves uncovered comes back as a question, never a failure. Once nothing is
  left to ask, the last question offers the document's next status, one more full review, or
  stopping, so you decide when the review ends. A full review runs again only when you ask, after
  a change you make yourself, on a document rewritten to a new layout, or in a new conversation.
- When the correction check fails in those skills, its findings now come back to you as
  questions instead of stopping the skill.
- When you say not to ask now, or stop partway, the questions left are deferred into Open
  questions.
- /spec never asks, or files as an open question, a question whose answer is a technical choice.
  It says the choice belongs in an ADR.
- /feedback, /release and /practices are unchanged: they still review once, check once, and stop
  on a failed check.

## [0.71.0] - 2026-11-18

### Changed

- When a skill asks you questions one at a time, "Question N of M" now only moves forward. The
  first number counts the questions asked or settled so far in the conversation, this one
  included, and the total adds those still open, so an answer that splits one question into two
  makes it "Question 2 of 7" rather than "Question 1 of 6" again. The skill says in one line when
  an answer opens or settles other questions. This holds in /brief, /spec, /adr, /plan, /spike
  and /practices.

## [0.70.0] - 2026-11-17

### Changed

- Every document status is now written word first, then its emoji, such as `Accepted 👍` and
  `Ready to build 🟢`, so the values line up when a document's frontmatter is shown as a table.
  This holds in the status line and wherever the plugin names a status.
- Documents written by earlier versions, with the emoji in front, such as `👍 Accepted`, keep
  working and count as their status. You don't need to change them: a skill rewrites the status
  line the next time it edits a document, and the status hook allows an edit that only moves the
  emoji on any document, decided ADRs and built plans included.
- `/agentic:audit` lists the documents whose status still puts the emoji in front, together as
  one problem.

## [0.69.0] - 2026-11-17

### Changed

- `/agentic:verify` now says, when it shows the requirements it will check, that its second
  agent re-challenges every verdict, passes included, so each spec takes about twice as long as
  one agent alone, and that the requirements a change touches are usually enough. Its page says
  the same, and suggests recording helpers in the Running the product practice, such as a reset
  command or a quick way to make a connection fail, to save each agent time.
## [0.68.0] - 2026-11-17

### Added

- Every new ADR shows its number in a `number:` field right after `type:`, the four digits its
  file name starts with, so a reader sees the number other ADRs use. The ADR template carries it,
  and a plugin hook refuses one that does not match the file name.
- `/agentic:audit` lists each ADR without a `number:` field, or with one that does not match.
  Existing ADRs may go without it: add it by hand when you like, with any edit, even to an
  accepted ADR.

## [0.66.0] - 2026-11-17

### Added

- `/agentic:practices logging` records how the product writes its logs (the library or helper,
  the levels and when each applies, the format) and where an agent reads them when working out
  why something failed: where they end up, locally and in each environment, and the command that
  shows them. It usually goes in `docs/practices/logging.md`, read before adding or reading logs.
  No skill depends on it.
- The Security and dependencies topic also asks what must never be written to logs, such as
  secrets, tokens and personal data.

## [0.65.0] - 2026-11-17

### Added

- `/agentic:deploy` puts one release, named by version or by commit, into one environment such
  as staging or production, by the steps `docs/practices/deploying.md` records. It checks that
  environment's practice and the commit first, shows what will go where, the check and the roll
  back, and deploys only on your yes. It then runs the recorded check until it passes or its wait
  runs out, and rolls back at once if it fails. It writes nothing to your repository: its reply is
  the record.

### Changed

- `/agentic:practices deploying` now says, for each environment, whether a release is named by
  version or by commit; the Deploy command may take `{environment}`, `{commit}` and `{version}`,
  and may be any line starting `None:`, such as "None: the pipeline deploys it"; Roll back may
  take `{environment}`.
- The practice check judges one environment of `deploying.md` with `--environment <name>`, so a
  gap in another environment no longer blocks a deploy, and lists the environments recorded.

## [0.64.0] - 2026-11-17

### Added

- `/agentic:practices reviews and merging` gives every pull request description the same
  sections: a plain Summary, what the work was built from (its plan, specs and ADRs), what
  changes, how it was checked, and optional notes, each saying which part of the `/agentic:build`
  report to draw from ([ADR 0047](docs/adrs/0047-practices-pull-request-template.md)). On GitHub
  it shows you the default template and writes `.github/pull_request_template.md` only if you say
  yes, leaving any template you already have alone. The practice gains a rule that descriptions
  follow the template; with no template, the rule lists the sections instead.

## [0.63.0] - 2026-11-17

### Changed

- A repository is one project, a monorepo included: the plugin counts every `docs/` path from the
  top of the git repository, wherever in it you start Claude. A session started inside one app,
  such as `apps/web`, now gets the lifecycle rules and writes to the root `docs/` folder. Before,
  it got no lifecycle rules when the documents sat at the root (ADR 0046, which replaces ADR 0032).
- `/agentic:spec` puts a new spec in the existing folder of `docs/specs/` it fits, such as one
  per app, and asks you only when none clearly does. The spec reviewer checks it.

### What you need to change

- A repository that kept a separate `docs/` folder inside each app or package, and started Claude
  in that app, no longer has those documents checked by the plugin's hooks. Keep one `docs/`
  folder at the top of the repository, grouping specs into folders if you like, or give each
  unrelated app a repository of its own.

## [0.62.0] - 2026-11-17

### Changed

- `/agentic:practices` records a step as it stands only when it calls a named entry point, a
  command runner entry, a script or a tool's standard command such as `npm test`, with nothing but
  `{name}` values ([ADR 0044](docs/adrs/0044-practice-step-entry-point.md)). Any other command,
  such as a long line holding your project's flags, folders or accounts, goes into a script in your
  scripts folder, and the practice records only the command that runs it, so those choices live in
  a file your tests can run instead of a line of Markdown that falls out of date.
- `/agentic:practices` writes those scripts itself when they hold no logic, creating `script/` if
  you have no scripts folder, and adds a runner entry that calls each one when you have a runner
  ([ADR 0045](docs/adrs/0045-practices-skill-writes-scripts.md)). It no longer asks which kind of
  place for commands to create. It runs a script only when that changes nothing real, and when a
  script changes a real outside service it suggests a test against a stand-in as work for
  `/agentic:plan`. A step that needs logic, such as a retry, is recorded as not set up yet and
  handed to `/agentic:plan`.
- Practices recorded earlier with long one-line commands may now fail the practices review until
  you move those commands into scripts.

## [0.61.0] - 2026-11-17

### Added

- `/agentic:release` makes a release by the steps your project records in
  `docs/practices/releasing.md`: it proposes the next version, drafts release notes for your
  users, has them reviewed by a new release reviewer and the wording checker, corrects them once
  and checks the corrections, then commits the version and notes after you sign off. It commits on
  the branch being merged, or on a new `release/<version>` branch, never on the default branch, and
  never opens a pull request or merges. It publishes only when the practice records a publish
  command, only from a commit the practice allows, and only after you say yes.
- The release notes come from the builds: every `/agentic:build` hand-over now gives at least one
  `--release-note`, a plain sentence on what users can now do, and the hand-over script adds it to
  the commit as a `Release-note:` line ([ADR 0043](docs/adrs/0043-build-commit-carries-release-note.md)).
  Commits with no note are drafted from their subject, marked as drawn from history, and you keep,
  reword or drop each.

### Changed

- `hand_over.py` now needs `--release-note` to hand over. If you call it yourself, add one.

## [0.60.0] - 2026-11-16

### Changed

- `/agentic:build` keeps your practices and its own rules in view however long it runs. A long
  build gives less weight to what it read at the start, so each time the script that checks a
  requirement's new tests runs, it prints the `## Practices` sections of `AGENTS.md` and
  `CLAUDE.md` and the build's rules for the whole build again, before any of that requirement's
  code is written. Only those sections are printed, about 1,500 tokens each time, not the rest of
  `AGENTS.md` or the topic files under `docs/practices/`.
## [0.59.0] - 2026-11-16

### Changed

- `/agentic:practices` now records releasing and deploying as two topics, `releasing.md` and
  `deploying.md`, in place of the single releasing topic. Each has a fixed set of headings: what
  may be released, the version and how a release is tied to its commit, and the publish command;
  and for each environment, which releases may go there and the commands that deploy, check and
  roll back. Their required items come from you or your repository, never from a default Claude
  proposes. While recording them, `/practices` tries only what is safe, such as reading the
  version, running a deploy check or a dry run, and never publishes, deploys or rolls back. A small
  script decides whether each topic is complete, so the coming release and deploy skills can stop
  and name exactly what is missing. A `releasing.md` recorded earlier is left as it is: run
  `/agentic:practices releasing` to bring it into the new layout (issue #87).

## [0.57.0] - 2026-11-16

### Changed

- Every step your practices record, such as running the tests or releasing, is now one command:
  one line that calls one program and says by its exit code whether it worked, so every skill can
  run it and judge it the same way. A step of several commands becomes an entry in your project's
  one place for commands, a command runner such as Make or the scripts of `package.json`, or a
  single scripts folder. `/agentic:practices` writes that entry when you agree the step, shows it,
  tries only what is safe to run, and records the one-line command; with no runner or scripts
  folder yet, it asks which you want first. A small script checks each command before it is
  recorded. No other skill writes commands. Practices recorded earlier with chained commands, such
  as `a && b`, are flagged in the overview and left for you to change.

## [0.56.0] - 2026-11-16

### Changed

- `/agentic:build` now checks each requirement's tests before writing its code. A small script
  runs the new or changed test files and accepts them only if each one fails and nothing else is
  uncommitted, so tests that already pass, or code written before its tests, are refused at the
  requirement where it happens. The build reads why each test failed, and lists every
  requirement's result in its report and in the build reviewer's request. The reviewer's
  tests-first check reads those results instead of judging the commit order. Tests refused because
  their code was already committed, such as by an earlier build that stopped, are kept, and the
  reviewer raises that requirement for you to accept or not, since commits are never rewritten
  (ADR 0039, issue #94).

## [0.55.0] - 2026-11-16

### Added

- `/agentic:verify` checks the running product against its accepted specs from the outside. It
  agrees with you which requirements to check, refuses to start while anything is uncommitted,
  then, one spec at a time, a fresh agent starts the product, tries each example the way a person
  would and gives it pass, fail or not checked with evidence, never reading the code, and a second
  agent tries to disprove each verdict. A rejected verdict is shown as disputed, for you to decide.
  It ends with a short reply and a report file outside your repository, with every agent's report
  copied in, and changes nothing in your repository. Its two agents run on Opus, since using a
  product is harder work than reviewing a document (ADR 0040, issue #86).
- `/practices` has a new topic, Running the product: how to start and stop the product, reach it,
  set up an example's starting state, and which services are safe to touch and which never are.
  `/practices` tries the commands before recording them. `/verify` needs this topic, and stops
  and points to `/agentic:practices running the product` when it is missing.
- The Reviews and merging topic asks whether `/verify` must run and pass before a build is merged.

### Changed

- `/build`'s closing reminder now suggests `/agentic:verify <the plan>` instead of Claude Code's
  own `/verify`: as a step before merging if your practices require it, otherwise as an option.
- The Setting up topic no longer asks for the command that runs the product; Running the product
  holds it now.

## [0.54.0] - 2026-11-16

### Added

- You can accept a build as it stands when its correction check fails, instead of sitting through
  another round of reviews that may well leave new findings open. Run `/build` again on the
  unchanged branch: it starts no review, lists the open findings, explains what accepting means and
  asks "Accept the build as it stands, or correct it?". If you accept, the plan is marked
  `✅ Built` in a commit whose message lists the findings you accepted, so the pull request shows
  them (ADR 0038, issue #93).
- The hand-over script checks the conditions itself: the plan is `🟢 Ready to build` and was
  signed off before the build, the newest build report for it on this computer shows the failed
  check, and the branch hasn't changed since. Otherwise `/build` reviews again as before. Its new
  options are `--open-findings` and `--accept-open-findings`, and its report now names the commit
  the branch was at (`Head:`).

## [0.53.0] - 2026-11-16

### Changed

- A build no longer has to start with the first message of a session. When you ask for one, the
  plugin measures how much conversation the session has gained since Claude's first reply. Under
  20,000 tokens (roughly 15,000 words) the build starts; over it, `/build` asks whether to build
  here anyway or start clean, and starting clean gives the two steps for a new session (ADR 0037,
  which replaces ADR 0031). A build is never refused for this any more, so a thread that Claude
  opened for you in a Claude project can build straight away (issue #83).
- The hook behind this is now `scripts/build_session.py`, replacing `scripts/fresh_session.py`.

## [0.52.0] - 2026-11-16

### Changed

- Every spec, ADR, plan and spike record is named by one rule: its number or date, then a
  subject of two to five lowercase words, each a word of its title (ADR 0035). The hook that
  checks each write refuses a new document whose name breaks the rule, giving the form it should
  take, and an edit that drops one of the name's words from the title. It refuses names it used
  to allow, such as a one-word ADR subject or a plan named with its whole title, so this is a
  minor version. Existing names are left as they are: the hook never refuses a file for its name
  alone, and documents written before the rule stay editable.
- `/audit` lists each document whose name does not have the rule's shape, and ADRs that share a
  number. It does not compare an existing name's words with its title.
- The ADR, plan and spike reviewers no longer check file names, since the hook does.
- Every document skill now holds the same sentence forbidding a rename once a document's review
  has started (ADR 0036), checked by `skill_check.py`; it replaces the spike skill's own.
- When the correction check finds no saved review of a document, its refusal says the document
  may have been renamed since its review, and to move it back.

## [0.51.1] - 2026-11-16

### Changed

- The reply that ends `/build` and `/audit` now gives the outcome in a sentence or two, then at
  most five bullets of at most 15 words each with the main findings and any question or action
  for you, then the report file's path, all under 150 words. Before, it was told not to list
  findings, but did anyway, at length; the full report stays in the file.

## [0.51.0] - 2026-11-14

### Changed

- `/build` and `/audit` now hand back their full report as a Markdown file, beside a reply of a
  few lines naming it, instead of a long summary in the conversation
  ([#85](https://github.com/michaelmarconi/agentic-engineering/issues/85), ADRs 0033 and 0034).
  The file is kept in the plugin's data folder, under `reports/<repository>/`, or in a private
  folder in the system's temporary folder where that can't be written, and is shown in the app's
  file viewer where there is one.
- A script writes the file: Claude gives it only its own sections, and the script copies in, word
  for word, the hand-over script's output, the build's three review reports and the correction
  check's report, or each audit agent's report. A build that refuses before it starts, or an
  audit that stops before its first agent starts, writes no file: the reply says why.
- A new hook, `scripts/audit_relay.py`, keeps the audit agents' reports for the file, and the
  build's hook now keeps the review reports until the hand-over.
- `audit.py` has two new commands, `start` and `report`, and `hand_over.py` takes `--report`,
  `--data` and `--session`.

## [0.50.0] - 2026-11-14

### Fixed

- The plugin's hooks now find the git repository from the file they act on, so they work when
  Claude Code starts in a folder above the repository, as in a Claude project thread
  ([#84](https://github.com/michaelmarconi/agentic-engineering/issues/84), ADR 0032). Before,
  `/build`'s correction check was always refused there, because the commit the reviews saw
  could not be recorded; the hooks that check document statuses, references between documents
  and the size of recorded practices let changes through unchecked; and the lifecycle rules were
  not given to Claude at the start of the session.

### Changed

- `/build` gives the plan's full path on every review request, so the reviews and the
  correction check use the plan's repository whatever folder you started in.
- When no git repository holds the plan, the correction check is refused with that reason,
  instead of a reason about a commit.
- ADR 0032 supersedes ADR 0022: one shared rule, in `scripts/repository.py`, for every hook.

## [0.49.0] - 2026-11-12

### Changed

- `/build` lets you build a plan before it is signed off, if you choose to
  ([#77](https://github.com/michaelmarconi/agentic-engineering/issues/77)). When the plan, or a
  spec or ADR it lists, is `📝 Draft`, it no longer refuses. It runs its other checks, lists what
  isn't signed off, including the plan's open questions, and asks "Build anyway, on the proposed
  answers?". Pick "Build anyway" and it builds each open question's proposed answer, asking you
  any question that has none. Pick "Stop and settle them first" and it changes nothing. It never
  builds an unsigned plan without your answer in the conversation.
- A build before sign-off records in a commit what wasn't signed off and how each open question
  was answered, so the record is in git. No document's status changes: the plan stays
  `📝 Draft` until you settle it and sign it off, and a later `/build` on the branch marks it
  `✅ Built`.
- A spec or ADR that is `❌ Rejected` or `↪️ Superseded`, a missing one, or a missing requirement
  heading still stops the build, with no offer to build anyway.

## [0.48.0] - 2026-11-12

### Changed

- When a build can't start because the session isn't fresh, the message now says the plugin has
  no reliable way to start a new session for you, then gives the two steps: run `/clear`, then send
  `/agentic:build` with the plan's path. In a Claude project thread, which has no `/clear`, it says
  to open a new thread and send that command as its first message. Before, it only said to start a
  new session. The plugin never tries to start a session itself (ADR 0031).
- When you sign a plan off as `🟢 Ready to build`, `/plan` ends its reply with the same two steps,
  for that plan.

## [0.47.1] - 2026-11-12

### Fixed

- `/build` now always reaches its correction check after the code review finds something
  ([#79](https://github.com/michaelmarconi/agentic-engineering/issues/79)). It runs `/code-review`
  inside a `general-purpose` agent, as it already ran `/security-review`, so the review's report
  reaches the plugin's hook whatever way the Claude Code version runs the skill: forked into an
  agent of its own, or inside the session, reporting through a tool the hook never sees. The hook
  no longer reads the Skill tool's result.

## [0.47.0] - 2026-11-12

### Changed

- The brief now changes only when you decide the product's intent has changed. No skill proposes
  editing it to match a spec or ADR, and changing the brief edits no other document.
- `/spec` raises the brief only when a spec contradicts its Goals, Out of scope or Constraints,
  such as a rule for something the brief puts out of scope. Detail the brief doesn't mention is
  never raised. A contradiction becomes an open question in the spec with two answers: change the
  spec, or you change the brief. Once you settle it, it is not raised again. The spec rubric gains
  check 15, "Fits the brief".

### Added

- `/audit` checks accepted specs and ADRs against the brief, with one new agent, `brief-checker`,
  that reads documents only. A second agent tries to disprove each contradiction before it is
  reported under "Contradicts the brief", with quotes of both and both corrections named. A window
  in which the brief changed checks every accepted spec and ADR against it.
- The audit script's `documents` command reports the brief's path as `brief`, and `window` reports
  `brief_changed`.

## [0.46.0] - 2026-11-12

### Changed

- A spike record's plain part now has two word limits: at most 600 words for the design, written
  before the runs, and 400 for the verdict, its Finding, Next steps, Results and Surprises, written
  after them. One 600-word limit used to cover both, so a design close to it left the verdict no
  room. The status hook checks both at every move forward, and `spike.py words` reports both.
- In a spike record, the lifecycle's own terms, such as "spec" and "ADR", count as plain words, as
  they already did in issues, plans and practices, so the template's `- Spec:` and `- ADR:` lines no
  longer fail the wording check.
- A spike record's Inputs are only files the run keeps a copy of. A site or service the experiment
  talks to, such as the one it tests, is not an input, since the run script downloads every input
  before the run starts and an address that can't simply be downloaded stopped the run.
- The verdict review judges only what can still change after the runs: the verdict, and the title,
  Code and Open questions. The design was reviewed and signed off before the runs and is fixed, so a
  finding about it could never be corrected and left the record unable to finish.

### What you need to change

- Nothing in finished spike records. A record that is not finished and holds more than 400 words in
  its Finding, Next steps, Results and Surprises must shorten them before it moves on.

## [0.44.1] - 2026-11-12

### Fixed

- An open question's **Proposed:** and **Why:** lines could show as one line, because without a
  line holding only `>` between them Markdown joins them into one paragraph. The skills now write
  that line, the status hook refuses Open questions without it, and `/audit` lists documents that
  lack it. To correct a document, add a line holding only `>` between the two lines.

## [0.44.0] - 2026-11-11

### Changed

- Every open question in a brief, spec, ADR, plan or spike record is now a numbered heading,
  `### 1. <what is to be settled>`, then the context it needs, then a block quote holding one
  `> **Proposed:**` line with the answer and one `> **Why:**` line with the reason, so the
  proposal is easy to spot. Each question holds one proposal: a question with two answers becomes
  two questions. ADR 0030 records the choice.
- The status hook refuses an edit that adds or changes Open questions in any other layout, naming
  the entry and what is wrong. An edit that leaves Open questions as they were is allowed, so older
  documents can still be edited.
- When a skill asks you to settle a question in the conversation, it shows a bold line such as
  "**Question 1 of 3: …**", the context, the same Proposed and Why quote, and the question itself
  last. This covers `/brief`, `/spec`, `/adr`, `/plan`, `/spike` and `/practices`.

### Added

- `/audit`'s document check lists each document whose Open questions are not in the new layout,
  leaving out documents that are never edited again, such as an accepted ADR or a built plan.

### What you need to change

- Nothing at once. A document written before this keeps its old Open questions until they next
  change; the change then has to bring the whole section into the new layout. Run `/audit` for the
  list of documents to bring over.

## [0.43.1] - 2026-11-11

### Fixed

- When `/plan`'s correction moves a Decisions line to Open questions, its "Proposed:" keeps the
  decision as the person agreed it. It sometimes proposed a different decision instead, so
  answering "yes" reversed what had been agreed. Any doubt about the decision now goes in the
  question's text. Nothing in your documents needs to change.

## [0.43.0] - 2026-11-11

### Added

- `/plan` offers diagrams at the hand-over, the same way `/adr` does: a flowchart of parts that
  call each other, a sequence diagram of events between actors, a state diagram or an
  entity-relationship diagram, each only when the plan's text names at least three of its things
  and two connections between them. It asks "Would you like to add any of these diagrams to the
  plan, or propose another?", draws nothing you don't pick, and never holds a plan back from
  `🟢 Ready to build`. A picked diagram is a `mermaid` block after the Plan section's opening
  paragraph; the plan rubric's new check 13 fails any box or arrow its text does not hold, and
  check 7 (no code) allows it. Only a `📝 Draft` plan gets the offer.

### Changed

- `/adr` and `/plan` ask the diagram offer's question word for word even when they offer a single
  diagram, and share more of the offer's wording, checked by the plugin's skill check.
- The ADR and plan reviewers fail a diagram's arrow unless the text says that one thing calls,
  sends to or is read by the other; naming both is not enough. Nothing in your documents needs to
  change.

## [0.42.2] - 2026-11-11

### Fixed

- `/build` no longer refuses to start on Linux with Claude Code's sandbox on. The sandbox puts
  stand-ins for `/dev/null` in place of files it protects, such as `.bashrc` and
  `.claude/settings.json`, and git lists them as untracked, so `/build` took them for
  uncommitted work. A new script, `uncommitted.py`, lists what is uncommitted and leaves those
  stand-ins out.
- The hand-over no longer drops the build's last work there. Git can't add the stand-ins, and one
  it can't add stopped the hand-over from adding anything, so the branch was pushed without the
  work and no error was shown. It now leaves the stand-ins out, and reports a failed add.

## [0.42.1] - 2026-11-11

### Fixed

- The plan reviewer no longer fails a plan's Decisions lines whose reason nobody needs once the
  work is built, such as a test's data or the order of the steps, by asking for the comment
  wording. Rubric check 5 now passes a line that only follows a spec, an ADR, the practices or
  existing code, and asks five questions of every other line in order, stopping at the first yes:
  must later work follow it (an ADR), does a user or caller rely on it (the spec), does every
  piece of work do it this way (the practices), would someone changing the code need the reason
  (a comment beside the code), or otherwise nobody. In a trial on seeded plans, false alarms fell
  from 22 of 39 to 1, with the same catches. A line that fails only for lacking the comment wording
  now gains that wording in the correction instead of moving to Open questions. Nothing in your
  documents needs to change.

## [0.42.0] - 2026-11-11

### Added

- `/adr` offers diagrams of the chosen option. Once Decision says "Chosen:", each hand-over
  offers one line per diagram the text has enough for (at least three parts, actors,
  states or records and two connections between them), drawn as a flowchart, sequence diagram,
  state diagram or entity-relationship diagram. While questions are open the offers sit with the
  optional suggestions; once none are left, it asks "Would you like to add any of these diagrams to
  the ADR, or propose another?". Nothing is drawn unless picked. A picked diagram is a
  `mermaid` block in Decision, after the reason, drawn only from what the text says; rubric check
  18 has the reviewer check every box and arrow against the text.
- A `mermaid` diagram in an ADR's Decision does not count towards the 500 words of the plain part.
- The offer's sentences are shared in `scripts/skill_check.py`, so `/plan` can hold the same ones.

## [0.41.0] - 2026-11-11

### Changed

- ADR and spike reviews no longer count sentences. A sentence over 25 words, a paragraph of more
  than three sentences, a Question or Hypothesis over three sentences, or a reason for the choice
  over two no longer fails a review or a correction check. The reviewer checks instead that each
  paragraph makes one point and that a newcomer can follow every sentence in one reading, quoting
  any sentence that fails. The counts stay in `/adr` and `/spike` as a guide for the writer, and a
  reviewer may list a long sentence only as a suggestion. The word limits for the plain part, 500
  for an ADR and 600 for a spike record, are unchanged and still checked by script. Nothing in
  your documents needs to change.

## [0.39.1] - 2026-11-11

### Fixed

- When a plan's review fails a Decisions line on rubric check 5, `/plan`'s correction moves the
  line to Open questions, naming the ADR, spec change or practice it belongs in, instead of
  rewording it in place, which left the decision in the plan.

## [0.39.0] - 2026-11-11

### Changed

- `/plan` keeps a decision under Decisions only if nobody needs its reason once the work is
  built. A decision later work must follow goes to an ADR, one a user or caller relies on, such
  as what a tool returns, to the spec, and one every piece of work follows, such as how a check by
  hand runs, to practices: each as an open question naming that document. A decision whose
  reason only someone changing the code later needs stays, saying `/build` leaves the reason as a
  comment beside the code, and `/build` and its reviewer now see that the comment is there. Plan
  rubric check 5 goes through Decisions line by line with the same test.
  **Change needed:** a plan that is not `✅ Built` may now fail its next review on a Decisions
  line that passed before; move such a line to Open questions as the review says, or add the
  comment wording to a line whose reason only someone changing the code needs.

## [0.38.0] - 2026-11-11

### Changed

- A plan lists each requirement as a link to its heading in the spec, nested beneath the spec,
  as `  - [Reply to all](../specs/mail.spec.md#2-reply-to-all)`, in place of
  `  - Requirement: Reply to all`, and lists its ADRs as a `| ADR | Decision |` table, with the
  ADR's number as the link and its title beside it. The hook checks each anchor is the one GitHub
  gives the heading, and each title is the ADR's own, and names the right one when it is not.
  **Change needed:** a plan that is not `✅ Built` and still uses `- Requirement:` lines or ADR
  bullets is refused at sign-off with a message saying how to rewrite it; `/plan` rewrites those
  sections with its next edit, and `/audit` lists a `🟢 Ready to build` plan in the old layout
  until it is rewritten. Built plans are never checked, so they need nothing.
- In practices, the marks `/practices` ends a practice with, "(default)" and "(not set up yet)",
  count as plain words, so the language checker no longer reports them.

## [0.37.1] - 2026-11-11

### Fixed

- In auto mode, as in the Claude desktop app, a review agent that Claude Code ran in the
  background could lose its report, so the correction checker was refused with "No review ...
  is on record". The agent hands its report back as it finishes, and the plugin read it from the
  agent's transcript, which may not hold it yet. The plugin now takes the report from the
  hand-back itself, for document reviews and for /build's reviews. When the correction checker is
  refused for a missing report, the reason now names which report is missing.

## [0.37.0] - 2026-11-11

### Changed

- In practices, the Practices section of `AGENTS.md` and the files under `docs/practices/`, the
  lifecycle's own terms such as "spec", "ADR" and the statuses count as plain words, as they
  already did in an issue or a plan, since agents that follow the lifecycle read them. The
  plugin's commands, such as `/agentic:build`, now count as plain in all three.

## [0.36.0] - 2026-11-10

### Changed

- The plugin is now called `agentic`, for Skills for Agentic Engineering, and its skills are
  `/agentic:<name>`, such as `/agentic:spec`. Its repository is now
  `michaelmarconi/agentic-engineering`, and new installs come from the `michaelmarconi` catalog:
  `claude plugin marketplace add michaelmarconi/marketplace`, then
  `claude plugin install agentic@michaelmarconi`.
- New documents carry "Change status only through the agentic plugin's skills" as their comment
  line. Documents that say "sdlc" there need no change.

### If you installed `sdlc@sdlc`

1. Finish any review, build or spike in progress first: the plugin's saved records of them are kept
   under the old name and are not carried over.
2. Run `claude plugin marketplace update sdlc`. This rewrites `sdlc@sdlc` to `agentic@sdlc` in your
   settings, including a repository's `.claude/settings.json`, which you then commit.
3. Run `claude plugin install agentic@sdlc`, adding `--scope project` if you installed it that way.
4. Use `/agentic:<name>` from now on, and change any notes or scheduled commands that use the old
   `sdlc` prefix.

If step 2 cannot reach the catalog, run `claude plugin marketplace remove sdlc` and install from
the new catalog as above instead, adding `--scope project` if you installed it that way, and
commit the settings change. Moving to the new catalog later is described in the README. Never
enable both `agentic@sdlc` and `agentic@michaelmarconi`.

## [0.35.0] - 2026-11-10

### Changed

- `/sdlc:adr` no longer lets a choice rest on something nobody has tried. When the conversation says
  the choice depends on such a claim, such as "this only works if the provider sends events in
  order", the claim becomes the first open question, proposing a spike to test it, instead of being
  left under Out of scope "to be proven in the build". It stays open until the spike's finding comes
  back; a refuted claim opens the choice again. Only if you choose to go ahead without a spike does
  the ADR record the claim as untested at your word, under Consequences. Caveats you mention stay
  under Out of scope as limits.
- `/sdlc:spike` sends a finding that settles an ADR's open question to that ADR.

## [0.34.0] - 2026-11-10

### Changed

- Every spec, ADR, plan and spike record carries `date:` in its frontmatter: the day its status
  last changed, written YYYY-MM-DD. The skills write today's date into a new document and set it
  in the same edit as every status change, `/sdlc:build` sets it when it marks a plan `✅ Built`,
  and the status hook refuses a new document or a status change without today's date, any other
  change to the date, and a date after today. An ADR's date, which had no stated meaning, now
  means the same, so superseding an ADR also sets its date (ADR 0027, which supersedes ADR 0012;
  who approved a change is still recorded by the pull request).
- `/sdlc:audit` lists each spec, ADR, plan or spike record with no `date:` or a malformed one.
- The spec and plan reviewers keep the frontmatter's `#` line, as the ADR and spike reviewers do.

### Upgrading

- Documents written before this version have no date, and nothing breaks: they may be edited as
  before, and the next status change adds today's date. To give one its real date now, add a
  `date:` line by hand or with any edit, using the day of its last status change from git; adding
  a date is allowed even to an accepted ADR, a built plan or a finished spike record. `/sdlc:audit`
  lists the documents still without one.

## [0.33.0] - 2026-11-10

### Changed

- No open question is ever left bare. In a brief, ADR, plan or spike record, as already in a spec,
  each open question ends with "Proposed:" and the answer the skill would choose, so you can accept
  it in a word, or, where only you can know, what would settle it. In a brief, a proposal rests
  only on what you said. Each rubric gains a check for it.
- `/sdlc:build` and its reviewer read your practices where `/sdlc:plan` does: the Practices section
  of both `AGENTS.md` and `CLAUDE.md`, and the topic files they name, even when `CLAUDE.md` does not
  import `AGENTS.md`.
- A plan is temporary: once `✅ Built` it is frozen, and you may delete it whenever nobody needs it.
- Every skill whose document has a status signs it off on the same terms, and `/sdlc:spec` now asks
  whether to accept a spec once nothing is left to settle. Every document reviewer reports in the
  same shape, with Suggestions kept apart.
- Plans, like briefs, specs and ADRs, state handed-over material in their own words rather than
  referring to it. The hook that refuses a hyperlink or path to such material now checks plans and
  spike records too, as well as the brief, specs and ADRs (ADR 0026, which supersedes ADR 0023).
- The spike reviewer and plan reviewer read every title their references check needs.
- `/sdlc:adr` says how a draft written in the old layout is brought to the current one.

### Upgrading

- A brief, ADR, plan or spike record whose open questions have no "Proposed:" now fails its review
  the next time it is reviewed. Nothing else changes until then: the skill adds the proposals in
  its next edit.

## [0.32.0] - 2026-11-10

### Changed

- Specs have a new layout. A one-sentence Story, "When <situation>, <who> wants to <do
  something>, so they can <outcome>", replaces Problem and Goal; In scope and Out of scope replace
  Scope. Requirements are numbered headings, as `### 2. Reply to all`; the number is only for
  reading, and plans still name a requirement by its name alone. Each example is a two-column
  table headed `| Example | <name> |` with Given, When, Then and And rows, and How we'll check
  replaces Verified by.
- The spec rubric adds three checks: the first requirement states the outcome the story asks for,
  a spec covers one capability, and every open question proposes an answer. A rule's subject is
  something someone can see, never an internal step.
- `/sdlc:spec` plays the story and scope back for your yes before it drafts requirements, unless
  you asked it to write the spec straight away, and offers to split a story that holds two
  capabilities. It never writes a default it chose as a rule: that goes into Open questions as its
  proposed answer. It asks what happens when each requirement cannot be met, and settles words
  whose meaning is plain from the product without asking.
- The status hook refuses a plan line that gives a requirement's number, and refuses to accept a
  spec with no numbered requirement.

### Upgrading

- A spec written for an earlier version, with Problem, Goal and Scope sections and
  `### Requirement:` headings, breaks nothing while left alone. But a plan naming it cannot be
  signed off as Ready to build, and `/sdlc:build` will not start on such a plan, until the spec is
  reworked: the next edit `/sdlc:spec` makes to it brings it to the new layout and checks, keeping
  what it says and the requirement names, and asks about anything the new checks need. That edit
  returns an accepted spec to Draft, so accept it again, then sign the plan off again. The hook,
  `/sdlc:plan` and `/sdlc:build` each say this plainly, and `/sdlc:audit` lists every spec still
  in the old layout, so you can see the rework before it is in the way. Briefs, ADRs, plans and
  spike records need no change.

## [0.31.0] - 2026-11-10

### Added

- Every lifecycle document says what kind of document it is in a `type:` field, the first in its
  frontmatter: `Brief`, `Spec`, `ADR`, `Plan` or `Spike`. The brief gains frontmatter holding
  only `type: Brief`. Titles no longer name the type, as "Spec:" or "ADR:" in front of them
  would; each document skill says so in the same sentence.
- The status hook refuses an edit that gives a document the wrong `type:` for its folder, a new
  document without one, or that takes an existing one away. `/sdlc:audit` reports a wrong
  `type:`.

### Changed

- Documents written before this version need no change by hand: each gains `type:` on its next
  edit through its skill. A decided document, such as an accepted ADR, a built plan or a
  finished spike record, may keep lacking it for good; adding it is always allowed and counts
  as no other change, so an old accepted ADR can still be superseded.

## [0.30.0] - 2026-11-09

### Changed

- Every skill that writes a document shows it to you the same way when it hands it over: in your
  Claude app's file viewer where there is one, so you can select lines in it to comment on, and
  always by its full path. It never sends you to a code-hosting site, such as GitHub, to read it. In a
  claude.ai project thread, where the viewer shows a copy, a fresh copy follows each change.
  See ADR 0025.
- The plugin's skill check fails a document skill that does not hold this sentence word for word.

## [0.29.0] - 2026-11-09

### Changed

- An ADR that names an earlier ADR links the number to that ADR's file, such as
  `[ADR 0001](0001-example-subject.md)`, so a reader can click through. The ADR rubric fails a
  bare number, and the template shows the linked form. The `supersedes:` and `superseded-by:`
  fields still hold bare numbers.
- The plugin's reference check refuses an ADR edit that adds a link to an ADR file that does not
  exist, matched by its exact name.

### Fixed

- `/sdlc:audit` no longer reports an ADR that links to another ADR as a references problem.

## [0.28.0] - 2026-11-08

### Changed

- ADRs are written to be read by people first, keeping the spirit of MADR. An ADR reads from
  plain to technical: Question, Decision, Background, Options, Consequences, Out of scope, How
  we'll check and Open questions, with the exact mechanism, rules and evidence under Technical
  detail at the foot. The part above Technical detail is at most 500 words; `adr.py words`
  counts it, and the status hook refuses to accept a longer ADR.
- `/sdlc:adr` writes the Question first and leaves Decision as "Not chosen yet; see Open
  questions." until you choose. Once you have, Decision opens with "Chosen:" and names the option
  in full, so it makes sense on its own; the status hook refuses to accept an ADR whose Decision
  does not. Options is a table saying of each option whether it was chosen or rejected, and why.
- A limit, an untested assumption or a decision left for later goes once under Out of scope, not
  under Consequences. An ADR that bundles two decisions is split by the skill rather than asked
  about.
- How we'll check replaces Confirmation. `/sdlc:audit`, `/sdlc:plan` and `/sdlc:build` read How
  we'll check, Decision and Technical detail, and still read Confirmation and Decision Outcome in
  ADRs accepted before this version.

### What you need to change

- ADRs already accepted need nothing: they keep working as they are. A draft ADR in the old
  layout, with Decision Outcome and Confirmation, cannot be accepted until it is re-laid from the
  new template; `/sdlc:adr` can do this for you.

## [0.27.0] - 2026-11-08

### Changed

- Spike records are written to be read by people first. A record now tests a hypothesis, a claim
  the experiment confirms or refutes, rather than answering a question, and reads from plain to
  technical: the hypothesis and the finding at the top, then How we'll know, Out of scope, How the
  test works, Risks and safeguards, Results and Surprises, with the experiment's detail, its code
  and its runs at the foot. The part above Experiment is at most 600 words; `spike.py words`
  counts it, and the status hook refuses to move a longer record forward.
- The Finding opens with Confirmed, Refuted or Not settled and then says what was found in full,
  so it makes sense on its own, never a bare "Yes" or "No". Results lists every run in a table,
  saying which runs count. The status hook refuses a finishing status the Finding does not open
  with.
- The finished statuses are now `💡 Confirmed`, `🚫 Refuted` and `❔ Not settled`, replacing
  `💡 Answered` and `❔ Not answered`. Where it goes is now Next steps.

### What you need to change

- Spike records written before this version use the old sections and statuses, which the hooks,
  the run script and `/sdlc:audit` no longer recognise. Rewrite any you keep in the new layout
  from the template, or delete them once their finding has reached its spec or ADR.

## [0.26.0] - 2026-11-05

### Added

- `/sdlc:practices` suggests a new topic, Delivering work: how work is split, how big one plan
  may be, measured by what a person can review, how many finished builds may wait for review,
  and what done means. It leaves out ways of working that exist for people rather than agents,
  such as sprint length, estimates and pair programming. Branches and commits now also asks how
  long a branch may live and how often it is merged back.
- `/sdlc:plan` reads your practices. Where they say how work is split or how big one plan may be,
  it plans within that; when the work is bigger, it proposes splitting it into several plans and
  asks which to plan first. If you keep the work as one plan, the plan says why under Decisions,
  and the plan's reviewer checks this.
## [0.25.0] - 2026-11-05

### Changed

- The brief, specs and ADRs now stand on their own. They refer to outside material only by a
  web link, and never, by hyperlink, path or title, to material handed over in the conversation
  (such as a requirements document, notes or a ticket), to anything outside the repository, or to
  a file under `docs/` that is not a lifecycle document. What matters from such material is
  stated in the document's own words. `/sdlc:brief`, `/sdlc:spec` and `/sdlc:adr` leave such a
  reference out and say why, and their reviewers check for it.
- The brief rubric's "Links back it" check is gone, so the brief reviewer no longer reads the
  documents a brief links to. A brief that links to a file under `docs/` that is not a lifecycle
  document fails its References check: restate what matters from that file in the brief.

### Added

- A hook refuses any edit that adds such a hyperlink or path to a brief, spec or ADR, and names
  each one (ADR 0023). A reference the document already held is not refused again, so older
  documents and decided ADRs can still be edited as the lifecycle allows.

## [0.24.3] - 2026-11-05

### Fixed

- On Python 3.6, the plugin now warns you when a session starts, rather than
  letting its checks fail later with an unclear error. The README now gives the minimum
  version, Python 3.7.

## [0.24.2] - 2026-11-05

### Fixed

- A correction check now works when Claude Code runs the reviews in the background, which it can
  do even when a skill asks for the foreground. The plugin's hooks used to keep a review's report
  only from the Agent tool's result, which for a background run is just a launch notice, so the
  correction checker was refused. They now keep the report that arrives when the agent finishes,
  for every document skill and for `/sdlc:build`, and no longer refuse reviews started in the
  background.

## [0.24.1] - 2026-11-05

### Fixed

- A correction check now works after the session ends and the same conversation carries on, as
  with `claude --resume` or a restarted cloud container. The plugin's hooks used to delete
  their saved reviews and build reports when a session ended, so the correction checker was
  refused. They now keep them, and delete any left unchanged for 30 days, the time after which
  Claude Code deletes the conversation itself. A resumed `/sdlc:build` session also keeps its
  branch guard. (#37)

## [0.24.0] - 2026-11-05

### Fixed

- Reviews now work when Claude Code is started in a folder other than the repository's, such as
  one holding several projects. Every skill that writes a document gives its reviewers the
  document's full path, and a plugin hook finds the repository from it, so each reviewer, the
  language checker and the correction checker read the document, and the documents they compare
  it with, from the right repository. A review of a document the hook can't find is refused, and
  an agent that still can't read its document reports an error, never a pass. `/sdlc:audit`'s
  agents follow the same rule.

## [0.23.1] - 2026-11-05

### Fixed

- `/sdlc:audit` no longer reports a clean result for documents it never read. Run from a folder
  other than the repository's, its agents used to look for the documents in the wrong place,
  find nothing and report no drift. Now every agent is given the repository's full folder, and
  an agent that still can't read its document reports an error, which the audit lists first as
  a document not checked. To audit a repository that isn't the folder you are in, name it, such
  as "audit the code in invoice-tool/".

## [0.23.0] - 2026-11-05

### Changed

- A brief or a spec can now have sections beyond the six it needs, such as "Safety and security"
  in a brief or "Security" in a spec, when you ask for them. The six must still all be there in
  their order, and Open questions stays last. Every other check applies to the new sections too,
  so they can't hold a feature list, a design or a guess, and a spec's requirements stay under
  Requirements. Before, the reviewer failed any section beyond the six.

## [0.22.0] - 2026-11-05

### Added

- `/sdlc:audit` finds drift, where the code and its documents no longer agree. A script checks
  every spec, ADR, plan and spike record as it stands: statuses, open questions, references,
  supersede pairs, ready plans and plans that build the same requirement. Then one fresh agent per
  `👍 Accepted` spec and ADR checks the code against it, and a second agent tries to disprove
  each drift it reports before you see it. Each finding comes with quotes of the document and the
  code, and a suggested correction and the skill that makes it. It can check the whole
  repository, the commits of a window (`last 7 days`, or `since <commit>`), or one named
  document, and it changes nothing in your repository, so it is safe to run as a scheduled
  routine. If your practices say what to do with its findings, such as filing issues, it does
  that once it has reported.

## [0.21.0] - 2026-11-04

### Added

- `/sdlc:spike` settles one unknown by a throwaway experiment. It writes a spike record in
  `docs/spikes/`: the question, the result that would answer it, the experiment and its code.
  Once the design is reviewed and you sign it off, it runs the experiment only through its run
  script, which writes each run's output into the record word for word. Then it writes the answer,
  has that reviewed too, and tells you which spec or ADR the answer belongs in. Experiments run
  in a fresh folder outside your repository, so your working tree is never touched. Secrets
  reach them only from Claude Code's environment, and are hidden in the recorded output.
- Spike records have their own statuses: `📝 Draft`, `🟢 Ready to run`, `💡 Answered` and
  `❔ Not answered`. The status hook enforces them. It also refuses any edit to a record's runs,
  and any change to a finished record.

### Changed

- `/sdlc:spec`, `/sdlc:adr`, `/sdlc:brief` and `/sdlc:plan` never refer to a spike record, so it
  can be deleted at any time. `/sdlc:spec` and `/sdlc:adr` can draft from a finished record, and
  state its evidence in their own words.

## [0.20.0] - 2026-11-04

### Changed

- Skills that write documents no longer review after every answer. While you walk through open
  questions, the review runs once when the walk-through ends, because no questions are left or
  you stop. A change you make or ask for at any other time is still reviewed once it is made. The lifecycle page's Review process says when a review
  runs, and a script check makes every such skill, including future ones, carry the same rule.
- The README says to install the plugin before starting the session you will use it in, since a
  plugin installed partway through a session only loads in the next one.

## [0.19.0] - 2026-11-04

### Added

- `/sdlc:practices` has a CI/CD topic. It asks where the pipeline is defined and what it runs,
  which checks are required, how to run them locally before pushing, what an agent does when a run
  fails (reproduce it, fix the cause, re-run at most once, never skip or disable a test), who may
  change the pipeline and how deployments start. Which CI service to use is left for
  `/sdlc:adr`.

### Fixed

- The `/sdlc:practices` overview reads the practices and the repository again each time, even
  later in a conversation, so it sees changes made outside it.
- `/sdlc:practices` no longer calls an answer recorded before the files are written.

## [0.18.0] - 2026-11-04

### Added

- `/sdlc:practices` records how your project does things, for coding agents to follow: the
  commands that set it up, run it and check the work, the rules an agent follows, and the files
  to read before a task. The essentials go in a `## Practices` section of `AGENTS.md`, and longer
  topics in files under `docs/practices/`. On its own it gives an overview of what is recorded,
  missing or out of step with the repository, and suggests where to start; with a topic, such as
  `/sdlc:practices testing`, it covers that topic alone. It reads the repository first and
  proposes what it finds, asks one question at a time, never writes a secret or makes a choice
  between technologies, and adds the line `@AGENTS.md` to `CLAUDE.md`, asking first if you
  already have one. Its changes are reviewed, corrected once and checked like every document.
- A hook refuses any edit by Claude that would take the Practices section past 50 lines or a
  practices topic file past 200, or that adds an `@` import to either.

### Changed

- One review can now cover several files at once, so a change to the Practices section and to a
  topic file is reviewed, corrected and checked together.

## [0.17.1] - 2026-11-04

### Added

- The plugin is released under the MIT licence, in `LICENSE`, so you may use, change and share
  it in your own and your clients' projects.

## [0.17.0] - 2026-11-04

### Changed

- `/sdlc:plan` writes a reviewer's decision that only you can make into the plan's Open
  questions, as `/sdlc:spec` and `/sdlc:adr` already do, so the plan cannot be marked
  `🟢 Ready to build` until you have settled it.
- The spec and brief reviewers now see the titles of your ADRs and plans, so they catch a
  reference to one by its title.
- The lifecycle rules now say an ADR may refer to any other ADR by number, as the ADR reviewer
  already allowed.

### Fixed

- The README and the `/plan` page no longer say a built plan is removed: it is kept for good, as
  the lifecycle says.
- The docs no longer describe `/audit` as working, or the language checker as part of
  `/sdlc:build`'s review.
- `/sdlc:spec`'s description no longer calls accepting a spec "ready to build".
- Smaller corrections across the README, the lifecycle rules and the skill pages, so they agree
  with each other and with the skills.

## [0.16.0] - 2026-11-04

### Changed

- `/sdlc:issue` is now `/sdlc:feedback`: same skill, new name. Type the `sdlc:` prefix, since in
  the terminal a bare `/feedback` is Claude Code's own command, which sends feedback to
  Anthropic. It still drafts and files a GitHub issue on the plugin's repository.

## [0.14.1] - 2026-11-04

### Fixed

- In a Claude project thread, the correction check failed every time: an agent's report reaches
  Claude there as a separate message, and the hooks that keep review reports saved only the
  tool's note saying where the report went. They now keep the report itself, for document
  reviews and for `/sdlc:build`'s reviews.

## [0.14.0] - 2026-11-04

### Added

- The design of `/sdlc:practices`, a skill not built yet, on its own page. It will record how a
  project does things, one topic at a time and whenever you need it: the essentials in a
  `## Practices` section of `AGENTS.md`, at most 50 lines, and longer topics in
  `docs/practices/`. `/sdlc:build` follows them.

### Changed

- The README and the lifecycle rules show the skills in three groups, each with its own small
  diagram: deciding what to build, building it, and skills used at any time.
- Recorded practices are the one thing the plugin writes outside the lifecycle's own documents,
  and only when you ask it to.

## [0.13.0] - 2026-11-04

### Added

- `/sdlc:build` builds one `🟢 Ready to build` plan on a branch of its own, tests first,
  requirement by requirement. It then has the work checked by three reviews side by side: Claude
  Code's own `/code-review` and `/security-review`, and a build reviewer that checks the work
  against the plan, its specs and ADRs. It corrects what they find once, has the corrections
  checked, and hands the branch back, committed and pushed. It never opens a pull request and
  never merges: verifying the software, opening a pull request and merging stay with you.
- `/sdlc:build` starts only in answer to the first message of a session, or the first after
  `/clear`, so a build always begins with a clean context. A plugin hook enforces this.
- Before starting, `/sdlc:build` checks that the plan is ready, that the specs and ADRs it names
  are still `👍 Accepted`, that nothing is uncommitted, that the repository has a remote named
  `origin` whose default branch git knows, and that `/code-review` and `/security-review` can
  run. It stops and says why if any check fails.
- While a build runs, a plugin hook refuses any commit or push to the default branch.
- `/sdlc:build` leans towards carrying on rather than asking. It corrects obvious defects, such
  as a crash on input no spec mentions, chooses error wording and exit codes, takes its own
  recommendation on choices that are easy to change later, and works out from the repository any
  practice that is not recorded, such as how to run the tests. Its summary lists each of these.
  It stops only for a real product choice or something hard to undo.
- A hand-over script commits what is left, marks the plan `✅ Built` when every review passed,
  and pushes the branch, reporting exactly what it did.

### Changed

- A `✅ Built` plan is kept as the record of what was built and how, and is never changed. Only
  `/sdlc:build`'s hand-over script sets `✅ Built`; the hook refuses it from anywhere else.
- The plugin is now tested on Opus 5.5 only. Its reviewers still run on Sonnet.

### What you need to change

- To use `/sdlc:build`, your repository needs a remote named `origin`. If `git` does not know
  its default branch, run `git remote set-head origin -a` once.

## [0.12.0] - 2026-11-03

### Changed

- Specs now have the statuses `📝 Draft` and `👍 Accepted`. A spec's status says whether you
  have accepted its text; it describes the document, never the software, because a status about
  the software would stop being true, without anyone noticing, as the code changes. To find out
  whether the software meets a spec, check the software against it. `/sdlc:spec` sets
  `👍 Accepted` when you sign a spec off, under the same rules `🟢 Ready to build` had, and any
  change returns it to `📝 Draft`.
- A plan can be `🟢 Ready to build` only when every spec it names is `👍 Accepted`.
- The hook refuses a new spec or plan written with another kind of document's status, such as a
  new spec written as `✅ Built`.

### What you need to change

- A spec that is `🟢 Ready to build` or `✅ Built` keeps that status until it is next changed,
  and the hook does not check it until then. Before `/sdlc:spec` can accept it, set it back to
  `📝 Draft`, then accept it again; a plan that names it cannot be `🟢 Ready to build` until it
  is `👍 Accepted`.

## [0.11.0] - 2026-10-29

### Added

- `/sdlc:plan` plans one piece of work before it is built. It finds the requirements of settled
  specs and the accepted ADRs the work builds, explores the code with Claude Code's own Explore
  and Plan helper agents, and settles each technical decision with you one at a time, proposing
  an answer and whether it belongs in the plan or in an ADR. Only then does it write a short plan
  in `docs/plans/YYYY-MM-DD-<title>.md`, have it reviewed and corrected once, and hand it to you.
  It never makes a technical decision for you, and it does not use Claude Code's plan mode.
- Plans have the statuses `📝 Draft`, `🟢 Ready to build` and `✅ Built`. The hook refuses
  `🟢 Ready to build` unless the plan has no open questions, every spec it names is
  `🟢 Ready to build` or `✅ Built` and holds each requirement it names, every ADR it names is
  `👍 Accepted`, and no other plan that is not `✅ Built` names the same requirement. Any change
  to a `🟢 Ready to build` plan returns it to `📝 Draft`. Only the build step will set
  `✅ Built`; until it exists, the hook refuses it.
- A plan reviewer agent checks each plan against the plan rubric, beside the language checker.

### Changed

- In a plan, as in an issue, the lifecycle's own terms such as "spec", "ADR" and the statuses
  count as plain words.
- The language checker no longer reads a document's frontmatter, whose wording the plugin fixes.

## [0.10.0] - 2026-10-29

### Changed

- ADRs now end with an Open questions section, as specs do. Whatever only you can settle, such
  as an option nobody named or why one was rejected, is written there instead of only being
  asked in the conversation. Your answer goes into the ADR and the question is removed.
- An ADR can be `👍 Accepted` only when its Open questions section is empty or says "None.". The
  hook refuses the change otherwise, and says so when the section is missing altogether. A
  `❌ Rejected` ADR may keep open questions.
- New ADR files are named `NNNN-<subject>.md`, where the subject is three to five words on what
  the decision is about, such as `0004-session-data-storage.md`. The title inside still states
  the decision.
- The lifecycle has a new principle: no document moves forward while it has open questions.

### Fixed

- The hook no longer counts the indented lines of a wrapped footnote after Open questions as
  open questions, which could block a spec or ADR from moving forward.

**This affects documents you already have.** A `📝 Draft` ADR written before this version has
no Open questions section, so it cannot be accepted until one is added, holding "None." if
nothing is open; that change needs a new review. ADRs that are already decided need nothing.
Renaming older ADR files to the new pattern is optional and done by hand, with `git mv`.

## [0.9.0] - 2026-10-29

### Changed

- Every document status now starts with an emoji: `📝 Draft`, `🟢 Ready to build`, `✅ Built`,
  `👍 Accepted`, `❌ Rejected` and `↪️ Superseded`. New specs and ADRs are written that way, and
  the plugin's pages name each status the same way.
- The plugin's hook now refuses a status written without its emoji, or with the wrong one, and
  says what to write instead. **This affects documents you already have.** A spec or ADR whose
  status is a bare word, such as `status: Accepted`, still counts as that status, but the next
  change Claude makes to it must also add the emoji. A change that only adds the emoji to the
  status line is always allowed, even on an ADR that is already decided. To bring every document
  over at once, ask Claude to add the emoji to each status line under `docs/specs/` and
  `docs/adrs/`.

## [0.8.1] - 2026-10-29

### Fixed

- On a computer without Python 3, the hook that checks spec and ADR status changes failed with
  only a warning, so Claude's edits to those documents went through unchecked. Such edits are
  now refused, with a message saying the plugin needs Python 3. Edits to any other file are not
  affected.

## [0.8.0] - 2026-10-29

### Added

- A language checker reads every document `/spec`, `/brief`, `/adr` and `/issue` write, at the
  same time as the skill's reviewer, and reports any words someone new to your project could not
  follow. The skill corrects what both reports find in its one round of corrections, and the
  correction checker checks those corrections too. The reasons, with the measurements behind
  them, are in this plugin's ADR 0013.
- A Plain words rule in the lifecycle page says what the checker holds documents to: computing
  terms are used freely, a term from your product's own field gets a footnote defining it where
  it first appears, and anything else a newcomer would not know, such as a team nickname or a
  figure of speech, is rewritten in plain words.

### Changed

- The brief's rubric no longer has its own plain words check, since the language checker now
  does that job for every skill.
- The note at the top of a new spec or ADR, and the prompt in the spec template's Problem
  section, are reworded in plain words.
- When a new spec conflicts with another spec, the hand-over names that spec and the rule that
  conflicts, since the spec itself cannot refer to it.

## [0.7.0] - 2026-10-28

### Changed

- `/spec`, `/brief`, `/adr` and `/issue` now take every document through a fixed review
  sequence: one review, one round of corrections, then a check of only those corrections by a
  shared correction checker. If the check fails, the skill stops and shows you its report rather
  than reviewing again. The reasons, with the measurements behind them, are in this plugin's
  ADRs 0010 and 0011.
- When the sequence ends, the skill gives you the review report, the check's report, the number
  of items left for you to settle, and then asks you about the first of them only. The reviewers'
  suggestions are listed separately as optional.
- `/adr` is also used when you ask to review or correct an existing ADR.

### Added

- A hook hands the correction checker the review report and the document as it was reviewed,
  word for word. It keeps them in the plugin's own data folder, outside your repository, and
  deletes them when the check is done or the session ends.
- A hook lets the plugin's skills and agents read the plugin's own files, such as a rubric,
  without asking you each time. It approves reads inside the plugin's folder only.

## [0.6.0] - 2026-10-27

### Added

- A new rule for the whole lifecycle: documents refer to one another only where neither end can
  go stale. A plan refers to the specs and ADRs it builds, and an ADR to the ADR it supersedes or
  that supersedes it. The brief, specs and ADRs never refer to one another in any way, whether
  by hyperlink, path or title, because either end can change or be deleted without the other
  being touched. The README and the summary Claude gets at the start of each session say so.
- The spec and brief rubrics have a References check, so their reviewers flag any such
  reference. When you ask `/spec` or `/brief` to add one, it leaves it out and tells you why.
  The brief still links to source material, such as a survey, as before.

### Changed

- A spec or brief you already have that refers to another lifecycle document now fails review
  the next time `/spec` or `/brief` changes it, which removes the reference. Nothing else in
  your documents needs to change.

## [0.5.0] - 2026-10-27

### Added

- `/adr` records one technical decision as an ADR (architecture decision record) in
  `docs/adrs/NNNN-<title>.md`, using the core of the MADR format: the context, the options
  considered and why each lost, the decision, its good and bad consequences, and a Confirmation
  saying what it applies to and how to check the code follows it. It drafts from your
  conversation, writes one ADR per decision, and has each one reviewed before you see it.
- ADRs move from Draft to Accepted or Rejected, and from Accepted to Superseded when a newer ADR
  replaces them. Only you can accept or reject an ADR: `/adr` asks you once the reviewed text is
  final.
- The status hook now covers ADRs too: it refuses status changes the lifecycle does not allow,
  and any edit to an ADR that is no longer a Draft, apart from marking it Superseded by an
  accepted replacement.

### Changed

- ADRs live in `docs/adrs/`, not `docs/decisions/`, and start as Draft rather than Proposed.

## [0.4.1] - 2026-10-27

### Added

- This changelog. Claude Code tells you when the plugin has updated but not what changed, so
  each version now has an entry here; the README's Update section points to it.

### Changed

- The plugin's versions follow Semantic Versioning: a fix is a patch, a new skill or new
  behaviour is a minor version, and a change that breaks documents you already have, or the
  lifecycle, is a major version. Until 1.0.0, a breaking change bumps the minor version and
  its entry says what breaks.

## [0.4.0] - 2026-10-27

### Added

- `/brief` writes or changes your product brief, `docs/brief.md`: the one short document that
  says what the product is, who it is for, why it exists and how you will know it works. It
  has a one-line summary and sections for Problem, Who it's for, Goals, Out of scope,
  Constraints and Open questions. Unlike a spec, a brief has no status.
- `/brief` drafts from what you have already said, reads only what you point it to, and asks
  before reading anything else. It gives the number of open questions and asks them one at a
  time, and it explains every acronym the first time it appears, title included.
- A brief reviewer checks the draft against the brief rubric before you see it. Where the
  brief links a document in your repo, the reviewer also checks the brief against it. Any
  remaining decisions are left to you.

## [0.3.0] - 2026-10-27

### Added

- `/issue` reports a bug or suggests an improvement in this plugin. It drafts the issue from
  the plugin's bug or improvement template, filling in Context with the plugin, Claude Code and
  operating system versions, and it can propose an eval case for the fix.
- Your project's details stay out of the issue: `/issue` paraphrases rather than quoting your
  repo, and replaces real names and code with stand-ins. An issue reviewer checks the draft
  before you see it.
- Nothing is filed until you approve the draft. `/issue` then files it with `gh`, as the
  GitHub account it showed you, or gives you a pre-filled link to submit yourself.

## [0.2.1] - 2026-10-27

### Added

- `/spec` writes or changes a spec with you: one living document per capability under
  `docs/specs/`, with sections for Problem, Goal, Scope, Requirements, Constraints and Open
  questions. Each requirement is one rule with Given/When/Then scenarios and a "Verified by:"
  line saying how it will be checked.
- `/spec` drafts from what you have already said and asks only about the gaps: it gives the
  number of open questions, then asks them one at a time. It keeps technical choices out of
  the spec and adds no behaviour you didn't ask for.
- A spec reviewer, which always runs on Sonnet, checks every draft against the spec rubric
  before you see it. It separates decisions only you can make, which block Ready to build,
  from suggestions, which don't. `/spec` fixes what it can and passes the rest to you.
- Spec statuses: Draft, Ready to build and Built. A spec becomes Ready to build only once you
  have seen its final text, it has no open questions and its review has passed. Built is
  reserved for `/build`, which isn't released yet.
- A session-start hook that gives Claude a short map of the lifecycle, only in repos that use
  it.
- A hook that refuses spec edits making a status change the lifecycle doesn't allow, such as
  skipping Draft or setting Ready to build while open questions remain.

## [0.1.1] - 2026-10-26

### Changed

- The README now explains the whole lifecycle for a reader starting with no context: the
  Planning steps (`/brief`, `/spec`, `/spike`, `/adr`, `/plan`), Building (`/build`) and
  `/audit`. Each skill has its own page under `docs/skills/`; for skills not yet released,
  that page is a placeholder.

## [0.1.0] - 2026-10-22

### Added

- The plugin and its own marketplace, so you can install it with
  `claude plugin marketplace add michaelmarconi/sdlc` and `claude plugin install sdlc@sdlc`.
  It has no skills yet.
