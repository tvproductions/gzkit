---
id: ADR-0.0.22-security-sensitivity-doctrine
status: Proposed
kind: foundation
semver: 0.0.22
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-24
dependencies:
  - ADR-0.0.18
  - ADR-0.0.17
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.22: Security Sensitivity Doctrine

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats AI-authored work touching credential, subprocess, crypto, auth, boundary, ledger-integrity, and ARB-receipt-chain surfaces as a first-class fabrication-vector class rather than a code-quality concern. Distinguishes the doctrine (this ADR — what classification is required and why) from the toolchain (the feature ADR promoting `pool.agentic-security-review` — which scanner produces the receipt). The 2am-operator rubric applies: at 2am, an operator authoring a brief that touches `src/` runs `gz validate --sensitivity --explain` against their proposed Allowed Paths and sees the classification verdict before committing. The pressure-relief valve is predictive, not a runtime bypass — fail-closed remains the posture even under operational pressure.

This ADR is a Foundation addition. Foundations codify app/system invariants — ADR-0.0.18 (taxonomy doctrine) and the GHI #290 closure (TTY+`ATTEST` gate at `_enforce_human_attestation_authenticity`) demonstrated that orthogonal axes (kind alongside lane) and mechanical attestation gates close fabrication-pathway classes that advisory prose cannot. This ADR extends the same pattern to security sensitivity: a third orthogonal axis with auto-detect floor + frontmatter escalation, mechanically enforced by `gz validate --sensitivity` and ORed into `_requires_human_obpi_attestation`.

## Intent

AI-generated code introduces security flaws at high rates — Veracode's 2026 study of 100+ LLMs across 211M lines reports 45% of AI-generated code contains security flaws, 86% failure on cross-site-scripting defenses, 88% on log injection, with hard-coded credentials appearing at twice the rate of human-authored code. gzkit's existing five-gate covenant verifies intent alignment, tests, docs, BDD, and human attestation, but has no mechanical surface that pattern-matches security-sensitive code paths or forces heightened review when AI agents author changes touching credential handling, subprocess invocation with user input, cryptographic primitives, authentication boundaries, external API surfaces, ledger integrity, or the ARB receipt chain. The fabrication-vector class GHI #290 closed for foundation-kind attestation (agent synthesizes a `human_attestation: true` receipt from a headless process) has a direct analogue at the security layer: an agent can author and self-attest a brief that introduces a hardcoded credential or an unsanitized subprocess call, and no gate fires because the existing kind/lane axes don't classify the work as security-sensitive. This ADR codifies the invariant that security-sensitivity is a third orthogonal classification axis alongside kind and lane, mechanically detected from Allowed Paths, escalatable but not escapable via frontmatter, and binding heightened Gate 5 rigor at the brief level regardless of lane or kind. The toolchain that produces the security scan receipt (bandit, semgrep, or successor) is deferred to the feature ADR that promotes ADR-pool.agentic-security-review — this foundation pins only the doctrine.

## Decision

Codify a third orthogonal classification axis `sensitivity` and mechanize it across schema, validate scope, audit OR, and Gate 5 evidence requirements.

**The invariant (canonical statement):** Briefs (and ADRs) carrying work that touches security-sensitive surfaces inherit heightened Gate 5 rigor regardless of lane or kind. `sensitivity` is a third orthogonal axis alongside `kind` (what the ADR is about) and `lane` (external-contract exposure). Permitted values: `security` or absent. Future axes (privacy, compliance, safety-critical) are separate foundation ADRs per YAGNI; this ADR establishes only the security axis.

**Hybrid auto-detect with escalate-not-escape:**
- `gz validate --sensitivity` intersects each brief's `## ALLOWED PATHS` glob list with a registered security-surface registry (`data/security_surfaces.json`).
- Any intersection forces `sensitivity: security` regardless of frontmatter (the auto-detect floor).
- Frontmatter MAY declare `sensitivity: security` when paths don't trigger detection (escalation channel for cases the registry misses, e.g. test fixtures for new auth flows under `tests/**`).
- Frontmatter MAY NOT declare a value lower than detected. Validator exits 3 on attempted escape.
- Same enforcement shape as `kind` (declared in frontmatter, validated by `gz validate --taxonomy`), with the auto-detect floor added on top.

