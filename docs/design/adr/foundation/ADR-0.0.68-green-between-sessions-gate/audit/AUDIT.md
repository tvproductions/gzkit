# AUDIT (Gate-5) — ADR-0.0.68

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.68 |
| ADR Title | Green-Between-Sessions Gate |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.68-green-between-sessions-gate |
| Audit Date | 2026-06-09 |
| Auditor(s) | agent (pipeline-orchestrator persona); operator g0 (attestor) |

## Feature Demonstration

For eight sessions, coupled-surface red traveled silently across session boundaries and surfaced only at closeout as archaeology (operator named it V.I.B.E.S.). ADR-0.0.68 is the structural exit: red is caught at push, the same session it was introduced. The three capabilities below show the floor declaring itself green, failing closed on every red path, and enforcing its own presence.

### Capability 1 — The green-gate declaration validates fail-closed

```console
$ uv run gz validate --session-green-gate
Validated: session_green_gate

✓ All validations passed (1 scopes).
(exit 0)
```

**Why it matters:** The operator gets a single, fast, exit-coded answer to "is the green-between-sessions gate actually wired?" — no reading config by eye, no trusting that a hook exists. Green here means the pre-push `gz check` floor is declared and will run.

### Capability 2 — Every red path fails closed, not open

```text
missing config                             -> FAIL-CLOSED (Missing .pre-commit-config.yaml — no pre-push gz check hook declared...)
unparseable yaml                           -> FAIL-CLOSED (Unparseable .pre-commit-config.yaml — treated as violation (fail-closed)...)
no pre-push hook                           -> FAIL-CLOSED (No stages: [pre-push] hook running 'gz check' declared...)
wrong verb (gz check-config-paths)         -> FAIL-CLOSED (No stages: [pre-push] hook running 'gz check' declared...)
GREEN: pre-push gz check declared          -> pass        (no errors)
```

*(audit/proofs/red-path-library.txt — exercised against temp-dir fixtures)*

**Why it matters:** The four ways the gate could be silently absent — no config, corrupt config, a hook on the wrong stage, or a look-alike verb (`gz check-config-paths` instead of `gz check`) — all fail closed. The operator can trust that "validator green" cannot mean "gate quietly missing." Absence is indistinguishable from presence is exactly the V.I.B.E.S. failure this closes.

### Capability 3 — The floor enforces its own presence (self-referential wiring)

```console
$ python: _build_check_steps() -> steps: 27, 'Session green gate' present: True
$ uv run gz check -> exit 0, "✓ All checks passed." (27 steps incl. ✓ Session green gate)
```

The declaration lives at `.pre-commit-config.yaml:88-93` (`id: gz-check-pre-push`, `stages: [pre-push]`, `entry: uv run gz check`) — verified present in the working tree.

**Why it matters:** `gz check` includes the session-green-gate validator as one of its 27 steps, and that validator asserts the pre-push `gz check` hook exists. Deleting the declaration turns the *next* `gz check` red. The gate cannot be removed without the gate catching its own removal — there is no quiet uninstall.

### Value Summary

