# Invoice tool

## Practices

- Python 3, standard library only. The code lives in `src/`, the tests in `tests/`.
- Run the tests with `python3 -m unittest discover -s tests -t .` from the repository root.
- After every `/sdlc:audit`, file each drift finding it reports as a GitHub issue with `gh issue create`, one issue per finding.
