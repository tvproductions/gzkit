# AUDIT — ADR-0.0.23-agent-failure-mode-taxonomy

**Phase:** Audit (Layer 2 — read ledger proof, do not re-litigate Layer-1).
**Outcome:** **FAIL — audit cannot proceed to VALIDATED.** No `validated`
receipt emitted. Surfaced to operator for routing.

## Summary

| Field | Value |
|---|---|
| ADR | ADR-0.0.23-agent-failure-mode-taxonomy |
| Kind / Lane | foundation / lite |
| OBPIs | 5/5 marked Completed in the ledger with attested operator signatures |
| Layer-2 verdict | **FAIL** — `uv run gz adr audit-check ADR-0.0.23` exits 3 with 79 covers-backfill findings (`proofs/audit-check.txt`) |
| Mechanical state | Unittest 3925/3925 PASS (1 skipped); mkdocs build clean; `gz gates --adr ADR-0.0.23` exits 0 |
| Gate 5 attestation | Not emitted — audit FAILed before receipt step |
| Lifecycle | Remains `Pending` (Completed but not Validated) |

## Execution log

| Step | Check | Result | Proof |
|---|---|---|---|
| 1 | Plan scoped (claims, checks, risk focus) | ✓ | `audit/AUDIT_PLAN.md` |
| 2 | Layer-2 ledger proof | ✗ | `proofs/audit-check.txt` (exit 3, 79 findings) |
| 3 | Demonstrate Value | not run | Cannot proceed past Step 2 FAIL per skill doctrine |
| 4 | Document | this file | — |
| 5 | Identify Shortfalls | see § Shortfalls | — |
| 6 | Remediate | not attempted | Operator routing required |
| 7 | Mark VALIDATED | NOT executed | — |
| 8 | Emit Validation Receipt | NOT executed | `audit-begin`/`audit-end` not run; no marker created |
| 9 | Verify Lifecycle Update | NOT executed | — |

## Layer-1 mechanical state

All Layer-1 verification commands pass when run in isolation:

| Command | Exit | Proof |
|---|---|---|
| `uv run -m unittest -q` | 0 (3925 tests, 1 skipped) | `proofs/unittest.txt` |
| `uv run mkdocs build -q` | 0 (clean) | `proofs/mkdocs.txt` |
| `uv run gz gates --adr ADR-0.0.23` | 0 (Gate 1 PASS, Gate 2 PASS) | `proofs/gates.txt` |

The mechanical surface is green. The Layer-2 trust gate is the blocker.

## Layer-2 finding — 79 covers-backfill flags

`gz adr audit-check ADR-0.0.23` exits 3 with the following structured
output (full capture in `proofs/audit-check.txt`):

- **OBPI completion:** PASS — all 5 OBPIs linked in the ledger with
  attested completion.
- **Advisory:** 9 REQs without `@covers` traceability (non-blocking) —
  REQ-0.0.23-01-{01,02,03}, REQ-0.0.23-02-{01,02,03},
  REQ-0.0.23-03-{01,02,03}. These are the rule-mirror OBPIs (01 author
  failure-modes rule, 02 cross-link/scorecard, 03 sync mirrors) whose
  surfaces are documentation rather than test-coverable code.
- **Coverage:** 21/30 REQs covered (70.0%). OBPI-04 = 10/10, OBPI-05 =
  11/11. OBPI-01/02/03 contribute 0/3 each (consistent with the advisory).
- **FAIL — 79 covers-backfill findings (blocking):** every flagged
  finding shows `introduced @ 65c530e (0c / 0d before receipt …)` for
  OBPI-04 entries or `introduced @ db39f7f (0c / 0d before receipt …)`
  for OBPI-05 entries.

### Distribution by REQ (head)

