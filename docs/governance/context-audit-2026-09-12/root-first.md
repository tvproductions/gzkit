# Root AGENTS.md first-half editorial audit

Scope: lines1–350; 248 nonblank lines; 19 sections. Source: `f53831450e7f0a5457966e83a16f8be7b6fdb016b255e58946211109cdffc1ac`.

Persona: main-session — craftsperson. Audit only; no selected edits and no repo writes.

Measured input: **30,995 UTF-8 bytes**. Full editorial proposal: **5,469 bytes**, **25,526 bytes saved**. These are literal text deltas, not a claim that CMS accepts the proposal or that invariant/scorecard constraints have been waived.

## Interpretation

The strongest reductions delete generic persistence/coaching and move task-specific recipes on demand. An invariant tier is a write-path constraint, not a reason to preserve a rule forever. The full proposal deliberately surfaces the required canon decisions instead of quietly relaxing rules. It is not an ordinary-diet executable patch.

Four long blocks containing history (lines60,115,215,301) are invariant corpus entries. Their full text is in the JSON source mapping; shortened successors require explicit operator selection and governed retirement/capture. Semantic source mapping is partial: declared ownership does not prove every line is captured (#983).

Do not use a passing bullet-retention check over AGENTS+CLAUDE+Claude rules as proof of Codex delivery: this audit preserves the distinction between aggregate surface presence and actual always-loaded context.

## Line classification counts

| Disposition | Nonblank lines |
|---|---:|
| DELETE | 8 |
| DUPLICATE | 51 |
| KEEP binding | 94 |
| LIFT rationale-history | 18 |
| ON-DEMAND | 40 |
| VERIFY conflict | 37 |

## Smallest first safe batch

Remove two duplicate Skills Protocol lines — **134 bytes**.

Both obligations remain verbatim in SKILLS FIRST lines65–66. No role/policy/command behavior changes. Renumber the surviving fourth item to second; this changes no byte count. No effective corpus entry is addressed to skills. Source is declared unowned, so do not hand-edit AGENTS or fabricate CMS provenance.

Operator selects these exact two removals; main session resolves governed CMS/onboarding versus approved carry-forward rendition path and verifies byte/retention/ownership coherence. No blanket authorization inferred.

Before:
````markdown
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
````

Proposed after:
````markdown
## Skills

Standardized and synchronized by `gz agent sync control-surfaces`.

### Canonical + Mirror Paths

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Skills Protocol

1. Discover from canonical directory
2. Re-run `gz agent sync control-surfaces` after adding/editing skills

### Available Skills

Run `uv run gz skill list` for the authoritative active catalog. For details on any skill, read `.gzkit/skills/<skill-name>/SKILL.md`.
````

## Section proposals

| Section | Lines | Before B | After B | Saving B | Source ownership |
|---|---:|---:|---:|---:|---|
| agents-md | 1–4 | 50 | 46 | 4 | unowned |
| project-identity | 5–10 | 123 | 70 | 53 | unowned |
| persona | 11–26 | 1180 | 287 | 893 | unowned |
| prime-directive-ownership | 27–40 | 1581 | 0 | 1581 | corpus-owned |
| do-it-right-craftsmanship-maxim | 41–60 | 3214 | 299 | 2915 | corpus-owned |
| skills-first-execution-routing | 61–69 | 347 | 0 | 347 | unowned |
| make-llm-stochastic-vibes-inert-anti-vibing-mantra | 70–82 | 1753 | 0 | 1753 | corpus-owned |
| stdlib-first-doctrine-dependency-posture | 83–102 | 1658 | 281 | 1377 | corpus-owned |
| operator-economy-of-effort-design-dialogue-mode | 103–118 | 2957 | 260 | 2697 | corpus-owned |
| behavior-rules | 119–154 | 5234 | 576 | 4658 | corpus-owned |
| pattern-discovery | 155–167 | 383 | 266 | 117 | unowned |
| skills | 168–189 | 688 | 368 | 320 | unowned |
| gate-covenant | 190–229 | 3107 | 593 | 2514 | corpus-owned |
| obpi-acceptance-protocol | 230–254 | 2180 | 478 | 1702 | corpus-owned |
| execution-rules | 255–274 | 690 | 245 | 445 | unowned |
| attestation | 275–294 | 1545 | 435 | 1110 | corpus-owned |
| defect-fix-routing | 295–330 | 2356 | 514 | 1842 | corpus-owned |
| control-surfaces | 331–340 | 191 | 247 | -56 | unowned |
| local-agent-rules | 341–350 | 1758 | 504 | 1254 | unowned |

### agents-md — lines1–4

Identity only; no engineering detail inferred.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
# AGENTS.md

Universal agent contract for gzkit.
````

Proposed compact after:
````markdown
# AGENTS.md

Project instructions for gzkit.
````

### project-identity — lines5–10

Delete tautological purpose/name repetition. Move the unique execution default here from Execution Rules.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## Project Identity

**Name**: gzkit
**Purpose**: A gzkit-governed project
**Tech Stack**: Python 3.13+ with uv, ruff, ty
````

Proposed compact after:
````markdown
## Project Identity

Python 3.13+; use `uv run` for Python commands.
````

### persona — lines11–26

Keep required persona/default. Load specialist traits when assigning that specialist, rather than preload six role rows.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Persona

Every agent frame MUST include a Persona. Default: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Read the applicable definition in [`.gzkit/personas/`](.gzkit/personas/) when assigning a role; compose traits, not generic expertise claims.
````

### prime-directive-ownership — lines27–40

Delete repeated generic persistence/competence coaching. Move the unique defect-accounting obligation to Defect-fix routing; command/output documentation coherence survives in DO IT RIGHT. Requires explicit corpus retirement/supersession, not ordinary rendition trim.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 7; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
[DELETE SECTION; retain any transferred obligation at its named destination.]
````

### do-it-right-craftsmanship-maxim — lines41–60

Retain coupled-surface and evidence boundaries. Delete generic craftsmanship exhortations; lift incident history and examples to the existing rationale page. Title/section-id change requires governed ownership/routing reconciliation.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 11; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Engineering evidence

When a change affects a reader, validator, or documented command output, verify and update that consumer in the same change. Verify claimed CLI behavior by running it. Gate evidence must witness the required state or action; a marker or file being present is insufficient.
````

### skills-first-execution-routing — lines61–69

Consolidate skill routing into Skills; the same obligation occurs here, Always16, and Skills Protocol.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## SKILLS FIRST (EXECUTION ROUTING)

**Matching skill first. No convenience exception.**

1. Read matching `SKILL.md` before edits, shell, ledger, or governance claims.
2. Follow the skill's order; raw tools are subordinate.
3. Report tool evidence before prose.
4. If blocked, name and track the blocker, then use the closest governed fallback.
````

Proposed compact after:
````markdown
[DELETE SECTION; retain any transferred obligation at its named destination.]
````

### make-llm-stochastic-vibes-inert-anti-vibing-mantra — lines70–82

Move philosophical framing, mnemonic and explanatory history to docs/governance/agent-contract-rationale.md. Recorded authority for doctrine changes is retained in the second-half operator contract; do not infer permission to relax governance.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 6; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)

