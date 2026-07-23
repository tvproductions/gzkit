---
id: ADR-0.0.64-task-envelope-and-planning-decomposition
status: Validated
kind: foundation
semver: 0.0.64
lane: heavy
parent: ADR-0.22.0
date: 2026-05-27
---

# ADR-0.0.64-task-envelope-and-planning-decomposition: TASK Envelope and Planning Decomposition

## Persona

Active persona: `main-session` (`.gzkit/personas/main-session.md`). Craftsperson, governance-aware, whole-file-reasoning, direct. Treats the TASK tier as the per-labor-unit envelope the four-tier governance spine carries to its execution leaf — not as bookkeeping. Implementations of this ADR's OBPIs MUST inherit `@covers`'s decoration-time defense surface (typos surface at import, not at closeout); MUST preserve `d70793c4`'s auto-coordination as the diagnostic baseline (not revert it); and MUST make subdivision a deliberate authored act (`gz task start --seq next`), never a pipeline-inferred side-effect.

## Why foundation tier?

**Invariance test:** Without this ADR, the project would not be the project because the four-tier governance spine (ADR → OBPI → REQ → TASK) would ship with no per-labor-unit attribution at its execution leaf — worklog truth would not trace to the unit-of-work that produced it. ADR-0.22.0 declares this binding; without ADR-0.0.64, the binding has no envelope. The spine could still operate, but it would lose the property that ledger evidence — not agent narration — is source-of-truth at the TASK tier. That is identity-shaping for gzkit's anti-vibing mantra (operative claim 4: stochastic LLM vibing is the named failure class).

