---
mode: CREATE
adr_id: ADR-0.0.9
branch: main
timestamp: "2026-05-31T10:56:41Z"
agent: claude-code
obpi_id: OBPI-0.0.37-11
session_id:
continues_from: 20260531T000357Z-adr-0.0.37-density-dial-cms-extension.md
last_commit_sha: c3d875903607cbcefb55c3ab4ee143af612cce60
---

<!-- Frontmatter migrated under GHI #709: pre-schema fields removed
     because `HandoffFrontmatter` is extra="forbid" and rejected them,
     making this handoff unparseable by its own validator. Their values
     are preserved verbatim here rather than discarded:
       last_lock_event: "2026-05-31T07:10:41Z (OBPI-0.0.37-11 claim; released this session at completion)"
       branch_state: "main, 0 ahead / 0 behind origin/main, clean"
     Body content is unchanged. -->


<!-- Handoff for the Canon Foundation design thread — created by claude-code at 2026-05-31T10:56:41Z -->

## ⚠️ THIS HANDOFF IS A PLAN OF ACTION — NOT A CLEARANCE TO EXECUTE IT

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** authorization to unilaterally execute that plan. The work
below — formalizing the canon foundation ADR, the `amends` disposition, the
planetary-blast-radius refactor — is **operator-gated**. On resume you MUST:

1. Present the plan and current state to the operator.
2. **Obtain explicit operator authorization before executing** any of it — no
   `gz-design` launch, no ADR authoring, no file mutation, no migration, until
   the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; authorization is the ignition.

## Current State Summary

A return-to-health/ADR-status check evolved into a deep co-design session that
produced a **new foundation direction: machine-readable CANON** as the
Layer-1 substrate, and an **honest GHI audit** that re-aimed its justification.

Done this session (all committed, tree clean at `c3d8759`):

- **OBPI-0.0.37-11 — Completed + attested** (`attested_completed`). Density-aware
  master content model: `Bullet` gains `classification`/`witness`/`rationale_ref`/
  `density_min` (Judgment 0-Kelvin floor), `Pillar` section primitive added,
  `reconcile_invariant()` bridges the invariant registry into the content
  substrate. 22 tests, full suite 5790 green. Operator attestation "attest
  completed" (g0). Behave coverage waived (schema-only; BDD deferred to
  ADR closeout per sibling precedent); REQ-05 accepted-uncovered (SUPPORT-kind).
- **Canon foundation design captured** → folded (2026-06-01) into
  `docs/governance/return-to-health-plan-2026-05-30.md` § "Designated Workstream —
  Canon Foundation" (the primary artifact; read that section in full on resume).
  Full blast radius, all nuance preserved. The standalone
  `canon-foundation-design-2026-05-31.md` was deleted in the same pass.
