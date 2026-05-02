# `gz adr audit-check` covers-backfill heuristic fixtures

Authored under OBPI-0.0.23-05 (closes GHI #309). Both fixtures are
**git-history-shape** rather than live filesystem fixtures: they declare the
expected `(git log --reverse -L<line>:<file>)` and
`(git rev-list --count <intro>..<receipt>)` outputs that the heuristic should
observe via the `git_runner` callable, plus the matching ADR / OBPI / test
file shapes.

The unit tests under `tests/governance/test_audit_check_covers_backfill.py`
mock `git_runner` directly (REQ-0.0.23-05-08); these fixture files are
end-to-end witnesses consumed by:

- The BDD scenario at `features/adr_audit_covers_backfill.feature`
  (`@REQ-0.0.23-05-09`).
- Future operator-facing reproductions of the heuristic in a sandbox repo.

## `legitimate_evolution/`

A `@covers(REQ-X.Y.Z-NN-MM)` decorator landed **30 commits / 60 days before**
the REQ's closing receipt — the canonical legitimate-evolution case. The
heuristic MUST NOT flag this decorator (REQ-0.0.23-05-04 / REQ-0.0.23-05-07).

## `same_commit_backfill/`

A `@covers(REQ-X.Y.Z-NN-MM)` decorator and the REQ's closing receipt were
authored in the **same commit** — the canonical cosmetic-backfill case. The
heuristic MUST flag this decorator and exit 3 under `--strict` or on
heavy / foundation lanes (REQ-0.0.23-05-01 through REQ-0.0.23-05-05).

Each subdirectory carries:

- `git_history.json` — the canned git history each `git_runner` call must
  observe (introducing commit, closing receipt commit, rev-list gap, dates).
- `adr.md` — the ADR shape the heuristic walks.
- `obpi.md` — the OBPI shape with one REQ in the acceptance criteria.
- `test_decorator.py` — the test file holding the `@covers(REQ-...)`
  decorator at a known line number.