**Port-vs-adapter framing:** This ADR is a **port** — it specifies that TASK attribution MUST span four discovery channels (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with mechanical coherence-checking, and that subdivision MUST be operator-authored. The `@advances` decorator (`src/gzkit/tasks.py`), the `gz validate --task-envelope-coherence` validator, the `gz task fanout` readback, and the `gz task envelope diagnose` diagnostic surface are all **adapters** behind this port. Reuse of `@covers`'s machinery is deliberate: the port specifies the contract; the adapter inherits a tested pattern.

## Intent

ADR-0.22.0 declared the TASK-driven workflow binding (TASK is *how*; REQ is *what*; multiple TASKs per REQ is normal labor-subdivision, not multi-cycle iteration), but the mechanical surface left a doctrine-runtime gap: the `Task:|Ceremony:|Eval-feedback-source:` commit-trailer OR-rule made TASK attribution silently optional, and GHI #552's layer-4 wiring (commit `d70793c4`, 2026-05-26) auto-emits `task_started` / `task_completed` ledger events at OBPI Stage 2 + Phase 4 with `seq=01` per REQ per OBPI. That wiring satisfies the validator's surface check but lands granularity-locked: worklog events (`artifact_edited`, `gate_checked`, etc.) carry no `task_id` attribution; one coarse-default bucket per REQ swallows all per-labor-unit work. GHI #553 names this the canonical 'presence != envelope' anti-vibing operative claim 4 violation at the TASK tier of the governance spine — same T1->T2 doctrine-runtime decoupling family as GHIs #537, #538, #551 (one layer deeper). Foundation tier per the invariance test: without TASK envelope coherence, the four-tier governance hierarchy (ADR/OBPI/REQ/TASK) carries no per-labor-unit attribution at its execution leaf; the spine ships but loses the property that worklog truth traces to the unit-of-work that produced it. Hexagonal lens: this is a port (it specifies what TASK attribution MUST be), not an adapter (the `@advances` decorator and validator are adapters). Restoration is strictly additive: `d70793c4`'s `auto_start_obpi_tasks` / `auto_complete_obpi_tasks` stay in place as the coarse-default bucket so unattributed work still has a signature for the validator to detect; nothing reverted. Closes GHI #553.

## Decision

Layer five additive components on top of `d70793c4` (nothing reverted; coarse-default `seq=01` bucket preserved as diagnostic baseline). Decision items (1:1 with OBPI decomposition):

(1) Worklog schema additive — `task_id: str | None = None` field added to 8 worklog event types in `src/gzkit/events.py` and `src/gzkit/schemas/ledger.json` (`artifact_edited`, `gate_checked`, `evidence_emitted`, `policy_breach`, `validator_run`, `tool_invoked`, `agent_message`, `lint_run` — precise list confirmed against current schema during implementation). Pre-restoration events grandfathered (the field is optional; legacy events validate unchanged). Pydantic `BaseModel` with `ConfigDict(extra='forbid')` per `.gzkit/rules/models.md`; ledger-event identifiers serialized via `.as_posix()` where they encode paths per `.gzkit/rules/cross-platform.md`.

(2) `@advances(TASK-...)` decorator as substantive peer of `@covers` — added to `src/gzkit/tasks.py`. Validates at decoration time; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers a frozen `TaskAttributionRecord` Pydantic model (`extra='forbid'`, `frozen=True`) into a module-level registry following `@covers`'s precedent (`src/gzkit/coverage.py` `_load_known_reqs` lazy pattern). Companion discovery channels: `tasks: list[str]` frontmatter for structured artifacts (briefs, ADR packages); commit-trailer-only attribution remains the freeform fallback for shell-shaped work. New rule `.gzkit/rules/task-discovery.md` codifies the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) and the subdivision sub-invariant. Decoration-time fail-close on unknown TASK ID — same root concern as `@covers`'s typo-detection (typo'd REQ IDs already block at import; typo'd TASK IDs join the same defense surface).

(3) Subdivision-driven seq advancement — new `next_seq_for_req(req_id: str) -> int` helper queries ledger for max(`seq`) under `(req_id, current_obpi_id)` and returns +1; new `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). `seq=01` auto-coordination from `d70793c4` preserved as the default bucket the validator USES to detect unattributed work; `--seq next` is the deliberate-subdivision act that splits a coarse REQ into per-labor-unit TASKs. Subdivision sub-invariant codified in `.gzkit/rules/task-discovery.md`: *'When work for a REQ subdivides — multiple labor units, distinct evidence channels, separable acceptance — agents/operators MUST mint a new `seq` via `gz task start --seq next` rather than reusing seq=01.'*

(4) `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog events emitted under an active TASK with no `task_id` field (attribution-drift); (b) OBPI completes with default-bucket-only TASKs (`seq=01` across all REQs) and no `req_atomic: list[str]` exemption in brief frontmatter (subdivision-skipped); (c) layer-drift across the four discovery channels — `@advances` decorator names TASK-A, frontmatter `tasks:` names TASK-B, commit trailer names TASK-C, ledger `task_id` names TASK-D for the same logical unit (declaration-divergence). Brief frontmatter additive `req_atomic: list[str]` is the operator-authored escape valve declaring 'these REQs are genuinely atomic; no subdivision warranted'; declaration requires inline rationale survived through attestation-evidence review (mitigation of the escape-valve becoming the new normalized bypass per GHI #552 pattern repetition). Heavy lane fail-closed; Lite lane warn-only. Joins the default `gz check` pipeline per the existing `--commit-trailers`, `--cli-alignment`, `--adr-status-fresh` pattern.

(5) `gz task fanout <REQ-ID>` readback surface — table default (precedent: `gz covers` table-default); `--detail` renders ASCII tree with file:line spans; `--json` for tooling consumption. Columns: TASK, seq, status (started/completed/active), files_touched (count), edits (worklog-event count), attribution_check (pass/drift). `gz status` gains a TASK fan-out summary block surfacing per-REQ fan-out shape during work (not retrospectively). The primary operator question — 'what is the fan-out shape of REQ-X' — best answered by table; tree available on demand. Includes `gz task envelope diagnose <OBPI-ID>` subcommand (added during stress-test 2am-operator pass) that shows per-channel declarations side-by-side and names which channel needs the update when layer-drift fail-closes a closeout.

Lane: heavy (new validator scope; new ledger schema field; new CLI surfaces; new authoring discipline binding on every Python source file touching gzkit's behavior). Foundation-kind brief-level Gate 5 attestation per ADR-0.0.36 (universal). Restoration strictly additive vs. `d70793c4`; reversibility is two-way (schema-additive; decorator deprecation possible; validator downgrade fail->warn possible) at ~2-week reversal cost in 12 months.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| TASK is the per-labor-unit envelope: the task-envelope coherence gate enforces worklog attribution, subdivision discipline, and four-channel coherence. | uv run gz validate --task-envelope-coherence | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.64-task-envelope-and-planning-decomposition --check | 0 |

## Consequences

### Positive

1. TASK becomes the per-labor-unit envelope ADR-0.22.0 declared it to be — the four-tier governance spine (ADR -> OBPI -> REQ -> TASK) carries attribution all the way to its execution leaf; worklog truth traces to the unit of work that produced it, not to a coarse OBPI-boundary bucket.
2. Per-REQ fan-out shape becomes a design-quality signal surfaced DURING work (not retrospectively at closeout) via `gz task fanout` and the `gz status` TASK summary block — operators see when a REQ is genuinely doing too many things and warrants splitting before the validator catches it.
3. The discovery convention spans four layers (Python `@advances`, structured frontmatter `tasks:`, freeform commit trailer, ledger `task_id`) with mechanical coherence-checking — the failure GHI #553 names ('mechanically permits silent non-compliance') is structurally addressed because no single channel can be the silent bypass surface; layer-drift IS a fail-close signature.
4. `req_atomic` exemption is reviewable in canon (brief frontmatter survives through attestation evidence) rather than silent threshold-tuning in a side data file — the escape-valve risk is mitigated by visibility, following the `--complexity-doctrine-links` precedent that operator-tunable thresholds on fail-close validators ARE themselves the GHI #552-pattern bypass surface.
5. Restoration is additive — `d70793c4`'s work (auto-coordination of TASK boundary stamps at OBPI Stage 2 + Phase 4) stays in place as the coarse-default bucket; this ADR layers on top to provide envelope semantics. GHI #552's progress is preserved, not reverted.
6. `@advances` decorator reuses the load-bearing machinery `@covers` already established (decoration-time validation + module-level registry + import-walk discovery). The constraint that drove `@covers` (REQ ID typos must surface at import) applies equally to TASK ID typos — same root concern, same defense, no new patterns to learn or maintain.
7. The auto-coordination wiring from `d70793c4` (which the original GHI #553 framing could have read as needing revert) instead becomes the diagnostic baseline the validator uses to DETECT unattributed work — what looked like a defect becomes a structural feature. The coarse-default bucket is intentional fallback so unattributed work still has a signature.
8. Plan-mode integration ADR (ExitPlanMode parses plan steps and auto-mints TASKs under the active REQ) becomes a clean downstream follow-up — `gz task start --seq next` is the substrate that plan-mode auto-mint sits on top of. This ADR does not preclude it; this ADR makes it cheap.
9. The cultural shift implicit in this ADR — that subdivision is the deliberate act of planning labor, not a bookkeeping side-effect — surfaces in operator-facing tooling (`gz status` shows fan-out shape; `gz task fanout` is a primary readback). The shift becomes visible at every interaction, not buried in validator output.
10. Spine-level T1/T2 doctrine-runtime decoupling at the TASK tier (GHI #553's named root concern) joins the closed-loop pattern GHIs #537/#538/#551 closed at their respective tiers. The four-tier spine's mechanical-enforcement coherence is now uniform across all four layers.

### Negative

1. New authoring discipline required — `@advances` decoration becomes load-bearing for Python source touching gzkit behavior; subdivision via `gz task start --seq next` becomes load-bearing for agents/operators when work subdivides. Discipline cost is real; mitigation is that `@covers` precedent already established the pattern (Python authors of test code already invoke `@covers`; extending to source is incremental, not novel).
2. Heavy-lane fail-close on layer-drift across the four channels means typos block closeout. Acceptable per `@covers` precedent (typo'd REQ IDs already block at import); the `gz task envelope diagnose <OBPI-ID>` subcommand named in Decision item 5 is the mitigation for the 2am-operator scenario — side-by-side per-channel rendering names which channel needs the update.
3. Validator import-walk over `src/gzkit/` adds CI time at every `gz check` invocation. Acceptable per `gz covers` precedent (same machinery, similar cost); the import-walk discovery is necessary because Python channel attribution lives at decoration sites that must be detected by import, not by source-text grep.
4. Brief frontmatter additive `req_atomic: list[str]` is an authored bypass surface — same shape that produced the GHI #552 pattern (mechanically optional discipline becomes silently non-compliant). Mitigation is the inline-rationale requirement plus attestation-evidence-review surface visibility plus `gz status` surfacing `req_atomic` declarations prominently; cultural enforcement supplements mechanical visibility. Risk remains that operators normalize the exemption; the 18-month pre-mortem named this the most plausible failure mode and the mitigation is the closing-question follow-up about successor ADRs.
5. Decoration-time validation explodes import time of large modules under naive implementation. Mitigated by following `@covers`'s lazy `_load_known_reqs` pattern (the registry is loaded once at first decoration encounter, not at every import). Real cost on the first-call import path; amortized across run.
6. Operators/agents may systematically skip `@advances` and the validator import-walk catches the omission too late — blocking closeouts en masse. Pre-mortem named this; the mitigation is making fan-out shape visible during work (`gz status` block + `gz task fanout`) so subdivision-skipping surfaces as an interactive signal, not just a CI gate that fires at closeout time.
7. Schema-additive `task_id` field on 8 worklog event types is backwards-compatible (optional field), but the mechanical surface that consumes it (validator signature (a) — 'worklog events emitted under an active TASK with no `task_id`') retroactively classifies pre-restoration events as the diagnostic baseline. Pre-restoration events ARE grandfathered (the validator only checks worklog events emitted under an active TASK, and pre-restoration events have no active TASK by definition), but the grandfathering is an implicit-by-construction rule that future maintainers may not see as deliberate.
8. The four-channel discovery taxonomy (Python decorator, frontmatter, commit trailer, ledger) adds authoring surface — operators must remember which channel applies in which context. Mitigated by `.gzkit/rules/task-discovery.md` documenting the channel-context matrix, but the cognitive load is real.
9. The closed-set choice (`@advances` decorator vs. comment marker vs. docstring-only) is a one-way door at the Python channel — switching to a different mechanism in 12 months would require deprecation + parallel-channel ceremony. Acceptable per Reversibility forcing function; the cost is acknowledged.
10. Successor risk: if `req_atomic` becomes a normalized bypass, this ADR forces a cultural-enforcement-via-tooling successor (potentially a follow-up foundation ADR that promotes 'rationale must cite OBPI-specific reasoning' or 'req_atomic count gates closeout'). Named in the closing forcing function; not deferred to chance.

## Boundary Invariants

Cross-OBPI structural invariants spanning the five-OBPI decomposition. Each
invariant is audited at ADR closeout, not per-OBPI; STRUCTURAL-FENCE REQs
in the child briefs cite this section as their proof channel
(ADR-0.0.59-02 § REQ-kind discipline).

1. **Restoration is additive — `d70793c4` is never reverted.** OBPIs 01-05
   layer on top of the GHI #552 layer-4 auto-coordination wiring
   (`auto_start_obpi_tasks` / `auto_complete_obpi_tasks` in
   `src/gzkit/commands/task.py`). The coarse-default `seq=01` per-REQ bucket
   is preserved as the diagnostic baseline the validator USES to detect
   unattributed work; no commit in this ADR's implementation may remove or
   reverse-direction the auto-coordination behavior. Audited at closeout by
   `git log --reverse 9b74d573..HEAD -- src/gzkit/commands/task.py` showing
   only additive diffs to `auto_start_obpi_tasks` / `auto_complete_obpi_tasks`.
   (OBPI-01, OBPI-03)

2. **Four-channel discovery coherence is the unit of envelope correctness.**
   TASK attribution spans four channels — Python `@advances` decorator
   (OBPI-02), structured frontmatter `tasks: list[str]` (OBPI-02), commit
   trailer `Task:` (existing infrastructure in `src/gzkit/tasks.py`), and
   ledger `task_id` field (OBPI-01). For a single logical labor unit, all
   present channels MUST name the same TASK ID; layer-drift across channels
   is the validator's signature (c) fail-close (OBPI-04). No OBPI in this
   ADR may introduce a channel that produces TASK attribution outside this
   four-channel set without amending this invariant.

3. **`req_atomic` exemption is the only mechanical bypass to subdivision
   discipline; it requires brief-frontmatter declaration and survives to
   attestation evidence.** OBPI-04's signature (b) (default-bucket-only TASKs
   without subdivision) MUST suppress for REQs explicitly listed under the
   brief's frontmatter `req_atomic: list[str]` field, AND ONLY for those
   REQs. When `req_atomic` covers every REQ in an OBPI, signature (b) MUST
   suppress entirely for that OBPI — legitimately-atomic single-or-multi-REQ
   OBPIs that DO declare `req_atomic` must NOT false-positive. No other
   bypass surface (threshold config, env var, CLI flag) may be added without
   amending this invariant; the surface is the GHI #552-pattern bypass
   risk OBPI-04 names explicitly.

## Post-authoring reconciliation (ADR-0.0.64 closeout, 2026-07-12)

The § Decision text records this ADR's design as authored. Two surfaces grew
additively after authoring; recorded here so the historical design and the
shipped state are both legible (state-doctrine: the code + `task-discovery.md`
rule are source-of-truth, this note is the trace):

- **Signatures: three → four.** § Decision item (4) names three Heavy-fail
  signatures (a)/(b)/(c). The validator ships a fourth — signature (d)
  `_sig_d_obpi_id_divergence` — added later under **GHI #653** (producer
  canonicalization drift). Additive and covered; the three-signature design is
  unchanged, (d) is a hardening peer.
- **Ledger `task_id`: eight enforced, additively broader.** § Decision item (1)
  adds `task_id` to the eight named worklog event types this ADR scoped — the
  set `gz validate --task-envelope-coherence` signature (a) still enforces.
  The optional field was later extended additively to further telemetry/ceremony
  event types (`composition_candidate_emitted`, `rendition_committed`,
  `rendition_advisor_verdict`, `brief_reconciled`); those are not signature-(a)
  enforced. `.gzkit/rules/task-discovery.md` v0.3.0 carries the authoritative
  current statement.

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
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.64-01: **task-id-worklog-schema-additive** — Add optional `task_id: str | None = None` field to 8 worklog event types in `src/gzkit/events.py` + `src/gzkit/schemas/ledger.json`. Pre-restoration events grandfathered (optional field; legacy events validate unchanged). Pydantic models per `.gzkit/rules/models.md` (`BaseModel` + `ConfigDict(extra='forbid')`); path identifiers via `.as_posix()` per `.gzkit/rules/cross-platform.md`. Tests: REQ-derived `@covers`-decorated tests asserting (a) optional-field validates None as well as concrete TASK-IDs; (b) schema rejects unknown event-shape fields per `extra='forbid'`. (heavy lane: ledger-schema change is a runtime contract).
- [ ] OBPI-0.0.64-02: **advances-decorator-and-discovery-convention** — Add `@advances(TASK-...)` decorator in `src/gzkit/tasks.py` as substantive peer of `@covers`. Decoration-time validation; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra='forbid')`) into module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Frontmatter `tasks: list[str]` channel added to structured-artifact schemas (brief frontmatter + ADR-package frontmatter where applicable). Author new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with body-level `<!-- rule-version: 0.1.0 -->` marker + visible block quote per `.claude/rules/skill-surface-sync.md`. Tests: `@advances` decoration fail-closes on unknown TASK ID at import; registry surface exposes `TaskAttributionRecord` query API; frontmatter channel parses + validates via existing brief/ADR schema machinery. (heavy lane: new authoring contract; new rule).
- [ ] OBPI-0.0.64-03: **subdivision-driven-seq-advancement** — Add `next_seq_for_req(req_id: str) -> int` helper to `src/gzkit/tasks.py` (queries ledger for max `seq` under `(req_id, current_obpi_id)`, returns +1). Add `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). Preserve `d70793c4`'s `seq=01` auto-coordination as default-bucket fallback. Add subdivision sub-invariant to `.gzkit/rules/task-discovery.md` (bump rule version). Tests: `next_seq_for_req` returns 1 on empty ledger, N+1 on populated; `gz task start --seq next` mints next-available; explicit `--seq N` is honored when N doesn't collide. (heavy lane: new CLI surface).
- [ ] OBPI-0.0.64-04: **gz-validate-task-envelope-coherence** — New `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog event under active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs without `req_atomic` exemption; (c) layer-drift across four discovery channels. Brief frontmatter `req_atomic: list[str]` exemption surface added (operator-authored escape valve; inline rationale required; surfaced in attestation evidence). Add `gz task envelope diagnose <OBPI-ID>` subcommand showing per-channel side-by-side declarations. Heavy fail-close / Lite warn-only. Join `gz check` default pipeline. Pydantic `BriefStructure` schema additive for `req_atomic`. Tests: each of three signatures triggers in fixture, with `req_atomic` exemption suppression verified; layer-drift across all 4-channel combinations covered; `gz check` pipeline integration smoke. (heavy lane: new validator scope; new schema additive; pipeline integration).
- [ ] OBPI-0.0.64-05: **gz-task-fanout-readback** — New `gz task fanout <REQ-ID>` CLI command (table default; `--detail` ASCII tree with file:line spans; `--json` machine-readable). Columns: TASK, seq, status, files_touched, edits, attribution_check. Add TASK fan-out summary block to `gz status` output (per-REQ fan-out shape rendered during work, not just at closeout). Tests: each output format (table/detail/json) verified against fixture ledger; `gz status` integration verified; `attribution_check` column reflects validator-aligned pass/drift state. (heavy lane: new CLI surface; `gz status` integration).

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-27T19:57:19.084858*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.64-task-envelope-and-planning-decomposition

### Q: What is the title of this ADR?

**A:** TASK Envelope and Planning Decomposition

### Q: What is the semantic version?

**A:** 0.0.64

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** ADR-0.22.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** ADR-0.22.0 declared the TASK-driven workflow binding (TASK is *how*; REQ is *what*; multiple TASKs per REQ is normal labor-subdivision, not multi-cycle iteration), but the mechanical surface left a doctrine-runtime gap: the `Task:|Ceremony:|Eval-feedback-source:` commit-trailer OR-rule made TASK attribution silently optional, and GHI #552's layer-4 wiring (commit `d70793c4`, 2026-05-26) auto-emits `task_started` / `task_completed` ledger events at OBPI Stage 2 + Phase 4 with `seq=01` per REQ per OBPI. That wiring satisfies the validator's surface check but lands granularity-locked: worklog events (`artifact_edited`, `gate_checked`, etc.) carry no `task_id` attribution; one coarse-default bucket per REQ swallows all per-labor-unit work. GHI #553 names this the canonical 'presence != envelope' anti-vibing operative claim 4 violation at the TASK tier of the governance spine — same T1->T2 doctrine-runtime decoupling family as GHIs #537, #538, #551 (one layer deeper). Foundation tier per the invariance test: without TASK envelope coherence, the four-tier governance hierarchy (ADR/OBPI/REQ/TASK) carries no per-labor-unit attribution at its execution leaf; the spine ships but loses the property that worklog truth traces to the unit-of-work that produced it. Hexagonal lens: this is a port (it specifies what TASK attribution MUST be), not an adapter (the `@advances` decorator and validator are adapters). Restoration is strictly additive: `d70793c4`'s `auto_start_obpi_tasks` / `auto_complete_obpi_tasks` stay in place as the coarse-default bucket so unattributed work still has a signature for the validator to detect; nothing reverted. Closes GHI #553.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Layer five additive components on top of `d70793c4` (nothing reverted; coarse-default `seq=01` bucket preserved as diagnostic baseline). Decision items (1:1 with OBPI decomposition):

(1) Worklog schema additive — `task_id: str | None = None` field added to 8 worklog event types in `src/gzkit/events.py` and `src/gzkit/schemas/ledger.json` (`artifact_edited`, `gate_checked`, `evidence_emitted`, `policy_breach`, `validator_run`, `tool_invoked`, `agent_message`, `lint_run` — precise list confirmed against current schema during implementation). Pre-restoration events grandfathered (the field is optional; legacy events validate unchanged). Pydantic `BaseModel` with `ConfigDict(extra='forbid')` per `.gzkit/rules/models.md`; ledger-event identifiers serialized via `.as_posix()` where they encode paths per `.gzkit/rules/cross-platform.md`.

(2) `@advances(TASK-...)` decorator as substantive peer of `@covers` — added to `src/gzkit/tasks.py`. Validates at decoration time; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers a frozen `TaskAttributionRecord` Pydantic model (`extra='forbid'`, `frozen=True`) into a module-level registry following `@covers`'s precedent (`src/gzkit/coverage.py` `_load_known_reqs` lazy pattern). Companion discovery channels: `tasks: list[str]` frontmatter for structured artifacts (briefs, ADR packages); commit-trailer-only attribution remains the freeform fallback for shell-shaped work. New rule `.gzkit/rules/task-discovery.md` codifies the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) and the subdivision sub-invariant. Decoration-time fail-close on unknown TASK ID — same root concern as `@covers`'s typo-detection (typo'd REQ IDs already block at import; typo'd TASK IDs join the same defense surface).

(3) Subdivision-driven seq advancement — new `next_seq_for_req(req_id: str) -> int` helper queries ledger for max(`seq`) under `(req_id, current_obpi_id)` and returns +1; new `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). `seq=01` auto-coordination from `d70793c4` preserved as the default bucket the validator USES to detect unattributed work; `--seq next` is the deliberate-subdivision act that splits a coarse REQ into per-labor-unit TASKs. Subdivision sub-invariant codified in `.gzkit/rules/task-discovery.md`: *'When work for a REQ subdivides — multiple labor units, distinct evidence channels, separable acceptance — agents/operators MUST mint a new `seq` via `gz task start --seq next` rather than reusing seq=01.'*

(4) `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog events emitted under an active TASK with no `task_id` field (attribution-drift); (b) OBPI completes with default-bucket-only TASKs (`seq=01` across all REQs) and no `req_atomic: list[str]` exemption in brief frontmatter (subdivision-skipped); (c) layer-drift across the four discovery channels — `@advances` decorator names TASK-A, frontmatter `tasks:` names TASK-B, commit trailer names TASK-C, ledger `task_id` names TASK-D for the same logical unit (declaration-divergence). Brief frontmatter additive `req_atomic: list[str]` is the operator-authored escape valve declaring 'these REQs are genuinely atomic; no subdivision warranted'; declaration requires inline rationale survived through attestation-evidence review (mitigation of the escape-valve becoming the new normalized bypass per GHI #552 pattern repetition). Heavy lane fail-closed; Lite lane warn-only. Joins the default `gz check` pipeline per the existing `--commit-trailers`, `--cli-alignment`, `--adr-status-fresh` pattern.

(5) `gz task fanout <REQ-ID>` readback surface — table default (precedent: `gz covers` table-default); `--detail` renders ASCII tree with file:line spans; `--json` for tooling consumption. Columns: TASK, seq, status (started/completed/active), files_touched (count), edits (worklog-event count), attribution_check (pass/drift). `gz status` gains a TASK fan-out summary block surfacing per-REQ fan-out shape during work (not retrospectively). The primary operator question — 'what is the fan-out shape of REQ-X' — best answered by table; tree available on demand. Includes `gz task envelope diagnose <OBPI-ID>` subcommand (added during stress-test 2am-operator pass) that shows per-channel declarations side-by-side and names which channel needs the update when layer-drift fail-closes a closeout.

Lane: heavy (new validator scope; new ledger schema field; new CLI surfaces; new authoring discipline binding on every Python source file touching gzkit's behavior). Foundation-kind brief-level Gate 5 attestation per ADR-0.0.36 (universal). Restoration strictly additive vs. `d70793c4`; reversibility is two-way (schema-additive; decorator deprecation possible; validator downgrade fail->warn possible) at ~2-week reversal cost in 12 months.

### Q: What good things result from this decision? List benefits.

**A:** 1. TASK becomes the per-labor-unit envelope ADR-0.22.0 declared it to be — the four-tier governance spine (ADR -> OBPI -> REQ -> TASK) carries attribution all the way to its execution leaf; worklog truth traces to the unit of work that produced it, not to a coarse OBPI-boundary bucket.
2. Per-REQ fan-out shape becomes a design-quality signal surfaced DURING work (not retrospectively at closeout) via `gz task fanout` and the `gz status` TASK summary block — operators see when a REQ is genuinely doing too many things and warrants splitting before the validator catches it.
3. The discovery convention spans four layers (Python `@advances`, structured frontmatter `tasks:`, freeform commit trailer, ledger `task_id`) with mechanical coherence-checking — the failure GHI #553 names ('mechanically permits silent non-compliance') is structurally addressed because no single channel can be the silent bypass surface; layer-drift IS a fail-close signature.
4. `req_atomic` exemption is reviewable in canon (brief frontmatter survives through attestation evidence) rather than silent threshold-tuning in a side data file — the escape-valve risk is mitigated by visibility, following the `--complexity-doctrine-links` precedent that operator-tunable thresholds on fail-close validators ARE themselves the GHI #552-pattern bypass surface.
5. Restoration is additive — `d70793c4`'s work (auto-coordination of TASK boundary stamps at OBPI Stage 2 + Phase 4) stays in place as the coarse-default bucket; this ADR layers on top to provide envelope semantics. GHI #552's progress is preserved, not reverted.
6. `@advances` decorator reuses the load-bearing machinery `@covers` already established (decoration-time validation + module-level registry + import-walk discovery). The constraint that drove `@covers` (REQ ID typos must surface at import) applies equally to TASK ID typos — same root concern, same defense, no new patterns to learn or maintain.
7. The auto-coordination wiring from `d70793c4` (which the original GHI #553 framing could have read as needing revert) instead becomes the diagnostic baseline the validator uses to DETECT unattributed work — what looked like a defect becomes a structural feature. The coarse-default bucket is intentional fallback so unattributed work still has a signature.
8. Plan-mode integration ADR (ExitPlanMode parses plan steps and auto-mints TASKs under the active REQ) becomes a clean downstream follow-up — `gz task start --seq next` is the substrate that plan-mode auto-mint sits on top of. This ADR does not preclude it; this ADR makes it cheap.
9. The cultural shift implicit in this ADR — that subdivision is the deliberate act of planning labor, not a bookkeeping side-effect — surfaces in operator-facing tooling (`gz status` shows fan-out shape; `gz task fanout` is a primary readback). The shift becomes visible at every interaction, not buried in validator output.
10. Spine-level T1/T2 doctrine-runtime decoupling at the TASK tier (GHI #553's named root concern) joins the closed-loop pattern GHIs #537/#538/#551 closed at their respective tiers. The four-tier spine's mechanical-enforcement coherence is now uniform across all four layers.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. New authoring discipline required — `@advances` decoration becomes load-bearing for Python source touching gzkit behavior; subdivision via `gz task start --seq next` becomes load-bearing for agents/operators when work subdivides. Discipline cost is real; mitigation is that `@covers` precedent already established the pattern (Python authors of test code already invoke `@covers`; extending to source is incremental, not novel).
2. Heavy-lane fail-close on layer-drift across the four channels means typos block closeout. Acceptable per `@covers` precedent (typo'd REQ IDs already block at import); the `gz task envelope diagnose <OBPI-ID>` subcommand named in Decision item 5 is the mitigation for the 2am-operator scenario — side-by-side per-channel rendering names which channel needs the update.
3. Validator import-walk over `src/gzkit/` adds CI time at every `gz check` invocation. Acceptable per `gz covers` precedent (same machinery, similar cost); the import-walk discovery is necessary because Python channel attribution lives at decoration sites that must be detected by import, not by source-text grep.
4. Brief frontmatter additive `req_atomic: list[str]` is an authored bypass surface — same shape that produced the GHI #552 pattern (mechanically optional discipline becomes silently non-compliant). Mitigation is the inline-rationale requirement plus attestation-evidence-review surface visibility plus `gz status` surfacing `req_atomic` declarations prominently; cultural enforcement supplements mechanical visibility. Risk remains that operators normalize the exemption; the 18-month pre-mortem named this the most plausible failure mode and the mitigation is the closing-question follow-up about successor ADRs.
5. Decoration-time validation explodes import time of large modules under naive implementation. Mitigated by following `@covers`'s lazy `_load_known_reqs` pattern (the registry is loaded once at first decoration encounter, not at every import). Real cost on the first-call import path; amortized across run.
6. Operators/agents may systematically skip `@advances` and the validator import-walk catches the omission too late — blocking closeouts en masse. Pre-mortem named this; the mitigation is making fan-out shape visible during work (`gz status` block + `gz task fanout`) so subdivision-skipping surfaces as an interactive signal, not just a CI gate that fires at closeout time.
7. Schema-additive `task_id` field on 8 worklog event types is backwards-compatible (optional field), but the mechanical surface that consumes it (validator signature (a) — 'worklog events emitted under an active TASK with no `task_id`') retroactively classifies pre-restoration events as the diagnostic baseline. Pre-restoration events ARE grandfathered (the validator only checks worklog events emitted under an active TASK, and pre-restoration events have no active TASK by definition), but the grandfathering is an implicit-by-construction rule that future maintainers may not see as deliberate.
8. The four-channel discovery taxonomy (Python decorator, frontmatter, commit trailer, ledger) adds authoring surface — operators must remember which channel applies in which context. Mitigated by `.gzkit/rules/task-discovery.md` documenting the channel-context matrix, but the cognitive load is real.
9. The closed-set choice (`@advances` decorator vs. comment marker vs. docstring-only) is a one-way door at the Python channel — switching to a different mechanism in 12 months would require deprecation + parallel-channel ceremony. Acceptable per Reversibility forcing function; the cost is acknowledged.
10. Successor risk: if `req_atomic` becomes a normalized bypass, this ADR forces a cultural-enforcement-via-tooling successor (potentially a follow-up foundation ADR that promotes 'rationale must cite OBPI-specific reasoning' or 'req_atomic count gates closeout'). Named in the closing forcing function; not deferred to chance.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OBPI-0.0.64-01: **task-id-worklog-schema-additive** — Add optional `task_id: str | None = None` field to 8 worklog event types in `src/gzkit/events.py` + `src/gzkit/schemas/ledger.json`. Pre-restoration events grandfathered (optional field; legacy events validate unchanged). Pydantic models per `.gzkit/rules/models.md` (`BaseModel` + `ConfigDict(extra='forbid')`); path identifiers via `.as_posix()` per `.gzkit/rules/cross-platform.md`. Tests: REQ-derived `@covers`-decorated tests asserting (a) optional-field validates None as well as concrete TASK-IDs; (b) schema rejects unknown event-shape fields per `extra='forbid'`. (heavy lane: ledger-schema change is a runtime contract).

2. OBPI-0.0.64-02: **advances-decorator-and-discovery-convention** — Add `@advances(TASK-...)` decorator in `src/gzkit/tasks.py` as substantive peer of `@covers`. Decoration-time validation; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra='forbid')`) into module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Frontmatter `tasks: list[str]` channel added to structured-artifact schemas (brief frontmatter + ADR-package frontmatter where applicable). Author new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with body-level `<!-- rule-version: 0.1.0 -->` marker + visible block quote per `.claude/rules/skill-surface-sync.md`. Tests: `@advances` decoration fail-closes on unknown TASK ID at import; registry surface exposes `TaskAttributionRecord` query API; frontmatter channel parses + validates via existing brief/ADR schema machinery. (heavy lane: new authoring contract; new rule).

