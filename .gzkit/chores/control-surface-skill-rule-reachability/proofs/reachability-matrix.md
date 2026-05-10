# Reachability Matrix — Control Surface Skill ↔ Rule Audit (Pass B)

**Generated:** 2026-05-10
**Scope:** every (skill, applicable-rule) pair where the rule applies via § Policy and Guardrails

## Applicability test (recap)

A rule applies to a skill if **any** of:

- (a) the skill's allowed paths overlap the rule's `paths:` frontmatter, OR
- (b) the skill's procedure invokes a CLI verb the rule governs, OR
- (c) the skill modifies files the rule's `paths:` covers.

## Honors test (recap)

A skill honors an applicable rule when its body either:

- cites the rule file by name (e.g. `.gzkit/rules/tests.md`), OR
- enforces the rule's invariant mechanically (e.g. by calling `gz validate --<scope>` or a wrapped runtime that auto-runs the validator).

Universal note: every skill is governed by `agent-failure-modes.md` and `governance-core.md` (paths: `**/*`), and every skill is governed by `model-selection.md` (paths: `.gzkit/skills/**/SKILL.md`). The mechanical honors path for `model-selection` is the `model:` frontmatter (validated by the skill schema per GHI #409) — counted **yes (mechanical)** universally and listed once here, not repeated per row. Similarly, `skill-surface-sync.md` is honored mechanically by `gz agent sync control-surfaces` (per-edit, not per-skill); listed once. `tool-skill-runbook-alignment.md` Invariant 1 is honored mechanically by `gz validate --skill-alignment`; per-skill honors of Invariants 2 + 3 are body-level (Output Contract declaration). The matrix below focuses on **non-universal applicability** to keep the table actionable.

## Matrix

### Legend

- Honored: **yes (cite)** | **yes (mechanical)** | **no**
- A "no" row carries a one-paragraph worked example of the procedure-vs-rule tension.

| # | Skill (vN.N.N) | Applicable rule § | Applicability | Honored | Worked example (if no) |
|---|---|---|---|---|---|
| 1 | gz-adr-audit (6.7.1) | `tests.md` § Tests assert semantics, not strings | CLI verb (`gz adr audit-check` traverses `tests/**` for `@covers`) + file modification (Step 2 edits brief evidence) | **yes (cite)** | n/a — body cites both Red-Green-Refactor and REQ-semantics rules at lines 127, 132 (post-GHI #272 fix) |
| 2 | gz-adr-audit (6.7.1) | `adr-audit.md` § Audit sequence | path overlap (`docs/design/adr/**`) | **no** | Skill prescribes Step 1-3 ordering but never points the agent at `.gzkit/rules/adr-audit.md` § Audit sequence to confirm the rule's prescribed ordering matches; an agent reading only the skill could omit a step the rule mandates (e.g. the rule's `gz adr report` check before `audit-check`). |
| 3 | gz-adr-closeout-ceremony (7.9.0) | `gate5-runbook-code-covenant.md` § Three-layer documentation model | path overlap (`docs/**`, `src/gzkit/**` via attestation evidence) | **no** | Closeout walkthrough demos product behavior, but never instructs the agent to confirm the runbook/code three-layer alignment per the rule. An ADR shipping a CLI surface where the runbook section was not updated can still pass closeout because the rule is not cited. (GHI #427 traces this drift.) |
| 4 | gz-adr-closeout-ceremony (7.9.0) | `tests.md` § Tests assert semantics, not strings | file modification (ceremony emits attestation receipts referencing tests) + CLI verb (`gz arb` invocations on `tests/**`) | **yes (mechanical)** | Ceremony uses canonical ARB invocations (`gz arb step --name unittest ...`) per AGENTS.md § Attestation; locked by `CANONICAL_STEP_COMMANDS` (`gz arb validate` flags drift). Mechanical via ARB receipt schema. |
| 5 | gz-adr-create (6.2.0) | `cli.md` § Help text + exit codes | path overlap (skill scaffolds CLI surfaces via OBPI briefs) | **no** | When the agent uses gz-adr-create to scaffold a heavy-lane ADR introducing a new `gz` verb, no rule citation forces the brief to inherit `cli.md`'s exit-code map or output-contract conventions. Briefs landing under a heavy ADR have shipped CLI verbs lacking the standard 4-code map — a class fixed mid-OBPI in commits 0.25.x but not surface-prevented. |
| 6 | gz-adr-create (6.2.0) | `brief-heading-conventions.md` § Canonical evidence sections (H3) | file modification (creates `docs/design/adr/**/obpis/**`) | **yes (mechanical)** | Brief template emits H3 headings; `gz validate --brief-headings` flags H2 drift (GHI #238). Mechanical honor via downstream validator. |
| 7 | gz-adr-sync (7.0.0) | `governance-core.md` § ADR status index regeneration | CLI verb (`gz register-adrs` is the canonical regenerator named by the rule) | **yes (mechanical)** | Skill's `gz_command: register-adrs` is the exact verb the rule names as the regenerator. `gz validate --adr-status-fresh` is fail-close. Honored mechanically by the validator wiring. |
| 8 | gz-agent-sync (1.1.1) | `skill-surface-sync.md` § Procedure | CLI verb (skill wraps `gz agent sync control-surfaces`); path overlap (`.gzkit/skills/**`, `.gzkit/rules/**`) | **yes (mechanical)** | Skill is the canonical wielder of the rule's mechanical regenerator. Counted once here even though I said "listed once" — kept because gz-agent-sync **is** the rule's mechanical handler. |
| 9 | gz-arb (1.0.2) | `tests.md` § Coverage Floor + Run/Verify | CLI verb (`gz arb step` wraps unittest/coverage); path overlap (`tests/**` via subject command) | **yes (mechanical)** | `gz arb validate` enforces `CANONICAL_STEP_COMMANDS` (AGENTS.md § Attestation); ARB receipts bind canonical invocations to tests.md commands. Mechanical honor. |
| 10 | gz-arb (1.0.2) | `pythonic.md` § Type-check suppression syntax | CLI verb (`gz arb typecheck` runs ty) | **yes (mechanical)** | `gz arb typecheck` runs `uvx ty check`; the rule's binding ty-ignore syntax is enforced by `gz validate --type-ignores` which the wrapper invokes in heavy lanes. |
| 11 | gz-check (1.4.0) | `tests.md` § General Rules + Coverage Floor | CLI verb (`gz check` runs lint+typecheck+test) | **yes (mechanical)** | Wraps the canonical unit-tier invocation; mechanical honor. |
| 12 | gz-check (1.4.0) | `cross-platform.md` § Console / UTF-8 + `.as_posix()` | CLI verb (`gz check` runs ruff over `src/**/*.py`) | **no** | `gz check` runs ruff but no ruff rule enforces `.as_posix()` for path rendering, and the `cross-platform.md` invariant is not surfaced as a separate validator. An agent running gz-check sees green and merges code with `str(path)` rendering — the rule's invariant is reachable only via human review or a downstream defect (e.g. GHI #383). |
| 13 | gz-check-config-paths | `governance-core.md` § Proof commands | CLI verb (the skill is one of the named proof commands) | **yes (mechanical)** | Skill executes the rule-named verb; mechanical honor. |
| 14 | gz-chore-runner (1.1.2) | `chores.md` § Two-Surface Layout + Layout discipline | path overlap (`src/gzkit/chores/**`, `.gzkit/chores/**`); CLI verb (`gz chores`) | **no** | Skill describes a generic show/plan/advise/execute/validate sequence but does not cite `chores.md` § Layout discipline. An agent runs `gz chores run` without first invoking `gz validate --chores-layout`; a stray `CHORE.md` outside the canonical roots passes execution and surfaces only when the validator runs at next CI gate. (Echoes GHI #306 / GHI #304.) |
| 15 | gz-cli-audit | `cli.md` § Help text + Adding CLI features | CLI verb (wraps `gz cli audit`); path overlap (`src/gzkit/commands/**`) | **yes (mechanical)** | `gz cli audit` is the mechanical audit named by the rule; honors are wired via the validator. |
| 16 | gz-complexity-distill (0.2.0) | `complexity-doctrine.md` § Selection Criteria + Distillation Cadence | path overlap (`docs/governance/complexity/**`, `data/exemplar_corpus.json`); CLI verb (`gz complexity distill`) | **yes (cite)** | Skill body lines 55, 152 cite the rule directly. |
| 17 | gz-complexity-distill (0.2.0) | `complexity-thresholds.md` § Per-metric thresholds | path overlap (`src/gzkit/complexity/**`) | **yes (mechanical)** | `gz validate --complexity-thresholds` is invoked by the chore wrapper; thresholds JSON is the source-of-truth. |
| 18 | gz-context-diet (1.0.0) | `gate5-runbook-code-covenant.md` § Three-layer documentation model | file modification (`AGENTS.md`, `CLAUDE.md`, `docs/governance/**`) | **no** | Skill trims per-turn contract weight by lifting pedagogy out of AGENTS.md to docs/governance/. The rule's three-layer covenant requires that when behavior-binding text moves between layers, the runbook ↔ code alignment must be reverified. The skill prescribes only the trimming pass, not the covenant recheck — leaving binding bullets behind without an alignment audit can silently drop a covenant-relevant cite. |
| 19 | gz-context-diet (1.0.0) | `skill-surface-sync.md` § Edit canonical first | path overlap (`.claude/rules/**`) | **no** | Skill body says to lift pedagogy from `.claude/rules/**`, but per `skill-surface-sync.md` the `.claude/rules/**` surface is a vendor mirror, not canonical. An agent following the skill literally edits the mirror; the next `gz agent sync` overwrites the work. The body should instruct edits at `.gzkit/rules/**` then sync. (Mirror of GHI #361 surface confusion.) |
| 20 | gz-deps-upgrade (1.0.0) | `models.md` § Pydantic departure rationale | file modification (`pyproject.toml`) | **no** | Skill walks the agent through `uv` upgrade flow but never instructs a check that any newly-pinned dep retains the stdlib-first / Pydantic-departure attestation. Adding a new runtime dep would skip the AGENTS.md § Stdlib-First Doctrine check that `models.md` operationalizes for the data-model surface. |
| 21 | gz-init (6.0.1) | `governance-core.md` § Required workflow order | file modification (`.gzkit/**`, `.claude/**`) | **yes (mechanical)** | `gz init` writes the canonical scaffolds the rule references; mechanical via wheel-shipped templates. |
| 22 | gz-issue-file (1.0.0) | `gh-cli.md` § Cross-repo filing | CLI verb (`gz issue file` wraps `gh issue create --repo`); path overlap (`.github/**`) | **yes (cite)** | Body line 78 cites the rule explicitly. |
| 23 | gz-issue-file (1.0.0) | `agent-failure-modes.md` § Safeguard circumvention | path overlap (every skill); cite | **yes (cite)** | Body line 80 cites the rule explicitly. |
| 24 | gz-obpi-lock (6.0.2) | `token-block-discipline.md` § Auditable Abandon Categories + Register-Entry Rule | path overlap (`src/gzkit/lock_manager.py`, `src/gzkit/commands/obpi_lock.py`, `.gzkit/handoffs/**`); CLI verb (`gz obpi lock`) | **no** | Skill prescribes `gz obpi lock acquire/release/list` but never names the rule's five binding sub-invariants. An agent abandoning a lock can complete a release without first satisfying Sub-Invariant 5 (Release Fail-Closed Precondition) because the skill body does not surface the rule's preconditions. (GHI #410 is the exact symptom: "release decoupled from register-entry write.") |
| 25 | gz-obpi-pipeline (6.14.3) | `tests.md` § General Rules + Red-Green-Refactor | CLI verb (Stage 2 runs unittest+behave); path overlap (`tests/**`, `features/**`) | **yes (mechanical)** | Pipeline runtime owns Stage 2 sequencing and enforces canonical ARB invocations from AGENTS.md § Attestation. Mechanical honor. |
| 26 | gz-obpi-pipeline (6.14.3) | `gate5-runbook-code-covenant.md` § Required updates when behavior changes | file modification (pipeline produces runbook+code+ADR diff across stages) | **no** | Pipeline runtime sequences implement → verify → ceremony → git-sync → complete, but no stage explicitly cites or mechanically gates on the runbook-code covenant beyond `gz validate --doc-surface-parity`. An agent passes Stage 4 with an ADR shipping a CLI change where the runbook section was not updated (GHI #427 root cause). |
| 27 | gz-obpi-pipeline (6.14.3) | `security-sensitivity.md` § `gz validate --sensitivity` | path overlap (`docs/design/adr/**/obpis/**`); sensitivity-bearing OBPIs | **yes (mechanical)** | Pipeline runtime hits `_requires_security_review_attestation` branch on `sensitivity: security` briefs (ADR-0.0.22); locked by `--sensitivity` validator. |
| 28 | gz-obpi-reconcile (3.0.3) | `governance-core.md` § ADR status index regeneration | CLI verb (reconcile triggers `register-adrs`); path overlap (`docs/design/adr/**/obpis/**`) | **yes (mechanical)** | Reconcile triggers index regen; `gz validate --adr-status-fresh` is the failclose. |
| 29 | gz-obpi-reconcile (3.0.3) | `brief-heading-conventions.md` § Mechanical check | path overlap (briefs); CLI verb | **yes (mechanical)** | `gz validate --brief-headings` runs inside the reconcile pipeline. |
| 30 | gz-obpi-simplify (6.0.4) | `pythonic.md` § Core Principles | path overlap (target `src/**/*.py`) | **no** | Skill reviews reuse/quality/efficiency under three dimensions but never references `.gzkit/rules/pythonic.md` § Size Limits, Imports, or Toolchain. An agent applying simplify can introduce a non-PEP-8 import block or a class exceeding 300 lines without the rule being surfaced; only the downstream `gz validate --class-size` audit catches it. |
| 31 | gz-obpi-specify (1.5.0) | `brief-heading-conventions.md` § Canonical evidence sections (H3) | file modification (`docs/design/adr/**/obpis/**`); CLI verb (`gz obpi specify`) | **yes (mechanical)** | Brief template authored by `gz obpi specify` uses H3 by default; `gz validate --brief-headings` is fail-close (GHI #238). |
| 32 | gz-obpi-specify (1.5.0) | `security-sensitivity.md` § Invariant + Registry contract | file modification (sensitivity-bearing briefs); path overlap | **no** | Brief-authoring skill does not instruct the agent to consult `data/security_surfaces.json` registry when scoping. A brief touching a registered surface can be authored without `sensitivity: security` until `gz validate --sensitivity` flags it post-authoring. |
| 33 | gz-patch-release (1.4.0) | `governance-core.md` § Non-negotiable rules (no manual ledger edits) | file modification (`RELEASE_NOTES.md`, `pyproject.toml`); CLI verb | **yes (mechanical)** | Skill wraps `gz patch release`; mechanical via CLI-only ledger writes. |
| 34 | gz-plan (1.1.1) | `adr-audit.md` § Audit sequence | path overlap (`docs/design/adr/**`); CLI verb (`gz plan create`) | **no** | Skill creates plan-level artifacts but never points back to `adr-audit.md` for the cadence of pre-plan defect-routing checks. Mid-flight defects flagged during planning don't auto-route through the audit sequence (GHI #271 is the exact pattern). |
| 35 | gz-pythonic-pattern-apply (1.0.0) | `tests.md` § Tests assert semantics + Red-Green-Refactor | path overlap (`src/**/*.py`, `tests/**/*.py`) | **yes (cite)** | Body lines 47 and 138 cite the rule and invariant 6f explicitly. |
| 36 | gz-pythonic-pattern-apply (1.0.0) | `pythonic.md` § Core Principles | path overlap (`**/*.py`) | **no** | Apply skill captures TDD GREEN receipts + xenon/radon deltas, but never cites `pythonic.md` for the rewrite target itself. An agent could rewrite a Strategy class into a function that violates pythonic.md § Imports without the rule being surfaced — the only catch is downstream lint. |
| 37 | gz-pythonic-pattern-detect (1.0.0) | `tests.md` § Tests assert semantics | path overlap (`**/*.py`) | **yes (cite)** | Body line 126 cites the rule explicitly. |
| 38 | gz-pythonic-pattern-detect (1.0.0) | `pythonic.md` § Core Principles | path overlap (`**/*.py`) | **no** | Detect skill surfaces Java-flavored patterns (Strategy, Singleton, Visitor) but does not cite `.gzkit/rules/pythonic.md`. The rule's own anti-pattern list (e.g. dunder over-implementation) is a different surface than the skill's detection list; an agent reading only the skill misses the rule-named anti-patterns. |
| 39 | gz-session-handoff (6.3.0) | `token-block-discipline.md` § Register-Entry Minimum-Information Rule | path overlap (`.gzkit/handoffs/**`) | **no** | Handoff documents are register-entries per the rule, but the skill body lists handoff content (active OBPI, gate state, etc.) without naming the rule's Sub-Invariant 2 minimum-information set. A handoff missing rule-mandated fields (TTL, lock-bearer identity) passes the skill but fails the rule's audit-path test. |
| 40 | gz-status / gz-state | `governance-core.md` § Proof commands | CLI verb (named proof commands) | **yes (mechanical)** | These verbs are the named proof commands. |
| 41 | gz-tech-debt-review (1.2.1) | `pythonic.md` § Type-check suppression syntax | path overlap (`src/**/*.py`) | **yes (cite)** | Body line 196 cites `.claude/rules/pythonic.md` in a worked example. |
| 42 | gz-tech-debt-review (1.2.1) | `tests.md` § Tests assert semantics | path overlap (`tests/**`) | **no** | Tech-debt review surfaces test smells (e.g. string-shape assertions) but does not cite `tests.md` § Tests assert semantics. An agent flagging a cosmetic backfill follows the skill's three-dimension lens but never sees the rule's Invariant 6f naming. |
| 43 | gz-tidy (1.1.1) | `governance-core.md` § Required workflow order | CLI verb (wraps `gz tidy`); repo-wide | **yes (mechanical)** | `gz tidy` is the named hygiene wrapper; mechanical honor via wheel-shipped procedures. |
| 44 | gz-validate | every rule with a `gz validate --<scope>` flag | CLI verb (`gz validate`) | **yes (mechanical)** | Universal mechanical honors — `gz validate --<scope>` is the named regenerator/audit for every promoted rule. |
| 45 | ghi-author (1.2.0) | `gh-cli.md` § Allowed commands | CLI verb (`gh issue create`); path overlap (`.github/**`) | **yes (cite)** | Body line 102 cites the rule. |
| 46 | ghi-author (1.2.0) | `security-sensitivity.md` § Heightened walkthrough | path overlap (data/security_surfaces.json reference) | **yes (cite)** | Body line 122 cites the rule. |
| 47 | ghi-close (2.4.0) | `tests.md` § Red-Green-Refactor + Tests assert semantics | CLI verb (any test-touching fix); path overlap (`tests/**`) | **yes (cite)** | Body lines 231, 243, 396 cite the rule and invariants. |
| 48 | ghi-close (2.4.0) | `tool-skill-runbook-alignment.md` § Commit-message discipline | path overlap (any commit) | **yes (cite)** | Body lines 247, 394 cite the rule. |
| 49 | ghi-triage (5.1.0) | `gh-cli.md` § Allowed commands | CLI verb (`gh issue list`); path overlap (`.github/**`) | **yes (cite)** | Body line 237 cites the rule. |
| 50 | git-sync (1.2.3) | `gh-cli.md` § Prohibited without explicit approval | CLI verb (push); path overlap (`.github/**`) | **no** | Skill prescribes guarded sync ritual but does not cite `gh-cli.md`. An agent following git-sync can perform a force-push if hooks pass (the rule explicitly forbids force-push to main without approval) — the rule's prohibition is reachable only via pre-commit hook, not via the skill body. |

## Counts (matrix only, excludes universal rules)

| Bucket | Count |
|---|---|
| **yes (cite)** rows | 13 |
| **yes (mechanical)** rows | 22 |
| **no** rows (reachability gap) | 15 |
| Total matrix rows | 50 |

Universal honors (counted once, not per-row):

- `model-selection.md`: 50/50 active skills declare `model:` frontmatter (GHI #409) — yes (mechanical) universally.
- `skill-surface-sync.md`: 50/50 active skills auto-sync via `gz agent sync control-surfaces` — yes (mechanical) universally.
- `tool-skill-runbook-alignment.md` Invariant 1: 50/50 active skills wield ≥ 1 CLI verb; `gz validate --skill-alignment` is the mechanical backstop — yes (mechanical) universally.
- `agent-failure-modes.md`: paths `**/*` apply to every skill; only `gz-issue-file` cites it directly — counted as a latent gap for the other 49 skills, surfaced in summary.md.
- `governance-core.md`: paths `**/*` apply to every skill; subset (gz-state, gz-status, gz-tidy, gz-init, gz-patch-release, etc.) honor mechanically via being the rule's named proof commands.

## Reading guide

The 15 "no" rows are the reachability gaps. They split into:

- **Known-blocking** (a recent GHI documents the exact symptom): rows 3, 14, 19, 24, 26 — see `ghi-cross-reference.md`.
- **Latent** (no GHI yet; pattern matches the chore's source case GHI #268): rows 2, 5, 12, 18, 20, 30, 32, 34, 36, 38, 39, 42, 50.

Two rows are honored mechanically only because a separate downstream validator fires; the **skill body** itself does not cite the rule. These are listed as yes (mechanical) but are weaker than yes (cite) honors and would degrade if the validator regresses (rows 6, 27, 29, 31).
