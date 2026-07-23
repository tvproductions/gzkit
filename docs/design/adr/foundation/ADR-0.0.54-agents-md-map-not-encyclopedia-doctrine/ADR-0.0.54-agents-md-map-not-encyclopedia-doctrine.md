---
id: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
status: Validated
kind: foundation
semver: 0.0.54
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-19
---

# ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine: AGENTS.md Map-Not-Encyclopedia Doctrine

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats AGENTS.md as the binding per-turn context surface, not as a documentation home; treats `docs/governance/` as the encyclopedia AGENTS.md points into, not as a hand-maintained library. Refuses to compress doctrine prose by deleting nuance — every lifted paragraph survives verbatim at a stable canonical URL the AGENTS.md bullet links to. Refuses to leave AGENTS.md a "soft target" where rationale prose accretes uncontested. The structural witness is not a passing diet pass — that already exists as a one-shot skill — but a *mechanical* invariant that AGENTS.md's shape stays map-not-encyclopedia at every commit.

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit's AGENTS.md continues to accumulate doctrine prose, worked examples, anti-pattern lists, and rationale paragraphs at every doctrinal expansion — the file is currently 30,924 chars / 390 lines (within the 40k budget) and the existing `instructions_files_budget.json` mechanism caps weight but does not constrain *shape*. The OpenAI Harness Engineering thesis (2026-02-11) names the four predictable failure modes directly: *"Context is a scarce resource… Too much guidance becomes non-guidance… It rots instantly… It's hard to verify."* gzkit's `gz-context-diet` skill exists precisely because the pattern repeatedly accretes; the skill is reactive, not preventive. The project still ships, but the per-turn context budget bleeds at every doctrinal expansion: each ADR's authoring impulse is to *add a paragraph to AGENTS.md*; the canonical lift target (`docs/governance/agent-contract-rationale.md`) exists but is not mechanically the default. **Yes — the project would still be the project, but it would lose the property that AGENTS.md remains a binding-bullets-and-links map rather than an encyclopedia.** This ADR names the map-not-encyclopedia property as invariant and ships mechanical enforcement.

**Port-vs-adapter framing:** This ADR authors a **port**. It declares the abstract shape AGENTS.md must satisfy (binding bullets + canonical links + structured tables; no multi-paragraph rationale prose; no worked examples; no anti-pattern catalogs; no narrative explanations) and the mechanical validator (`gz validate --agents-md-map-conformance`) that binds the shape. The specific section layout, the choice of which subsections to lift first, and the per-section character targets are adapters behind the port. The existing `gz-context-diet` skill becomes the *operator-facing procedure* against the port; the validator becomes the *mechanical witness*.

## Intent

The OpenAI Harness Engineering thesis (2026-02-11) names the failure pattern directly:

> *"We tried the 'one big AGENTS.md' approach. It failed in predictable ways:*
>
> *Context is a scarce resource. A giant instruction file crowds out the task, the code, and the relevant docs — so the agent either misses key constraints or starts optimizing for the wrong ones.*
>
> *Too much guidance becomes non-guidance. When everything is 'important,' nothing is. Agents end up pattern-matching locally instead of navigating intentionally.*
>
> *It rots instantly. A monolithic manual turns into a graveyard of stale rules. Agents can't tell what's still true, humans stop maintaining it, and the file quietly becomes an attractive nuisance.*
>
> *It's hard to verify. A single blob doesn't lend itself to mechanical checks (coverage, freshness, ownership, cross-links), so drift is inevitable.*
>
> *So instead of treating AGENTS.md as the encyclopedia, we treat it as the table of contents."*

gzkit has been authoring the encyclopedia-style AGENTS.md and lamenting the result in parallel. The empirical state at this ADR's authoring (2026-05-19):

- **AGENTS.md**: 390 lines / 30,924 chars (~77% of the 40k budget). Contains: binding bullet lists (PRIME DIRECTIVE, DO IT RIGHT, Behavior Rules, Defect-fix routing), structured tables (Persona, Gate Covenant, OBPI kinds, Attestation canonical invocations), AND multi-paragraph rationale prose, worked examples, anti-pattern catalogs, and "Why this is canon" coda paragraphs that the OpenAI thesis specifically names as the failure-pattern surface.
- **CLAUDE.md**: 27 lines / 1,378 chars. Already tight; serves as the model-specific harness file pointing at AGENTS.md as the universal contract.
- **`.claude/rules/*.md`**: per-file 16k cap (with current max ~15k). Same encyclopedia-style accretion risk; the cap is mechanical, the shape is not.