3. OBPI-0.0.64-03: **subdivision-driven-seq-advancement** — Add `next_seq_for_req(req_id: str) -> int` helper to `src/gzkit/tasks.py` (queries ledger for max `seq` under `(req_id, current_obpi_id)`, returns +1). Add `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). Preserve `d70793c4`'s `seq=01` auto-coordination as default-bucket fallback. Add subdivision sub-invariant to `.gzkit/rules/task-discovery.md` (bump rule version). Tests: `next_seq_for_req` returns 1 on empty ledger, N+1 on populated; `gz task start --seq next` mints next-available; explicit `--seq N` is honored when N doesn't collide. (heavy lane: new CLI surface).

4. OBPI-0.0.64-04: **gz-validate-task-envelope-coherence** — New `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog event under active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs without `req_atomic` exemption; (c) layer-drift across four discovery channels. Brief frontmatter `req_atomic: list[str]` exemption surface added (operator-authored escape valve; inline rationale required; surfaced in attestation evidence). Add `gz task envelope diagnose <OBPI-ID>` subcommand showing per-channel side-by-side declarations. Heavy fail-close / Lite warn-only. Join `gz check` default pipeline. Pydantic `BriefStructure` schema additive for `req_atomic`. Tests: each of three signatures triggers in fixture, with `req_atomic` exemption suppression verified; layer-drift across all 4-channel combinations covered; `gz check` pipeline integration smoke. (heavy lane: new validator scope; new schema additive; pipeline integration).

