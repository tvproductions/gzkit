# Review — check-outcome-reporting

A readable account of the run, written for the operator's review before sign-off. It is a view
over `docs/rnd/check-outcome-reporting.md` and holds no authority; where the two disagree, the
record governs.

## The problem

On 2026-11-22 the pre-push hook printed `gz check (pre-push gate)... Passed` for a `gz check`
that never ran: in the drydock the alarm switch skips it and exits 0, and pre-commit hides a
passing hook's output. Three sweeps then found the same thing on every enforcement surface:

- **Reporting a skip or demotion as a pass.** `gz check` draws ✓ beside a step the hangar
  demoted. `gz validate` prints *"All validations passed"* and JSON `valid: true` over demoted
  findings (`--hexagon-tests`: exit 0 over 143 stderr lines; exit 3 at full strength). A
  demoted run writes the "already verified" receipt a later push reuses. The unit tier's
  zero-test refusal, exit 3, is demoted to ✓ in CI, because the marker is committed.
- **Passing without reading what is guarded.** The ledger guard passed when git failed, and the
  authorship guard read config rather than the identity a commit stamps (both fixed this
  session, #1339 and #1340). Behave, `Test (changed)`, `gz test --obpi` and ARB step receipts
  trust exit 0 for zero or all-skipped tests. Validators pass on a missing, corrupt or empty
  input, and a scope's zero findings then count as proof of a SUPPORT REQ at closeout.

The class is old. Fifteen issues were read in full: 8 open, 7 closed. The landscape run named
part of it F2, *"a gate reports green over a state it cannot see"*, and ruled no disposition.
#919 named its shape before this run: *"A two-valued verdict over a three-valued world:
`caught` / `did not catch` / `could not observe`."*

## The model

**One class, one outcome contract** (ruled). A check's outcome has two kinds of state:

- **subject-state** — what it found about what it guards: *passed*, *failed*;
- **run-state** — what happened to the check: *not run*, *demoted*, *not observed*.

The defect is a run-state reported in the vocabulary of a subject-state, as a pass or, in
#919's case, as a FAIL. `tests.md` already binds this split for the mutation sweep (*"`killed`
and `survived` are claims about the guard, `invalid` and `inconclusive` about the run"*).
Nothing bound it for every check.

**A run-state grounds at the check's own level** (ruled). Outside the hangar, an ERROR check
that could not observe blocks. Inside it, the hangar demotes it like any finding, and the report
reads *demoted*, never ✓. One rule in every mode, so there is no safe-mode exception. This
answers #919's open ruling.

## The names

| Name | Status | Source |
|---|---|---|
| one class, one outcome contract | ruled | operator, *"One class, one contract (Rec.)"* |
| subject-state / run-state | sourced, coined here | `tests.md` *"claims about the guard … about the run"*; #919 *"the thing under test is wrong" / "I could not test the thing"* |
| passed, failed | sourced | the existing report vocabulary |
| not run, demoted, not observed | sourced, provisional | *demoted* from `mx-mode.md`; *not observed* from #919's *"could not observe"*; *not run* from the alarm switch's *"is off until gz mx exit"*. The final names wait on the row-7 research. |
| *skip* and *inconclusive* for the whole family | rejected | each names one member, and `tests.md` uses *inconclusive* for one |

## What each row produces

1. **Change order on RP-13: commissioned (proposed).** The drydock's scope is frozen, so this is
   no new order. The class blocks return to service, because a sea trial read through
   false-green reports proves nothing. RP-13 owns it: the outcome contract joins its
   foundation tranche beside the MEL model and the place-of-call reader, every surface is
   retrofitted with the controls, and the rule clause lands there with its witness. The class's
   open members attach to it. You issue the change order; this run issues nothing.
2. **GHIs: commissioned, awaiting your go.**
   - Three new GHIs through `ghi-author`, one per mechanism:
     - a run-state rendered as a pass;
     - a vacuous population or proxy passing a validator;
     - the pre-push range: first ref only, the index rather than the pushed tree, deletion-only and empty commits skipping hooks, and authorship judged on config.
   - Evidence comments on #1154 and #1224, and a comment on #919 giving its answer.
3. **Chore: not pursued.** RP-13's shrink-only baseline is the planned witness.
4. **Rule text: not pursued here.** Your ruling: no text until RP-13 lands it with its witness.
5. **Refactoring: not pursued.** It is the retrofit row 1 carries.
6. **No action: recorded.** The MX rulings stand: the committed marker, and CI's full-strength
   run reporting without failing. Under the contract, CI's demotions read *demoted*, not ✓.
7. **Further research: commissioned.** The outcome vocabularies of JUnit XML, TAP and SARIF, and
   whether each is held to a standard. You open it when RP-13's change order is planned.

## What this does not license

No order, package, GHI or rule is created by the run itself. Row 1 waits for your change
order, and row 2 waits for your go on that row. #1339 and #1340 were fixed before the run
opened, on your direct ruling.