**Brief-level attestation rigor (mirrors foundation-kind precedent from ADR-0.0.18):**
- A new function `_requires_security_review_attestation` at `src/gzkit/commands/adr_audit.py` returns True when the brief carries `sensitivity: security` (whether declared or auto-detected).
- This function ORs into the existing `_requires_human_obpi_attestation` predicate alongside the foundation-kind branch and the heavy-lane branch.
- A `lite + feature + sensitivity:security` brief is no longer self-closeable. Gate 5 human attestation is required at the brief level.
- The TTY + `ATTEST` confirmation gate at `_enforce_human_attestation_authenticity` (the GHI #290 closure) automatically applies because attestation is now required.

**Gate 5 evidence requirements:**
- Heightened attestation walkthrough: TTY + `ATTEST` prompt enumerates a security-specific checklist (credential handling reviewed, subprocess input validated, crypto choices justified, boundary validation confirmed). The walkthrough is enumerated in the rule file, not authored ad-hoc per brief.
- Scan receipt cited inline: attestation text MUST cite a fresh `arb-step-security-*` receipt produced by whatever scanner the feature ADR settles on. `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with the security-scan invocation slot; the slot is reserved by this ADR but the canonical command string is filled by the feature ADR that promotes the toolchain.
- Same shape as today's heavy-lane attestation pattern (canonical receipts cited + attestation text), with the security-specific walkthrough added.

**Scanner-unavailable failure mode:** Fail-closed. When the canonical security-scan command at `CANONICAL_STEP_COMMANDS` is unavailable or fails to produce a receipt, Gate 5 cannot pass for `sensitivity: security` briefs. The pressure-relief valve is the registry-explain CLI (`gz validate --sensitivity --explain ALLOWED_PATHS_LIST`) which lets operators predict classification before authoring — not a runtime bypass. Emergency hotfixes touching security surfaces still go through ceremony; gzkit's posture matches the rant's prescription that 'the AI wrote it' is not a defense at any time of day.

**Security-surface registry governance (`data/security_surfaces.json`):** Edits to the registry require a brief carrying `sensitivity: security` themselves. Self-bootstrapping after first commit: the initial registry lands as part of OBPI-02 with this ADR's own brief carrying the marker. Future expansions (a new module enters the security surface) are governed the same way the registry governs itself. This closes the bootstrap question 'who classifies the classifier' — the same rigor that classifies code into the registry classifies edits to the registry.

**Mechanical surfaces (what changes in code):**
- `src/gzkit/schemas/adr.json` and `src/gzkit/schemas/obpi.json`: add optional `sensitivity` enum field with values [`security`].
- `data/security_surfaces.json` (new): registry of glob patterns + category labels. Edits governed by the doctrine itself.
- `src/gzkit/governance/trust_audits.py`: add `validate_sensitivity_binding` for `gz validate --sensitivity` scope. Emits structured findings (file, declared_sensitivity, detected_sensitivity, intersecting_paths, registry_categories). Fail-closed (exit 3) on escape attempts and unwaived violations.
- `src/gzkit/commands/adr_audit.py`: add `_requires_security_review_attestation`; OR into `_requires_human_obpi_attestation` alongside the existing foundation-kind and heavy-lane branches.
- `src/gzkit/arb/validator.py`: extend `CANONICAL_STEP_COMMANDS` with the security-scan invocation slot (reserved name, command string filled by the toolchain feature ADR).
- `src/gzkit/commands/obpi_complete.py`: walkthrough prompt extension when the brief being completed carries `sensitivity: security`.
- `data/behave_coverage_waivers.json` extension: foundation OBPIs deferring BDD per existing pattern.
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.
- `.gzkit/rules/security-sensitivity.md` (new): canonical rule file declaring the invariant, the registry contract, the validate scope, the walkthrough enumeration, and the scanner-unavailable failure mode.
- `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix: add the third axis to the existing lane/kind matrix.

**Six OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.22-01 — Schema + frontmatter field (parallel-root):** Add `sensitivity` enum to `src/gzkit/schemas/adr.json` and `src/gzkit/schemas/obpi.json`; Pydantic model updates at `src/gzkit/models/`; table-driven TDD tests covering declared:absent, declared:security, malformed values; backwards-compatibility audit confirms ~150 existing briefs without the field validate as `sensitivity: null`.

**OBPI-0.0.22-02 — Security-surface registry (parallel-root, no dependency on 01):** Author `data/security_surfaces.json` with initial categories (credential_handling, subprocess_user_input, crypto_primitives, auth_boundaries, external_api_surfaces, ledger_integrity, arb_receipt_chain, secret_handling, deserialization_user_input); JSON schema fragment at `src/gzkit/schemas/security_surfaces.json`; Pydantic model `SecuritySurfaceEntry` with `ConfigDict(frozen=True, extra='forbid')`; governance contract documented (edits require `sensitivity: security` brief — self-bootstrapping); table-driven tests for glob matching, malformed entries, missing-category errors.

**OBPI-0.0.22-03 — `gz validate --sensitivity` scope (depends on OBPI-01 + OBPI-02):** `validate_sensitivity_binding` at `src/gzkit/governance/trust_audits.py`; CLI flag registration at `src/gzkit/cli/parser_validate.py`; `--explain ALLOWED_PATHS_LIST` subform for predictive classification (the 2am-operator pressure-relief valve); `--json` output supports machine consumption; auto-detect floor + escalate-not-escape rule mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover detection-floor-fires, frontmatter-escalation-allowed, frontmatter-escape-blocked, malformed-paths-tolerated, registry-missing-fail-closed.

**OBPI-0.0.22-04 — `_requires_security_review_attestation` audit OR (depends on OBPI-01):** Add function at `src/gzkit/commands/adr_audit.py`; OR into existing `_requires_human_obpi_attestation` alongside foundation-kind and heavy-lane branches; behavioral tests confirm `lite + feature + sensitivity:security` brief is not self-closeable; behavioral tests confirm the existing TTY + `ATTEST` gate at `_enforce_human_attestation_authenticity` activates correctly for security-sensitive briefs; matrix update at `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix.

**OBPI-0.0.22-05 — Gate 5 walkthrough extension + ARB canonical command slot (depends on OBPI-04):** Walkthrough prompt extension at `src/gzkit/commands/obpi_complete.py` when brief carries `sensitivity: security`; checklist enumerated in canonical rule file; `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with reserved security-scan slot (name only, command string deferred to toolchain feature ADR); fail-closed when scan receipt unavailable; behavioral tests confirm walkthrough fires, receipt-missing fails attestation, receipt-stale (>24h) fails attestation.

**OBPI-0.0.22-06 — Rule file + AGENTS.md matrix + advisory scorecard (depends on 03/04/05):** Author `.gzkit/rules/security-sensitivity.md` declaring invariant, registry contract, validate scope, walkthrough enumeration, scanner-unavailable failure mode; AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix authored; advisory-rules-audit.md scorecard entry (Mechanical); `gz agent sync control-surfaces` propagates rule to vendor mirrors; foundation-kind closeout walkthrough per ADR-0.0.18 (Lite-vs-Heavy lane does not exempt foundation doctrine — but this is heavy lane regardless).

**Parallelism:** {OBPI-01, OBPI-02} → OBPI-03 → {OBPI-04 → OBPI-05} → OBPI-06.

**Lane: Heavy.** Schema enum extension is a contract change; new validate scope is a CLI surface addition; audit OR changes Gate 5 semantics; ARB canonical command slot extends the receipt chain. All four trigger heavy-lane rigor per cli.md and gate5-runbook-code-covenant.md. Foundation-kind rigor stacks on top per ADR-0.0.18 (closeout walkthrough at brief level + ADR closeout).

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT author the security scanner toolchain (bandit/semgrep) — that's the feature ADR promoting `pool.agentic-security-review`.
- Does NOT author content-layer injection scanning — that's `pool.content-injection-scanning`, complementary attack surface.
- Does NOT add additional sensitivity values beyond `security` — privacy, compliance, safety-critical are separate foundation ADRs (YAGNI).
- Does NOT enforce separation-of-duties (attestor != implementer) — appealing but adds multi-agent coordination requirement; follow-up ADR if drift observed.
- Does NOT enforce allow-list expiry on the registry — registry edits are governed by the doctrine; no expiry mechanism in v1.
- Does NOT change the existing `kind` or `lane` axes — sensitivity is purely additive.

## Consequences

### Positive

1. Mechanical closure of the Veracode-class gap — the rant's strongest quantitative claim (45%/86%/88%) maps to a registered registry of security-sensitive paths and a fail-closed validate scope. The fabrication-vector pattern that GHI #290 closed for foundation-kind attestation now extends to the security layer.
2. Orthogonality preserved — `kind`, `lane`, and `sensitivity` are three independent axes that compose cleanly. No stacked meaning on a binary lane axis (rejected alternative #1); no breakage of the 5-gate covenant (rejected alternative #2). Each axis answers a different question.
3. Toolchain can evolve without reopening the foundation decision — bandit → semgrep → custom is a feature ADR concern; the doctrine is stable across toolchain shifts.
4. Mirrors the established foundation-kind precedent (ADR-0.0.18) — the OR pattern at `_requires_human_obpi_attestation` is the same shape, the TTY + `ATTEST` gate is the same closure, the matrix table is the same operator-facing surface. Cognitive surface stays consistent.
5. The security-surface registry is itself governed by the doctrine — self-bootstrapping closes 'who classifies the classifier' and avoids the human-vs-AI registry-authoring drift the pre-mortem flagged.
6. The `--explain` CLI gives operators predictive classification before authoring — the 2am operator can run `gz validate --sensitivity --explain` against a path list and see the classification verdict without committing. Reduces friction for the legitimate operator without opening a runtime bypass.
7. Pool ADR `pool.agentic-security-review` becomes the natural feature implementation — toolchain choices, severity thresholds, baseline suppression model live there, consuming this foundation's invariants.
8. AGENTS.md gains a third-axis matrix that ports cleanly to other GovZero-compliant repositories (the Linux Foundation agents.md/ standard already supports this content shape).

### Negative

1. Third axis to learn — operators authoring briefs now reason across `kind`, `lane`, and `sensitivity` simultaneously. Doc burden on AGENTS.md and runbook; cognitive burden on new contributors. Mitigation: the auto-detect floor means most operators encounter sensitivity only when paths trigger it; the matrix table makes the composition explicit.
2. Registry-staleness risk — `data/security_surfaces.json` becomes a stale rubber-stamp if not actively curated. New crypto modules added to `src/` without registry update produce false-negative classification. Mitigation: scorecard entry tracks the rule; `gz validate --advisory-scorecard` audits coverage; pre-mortem #1 flagged this as the highest-likelihood failure mode.
3. Schema migration burden — ~150 existing briefs gain an optional `sensitivity` field that defaults to absent. Backwards-compatibility audit required (OBPI-01); no behavioral change for briefs that don't touch security surfaces, but the schema validator must accept absent-field as `sensitivity: null`.
4. Attestation friction increases for any brief touching auth/crypto/credential code — operators authoring tests for new auth flows will see the walkthrough fire even on small TDD increments. Potential alarm-fatigue if false-positive rate is high (assumption-surfacing #4 flagged this). Mitigation: the registry is curated to favor true-positive signal; `--explain` lets operators predict before authoring.
5. Toolchain feature ADR must land within ~1 minor of this foundation — otherwise the canonical security-scan slot at `CANONICAL_STEP_COMMANDS` is reserved-but-empty and Gate 5 walkthrough is unmechanical (pre-mortem #1 flagged this). Mitigation: this ADR's closeout includes a forcing function to schedule the toolchain feature ADR.
6. Fail-closed posture means scanner outages block ceremony — operator at 2am with broken scanner cannot ship a security-sensitive hotfix through the normal path. The `--explain` valve is for prediction, not bypass. Acceptable per the rant's posture and per gzkit's existing fail-closed history (Gate 5 doesn't relax for headless processes either). Mitigation: registry curation discipline reduces false-classification; scanner reliability is a feature-ADR concern.
7. Foundation-kind closeout ceremony overhead — heavy lane plus foundation kind plus sensitivity:security stacks attestation discipline. Real cost but proportional to the invariant's weight.
8. Self-bootstrapping registry governance creates a cold-start question — the very first edit to `data/security_surfaces.json` (OBPI-02) cannot itself carry `sensitivity: security` because the registry doesn't exist yet. Resolved by the foundation ADR's own brief carrying the marker (declared, not auto-detected, since the registry isn't authored until OBPI-02 commits) — a one-time bootstrap exception documented in the rule file.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.22-01: Schema + frontmatter field — Add `sensitivity` enum to adr.json and obpi.json schemas; Pydantic model updates; table-driven TDD tests (declared:absent, declared:security, malformed); backwards-compatibility audit on ~150 existing briefs.
- [ ] OBPI-0.0.22-02: Security-surface registry — Author `data/security_surfaces.json` with 9 initial categories; JSON schema fragment; Pydantic `SecuritySurfaceEntry` model with frozen+forbid; governance contract documented (self-bootstrapping); glob-matching tests.
- [ ] OBPI-0.0.22-03: `gz validate --sensitivity` scope — `validate_sensitivity_binding` at trust_audits.py; CLI flag registration; `--explain` subform for predictive classification; `--json` machine output; auto-detect floor + escalate-not-escape mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover floor-fires, escalation-allowed, escape-blocked, registry-missing-fail-closed.
- [ ] OBPI-0.0.22-04: `_requires_security_review_attestation` audit OR — Function at adr_audit.py; OR into `_requires_human_obpi_attestation`; behavioral tests confirm lite+feature+security brief not self-closeable; TTY+ATTEST gate activates correctly; matrix update at AGENTS.md.
- [ ] OBPI-0.0.22-05: Gate 5 walkthrough extension + ARB canonical command slot — Walkthrough prompt at obpi_complete.py; checklist in rule file; `CANONICAL_STEP_COMMANDS` extends with reserved security-scan slot; fail-closed when receipt unavailable; behavioral tests for walkthrough-fires, receipt-missing, receipt-stale.
- [ ] OBPI-0.0.22-06: Rule file + AGENTS.md matrix + advisory scorecard — Author `.gzkit/rules/security-sensitivity.md`; AGENTS.md three-axis matrix; advisory-rules-audit.md scorecard entry (Mechanical); `gz agent sync control-surfaces` propagates to mirrors; foundation-kind closeout walkthrough per ADR-0.0.18.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-24T19:14:04.628857*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.22

### Q: What is the title of this ADR?

**A:** Security Sensitivity Doctrine

### Q: What is the semantic version?

**A:** 0.0.22

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** AI-generated code introduces security flaws at high rates — Veracode's 2026 study of 100+ LLMs across 211M lines reports 45% of AI-generated code contains security flaws, 86% failure on cross-site-scripting defenses, 88% on log injection, with hard-coded credentials appearing at twice the rate of human-authored code. gzkit's existing five-gate covenant verifies intent alignment, tests, docs, BDD, and human attestation, but has no mechanical surface that pattern-matches security-sensitive code paths or forces heightened review when AI agents author changes touching credential handling, subprocess invocation with user input, cryptographic primitives, authentication boundaries, external API surfaces, ledger integrity, or the ARB receipt chain. The fabrication-vector class GHI #290 closed for foundation-kind attestation (agent synthesizes a `human_attestation: true` receipt from a headless process) has a direct analogue at the security layer: an agent can author and self-attest a brief that introduces a hardcoded credential or an unsanitized subprocess call, and no gate fires because the existing kind/lane axes don't classify the work as security-sensitive. This ADR codifies the invariant that security-sensitivity is a third orthogonal classification axis alongside kind and lane, mechanically detected from Allowed Paths, escalatable but not escapable via frontmatter, and binding heightened Gate 5 rigor at the brief level regardless of lane or kind. The toolchain that produces the security scan receipt (bandit, semgrep, or successor) is deferred to the feature ADR that promotes ADR-pool.agentic-security-review — this foundation pins only the doctrine.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify a third orthogonal classification axis `sensitivity` and mechanize it across schema, validate scope, audit OR, and Gate 5 evidence requirements.

**The invariant (canonical statement):** Briefs (and ADRs) carrying work that touches security-sensitive surfaces inherit heightened Gate 5 rigor regardless of lane or kind. `sensitivity` is a third orthogonal axis alongside `kind` (what the ADR is about) and `lane` (external-contract exposure). Permitted values: `security` or absent. Future axes (privacy, compliance, safety-critical) are separate foundation ADRs per YAGNI; this ADR establishes only the security axis.

**Hybrid auto-detect with escalate-not-escape:**
- `gz validate --sensitivity` intersects each brief's `## ALLOWED PATHS` glob list with a registered security-surface registry (`data/security_surfaces.json`).
- Any intersection forces `sensitivity: security` regardless of frontmatter (the auto-detect floor).
- Frontmatter MAY declare `sensitivity: security` when paths don't trigger detection (escalation channel for cases the registry misses, e.g. test fixtures for new auth flows under `tests/**`).
- Frontmatter MAY NOT declare a value lower than detected. Validator exits 3 on attempted escape.
- Same enforcement shape as `kind` (declared in frontmatter, validated by `gz validate --taxonomy`), with the auto-detect floor added on top.

**Brief-level attestation rigor (mirrors foundation-kind precedent from ADR-0.0.18):**
- A new function `_requires_security_review_attestation` at `src/gzkit/commands/adr_audit.py` returns True when the brief carries `sensitivity: security` (whether declared or auto-detected).
- This function ORs into the existing `_requires_human_obpi_attestation` predicate alongside the foundation-kind branch and the heavy-lane branch.
- A `lite + feature + sensitivity:security` brief is no longer self-closeable. Gate 5 human attestation is required at the brief level.
- The TTY + `ATTEST` confirmation gate at `_enforce_human_attestation_authenticity` (the GHI #290 closure) automatically applies because attestation is now required.

**Gate 5 evidence requirements:**
- Heightened attestation walkthrough: TTY + `ATTEST` prompt enumerates a security-specific checklist (credential handling reviewed, subprocess input validated, crypto choices justified, boundary validation confirmed). The walkthrough is enumerated in the rule file, not authored ad-hoc per brief.
- Scan receipt cited inline: attestation text MUST cite a fresh `arb-step-security-*` receipt produced by whatever scanner the feature ADR settles on. `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with the security-scan invocation slot; the slot is reserved by this ADR but the canonical command string is filled by the feature ADR that promotes the toolchain.
- Same shape as today's heavy-lane attestation pattern (canonical receipts cited + attestation text), with the security-specific walkthrough added.

**Scanner-unavailable failure mode:** Fail-closed. When the canonical security-scan command at `CANONICAL_STEP_COMMANDS` is unavailable or fails to produce a receipt, Gate 5 cannot pass for `sensitivity: security` briefs. The pressure-relief valve is the registry-explain CLI (`gz validate --sensitivity --explain ALLOWED_PATHS_LIST`) which lets operators predict classification before authoring — not a runtime bypass. Emergency hotfixes touching security surfaces still go through ceremony; gzkit's posture matches the rant's prescription that 'the AI wrote it' is not a defense at any time of day.

**Security-surface registry governance (`data/security_surfaces.json`):** Edits to the registry require a brief carrying `sensitivity: security` themselves. Self-bootstrapping after first commit: the initial registry lands as part of OBPI-02 with this ADR's own brief carrying the marker. Future expansions (a new module enters the security surface) are governed the same way the registry governs itself. This closes the bootstrap question 'who classifies the classifier' — the same rigor that classifies code into the registry classifies edits to the registry.

**Mechanical surfaces (what changes in code):**
- `src/gzkit/schemas/adr.json` and `src/gzkit/schemas/obpi.json`: add optional `sensitivity` enum field with values [`security`].
- `data/security_surfaces.json` (new): registry of glob patterns + category labels. Edits governed by the doctrine itself.
- `src/gzkit/governance/trust_audits.py`: add `validate_sensitivity_binding` for `gz validate --sensitivity` scope. Emits structured findings (file, declared_sensitivity, detected_sensitivity, intersecting_paths, registry_categories). Fail-closed (exit 3) on escape attempts and unwaived violations.
- `src/gzkit/commands/adr_audit.py`: add `_requires_security_review_attestation`; OR into `_requires_human_obpi_attestation` alongside the existing foundation-kind and heavy-lane branches.
- `src/gzkit/arb/validator.py`: extend `CANONICAL_STEP_COMMANDS` with the security-scan invocation slot (reserved name, command string filled by the toolchain feature ADR).
- `src/gzkit/commands/obpi_complete.py`: walkthrough prompt extension when the brief being completed carries `sensitivity: security`.
- `data/behave_coverage_waivers.json` extension: foundation OBPIs deferring BDD per existing pattern.
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.
- `.gzkit/rules/security-sensitivity.md` (new): canonical rule file declaring the invariant, the registry contract, the validate scope, the walkthrough enumeration, and the scanner-unavailable failure mode.
- `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix: add the third axis to the existing lane/kind matrix.

**Six OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.22-01 — Schema + frontmatter field (parallel-root):** Add `sensitivity` enum to `src/gzkit/schemas/adr.json` and `src/gzkit/schemas/obpi.json`; Pydantic model updates at `src/gzkit/models/`; table-driven TDD tests covering declared:absent, declared:security, malformed values; backwards-compatibility audit confirms ~150 existing briefs without the field validate as `sensitivity: null`.

**OBPI-0.0.22-02 — Security-surface registry (parallel-root, no dependency on 01):** Author `data/security_surfaces.json` with initial categories (credential_handling, subprocess_user_input, crypto_primitives, auth_boundaries, external_api_surfaces, ledger_integrity, arb_receipt_chain, secret_handling, deserialization_user_input); JSON schema fragment at `src/gzkit/schemas/security_surfaces.json`; Pydantic model `SecuritySurfaceEntry` with `ConfigDict(frozen=True, extra='forbid')`; governance contract documented (edits require `sensitivity: security` brief — self-bootstrapping); table-driven tests for glob matching, malformed entries, missing-category errors.

**OBPI-0.0.22-03 — `gz validate --sensitivity` scope (depends on OBPI-01 + OBPI-02):** `validate_sensitivity_binding` at `src/gzkit/governance/trust_audits.py`; CLI flag registration at `src/gzkit/cli/parser_validate.py`; `--explain ALLOWED_PATHS_LIST` subform for predictive classification (the 2am-operator pressure-relief valve); `--json` output supports machine consumption; auto-detect floor + escalate-not-escape rule mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover detection-floor-fires, frontmatter-escalation-allowed, frontmatter-escape-blocked, malformed-paths-tolerated, registry-missing-fail-closed.

**OBPI-0.0.22-04 — `_requires_security_review_attestation` audit OR (depends on OBPI-01):** Add function at `src/gzkit/commands/adr_audit.py`; OR into existing `_requires_human_obpi_attestation` alongside foundation-kind and heavy-lane branches; behavioral tests confirm `lite + feature + sensitivity:security` brief is not self-closeable; behavioral tests confirm the existing TTY + `ATTEST` gate at `_enforce_human_attestation_authenticity` activates correctly for security-sensitive briefs; matrix update at `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix.

**OBPI-0.0.22-05 — Gate 5 walkthrough extension + ARB canonical command slot (depends on OBPI-04):** Walkthrough prompt extension at `src/gzkit/commands/obpi_complete.py` when brief carries `sensitivity: security`; checklist enumerated in canonical rule file; `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with reserved security-scan slot (name only, command string deferred to toolchain feature ADR); fail-closed when scan receipt unavailable; behavioral tests confirm walkthrough fires, receipt-missing fails attestation, receipt-stale (>24h) fails attestation.

**OBPI-0.0.22-06 — Rule file + AGENTS.md matrix + advisory scorecard (depends on 03/04/05):** Author `.gzkit/rules/security-sensitivity.md` declaring invariant, registry contract, validate scope, walkthrough enumeration, scanner-unavailable failure mode; AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix authored; advisory-rules-audit.md scorecard entry (Mechanical); `gz agent sync control-surfaces` propagates rule to vendor mirrors; foundation-kind closeout walkthrough per ADR-0.0.18 (Lite-vs-Heavy lane does not exempt foundation doctrine — but this is heavy lane regardless).

**Parallelism:** {OBPI-01, OBPI-02} → OBPI-03 → {OBPI-04 → OBPI-05} → OBPI-06.

**Lane: Heavy.** Schema enum extension is a contract change; new validate scope is a CLI surface addition; audit OR changes Gate 5 semantics; ARB canonical command slot extends the receipt chain. All four trigger heavy-lane rigor per cli.md and gate5-runbook-code-covenant.md. Foundation-kind rigor stacks on top per ADR-0.0.18 (closeout walkthrough at brief level + ADR closeout).

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT author the security scanner toolchain (bandit/semgrep) — that's the feature ADR promoting `pool.agentic-security-review`.
- Does NOT author content-layer injection scanning — that's `pool.content-injection-scanning`, complementary attack surface.
- Does NOT add additional sensitivity values beyond `security` — privacy, compliance, safety-critical are separate foundation ADRs (YAGNI).
- Does NOT enforce separation-of-duties (attestor != implementer) — appealing but adds multi-agent coordination requirement; follow-up ADR if drift observed.
- Does NOT enforce allow-list expiry on the registry — registry edits are governed by the doctrine; no expiry mechanism in v1.
- Does NOT change the existing `kind` or `lane` axes — sensitivity is purely additive.

### Q: What good things result from this decision? List benefits.

**A:** 1. Mechanical closure of the Veracode-class gap — the rant's strongest quantitative claim (45%/86%/88%) maps to a registered registry of security-sensitive paths and a fail-closed validate scope. The fabrication-vector pattern that GHI #290 closed for foundation-kind attestation now extends to the security layer.
2. Orthogonality preserved — `kind`, `lane`, and `sensitivity` are three independent axes that compose cleanly. No stacked meaning on a binary lane axis (rejected alternative #1); no breakage of the 5-gate covenant (rejected alternative #2). Each axis answers a different question.
3. Toolchain can evolve without reopening the foundation decision — bandit → semgrep → custom is a feature ADR concern; the doctrine is stable across toolchain shifts.
4. Mirrors the established foundation-kind precedent (ADR-0.0.18) — the OR pattern at `_requires_human_obpi_attestation` is the same shape, the TTY + `ATTEST` gate is the same closure, the matrix table is the same operator-facing surface. Cognitive surface stays consistent.
5. The security-surface registry is itself governed by the doctrine — self-bootstrapping closes 'who classifies the classifier' and avoids the human-vs-AI registry-authoring drift the pre-mortem flagged.
6. The `--explain` CLI gives operators predictive classification before authoring — the 2am operator can run `gz validate --sensitivity --explain` against a path list and see the classification verdict without committing. Reduces friction for the legitimate operator without opening a runtime bypass.
7. Pool ADR `pool.agentic-security-review` becomes the natural feature implementation — toolchain choices, severity thresholds, baseline suppression model live there, consuming this foundation's invariants.
8. AGENTS.md gains a third-axis matrix that ports cleanly to other GovZero-compliant repositories (the Linux Foundation agents.md/ standard already supports this content shape).

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Third axis to learn — operators authoring briefs now reason across `kind`, `lane`, and `sensitivity` simultaneously. Doc burden on AGENTS.md and runbook; cognitive burden on new contributors. Mitigation: the auto-detect floor means most operators encounter sensitivity only when paths trigger it; the matrix table makes the composition explicit.
2. Registry-staleness risk — `data/security_surfaces.json` becomes a stale rubber-stamp if not actively curated. New crypto modules added to `src/` without registry update produce false-negative classification. Mitigation: scorecard entry tracks the rule; `gz validate --advisory-scorecard` audits coverage; pre-mortem #1 flagged this as the highest-likelihood failure mode.
3. Schema migration burden — ~150 existing briefs gain an optional `sensitivity` field that defaults to absent. Backwards-compatibility audit required (OBPI-01); no behavioral change for briefs that don't touch security surfaces, but the schema validator must accept absent-field as `sensitivity: null`.
4. Attestation friction increases for any brief touching auth/crypto/credential code — operators authoring tests for new auth flows will see the walkthrough fire even on small TDD increments. Potential alarm-fatigue if false-positive rate is high (assumption-surfacing #4 flagged this). Mitigation: the registry is curated to favor true-positive signal; `--explain` lets operators predict before authoring.
5. Toolchain feature ADR must land within ~1 minor of this foundation — otherwise the canonical security-scan slot at `CANONICAL_STEP_COMMANDS` is reserved-but-empty and Gate 5 walkthrough is unmechanical (pre-mortem #1 flagged this). Mitigation: this ADR's closeout includes a forcing function to schedule the toolchain feature ADR.
6. Fail-closed posture means scanner outages block ceremony — operator at 2am with broken scanner cannot ship a security-sensitive hotfix through the normal path. The `--explain` valve is for prediction, not bypass. Acceptable per the rant's posture and per gzkit's existing fail-closed history (Gate 5 doesn't relax for headless processes either). Mitigation: registry curation discipline reduces false-classification; scanner reliability is a feature-ADR concern.
7. Foundation-kind closeout ceremony overhead — heavy lane plus foundation kind plus sensitivity:security stacks attestation discipline. Real cost but proportional to the invariant's weight.
8. Self-bootstrapping registry governance creates a cold-start question — the very first edit to `data/security_surfaces.json` (OBPI-02) cannot itself carry `sensitivity: security` because the registry doesn't exist yet. Resolved by the foundation ADR's own brief carrying the marker (declared, not auto-detected, since the registry isn't authored until OBPI-02 commits) — a one-time bootstrap exception documented in the rule file.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Schema + frontmatter field — Add `sensitivity` enum to adr.json and obpi.json schemas; Pydantic model updates; table-driven TDD tests (declared:absent, declared:security, malformed); backwards-compatibility audit on ~150 existing briefs
2. Security-surface registry — Author `data/security_surfaces.json` with 9 initial categories; JSON schema fragment; Pydantic SecuritySurfaceEntry model with frozen+forbid; governance contract documented (self-bootstrapping); glob-matching tests
3. `gz validate --sensitivity` scope — `validate_sensitivity_binding` at trust_audits.py; CLI flag registration; `--explain` subform for predictive classification; `--json` machine output; auto-detect floor + escalate-not-escape mechanically enforced; integrates into `gz validate --all` and `gz check`; TDD tests cover floor-fires, escalation-allowed, escape-blocked, registry-missing-fail-closed
4. `_requires_security_review_attestation` audit OR — Function at adr_audit.py; OR into `_requires_human_obpi_attestation`; behavioral tests confirm lite+feature+security brief not self-closeable; TTY+ATTEST gate activates correctly; matrix update at AGENTS.md
5. Gate 5 walkthrough extension + ARB canonical command slot — Walkthrough prompt at obpi_complete.py; checklist in rule file; `CANONICAL_STEP_COMMANDS` extends with reserved security-scan slot; fail-closed when receipt unavailable; behavioral tests for walkthrough-fires, receipt-missing, receipt-stale
6. Rule file + AGENTS.md matrix + advisory scorecard — Author `.gzkit/rules/security-sensitivity.md`; AGENTS.md three-axis matrix; advisory-rules-audit.md scorecard entry (Mechanical); `gz agent sync control-surfaces` propagates to mirrors; foundation-kind closeout walkthrough per ADR-0.0.18

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Lane modifier (`heavy+security` tier in existing lane axis)** — extend the lane enum with a security qualifier rather than introduce a third axis. REJECTED: stacks meaning onto a binary axis that operators have learned as lite/heavy. Loses the orthogonality property — `kind` answers what the ADR is about, `lane` answers external-contract exposure, `sensitivity` answers what class of failure dominates. Conflating sensitivity with lane forces every future axis (privacy, compliance) into the same lane field, producing a combinatorial enum (`heavy+security+privacy+compliance`) that is unreadable. The orthogonal-axis pattern that worked for `kind` (ADR-0.0.17/18) is the right precedent.

2. **New gate (Gate 6 — Security Review)** — add a sixth gate to the covenant with its own pass/fail state in `gz gates`. REJECTED: breaks the 5-gate covenant's stability. Every downstream skill, manpage, runbook, and AGENTS.md reference cites 'Gate 5 human attests' as the terminal gate. Gate 6 cascades through ~30 documentation surfaces and ~15 skill files. The 5-gate model is itself foundational (ADR-0.0.1 lineage); changing it requires a much heavier doctrine shift than this ADR's scope. Gate 5 augmentation (heightened walkthrough + scan receipt) achieves the same outcome without the cascade.

3. **Author-declared frontmatter only (no auto-detect)** — `sensitivity: security` is purely a frontmatter field set by the brief author; validator only checks that declared briefs follow the rules. REJECTED: reproduces the self-classification fabrication vector this ADR exists to close. An AI agent authoring a brief that touches credential code can omit the `sensitivity` field and the validator sees nothing wrong. The whole rant is about AI agents producing security-flawed code; trusting them to self-classify the work as security-sensitive is exactly the failure mode. Auto-detect from Allowed Paths gives the mechanical backstop the rant's posture demands.

4. **Pure auto-detect (no escalation channel)** — `sensitivity` is computed entirely from the path-glob intersection; frontmatter cannot override or escalate. REJECTED: loses the ability to flag legitimate cases the registry misses. A brief that touches `tests/**` to author fixtures for a new auth flow doesn't intersect the registered surfaces (which target `src/**`), but the work warrants security treatment. Auto-detect-only forces the registry to enumerate every test path that mirrors a security surface — the registry becomes its own consistency burden. Escalate-not-escape gives operators the narrow override channel without opening a bypass.

5. **Heightened attestation only (no scan receipt requirement)** — Gate 5 walkthrough enumerates the security checklist; no requirement to cite a fresh `arb-step-security-*` receipt. REJECTED: reproduces the GHI #290 fabrication-pathway shape at the security layer. An agent can synthesize a 'yes I reviewed crypto choices' walkthrough as easily as it can synthesize a foundation-kind attestation; the TTY+ATTEST confirmation closes that for human presence but not for actual scan-evidence depth. Scanner output (true-positive findings) is the mechanical backstop that human attention alone can't provide. Pairing both — receipt cited inline AND heightened walkthrough — mirrors today's heavy-lane shape and gives both mechanical and judgment evidence.

6. **Single foundation ADR absorbing toolchain (this ADR + bandit/semgrep + scoring + suppression model)** — collapse doctrine and toolchain into one ADR. REJECTED: conflates two decisions with different lifetimes. Doctrine should be stable (the invariant 'security work needs heightened review' is unlikely to change); toolchain choices evolve (bandit, semgrep, custom). Mixing them means every toolchain refresh reopens the doctrine, and every doctrine clarification forces a toolchain re-evaluation. The clean layering — foundation pins doctrine, feature ADR (promoting `pool.agentic-security-review`) pins toolchain — keeps each decision in scope.

7. **Promote `pool.agentic-security-review` directly to a feature ADR (skip foundation layer)** — fold the doctrine inline into the toolchain ADR's Rationale. REJECTED in design dialogue: foundation-kind is the right home for 'this class of code requires this class of review' — that's an invariant codifying app/system identity, not a release-carrying capability. Foundation lets the lane-matrix mechanism be reused across future axes (privacy, compliance) without reopening the toolchain ADR. The user explicitly accepted the foundation-first layering when offered the choice between options #1 and #2.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Lane modifier (`heavy+security` tier in existing lane axis)** — extend the lane enum with a security qualifier rather than introduce a third axis. REJECTED: stacks meaning onto a binary axis that operators have learned as lite/heavy. Loses the orthogonality property — `kind` answers what the ADR is about, `lane` answers external-contract exposure, `sensitivity` answers what class of failure dominates. Conflating sensitivity with lane forces every future axis (privacy, compliance) into the same lane field, producing a combinatorial enum (`heavy+security+privacy+compliance`) that is unreadable. The orthogonal-axis pattern that worked for `kind` (ADR-0.0.17/18) is the right precedent.

2. **New gate (Gate 6 — Security Review)** — add a sixth gate to the covenant with its own pass/fail state in `gz gates`. REJECTED: breaks the 5-gate covenant's stability. Every downstream skill, manpage, runbook, and AGENTS.md reference cites 'Gate 5 human attests' as the terminal gate. Gate 6 cascades through ~30 documentation surfaces and ~15 skill files. The 5-gate model is itself foundational (ADR-0.0.1 lineage); changing it requires a much heavier doctrine shift than this ADR's scope. Gate 5 augmentation (heightened walkthrough + scan receipt) achieves the same outcome without the cascade.

3. **Author-declared frontmatter only (no auto-detect)** — `sensitivity: security` is purely a frontmatter field set by the brief author; validator only checks that declared briefs follow the rules. REJECTED: reproduces the self-classification fabrication vector this ADR exists to close. An AI agent authoring a brief that touches credential code can omit the `sensitivity` field and the validator sees nothing wrong. The whole rant is about AI agents producing security-flawed code; trusting them to self-classify the work as security-sensitive is exactly the failure mode. Auto-detect from Allowed Paths gives the mechanical backstop the rant's posture demands.

4. **Pure auto-detect (no escalation channel)** — `sensitivity` is computed entirely from the path-glob intersection; frontmatter cannot override or escalate. REJECTED: loses the ability to flag legitimate cases the registry misses. A brief that touches `tests/**` to author fixtures for a new auth flow doesn't intersect the registered surfaces (which target `src/**`), but the work warrants security treatment. Auto-detect-only forces the registry to enumerate every test path that mirrors a security surface — the registry becomes its own consistency burden. Escalate-not-escape gives operators the narrow override channel without opening a bypass.

5. **Heightened attestation only (no scan receipt requirement)** — Gate 5 walkthrough enumerates the security checklist; no requirement to cite a fresh `arb-step-security-*` receipt. REJECTED: reproduces the GHI #290 fabrication-pathway shape at the security layer. An agent can synthesize a 'yes I reviewed crypto choices' walkthrough as easily as it can synthesize a foundation-kind attestation; the TTY+ATTEST confirmation closes that for human presence but not for actual scan-evidence depth. Scanner output (true-positive findings) is the mechanical backstop that human attention alone can't provide. Pairing both — receipt cited inline AND heightened walkthrough — mirrors today's heavy-lane shape and gives both mechanical and judgment evidence.

6. **Single foundation ADR absorbing toolchain (this ADR + bandit/semgrep + scoring + suppression model)** — collapse doctrine and toolchain into one ADR. REJECTED: conflates two decisions with different lifetimes. Doctrine should be stable (the invariant 'security work needs heightened review' is unlikely to change); toolchain choices evolve (bandit, semgrep, custom). Mixing them means every toolchain refresh reopens the doctrine, and every doctrine clarification forces a toolchain re-evaluation. The clean layering — foundation pins doctrine, feature ADR (promoting `pool.agentic-security-review`) pins toolchain — keeps each decision in scope.

7. **Promote `pool.agentic-security-review` directly to a feature ADR (skip foundation layer)** — fold the doctrine inline into the toolchain ADR's Rationale. REJECTED in design dialogue: foundation-kind is the right home for 'this class of code requires this class of review' — that's an invariant codifying app/system identity, not a release-carrying capability. Foundation lets the lane-matrix mechanism be reused across future axes (privacy, compliance) without reopening the toolchain ADR. The user explicitly accepted the foundation-first layering when offered the choice between options #1 and #2.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.22 | Completed | Jeffry | 2026-04-29 | attest completed — Foundation-kind heavy-lane doctrine landed: sensitivity third axis canonized across schema (OBPI-01), surface registry data/security_surfaces.json (OBPI-02), gz validate --sensitivity scope with --explain subform (OBPI-03; 587 briefs scanned, no escapes, registry healthy), _requires_security_review_attestation OR'd into _requires_human_obpi_attestation (OBPI-04), Gate 5 walkthrough + reserved arb-step-security- canonical slot (OBPI-05), and .gzkit/rules/security-sensitivity.md + AGENTS.md matrix + Mechanical scorecard entry (OBPI-06). All 6 OBPIs attested_completed. Receipts: lint arb-ruff-c0a477b263e24d70ba3a4c12a6eb0c9b; types arb-step-typecheck-59a09b5cb3184fb89afc736ecf2cb008; tests arb-step-unittest-ffa18f3cf496467881a57e3bcf19524b (3803 passed, 1 skipped); docs arb-step-mkdocs-9bb99769aa4a49aa851cf4b4d8736e5d. Out-of-scope BOM table rendering defect tracked GHI #362. |
