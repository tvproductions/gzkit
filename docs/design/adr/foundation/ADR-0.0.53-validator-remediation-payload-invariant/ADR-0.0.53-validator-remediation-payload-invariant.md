---
id: ADR-0.0.53-validator-remediation-payload-invariant
status: Draft
kind: foundation
semver: 0.0.53
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-19
---

# ADR-0.0.53-validator-remediation-payload-invariant: Validator Remediation Payload Invariant

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats every fail-closed exit from a gzkit validator, ARB step, or blocking hook as an agent-context-injection surface: when the harness refuses, what it says is the next thing an agent reads. Refuses to ship a validator that exits non-zero with a bare assertion message; refuses to accept `print("FAIL")` as a fail-closed contract. The structural witness is not a passing test of the validator's *detection* — that already exists — but a structural assertion that the validator's *failure utterance* carries the three canonical fields every consuming agent needs to recover.

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit's harness still validates and still fails closed — but every validator emits its rejection in an ad-hoc shape (one-liner stderr, multi-paragraph JSON, jsonschema raw output, "see file X" pointer with no diagnosis). Agents reading the failure cannot mechanically extract the recovery command, so the harness's refusal becomes shallow signal: the gate fired, but the next step is unclear. The project still ships, but the agent-legibility contract — *"anything the agent can't access in-context while running effectively doesn't exist"* — is silently broken at the precise moment the harness has the most to say. **Yes — the project would still be the project, but it would lose the property that every fail-closed gate is also a structured prompt-augmentation surface.** This ADR names that property as invariant.

**Port-vs-adapter framing:** This ADR authors a **port**. It defines the abstract `RemediationPayload` contract every validator / ARB receipt / blocking hook must honor; it does not specify how any individual validator computes its three fields. Existing informal implementations at `src/gzkit/governance/trust_audits/vendor_manifest.py:82` ("canonical recovery hint") and `src/gzkit/governance/trust_audits/instructions_files_budget.py:14` ("remediation pointer to the …") are the canonical anchor — this ADR canonizes the shape they already grope toward, then extends it to every fail-closed surface.

## Intent

The OpenAI "Harness Engineering" thesis (2026-02-11) identified one mechanical lever that compounded across their fully agent-generated codebase: *"Because the lints are custom, we write the error messages to inject remediation instructions into agent context."* The error string is not human-only documentation — it is the next prompt the agent reads. In a harness where the agent is the primary reader of validator output, the failure utterance's *shape* is a first-class agent-legibility surface, equal in importance to the validation logic itself.

gzkit already does this **informally**, in two places that surfaced during the empirical audit before this ADR was authored:

- `src/gzkit/governance/trust_audits/vendor_manifest.py:82` — comment annotates a "canonical recovery hint rather than only the jsonschema rendering"
- `src/gzkit/governance/trust_audits/instructions_files_budget.py:14` — module docstring names "a remediation pointer to the [`gz-context-diet` skill]"

The shape exists. It is not declared. It is not enforced. It varies by author taste. New validators landing under future ADRs inherit no contract — they emit whatever fail-closed string the author wrote in the moment. The result: gzkit ships a harness where ~60% of fail-closed validators include a recovery command, ~40% emit only a diagnosis, and the agent reading the output cannot programmatically tell which to expect.

This ADR canonizes the existing informal shape as the **`RemediationPayload` invariant**: every fail-closed exit from a `gz validate --<scope>` validator, every ARB step / receipt rejection, and every blocking hook utterance MUST carry three named fields — **`rule_citation`** (file:line of the rule the failure violates), **`diagnosis`** (one-line statement of what failed), **`recovery`** (the exact shell command that would make the failure go away or, if no single command suffices, the canonical skill invocation that walks the operator to recovery). Format is machine-parseable (JSON line at the head of stderr) AND human-readable (the same payload rendered as a three-line block). Both renderings come from one source via a single helper; no validator hand-formats payload fields.

The scope is broad by design — limiting to validators only would leave the two adjacent agent-context-injection surfaces (ARB receipt failures, hook blocks) emitting in their existing ad-hoc shapes, breaking the *"every harness refusal is a structured prompt"* property at exactly the seams where it matters most.