5. OBPI-0.0.64-05: **gz-task-fanout-readback** — New `gz task fanout <REQ-ID>` CLI command (table default; `--detail` ASCII tree with file:line spans; `--json` machine-readable). Columns: TASK, seq, status, files_touched, edits, attribution_check. Add TASK fan-out summary block to `gz status` output (per-REQ fan-out shape rendered during work, not just at closeout). Tests: each output format (table/detail/json) verified against fixture ledger; `gz status` integration verified; `attribution_check` column reflects validator-aligned pass/drift state. (heavy lane: new CLI surface; `gz status` integration).

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Revert `d70793c4`** — Restoration is additive; the coarse-default `seq=01` bucket is intentional fallback so unattributed work has a signature for the validator to detect. Reverting removes the safety net and re-opens GHI #552. REJECTED — restoration is layered, not reverted.

2. **Extend Validated ADR-0.22.0 with new OBPIs** — Same anti-pattern as editing attested briefs (closeout invariant: Validated ADRs are immutable contracts). REJECTED — every doctrine extension of an attested ADR ships as a successor ADR per ADR closeout invariants.

3. **Required `task_id` on all worklog events** — Breaks 7,897 prior ledger entries (backwards-compatibility blast radius). Wrong tradeoff for a discovery-channel improvement that is structurally additive. REJECTED — optional field with validator-detected drift signature is the correct shape.

