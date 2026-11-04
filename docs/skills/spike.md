# `/spike`

*Not built yet.*

When an unknown can only be settled by trying something, we build a throwaway experiment before
the real work. A fact goes back into the spec; a choice becomes an ADR. A spike agent runs the
experiment in its own copy of the repository, so the throwaway code never touches the real work.

The spike agent will work in its own git worktree, which is deleted when the spike ends.