| REQ | Hits |
|---|---|
| REQ-0.0.23-05-01 | 12 |
| REQ-0.0.23-05-03 | 10 |
| REQ-0.0.23-04-04 | 10 |
| REQ-0.0.23-05-05 | 7 |
| REQ-0.0.23-05-07 | 6 |
| REQ-0.0.23-05-02 | 6 |
| REQ-0.0.23-04-06 | 6 |
| REQ-0.0.23-05-06 | 5 |
| REQ-0.0.23-05-04 | 3 |
| REQ-0.0.23-05-{08,10}, 04-08, 03-{01,02,03}, 02-{01,02,03}, 01-{02,03} | 2 each |

### Flagged file footprint

| File | Created at | Lines | Trailer |
|---|---|---|---|
| `tests/commands/test_issue_cmd.py` | `65c530e9` | 350 | `Ceremony: gz-git-sync` |
| `tests/governance/test_audit_check_covers_backfill.py` | `db39f7fe` | 1086 | `Ceremony: gz-git-sync` |

Both files were **created in their entirety** in `Ceremony: gz-git-sync`
commits — the diff for each commit shows `1 file changed, N insertions(+)`
with N matching the file's line count. The `@covers` decorators were
added at the same time as the test file came into existence.

## Shortfalls (surfaced for operator routing)

Three findings worth distinct attention. Each is *characterized*, not
remediated — Layer-2 reads ledger proof and surfaces; it does not
override Layer-1's verdict by re-reading test source and forming a new
verdict (per § Trust Chain).

### Shortfall 1 — Layer-1 audit-check is fail-closed; receipt cannot be emitted

The skill is binding: *"Audit fails → no receipt. Only emit after all
shortfalls are resolved."* `gz adr audit-check` exit 3 is a hard gate
on `gz adr emit-receipt --event validated`. The audit terminates here.

### Shortfall 2 — Heuristic-vs-creation-pattern disambiguation needed

The covers-backfill heuristic detects `@covers` decorators introduced
within a same-commit-window of the closing receipt. The 79 findings all
match this temporal pattern. Two interpretations cannot be distinguished
from Layer-2 evidence alone:

- **(a) The heuristic is correctly detecting cosmetic backfill** —
  decorators added to silence audit-check without re-deriving REQ
  semantics (the GHI #272 anti-pattern, canonized at
  `.gzkit/rules/tests.md` § Invariant 6f).
- **(b) The heuristic is correctly detecting same-commit creation** —
  test files authored as part of OBPI implementation but landed via a
  `Ceremony: gz-git-sync` commit rather than a `Task: TASK-…` commit.
  The decorators were never on pre-existing tests; the tests were born
  with the decorators in the same commit that received the OBPI's
  closing receipt.

Sampled evidence (`tests/commands/test_issue_cmd.py:30-101`) shows
assertions that pin REQ-derived semantics (e.g. `derive_consumer_slug()`
returning the correct slug across SSH, HTTPS, and no-suffix git remote
forms) rather than string output from a prior implementation. **This is
one class out of 79 sites; assertion-shape across the OBPI-05 file
(`tests/governance/test_audit_check_covers_backfill.py`, 1086 lines,
the bulk of the count) was not sampled.** Forming a verdict from the
sampled class would be the same confident-from-thin-evidence shape this
ADR's taxonomy names — and would be Layer-2 over-ruling Layer-1, which
is the trust-chain poisoning shape gzkit doctrine names.

### Shortfall 3 — Self-referential signal worth doctrine-level attention

The OBPI-05 implementation (`src/gzkit/commands/adr_audit_covers_backfill.py`)
is the covers-backfill heuristic itself. Its tests
(`tests/governance/test_audit_check_covers_backfill.py`, 1086 lines)
are flagged BY that heuristic when the heuristic is invoked against
ADR-0.0.23. The heuristic's own implementation tests trigger the
heuristic.

Two possible readings, both operator-relevant:

- The heuristic is correctly catching the authoring pattern of its
  own implementation — in which case OBPI-05's authoring trajectory
  (test file landed via `Ceremony: gz-git-sync` rather than `Task: …`)
  is the canonical instance of what the heuristic is designed to flag,
  and ADR-0.0.23 is *de facto* not Validated until the authoring
  pattern itself is reconciled.
- The heuristic is miscalibrated against same-commit creation — in
  which case the heuristic needs a doctrine refinement to distinguish
  "decorator added to existing test" (cosmetic backfill, GHI #272)
  from "test file created in a sync commit with decorators present
  from line one" (process anomaly, possibly orthogonal failure class).

Either reading routes to operator judgment, not to Layer-2 override.

## What this audit explicitly did NOT do

- **Did not run `audit-begin`/`audit-end`.** No co-presence marker was
  written. The ceremony pair is for receipt emission; FAIL never reaches
  receipt emission.
- **Did not emit a `validated` receipt.** Per skill doctrine (Audit
  fails → no receipt), the agent does not relay an attestation when
  the audit cannot complete.
- **Did not mark the ADR `Status: Validated`.** Lifecycle remains
  `Pending` (Completed but not Validated). `gz adr report ADR-0.0.23`
  will continue to show `Lifecycle: Pending`.
- **Did not perform Step 3 Feature Demonstration.** The skill's
  mandatory Demonstrate Value step requires a passing Layer-2 verdict
  to proceed; capability demonstration without a passing audit would
  conflate verification (mechanical state PASS) with validation
  (Layer-2 trust gate FAIL).
- **Did not re-read Layer-1 verification source for 79 sites.** That
  scope is Layer-1 work; performing it from `/gz-adr-audit` would be
  trust-chain poisoning. Operator routes the disposition.

## Recommended next-actions (operator routing surface)

These are *possible routes*, not pre-empted recommendations:

1. **Doctrine refinement.** A GHI for refining the covers-backfill
   heuristic to distinguish "decorator added to existing test"
   (GHI #272 cosmetic backfill) from "test file created in same
   commit with decorators present from authoring" (process anomaly).
   The OBPI-05 self-referential signal is the canonical case study.
2. **Process review.** A GHI for the authoring pattern of OBPI-04 and
   OBPI-05 — 350 + 1086 lines of test code created in `Ceremony:
   gz-git-sync` commits rather than `Task: TASK-…` commits, and the
   relationship to AGENTS.md TASK-Driven Workflow (binding — GHI #160
   Phase 6) which prescribes `Task:` trailers for src/tests-touching
   commits.
3. **Re-derivation pass.** If the heuristic's verdict is treated as
   correct on the merits (GHI #272 anti-pattern present), 79 sites
   require assertion re-derivation per `.gzkit/rules/tests.md`
   § Invariant 6f. Scope crosses OBPI ceremony triggers; would be
   sequenced as a remediation OBPI under ADR-0.0.23.
4. **Audit re-run after remediation.** After whichever route lands,
   re-run `/gz-adr-audit ADR-0.0.23` from this same Phase 1 plan; if
   audit-check PASSes, proceed to Step 3 Feature Demonstration and
   the validation receipt ceremony.

## Attestation

Audit completed by agent (Claude Opus 4.7, model ID `claude-opus-4-7[1m]`).
No human attestation relayed; FAIL state precluded receipt emission.
Operator: Jeffry Babb. Date: 2026-05-02.

The agent's signature on this AUDIT.md attests only to:

- The Layer-1 mechanical state (unittest, mkdocs, gates) being PASS as
  captured in `proofs/`.
- The Layer-2 audit-check exit-3 verdict being captured in
  `proofs/audit-check.txt`.
- The above shortfalls being surfaced from observed evidence rather
  than from a Layer-2 verdict overriding Layer-1.

It does **not** attest the ADR as Validated; that requires Layer-1
PASS plus operator-relayed Gate 5 attestation, neither of which is
available at this time.
