---
id: ADR-0.0.35-foundation-feature-invariance-test
status: Draft
kind: foundation
semver: 0.0.35
lane: heavy
parent: ADR-0.0.18
date: 2026-04-26
---

# ADR-0.0.35-foundation-feature-invariance-test: Foundation/Feature Invariance Test

## Persona

**Active persona:** `main-session` — operator-facing doctrine author who treats kind classification as a load-bearing decision, not a tagging chore. ADR-0.0.18 supplied decision *guidance* (heuristics, worked examples, decomposition narrative); this ADR supplies the *invariance test* — a one-line mechanical question that resolves edge cases the heuristic alone leaves ambiguous. The craft standard is: an adopter facing a kind decision should be able to answer the test in one sentence, with the same answer the project's authors would give.

## Intent

ADR-0.0.18 (ADR Taxonomy — Operator Doctrine, Validated) lands the kind/lane decision playbook for adopters: how to decompose PRDs into ADRs, when to pool vs. promote, how to group epics, and worked examples for foundation-vs-feature classification. That doctrine is sufficient for the typical case — *"is this app-system identity, or is this a named capability?"* routes most decisions cleanly.

But two classes of edge case escape the heuristic:

1. **Substrate decisions that look like features.** The ledger storage backend (JSONL today, candidate Supabase / Pydantic Logfire / SQLite tomorrow) is a *plug* into a port — it ships a named capability and could plausibly be classified as feature work. Yet ledger *discipline* (write-only, append-only, system-of-record) is the invariant; the storage choice is the plug. Without an invariance test, an adopter classifying "switch ledger backend to SQLite" might author it as foundation because *ledger feels foundational*.

2. **Doctrine that looks like discretionary tooling.** Agent control surface fidelity (ADR-0.0.33) and rendering substrate (ADR-0.0.34) both pass cleanly as foundation under the invariance test — *without them, every other gzkit pillar's binding-rule assumption is unprovable* — but the heuristic *"shapes app-system identity"* alone leaves room for an adopter to mis-classify either as feature work, since both ship through tooling and both produce operator-visible artifacts.

The 2026-04-25 complexity-doctrine session sharpened the distinction with a single binding test: **Foundation = "without it, we wouldn't be doing the project."** Paired with the **hexagonal-ports lens** as the structural cue (ports point to invariance; what plugs into the port is feature), the test resolves both edge classes mechanically.

