# ADR-0.0.69 Audit — Channels-First Closeout Proof

**Phase:** 2 (COMPLETED → VALIDATED)
**Date:** 2026-06-11
**Driver persona:** `pipeline-orchestrator`
**Lane:** heavy · **Kind:** foundation (0.0.69)
**Independent verification:** `spec-reviewer` + `quality-reviewer` (fresh-context subagents)

---

## Feature Demonstration (Step 3 — mandatory)

ADR-0.0.69 delivers a **channels-first closeout proof**: closeout proof is recomputed
from the live three-channel REQ-kind evidence surface every run, never read from a stored,
drift-prone artifact. The `ln:` closeout-proof-binding surface is retired entirely.

### What the operator can do now that they could not before

| Capability | Command | Observed result | Why it matters |
|---|---|---|---|
| Recompute per-REQ closeout proof from live evidence | `uv run gz validate --closeout-proof` | `✓ All validations passed (1 scopes)` (exit 0) | Proof is derived, not stored — a broken channel can never hide behind a stale block |
| Machine-readable form for CI | `uv run gz validate --closeout-proof --json` | `{"valid": true, "errors": []}` | Wired into the `gz check` default set (`commands/quality.py:329`) |
| SUPPORT channel is load-bearing | `req_kind.py::resolve_support_proof` | real ledger query + cited-validator dispatch; fail-close on missing event / non-zero exit | Closes #543 — no more hardcoded `"advisory-support"` |
| STRUCTURAL-FENCE channel is load-bearing | `req_kind.py::resolve_fence_proof` | asserts a real parent-ADR `## Boundary Invariants` anchor; `"unproven-fence"` when absent | Closes #538 — no more `"grandfathered"` pass-through |
| `ln:` surface gone | `uv run gz validate --closeout-proof-binding` | `error: unrecognized arguments` (flag retired) | 0 `ln:` blocks remain in `docs/design/adr`; `closeout_proof_binding.py` deleted |

Full captured output: [`proofs/value-demonstration.txt`](proofs/value-demonstration.txt).

---

## Step 2 — Ledger Proof (Layer-2 trust)

`uv run gz adr audit-check ADR-0.0.69` → **PASS** — all four linked OBPIs completed with
evidence (`attested_completed` in ledger). Coverage 14/21 REQs via `@covers`; the 7
uncovered REQs are the **5 SUPPORT + 2 STRUCTURAL-FENCE** set, which prove through
ledger/validator and Boundary-Invariants anchors respectively (advisory, non-blocking by
design — ADR-0.0.59 req-kind discipline). No BEHAVIOR REQ is uncovered.

| OBPI | State | Claim verified in code |
|---|---|---|
| 0.0.69-01 SUPPORT channel | attested_completed | `resolve_support_proof` (`req_kind.py:222-245`) queries ledger + dispatches validator |
| 0.0.69-02 FENCE channel | attested_completed | `resolve_fence_proof` (`req_kind.py:88-104`) asserts `## Boundary Invariants` anchor |
| 0.0.69-03 derived view | attested_completed | `governance/trust_audits/closeout_proof.py` recomputes live; writes nothing to disk |
| 0.0.69-04 `ln:` retirement | attested_completed | binding module/flag/schema/19+ brief blocks all gone |

---

## Independent Verification Verdicts

### spec-reviewer → **VALIDATED-READY**

All four OBPIs' central claims hold against a fresh source read. Each of the 7 uncovered
REQs adjudicated by kind (5 SUPPORT, 2 FENCE) — all legitimately non-blocking; no BEHAVIOR
REQ uncovered. SUPPORT/FENCE arms confirmed load-bearing (not `advisory-support` /
`grandfathered`); `ln:` surface confirmed fully removed; all three Boundary Invariants
carry real anchors citing real REQ IDs.

### quality-reviewer → **COHERENT**

The four OBPIs cohere into the single claimed capability. All three Boundary Invariants
hold (FENCE load-bearing; view never persisted; ADR-0.0.68 session-green gate untouched —
swap localized to `closeout_ceremony.py:261-282` on the EXECUTE→ATTESTATION edge). The two
channels the ADR exists to fix (SUPPORT, FENCE) share one proof model with no divergence.

---

## Step 5 — Shortfalls (all NON-BLOCKING; recorded on the Validated transition)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| F1 | BEHAVIOR proof is computed twice by divergent implementations — the closeout view's regex `@covers` scan (`closeout_proof.py:60-73`) vs `--req-kind-discipline`'s AST-parsed `CoverageReport` (`req_kind.py:405-406`). BEHAVIOR was never the masked channel, so no proof gap; it is a maintenance seam. | non-blocking | **Routed to GHI #573** (existing "DRY classifier fork" home) as a new-instance of the same class — avoids a sibling-cut duplicate per `/ghi-author` Step-0. Post-1.0 reduction-pass candidate (prove redundancy before culling). |
| F2 | Output-shape / exit-code drift from ADR §Decision item 3: code returns `list[ValidationError]` (exit 0/3) rather than a frozen `CloseoutProofReport` table + exit-2-on-I/O. Docstring (`closeout_proof.py:6-9`) overstated an unreachable exit-2 path. The realized shape is arguably *more* BI-2-aligned (no report object to persist). | cosmetic-to-minor | **Resolved in this audit commit** — module docstring corrected; output-shape reconcile recorded in ADR §Post-Validation Notes. |
| F3 | 24h active-closeout freshness window (`closeout_proof.py:111-126`) narrows the `gz check` **sweep** path so parked ceremonies (e.g. ADR-0.0.41) don't redden `main`. Operator-ruled 2026-06-10, recorded in the campaign (A.2) and OBPI-03 attestation, but the ADR §Intent prose ("recomputes … every run") was not updated. The explicit-`adr_id` ceremony-gate path always enforces unconditionally, so the real EXECUTE→ATTESTATION gate is **not** weakened. | non-blocking | **Resolved in this audit commit** — canon-precision note added to ADR §Post-Validation Notes. |

None of F1–F3 blocks the COMPLETED → VALIDATED transition. All are disclosed here so the
drift is tracked rather than silent (DO IT RIGHT — flag, never excuse).

---

## Summary Table

| Dimension | Outcome |
|---|---|
| Completeness (all OBPIs shipped w/ evidence) | ✓ 4/4 attested_completed |
| Integrity (ledger proof complete) | ✓ audit-check PASS |
| Alignment (code = docs = tests) | ✓ (3 non-blocking drifts disclosed: F1–F3) |
| Value demonstrated (feature shown working) | ✓ `--closeout-proof` green; retirement proven |
| Boundary Invariants hold | ✓ 3/3 |
| Independent verification | ✓ spec-reviewer + quality-reviewer both GREEN |

## Attestation

Agent (driver) signs this audit: evidence verified, value demonstrated, two independent
reviewers GREEN, three non-blocking shortfalls disclosed and routed. Human attested at each
OBPI completion (`attested_completed`). **Awaiting operator audit acceptance** (`accept
audit` / `verify audit`) to emit the `validated` Gate-5 receipt.