- **GHI root-cause audit** (2 independent passes, 30 open + 44/458 closed): the
  narrow "ADR-0.0.9 docs-as-canon definition caused most failures" hypothesis is
  **refuted (~9–10% L1-ROOT)**; the broad thesis (latent-prose governance /
  mechanical lag) is **validated** (dominant failure family = "advisory rule
  never promoted to mechanical / missing validator"). Justify canon **forward**
  as the mechanization substrate, not backward as root-cause repair.

## Connected To

- **`docs/governance/return-to-health-plan-2026-05-30.md`** — this canon work is
  the foundational layer beneath the plan's **Context-Load CMS workstream**
  (#519 remediation). The CMS (ADR-0.0.37 density dial) renders control surfaces
  *from* canon; canon is the substrate that workstream assumes. Recovery stays
  open (emergency #519 open); this thread advances its route. Keep the plan and
  this handoff in sync.
- **`docs/governance/return-to-health-plan-2026-05-30.md` § "Designated Workstream
  — Canon Foundation"** — the full design capture (five-role ontology, two modes,
  two reconciliation loops, human-as-final-witness, law-vs-rhetoric, Foundry
  north-star, the audit verdict, the full blast radius incl. formerly-deferred
  items, open questions, sequencing). Folded in 2026-06-01 from the now-deleted
  standalone `canon-foundation-design-2026-05-31.md`.
- **`docs/governance/agent-control-surface-rendering-substrate.md`** — the binding
  rendering doctrine the CMS half depends on.

## The Architecture (one-paragraph anchor; full detail in the capture doc)

```
CODE  ⟺  CANON | DESIGN  ⟺  HUMAN DOCS
```
**Canon** (`.gzkit/canon/`) = invariant rules, machine-readable JSON, ontology-
shaped (Foundry: objects/properties/links/actions), two witness kinds (mechanical
gate | the operator at the terminal gate — never null). **Design** (`.gzkit/design/`)
= ADRs/OBPIs, out of `docs/`. **Docs** (`docs/`) = mirror + window; editorial;
**forbidden in operating mode**. Forbidden edges: `code → docs`, `operating-agent
→ docs`. Authoring only via a forced `gz canon` verb; `gz validate --canon-coherence`
governs canon with the gate it enables. The operator authors nothing directly and
reviews the *law* (canon); the gates transitively guarantee the code.

## Decisions Made

- **Decision:** Author a NEW foundation ADR for canon, using a NEW **`amends`**
  ADR disposition that **amends ADR-0.0.9** (state doctrine) and reconciles
  ADR-0.0.10 (storage tiers). The `amends` disposition does not exist in tooling
  yet — this ADR is its first user (self-bootstrap).
  **Rationale:** canon redefines "canon" and "Layer-1," which ADR-0.0.9 owns; the
  audit refutes "0.0.9 caused our failures," so the amend is justified as the
  mechanization substrate, not root-cause repair.
- **Decision (operator):** blast radius = "nuke from orbit, touch all." The three
  items previously parked are IN scope (designed-now, built-last): harness/model
  auto-detection of templates; the full graph engine (canon's links = the graph
  spine; canon is the state-doctrine-lock that unblocks Boundary 3); adopter
  domain-canon `gz init` scaffolding (adopters get two canons, we have one).
- **Decision:** classification source-of-truth = the `advisory-rules-audit.md`
  scorecard data moves INTO canon; the `.md` becomes a `rationale_ref`. Dissolves
  the ADR-0.0.37 concern-1 tension.

## Immediate Next Steps (operator-authorization-gated — see the ⚠️ banner)

1. **Present this plan; get explicit operator go.** Do not execute without it.
2. On authorization: `gz-design` → the canon foundation ADR, using the capture
   doc as founding input; bootstrap the `amends` disposition (amends ADR-0.0.9).
3. Build sequences by failure-mass leverage (capture §12): canon store + `gz canon`
   + `--canon-coherence` + canon-entry-#1 → migrate `.gzkit/rules/*.md` → canon
   (+ the bullet↔scorecard correspondence map, the real center of gravity) →
   design-store relocation → subsume scattered L1 + amend ADR-0.0.9 → CMS renders
   from canon (#519 relief) → graph/detection/adopter-scaffolding.

## Pending Work / Open Loops

- **Open design questions** (capture §9): the bullet↔scorecard correspondence map;
  "one spine" honesty (registry is a lossy projection — pin SoT); the two-gate
  floor check (byte-compare = anti-vibe-edit; path-independent
  `count(Judgment in model) == count(Judgment in rendered-lite)` = render-correctness).
- **Tracked insight (not yet filed):** ceremony gates are not kind-aware —
  `gz obpi complete` flags a SUPPORT-kind REQ as "uncovered" though `gz covers`
  already classifies it SUPPORT (forced a manual `--accept-uncovered`). This is the
  ADJACENT "ceremony incompleteness" family the audit named; candidate for a GHI /
  canon-mechanization target. Consider `/ghi-author`.
- **ADR-0.0.37 OBPI-13/14 re-sequenced** behind the canon ADR (13's classification
  derives from canon). OBPIs 06–10 of 0.0.37 remain Draft and untouched this session.
- **Emergency GHI #519** remains open; canon + CMS-from-canon is its structural route.

## Verification Checklist (on resume)

- [ ] Read `docs/governance/return-to-health-plan-2026-05-30.md` § "Designated
      Workstream — Canon Foundation" in full FIRST (the folded canon capture).
- [ ] `git status` clean; `git branch --show-current` = `main`; HEAD at or beyond `c3d8759`.
- [ ] `uv run gz adr status ADR-0.0.37` shows OBPI-11 `attested_completed`.
- [ ] **Operator authorization obtained before any execution** (the ⚠️ banner).

## Environment State

macOS (darwin), branch `main`, 0 ahead / 0 behind origin, tree clean at handoff.
All this session's work is committed and pushed. OBPI-0.0.37-11 lock released;
no locks held.
