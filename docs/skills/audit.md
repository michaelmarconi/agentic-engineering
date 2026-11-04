# `/audit`

*Not built yet.*

Code and its documents can drift apart, for example when someone changes code without going
through this lifecycle. `/audit` will check the code across the whole repository against each
spec and `👍 Accepted` ADR, and report where they disagree; you choose whether to fix the code,
return the spec to `📝 Draft`, or supersede the ADR.

Its findings will appear only in the conversation, each with a suggested way back.