4. **`task_id` only on `artifact_edited`** — Validator layer-drift signature needs uniform attribution coherence across all worklog channels; restricting to one channel makes drift detection blind to non-edit work (gate checks, validator runs, agent messages). REJECTED — partial coverage produces partial validator signal.

5. **Uniform `task_id` on every event type (including parent/boundary stamps)** — Category error: `task_started` / `task_completed` ARE TASK-boundary events; they have a TASK identity by construction, not as a child attribution field. Re-adding `task_id` on a `task_started` event would be tautological. REJECTED — schema additive is scoped to worklog events specifically.

6. **`@advances` ≡ docstring equivalence with no precedence** — Equivalence-without-precedence is the canonical signature of authored drift (two channels for the same fact, neither authoritative). REJECTED — Python channel is decorator-only; docstring channel is for prose context, not attribution.

7. **`@advances` as comment marker `# @advances: ...`** — Category error: it's a comment (no AST node, no decoration-time validation, no lint-time typo detection). Loses every property that makes `@covers` load-bearing. REJECTED — Python channel must be a decorator to inherit `@covers`'s machinery.

8. **Docstring-only Python channel (no decorator)** — Loses decoration-time fail-close that `@covers` precedent provides. Typo'd TASK IDs would survive to runtime; the same defense that GHIs #197/#272/#309 codified for `@covers` would not apply. REJECTED — Python channel must inherit the decoration-time defense surface.

