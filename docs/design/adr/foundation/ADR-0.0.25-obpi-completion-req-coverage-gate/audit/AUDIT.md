# AUDIT — ADR-0.0.25-obpi-completion-req-coverage-gate

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.25-obpi-completion-req-coverage-gate |
| ADR Title | OBPI Completion REQ-Coverage Gate |
| Kind / Lane | foundation / heavy |
| ADR Dir | `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/` |
| Audit Date | 2026-05-03 |
| Auditor | main-session (agent-relayed; operator attests) |

## Feature Demonstration (Step 3)

ADR-0.0.25 redefines what `Completed` means at OBPI brief level: a brief is
completable iff every REQ in its `## Acceptance Criteria` section has at
least one passing `@covers`-decorated test, or an explicit ledger-recorded
operator waiver. The gate is mirrored at ADR closure
(`gz adr emit-receipt --event closed`). Three capabilities to demonstrate:

### Capability 1 — Pre-emission REQ-coverage gate at OBPI completion

Trust check: the agent-facing audit-check surface confirms 15/15 REQs are
covered for ADR-0.0.25 itself (the gate is dogfooded on its own delivery).

```bash
$ uv run gz adr audit-check ADR-0.0.25
ADR audit-check: ADR-0.0.25-obpi-completion-req-coverage-gate
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.25-01-implement-coverage-gate
  - OBPI-0.0.25-02-override-and-mirror
  - OBPI-0.0.25-03-bdd-and-doc

Coverage: 15/15 REQs covered (100.0%)
  OBPI-0.0.25-01: 6/6 (100.0%)
  OBPI-0.0.25-02: 5/5 (100.0%)
  OBPI-0.0.25-03: 4/4 (100.0%)
```

The gate's mechanical correctness is exercised by the scoped REQ-coverage
test suite (25 tests, 0 failures):

```text
Ran 25 tests in 0.062s
OK
```

(Full proof: `audit/proofs/scoped-tests.txt`.)