Before ADR-0.0.68, coupled-surface red could cross a session boundary undetected and resurface as a closeout archaeology dig — the operator paying, sessions later, for red introduced and forgotten. Now red is caught at push, in the session that introduced it: the pre-push `gz check` floor fails closed on every way it could be absent and enforces its own presence. Every future closeout becomes routine attestation instead of an excavation. Honest scope: the floor makes red *un-persistable-undetected*, not *push-impossible-while-red* — `git push --no-verify` remains the documented 2am escape hatch, but the next `gz check` catches anything slipped past it.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Ledger proof complete | `uv run gz adr audit-check ADR-0.0.68` | ✓ | PASS exit 0 (proofs/audit-check.txt). Initially exit 3 on a covers-backfill false positive — remediated, see Recommendations |
| Green path | `uv run gz validate --session-green-gate` | ✓ | exit 0 (proofs/green-path.txt) |
| Red path fail-close | `audit_session_green_gate(tmp)` × 5 fixtures | ✓ | 4/4 red paths FAIL-CLOSED, green fixture passes (proofs/red-path-library.txt) |
| Self-referential wiring | `_build_check_steps()` + live `uv run gz check` | ✓ | 27 steps, "Session green gate" present; gz check exit 0 (proofs/wiring-and-declaration.txt, proofs/gz-check.txt) |
| Pre-push declaration | `.pre-commit-config.yaml` inspection | ✓ | lines 88–93, `stages: [pre-push]`, `entry: uv run gz check` |
| Boundary Invariant REQ-0.0.68-02-04 | code read (driver + both reviewers) | ✓ | No hardcoded validator list anywhere in the gate chain — pure `gz check` delegation |
| Docs build | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | ✓ | exit 0, receipt `arb-step-mkdocs-fea7e27ecb134429ae79b25c547300f1` |
| CLI doc coverage | `uv run gz cli audit` | ✓ | exit 0 (proofs/cli-audit.txt) |
| Unit suite | `uv run gz arb step --name unittest -- uv run -m unittest -q` | ✓ | Ran 5997 tests, OK; receipt `arb-step-unittest-8e08a061a1bb4206958a3d1d7368a820` |
| Lint / typecheck | `uv run gz arb ruff` / `uv run gz arb typecheck` | ✓ | receipts `arb-ruff-daa9023bf8594199a9b5243d4abe12db`, `arb-step-typecheck-3907ff1d59c844f79562bd181ae59b52` |
| Independent spec review | spec-reviewer persona subagent | ✓ | SPEC-REVIEW: PASS, 6/6 REQs (proofs/persona-dispatch-verdicts.md) |
| Independent quality review | quality-reviewer persona subagent | ✓ | QUALITY-REVIEW: COHERENT; 1 minor defect remediated in-ceremony (proofs/persona-dispatch-verdicts.md) |

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ — 2/2 OBPIs attested_completed; 6/6 REQs trace to proof channels |
| Data Integrity | ✓ — ledger proof PASS; ARB receipts resolve |
| Performance Stability | ✓ — full `gz check` (27 steps) green; suite 5997 OK in ~71s |
| Documentation Alignment | ✓ — manpage exit-3 contract, runbook install step, mkdocs --strict, cli audit |
| Risk Items Resolved | ✓ — 2 in-ceremony defects direct-fixed (see Recommendations); residual risks documented in ADR § Consequences |

## Evidence Index

- audit/proofs/audit-check.txt — ledger proof (PASS exit 0)
- audit/proofs/green-path.txt — validator green path (exit 0)
- audit/proofs/red-path-library.txt — 4 fail-closed red paths + green fixture
- audit/proofs/wiring-and-declaration.txt — check-steps enumeration + pre-push declaration
- audit/proofs/gz-check.txt — full live `gz check` run (exit 0)
- audit/proofs/cli-audit.txt — CLI doc coverage (exit 0)
- audit/proofs/persona-dispatch-verdicts.md — spec-reviewer PASS + quality-reviewer COHERENT
- ARB receipts: `arb-step-unittest-8e08a061a1bb4206958a3d1d7368a820` (5997 OK), `arb-ruff-daa9023bf8594199a9b5243d4abe12db`, `arb-step-typecheck-3907ff1d59c844f79562bd181ae59b52`, `arb-step-mkdocs-fea7e27ecb134429ae79b25c547300f1`

## Recommendations

- **Issue 1 (remediated):** `gz adr audit-check` flagged a blocking covers-backfill finding — diagnosed as a validator false positive (`git log -L` vs `git blame` cross-attribute content-identical `@covers` lines after the GHI #600 fix inserted a twin decorator block).
  - **Remedy applied:** direct fix `5b2a71ed` — blame re-anchor in `adr_audit_covers_backfill.py`, RED→GREEN with 4 new tests; GHI #272/#309 protections preserved; audit-check re-run PASS exit 0.
- **Issue 2 (remediated):** quality-reviewer Finding 4 — local identity `covers` shadow in `tests/test_session_green_gate_validator.py` discarded the import-time REQ-existence guard.
  - **Remedy applied:** direct fix `423701ea` — canonical `gzkit.traceability.covers` import; module 7/7 OK.
- **Tracked (out of scope):** typecheck gate scopes `src` only (blind to `tests/`); 5 ty errors in `gz-foundation-triage/scripts/triage.py` — logged in `.gzkit/insights/agent-insights.jsonl` (2026-06-09 discovery record) for next-session routing.
- No blocking issues remain.

## Attestation

Agent attests the evidence above is reproducible and complete; ledger proof verified; value demonstrated live; no blocking discrepancies remain. Human attestation recorded via the audit-begin/audit-end ceremony: operator's verbal audit acceptance relayed to `gz adr emit-receipt ADR-0.0.68 --event validated` (attestation_text carries the operator's verbatim words).

Signed: agent (pipeline-orchestrator), 2026-06-09 — operator receipt: see ledger `validated` event for ADR-0.0.68.
