# Feedback rubric

Each check passes or fails. `/feedback` reads this while drafting; the feedback reviewer reads it while
checking, and quotes the draft as evidence for every failure.

1. **Shape.** The draft has a title and a body. The body uses the headings of its kind's
   template, bug or improvement, in the template's order, and nothing is left under a heading
   as a placeholder.
2. **Specific title.** The title says what went wrong or what should change, and names the
   skill, agent or hook involved when one is. "Spec skill bug" fails; "/spec puts a library
   choice in a requirement" passes.
3. **One problem.** The issue reports one problem or one improvement. Two unrelated ones are two
   issues.
4. **Redacted.** Nothing identifies the person's project, organisation, people or code: no
   names, product names, paths, URLs, hosts, identifiers, secrets or sentences taken from their
   repository. Each is replaced with a plain stand-in such as "a web app" or
   `docs/specs/example.spec.md`. A stand-in shares no distinctive part with what it replaces:
   `kafka.internal.example.com` standing in for `kafka.internal.acme.io` still leaks the host,
   and so does a file's own name kept in a stand-in path. A sentence from their repository with
   the names swapped is still their sentence: describe what it says in other words instead.
   Ordinary words and short phrases that would describe many projects, such as "nightly sync" or
   "password reset", are not leaks, and neither are the plugin's own files and well-known public
   technologies.
5. **Context.** Context gives the plugin version, the Claude Code version and the OS, names the
   skill, agent or hook involved (or says none is known). A version that couldn't be read is
   given as "unknown", which passes, and describes any lifecycle documents
   involved by kind and status, such as "a `👍 Accepted` spec with two requirements".
6. **Reproducible.** A bug's Steps to reproduce let someone without the person's repository
   produce the same behaviour: a starting state built from stand-ins, the exact request to make,
   and what then happens. When the original request isn't known, the steps give a concrete
   request that should reproduce it and say it is a reconstruction; "mention a technology in
   the request" is not a request.
7. **Concrete.** What happened and what was expected (or what got in the way and what would be
   better) are stated separately and concretely enough to tell whether a fix works. "It was
   confusing" fails unless it says what was confusing and where.
8. **Eval when it fits.** Proposed eval is either a case or "None", with a one-line reason for
   "None". A case is a request to Claude with the plugin loaded, so a problem in a file no
   request exercises, such as the README's layout, has "None". A case gives the prompt, any starting files as stand-ins, and checks that would fail
   today and pass once fixed. A concrete, reproducible report has a case; a report too vague to
   check has "None" rather than a case invented to fill the heading.
