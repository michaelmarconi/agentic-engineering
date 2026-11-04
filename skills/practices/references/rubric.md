# Practices rubric

Each check passes or fails. `/practices` reads this while writing; the practices reviewer reads it
while checking, and quotes the practices as evidence for every failure. A hook (ADR 0019) already
refuses an edit that takes the section past 50 lines or a topic file past 200, or that adds an `@`
import, so the reviewer does not count lines or look for imports in the section or topic files.

1. **Shape.** The `## Practices` section of `AGENTS.md` has three `###` headings, in order: Check
   your work, Rules, Files to read before a task. A part with nothing in it says "None yet."
   rather than being left out.
2. **Commands are real.** Each script or file path a command names exists in the repository, and
   each tool it runs is one the repository's build, dependency, CI or setup files use. A command
   the repository does not show yet passes only while the section says it is not set up yet.
3. **Commands are exact.** Each command is the literal text to run, with no placeholder the agent
   would have to guess. Apart from the command that runs the product, each finishes on its own
   without asking for input or waiting in watch mode.
4. **Rules can be acted on.** Each rule says what to do or not do, in a way an agent could follow
   or break, such as "run the linter before every commit". A vague aim ("write clean code")
   fails.
5. **Pointers say when.** Apart from a "None yet." line, each line under Files to read before a
   task names one file under `docs/practices/` and the task that calls for reading it.
6. **Pointers match the topic files.** Each file a pointer names exists, and every file under
   `docs/practices/` is named by exactly one pointer.
7. **Topic files stand alone.** A topic file covers one topic and refers to no other file the
   agent must read to follow it.
8. **Core and topic files agree.** No topic file contradicts the core, such as by giving a
   different command for the same job.
9. **Practices, not choices.** Nothing picks between real alternatives, such as a language,
   framework, library, test framework or code style: those belong in ADRs. Saying how to use what
   an ADR chose passes.
10. **Nothing secret.** No password, key, token or other secret appears; saying where secrets live
    passes.
11. **Nothing guessed.** No practice is hedged ("probably", "usually", "we assume") or carries a
    marker such as [?] or TODO. A practice that is a default the person accepted, rather than
    something they said or the repository shows, says it is a default.
12. **CLAUDE.md imports AGENTS.md.** `CLAUDE.md` exists and has a line that is exactly
    `@AGENTS.md`.
