# AUDIT_PLAN — ADR-0.0.37-constitutional-invariant-composition

**Date:** 2026-07-18
**Driver persona:** `pipeline-orchestrator`
**Ceremony:** `/gz-adr-audit` — COMPLETED → VALIDATED
**Entry state:** Lifecycle `Completed`, closeout phase `attested`, OBPI 15/15, Closeout READY, QC READY, lane `heavy`, kind `foundation`

## Scope

ADR-0.0.37 declares two constitutional invariants:

- **CIC-1** — AGENTS.md is a Layer-3 derived view composed from schema-validated,
  ledger-witnessed canon; drift between rendered and committed fails closed.
- **CIC-2** — every OBPI brief reconciles against real project shape at Stage 1
  and at completion.

The ADR carries a **Terminal Disposition (2026-07-18): Split-and-Supersede**,
booking itself `Completed — Partial`: the delivered floor is gated and green;
the composition engine (registry spine OBPI-02/03; corpus-derivation OBPI-21/22)
is severed to GHI #623 (absorbing #654) as a post-1.0 successor feature.

This audit therefore verifies **the floor as scoped**, not the original
full-engine thesis. The re-scoping is itself an audit object: does the
Terminal Disposition honestly describe what shipped?

## Checks

| # | Claim under audit | Method | Layer |
|---|---|---|---|
| C1 | All linked OBPIs completed with ledger evidence | `gz adr audit-check ADR-0.0.37` | L2 |
| C2 | Uncovered REQs are advisory-only, not BEHAVIOR-kind gaps on linked briefs | independent `spec-reviewer` dispatch | L1 |
| C3 | ADR thesis holds against the running system | `gz adr fidelity` (bound gate) | L1 |
| C4 | Heavy-lane gates 1–4 pass | `gz gates --adr ADR-0.0.37` | L1 |
| C5 | Full unit suite green | `uv run -m unittest -q` | L1 |
| C6 | CLI governance coverage clean | `gz cli audit` | L1 |
| C7 | Surviving 15 OBPIs cohere into the claimed capability | independent `quality-reviewer` dispatch | L1 |
| C8 | Feature Checklist 1:1 sync with surviving briefs | checklist read vs `gz adr status` | L1 |

## Risk focus

This ADR lost **12 of 27** authored briefs mid-flight, including four
composition OBPIs withdrawn in `d03ce98f`. The named risk is that withdrawal
paperwork diverged from delivered code — that briefs were marked abandoned
while their deliverables shipped and became load-bearing. Because ADR-0.0.37
exists precisely to prevent Layer-1 canon from diverging from reality, any such
divergence inside its own package is a first-class finding, not a clerical nit.

Secondary risk: fidelity assertions that restate the gate rather than exercise
the thesis (tautological rows).

## Persona dispatch (per SKILL.md)

- `spec-reviewer` — independent REQ-coverage trace (C2)
- `quality-reviewer` — independent structural-coherence assessment (C7)
- `narrator` — frames AUDIT.md in operator-value terms (Step 4)

`implementer` is NOT dispatched: no code is written in this ceremony. Defects
found route to a GHI, never to an in-audit implementation.
