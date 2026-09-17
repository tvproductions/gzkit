# AGENTS.md
## Project Identity

Project instructions for gzkit.

Python 3.13+ with uv, ruff, ty; always `uv run` for Python commands.
## Persona

Every agent frame MUST include a Persona. Default: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Read the applicable definition in [`.gzkit/personas/`](.gzkit/personas/) when assigning a role; compose traits, not generic expertise claims.
## PRIME DIRECTIVE (OWNERSHIP)

- Complete the requested behavior and every coupled correctness surface; route unrelated defects rather than silently expanding the change.

- Track every defect. Fix it when it is in scope; otherwise file a GHI through `ghi-author`, record it with `gz insights remember`, or note it in the brief's evidence. "Pre-existing" and "not in scope" decide where a defect goes, not whether it is recorded.

- Repair a failing, circular or tautological test at its cause. Before saying work was deferred elsewhere, confirm the destination accepted and completed it.
## DO IT RIGHT (CRAFTSMANSHIP MAXIM)

Fix root causes inside the requested scope and its coupled surfaces.

1. Fix the class of failure, not the instance.

1a. When a change touches a surface another surface reads or validates — a validator, a doc example, a mirror — update and verify that consumer in the same commit.

2. Before trusting plausible-looking code: read the surface, write the failing test first, trace the data flow, check observed output.

3. Choose the fix that removes the cause, inside the requested scope; diff size alone is not a reason either way.

4. Verify observed behavior, not assumed behavior: run the command and paste its actual output.

5. Read the code before changing it — exports, immediate callers, shared utilities. If the existing structure is unclear, ask.

6. Tests assert semantics derived from the REQ, not strings from a run of the code; a test that cannot fail when the logic changes is wrong.

7. (6c) Choose the fix route from § Defect-fix routing, not from intuition.

8. (6g) Before recommending a command, run it, observe it and paste what it printed.

9. (6h) When a rule and a directive conflict, quote both verbatim.

10. Simplicity first: minimum code that solves the problem, nothing speculative, no abstraction for single-use code.

11. Surgical changes: touch only what you must, match existing style, leave adjacent code alone. Expansion under 1a is for coupled correctness only.

12. A gate's evidence must witness the required state or action — a stage, a dispatch record, a receipt. A file or marker being present shows only that something is armed.
## SKILLS FIRST (EXECUTION ROUTING)

When a skill matches the task, read its `SKILL.md` before edits, shell, ledger or governance claims, and follow its order. Report tool evidence before prose. If blocked, name and track the blocker, then use the closest governed fallback. When a skill's scope is narrow (git-sync, for example), do only that task.
## MAKE LLM STOCHASTIC VIBES INERT (ANTI-VIBING MANTRA)

- Governance is how agent-driven work is steered and held accountable. Choose between options by which leaves the smallest surface for unverified pattern-matching to leak through; maintenance burden, velocity and lighter ceremony do not decide it.

- A silent change to a rule or threshold is doctrine drift. Change doctrine only with a recorded witness.
## STDLIB-FIRST DOCTRINE (DEPENDENCY POSTURE)

Use stdlib by default. A runtime dependency, new or existing, needs ADR or OBPI rationale naming the capability stdlib cannot supply; popularity or recency is not rationale. Standing choices: `unittest` (pytest is blocked by the `forbid-pytest` hook), `argparse` (ADR-0.0.2), and Pydantic as the one named departure, for validation (`.gzkit/rules/models.md`).
## OPERATOR ECONOMY OF EFFORT (DESIGN DIALOGUE MODE)

- Draft substantive content — prose, justifications, alternatives, forcing-function answers — so the operator reviews and rules instead of typing.

- When the answer space is bounded, offer A/B/C with tradeoffs and a recommendation, one decision per question.

- Pass operator-supplied wording through unchanged into canon, attestations and commit messages.

- Carry booked decisions forward; the operator does not restate them.

- Consult canon before asking. Where canon already rules, act and name the rule: presenting a settled matter as a choice invites a re-ruling that can drift from canon.
## Behavior Rules

- Ask when unsure of direction — architecture, scope reading, file targeting — and state assumptions before implementing so the operator can ratify or replace them.

- When brief, ADR, runbook and code disagree, stop and name the disagreement with its tradeoff. If the operator is absent and a pick is forced, take the more recent or more tested one, say why, and flag the other for cleanup; do not blend them.