9. **Pipeline auto-mints `seq>=02` on edit threshold** — Pipeline can't read agent intent; threshold-based auto-mint papers over the deliberate labor-decomposition planning act that `gz task start --seq next` makes explicit. Defeats the whole framing (subdivision is the deliberate act, not a bookkeeping side-effect). REJECTED — subdivision is operator-authored, not pipeline-inferred.

10. **Threshold-based validator severity config file (`data/task_envelope_thresholds.json`)** — Operator-tunable thresholds on a fail-close validator ARE the escape valve; threshold tuning would itself become the GHI #552-pattern bypass surface (mechanically optional discipline becomes silently non-compliant). REJECTED — `req_atomic` exemption with mandatory rationale + attestation visibility is the correct escape valve shape; a side data file is the wrong shape.

11. **Tree/histogram default for `gz task fanout`** — Breaks `gz covers` table-default precedent. The primary operator question ('what is the fan-out shape of REQ-X') is best answered by a table (TASK x seq x status x edits-count); tree is the on-demand `--detail` shape for spatial inspection. REJECTED — default shape follows the established `gz covers` precedent.

## Stress-test forcing-function answers (Tier 2)

**Pre-mortem (18 months out, failed spectacularly):** (a) operators/agents systematically skip `@advances` and the validator import-walk catches the omission too late, blocking closeouts en masse — needs early-detection signal during work; mitigation is `gz status` TASK fan-out block surfacing the shape interactively; (b) `req_atomic` exemption becomes the new escape valve operators tune everything into — same #552 pattern repeats one layer deeper; mitigated by rationale requirement + attestation-evidence-review visibility; (c) decoration-time validation explodes import time — mitigated by `@covers`'s lazy `_load_known_reqs` precedent.