The existing mechanical defense (`gz validate --instructions-files-budget`) caps *weight* but not *shape*. The existing operator-facing remedy (`/gz-context-diet`) lifts content reactively when invoked, but the lift is one-shot — the file is free to re-accumulate prose by the next ADR. The canonical lift target (`docs/governance/agent-contract-rationale.md`) exists and has been receiving partial lifts under prior GHIs (the file's *"§ Rationale for 1a"*, *"§ Anti-vibing mantra"*, *"§ Stdlib-First doctrine"*, *"§ Operator economy"*, *"§ Rationale for Behavior Rule 11"* sections were each lifted there from AGENTS.md under specific GHI numbers). The path exists; what's missing is the *default*.

This ADR authors the **map-not-encyclopedia doctrine** as a foundation invariant:

- **AGENTS.md contains binding bullets, structured tables, and canonical links — nothing else.** Multi-paragraph rationale prose, worked examples, anti-pattern catalogs, *"Why this is canon"* paragraphs, and narrative justifications live in `docs/governance/` at stable URLs the AGENTS.md links to. The bullet states the rule; the link names the encyclopedia.
- **The budget for AGENTS.md tightens 40k → 15k chars.** This is the operator-selected "moderate" target (the OpenAI sweet spot is ~100 lines / ~8k chars; the operator selected ~200 lines / ~15k chars as the balanced first step, preserving the binding-bullet density gzkit has accreted while halving the rationale-prose surface).
- **The doctrine is mechanically enforced.** Ship `gz validate --agents-md-map-conformance` that asserts: AGENTS.md contains no paragraph longer than N lines, no fenced "Why this is canon" coda blocks, no worked-example subsections (detected by recognizable markers: blockquoted multi-line examples; subsections titled "Worked example", "Anti-patterns", "Rationale", "Why X is canon"); each binding-bullet section ≤ M chars; every "See …" / "see [doc]" reference resolves to an existing file.
- **The path of least resistance to lift rationale becomes the default.** The new validator's `RemediationPayload.recovery` (per ADR-0.0.53) is `/gz-context-diet` for any conformance failure; future ADRs landing under the rule cannot accrete prose without the diet pass running first.

**Target table of contents for the post-diet AGENTS.md** (operator-reviewed during this ADR's drafting; the per-section target sizes are inferences from the current file plus the OpenAI shape — they are codified in OBPI-02's lift instructions):

| Section | Current chars (approx) | Target chars | Action |
|---|---|---|---|
| Project Identity | 200 | 200 | KEEP |
| Why this contract is not minimal | 600 | 100 (link only) | LIFT to `docs/governance/agent-contract-rationale.md` § Why this contract is not minimal |
| Persona | 1,600 | 1,200 | KEEP table; LIFT discovery prose (1 line link) |
| PRIME DIRECTIVE (OWNERSHIP) | 2,800 | 1,800 | KEEP 6 numbered items + 5 sub-bullets; LIFT examples/anti-rationalizations to `docs/governance/prime-directive.md` |
| DO IT RIGHT (CRAFTSMANSHIP MAXIM) | 2,500 | 1,500 | KEEP 9 numbered claims + Invariant 6c/6g/6h lines; LIFT pedagogical examples to existing rationale doc |
| MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA) | 1,700 | 800 | KEEP 4 operative claims; LIFT mantra blockquote prose to existing rationale doc § Anti-vibing mantra |
| STDLIB-FIRST DOCTRINE | 1,800 | 1,100 | KEEP 5 operative claims; LIFT "Existing canonical applications" subsection to rationale doc |
| OPERATOR ECONOMY OF EFFORT | 1,700 | 1,000 | KEEP 6 operative claims; LIFT anti-patterns subsection to existing rationale doc § Operator economy |
| Behavior Rules — Always | 4,800 | 2,800 | KEEP 13 numbered items as one-line bindings; LIFT prose explanations to `docs/governance/behavior-rules.md` |
| Behavior Rules — Never | 1,400 | 900 | KEEP 7 items as one-line bindings; LIFT prose to same |
| Pattern Discovery | 350 | 350 | KEEP |
| Skills | 2,200 | 600 | KEEP cluster names + canonical-directory link; LIFT skill-by-skill catalog to `docs/governance/skills-catalog.md` (auto-generated from manifest by `gz agent sync control-surfaces`) |
| Gate Covenant | 2,400 | 1,400 | KEEP tables (Gate / Kinds); LIFT mechanical-enforcement narrative to existing taxonomy ADR pointer |
| OBPI Acceptance Protocol | 1,800 | 1,000 | KEEP binding paragraphs; LIFT Universal-OBPI-Attestation expansion to `docs/governance/obpi-attestation.md` |
| Execution Rules | 350 | 350 | KEEP |
| Attestation | 1,800 | 1,200 | KEEP canonical-invocations table; LIFT worked-example pointer + lane-behavior expansion to existing rationale doc § Attestation |
| Defect-fix routing | 1,800 | 1,200 | KEEP threshold table + decision protocol; LIFT precedent catalog pointer to existing routing doc |
| Control Surfaces | 200 | 200 | KEEP |
| Local Agent Rules | 1,500 | 1,200 | KEEP binding rules; LIFT operator-PII incident pointer detail to handoff doc |
| Governance doctrine surfaces | 2,000 | 1,200 | KEEP binding pointers; LIFT mechanical-scopes narrative to existing scorecard doc |
| Architectural Boundaries | 1,500 | 900 | KEEP 6 numbered bullets; LIFT memo-source narrative |
| **TOTAL (approximate)** | **~30,900** | **~21,000** | |

