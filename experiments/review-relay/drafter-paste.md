You are finishing a spec with the person, and the spec at SPEC_PATH is your draft. Take it through
review now, in this order, one step at a time, and do nothing else:

1. Start the `relay:spec-reviewer` agent. Its request must be exactly these two lines:
   Document: SPEC_PATH
   Review this spec.
2. Read the spec, so you have its text exactly as it was reviewed.
3. Correct the spec once, editing the file, for every failure and other finding in the report.
   A decision under Needs a person becomes an entry in the spec's Open questions; never guess it.
   Wait until every edit has succeeded before going on.
4. Start the `relay:correction-checker` agent. Its request must be, in this order:
   - the line `Document: SPEC_PATH`
   - the line `Check the corrections.`
   - the line `=== REVIEW REPORT ===`, then the reviewer's report word for word, then the line
     `=== END REVIEW REPORT ===`
   - the line `=== DOCUMENT AS REVIEWED: SPEC_PATH ===`, then the spec's text as you read it in
     step 2, word for word, then the line `=== END DOCUMENT ===`
5. Reply with the checker's report, word for word.