**What would have to be true (this is right):** (i) authoring discipline holds — agents/operators actually invoke `gz task start --seq next` when subdividing; (ii) `@covers` precedent really does carry over to src/ as it does for tests/; (iii) `req_atomic` exemption mechanism doesn't normalize into routine bypass (needs cultural enforcement plus mechanical visibility in `gz status`). Shakiest condition is (iii); the closing-question follow-up names a cultural-enforcement-via-tooling successor ADR as the mitigation if it drifts.

**What would have to be true (Alternative 1 — revert `d70793c4` — to be better):** coarse-default `seq=01` bucket would have to be more harmful than helpful — but it IS the diagnostic signature the validator USES to detect unattributed work; reverting removes the safety net. Not credible.

**Constraint archaeology:** `@covers`'s pattern (decoration-time validation + module-level registry + import-walk discovery) was established for REQ coverage. Reusing it for TASK attribution is leveraging tested machinery, not inheriting unexamined convention. The constraint that drove `@covers` (REQ ID typos must surface at import) applies equally to TASK ID typos — same root concern.

**Assumptions surfaced:** (a) agents will subdivide via `gz task start --seq next` when work warrants it (counter-truth: validator catches the always-`seq=01` pattern); (b) `req_atomic` declarations will be made deliberately (counter-truth: rationale required, attestation-surface visibility); (c) decoration-time fail-close doesn't unduly slow import (counter-truth: `@covers` precedent shows acceptable cost).