This ADR codifies the test as forward extension of ADR-0.0.18. ADR-0.0.18 is Validated and the test post-dates its authoring; the right move is *extend forward via new foundation ADR*, not amend backward (per `.gzkit/rules/adr-audit.md` and the operator's complexity-doctrine guidance).

**After this ADR:** every `gz plan create --kind foundation` invocation has a one-line test the operator (or skill-prompt-driven adopter) can apply to confirm the classification. `gz-design`, `gz-plan`, and `gz-adr-create` skill prompts cite the test inline. Future-promotable: `gz validate --kind-invariance` asserts every foundation ADR's body answers the test affirmatively in a Why-foundation-tier section (out-of-scope here; capture as forward hook).

## Decision

Land the Foundation/Feature Invariance Test as a binding kind-classification rule, paired with the hexagonal-ports structural lens. Author the test as a Lite-lane foundation ADR with brief-level Gate 5 attestation per the Lane & Kind Attestation Matrix (foundation-kind rigor, regardless of lane).

**Key doctrine decisions (locked with operator, 2026-04-26):**

1. **The invariance test, verbatim:** *"Foundation = without it, we wouldn't be doing the project."* If the answer is yes — without this decision/capability/discipline, the project would not exist as a project, would not be coherent, would not be itself — the ADR is foundation. If the answer is no — the project would still be the project; this is a capability or a substrate choice — the ADR is feature (or pool, if not yet committed).

2. **The hexagonal-ports lens as structural cue.** Ports point to invariance; plugs are features.
   - A *port* is the abstract contract — what the system requires from a collaborator. Ports define what the project *is*: ledger discipline, gate covenant, attestation surface, agent control-surface fidelity. Authoring a port is foundation work.
   - A *plug* is the concrete implementation behind the port — what fills the contract. Plugs ship named capabilities: JSONL storage, the specific renderer for control surfaces, the chosen test runner. Authoring a plug is feature work.
   - When kind is ambiguous, ask: *am I authoring the port (the contract every implementation must honor) or a plug (one specific implementation behind a port that already exists)?*

3. **Worked example — ledger discipline vs. storage backend.**
   - **Foundation:** *"The ledger is the system-of-record; events are append-only and write-only; every governance decision must trace to a ledger entry."* This is the port. Without it, gzkit is not gzkit.
   - **Feature:** *"Replace the JSONL ledger backend with SQLite for query performance."* This is a plug change. The project remains the project under either backend; the discipline is invariant.

4. **Worked example — paired foundations from the 2026-04-25 cluster.**
   - **ADR-0.0.33** (Agent Control Surface Fidelity Doctrine) is foundation because *without it, every other gzkit pillar's binding-rule assumption is unprovable*. The fidelity contract is a port: every rendering substrate must honor it.
   - **ADR-0.0.34** (Agent Control Surface Rendering Substrate) is foundation because *without it, the per-turn surface is a hand-authored vibing surface and the fidelity validators have nothing canonical to diff against*. The canonical substrate is the port that fidelity validators read against; a future renderer-of-the-month is the plug.

5. **Anti-pattern: classifying as foundation because "it feels foundational."** Foundation is a *test answer*, not a *vibe*. If an adopter cannot articulate "without this, the project would not be the project," the ADR is not foundation regardless of how weighty the topic feels. Classify as feature (or pool); promote to foundation later only if the invariance test starts answering yes — which usually means the scope itself shifted from plug to port.

6. **Why-foundation-tier section becomes load-bearing.** Every foundation ADR's body answers the invariance test affirmatively, in plain language, under a `## Why foundation tier?` section the validator can find. This ADR introduces the convention (OBPI-03), updates the foundation-ADR scaffolding so new ADRs land the section pre-populated, and ships `gz validate --kind-invariance` (OBPI-04) as the mechanical assertion that every foundation ADR carries the section non-empty. The validator is in-scope here, not deferred — single-OBPI doctrine ADRs that punt their own enforcement hook to a future ADR are the smell that triggered this re-decomposition.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT amend ADR-0.0.18. ADR-0.0.18 is Validated; the invariance test post-dates its authoring; backward amendment is the wrong motion. Adopters reading ADR-0.0.18 will be cross-linked forward to this ADR.
- Does NOT re-litigate the kind taxonomy vocabulary (locked in ADR-0.0.17) or the kind/lane orthogonality (locked in ADR-0.0.18).
- Does NOT extend the invariance test to non-ADR artifacts (PRDs, OBPIs, constitutions). The test is for ADR kind classification specifically; analogous tests for other artifact types are separate doctrine if needed.
- Does NOT replace ADR-0.0.18's worked examples or decision narrative. ADR-0.0.18 remains the canonical playbook; this ADR adds the invariance test as a sharper resolution rule for edge cases the playbook leaves ambiguous.
- Does NOT backfill the Why-foundation-tier section into existing foundation ADRs. The convention is forward-applicable; backfill is a separate sweep tracked as a follow-up chore (not gated by this ADR's closeout).

## Consequences

### Positive

1. Edge-case kind decisions resolve mechanically — the substrate-vs-port and fidelity-doctrine cases that ADR-0.0.18's heuristic leaves ambiguous have a one-line test that returns the same answer regardless of which adopter applies it.
2. Skill prompts (`gz-design`, `gz-plan`, `gz-adr-create`) gain a single invariance question to cite inline alongside ADR-0.0.18's heuristic — typing budget for the operator stays low while classification rigor goes up.
3. The hexagonal-ports lens makes the test architecturally legible — adopters who already think in ports/adapters need no translation; adopters who don't gain a structural framing they can apply elsewhere (e.g. test boundaries, dependency posture).
4. Future foundation ADRs become self-justifying — the Why-foundation-tier convention forces every author to *show their work* against the invariance test, and `gz validate --kind-invariance` (shipped under OBPI-04) closes the convention mechanically so the discipline is structural rather than honor-system.
5. The test makes "downgrade to feature" a routine routing decision rather than a controversial reclassification. Adopters who fail the invariance test on a candidate foundation ADR have a clean off-ramp: classify as feature, scope appropriately.

### Negative

1. The invariance test is a *one-line judgment*, not a mechanical assertion — different adopters can in principle disagree on what *"the project"* is. Mitigation: the hexagonal-ports lens supplies the structural tiebreaker, and the worked examples (ledger discipline vs. backend; ADR-0.0.33/0.0.34 paired foundations) ground the test in concrete precedent.
2. Risk of retroactive re-classification anxiety — adopters reading the test may want to audit existing foundation ADRs against it. Mitigation: existing foundation ADRs are Validated; this ADR is forward-applicable only. A separate sweep would be its own scope (and most existing foundation ADRs pass the test on inspection).
3. Adds a doctrine page adopters must read alongside ADR-0.0.18 — minor cognitive load increase. Mitigation: the test is one sentence and the lens is one sentence; cross-link from ADR-0.0.18's "see also" tail keeps discovery cheap.
4. Adds a Heavy-lane CLI surface (`gz validate --kind-invariance`) under OBPI-04 — that triggers the full Heavy-lane gate covenant (manpage, behave scenario, attestation) for what is fundamentally a doctrine-enforcement validator. Mitigation: the validator is small (one scope function plus REQ-derived tests), and the Heavy-lane discipline is exactly what guarantees the convention stays structural rather than drifting back to honor-system.
5. Backfilling the Why-foundation-tier section into existing foundation ADRs is out-of-scope and remains honor-system until a separate sweep lands. Mitigation: `gz validate --kind-invariance` reports drift on every existing foundation ADR on first run, which produces the work list for the backfill sweep mechanically rather than requiring up-front enumeration.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 0
- Logic/Engine: 1
- Interface: 1
- Observability: 0
- Lineage: 1
- Dimension Total: 3
- Baseline Range: 3-4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.35-01: Concept page authoring — `docs/user/concepts/foundation-feature-invariance-test.md` as canonical reference (verbatim test, hexagonal-ports lens, both worked examples, anti-pattern), bidirectional cross-link with ADR-0.0.18's concepts page, `docs/user/index.md` integration, runbook navigation entry. Parallel-root.
- [ ] OBPI-0.0.35-02: Skill prompt enrichment — `gz-design`, `gz-plan`, `gz-adr-create`, `gz-adr-promote` skill prompts for `--kind` cite the invariance test inline alongside ADR-0.0.18's heuristic; skill body text gains the one-line test plus lens; mirror sync to `.claude/skills/` and `.github/skills/`; skill versions bumped per skill-surface-sync discipline. Depends on OBPI-01.
- [ ] OBPI-0.0.35-03: Why-foundation-tier section convention — define the `## Why foundation tier?` section every foundation ADR carries (one-line answer to the invariance test plus port-vs-plug framing); update the foundation ADR template in `gz plan create --kind foundation` scaffolding so new ADRs scaffold the section pre-populated; document the convention in the concepts page authored under OBPI-01. Depends on OBPI-01.
- [ ] OBPI-0.0.35-04: `gz validate --kind-invariance` validator scope — author validator in `src/gzkit/governance/trust_audits.py` enumerating every `kind: foundation` ADR under `docs/design/adr/foundation/**` and asserting each carries the Why-foundation-tier section non-empty; wire into `gz check`; REQ-derived unit tests asserting section-presence semantics (per `.gzkit/rules/tests.md` § Tests assert semantics, not strings); manpage and runbook updates per `.claude/rules/gate5-runbook-code-covenant.md`; behave scenario tagged with the new REQ-IDs. Heavy-lane CLI surface change. Depends on OBPI-03.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

**Origin:** 2026-04-25 complexity-doctrine session. Operator sharpened the foundation/feature distinction with the binding invariance test ("Foundation = without it, we wouldn't be doing the project") and the hexagonal-ports lens (ports point to invariance; plugs are features). Recorded against ADR-0.0.33 (Agent Control Surface Fidelity Doctrine) and ADR-0.0.34 (Agent Control Surface Rendering Substrate) as paired foundations passing the test cleanly.

**Routing decision (2026-04-26):** GHI #334 originally proposed amending ADR-0.0.18 in place via OBPI-0.0.18-06. Operator pushback: ADR-0.0.18 is Validated and foundation-tier; reopening for an amendment OBPI inverts the closeout/attestation cycle. The correct routing for new doctrine post-dating a Validated ADR is **extend via new foundation ADR**, not patch the closed one. Patch would imply admission that ADR-0.0.18's design intent was unmet — but ADR-0.0.18's intent was decision *guidance*, and that guidance is sound; the invariance test is sharper, mechanical doctrine that crystallized later. Forward extension preserves ADR-0.0.18's Validated state and lands the test where its own Gate 5 attestation can fire cleanly.

**Closed:** GHI #334 (`withdrawn` with route correction comment, 2026-04-26).

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_kind_invariance.py` (validator scope under OBPI-04, REQ-derived semantics), `tests/commands/test_validate.py` additions for the `--kind-invariance` flag wiring
- [ ] Docs: `docs/user/concepts/foundation-feature-invariance-test.md` (OBPI-01), runbook cross-link, ADR-0.0.18 concept-page bidirectional back-link, `docs/user/manpages/gz-validate.md` updates (OBPI-04)
- [ ] Skills: `.gzkit/skills/gz-design/SKILL.md`, `.gzkit/skills/gz-plan/SKILL.md`, `.gzkit/skills/gz-adr-create/SKILL.md`, `.gzkit/skills/gz-adr-promote/SKILL.md` — interview-prompt enrichment with the invariance test (OBPI-02), version bumps per skill-surface-sync discipline
- [ ] Templates: foundation-ADR scaffolding template gains pre-populated `## Why foundation tier?` section (OBPI-03)
- [ ] Behave: scenarios under `features/` tagged with `@REQ-0.0.35-04-NN` for the validator (OBPI-04)
- [ ] ARB receipts: `arb-step-unittest-*`, `arb-step-ruff-*`, `arb-step-typecheck-*`, `arb-step-coverage-*`, `arb-step-mkdocs-*` cited in OBPI-04 closeout (Heavy-lane attestation requirement)

## Alternatives Considered

**Alternative 1 — Amend ADR-0.0.18 in place via OBPI-0.0.18-06.**
Rejected. ADR-0.0.18 is Validated; reopening a Validated foundation ADR for retroactive doctrine grafting inverts the closeout cycle and pushes brief-level Gate 5 attestation back onto an ADR that already passed it. The 2026-04-26 operator guidance was explicit: *"return to a validated foundation"* options are *extend via new ADR* or *patch (admission of design-intent failure)*. ADR-0.0.18's design intent (decision guidance for adopters) is sound; the invariance test is net-new sharpening, not a retro-fix. Extend, don't patch.

**Alternative 2 — Patch ADR-0.0.18 as design-intent admission.**
Rejected. Patch would require evidence that ADR-0.0.18's worked examples or decision heuristic *actually mis-route adopters today*. They don't — ADR-0.0.18 routes the typical case cleanly; the invariance test resolves edge cases the heuristic alone leaves ambiguous (substrate vs. port; doctrine that looks like tooling). The test post-dates ADR-0.0.18's authoring; that is forward motion, not retroactive correction.

**Alternative 3 — Codify the invariance test in `AGENTS.md` § Kinds as a direct doctrine edit.**
Rejected. AGENTS.md is the live operator contract; doctrine that crystallizes through cluster-session work belongs in an ADR with attestation, not a direct contract edit that bypasses Gate 5. The proper flow is: ADR codifies the doctrine, attestation closes the loop, then AGENTS.md (and the concepts page) cite the ADR. AGENTS.md edits are downstream of this ADR's OBPI-01, not a substitute for it.

**Alternative 4 — Leave the invariance test as judgment-only doctrine (no codification).**
Rejected. The test answers the same question for the same adopter every time only if it has a canonical home. Judgment-only doctrine drifts: each adopter re-derives or partially-recalls it; the worked-example precedent (ADR-0.0.33/0.0.34) is invisible to future authors who weren't in the 2026-04-25 session. Codifying the test in a foundation ADR with cross-linked concepts page is the mechanical defense against that drift.

**Alternative 5 — Author as feature ADR rather than foundation.**
Rejected by the test itself. *Without the invariance test, kind classification for foundation candidates remains heuristic-only* — the project's ability to distinguish substrate from port collapses to per-author judgment, and the foundation tier loses its meaning. The test answers the invariance question affirmatively when applied to itself: it is foundation.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.35 | Pending | | | |