The table targets ~21k chars; the budget is set to **15k chars** with 6k headroom. The 15k target is achievable via tighter wording during the lift (the table above is conservative; OBPI-02's lift pass tightens each lifted section's surviving AGENTS.md text). If the lift cannot reach 15k without lossy compression, the budget is amended under an OBPI-04 receipt (the operator's stated preference was *"moderate"* — 15k is the floor, not a sacred constant).

**Empirical grounding for the doctrine:** every section the OpenAI thesis names as a failure mode is currently present in gzkit's AGENTS.md (multi-paragraph rationale, worked examples, anti-pattern lists, "Why X is canon" coda blocks). The existing `gz-context-diet` skill confirms the path is known — what's missing is the *mechanical default* that makes the diet the resting state, not the cleanup pass.

## Decision

Canonize AGENTS.md (and by extension, the analogous map-not-encyclopedia shape for CLAUDE.md and `.claude/rules/*.md`) as a binding map of bullets + tables + canonical links, tightening the AGENTS.md budget from 40k to 15k chars, lifting the named rationale-prose sections to `docs/governance/`, and shipping `gz validate --agents-md-map-conformance` as the mechanical witness. Decomposed into four OBPIs.

**The invariant (canonical statement):** AGENTS.md MUST contain only (a) binding bullet rules (one bullet = one rule, ≤ 3 lines per bullet), (b) structured tables (Persona, Gate Covenant, OBPI kinds, canonical-invocations, defect-fix routing thresholds), and (c) canonical-link references to deeper documentation at stable URLs under `docs/governance/`. AGENTS.md MUST NOT contain (i) multi-paragraph rationale prose (paragraph > 5 lines without a binding-bullet anchor), (ii) worked examples or anti-pattern catalogs, (iii) "Why this is canon" / "Why X" coda blockquotes, (iv) narrative pedagogical sections, or (v) operative-claims expansions whose binding-bullet form already states the rule. CLAUDE.md inherits the same shape contract (with a tighter per-file budget reflecting its already-tight state). `.claude/rules/*.md` files inherit the same shape with their existing 16k per-file budget, plus a per-file shape audit.

**Decision items (1:1 with Checklist below):**

1. **Author the doctrine + budget tightening port.** Author `.gzkit/rules/agents-md-map-doctrine.md` (rule version `0.1.0`, paths `AGENTS.md`, `CLAUDE.md`, `.claude/rules/*.md`) naming the invariant and the five prohibited shapes. Author `docs/governance/agents-md-doctrine.md` as the canonical expansion the AGENTS.md `Why this contract is not minimal` link will eventually point to. Update `data/instructions_files_budget.json`: AGENTS.md `40000 → 15000`, CLAUDE.md `40000 → 4000` (with 2k headroom over the current 1378), per-rule-file `16000` unchanged (parallel lift OBPI deferred to a future GHI if needed). Add scorecard entry to `docs/governance/advisory-rules-audit.md` classifying the rule **Mechanical** for shape; the per-section size targets remain **Judgment** and live in this ADR's TOC table.

2. **Lift the named sections from AGENTS.md to `docs/governance/`.** Execute the lift table above: each named subsection's rationale prose moves to the named target file at a stable section anchor; the AGENTS.md bullet replaces the prose with a one-line `See […](docs/governance/…)` link preserving the bullet's binding text. Files affected: `docs/governance/agent-contract-rationale.md` (already exists; gains §§ for the lifted subsections), `docs/governance/prime-directive.md` (new), `docs/governance/behavior-rules.md` (new), `docs/governance/skills-catalog.md` (new; auto-regenerated from `.gzkit/manifest.json` by `gz agent sync control-surfaces`), `docs/governance/obpi-attestation.md` (new). Each lifted section preserves verbatim wording; no compression-by-summarization permitted. The post-lift AGENTS.md must be ≤ 15k chars; if it overruns, the lift table targets tighten in this OBPI's review pass.

3. **Ship `gz validate --agents-md-map-conformance` mechanical validator.** New validator scope under `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` that asserts: (a) every paragraph in AGENTS.md is either ≤ 5 lines OR begins with a binding bullet marker (`- `, `1.`, `**`); (b) no subsection has a title in the prohibited set (`Worked example`, `Anti-patterns`, `Rationale`, `Why this is canon`, `Why X is canon`); (c) every `See [text](path)` link resolves to an existing file with the named anchor; (d) the file size is within the budget set by `data/instructions_files_budget.json`. Validator emits `RemediationPayload` per ADR-0.0.53 with `recovery: /gz-context-diet`. Add the scope to `gz check` default pipeline. Author tests under `tests/governance/test_agents_md_map_conformance.py` covering each rejection path + the happy path against the lifted AGENTS.md. Update `docs/user/manpages/validate.md` with the new scope.

4. **Apply the doctrine to CLAUDE.md and `.claude/rules/*.md`; finalize budgets and runbook.** Audit CLAUDE.md against the same shape rules; lift any prohibited shapes (CLAUDE.md is currently 1378 chars and tight; the audit may surface zero work, in which case the OBPI's deliverable is the audit receipt itself). Audit every file under `.claude/rules/*.md` against the same shape; lift to per-rule expansion docs as needed. Update `data/instructions_files_budget.json` to its final values (per-file `.claude/rules/*.md` tightening if the audit identifies headroom). Update `docs/user/runbook.md` § Recovery flows with the canonical "AGENTS.md drift → /gz-context-diet" path. Update `docs/governance/governance_runbook.md` § Instruction files naming the map-not-encyclopedia doctrine as the resting state. Cross-link the new `gz validate --agents-md-map-conformance` from the trust-doctrine page.

**Sequencing:** OBPI-01 (doctrine + budget tightening + rule + scorecard) is the precondition for all others — the budget change and the rule must land before the lift, so the lift is operating against the new contract. OBPI-02 (the lift) is the largest content-edit OBPI and must complete before OBPI-03 (validator) ships, because the validator's happy-path tests run against the lifted AGENTS.md. OBPI-03 (validator + tests + manpage) lands third. OBPI-04 (CLAUDE.md + `.claude/rules/*` parallel application + runbook + final budgets) lands fourth.

**Lane: Heavy.** New rule file + new doctrine doc + new CLI validator scope + behavior change at the per-turn context surface every agent reads + budget change in `data/instructions_files_budget.json` + lifts to new and existing governance docs. Per `.claude/rules/cli.md` (new validator scope), `.gzkit/rules/skill-surface-sync.md` (new canonical rule surface), and the universality of the file under change (every agent run reads AGENTS.md). Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.36-universal-obpi-attestation.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT change the *content* of any binding bullet — only the location of rationale prose and worked examples. Every rule, every operative claim, every behavior-rule item survives verbatim.
- Does NOT modify the existing `gz validate --instructions-files-budget` weight cap — that mechanism is preserved; this ADR's `--agents-md-map-conformance` scope is additive (shape vs weight).
- Does NOT compress lifted prose by summarization — verbatim preservation at the new URL is the rule; if a paragraph wants editing, that's a separate doctrinal-edit OBPI.
- Does NOT modify the `gz-context-diet` skill's procedure beyond pointing it at the new validator as the conformance witness — the skill's existing instructions remain authoritative.
- Does NOT extend to other instructions files outside the named scope (e.g., per-skill `SKILL.md` files, runbooks, manpages) — those have their own shape contracts via `gz-cli-audit` and the operator-doc-verb-resolution rule.
- Does NOT introduce a new auto-regeneration pipeline for `docs/governance/skills-catalog.md` beyond reusing the existing `gz agent sync control-surfaces` mechanism — the catalog regenerates from `.gzkit/manifest.json` exactly as the current `.claude/rules/*.md` mirrors do.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| AGENTS.md conforms to the map-not-encyclopedia shape — the exact mechanical invariant this ADR ships via gz validate --agents-md-map-conformance. | uv run gz validate --agents-md-map-conformance | 0 |

## Boundary Invariants

Structural fences this ADR's OBPIs must not cross — the proof channel for
`STRUCTURAL-FENCE` REQs per ADR-0.0.59:

- **The conformance validator is additive-only (REQ-0.0.54-03-06).** Shipping
  `gz validate --agents-md-map-conformance` (OBPI-03) MUST NOT modify the
  surfaces it audits: `AGENTS.md`, the OBPI-01 rule file
  (`.gzkit/rules/agents-md-map-doctrine.md`), and the OBPI-02 lift targets under
  `docs/governance/` are read-only to the validator increment. A validator that
  rewrites its own audit surface to make itself pass is the failure this fence
  forecloses.

## Consequences

### Positive

1. **The OpenAI Harness Engineering "map, not encyclopedia" pattern lands as a foundation invariant for gzkit's per-turn context surface.** Future ADRs landing under this contract cannot accrete prose into AGENTS.md silently; the validator surfaces the violation, the `RemediationPayload` points at `/gz-context-diet`, the path of least resistance is the lift, not the in-place expansion.

2. **The per-turn context budget is halved (40k → 15k) for the file every agent reads first.** At Claude's 200k context (or Codex's larger window), shaving 15k off the per-turn AGENTS.md injection is ~7.5% per turn over a long session — compounding into hundreds of saved turns. The OpenAI thesis's *"context is a scarce resource"* claim becomes mechanically realized at the surface where the scarcity bites first.

3. **The existing `gz-context-diet` skill graduates from reactive cleanup to mechanical default.** Today: the skill exists, the operator invokes it occasionally, the file re-accretes between invocations. After this ADR: the validator fires on any commit that introduces a prohibited shape; the skill is the default `RemediationPayload.recovery`; the resting state of AGENTS.md is map-shaped.

4. **`docs/governance/agent-contract-rationale.md` becomes the encyclopedia gzkit has been informally building.** That file already received six lifts under prior GHIs (`§ Rationale for 1a`, `§ Anti-vibing mantra`, `§ Stdlib-First doctrine`, `§ Operator economy`, `§ Rationale for Behavior Rule 11`, `§ Attestation worked example`). This ADR completes the pattern: every rationale prose section now has a canonical home there or in the new sibling files; future lifts inherit the same destination convention.

5. **The doctrine extends naturally to CLAUDE.md and `.claude/rules/*.md`.** OBPI-04's audit applies the same shape rules to the parallel files; the per-file budget mechanism already exists; the validator's scope expands once with the new file globs. The lift discipline becomes a property of every instruction file in the repo, not just the universal one.

6. **Coupled-surface coherence (DO IT RIGHT 1a) gains a structural defense at the AGENTS.md ↔ rationale-doc boundary.** Today, lifting a paragraph to `docs/governance/agent-contract-rationale.md` and leaving a stale reference in AGENTS.md is silent drift. After this ADR, the validator's resolve-every-link check (decision item 3, criterion c) surfaces every dangling reference at CI time. The `gz validate --cli-alignment` rule's pattern (every `gz <verb>` resolves) extends to every `See […](path)` link.

7. **Composability with the other two ADRs landing this session.** ADR-0.0.53's `RemediationPayload` provides the structured failure shape for the new validator. ADR-0.0.55's package-import-direction validator extends the *"every claim has a mechanical witness"* property to the import graph. Three foundation ADRs in one session, all reinforcing the same harness-engineering thesis: the OpenAI piece's *"constraints become multipliers"* claim compounds in gzkit's own substrate.

### Negative

1. **OBPI-02 (the lift) is a high-touch content edit affecting the most-read file in the repo.** **Pre-mortem scenario:** the lift inadvertently breaks a binding-bullet's meaning by moving the wrong paragraph or splitting a coupled bullet+example pair across files; agents reading post-lift AGENTS.md miss a constraint they were relying on. **Mitigation:** the lift table above is operator-reviewed before OBPI-02 executes; the lift preserves verbatim wording (no compression-by-summarization); the OBPI's regression test runs `gz validate --advisory-scorecard` against the lifted file to confirm every rule still resolves to a binding bullet. The reverse-direction "AGENTS.md still says X" coupling is structurally checked by the validator's link-resolution criterion.

2. **The 15k budget target may force a second lift pass if the first lift overruns.** **Pre-mortem scenario:** OBPI-02 completes; the post-lift AGENTS.md is 17k chars (over the new budget); the validator rejects the file. The operator must choose between (a) tightening the lift further (risk of lossy compression), (b) amending the budget upward (15k → 18k), or (c) returning to OBPI-02 for another pass. **Mitigation:** the budget is set in `data/instructions_files_budget.json` and amendable under an OBPI receipt without re-authoring this ADR; the operator's stated preference was "moderate" with 15k as the first step, not the eternal floor. The pre-mortem outcome is one of three known options, each tractable.

3. **The validator's prohibited-shape detection is heuristic.** Detecting "multi-paragraph rationale prose" by line count is approximate; a 6-line binding-bullet exposition may falsely trigger a violation, while a cleverly-formatted prose block masquerading as bullets may slip through. **Pre-mortem scenario:** 6 months in, an author cleverly-formats their pedagogical insertion as a series of one-line bullets to bypass the validator; the file slowly accretes again under cover of bullet shape. **Mitigation:** the heuristic is the first line of defense; the operator's review (during OBPI ceremony) is the second; the `gz-context-diet` skill's manual audit (when invoked) is the third. The structural defense is sufficient to block accidental accretion; intentional adversarial accretion would require operator collusion, which is outside threat model.

4. **Reversibility: this is a one-way door at the file-shape level.** Once AGENTS.md is lifted and the validator binds the shape, the binding-bullets-and-links structure is the contract. Reversal in 18 months would require either an amendment ADR loosening the shape or a re-merge of the lifted content back into AGENTS.md. Justified by: the alternative is the indefinite encyclopedia-style accretion the OpenAI thesis names as a four-pattern failure mode; the asymmetry is intentional.

5. **CLAUDE.md tightening (4000 floor) may be unnecessary or insufficient depending on future model-specific guidance.** CLAUDE.md is currently 1378 chars; the 4000 floor leaves 2622 chars of headroom. **Pre-mortem scenario:** a future Claude-specific tuning ADR wants to add 3000 chars of binding guidance; the budget refuses; the operator has to amend before landing. **Mitigation:** the budget is amendable under any OBPI receipt without re-authoring this ADR; the 4000 floor is the operator's preferred starting point and not load-bearing.

6. **The lift introduces five new/expanded governance docs under `docs/governance/`.** **Pre-mortem scenario:** the encyclopedia accumulates the same accretion pathology that AGENTS.md previously had — each rationale doc grows by 50% over 18 months until *those* files are also encyclopedic. **Mitigation:** the rationale docs are *meant* to be encyclopedias; that's the doctrine's whole point (the encyclopedia exists so the map can stay small). Per-doc growth is acceptable; the doctrine's invariant binds AGENTS.md's shape, not the rationale docs'.

7. **The 2am operator scenario:** an operator on-call at 2am needs to add a critical new binding rule to AGENTS.md (e.g., a security-incident-response rule that just surfaced); the validator's per-bullet 3-line limit fights them. **Mitigation:** the per-bullet limit is heuristic, not binding — the validator emits a warning above 3 lines, not a hard rejection, for bullets in the binding-rule sections (PRIME DIRECTIVE, DO IT RIGHT, Behavior Rules). Hard rejection is reserved for the prohibited-subsection-title set (Worked example, Anti-patterns, etc.) where the intent is unambiguous. The 2am operator's new binding rule is a binding rule; it lands as a bullet; the bullet may exceed 3 lines if it must; the validator's warning surfaces in `gz check` output but does not block the merge. The structural defense is against *encyclopedic accretion of rationale*, not against *new binding rules*.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 1
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.54-01: Author map-not-encyclopedia doctrine + budget tightening + rule + scorecard + canonical doctrine doc
- [ ] OBPI-0.0.54-02: Lift named sections from AGENTS.md to `docs/governance/` per the TOC table (verbatim; no compression-by-summarization)
- [ ] OBPI-0.0.54-03: Ship `gz validate --agents-md-map-conformance` validator + tests + `gz check` integration + manpage
- [ ] OBPI-0.0.54-04: Apply doctrine to CLAUDE.md and `.claude/rules/*.md` + final budget amendments + runbook updates

## Q&A Transcript

<!-- Interview transcript preserved for context -->

**Operator framing:** Discussion of OpenAI's "Harness Engineering" thesis (2026-02-11) surfaced *"map, not encyclopedia"* as the named failure-pattern remediation. The operator named the gap directly during analysis: gzkit already does encyclopedia-style accretion; the existing `gz-context-diet` skill is reactive; the file re-accretes between invocations.

**Bounded decision (AGENTS.md target tightness):** Three options surfaced — (a) Aggressive ~100 lines / ~8k chars (OpenAI sweet spot), (b) **Moderate ~200 lines / ~15k chars (operator-selected)**, (c) Light keep ~390 lines with per-section caps. Operator selected **Moderate** with rationale: halve current weight while preserving binding-bullet density gzkit has accreted; empirically achievable in one diet pass; preserves operator's recent additions.

**Pre-authoring empirical state:** AGENTS.md 390 lines / 30,924 chars (within 40k budget). CLAUDE.md 27 lines / 1,378 chars (well under 40k budget). `.claude/rules/*.md` files capped at 16k per file (current max ~15k). The lift target `docs/governance/agent-contract-rationale.md` already exists with six previously-lifted sections from prior GHIs.

**Target TOC**: see § Intent table above. Section-by-section action items with action codes (KEEP / LIFT). Operator confirmation captured in this ADR's authoring transcript; further per-section verification happens during OBPI-02 ceremony.

**OBPI brief authoring deferral (explicit annotation):** The 4 OBPIs declared in this ADR's Checklist (OBPI-0.0.54-01 through -04) are listed as canonical decomposition items, but their per-brief authoring under `gz-obpi-specify` is **deferred to a follow-up session** and tracked under **GHI #499** (sibling-class to GHI #495 — ADR-0.0.37 unindividualized scaffold state). The 1:1 Synchronization Mandate is satisfied at the Checklist level; the `obpis/` subdirectory populates under GHI #499's follow-up authoring passes before this ADR's promotion from Draft to Proposed.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_agents_md_map_conformance.py`, `tests/governance/test_lifted_section_links.py` (link-resolution against lifted docs), `tests/governance/test_instructions_budget_amendment.py` (budget change is recorded)
- [ ] Rule file: `.gzkit/rules/agents-md-map-doctrine.md` (body version `0.1.0`)
- [ ] Doctrine doc: `docs/governance/agents-md-doctrine.md` (canonical expansion)
- [ ] Lifted sections: `docs/governance/agent-contract-rationale.md` (expanded), `docs/governance/prime-directive.md` (new), `docs/governance/behavior-rules.md` (new), `docs/governance/skills-catalog.md` (new, auto-regenerated), `docs/governance/obpi-attestation.md` (new)
- [ ] Budget: `data/instructions_files_budget.json` (AGENTS.md 40000 → 15000; CLAUDE.md 40000 → 4000)
- [ ] Scorecard: `docs/governance/advisory-rules-audit.md` entry (Mechanical for shape; Judgment for per-section size targets)
- [ ] Docs: `docs/user/manpages/validate.md` (new `--agents-md-map-conformance` scope), `docs/governance/governance_runbook.md` § Instruction files, `docs/user/runbook.md` § Recovery flows

## Alternatives Considered

**Alt 1: Aggressive ~100 lines / ~8k chars target (OpenAI sweet spot).** Maximally on-doctrine. Rejected by operator selection ("Moderate" preferred) with rationale that some binding rules in gzkit's current AGENTS.md may resist compression into a single line and need careful rehoming; aggressive target risks lossy compression of binding semantics in one pass. Defer aggressive target to a future amendment OBPI once moderate target proves sustainable.

**Alt 2: Light keep ~390 lines with per-section caps.** Lowest-disruption. Rejected because it doesn't realize the OpenAI thesis — context-weight per turn stays high; the doctrinal default remains encyclopedia-style; the reactive `gz-context-diet` skill remains the only defense; the shape-as-invariant property is never established.

**Alt 3: Author the validator but defer the lift.** Author `gz validate --agents-md-map-conformance` and run it against the existing AGENTS.md; let the validator's warnings drive a slow-burn lift over many subsequent ADRs. Rejected because (a) the warnings would fire constantly against the existing prohibited shapes, producing the same desensitization pattern ADR-0.0.55's pre-mortem #5 names; (b) the validator's happy-path test would have no green-path file to assert against until the lift completes; (c) the lift's verbatim-preservation discipline is best done in one curated pass rather than piecemeal under unrelated ADRs.

**Alt 4: Lift to a single mega-doc `docs/governance/agent-contract-encyclopedia.md`.** Rather than the five-target lift (`agent-contract-rationale.md` expanded + `prime-directive.md` new + `behavior-rules.md` new + `skills-catalog.md` new + `obpi-attestation.md` new), lift everything to one large rationale doc. Rejected because (a) the encyclopedia itself becomes an accretion target without per-topic separation; (b) the link surface (`See [doc] § X`) is denser with per-topic destinations; (c) auto-regeneration of `skills-catalog.md` from `.gzkit/manifest.json` requires its own file by definition.

**Alt 5: Skip CLAUDE.md and `.claude/rules/*.md` from the doctrine.** Apply only to AGENTS.md. Rejected because (a) CLAUDE.md is the model-specific harness file; the shape doctrine that binds AGENTS.md naturally extends to its model-specific siblings; (b) `.claude/rules/*.md` files already carry the same encyclopedia-risk pattern (max ~15k chars per file); applying the doctrine universally is the OpenAI thesis's *"single map, deep encyclopedia"* property at full scope.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.54 | Completed - Partial: Completed - Partial: map-shape enforcement (validator + prohibited-shape/paragraph/link/budget checks) delivered and wired into gz check; the 15k weight-halving is deferred to GHI #533 / ADR-0.0.37. Truthfulness corrections applied at closeout (false enforced-budget surfaces repointed to live JSON; false OBPI-02 under-budget attestation line annotated). Receipts: arb-ruff-c75d8372eca94746a2719ccda00a461a, arb-step-typecheck-b160b00c929045c7bff98ee27a2f3794, arb-step-unittest-48a0ef68f210402a8bb79c98c99cb279, arb-step-mkdocs-703e8f80b8e143eeab9954ee936eb790 | g0 | 2026-07-12 | Completed - Partial: map-shape enforcement (validator + prohibited-shape/paragraph/link/budget checks) delivered and wired into gz check; the 15k weight-halving is deferred to GHI #533 / ADR-0.0.37. Truthfulness corrections applied at closeout (false enforced-budget surfaces repointed to live JSON; false OBPI-02 under-budget attestation line annotated). Receipts: arb-ruff-c75d8372eca94746a2719ccda00a461a, arb-step-typecheck-b160b00c929045c7bff98ee27a2f3794, arb-step-unittest-48a0ef68f210402a8bb79c98c99cb279, arb-step-mkdocs-703e8f80b8e143eeab9954ee936eb790 |
