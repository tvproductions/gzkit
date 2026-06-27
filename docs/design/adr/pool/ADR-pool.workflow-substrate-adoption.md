---
id: ADR-pool.workflow-substrate-adoption
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.agent-evidence-boundary-flow-controls
inspired_by: anthropic-dynamic-workflows
---

# ADR-pool.workflow-substrate-adoption: Workflow substrate adoption — harness below, gates above

## Status

Pool

## Date

2026-06-27

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Agent context engineering and session reliability

---

## Intent

Adopt Claude Code's **dynamic-workflow execution substrate** as the mechanical
orchestration layer for OBPI pipeline **stages 1–3** (Load Context → Implement →
Verify), replacing prose-dispatched subagent orchestration with deterministic
JavaScript control flow (`pipeline()` / `parallel()` / fan-out / adversarial
verify / loop-until-done). The substrate runs **below the attestation seam**;
gzkit's governance (Gate 5 human attestation, the ledger as system-of-record,
Layer-1 canon) remains **above** it, untouched.

The thesis in one line: **harness below, gates above.** The substrate makes a
run reliable-to-itself; gzkit makes a run accountable-to-a-human. They compose;
they do not compete.

The motivating insight is that gzkit's two weakest anti-vibing defenses are
*prose* rules fighting *stochastic* tendencies — and the source article supplies
*structural* replacements for exactly those.

---

## Motivation

### The source article names gzkit's failure class

[Anthropic, "A harness for every task: dynamic workflows in Claude Code"](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)
(see § Source & References) names three single-context failure modes. Each maps
onto a gzkit defense — and two of those defenses are prose, the weakest
anti-vibing surface gzkit has:

| Article failure mode | gzkit defense today | Defense type |
|---|---|---|
| Agentic laziness (premature abandonment) | Iron Law: "pipeline runs to Stage 5; no stop-and-summarize" | **Prose** (rationalization table) |
| Self-preferential bias (favoring own output as judge) | independent `spec-reviewer` + `quality-reviewer` dispatch | **Prose dispatch** (pool ADR, unpromoted) |
| Goal drift via iterative summarization | ledger as system-of-record; compact rules | Structural ✓ |

gzkit's own doctrine prefers a mechanical backstop over advisory prose
("MAKE LLM STOCHASTIC VIBES INERT"). Converting the Iron Law and the reviewer
dispatch from prose into orchestration is the doctrine applied to itself.

### The new vibing surface this introduces (and why that is in-scope)