> gzkit's purpose is to make stochastic LLM vibing structurally inert. Governance is the surface that steers direction and holds agent-driven work accountable — not overhead to be optimized against. Every option is framed by *"which choice leaves the smallest surface for vibing to leak through,"* never by maintenance burden or velocity. *"Lighter ceremony"* is not a tradeoff axis on its own.

> See [`docs/governance/agent-contract-rationale.md` § Anti-vibing mantra](docs/governance/agent-contract-rationale.md#anti-vibing-mantra--relationship-to-the-rest-of-the-contract) for the rationale and relationship to the other contract pillars; see [`docs/governance/harness-engineering-appraisal.md`](docs/governance/harness-engineering-appraisal.md) for the appraisal of gzkit's harness fitness against the Böckeler ("Harness Engineering") and Greyling ("98% of Claude Code Is Not AI") external theses.

### Operative claims (binding)

1. **Governance is the steering and accountability surface for agent-driven work, not overhead.** Volume follows steering need; "lighter ceremony" alone is never the tradeoff axis. (Prior framings invoking a literal "5:1 ratio" were rhetorical — read the rule, not the metaphor.)
2. **Every option is framed by smallest-vibing-surface, never maintenance burden or velocity.**
3. **Doctrine drift is invariant drift.** Silent rule/threshold changes without a witness are the root failure.
4. **Stochastic LLM vibing is the named failure class** — operator's mnemonic **V.I.B.E.S.: "Velocity Increased, Bugs Expected Software."** Pattern-matching from training memory, narrative-recall claims, "graceful degradation" exits, bundled Gate 5 attestations.
````

Proposed compact after:
````markdown
[DELETE SECTION; retain any transferred obligation at its named destination.]
````

### stdlib-first-doctrine-dependency-posture — lines83–102

Keep concrete stack/dependency boundary. Propose deleting popularity examples and arbitrary five-year aging test; this changes policy, not merely length. Resolve foundation-attested wording against sealed foundation authoring before choosing replacement. Needs operator ruling and corpus update.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 10; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)