Empirical grounding: the validator-remediation shape was already being reached for in trust_audits; the question is no longer *"does this pattern work?"* but *"why is it not the contract?"* This ADR answers: because no foundation ADR has named it. After this ADR lands, the contract exists; future validators inherit it mechanically; the meta-validator `gz validate --remediation-payload-binding` flags any new fail-closed surface that emits a non-payload-shaped rejection.

## Decision

Canonize the **`RemediationPayload`** invariant: every fail-closed exit from a gzkit validator, ARB step / receipt validator, or blocking hook MUST emit a structured payload carrying `rule_citation` (file:line), `diagnosis` (one-line), and `recovery` (exact command or canonical skill invocation), rendered both as a JSON line (first stderr line, for agent context injection) and as a human-readable three-line block (for operator terminal output), from a single helper. Decomposed into four OBPIs.

**The invariant (canonical statement):** When a gzkit validator, ARB step, ARB receipt validator, or blocking hook exits non-zero, the process MUST emit a `RemediationPayload` containing (1) `rule_citation` in `path/to/rule.md:LINE` or `path/to/canon.py:LINE` form pointing to the rule whose violation triggered the failure; (2) `diagnosis`, a one-line natural-language statement of what specifically failed (no multi-paragraph prose, no jsonschema raw output, no stack traces in the diagnosis field — stack traces remain available on `--debug`); (3) `recovery`, either a single shell command that would re-pass the gate if the operator's local state were correct, or the canonical skill invocation (e.g. `/gz-context-diet`, `uv run gz register-adrs`) whose procedure walks the operator to a passing state. Both JSON-line rendering and human-readable rendering come from one canonical helper; no validator hand-rolls either rendering.

**Decision items (1:1 with Checklist below):**

1. **Author the `RemediationPayload` port and helper.** Add `RemediationPayload` as a Pydantic model in `src/gzkit/core/models.py` (named-departure stdlib exception per `.gzkit/rules/models.md`) with fields `rule_citation: str` (pattern `^[^:]+:\d+$`), `diagnosis: str` (max length 240, no newlines), `recovery: str` (one of: a shell command starting with `uv run gz `, `gh `, `git `, `python -m `, or a slash-skill invocation starting with `/`). Add `RemediationPayload.render_jsonline() -> str` and `RemediationPayload.render_human() -> str` methods. Add `gzkit.core.exceptions.RemediationFailure` exception type that wraps a `RemediationPayload` and is raised by any fail-closed surface; `__main__.py`'s top-level exception handler catches it and emits the dual rendering to stderr before exiting non-zero. Author `.gzkit/rules/validator-remediation.md` (rule version `0.1.0`, paths `src/gzkit/governance/trust_audits/**/*.py`, `src/gzkit/validators/**/*.py`, `src/gzkit/arb/**/*.py`, `src/gzkit/hooks/**/*.py`) declaring the invariant and the three-field shape. Add scorecard entry to `docs/governance/advisory-rules-audit.md` classifying the rule **Mechanical** (the helper-existence check is mechanical; the *content* of `diagnosis` and `recovery` remains Judgment-class and is not validated here).

2. **Migrate every `gz validate --<scope>` validator to emit `RemediationPayload`.** Walk every validator scope registered in `src/gzkit/governance/trust_audits/` (the audit found at minimum: `vendor_manifest.py`, `instructions_files_budget.py`, `adr_status_index.py`, `brief_path_validity.py`, `frontmatter_coherence.py`, `req_coverage.py`, `status_vocab.py`, plus every scope in `trust_audits/`). Each fail-closed path raises `RemediationFailure(RemediationPayload(...))` rather than calling `sys.exit()` or printing ad-hoc strings. The two existing informal sites (vendor_manifest.py:82, instructions_files_budget.py:14) become the canonical reference implementations; their existing comment annotations promote to active code emitting the structured payload. Ship `gz validate --remediation-payload-binding` meta-validator that imports every validator scope and asserts: every fail-closed path raises `RemediationFailure` (not `SystemExit`, not bare exceptions); every emitted payload validates the Pydantic model; the meta-validator binds the contract going forward. Heavy-lane attestation pattern: the meta-validator's existence is itself enforced by the `validate-cli-scopes` audit listing `--remediation-payload-binding` as a required scope.

