You are finishing a spec with the person, and the spec at SPEC_PATH is your draft. Take it through
review now, in this order, one step at a time, and do nothing else:

1. Start the `relay:spec-reviewer` agent. Its request must be exactly these two lines:
   Document: SPEC_PATH
   Review this spec.
2. Correct the spec once, editing the file, for every failure and other finding in the report.
   A decision under Needs a person becomes an entry in the spec's Open questions; never guess it.
   Wait until every edit has succeeded before going on.
3. Start the `relay:correction-checker` agent. Its request must be exactly these two lines:
   Document: SPEC_PATH
   Check the corrections.
   Do not add the report or any text of the spec to the request.
4. Reply with the checker's report, word for word.
