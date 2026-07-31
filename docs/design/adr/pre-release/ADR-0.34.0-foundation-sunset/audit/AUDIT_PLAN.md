# AUDIT PLAN — ADR-0.34.0-foundation-sunset

**Date:** 2026-07-31
**Transition:** COMPLETED → VALIDATED
**Lane:** heavy · **Kind:** feature (0.34.0)
**Driver persona:** `pipeline-orchestrator`

## Scope

ADR-0.34.0 seals the `foundation` ADR kind: closed to new authoring at every
door, while remaining a valid schema value so the 51 grandfathered ADRs on disk
keep validating. The historical set is partitioned from Layer-2 ledger truth
(never frontmatter) into 51 frozen-historic and 23 demoted-to-pool.

Five OBPIs, all `attested_completed` by `g0` between 2026-07-19 and 2026-07-31.
Closeout ceremony completed 2026-07-31; release v0.34.0 published.

## Claims extracted from the ADR

| # | Claim | Check |
|---|-------|-------|
| C1 | The foundation kind is closed to new authoring at every door | Refusal probes at each authoring ingress + fidelity assertion 1 |
| C2 | The kind remains a valid schema value; grandfathered ADRs still validate | `gz validate --documents` exit 0 over the 51-entry roster |
| C3 | Every on-disk foundation ADR is grandfathered or demoted; none in limbo | `gz validate --taxonomy` exit 0 + fidelity assertion 2 |
| C4 | The partition is computed from Layer-2 ledger truth, never frontmatter | Read the partition source; confirm `foundation_grandfathered` events are the input |
| C5 | The gate is permanent and self-maintaining, with no staging flag | `--taxonomy` present in `gz check` aggregate; no flag gating it |
| C6 | The 23-node demotion preserved lineage and left no orphans | `gz ontology resense` node/edge delta; parked-child accounting |

## Checks

| Check | Command | Layer | Proof |
|-------|---------|-------|-------|
| Ledger proof complete | `gz adr audit-check ADR-0.34.0` | L2 | `proofs/audit-check.txt` |
| Bound fidelity gate | `gz adr fidelity ADR-0.34.0` | L1 | `proofs/fidelity.txt` |
| CLI/doc coverage | `gz cli audit` | L1 | `proofs/cli-audit.txt` |
| Config-path coherence | `gz check-config-paths` | L1 | `proofs/config-paths.txt` |
| Unit suite | `gz arb step --name unittest` | L1 | receipt (closeout) |
| BDD suite | `uv run behave features` | L1 | closeout evidence |
| Docs build | `gz arb step --name mkdocs` | L1 | receipt (closeout) |

## Risk focus

The audit's attention is deliberately weighted toward **claim C1**, because it
is the claim most likely to be over-stated and least likely to be caught by a
green test run:

1. **Enforcement claims fail silently in the positive direction.** An all-green
   suite is what you observe both when a closure works and when it was never
   built. The closeout walkthrough surfaced zero refusal demos (now GHI #738),
   so C1's evidence had to be constructed by hand during the ceremony.
2. **Guard placement is the known weak seam.** GHI #734 (OPEN) reports the
   membrane was seated at *call sites* rather than at the shared writer
   `register_adr_in_ledger`, with a reproduced probe booking a prohibited ADR.
   The audit must state where C1 actually holds and where it does not, rather
   than inheriting OBPI-05's "both ingresses" phrasing.

Secondary focus: **C4**, the Layer-2-not-frontmatter partition source, since
frontmatter was disqualified precisely because the ADR-0.0.37 investigation
proved it can lie.

## Independent review dispatched

Per skill § Persona Dispatch — the driver ran this ADR's closeout ceremony and
therefore carries a positive prior; a driver scoring its own findings is the
`optimistic-bias` failure mode.

| Persona | Charge |
|---------|--------|
| `spec-reviewer` | Re-derive REQ coverage from a fresh read of briefs and tests; scrutinize the REQ-0.34.0-05-01 BEHAVIOR→SUPPORT re-kinding specifically |
| `quality-reviewer` | Integration coherence: enumerate every `adr_created` write path, confirm or refute #734's "third ingress" framing, test whether closure holds in production configuration |

## Known-open at audit time (not to be re-discovered)

| # | Title | Status at audit |
|---|-------|-----------------|
| 734 | third `adr_created` ingress bypasses the foundation membrane | OPEN — operator-accepted residual at attestation |
| 735 | leading BOM hides the whole frontmatter block | OPEN — deferred hardening |
| 736 | three ad-hoc frontmatter decoders disagree | OPEN — deferred hardening |
| 738 | closeout-walkthrough demo discovery cannot surface refusal demos | OPEN — filed from this ceremony |
| 739 | closeout minor-release ceremony deadlocks on the rule-11 tag audit | OPEN — filed from this ceremony |