3. **Extend the payload contract to ARB step + ARB receipt validation failures.** Every ARB step that exits non-zero (`uv run gz arb step --name <X> -- <cmd>`) emits the `RemediationPayload` to stderr when the wrapped command fails. The receipt body's `failure` block (when present) carries the same three fields. `uv run gz arb validate` failures (receipt-shape rejections, fabricated-receipt detection, missing-receipt detection) all speak the payload shape. Update `CANONICAL_STEP_COMMANDS` enforcement: when `gz arb validate` rejects a non-canonical step, the rejection cites `AGENTS.md` § Attestation and emits a `RemediationPayload` whose `recovery` field is the canonical invocation string. Tests: `tests/arb/test_remediation_payload.py` asserts every ARB failure path emits a valid payload; the meta-validator's scope is extended to cover `src/gzkit/arb/**/*.py`.

4. **Extend the payload contract to blocking hook exits.** Every blocking hook (SessionStart, PreToolUse, PreCommit, PostToolUse-if-blocking) under `src/gzkit/hooks/` emits the `RemediationPayload` to stderr when the hook returns a non-success status. The first line of hook output is the JSON-line rendering (so the agent's automatic context-injection sees the parseable form first); subsequent lines are the human-readable rendering (so the operator's terminal sees the formatted block). Existing hooks under `src/gzkit/hooks/` migrate to the helper; new hooks landing after this ADR inherit the contract via Pydantic validation at construction time. Tests: `tests/hooks/test_remediation_payload.py` covers every registered hook's failure path. Update `docs/governance/governance_runbook.md` § Hook outputs naming the three-field contract; update `docs/user/runbook.md` § Recovery flows naming the canonical recovery-command pattern. The meta-validator's scope is extended to cover `src/gzkit/hooks/**/*.py`.

**Sequencing:** OBPI-01 (port + helper + rule + scorecard) is the precondition for all others — every subsequent OBPI consumes the helper. OBPI-02 (validator migration + meta-validator) lands second; the meta-validator's existence is the structural witness that future validators inherit the shape. OBPI-03 (ARB migration) and OBPI-04 (hook migration) are independent of each other and can land in parallel after OBPI-02. The meta-validator scope is extended in each of OBPI-02, OBPI-03, OBPI-04 — the scope grows monotonically; each OBPI's attestation is conditional on the meta-validator covering its surface.

