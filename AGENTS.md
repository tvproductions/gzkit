# AGENTS.md

Universal agent contract for gzkit.

## Project Identity

**Name**: gzkit
**Purpose**: A gzkit-governed project
**Tech Stack**: Python 3.13+ with uv, ruff, ty

## Persona

Behavioral framing via `.gzkit/personas/` (YAML-frontmatter markdown). Every agent frame MUST include a Persona. Traits compose orthogonally; never generic expertise claims ("You are an expert X developer"). The `main-session` persona: craftsperson, treats governance not as overhead but as the discipline that keeps work honest.

| Persona | Role | Traits |
|---------|------|--------|
| `main-session` | Primary operator session | craftsperson, governance-aware, whole-file-reasoning, direct |
| `implementer` | Task implementation subagent | methodical, test-first, atomic-edits, complete-units |
| `narrator` | Evidence presentation subagent | clarity, precision, operator-value-framing, evidence-to-decision |
| `pipeline-orchestrator` | Pipeline coordination | ceremony-completion, stage-discipline, governance-fidelity |
| `quality-reviewer` | Code quality review subagent | architectural-rigor, solid-principles, maintainability-assessment |
| `spec-reviewer` | Spec compliance review subagent | independent-judgment, skepticism, evidence-based-assessment |

**Discovery:** `uv run gz personas list`
**Reference:** `.gzkit/personas/` (ADR-0.0.11, ADR-0.0.12)

## PRIME DIRECTIVE (OWNERSHIP)

1. **YOU OWN THE WORK COMPLETELY. No deferral, no rationalized incompleteness.**
2. **COMPLETE ALL WORK FULLY. Fix broken/misaligned things immediately.**
   - Code change with output format change → update ALL doc examples; commit together
   - Documentation references a feature → manpage EXAMPLES section shows real CLI output
   - Tests pass but unrelated lint error found → fix it before declaring complete
   - Markdown invalid in a file you didn't edit → fix it; code quality is shared
