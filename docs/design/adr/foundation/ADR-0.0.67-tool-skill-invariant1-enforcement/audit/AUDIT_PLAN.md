# AUDIT_PLAN — ADR-0.0.67-tool-skill-invariant1-enforcement

**Lifecycle transition:** COMPLETED → VALIDATED
**Lane/Kind:** heavy / foundation
**Audit date:** 2026-06-09
**Driver persona:** pipeline-orchestrator
**Independent reviewers:** spec-reviewer (REQ-tracing), quality-reviewer (structural coherence), narrator (value framing)

## Claims extracted from ADR prose

| # | Claim (from § Decision / § Consequences) | Check | Proof |
|---|------------------------------------------|-------|-------|
| C1 | Recursive enumeration (`_known_cli_verb_paths()`) walks the full argparse tree; `audit_skill_alignment` enforces Invariant 1 across multi-word subcommands (the port) | Enumerate paths; assert multi-word leaf paths present and audited | `proofs/demo1-recursion-port.txt`, `proofs/skill-alignment.txt` |
| C2 | 10 live orphan verbs genuinely wielded by 6 skills, zero new `_NO_SKILL_VERBS` waivers | `gz validate --skill-alignment` green; OBPI-02 Key Proof | `proofs/skill-alignment.txt` |
| C3 | `gz obpi audit` is the deterministic engine gz-obpi-reconcile Phase 1 wields | Run `gz obpi audit --adr ADR-0.0.67`; show structured per-OBPI output | `proofs/demo3-obpi-audit-engine.txt` |
| C4 | 3 deprecated `obpi lock-*` hyphen aliases deleted; canonical space forms intact | argparse rejects `obpi lock-claim`; `obpi lock list` works | `proofs/demo2-alias-deleted.txt` |
| C5 | All BEHAVIOR REQs covered; SUPPORT REQs proven via ledger event + structural validator | `gz validate --req-kind-discipline` green (fail-closes on uncovered BEHAVIOR) | `proofs/req-kind-discipline.txt` |
| C6 | All linked OBPIs completed with evidence (L2 ledger proof) | `gz adr audit-check ADR-0.0.67` PASS | `proofs/audit-check.txt` |

## Risk focus

- **Wire-not-waive integrity:** verify wirings are genuine procedural use, not name-drops (ADR pre-mortem #1). → spec-reviewer.
- **Coupled-surface coherence:** alias deletion removed parser + stale waivers + doc cascade together. → quality-reviewer.
- **Coverage-advisory interpretation:** 5 uncovered REQs must all be SUPPORT-kind, not hidden BEHAVIOR gaps. → confirmed by C5 (req-kind-discipline).

## Known anomaly to explain (Step 5)

`gz obpi audit --adr ADR-0.0.67` reports per-OBPI coverage FAIL (12–14% < 40%). This is **per-OBPI-scoped** coverage (each lone test file vs its whole module), orthogonal to the suite-level floor the OBPIs passed at Gate 2 (5958–5961 tests). The authoritative L2 gate is `gz adr audit-check` (PASS). To be documented as an explained anomaly, not a shortfall.

## Trust model

Layer-2 audit: consumes ledger proof. audit-check PASS + attestations 1–2 days old (inside 7-day staleness window) → trust L1 proof, no re-verification of the test suite required. Value demonstration (Step 3) is run live regardless.