The article celebrates Claude **authoring its own harness per task**. A
dynamically-generated harness is the LLM choosing its own control flow — by
gzkit's lights, a *new vibing surface*. This ADR does not ban it; it **fences**
it. The smallest-vibing-surface move is to make the harness structurally unable
to reach the gate it must never touch (the attestation seam, Target Scope #2).

---

## Decision

Adopt the substrate for stages 1–3 and fence it below the attestation seam. The
substrate is a **canonical surface** delivered byte-equivalent by `gz init`
(ADR-0.0.31) — never sourced from `~/.claude/workflows`, which would be an
ungoverned, drifting surface.

### Target Scope

#### TS-1 — Express pipeline stages 1–3 on the Workflow substrate (R1)

`pipeline_runtime.py` invokes a canonical `Workflow` script for stages 1–3
instead of dispatching subagents via prose skill steps. Stage 2 uses `pipeline()`
(implement test-first → review) with the two reviewers in `parallel()` per REQ.
A `pipeline()` literally cannot "stop and summarize at Stage 2" — agentic
laziness becomes **structurally** impossible, not merely forbidden.

#### TS-2 — Fence the attestation seam (R2) — STRUCTURAL-FENCE

A gzkit Workflow script may not contain `gz obpi complete`, `gz attest`, or
pipeline-marker writes. Evidence flows *up* across the seam; authority never
flows *down*. Enforced by a new validator scope (`gz validate --harness-seam`,
fail-close exit 3). This is the augment that protects Gate 5 sacrosanctity while
permitting dynamic authoring below the line. Builds on the enabler ADR's
boundary-flow doctrine.

#### TS-3 — Schema-forced review verdicts (R3)

Promote the dormant `ADR-pool.obpi-pipeline-dispatch-attestation` and back
reviewer verdicts with the substrate's schema-forced StructuredOutput, so a
review is a *validated object* (and a ledger event), not a prose claim.
Self-preferential-bias defense moves from prose → mechanical; review receipts
fail-close on Heavy lane.

#### TS-4 — Name the harness-vs-direct routing choice (R5)

Add one row to AGENTS.md § Defect-fix routing: the harness is the
heavy/contract-bearing execution path; direct-fix stays cheap. Prevents wrapping
a 5-line patch in a 5-stage harness (the article's own "workflows use more
tokens; reserve for high-value" caution, expressed as a gzkit routing
threshold).

### The ledger remains truth (binding constraint on all Target Scopes)

Every durable fact produced inside stages 1–3 is written by a `gz` command run
*inside* a subagent (which emits a ledger event) and merely *reported* in the
workflow's return value. **The workflow's return value is Layer-3 / advisory.**
If the harness's state and the ledger ever disagree, the ledger wins. The
substrate's own resume journal / `runId` is **not** adopted as resume-truth —
the ledger + pipeline markers (campaign's "ledger↔marker binding") remain the
resume authority. Two state systems both claiming truth would be the exact
Layer-3-becomes-source-of-truth failure (Architectural Boundary 6).

---

## Alternatives Considered

1. **Do nothing — keep prose dispatch.** Rejected: leaves gzkit's two weakest
   defenses as prose against a stochastic tendency the platform vendor now
   addresses structurally. Risks gzkit ceremony reading as overhead.
2. **Adopt the substrate wholesale, including above the seam.** Rejected:
   internalizing Gate 5 into a JS harness is the "transport mechanism gating
   attestation" the canon forbids ("never, ever again that TTY/PTY bullshit").
3. **Adopt the substrate's resume journal as the pipeline's resume-truth.**
   Rejected: violates Architectural Boundary 6 (derived views never
   source-of-truth) and duplicates the campaign's ledger↔marker work.
4. **Share harnesses via `~/.claude/workflows`.** Rejected: an ungoverned,
   drifting surface outside the ADR-0.0.31 distribution invariant.

---

## Relationship to Existing Pool ADRs (prior-art positioning)

This ADR was prior-art-checked against the agent-* pool cluster before
authoring. It is deliberately scoped to avoid duplication:

| Pool ADR | Relationship |
|---|---|
| `ADR-pool.agent-evidence-boundary-flow-controls` | **Enabler.** TS-2 (seam fence) is an application of its producer/consumer/validator boundary-flow doctrine. |
| `ADR-pool.advisory-judge-surface` | **Defers to it.** Independent-judge-as-advisory (the R4 in the originating analysis) is *that* ADR's scope; this ADR does **not** restate it. |
| `ADR-pool.obpi-pipeline-dispatch-attestation` | **Consumes.** TS-3 promotes it and supplies the schema-forced mechanism it was missing. |
| `ADR-pool.agent-reliability-framework` | Adjacent, different altitude (standards-grade leveled trust framework). No overlap. |
| `ADR-pool.agent-execution-intelligence` | Adjacent (graduated deviation / MODE). No overlap. |

The distinct, unclaimed core this ADR owns: **adopting the dynamic-workflow
execution substrate as the orchestration layer for pipeline stages 1–3.** No
existing pool ADR proposes this.

---

## Source & References

- **Primary source:** Anthropic, *A harness for every task: dynamic workflows in
  Claude Code* — <https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code>
  (cited frontmatter `inspired_by: anthropic-dynamic-workflows`). Core concepts
  drawn on: subagent isolation, the six patterns (classify-and-act,
  fan-out-and-synthesize, adversarial verification, generate-and-filter,
  tournament, loop-until-done), deterministic JS orchestration, token-budget
  awareness, resumability.
- gzkit anchors: AGENTS.md § "MAKE LLM STOCHASTIC VIBES INERT", § Defect-fix
  routing; `.gzkit/rules/governance-core.md` (human-attestation canon); ADR-0.0.31
  (distribution invariant); Architectural Boundary 6 (derived views never
  source-of-truth); `src/gzkit/pipeline_runtime.py` (current dispatch surface).

---

## Open Questions (resolve at promotion)

1. **Lane/kind at promotion** — heavy + foundation (it changes a runtime
   contract and an app invariant: how stages execute) vs heavy + feature?
2. **Substrate availability contract** — what is the fallback when the Workflow
   tool is unavailable (e.g. `--no-subagents` single-session mode)? The fence
   (TS-2) and ledger-truth constraint must hold in both modes.
3. **Sequencing** — this is queued *behind* the active Magna Carta campaign's
   topmost item (MX lean kernel → `0.29.0`). Promotion is operator-ratified, not
   pulled ahead.

---

## Non-Goals

- No change to gate *sequencing* or to Gate 5 semantics. Stages 4–5 stay in the
  governed main loop, human-attested.
- No new source-of-truth. The ledger remains canonical; the substrate is
  execution only.
- No dynamic authoring *above* the seam.

---

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
