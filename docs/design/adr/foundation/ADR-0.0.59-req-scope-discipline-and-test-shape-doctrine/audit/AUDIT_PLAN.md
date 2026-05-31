# ADR-0.0.59 Audit Plan

**ADR:** ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
**Kind / Lane:** foundation / heavy
**Lifecycle (pre-audit):** Completed (closeout attested 2026-05-27 by g0)
**Auditor:** main-session (driver: `pipeline-orchestrator`)
**Audit date:** 2026-05-27

## Scope

Audit the ADR-0.0.59 package as an integrated whole: do the 5 OBPIs cohere
into the claimed capability — a three-kind REQ taxonomy (BEHAVIOR / SUPPORT /
STRUCTURAL-FENCE) keyed to three distinct proof channels, mechanically
enforced at brief-authoring time, at the parity gate, and via a re-runnable
decommissioning chore for the existing rot.

The closeout ceremony already attested OBPI-level completion. This audit
moves the ADR from COMPLETED → VALIDATED by verifying ledger proof and
demonstrating the integrated capability working at the operator surface.

## Trust model

Layer 2 audit per the `gz-adr-audit` skill: `gz adr audit-check ADR-0.0.59`
returns PASS for all 5 OBPIs, each with `attested_completed` runtime state,
human attestation present, key proof recorded. No re-verification needed.

## Claims extracted from ADR prose

| Claim | Surface | Verification |
|---|---|---|
| C1: Three-kind REQ taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL-FENCE) is the canonical doctrine | `.gzkit/rules/tests.md` § REQ Scope Discipline; `docs/governance/req-scope-discipline.md` | doctrine-headings.txt — both files present with the three kinds named |
| C2: Each kind has exactly one proof channel | `src/gzkit/req_kind.py` (ReqKind/ProofChannel/ReqClassification frozen Pydantic models) | artifact-inventory.txt + covers-three-channel-output.json fields |
| C3: Brief-time validator fail-closes on missing kind tags / channel-citation gaps | `gz validate --req-kind-discipline` | validate-req-kind-discipline.txt — PASS, 1 scope |
| C4: Parity gate consumes three channels with per-kind resolution | `gz covers OBPI --json` per-REQ `taxonomy_kind` / `proof_channel` / `proof_status` / `ledger_event_ids` / `parent_adr_anchor` fields | covers-three-channel-output.json — all five fields present on every entry |
| C5: Re-runnable decommissioning chore registered | `gz chores list` (slug `decommission-tautological-tests`, lane heavy, ADR-0.0.59-04) | chores-list.txt |
| C6: Drift gate fail-closes on growth above baseline + waivers | `gz validate --tautological-test-audit` against `data/tautological_test_baseline.json` (765 ops baseline) + `data/tautological_test_waivers.json` | validate-tautological-test-audit.txt — PASS, 1 scope; baseline-count.txt — 765 ops |
| C7: Grandfathering cache for legacy briefs | `data/req_kind_grandfathering.json` | artifact-inventory.txt |
| C8: All 5 OBPIs ledger-completed with human attestation | `gz adr audit-check ADR-0.0.59` | adr-audit-check.txt — PASS, 5/5 attested_completed |
| C9: 17 uncovered REQs are advisory (SUPPORT/STRUCTURAL-FENCE kinds use non-`@covers` channels) | adr audit-check output | adr-audit-check.txt — "Advisory 17 REQ(s)... (non-blocking)" |

## Persona dispatch

Per the `gz-adr-audit` skill's read-only-judgment safeguard: a single driver
scoring its own findings is the optimistic-bias failure mode. Independent
subagents produce evidence the driver synthesizes:

- `spec-reviewer` — independent requirement-tracing for each OBPI's REQ
  coverage against fresh reads of brief + tests
- `quality-reviewer` — structural-coherence assessment: do the 5 OBPIs
  integrate into the claimed ADR-level capability, or is the integration
  brittle?
- `narrator` — composes the Step 3 Value Demonstration in operator-value
  terms

## Steps

1. ✓ Plan authored (this document).
2. Verify ledger proof (already PASS — see adr-audit-check.txt) + dispatch
   spec-reviewer for independent REQ-coverage tracing.
3. Structural coherence review (quality-reviewer) before value demonstration.
4. Demonstrate value (narrator frames the integrated capability working).
5. Document findings in AUDIT.md.
6. Identify shortfalls; remediate or file follow-up GHIs.
7. Mark VALIDATED; emit validation receipt via `audit-begin` / `audit-end`.
8. Verify lifecycle update (`gz adr report ADR-0.0.59` shows Validated).

## Risk focus

- **Integration brittleness** — the parity gate (OBPI-03) is load-bearing;
  bugs in three-channel resolution would silently let uncovered REQs pass.
  Adversarial test discipline named in ADR Negative #6.
- **Closed-set discipline** — the three-kind taxonomy is a one-way door
  (frozen StrEnum). A fourth kind requires amendment ADR ceremony, not
  in-place edit. Audit verifies the closed-set is enforced.
- **Long-tail rot** — drift gate prevents new rot; existing ~3,400
  filesystem-shaped operations are not all decommissioned (OBPI-05 only
  processed top-5 of tests/governance/). Audit verifies this is acknowledged
  not papered over.

## Post-validation follow-up

On 2026-05-31, GHI #571 extended this audit with a unit-testing doctrine
deep dive. The durable follow-up artifact is
[`FOLLOW_UP_UNIT_TESTING_DOCTRINE_2026-05-31.md`](FOLLOW_UP_UNIT_TESTING_DOCTRINE_2026-05-31.md).
It is scoped as recurrence defense for ADR-0.0.59, not a competing design:
control-surface wording, stale skill evidence tables, completion-layer
`@covers` pressure, scanner inventory, and output/render assertion triage.