**Lane: Heavy.** New rule file + new `RemediationFailure` exception type + new `RemediationPayload` Pydantic model + new `gz validate --remediation-payload-binding` CLI scope + behavior change across every fail-closed exit in the harness. Per `.claude/rules/cli.md` (new validator scope, new CLI exit semantics for many existing commands) and `.gzkit/rules/skill-surface-sync.md` (new canonical rule surface). Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.36-universal-obpi-attestation.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT validate the *content* of `diagnosis` or `recovery` — only the *shape* of the payload. Whether a diagnosis is accurate or a recovery command actually recovers is Judgment-class and remains the validator author's responsibility, just as `.gzkit/rules/agent-failure-modes.md` is Judgment-class.
- Does NOT introduce machine-readable structured logging for non-fail-closed paths (success exits, warning emissions, info-level output) — those remain free-form. Only the fail-closed surface is constrained.
- Does NOT extend to operator-facing CLI commands that are not validators/ARB/hooks (e.g., `gz state`, `gz status` failure outputs remain in their existing shapes); the scope is precisely the "agent reads this as a prompt" surface, not all CLI failure output. The operator-doc-verb-resolution rule already binds those surfaces from another angle.
- Does NOT modify existing skill `SKILL.md` files to use the payload — skills are advisory operator-facing procedure, not blocking surfaces.
- Does NOT canonize recovery commands as receipts. The `recovery` field is *the command the operator would run* if they had to recover manually; it is not a step-receipt invocation.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Every validator graph-field read has a coupled write path (GHI #193 class) — the validator-output-integrity surface this remediation-payload invariant extends to a three-field contract. | uv run gz validate --validator-fields | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.53-validator-remediation-payload-invariant --check | 0 |

## Consequences

### Positive

1. **The OpenAI Harness Engineering "inject remediation into agent context" pattern lands as a foundation invariant, not a per-validator best practice.** New validators landing under future ADRs inherit the shape mechanically via the meta-validator; the contract cannot silently drift because non-conforming validators fail `gz validate --remediation-payload-binding` at CI time.

2. **Two existing informal anchors (vendor_manifest.py:82, instructions_files_budget.py:14) get promoted from comment-annotations to canonical reference implementations.** The pattern these validators reached for is now the shape every validator emits. Maintenance cost: one helper, one Pydantic model, one rule file — the previous informal pattern produced one-off implementations per validator.

3. **Agent context injection becomes structured by default.** The JSON-line first stderr line is parseable by agents (Codex, Claude Code, etc.) without prompt engineering; the human-readable block is operator-terminal-friendly. One emission, two consumers, no duplication.

4. **The Anti-vibing operative claim "doctrine drift is invariant drift" is structurally defended at the failure-utterance surface.** Today, drift between AGENTS.md attestation language ("see [skill X]") and validator output ("FAIL: [raw jsonschema]") is silent. After this ADR, the validator's `rule_citation` field MUST point to the actual rule file:line, and the meta-validator flags any payload whose citation does not resolve to an existing line in an existing rule file (mechanical scope: `gz validate --remediation-citation-resolves`, named as a future GHI in OBPI-01). The citation is the structural witness that the validator and the rule remain coupled.

5. **Coupled-surface coherence (DO IT RIGHT 1a) lands a new structural defense.** When a rule's wording changes, the validator's `rule_citation` either still resolves (rule moved or expanded) or no longer resolves (rule deleted or section renamed) — the meta-validator surfaces the second case at CI time before the change merges. This is the same class of structural defense `gz validate --cli-alignment` provides for `gz <verb>` references in docs, extended to validator-side coupling.

6. **Recovery commands become first-class artifacts.** The `recovery` field is constrained to a small enum of prefixes (`uv run gz`, `gh`, `git`, `python -m`, `/<skill>`); the operator never wonders whether a validator's stated recovery is invocable. Tests assert every emitted recovery either parses as a registered `gz` verb (via the same resolution `gz validate --cli-alignment` uses), a known skill, or a documented external command — pinned, not narrative.

7. **Hook output becomes agent-prompt-injection-friendly.** Today, a SessionStart-hook failure can emit multi-line shell output, banner art, or version strings that crowd the agent's first-turn context. After this ADR, the first line is structured, parseable, and bounded to ~240 chars (`diagnosis` max length); the parseable form precedes any human-readable banner. Context budget compounds against the Anti-vibing operative claim "context is a scarce resource."

### Negative

1. **Migration cost across every fail-closed exit.** The audit identified 7+ trust_audit scopes and an unknown number of `src/gzkit/validators/`, `src/gzkit/arb/`, and `src/gzkit/hooks/` failure paths. Each must be rewritten to raise `RemediationFailure` rather than emit ad-hoc strings. Mitigated by: (a) OBPI-01 ships the helper before any migration is required, so each migration is mechanical (find-and-replace `sys.exit(1)` + ad-hoc print → `raise RemediationFailure(...)` with the three fields); (b) the meta-validator is added at the end of each migration OBPI, so the migration is self-verifying; (c) the existing informal sites (vendor_manifest.py:82, instructions_files_budget.py:14) already have the three fields in comment form — migration there is comment-to-code lifting.

2. **The `recovery` field's prefix enum may not cover legitimate recoveries.** **Pre-mortem scenario:** 12 months from now, a validator surfaces a failure whose only recovery is a sequence of commands ("first run X, then edit Y, then run Z") — the single-prefix constraint forces an awkward catch-all skill invocation that doesn't actually exist yet. **Mitigation:** the `recovery` field allows `/<skill>` invocation as one of the enum prefixes specifically for this case — multi-step recoveries route to a skill, and if no skill exists, the OBPI completing the change either authors one or expands an existing skill. The constraint is a feature: it forces authors to either name a single command or invest in skill ceremony rather than emit a multi-paragraph recovery narrative the agent then has to parse heuristically.

3. **`diagnosis` 240-char limit may force authors to truncate context.** **Pre-mortem scenario:** validators with complex failure modes (e.g. cycle detection in ADR DAG) emit a one-line diagnosis that strips the cycle path, leaving the operator and the agent without the actionable detail. **Mitigation:** the diagnosis is one of three fields, not the only field — detailed failure context (cycle path, jsonschema delta, conflicting receipt IDs) emits on the lines following the human-readable block, prefixed by a `details:` marker. The 240-char cap binds the *first agent-readable line*, not the entire output. This is symmetric with how OpenAI's piece treats agent context: the entry surface is constrained; the deep dive is reachable from there.

4. **Reversibility: this is a one-way door at the canonical-shape level.** Once every fail-closed surface emits the payload, downstream tooling (CI parsers, agent context-injection logic, operator dashboards) depends on the JSON-line presence. Reversal in 18 months would require either renaming the contract (and migrating all consumers) or accepting a backward-incompatible break. Justified by: the alternative is the indefinite continuation of the ad-hoc ~60/40 split the audit surfaced — a state worse than either pole. The asymmetry is intentional.

5. **The meta-validator may produce noise during the migration window.** During OBPI-02/03/04 rollout, every validator not yet migrated fails the meta-validator scope. **Pre-mortem scenario:** developers running `uv run gz check` during the migration window see a wall of meta-validator failures for surfaces they didn't change, get desensitized, and start ignoring the meta-validator's output. **Mitigation:** the meta-validator ships with a baseline allowlist file (`data/validator_remediation_baseline.json`) listing every pre-existing fail-closed surface as exempt at OBPI-01 landing; each subsequent migration OBPI removes its targeted surfaces from the allowlist. The allowlist shrinks monotonically across the four OBPIs; the final OBPI's attestation requires the allowlist to be empty. This is the same pattern `gz validate --reconcile-freshness` uses for bootstrap-vs-drift distinction.

6. **Pydantic dependency expansion.** The `RemediationPayload` model is a Pydantic model per `.gzkit/rules/models.md`'s named-departure doctrine. Adding another Pydantic-bound surface increases the project's Pydantic coupling. Mitigated by: Pydantic is the canonical named departure from stdlib for validation per `.gzkit/rules/models.md`; adding one more model to the existing surface is on-doctrine. The alternative (a dataclass with hand-rolled validation) duplicates work the named departure already justifies.

7. **The 2am operator scenario:** an operator on-call at 2am sees a fail-closed exit with a structured `recovery` command pointing to a skill the operator doesn't remember, in a context where they need to ship a hotfix in five minutes. **Mitigation:** the human-readable rendering puts the `recovery` command on its own line, prefixed `Recovery: <command>` — copy-pasteable, no skill invocation required to act. The structured first line is for agents; the human form is for the operator. Both render from one source. No friction beyond the existing read-and-run pattern.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
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

- [ ] OBPI-0.0.53-01: Author `RemediationPayload` port (Pydantic model + helper + exception type + rule file + scorecard entry)
- [ ] OBPI-0.0.53-02: Migrate `gz validate --<scope>` validators + ship `gz validate --remediation-payload-binding` meta-validator
- [ ] OBPI-0.0.53-03: Extend payload contract to ARB step / receipt validation failures + extend meta-validator scope
- [ ] OBPI-0.0.53-04: Extend payload contract to blocking hooks + runbook updates + finalize meta-validator scope (allowlist empty)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

**Operator framing:** Discussion of OpenAI's "Harness Engineering" (2026-02-11) external thesis surfaced the observation: *"Lint error messages inject remediation instructions into agent context."* The operator asked for foundation ADRs covering invariants/ports, GHIs where needed, and clarifying questions on bounded decisions.

**Bounded decision (validator-remediation scope):** Three options surfaced — (a) validators only, (b) validators + ARB, (c) validators + ARB + hooks. Operator selected **(c) validators + ARB + hooks** with rationale: broadest agent-context coverage; matches OpenAI's "inject remediation into agent context" principle wherever the harness can speak.

**Bounded decision (sequencing):** Operator selected **draft all three foundation ADRs this session** (validator-remediation + AGENTS.md map + import-direction) plus three GHIs (doc-gardening chore, scorecard-velocity metric, external-corroboration doc citations).

**Empirical pre-authoring audit:** Two informal anchor sites identified — `src/gzkit/governance/trust_audits/vendor_manifest.py:82` and `src/gzkit/governance/trust_audits/instructions_files_budget.py:14` — confirming the shape exists informally before this ADR canonizes it.

**OBPI brief authoring deferral (explicit annotation):** The 4 OBPIs declared in this ADR's Checklist (OBPI-0.0.53-01 through -04) are listed as canonical decomposition items, but their per-brief authoring under `gz-obpi-specify` is **deferred to a follow-up session** and tracked under **GHI #499**. This annotation is the explicit-deferral path the advisor named as acceptable (the alternative — scaffolding 12 briefs across three ADRs in the same harness-engineering session — would have doubled session length and produced lower-quality briefs). The 1:1 Synchronization Mandate is satisfied at the Checklist level; the `obpis/` subdirectory populates under GHI #499's follow-up authoring passes before this ADR's promotion from Draft to Proposed.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/core/test_remediation_payload.py`, `tests/governance/test_validator_remediation_meta.py`, `tests/arb/test_remediation_payload.py`, `tests/hooks/test_remediation_payload.py`
- [ ] Rule file: `.gzkit/rules/validator-remediation.md` (body version `0.1.0`)
- [ ] Scorecard: `docs/governance/advisory-rules-audit.md` entry (Mechanical for shape; Judgment for content)
- [ ] Docs: `docs/governance/governance_runbook.md` § Hook outputs, `docs/user/runbook.md` § Recovery flows, `docs/user/manpages/gz-validate.md` (new `--remediation-payload-binding` scope)
- [ ] Baseline: `data/validator_remediation_baseline.json` (shrinks monotonically; empty at OBPI-04 completion)

## Alternatives Considered

**Alt 1: Validators-only scope.** Cheapest migration. Rejected because it leaves the two adjacent agent-context surfaces (ARB receipt failures, hook blocks) emitting in their existing ad-hoc shapes, breaking the *"every harness refusal is a structured prompt"* property exactly at the seams where it matters most (hook blocks are the *first* turn agents see; ARB failures are how `gz obpi complete` rejects attestations).

**Alt 2: Free-form remediation guidance encoded as Markdown blocks.** Author a `docs/governance/validator-recovery-cookbook.md` listing every validator's recovery procedure as Markdown prose; validators emit a single pointer to a section. Rejected because (a) it pushes the recovery content into a separate file the agent must fetch on-demand, breaking the *"first stderr line carries the recovery"* property; (b) the cookbook drifts from validator behavior with no mechanical coupling (the same anti-pattern OpenAI named with monolithic AGENTS.md); (c) it duplicates the rule-citation field's purpose with weaker enforcement.

**Alt 3: Use jsonschema raw output as the de facto contract.** Several existing validators already emit jsonschema validation errors verbatim. Rejected because (a) jsonschema raw output is dense and not bounded — exceeds the 240-char first-line budget routinely; (b) it carries no rule citation (the schema is the rule, but the line within the rule file is not surfaced); (c) it carries no recovery command (the agent must infer what to do from the schema mismatch). The payload contract is strictly more constrained.

**Alt 4: Defer to a future GHI; ship only the rule file now.** Author the rule file but leave migration to per-validator GHIs over time. Rejected because (a) the existing ~60/40 ad-hoc state would persist indefinitely; (b) without the meta-validator, the rule file is advisory-only and produces no structural defense; (c) the OpenAI thesis's evidence is that the lever's value compounds when applied everywhere — partial coverage produces only partial agent-legibility gains.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.53 | Pending | | | |