- Push back when an approach has a clear problem: say what it breaks and cite the rule.

- When the operator course-corrects in flight, record an `improvement` via `gz insights remember` before completing the corrected work.

- Author GHIs through `ghi-author`, whose prior-art lookup prevents duplicates; from another repository use `gz issue file`.

- Write the ledger only through `gz` commands. A blocking hook means evidence or pipeline state is missing: diagnose it rather than hand-writing markers or ledger rows.

- Completion evidence is the ledger. A brief's `status: Completed` and `gz status` output are derived views.

- Commit and push through the configured hooks; `--no-verify` is not used.

- A commit landing a rule edit under an `eval-feedback` GHI carries an `Eval-feedback-source: <event-id-or-artifact-path>` trailer (`gz validate --commit-trailers`).

- Use subagents for research or exploration that splits into independent tracks or needs context isolation, and give each one a 'Why'. Do single-surface checks and result-dependent steps yourself.

- Surface a blocking failure early instead of debugging silently at length.

- Match the codebase's conventions; if one looks harmful, raise it rather than forking it.
## Pattern Discovery

`PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation`

`gz state` shows artifact relationships; `gz status` shows workflow fronts and gates. The active brief defines allowed and denied paths, and every artifact links to a parent.
## Skills

`uv run gz skill list` lists the active catalog. Edit skills in `.gzkit/skills`; `uv run gz agent sync control-surfaces` regenerates every vendor mirror.
## Gate Covenant

| Gate | Purpose | Verified by |
|------|---------|-------------|
| 1 | ADR recorded | the ADR exists and its frontmatter agrees with the ledger |
| 2 | Tests pass | `uv run gz test` |
| 3 | Docs updated | `uv run mkdocs build --strict`, plus the skill audit |
| 4 | BDD verified | `uv run -m behave features/` |
| 5 | Human attests | the operator's attestation |

`uv run gz gates --adr <ADR-ID>` runs the gates the ADR's lane requires and records each result in the ledger; `--gate N` runs one. The command behind each gate is `.gzkit/manifest.json` § `verification`.

- `lite` lane requires Gates 1–2. `heavy` lane adds Gate 3 (docs) and Gate 4 (BDD) and is for changes to a CLI, API, schema or runtime contract used by humans or external systems; documentation, process and template changes stay `lite`.