**Why it matters:** Closes the "completed-with-uncovered-REQs" vector at
brief layer rather than catching it post-attestation in `gz adr audit-check`.
The `Malformed REQ line (skipped)` warning visible in the test output is the
parser's documented tolerance for non-canonical checklist items
(REQ-0.0.25-01-06 in the ADR's Decision §1).

### Capability 2 — Operator override path with ledger event recording

The `--accept-uncovered` and `--accept-uncovered-reason` flags surface on
the live CLI with the documented 1:1 pairing requirement:

```bash
$ uv run gz obpi complete --help | grep -A1 'accept-uncovered'
  --accept-uncovered REQ_ID
                        Waive an uncovered REQ (repeatable). Requires
                        --accept-uncovered-reason.
  --accept-uncovered-reason REASON
                        Rationale for --accept-uncovered (repeatable, 1:1
                        positional pairing).
```

The override path has been exercised in production: 4 canonical
`obpi_completion_uncovered_accept` events exist in the ledger, each
naming operator + REQ-ID + rationale + acceptance type:

```text
{"event":"obpi_completion_uncovered_accept","id":"OBPI-0.0.25-03-bdd-and-doc",
 "ts":"2026-05-03T07:12:47.301204+00:00",
 "obpi_id":"OBPI-0.0.25-03-bdd-and-doc","req_id":"REQ-0.0.25-03-01",
 "operator":"g0",
 "rationale":"Covered by @REQ-0.0.25-03-01 BDD scenario tag …",
 "acceptance_type":"agent-relayed-operator-attestation"}
```

(Full proof: `audit/proofs/uncovered-accept-ledger.jsonl`.)

**Why it matters:** Operator override remains available, but each waiver is
now ledger-visible and operator-attributed — no silent skipping. The
`acceptance_type` field records whether the waiver came through PTY+`ACCEPT`
confirmation or the GHI #292 agent-relayed branch, preserving the GHI #290
anti-fabrication guarantee at the override surface as well.

### Capability 3 — ADR-close mirror gate

`gz adr emit-receipt --event closed` exposes the closure event in the
parser enum, and the mirror logic refuses ADR closure while any linked
OBPI carries an unwaived REQ gap:

```bash
$ uv run gz adr emit-receipt --help | head -3
usage: gz adr emit-receipt [-h] --event {completed,validated,closed}
                           --attestor ATTESTOR ...
```

The mirror's enforcement path is `_check_adr_obpi_coverage_gaps` at
`src/gzkit/commands/adr_audit.py:927`, asserted by 6 wiring tests in
`tests/commands/test_adr_emit_receipt_coverage_gate.py`.

**Why it matters:** A brief that legitimately waives a gap at completion
time still surfaces in the ADR-close gate's view, so an ADR cannot quietly
close while an unwaived gap remains anywhere in its OBPI chain. Bridge
between brief-level Gate 5 (per-OBPI attestation) and ADR-level Gate 5
(closeout attestation).

### Value Summary

Operators can now trust that a brief's `Completed` status implies REQ-
specific test coverage, not just a globally-passing test suite. When
genuine REQ-coverage gaps exist (broader REQ language than any single
test legitimately covers), the operator chooses between expanding the
test or recording a ledger-visible waiver — the silent-completion path
is closed. The ADR-close mirror prevents the same gap from re-opening
at the parent ADR's closeout.

---

## Execution Log

| # | Check | Command | Result | Notes / Proof |
|---|-------|---------|--------|---------------|
| 1 | Ledger proof exists | `uv run gz adr audit-check ADR-0.0.25` | ✓ | `audit/proofs/audit-check.txt` — PASS, 15/15 REQs covered |
| 2 | Lifecycle pre-state | `uv run gz adr report ADR-0.0.25` | ✓ | `audit/proofs/adr-report-pre.txt` — Lifecycle = Completed, Closeout = attested |
| 3 | Scoped REQ-coverage tests | `uv run -m unittest -q tests.commands.test_obpi_complete_coverage_gate tests.commands.test_adr_emit_receipt_coverage_gate tests.governance.test_req_coverage` | ✓ | `audit/proofs/scoped-tests.txt` — 25 tests, 0 failures |
| 4 | CLI surface exposes override | `uv run gz obpi complete --help` | ✓ | `audit/proofs/obpi-complete-help.txt` — `--accept-uncovered` + `--accept-uncovered-reason` present with 1:1 pairing language |
| 5 | ADR-close mirror surface | `uv run gz adr emit-receipt --help` | ✓ | `audit/proofs/adr-emit-receipt-help.txt` — `closed` enum value present |
| 6 | BDD scenarios | `uv run -m behave features/obpi_completion_coverage_gate.feature` | ✓ | `audit/proofs/bdd.txt` — 15 scenarios, 79 steps, all passed |
| 7 | Docs build | `uv run mkdocs build -q` | ✓ | `audit/proofs/mkdocs.txt` — clean (no output) |
| 8 | Governance CLI audit | `uv run gz cli audit` | ✓ | `audit/proofs/cli-audit.txt` — CLI cross-coverage 90/90 fully covered |
| 9 | Override-event ledger presence | `grep '"event":"obpi_completion_uncovered_accept"' .gzkit/ledger.jsonl` | ✓ | `audit/proofs/uncovered-accept-ledger.jsonl` — 4 canonical events |

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 3 OBPIs `attested_completed`; ledger 15/15 REQs covered |
| Data Integrity | ✓ Override-path ledger events well-formed (operator + REQ-ID + rationale + acceptance_type) |
| Surface Stability | ✓ Both CLI surfaces (`gz obpi complete`, `gz adr emit-receipt`) expose new flags / enum values cleanly |
| Documentation Alignment | ✓ AGENTS.md § OBPI Acceptance Protocol names ADR-0.0.25 REQ-coverage gate; runbook references `--accept-uncovered` flag |
| Risk Items Resolved | ✓ All planned-checks risks (override corruption, mirror drift, doc drift) closed with proofs |

## Evidence Index

- `audit/proofs/audit-check.txt`
- `audit/proofs/adr-report-pre.txt`
- `audit/proofs/scoped-tests.txt`
- `audit/proofs/obpi-complete-help.txt`
- `audit/proofs/adr-emit-receipt-help.txt`
- `audit/proofs/bdd.txt`
- `audit/proofs/mkdocs.txt`
- `audit/proofs/cli-audit.txt`
- `audit/proofs/uncovered-accept-ledger.jsonl`

(Lifecycle-post proof `audit/proofs/adr-report-post.txt` will be appended
after Step 8 emits the `validated` receipt.)

## Recommendations

No blocking issues found. Two informational notes:

- **Note 1.** The scoped-test output includes one expected `Malformed REQ
  line (skipped)` warning. This is the parser's documented tolerance branch
  (REQ-0.0.25-01-06: "REQ-ID parsing tolerates the canonical brief shape
  and skips non-REQ checklist items"), exercised by a fixture, not a
  defect.
- **Note 2.** The 5 ledger lines initially matched by a loose `grep
  obpi_completion_uncovered_accept` pattern include 1 OBPI completion
  receipt whose narrative *describes* the override mechanism plus 4
  canonical `obpi_completion_uncovered_accept` events. The captured proof
  file uses the precise `"event":"obpi_completion_uncovered_accept"`
  filter; the count of 4 matches the SessionStart orientation summary.

## Attestation

Agent attests that the ADR's claims are reproducible against the
captured proofs and the gate is observably working on the live CLI.
Operator's verbal `accept audit` ack will be relayed into the ledger
receipt via the `gz adr audit-begin` / `gz adr emit-receipt --event
validated` / `gz adr audit-end` ceremony.

Signed: main-session (agent), 2026-05-03.