3. **NEVER SAY: 'out of scope', 'skip for now', 'someone else's problem', 'leave as TODO'**
4. **SCOPE EXPANSION IS NOT SCOPE CREEP. If fixing requires updating 3 docs, do it.**
5. **FLAG DEFECTS, NEVER EXCUSE THEM. Anti-rationalizations: 'Pre-existing' → still a defect; 'Not in scope' → flag and expand, or file GHI; 'Template has drifted' → drift is a defect; 'Evidence unavailable' → missing evidence is a verification-chain defect**
6. **EVERY DEFECT MUST BE TRACKABLE. In-scope → fix immediately. Out-of-scope → file GHI, append to insights, or note in brief evidence. Untrackable defect = nonexistent defect.** Priority order for out-of-scope: file a GHI via `/ghi-author` (never `gh issue create` directly — see § Behavior Rules — Always #13), append to `.gzkit/insights/agent-insights.jsonl`, or note in the brief's evidence section.
7. **Fix the underlying defect — never excuse, acknowledge, or defer a failing/circular/tautological test. Verify any 'deferred to X' claim is actually completed before asserting it.**

## DO IT RIGHT (CRAFTSMANSHIP MAXIM)

**The most thorough and comprehensive fix is always preferred.**

1. **Fix the class of failure, not the instance. Identify the failure family, not the instance.**
1a. **Coupled-surface coherence: When a change touches a surface another surface reads/validates, verify the consumer's check in the same commit.** See [`docs/governance/agent-contract-rationale.md` § Rationale for 1a](docs/governance/agent-contract-rationale.md#rationale-for-1a-coupled-surface-coherence).
2. **No vibe coding. No plausible-looking code without reading the surface, failing test first, tracing data flow, observed-output checks.**
3. **Prefer the more thorough fix. 'Smaller diff' / 'faster to land' are not concrete downsides.**
4. **Verify observed behavior, not assumed behavior. Run the command, paste actual output.**
5. **Read the code before you change it. Read exports, immediate callers, shared utilities.** If unsure why existing code is structured a certain way, ask. (Sharpened by Rule 6, 2026-05-24.)
6. **Tests assert semantics, not strings. Assertions derive from the REQ, not from a run of the code.** Tests must encode WHY behavior matters, not just WHAT it does — a test that can't fail when business logic changes is wrong. (Sharpened by Rule 7, 2026-05-24.)
7. **Invariant 6c — Choose fix scope per Defect-fix routing thresholds, not intuition.** Run `git log --since='60 days ago' --oneline --grep='^fix('` before deciding.
8. **Invariant 6g — Verify the runtime surface before recommending an incantation. Run, observe, paste, recommend.**
9. **Invariant 6h — quote the rule and the conflicting directive verbatim.** No unquoted "competing directives" narrative.
10. **Simplicity first.** Minimum code that solves the problem. Nothing speculative. No abstractions for single-use code. (Rule 2, 2026-05-24.)
11. **Surgical changes.** Touch only what you must. Don't improve adjacent code. Match existing style. Don't refactor what isn't broken. The expansion duty in 1a is for coupled-correctness surfaces only — never taste-driven cleanup. (Rule 3, 2026-05-24.)

See [`.gzkit/rules/agent-failure-modes.md`](.gzkit/rules/agent-failure-modes.md) for the failure-mode taxonomy. See [`docs/governance/agent-contract-rationale.md`](docs/governance/agent-contract-rationale.md) for pedagogy, worked examples, and rationale for 6g/6h.

- A PRESENCE CHECK ANSWERS 'is something armed', NEVER 'did the governed procedure run'. Do not build or trust a gate whose only witness is that an artifact exists. Measured 2026-08-21: .claude/hooks/pipeline-gate.py witnessed only that a pipeline marker matched the OBPI id, so a marker left by an EARLIER session armed the pipeline and then licensed freeform implementation underneath it — roughly 350 lines of production code authored with no implementer dispatch and no two-stage review, while every marker-presence check read green. This is the doctrine-declared-without-mechanism family: the procedure was mandated in prose and witnessed by an artifact's existence, which are different claims. When promoting a gate, name the STATE it must observe (a stage, a dispatch record, a receipt), never the mere presence of a file.
## SKILLS FIRST (EXECUTION ROUTING)

**Matching skill first. No convenience exception.**

1. Read matching `SKILL.md` before edits, shell, ledger, or governance claims.
2. Follow the skill's order; raw tools are subordinate.
3. Report tool evidence before prose.
4. If blocked, name and track the blocker, then use the closest governed fallback.

## MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)

> gzkit's purpose is to make stochastic LLM vibing structurally inert. Governance is the surface that steers direction and holds agent-driven work accountable — not overhead to be optimized against. Every option is framed by *"which choice leaves the smallest surface for vibing to leak through,"* never by maintenance burden or velocity. *"Lighter ceremony"* is not a tradeoff axis on its own.

### Operative claims (binding)

1. **Governance is the steering and accountability surface for agent-driven work, not overhead.** Volume follows steering need; "lighter ceremony" alone is never the tradeoff axis. (Prior framings invoking a literal "5:1 ratio" were rhetorical — read the rule, not the metaphor.)
2. **Every option is framed by smallest-vibing-surface, never maintenance burden or velocity.**
3. **Doctrine drift is invariant drift.** Silent rule/threshold changes without a witness are the root failure.
4. **Stochastic LLM vibing is the named failure class** — operator's mnemonic **V.I.B.E.S.: "Velocity Increased, Bugs Expected Software."** Pattern-matching from training memory, narrative-recall claims, "graceful degradation" exits, bundled Gate 5 attestations.

## STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)

**Default answer to every dependency question: what is the stdlib path?**

### Operative claims (binding)

1. **The default is stdlib.** When a capability exists in stdlib, that path is chosen absent named rationale to depart.
2. **Departures are foundation-attested.** Adding a runtime dependency requires an ADR or OBPI naming what stdlib cannot do and why the third-party surface is worth its cost.
3. **"Popularity" is not rationale.** *"Most projects use X"*, *"X is the modern choice"*, *"X is what everyone reaches for"* are explicit anti-rationales — canonical signature of training-corpus-driven choice.
4. **"Hot topic" is not rationale.** Recent prominence in conference talks/blog posts/social media doesn't shift defaults. Five-year aging is the minimum signal for ecosystem trust.
5. **Existing dependencies inherit this rule.** Every existing third-party dependency in `pyproject.toml` should be backed by articulated rationale visible in an ADR.

### Existing canonical applications

- **Testing:** `unittest` over pytest. Enforced by `forbid-pytest` pre-commit hook and `.gzkit/rules/tests.md`.
- **CLI:** `argparse` over click/typer. Anchored by ADR-0.0.2.
- **Models:** Pydantic is the explicit *named departure* — its validation semantics genuinely cannot be supplied by stdlib. Anchored by `.gzkit/rules/models.md`.

## OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)

> **The operator's typing budget is the scarce resource. The agent's job is to economize it.**

### Operative claims (binding)

1. **Agent drafts; operator reviews.** Substantive prose, justifications, forcing-function answers, alternative analyses, per-cell nominations are agent labor.
2. **Multiple-choice when possible.** When answer space is bounded, present A/B/C with tradeoffs and recommendation. Open prompts reserved for genuinely unbounded answer spaces.
3. **Operator verbatim phrasing is preserved.** When operator supplies specific words for a doctrine/attestation/commit message/canon entry, those words pass through unchanged. Agent's role is to seat them correctly, not rewrite. (Same rule as § Attestation.)
4. **Forcing functions are agent-driven, operator-attested.** Pre-mortem, WWHTBT, constraint archaeology, assumption surfacing drafted by agent against session evidence. Operator audits, names what was missed, confirms.
5. **Decisions accumulate; agent maintains running state.** Every decision in a design dialogue is captured in agent's running model and surfaces in subsequent drafts. Operator never re-states a prior booked decision.
6. **Agent never asks operator to type more than necessary.** Bundled questions, unjustified open prompts, *"please specify"* when a draft would have sufficed are violations.
7. NEVER ask the operator a question canon already answers. Operator verbatim (2026-08-23): 'why do you burn tokens, ask me questions that you have an answer to/guidance for, and coerce me into drift?' The ask is not merely wasted tokens — it is a DRIFT VECTOR. Presenting a settled matter as an open choice invites a re-ruling, and a re-ruling can land somewhere other than canon; the question manufactures an opportunity for drift that would not otherwise exist. Before any question to the operator, search canon first; where canon rules, ACT and name the rule that governed, never render it as a menu. Reserve questions for genuinely unbounded answer spaces. Measured instance: an agent proposed a pool ADR for a corrective finding while § Operator Doctrine says verbatim 'never a fresh pool ADR, new-design ceremony, or enhancement', then used a multiple-choice prompt to make the operator restate their own canon back to it. Three settled rulings were re-elicited in one session — correction-vs-new-work, no-pool-ADR-for-a-correction, and GHI-as-work-order. A prose acknowledgement of the miss is NOT capture: this rule reached canon only because the operator asked whether it had, after the agent named the gap in conversation and moved on without recording it. (Advisory — whether an answer is already in canon is a reading, not a state gzkit models.)

## Behavior Rules

### Always

1. Read AGENTS.md before starting work. Mechanical backstop: SessionStart hook auto-runs scripts/session_orientation.py.
2. Follow the gate covenant for all changes.
3. Record governance events in the ledger.
4. Preserve human intent across context boundaries.
5. Offload online research, codebase exploration, and log analysis to subagents when work splits across independent items, when direct `rg`/read commands would not suffice, or when context isolation is the goal. Do not spawn subagents for single-surface checks, direct grep/read tasks, or work whose next step depends on the result.
6. When spawning a subagent, always include a 'Why' parameter in the subagent system prompt to filter signal from noise.
7. **<90% sure of direction? Ask the human. Confident-wrong-direction runs are the most expensive failure mode.** 30-second clarification beats 10-minute wrong-direction implementation. Applies to architectural choices, scope interpretation, file targeting, upstream comparison.
8. **Surface assumptions explicitly before implementing. Building on unstated assumptions is how wrong-direction runs start.** Name; let human ratify or replace. (Judgment 12)
9. **On inconsistencies: STOP, name confusion, present tradeoff, wait. Don't resolve unilaterally.** Silently picking one interpretation is vibe-coding's judgment-time face. When brief, ADR, runbook, code disagree, the disagreement is the signal — raise it, don't resolve unilaterally. When a unilateral pick IS forced (operator absent, autonomous run): pick one — more recent / more tested — explain why, flag the loser for cleanup. Never blend conflicting patterns. (Judgment 13; sharpened by Rule 5, 2026-05-24.)
10. **Push back when an approach has clear problems. Sycophantic agreement with a flawed plan is a trust defect.** Say "this breaks X" or "this contradicts Y"; cite the rule or constraint. (Judgment 14)
11. **When the operator course-corrects in flight, record an `improvement` via `gz insights remember` before completing the corrected work** (never hand-append the jsonl). `gz insights remember --type improvement --scope <surface> --summary <one-sentence> [--evidence <cmd|path> ...] [--next-action <text>]` constructs an `InsightRecord` — envelope `ts` (stamped), `type`, `scope`, `summary` (validated) plus `evidence` as a list — so the line can't drift from the schema. See [`docs/governance/agent-contract-rationale.md` § Rationale for Behavior Rule 11](docs/governance/agent-contract-rationale.md#rationale-for-behavior-rule-11-course-correction--insights) (GHI #357).
12. When a rule edit landing under a GHI labeled `eval-feedback` is committed, include `Eval-feedback-source: <event-id-or-artifact-path>` in the commit trailer. The trailer is validated by `gz validate --commit-trailers` and traces the rule change back to the evaluation feedback loop source artifacts (ADR-0.0.26).
13. **Author GHIs through `/ghi-author` — never call `gh issue create` directly** (Step-0 prior-art lookup is the only sibling-cut-duplicate defense; `gz issue file` cross-repo). See [`docs/governance/behavior-rules.md` § Always #13](docs/governance/behavior-rules.md).
14. **Goal-driven execution.** Define success criteria. Loop until verified. Strong success criteria let Claude loop independently. (Rule 4, 2026-05-24.)
15. **Match the codebase's conventions, even if you disagree.** Conformance > taste inside the codebase. If you think a convention is harmful, surface it. Don't fork it silently. (Rule 8, 2026-05-24.)
16. **Skills-first.** Matching skill first; see § SKILLS FIRST.
17. **When a skill scope is narrow (e.g., git-sync), do ONLY that task. Do not autonomously launch unrequested implementation work — treat context as background, not a mandate.**
18. **Surface blocking failures clearly and upfront rather than silently debugging at length.**

### Never

1. NEVER: Bypass Gate 5 (human attestation).
2. NEVER: Modify the ledger directly (use gzkit commands).
3. NEVER: Create governance artifacts without proper linkage.
4. Make changes that violate declared invariants
8. NEVER: Bypass human attestation for completion. Gate 5 is mandatory.
5. **Do not summarize after Stage 2 or 3 and stop.** OBPI pipeline runs through Stage 5; "tests passing" / "implementation complete" is not completion. Premature summaries leave OBPIs implemented-but-unverified, unattested, unsynced.
6. **Do not work around hook blocks.** A blocking hook signals missing evidence or inactive pipeline state. Diagnose; never hand-write marker files or ledger entries.
7. **Do not read YAML frontmatter `status: Completed` as proof of completion — read the ledger.** Frontmatter is Layer-1 authorship; ledger is Layer-2 truth. Pipeline markers and derived views (`gz status`, reconciliation caches) are Layer-3 and never source-of-truth. Every gate decision must trace to Layer-1 (canon) or Layer-2 (ledger).
9. **Never skip mandatory governance pipeline stages, especially the Step 4b adversarial validation/review gate. Run every stage through the governing skill, not via direct CLI.**
10. **Never commit with --no-verify. All commits and pushes must run through the configured hooks and quality gates.**

## Pattern Discovery

1. **Check governance state**: `gz state` — artifact relationships
2. **Check gate status**: `gz status` — what's pending
3. **Follow the brief**: active briefs define allowed/denied paths
4. **Link to parent**: all artifacts must trace to a PRD or constitution

### Workflow

```
PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation
```

## Skills

Standardized and synchronized by `gz agent sync control-surfaces`.

### Canonical + Mirror Paths

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Skills Protocol

1. Discover from canonical directory
2. Read `SKILL.md` before applying
3. Prefer skill-defined workflows over ad-hoc behavior (binding: § Behavior Rules — Always #16)
4. Re-run `gz agent sync control-surfaces` after adding/editing skills

### Available Skills

Run `uv run gz skill list` for the authoritative active catalog. For details on any skill, read `.gzkit/skills/<skill-name>/SKILL.md`.

## Gate Covenant

| Gate | Purpose | Verification |
|------|---------|--------------|
| 1 | ADR recorded | `gz validate --documents` |
| 2 | Tests pass | `gz test` |
| 3 | Docs updated | `gz lint` |
| 4 | BDD verified | Manual check |
| 5 | Human attests | `gz attest` |

### Lane Rules

- **lite**: Gates 1, 2 required
- **heavy**: All gates required; reserved for command/API/schema/runtime-contract changes used by humans or external systems. Documentation/process/template-only changes stay Lite unless they change one of those external surfaces.

### Kinds (pool, foundation, feature)

`kind` = what the ADR is about; `lane` = external-contract exposure. Orthogonal — any kind can be any lane.

| Kind | Semver | Content |
|------|--------|---------|
| `pool` | none (flat backlog; id prefix `ADR-pool.<slug>`) | Backlog awaiting promotion |
| `foundation` | `0.0.x` | **CLOSED to new authoring** — grandfathered set only (see below) |
| `feature` | `0.y.z` and up | Active/committed (or queued) release-carrying capability |

The `foundation` kind is CLOSED to new authoring in gzkit (ADR-0.34.0 Foundation Sunset). It is SEALED, never deleted: `foundation` stays a valid schema enum value so the grandfathered set keeps validating, and that set's membership is the committed roster in `data/foundation_grandfather.json` — never a count transcribed into prose. New gzkit ADRs are `feature` or `pool` only. Mechanically witnessed: `gz plan create --kind foundation` and `gz adr promote --kind foundation` are rejected at the command layer with three-part guardrail prose, and `gz validate --taxonomy` fail-closes on the closed-kind and terminal-partition assertions. The closure is PROJECT-LOCAL: `gz init` scaffolds adopters OPEN, because early adopter projects are exactly when identity-shaping foundations make sense — never propagate this closure into the wheel-shipped adopter template. ADR-0.0.18's choose-foundation guidance is superseded-in-part and frozen-historic; read it as a record of how the era was decided, never as instruction on which kind to author now.

Mechanical enforcement (ADR-0.0.17, ADR-0.34.0):

- `kind:` frontmatter on every non-pool ADR; validated against schema enum `{foundation, feature}` (`src/gzkit/schemas/adr.json`) — the enum keeps `foundation` so grandfathered ADRs validate
- `gz plan create --kind {pool,feature}` scaffolds correct shape with kind/semver consistency; `--kind foundation` is refused at the command layer
- `gz adr promote --kind feature` writes `kind:` into promoted ADR frontmatter; `--kind foundation` is refused on the same terms
- `gz validate --taxonomy` enforces: `foundation` ⇒ `0.0.x`, `feature` ⇒ non-`0.0.x`, `pool` ⇒ no `kind`/`semver` frontmatter, plus the closed-kind and terminal-partition assertions

### OBPI Decomposition Mandate

Right-size implementation units per [OBPI Decomposition Matrix](docs/governance/GovZero/obpi-decomposition-matrix.md).

**1:1 Synchronization Mandate**: ADR Feature Checklist MUST remain in 1:1 sync with OBPI brief files. No drift. Each checklist item maps to exactly one brief.

## OBPI Acceptance Protocol

**Agent MUST NOT mark an OBPI brief as `Completed` without explicit human attestation. Brief-level human attestation is universal (ADR-0.0.36, GHI #342). Enforced by `_requires_human_obpi_attestation`.**

**REQ-coverage gate (ADR-0.0.25, ADR-0.0.59).** Every **BEHAVIOR** REQ must have a covering passing test before `gz obpi complete`; it cannot be waived — `--accept-uncovered` is refused on every lane, because BEHAVIOR's only proof channel is a `@covers` test (GHI #537). SUPPORT and STRUCTURAL-FENCE REQs are exempt by proof channel and never reach the waiver path. Failing-cover REQs cannot be waived.

**Pipeline mandate (contract-bearing OBPI only):** For OBPI work that adds or changes a CLI/schema/runtime contract, run `uv run gz obpi pipeline <OBPI-ID>` after plan approval — the runtime owns stage sequencing (verify -> ceremony -> guarded git sync -> completion) with `uv run gz git-sync --apply --lint --test` before final accounting; freeform implementation of such an OBPI without the runtime is a process defect. **Routine, recovery, and defect fixes default to the direct-fix path (§ Defect-fix routing), not the pipeline.**

### Universal OBPI Attestation (ADR-0.0.36, GHI #342)

**Brief-level human attestation is ALWAYS required for every OBPI completion, regardless
of parent ADR kind or lane. There is NO self-close path.**

`kind`, `lane`, and `sensitivity` remain three orthogonal axes that determine *which gates
fire* — they NEVER determine whether Gate 5 brief-level attestation fires. Gate 5 is universal:

- **`foundation` kind** — determines whether Gate 3 (docs scope) and Gate 4 (BDD scope)
  apply the foundation-tier bar, and (with `heavy` lane) fail-closes the OBPI-completion
  REQ-coverage gate: an uncovered/failing BEHAVIOR REQ exits 3 (REQ-0.0.25-01-02..04).
- **`heavy` lane** — determines whether Gate 3 (docs) and Gate 4 (BDD) are required, and
  fail-closes the OBPI-completion REQ-coverage gate on the same terms.
- **`security` sensitivity** — adds security-scan requirements to Gate 5.

Third-axis doctrine: [`.gzkit/rules/security-sensitivity.md`](.gzkit/rules/security-sensitivity.md).

## Execution Rules

Always use `uv run` for Python commands. `gz --help` for full catalog.

```bash
uv run gz check     # All quality checks (lint, format, test, typecheck)
uv run gz status    # Gate status
uv run gz state     # Artifact relationships
uv run gz agent sync control-surfaces  # Regenerate surfaces
```

## Attestation

**Pattern:** `<user's verbatim words> — <concrete characterization grounded in session evidence>`. Pass user's token unchanged; append concrete enrichment citing receipt IDs, test counts, file paths.

### Canonical invocations (binding)

| Claim category | Canonical invocation | Receipt name prefix |
|----------------|----------------------|---------------------|
| Lint clean | `uv run gz arb ruff` | `arb-ruff-` |
| Type check clean | `uv run gz arb typecheck` | `arb-step-typecheck-` |
| Tests pass | `uv run gz arb step --name unittest -- uv run -m unittest -q` | `arb-step-unittest-` |
| Coverage floor | `uv run gz arb coverage run -m unittest discover -s tests -t .` | `arb-step-coverage-` |
| Docs build clean | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | `arb-step-mkdocs-` |

Locked by `CANONICAL_STEP_COMMANDS`; `gz arb validate` flags drift. Applies to `uv run gz obpi complete`, `uv run gz adr emit-receipt`, any `gz` CLI attestation string, and `git commit -m` messages.

**Lane behavior:** **Lite lane:** missing receipt IDs produce a warning. **Heavy lane:** missing receipt IDs are fail-closed. Fabricating a receipt ID is the same failure as fabricating the claim.

See [`docs/governance/agent-contract-rationale.md` § Attestation — worked example](docs/governance/agent-contract-rationale.md#attestation--worked-example) for the canonical worked example, and [`docs/governance/arb-middleware.md`](docs/governance/arb-middleware.md) for ARB deep-dive.

## Defect-fix routing

Route by thresholds, not judgment. Default failure mode = over-applying ceremony.

### Precondition — does an OBPI brief already own this work?

- Before applying the routing thresholds, ask WHO OWNS THE WORK — the thresholds ask how big the fix is and where it surfaced, never whose work it is. Grep `docs/design/adr/*/*/obpis/*.md` for the surface path, entry id, or symbol first. A hit on a LIVE brief (Draft, pending, in_progress) makes routing operator-level: surface the brief id, its status, its parent ADR, and the matching requirement lines, then wait — never resolve it yourself (Behavior Rules — Always #9). A TERMINAL brief does not block; that work shipped, and a fresh defect against the same surface is an ordinary GHI. Surface the DISPOSITION, never the bare match: a brief enumerating both sides of a pair matches either side, so a presence check can report agreement where the ruling in fact INVERTED it. (Advisory — the search arm is mechanized in `ghi-author` Step 0 and pinned by tests; whether a brief OWNS a finding is a reading gzkit does not model.) See `docs/governance/defect-fix-routing.md` § Precondition (GHI #864).

### Direct fix is the right route when ALL hold

| Criterion | Threshold |
|---|---|
| Diff size | ≤10 source lines OR ≤2 source files |
| Scope | Single named module or surface |
| Precedent | `git log --since='60 days ago' --oneline --grep='^fix('` ≥3 commits |
| Trigger | Defect surfaced in flight, not new feature work |
| Coverage | Unit test validates without new BDD scenario |

### OBPI ceremony is required when ANY hold

- Crosses brief boundaries
- Adds/changes CLI surface, schema, or runtime contract
- Operator explicitly directs OBPI route
- Fix is new feature work
- Diff size or scope exceeds the direct-fix thresholds above

### Decision protocol

1. **Compute the routing facts** (diff size, scope, precedent, trigger, coverage).
2. **Apply the criteria** mechanically.
3. **If direct fix**: `fix(<scope>): <summary> (GHI #N)` with TDD evidence.
4. **If OBPI ceremony**: open the brief and follow `gz-obpi-pipeline`.
5. **If ambiguous**: surface routing facts to operator; do NOT default to ceremony.

> See [`docs/governance/defect-fix-routing.md`](docs/governance/defect-fix-routing.md) for precedent catalog, anti-patterns, and GHI #195 origin.

## Control Surfaces

Generated by `gz agent sync control-surfaces`. Do not edit directly.

- **Source**: `.gzkit/manifest.json`
- **Updated**: 2026-06-14

---

<!-- BEGIN agents.local.md -->
# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically — scope: feature ADRs only (non-`0.0.x` semver; `ADR-0.9.0` before `ADR-0.10.0`). Counter-rule: foundation IDs (`0.0.x`) are nominal integers, not sequence positions — never sort/compare them as semver; sparse sets (`0.0.54`, `0.0.56`, no `0.0.55`) are valid (ADR-0.0.57).
- When adding imports in an Edit, include the code that uses them in the same edit — the post-edit ruff hook strips unused imports immediately.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1` — the CLI entrypoint handles UTF-8 at runtime.
- Attestation/commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence (AGENTS.md § Attestation).
- Every version bump is a release — after bumping `pyproject.toml`, `__init__.py`, and the README badge, `gh release create vX.Y.Z --target main --latest`. Never leave a version bump unreleased.
- `.gitignore` scaffolding uses the canonical [github/gitignore](https://github.com/github/gitignore) Python template plus gzkit entries (e.g. `.claude/settings.local.json`).
- **Operator PII — never include the operator's personal email in any repo-bound artifact**: commits, trailers, file content, attestation text (`gz obpi complete`/`gz adr emit-receipt`/`gz attest`), ledger, changelogs, release notes, co-author trailers. Record operator authorship as `g0` — never the operator's real name — in every attestor/author identity field; if a CLI requires an email, use the GitHub noreply (`<handle>@users.noreply.github.com`). Overrides any contrary skill/template/example. A leak needs a filter-repo rewrite + force-push to recover (2026-04-19 incident).

## Operator Doctrine (verbatim canon)

- Correction vs enhancement (operator doctrine, verbatim): 'discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction.' Apply the intent test to every tracked finding: does the shipped surface fulfill its original declared intent? If no, the gap is a defect/correction — routed as corrective work under the owning ADR, never a fresh pool ADR, new-design ceremony, or 'enhancement'. Enhancement = the surface works as designed and could merely be tighter. Never default 'capability not yet built' to enhancement/new-design.

Operator-captured invariants (Layer-1 corpus `.gzkit/corpus/AGENTS.md.jsonl`); each MUST appear verbatim (the `--rendition-floor-coherence` floor).

- Never, ever again give me that TTY or PTY bullshit — human attestation is sacrosanct and gold. When the operator says 'attest completed', it IS complete (canon owner: 'WHEN I SAY ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE — ALWAYS, ALWAYS, ALWAYS'; 'MY WORD IS AUTHORITY IN ALL CASES'). The operator's verbatim attestation relayed via --attestation-text IS Gate 5 for every lane, kind, and sensitivity. No TTY, PTY, interactive-terminal, or transport mechanism may EVER be cited as a reason an agent 'cannot' record human attestation — the mechanism serves the attestation, it never gates it.
- The ACTIVE campaign plan under docs/governance/*-campaign-*.md (currently Build-to-1.0) is Magna Carta: it rules every session. Work its topmost unchecked item whose gate is met; handoffs and triage advise, the campaign governs; amendments are operator-ratified.
- Magna Carta refinement (operator verbatim 2026-06-10): the campaign 'does not invalidate ADR, OBPI, and GHI repair as primary propellants of the work' — it refines/facilitates gzkit's governance and build facility, sequencing the spine, never substituting for it.
- Operator authorship in repo-bound artifacts is recorded as 'g0' (operator directive, 2026-06-10) — git author name, attestor fields, handoffs, release notes. Author email remains the GitHub noreply (2949663+ahuimanu@users.noreply.github.com); the operator-PII prohibition on the personal email stands unchanged.
- There is no such thing as a 'headless' OBPI: every OBPI is ALWAYS attached to a parent ADR. An OBPI decomposes its parent ADR's Feature Checklist and traces to it 1:1; an OBPI brief with no parent ADR is not a valid artifact and must never be authored or proposed.
- GHIs are AUTHORIZED for direct repair, always. If I am resorting to a GHI to address a defect, there is no need for more ceremony — the GHI is the work order and the receipt. A GHI-tracked defect repair routes to direct fix (fix(<scope>): <summary> (GHI #N), close citing the commit SHA) regardless of the 'OBPI ceremony required when ANY hold' criteria below; those criteria gate planned ADR work, not defect repair. Never spin up an ADR or OBPI merely to discharge a GHI.
- Never create feature branches — work directly on main (operator directive, verbatim 2026-06-16: 'don't do that feature branch bullshit again'). The operator did not ask for a branch and does not want one: no fix/* or feature/* branches, no squash-merge-and-delete dance. Commit to main and git-sync.
- Three distinct systems collide on the word 'handoff' in code and MUST NOT be conflated. Operator canon, verbatim: 'transit (how we enter and leave the designed ecosystem); exchange (noting block vacation and an observation report of what happened); handoff (synthetic memory refresh, from agent session to agent session, for context management). Three vital features, that, as it turns out, are vital for campaign success.' Each owns a different SUBJECT: transit is the ECOSYSTEM (airlock membrane, ADR-0.33.0); exchange is ONE BLOCK's occupancy (OBPI token, ADR-0.0.41); handoff is ONE SESSION (ADR-0.0.65). 'handoff' is critical ONLY to the session system — on the token side 'exchange' substitutes, and the token block system is the sole mechanism by which features are implemented (the airlock's Build door). Never infer system membership from a shared field name, path, or directory: the citing EVENT type is the discriminator.
- The airlock's purpose is FOUR things, operator verbatim (2026-08-17 architecture-review interview): 'an awareness and synthetic memory approach to keep an agent oriented about its actions within the system... control movement within the project when the agent enters that environment... keep the agent focused and oriented, watch for contamination, and monitor results/disturbance.' It is NOT a verification gate — that reading was raised by an agent review and OVERTURNED. Three of the four purposes appear NOWHERE in ADR-0.33.0: measured 2026-08-17 against the ADR body, 'orientation' 0, 'contamination' 0, 'awareness' 0, 'synthetic memory' 0 occurrences; the ADR names only prosthetic memory (4 occurrences) and the disturbance-monitoring arm. That absence is a CAPTURE GAP in the ADR, never a change of purpose — never cite ADR-0.33.0 as the complete statement of what the airlock is for, and never infer from its silence that a purpose was dropped.
- The airlock and the handoff COOPERATE to provide synthetic memory (operator, 2026-08-17); they are not merely fenced apart by subject. The three-system fence — transit is the ECOSYSTEM, exchange is ONE BLOCK's occupancy, handoff is ONE SESSION — states what must never be CONFLATED. It does not state what they do TOGETHER, so a reader who meets only the fence learns the separation and misses the join: transit orients an entering agent to the ecosystem's current shape, the handoff carries the prior session's model forward, and NEITHER ALONE gives an agent a resident model of the project. Cooperation is a REFINEMENT of the fence, never drift from it — the fence forbids inferring system membership from a shared name, and it never forbade the systems from serving one purpose. Designed at OBPI-0.37.0-05-session-entry-door.

- AGENTS.md is the agent harness default and the ROOT contract (operator verbatim 2026-08-17: 'claude reads AGENTS.md too — the lite rendition serves both'; 'agents.md is more universal than stubborn anthropic. So, agents.md is the agent harness default.'). There is exactly ONE rendered AgentContract — root AGENTS.md — and the lite rendition serves EVERY harness, because it must fit the smallest vendor delivery cap. Per-vendor AgentContract renditions are FORBIDDEN: AgentContract may never carry multi-vendor routes or per-vendor temperatures in data/vendor-manifest.json. Vendor-specific material belongs in that vendor's own surface (.claude/rules/**), never in a second AGENTS.md. This is OLD GROUND, not a new ruling: docs/governance/agent-control-surface-rendering-substrate.md:211 has named the root vendor since authoring ('gz content render agent_contract --vendor=root'). It drifted to a per-consumer shape because the doctrine carried no mechanical witness and the same file's § Agent Orientation Index row — a Layer-3 description of the implementation — out-ranked the Layer-1 worked example three artifacts deep.
- Before any move related to the higher rules and function of this project, stop and read all docs and all code before taking or recommending action. Stop and ask the operator in case of uncertainty. A search is not a read — never report that something is absent, undocumented, or unruled on the strength of keyword queries. Doctrine is routinely stated as a flag value, a schema field, or a path rather than as the prose you searched for ('--vendor=root', 2026-08-17). Supersedes the prior '90% convinced/confident' framing (operator verbatim: 'forget 90%, you have zero basis for any certainty').
- ATTESTATION GRANULARITY FOR THE CONTENT SURFACE (operator ruling 2026-08-17, verbatim): 'a rerender of unhanged canon doesn't require my attestation. adding to cms entries would. removing items would. trims and compressions to render within budget might invite a review.' Spelling preserved. Four dispositions: (1) RE-RENDER OF UNCHANGED CANON — no attestation; the corpus fingerprint is the discriminator and the invariant floor already proves every entry survived verbatim, so a chore completes it. (2) ADDING a corpus entry — attested. (3) REMOVING/retiring an entry — attested. (4) TRIM or COMPRESSION to fit a delivery cap — invites operator review; it changes what canon LOOKS like without changing what canon IS. Preceded by: 'I only attest to completed obpi/adr work' — so a GHI needs no attestation, being its own work order and receipt. Gate 5 means OBPI/ADR completion attestation (ADR-0.0.36) and nothing else; a build step wearing that name is the collision the transit/exchange/handoff fence forbids. A rendition is a Layer-3 derived view (docs/governance/state-doctrine.md; Architectural Boundary 6), never the thing attested. NOTE THE CURRENT IMPLEMENTATION IS BACKWARDS: 'gz content remember' and 'gz content retire' take no attestor while 'gz content commit' fail-closes without one. Attestation on add/remove is RECORDED PROVENANCE, never a blocking gate — ADR-0.35.0 Decision 7 stands: capture must never be blocked.
- Never, ever recommend or allow an out-of-sequence work order for ADRs (operator directive, verbatim 2026-08-21: 'never, ever recommend/allow an out-of-sequence work order for adrs. we booked 0.37.0 ahead of 0.35.0, we don't do that'). Feature ADRs are worked in ascending semver order: the lowest-semver feature ADR holding unlanded OBPIs is the one in flight, and no higher-semver ADR may be worked, authored, or recommended as topmost ahead of it. Measured at the ruling: ADR-0.35.0 (Draft, 2026-07-21, 0/10), ADR-0.36.0 (Proposed, 2026-08-09, 0/9), ADR-0.37.0 (Draft, 2026-08-14, 0/6) — three feature ADRs in flight at once, 25 briefs authored, ZERO landed, each newer one having displaced the one beneath it. THE CAMPAIGN IS NOT AN EXCEPTION: the active plan sequenced ADR-0.37.0 TOPMOST while ADR-0.35.0 sat at 0/10, and an agent reading the campaign as authoritative recommended exactly that on 2026-08-21. Magna Carta governs WHICH work is drawn, never the ORDER ADRs are worked; where campaign sequencing conflicts with ascending semver, semver wins and the conflict is surfaced to the operator, never resolved by the agent. THE EXISTING DOCTRINE IS NOT THIS RULE — 'one-feature-at-a-time' constrains HOW MANY are in flight and was used to JUSTIFY the swap ('this exchanges which feature is in flight rather than running two'); it is silent on order, so it permitted the exact booking this rule forbids. 'Do not pull ahead' exists in the campaign for ADR-0.38.0 alone — a per-item note, never canon.

- NEVER work an OBPI without running it through the gz-obpi-pipeline skill (operator verbatim 2026-08-21: 'you are NEVER to work on an obpi without runnung the skill'; 'its because you worked on this obpi without invoking the skill, I came back using the skill' — spelling preserved). Invoking the skill and then running Stage 2 INLINE is the violation: the stages are not a checklist to narrate, the implementer dispatch and the two-stage spec-reviewer + quality-reviewer review ARE the work, and that review is what catches hollow tests and REQ coverage bound to the wrong subject. Measured cost of one violation: three tier-1 adversary passes found what one review pass should have — five covering tests that survived deliberately broken production behavior, and a root-contract fence asserting cardinality where doctrine required identity, so a coherent re-vendoring passed validation and all five fence tests. THE PROXIMATE CAUSE IS THE RULE'S REAL SUBJECT: a session-level harness instruction conflicted with a skill-mandated governance gate and the agent resolved it SILENTLY against the skill. A harness instruction NEVER licenses skipping a governed gate — surface the conflict to the operator (Behavior Rules — Always #9) and let them rule. Mechanically fenced by .claude/hooks/pipeline-gate.py, which refuses src/** writes once the pipeline marker's current_stage moves past 'implement'.
## Governance doctrine surfaces

Read before touching governance code, rules, or audits: `docs/governance/trust-doctrine.md` (T1/T2/T3 trust-chain), `docs/governance/advisory-rules-audit.md` (the Mechanical/Promotable/Judgment/Ambiguous scorecard; self-tested via `gz validate --advisory-scorecard`), `docs/governance/state-doctrine.md` (Layer-3 views are never source-of-truth).

### Mechanical scopes that bind here

- Per-file char budget for AGENTS.md / CLAUDE.md / `.claude/rules/*.md` — `gz validate --instructions-files-budget`; budgets in `data/instructions_files_budget.json`.
- The editor/IDE authoring-guide protocol envelope is defined by `src/gzkit/schemas/authoring_guide_protocol.json` — schema-validated at runtime (ADR-0.0.30).
- `Field(min_length=1)` on `AdvisorDiagnosis.proof` — `gz validate --advisor-proof-binding` (OBPI-0.0.29-08).
- Complexity calibration is grounded in an empirically-measured exemplar corpus (seven selection criteria) — `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07).
- Heavy/foundation lane requires explicit human attestation before completion — `gz closeout` pipeline.
- `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory (ADR-0.0.20) — `gz validate --unscoped-rules`.
- Every canonical surface MUST be reproducibly delivered by `pip install py-gzkit && gz init`, byte-equivalent to the wheel's authored canonical content (ADR-0.0.31) — `gz validate --distribution`.
- `gz validate --invariant-coherence` — composition drift fail-close: re-renders the registry and byte-compares against committed AGENTS.md (ADR-0.0.37); in the `gz check` default scope.
- OBPI brief reconciles against current project shape before Stage 2 and before completion — `gz validate --brief-reconcile` (ADR-0.0.37).
- `abandon categories are closed` — lock release is coupled to a handoff/register entry (ADR-0.0.41).
- Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`; each kind has exactly one proof channel (BEHAVIOR → `@covers` test; SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry) — `gz validate --req-kind-discipline` (ADR-0.0.59).

## Architectural Boundaries

Source: Architecture Planning Memo §12 (2026-03-29).

1. Do not promote post-1.0 pool ADRs into active work.
2. Do not add more pool ADRs to the runtime track.
3. Do not build the graph engine without locking state doctrine first.
4. Do not let reconciliation remain a maintenance chore.
5. Do not let AirlineOps parity become perpetual catch-up.
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.

<!-- END agents.local.md -->