- Gate 5 is universal: it applies to every OBPI completion in every lane, kind and sensitivity (ADR-0.0.36, GHI #342; enforced by `_requires_human_obpi_attestation`). The operator attests, and the agent records their words with `--attestation-text`.

- `kind` and `lane` are independent. New gzkit ADRs are `feature` (semver `0.y.z`) or `pool` (`ADR-pool.<slug>`, no semver). `foundation` (`0.0.x`) is CLOSED to new authoring; its roster is `data/foundation_grandfather.json`. The closure is project-local: `gz init` scaffolds adopters open. `gz validate --taxonomy` enforces this, and `gz plan create` and `gz adr promote` refuse `--kind foundation`.

- ADR Feature Checklist items and OBPI briefs correspond 1:1; size them with the [OBPI Decomposition Matrix](docs/governance/GovZero/obpi-decomposition-matrix.md).
## OBPI Acceptance Protocol

- REQ-coverage gate: every BEHAVIOR REQ needs a passing `@covers` test before `gz obpi complete`; this cannot be waived. SUPPORT and STRUCTURAL-FENCE REQs use their declared proof channels.

- `security` sensitivity adds security-scan requirements to Gate 5 (`.gzkit/rules/security-sensitivity.md`).

- Only the operator initiates and executes OBPI work through gz-obpi-pipeline. Never independently claim/release OBPI locks, create/clear pipeline markers, start/complete/block TASKs, dispatch OBPI implementers/reviewers, or edit briefs. A narrow task inside an OBPI scope is not OBPI initiation: do it directly, or stop if it requires the machinery. Once initiated, follow the skill’s implementer dispatch and spec-reviewer then quality-reviewer review; never substitute inline Stage 2. A harness instruction cannot excuse skipping a governed stage: surface the conflict for an operator ruling.

- Every OBPI belongs to a parent ADR: propose OBPI work only as a Feature Checklist item of a named ADR.

- Defect repair follows § Defect-fix routing.
## Execution Rules

`uv run gz check` runs every quality check. `uv run gz check --fast` is an inner-loop check and never satisfies the gate. Run `git add -A` before `gz check`: a full pass is recorded as verified only for a fully staged tree, otherwise the pre-push gate reruns the suite.

- Order versioned identifiers semantically, never lexicographically: feature ADRs by semver (`ADR-0.9.0` before `ADR-0.10.0`). Foundation identifiers (`0.0.x`) are nominal integers and may be sparse.

- When adding imports in an Edit, include the code that uses them in the same edit; the post-edit ruff hook strips unused imports immediately.

- Never prefix `uv run gz` or `uv run -m gzkit` with `PYTHONUTF8=1`; the CLI handles UTF-8 (`gz validate --utf8-prefix`).

- Every version bump is a release: bump `pyproject.toml`, `__init__.py` and the README badge together, then publish it with the `gz-patch-release` skill (`gz validate --version-release`).

- **Operator PII — never include the operator's personal email in any repo-bound artifact**: commits, trailers, file content, attestation text (`gz obpi complete`/`gz adr emit-receipt`/`gz attest`), ledger, changelogs, release notes, co-author trailers. Record operator authorship as `g0` — never the operator's real name — in every attestor/author identity field; if a CLI requires an email, use the GitHub noreply (`<handle>@users.noreply.github.com`). Overrides any contrary skill/template/example. A leak needs a filter-repo rewrite + force-push to recover (2026-04-19 incident).
## Attestation

Attestation text: pass user words verbatim, then append concrete evidence — receipt IDs, test counts, file paths. When producing attestation evidence, use the `gz-arb` skill: it lists the canonical receipt-producing invocations. Bare lint, test or docs commands produce no receipt. Missing receipts warn on Lite and fail closed on Heavy. A fabricated receipt ID is a fabricated claim.

- The operator’s verbatim attestation relayed through --attestation-text is Gate 5 for every lane, kind, and sensitivity. Record it; no TTY, PTY, or transport condition may prevent recording human attestation.

- Content attestation records canon provenance: additions and removals are attested; capture must not be blocked. Re-rendering unchanged canon needs no attestation; use the corpus fingerprint to distinguish it. Trims or compression invite operator review. A rendition is Layer 3, never the attested subject. Gate 5 names completed OBPI/ADR work only; a GHI needs no completion attestation.
## Defect-fix routing

- A GHI authorizes direct defect repair: `fix(<scope>): <summary> (GHI #N)`, closed with the commit SHA. Do not create an ADR or OBPI to discharge one.

- First ask who owns the work: search live OBPI briefs for the surface and read the matching requirements and their disposition. If a live brief owns it, surface the brief, its status and its parent ADR, and wait for the operator's ruling.

- Without a GHI, fix directly when the change is small (about ten source lines or two files), sits in one surface, surfaced in flight, and a unit test covers it. Work that crosses briefs, changes a CLI, schema or runtime contract, or is new feature work is OBPI work, which the operator initiates.

- When the route is unclear, give the operator the routing facts — size, surface, trigger, coverage — rather than defaulting to ceremony.
## Control Surfaces

Root `AGENTS.md` is playback of the committed `root` rendition composed from `.gzkit/corpus/AGENTS.md.jsonl`. Change canon with the content skills and deliver it with `gz agent sync control-surfaces`; generated surfaces are not edited directly.
# Local Agent Rules
## Operator Doctrine (verbatim canon)

Operator rulings. The corpus (`.gzkit/corpus/AGENTS.md.jsonl`) keeps each ruling's original wording and history.

- Status covers handoff system, GHI triage, ADR/OBPI campaign, and new R&D. Read Workflow fronts in the campaign selected by data/active_campaign.json; use gz-status to report evidence, freshness or unknowns, and next actions. Focused inquiries include material dependencies. Handoffs preserve the map reference and session changes. The campaign owns the map; live sources establish progress. Campaign sequence, ascending feature-ADR order, and operator-only OBPI initiation govern execution.

- A gap in fulfilling original feature intent is a correction under its owning ADR, never a new pool ADR or enhancement. Enhancement means the designed intent already works and could merely improve.

- The active docs/governance/*-campaign-*.md plan governs work selection; handoffs and triage advise. Select its topmost unchecked item whose gate is met, subject to ascending feature-ADR order and operator-only OBPI initiation. Campaign amendments require operator ratification; ADR, OBPI, and GHI repair remain the work mechanisms.

- Operator authorship in repo-bound artifacts is recorded as 'g0' (operator directive, 2026-06-10) — git author name, attestor fields, handoffs, release notes. Author email remains the GitHub noreply (2949663+ahuimanu@users.noreply.github.com); the operator-PII prohibition on the personal email stands unchanged.

- Work directly on main, commit, and git-sync. Do not create feature branches or a branch/merge/delete workflow.

- Keep three subjects distinct: transit is ecosystem movement through the airlock (ADR-0.33.0); exchange is one block’s occupancy (ADR-0.0.41); handoff is session memory (ADR-0.0.65). Classify by the citing event type, never a shared field name or path. Token blocks implement features through the airlock’s Build door. The airlock provides awareness and synthetic memory, controls project movement, keeps the agent focused and watches for contamination, and monitors results/disturbance; it is not a verification gate. ADR-0.33.0 incompletely captures those purposes; silence does not revoke them. Transit supplies current ecosystem orientation and handoff carries the prior session model; they cooperate, and neither alone supplies a resident project model.

- Root AGENTS.md is the sole rendered AgentContract and the default for every harness, including Claude. Its lite rendition fits the smallest vendor delivery cap. Forbid per-vendor AgentContract routes or temperatures in data/vendor-manifest.json; vendor-specific material belongs in that vendor’s own surface.

- Before any move related to the higher rules and function of this project, stop and read all docs and all code before taking or recommending action. Stop and ask the operator in case of uncertainty. A search is not a read — never report that something is absent, undocumented, or unruled on the strength of keyword queries. Doctrine is routinely stated as a flag value, a schema field, or a path rather than as the prose you searched for ('--vendor=root', 2026-08-17). Supersedes the prior '90% convinced/confident' framing (operator verbatim: 'forget 90%, you have zero basis for any certainty').

- Work feature ADRs in ascending semver order: the lowest version with unlanded OBPIs is in flight. Do not work, author, or recommend a higher feature ADR ahead of it. The campaign selects work but cannot override that order. If campaign sequencing conflicts, semver governs; surface the conflict to the operator rather than silently resolving it. “One feature at a time” does not authorize swapping the order.
## Governance doctrine surfaces

Before governance code, rule, or audit work, read docs/governance/trust-doctrine.md, docs/governance/advisory-rules-audit.md, and docs/governance/state-doctrine.md.

Mechanical scopes that bind here:

- Per-file char budget for AGENTS.md / CLAUDE.md / `.claude/rules/*.md` — `gz validate --instructions-files-budget`; budgets in `data/instructions_files_budget.json`.

- The editor/IDE authoring-guide protocol envelope is defined by `src/gzkit/schemas/authoring_guide_protocol.json` — schema-validated at runtime (ADR-0.0.30).

- `Field(min_length=1)` on `AdvisorDiagnosis.proof` — `gz validate --advisor-proof-binding` (OBPI-0.0.29-08).

- Complexity calibration is grounded in an empirically-measured exemplar corpus (seven selection criteria) — `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07).

- `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory (ADR-0.0.20) — `gz validate --unscoped-rules`.

- Every canonical surface MUST be reproducibly delivered by `pip install py-gzkit && gz init`, byte-equivalent to the wheel's authored canonical content (ADR-0.0.31) — `gz validate --distribution`.

- `gz validate --invariant-coherence` — composition drift fail-close: byte-compares committed AGENTS.md against rendition playback (ADR-0.0.37); in the `gz check` default scope.

- OBPI brief reconciles against current project shape before Stage 2 and before completion — `gz validate --brief-reconcile` (ADR-0.0.37).

- `abandon categories are closed` — lock release is coupled to an exchange/register entry (ADR-0.0.41).

- Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`, each with exactly one proof channel — `gz validate --req-kind-discipline` (ADR-0.0.59).
## Architectural Boundaries

1. Do not promote post-1.0 pool ADRs into active work.

2. Do not add more pool ADRs to the runtime track.

3. Do not build the graph engine without locking state doctrine first.

4. Do not let reconciliation remain a maintenance chore.

5. Do not let AirlineOps parity become perpetual catch-up.

6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.