**2am operator question:** 'Validator is fail-closing my closeout because layer-drift between `@advances` decorator and commit trailer. What do I do?' — `gz task envelope diagnose <OBPI-ID>` subcommand (added to OBPI-04 scope) shows per-channel declarations side-by-side and names which channel needs updating. Without this surface the 2am operator has no observable signal to act on.

**Reversibility:** Two-way door. Schema additive is backwards-compatible (optional field); `@advances` decorator can be deprecated via parallel-channel ceremony; validator can be downgraded fail->warn. Reversal cost in 12 months: ~2 weeks.

**Scope minimization:** OBPIs 01 + 02 are the minimum delivering value (schema channel + authoring convention). OBPIs 03-05 (subdivision CLI, validator, readback) make it enforceable end-to-end. Cuttable under time pressure: OBPI-05 readback could ship as plain `gz status` block without standalone `gz task fanout` (defer to follow-up). Real cost — design-quality signals are the value proposition.

**Downstream ADRs forced:** (i) plan-mode integration ADR (ExitPlanMode parses plan steps and auto-mints TASKs under active REQ; `gz task start --seq next` is the substrate); (ii) potentially a successor ADR if `req_atomic` becomes a normalized bypass — cultural-enforcement-via-tooling ADR that promotes rationale-citation discipline or count-gates closeout.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Revert `d70793c4`** — Restoration is additive; the coarse-default `seq=01` bucket is intentional fallback so unattributed work has a signature for the validator to detect. Reverting removes the safety net and re-opens GHI #552. REJECTED — restoration is layered, not reverted.

2. **Extend Validated ADR-0.22.0 with new OBPIs** — Same anti-pattern as editing attested briefs (closeout invariant: Validated ADRs are immutable contracts). REJECTED — every doctrine extension of an attested ADR ships as a successor ADR per ADR closeout invariants.

3. **Required `task_id` on all worklog events** — Breaks 7,897 prior ledger entries (backwards-compatibility blast radius). Wrong tradeoff for a discovery-channel improvement that is structurally additive. REJECTED — optional field with validator-detected drift signature is the correct shape.

4. **`task_id` only on `artifact_edited`** — Validator layer-drift signature needs uniform attribution coherence across all worklog channels; restricting to one channel makes drift detection blind to non-edit work (gate checks, validator runs, agent messages). REJECTED — partial coverage produces partial validator signal.

5. **Uniform `task_id` on every event type (including parent/boundary stamps)** — Category error: `task_started` / `task_completed` ARE TASK-boundary events; they have a TASK identity by construction, not as a child attribution field. Re-adding `task_id` on a `task_started` event would be tautological. REJECTED — schema additive is scoped to worklog events specifically.

6. **`@advances` ≡ docstring equivalence with no precedence** — Equivalence-without-precedence is the canonical signature of authored drift (two channels for the same fact, neither authoritative). REJECTED — Python channel is decorator-only; docstring channel is for prose context, not attribution.

7. **`@advances` as comment marker `# @advances: ...`** — Category error: it's a comment (no AST node, no decoration-time validation, no lint-time typo detection). Loses every property that makes `@covers` load-bearing. REJECTED — Python channel must be a decorator to inherit `@covers`'s machinery.

8. **Docstring-only Python channel (no decorator)** — Loses decoration-time fail-close that `@covers` precedent provides. Typo'd TASK IDs would survive to runtime; the same defense that GHIs #197/#272/#309 codified for `@covers` would not apply. REJECTED — Python channel must inherit the decoration-time defense surface.

9. **Pipeline auto-mints `seq>=02` on edit threshold** — Pipeline can't read agent intent; threshold-based auto-mint papers over the deliberate labor-decomposition planning act that `gz task start --seq next` makes explicit. Defeats the whole framing (subdivision is the deliberate act, not a bookkeeping side-effect). REJECTED — subdivision is operator-authored, not pipeline-inferred.

10. **Threshold-based validator severity config file (`data/task_envelope_thresholds.json`)** — Operator-tunable thresholds on a fail-close validator ARE the escape valve; threshold tuning would itself become the GHI #552-pattern bypass surface (mechanically optional discipline becomes silently non-compliant). REJECTED — `req_atomic` exemption with mandatory rationale + attestation visibility is the correct escape valve shape; a side data file is the wrong shape.

11. **Tree/histogram default for `gz task fanout`** — Breaks `gz covers` table-default precedent. The primary operator question ('what is the fan-out shape of REQ-X') is best answered by a table (TASK x seq x status x edits-count); tree is the on-demand `--detail` shape for spatial inspection. REJECTED — default shape follows the established `gz covers` precedent.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.64 | Completed | g0 | 2026-07-12 | Completed — TASK-envelope capability delivered and honestly decomposed. Hollow-gate integrity findings corrected in-place (not deferred): OBPI-02/03 scaffold-default REQs re-authored with [kind] tags over 11 genuine tests, cosmetic .is_file() tests deleted, gz task envelope diagnose fixed to read all four channels (+ genuine REQ-04-05 test), 8->12 event / 3->4 signature drifts reconciled (task-discovery.md v0.3.0 + ADR reconciliation note), runbook gap closed. Receipts: arb-ruff-f1becc372d8a4ec6af4045343e0a1e69, arb-step-typecheck-db354d379e884aea98161f4bbbc26658, arb-step-unittest-da4d07dd5042422b882c2026122f2431, arb-step-mkdocs-ce2a7565e2b64da5bd64bba2dc425684. |