**Default answer to every dependency question: what is the stdlib path?**

> See [`docs/governance/agent-contract-rationale.md` § Stdlib-First doctrine](docs/governance/agent-contract-rationale.md#stdlib-first-doctrine--rationale) for the corpus-bias rationale, opinionated-defaults framing, and relationship to the Exemplar-Corpus Doctrine.

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
````

Proposed compact after:
````markdown
## Dependencies

Use stdlib by default. A runtime dependency requires ADR/OBPI rationale naming the capability stdlib cannot supply; popularity alone is insufficient. Use `unittest` (pytest is forbidden), `argparse`, and Pydantic as the existing named model-validation exception.
````

### operator-economy-of-effort-design-dialogue-mode — lines103–118

Retain operator-specific interaction commitments once. Delete repetitive typing-budget coaching and generic multiple-choice prescription; lift the measured incident. Corpus invariants make this a reviewed canon-change proposal.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 1; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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

> See [`docs/governance/agent-contract-rationale.md` § Operator economy](docs/governance/agent-contract-rationale.md#operator-economy--why-this-is-canon) for rationale and anti-pattern catalog.
````

Proposed compact after:
````markdown
## Operator interaction

Draft substantive decisions for operator review. Carry accepted decisions forward. Consult canon before asking and do not reopen settled rulings. Preserve operator-supplied wording in canon, attestation and requested commit messages.
````

### behavior-rules — lines119–154

Keep project-specific ledger, trailer and hook boundaries. Lift workflow details to governing skills. Generic persistence, confidence percentages, repetition of scope and skill rules are deletion candidates; preserve operator-only initiation and full pipeline completion in the second-half contract / on-demand pipeline skill. Do not apply section renaming before ownership reconciliation.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 16; exact Mechanical/Promotable scorecard matches changed: 2. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Governance boundaries

- Record course corrections through `gz-insights-remember` before completing the corrected work.
- For a committed rule edit under an `eval-feedback` GHI, include `Eval-feedback-source: <event-id-or-artifact-path>` in the commit trailer.
- Use governed commands for ledger writes. Do not hand-write pipeline markers or work around hook blocks.
- Completion evidence comes from the ledger, never a brief's `status: Completed` or a derived status view.
- Never commit with `--no-verify`; commits and pushes run the configured hooks and quality gates.
````

### pattern-discovery — lines155–167

Keep topology and entry points, not a repeated command checklist. Status output is a derived view, not authority.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## Pattern Discovery

1. **Check governance state**: `gz state` — artifact relationships
2. **Check gate status**: `gz status` — what's pending
3. **Follow the brief**: active briefs define allowed/denied paths
4. **Link to parent**: all artifacts must trace to a PRD or constitution

### Workflow

```
PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation
```
````

Proposed compact after:
````markdown
## Project map

`PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation`

Use `gz state` for artifact relationships and `gz status` for workflow fronts and gates. Read the active brief for allowed and denied paths; artifacts require parent linkage.
````

### skills — lines168–189

Keep one execution-routing instruction, discovery command and source/mirror direction. Copilot roster needs current-state verification; proposed omission reflects removal rather than assuming the old roster remains authoritative.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 1. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Skills

Read the matching `.gzkit/skills/<name>/SKILL.md` before acting and follow its order. `uv run gz skill list` lists the active catalog. After canonical skill changes, run `uv run gz agent sync control-surfaces`.

Canonical skills: `.gzkit/skills`; Codex mirror: `.agents/skills`; Claude mirror: `.claude/skills`. Edit canonical sources; let sync propagate.
````

### gate-covenant — lines190–229

Move detailed gate commands, taxonomy mechanics and decomposition procedure to named skills/runbooks. Preserve actual lane, foundation/adopter and linkage boundaries. Full invariant paragraph215 cannot be truncated by a normal diet; this is a proposed corpus supersession. Lane text must expressly preserve universal completion attestation.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 1; exact Mechanical/Promotable scorecard matches changed: 1. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Gate covenant

- Lite requires Gates 1–2; Heavy adds docs and BDD gates for CLI/API/schema/runtime contracts. Every OBPI completion requires explicit human attestation regardless of lane.
- `kind` and `lane` are independent. gzkit permits new `feature` or `pool` ADRs; the sealed foundation roster is `data/foundation_grandfather.json`. This closure is project-local: adopter scaffolds remain open. Feature IDs use semver; foundation IDs are nominal identifiers.
- ADR checklist items and OBPI briefs correspond 1:1. Use the governing ADR/OBPI skill for gate commands and decomposition.
````

### obpi-acceptance-protocol — lines230–254

State proof-channel and security boundaries once. Remove repeated universal-attestation paragraphs, now retained in Gate covenant. Retire old contract-bearing-only pipeline wording in favor of current operator-only/all-OBPI ruling after explicit review; do not silently treat this as neutral compression.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## OBPI acceptance

Every BEHAVIOR REQ needs a passing `@covers` test; uncovered or failing BEHAVIOR proof cannot be waived. SUPPORT and STRUCTURAL-FENCE use their declared proof channels. Security sensitivity adds security-scan requirements independently of lane and kind.

Only operator-initiated OBPI work may enter `gz-obpi-pipeline`; the skill owns implementation, verification, independent review, attestation and final accounting. GHI repair follows Defect-fix routing.
````

### execution-rules — lines255–274

Move command catalog and performance rationale to skills. Retain fast-check limitation and tested/staged-tree identity; uv rule retained in Project Identity. Changing literal git add -A to intended changes is an explicit reviewed clarification, not an assumed equivalent.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## Execution Rules

Always use `uv run` for Python commands. `gz --help` for full catalog.

```bash
uv run gz check     # All quality checks (lint, format, test, typecheck)
uv run gz check --fast  # Inner loop: skips suite/behave/docs; never satisfies the gate
uv run gz status    # Gate status
```

`git add -A` BEFORE `gz check`. A full pass is recorded as verified only when
nothing is unstaged, because the gate must have tested the tree a commit will
carry — so on a dirty tree the pre-push `--reuse-verified` gate cannot reuse it
and pays the whole suite again.

```bash
uv run gz state     # Artifact relationships
uv run gz agent sync control-surfaces  # Regenerate surfaces
```
````

Proposed compact after:
````markdown
## Verification

Use `gz-check` for verification. `gz check --fast` is an inner-loop check and never satisfies the gate. A reusable full check verifies the staged tree: stage the intended changes first. Use `git-sync` for commit/push workflow.
````

### attestation — lines275–294

Move five command recipes/prefixes to gz-arb. This is subject to explicit Mechanical-bullet-retention policy review: present chore requires these load-bearing instructions remain per-turn. Preserve evidence rule, universal human attestation elsewhere, and operator wording once.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## Attestation

**Pattern:** `<user's verbatim words> — <concrete characterization grounded in session evidence>`. Pass user's token unchanged; append concrete enrichment citing receipt IDs, test counts, file paths.

### Canonical invocations (binding)

| Claim category | Canonical invocation | Receipt name prefix |
|----------------|----------------------|---------------------|
| Lint clean | `uv run gz arb ruff` | `arb-ruff-` |
| Type check clean | `uv run gz arb typecheck` | `arb-step-typecheck-` |
| Tests pass | `uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer` | `arb-step-unittest-` |
| Coverage floor | `uv run gz arb coverage run -m unittest discover -s tests -t .` | `arb-step-coverage-` |
| Docs build clean | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | `arb-step-mkdocs-` |

Locked by `CANONICAL_STEP_COMMANDS`; `gz arb validate` flags drift. Applies to `uv run gz obpi complete`, `uv run gz adr emit-receipt`, any `gz` CLI attestation string, and `git commit -m` messages.

**Lane behavior:** **Lite lane:** missing receipt IDs produce a warning. **Heavy lane:** missing receipt IDs are fail-closed. Fabricating a receipt ID is the same failure as fabricating the claim.

See [`docs/governance/agent-contract-rationale.md` § Attestation — worked example](docs/governance/agent-contract-rationale.md#attestation--worked-example) for the canonical worked example, and [`docs/governance/arb-middleware.md`](docs/governance/arb-middleware.md) for ARB deep-dive.
````

Proposed compact after:
````markdown
## Attestation evidence

Use the operator's verbatim words plus concrete evidence: receipt IDs, counts and artifact paths. Use `gz-arb` for canonical receipt-producing commands; bare lint/test/docs commands do not establish attestation evidence. Missing required receipts fail closed on Heavy and warn on Lite; never fabricate a receipt.

See [ARB middleware](docs/governance/arb-middleware.md) for exact command and receipt schemas.
````

### defect-fix-routing — lines295–330

Replace stale threshold-first rule with already-recorded operator precedence. Remove threshold matrix and procedure from always-loaded context, retain it only in the correctly scoped on-demand workflow. Line301 is invariant and would require corpus supersession; no live brief is initiated by this recommendation.

Declared corpus-owned; exact entry matches above distinguish real source content from the uncovered remainder. #983 means section label alone is not source coverage.

Invariant entries changed: 1; exact Mechanical/Promotable scorecard matches changed: 0. Unmatched text is not implicitly compressible.

Exact before:
````markdown
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
````

Proposed compact after:
````markdown
## Defect-fix routing

A GHI is authorization for direct repair; do not create an ADR/OBPI merely to discharge one. Before repair, search live briefs for the surface and read the matching requirements and disposition. If a live brief owns the work, surface that ownership for an operator ruling; do not initiate its machinery.

Record every defect through `ghi-author`, a governed insight, or brief evidence. Use `ghi-close` for authorized repair and verification; planned ADR/OBPI work uses its governing skill.
````

### control-surfaces — lines331–340

Replace misleading Source:manifest attribution and stale Updated date with actual corpus→rendition→root direction. This is a source-attribution correction requiring validation, not evidence that manifest formerly owned these bytes.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 1. Unmatched text is not implicitly compressible.

Exact before:
````markdown
## Control Surfaces

Generated by `gz agent sync control-surfaces`. Do not edit directly.

- **Source**: `.gzkit/manifest.json`
- **Updated**: 2026-06-14

---

<!-- BEGIN agents.local.md -->
````

Proposed compact after:
````markdown
## Control surfaces

Root AGENTS.md is generated playback of the committed `root` rendition from `.gzkit/corpus/AGENTS.md.jsonl`. Use the content skills for canon changes and `gz-agent-sync` for delivery; do not edit generated surfaces directly.
````

### local-agent-rules — lines341–350

Keep unique ordering/encoding/release/privacy facts. Lift import-hook details and gitignore template recipe to appropriate Python/bootstrap workflow. Remove duplicate attestation wording and incident-repair anecdote. Semantic ordering, UTF8 and release claims are Mechanical: exact changes require retention review, not silent removal.

Declared unowned; carried forward from prior rendition. Do not invent a corpus entry. Source onboarding or explicitly authorized rendition treatment must be planned before change.

Invariant entries changed: 0; exact Mechanical/Promotable scorecard matches changed: 2. Unmatched text is not implicitly compressible.

Exact before:
````markdown
# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically — scope: feature ADRs only (non-`0.0.x` semver; `ADR-0.9.0` before `ADR-0.10.0`). Counter-rule: foundation IDs (`0.0.x`) are nominal integers, not sequence positions — never sort/compare them as semver; sparse sets (`0.0.54`, `0.0.56`, no `0.0.55`) are valid (ADR-0.0.57).
- When adding imports in an Edit, include the code that uses them in the same edit — the post-edit ruff hook strips unused imports immediately.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1` — the CLI entrypoint handles UTF-8 at runtime.
- Attestation/commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence (AGENTS.md § Attestation).
- Every version bump is a release — after bumping `pyproject.toml`, `__init__.py`, and the README badge, `gh release create vX.Y.Z --target main --latest`. Never leave a version bump unreleased.
- `.gitignore` scaffolding uses the canonical [github/gitignore](https://github.com/github/gitignore) Python template plus gzkit entries (e.g. `.claude/settings.local.json`).
- **Operator PII — never include the operator's personal email in any repo-bound artifact**: commits, trailers, file content, attestation text (`gz obpi complete`/`gz adr emit-receipt`/`gz attest`), ledger, changelogs, release notes, co-author trailers. Record operator authorship as `g0` — never the operator's real name — in every attestor/author identity field; if a CLI requires an email, use the GitHub noreply (`<handle>@users.noreply.github.com`). Overrides any contrary skill/template/example. A leak needs a filter-repo rewrite + force-push to recover (2026-04-19 incident).
````

Proposed compact after:
````markdown
# Local Agent Rules

- Feature ADR identifiers sort by semver; foundation identifiers are nominal integers and may be sparse.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1`; the CLI handles UTF-8.
- Every version bump is a release; use `gz-patch-release` and `git-sync` to carry it through publication.
- Never put the operator's personal email in repository artifacts. Record authorship/attestor identity as `g0`; use the GitHub noreply address when an email is required.
````

## Every nonblank source line

| Line | Disposition | Corpus invariant lock | Reason / destination |
|---:|---|---|---|
| 1 | KEEP binding | no exact entry on line; not proof of free edit | agents-md; see exact section before/after and JSON source map |
| 3 | KEEP binding | no exact entry on line; not proof of free edit | agents-md; see exact section before/after and JSON source map |
| 5 | KEEP binding | no exact entry on line; not proof of free edit | project-identity; see exact section before/after and JSON source map |
| 7 | KEEP binding | no exact entry on line; not proof of free edit | project-identity; see exact section before/after and JSON source map |
| 8 | DELETE | no exact entry on line; not proof of free edit | project-identity; see exact section before/after and JSON source map |
| 9 | KEEP binding | no exact entry on line; not proof of free edit | project-identity; see exact section before/after and JSON source map |
| 11 | KEEP binding | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 13 | KEEP binding | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 15 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 16 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 17 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 18 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 19 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 20 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 21 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 22 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 24 | KEEP binding | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 25 | ON-DEMAND | no exact entry on line; not proof of free edit | persona; see exact section before/after and JSON source map |
| 27 | ON-DEMAND | no exact entry on line; not proof of free edit | prime-directive-ownership; see exact section before/after and JSON source map |
| 29 | DELETE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 30 | DUPLICATE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 31 | DUPLICATE | no exact entry on line; not proof of free edit | prime-directive-ownership; see exact section before/after and JSON source map |
| 32 | DUPLICATE | no exact entry on line; not proof of free edit | prime-directive-ownership; see exact section before/after and JSON source map |
| 33 | DUPLICATE | no exact entry on line; not proof of free edit | prime-directive-ownership; see exact section before/after and JSON source map |
| 34 | DUPLICATE | no exact entry on line; not proof of free edit | prime-directive-ownership; see exact section before/after and JSON source map |
| 35 | DELETE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 36 | DUPLICATE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 37 | DELETE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 38 | KEEP binding | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 39 | DELETE | yes; reviewed canon change required | prime-directive-ownership; see exact section before/after and JSON source map |
| 41 | KEEP binding | no exact entry on line; not proof of free edit | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 43 | DUPLICATE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 45 | DELETE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 46 | KEEP binding | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 47 | DELETE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 48 | DUPLICATE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 49 | KEEP binding | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 50 | DUPLICATE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 51 | DELETE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 52 | VERIFY conflict | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 53 | DUPLICATE | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 54 | KEEP binding | no exact entry on line; not proof of free edit | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 55 | DUPLICATE | no exact entry on line; not proof of free edit | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 56 | DUPLICATE | no exact entry on line; not proof of free edit | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 58 | LIFT rationale-history | no exact entry on line; not proof of free edit | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 60 | LIFT rationale-history | yes; reviewed canon change required | do-it-right-craftsmanship-maxim; see exact section before/after and JSON source map |
| 61 | ON-DEMAND | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 63 | DUPLICATE | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 65 | DUPLICATE | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 66 | DUPLICATE | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 67 | DUPLICATE | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 68 | DUPLICATE | no exact entry on line; not proof of free edit | skills-first-execution-routing; see exact section before/after and JSON source map |
| 70 | ON-DEMAND | no exact entry on line; not proof of free edit | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 72 | DUPLICATE | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 74 | LIFT rationale-history | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 76 | ON-DEMAND | no exact entry on line; not proof of free edit | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 78 | LIFT rationale-history | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 79 | DUPLICATE | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 80 | LIFT rationale-history | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 81 | LIFT rationale-history | yes; reviewed canon change required | make-llm-stochastic-vibes-inert-anti-vibing-mantra; see exact section before/after and JSON source map |
| 83 | KEEP binding | no exact entry on line; not proof of free edit | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 85 | KEEP binding | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 87 | LIFT rationale-history | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 89 | KEEP binding | no exact entry on line; not proof of free edit | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 91 | KEEP binding | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 92 | VERIFY conflict | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 93 | LIFT rationale-history | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 94 | LIFT rationale-history | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 95 | KEEP binding | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 97 | KEEP binding | no exact entry on line; not proof of free edit | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 99 | KEEP binding | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 100 | KEEP binding | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 101 | LIFT rationale-history | yes; reviewed canon change required | stdlib-first-doctrine-dependency-posture; see exact section before/after and JSON source map |
| 103 | KEEP binding | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 105 | DUPLICATE | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 107 | KEEP binding | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 109 | KEEP binding | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 110 | DUPLICATE | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 111 | DUPLICATE | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 112 | DUPLICATE | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 113 | KEEP binding | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 114 | DUPLICATE | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 115 | LIFT rationale-history | yes; reviewed canon change required | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 117 | LIFT rationale-history | no exact entry on line; not proof of free edit | operator-economy-of-effort-design-dialogue-mode; see exact section before/after and JSON source map |
| 119 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 121 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 123 | VERIFY conflict | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 124 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 125 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 126 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 127 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 128 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 129 | VERIFY conflict | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 130 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 131 | VERIFY conflict | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 132 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 133 | LIFT rationale-history | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 134 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 135 | LIFT rationale-history | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 136 | DUPLICATE | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 137 | DUPLICATE | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 138 | DUPLICATE | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 139 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 140 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 142 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 144 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 145 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 146 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 147 | DUPLICATE | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 148 | DUPLICATE | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 149 | DUPLICATE | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 150 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 151 | KEEP binding | no exact entry on line; not proof of free edit | behavior-rules; see exact section before/after and JSON source map |
| 152 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 153 | KEEP binding | yes; reviewed canon change required | behavior-rules; see exact section before/after and JSON source map |
| 155 | KEEP binding | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 157 | DUPLICATE | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 158 | DUPLICATE | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 159 | DUPLICATE | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 160 | DUPLICATE | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 162 | KEEP binding | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 164 | KEEP binding | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 165 | KEEP binding | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 166 | KEEP binding | no exact entry on line; not proof of free edit | pattern-discovery; see exact section before/after and JSON source map |
| 168 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 170 | DUPLICATE | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 172 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 174 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 175 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 176 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 177 | VERIFY conflict | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 179 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 181 | DUPLICATE | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 182 | DUPLICATE | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 183 | DUPLICATE | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 184 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 186 | KEEP binding | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 188 | DUPLICATE | no exact entry on line; not proof of free edit | skills; see exact section before/after and JSON source map |
| 190 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 192 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 193 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 194 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 195 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 196 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 197 | VERIFY conflict | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 198 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 200 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 202 | VERIFY conflict | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 203 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 205 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 207 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 209 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 210 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 211 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 212 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 213 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 215 | LIFT rationale-history | yes; reviewed canon change required | gate-covenant; see exact section before/after and JSON source map |
| 217 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 219 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 220 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 221 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 222 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 224 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 226 | ON-DEMAND | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 228 | KEEP binding | no exact entry on line; not proof of free edit | gate-covenant; see exact section before/after and JSON source map |
| 230 | KEEP binding | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 232 | DUPLICATE | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 234 | KEEP binding | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 236 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 238 | KEEP binding | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 240 | DUPLICATE | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 241 | DUPLICATE | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 243 | DUPLICATE | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 244 | DUPLICATE | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 246 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 247 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 248 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 249 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 250 | VERIFY conflict | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 251 | KEEP binding | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 253 | KEEP binding | no exact entry on line; not proof of free edit | obpi-acceptance-protocol; see exact section before/after and JSON source map |
| 255 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 257 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 259 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 260 | ON-DEMAND | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 261 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 262 | ON-DEMAND | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 263 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 265 | VERIFY conflict | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 266 | VERIFY conflict | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 267 | VERIFY conflict | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 268 | VERIFY conflict | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 270 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 271 | ON-DEMAND | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 272 | ON-DEMAND | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 273 | KEEP binding | no exact entry on line; not proof of free edit | execution-rules; see exact section before/after and JSON source map |
| 275 | KEEP binding | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 277 | DUPLICATE | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 279 | KEEP binding | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 281 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 282 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 283 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 284 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 285 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 286 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 287 | ON-DEMAND | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 289 | KEEP binding | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 291 | KEEP binding | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 293 | LIFT rationale-history | no exact entry on line; not proof of free edit | attestation; see exact section before/after and JSON source map |
| 295 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 297 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 299 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 301 | KEEP binding | yes; reviewed canon change required | defect-fix-routing; see exact section before/after and JSON source map |
| 303 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 305 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 306 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 307 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 308 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 309 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 310 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 311 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 313 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 315 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 316 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 317 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 318 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 319 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 321 | KEEP binding | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 323 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 324 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 325 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 326 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 327 | VERIFY conflict | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 329 | LIFT rationale-history | no exact entry on line; not proof of free edit | defect-fix-routing; see exact section before/after and JSON source map |
| 331 | KEEP binding | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 333 | KEEP binding | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 335 | VERIFY conflict | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 336 | VERIFY conflict | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 338 | KEEP binding | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 340 | KEEP binding | no exact entry on line; not proof of free edit | control-surfaces; see exact section before/after and JSON source map |
| 341 | KEEP binding | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 343 | KEEP binding | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 344 | ON-DEMAND | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 345 | KEEP binding | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 346 | DUPLICATE | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 347 | KEEP binding | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 348 | ON-DEMAND | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |
| 349 | LIFT rationale-history | no exact entry on line; not proof of free edit | local-agent-rules; see exact section before/after and JSON source map |

## Concrete conflicts for operator review

- Line129 confidence threshold is superseded by the later operator rule requiring relevant docs/code reads before governance recommendations; retain neither a contradictory percentage nor duplicate history in a final design.
- Line236 says contract-bearing OBPI only, while later canon requires operator initiation and skill execution for all OBPI work. Use the later authority; do not interpret narrower prose as initiation permission.
- Lines297–327 threshold-first routing omit the later GHI direct-repair override. Rewrite once with correct precedence; do not re-ask the already-settled ruling.
- Line92 foundation-attested wording needs clarification against the foundation sunset; do not invent an exception or substitute feature policy without review.
- Lines335–336 attribute source to the manifest and carry a stale update date; actual root playback is corpus/rendition-derived.
- Mechanical/promotable retention under the old chore is stricter than the requested on-demand design. Explicitly select the new delivery policy and update its coupled source/readers before applying any broad removal.

## Limits and execution boundary

- Editorial audit of delivered source; no compose, render, capture, retire, land, ledger mutation or chore execution performed. Main session owns delivery-budget evidence.
- No absence-of-keyword claim: every assigned nonblank line is explicitly classified. Corpus correspondence is exact occurrence plus declared section; absence of an exact match never means lack of authority.
- Scorecard automated matches reproduce normalized-substring semantics only. Semantic row correspondences read separately: Agent Contract263–280; Local98–108; GovernanceCore109–130; DefectFix226–231; Gate5Covenant233–241; ARB292–294. Missing match is unclassified, not Judgment or permission.
- New user instruction authorizes critical DELETE/ON-DEMAND proposals even for invariant entries. Those are canon-change recommendations, not ordinary-diet candidates under the older chore restrictions.
- Root is a single cross-harness contract. Codex-specific alternative root renditions are not proposed.
- Deleting/renaming H1/H2 sections changes section identities/ownership/survival declaration and cannot be applied by simply pasting this draft.
- Known983 corpus-underpopulation: do not replace the live contract with a generated partial-corpus candidate as a shortcut.
- The constrained first batch is intentionally separate from the full judgment-oriented redesign. Neither is authorized for application by this audit.
