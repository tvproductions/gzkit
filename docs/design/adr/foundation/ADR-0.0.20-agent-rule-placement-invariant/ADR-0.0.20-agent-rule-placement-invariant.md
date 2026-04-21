---
id: ADR-0.0.20-agent-rule-placement-invariant
status: Draft
kind: foundation
semver: 0.0.20
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-04-21
dependencies:
  - ADR-0.17.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.20: Agent Rule Placement Invariant

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Reads the anchor before proposing a change; treats duplicate always-on rule content as a first-class drift vector rather than a cosmetic inefficiency; distinguishes structural binding (where a rule lives) from semantic content (what a rule says). This ADR formalizes a placement invariant extracted from the 2026-04-21 governance-bloat audit and makes it mechanically enforceable via the new `gz validate --unscoped-rules` scope.

This ADR is a Foundation addition. Foundations are baseline assumptions about good app substrates — ADR-0.17.0 Intent #1 ("~80% token reduction in always-loaded content") has been load-bearing since 2026-03-15 but has had no anti-regression mechanism; this ADR provides one without imposing universal friction. The 2am-operator rubric applies: at 2am, an operator adding a new always-on rule hits the validator at pre-commit, gets three-option recovery (narrow glob / fold / allow-list), reads this ADR for context. The validator is THE enforcement.

## Intent

### Before (current state)

Today, `.gzkit/rules/` carries three always-on rule files with `paths: "**"` — `agent-contract.md` (213 lines), `attestation-enrichment.md` (155 lines), and `defect-fix-routing.md` (80 lines). These files load unconditionally into every agent turn alongside `AGENTS.md`, `CLAUDE.md`, the ~50-entry skill catalog, and 13 other path-scoped rules that are currently loaded unconditionally because the `paths:` frontmatter is advisory (not yet wired into the harness). The 2026-04-21 session that produced this ADR measured ~25 KB of governance preamble (~1,800 lines) entering every session before the operator types a word. Worse, ~60% of the three always-on rule files duplicates content already present in `AGENTS.md` § Prime Directive / § DO IT RIGHT / § Behavior Rules. ADR-0.17.0 (Validated 2026-03-15) set Intent #1 "Reduce context window bloat — ~80% token reduction in always-loaded content" but had no anti-regression mechanism — so new always-on rules can silently accrete into `.claude/rules/` over time, eroding the token-reduction win.

This is not a token-cost concern — it is an attention-dilution concern (reporting-pathway vs. execution-pathway drift, Lindsey et al. 2025, applied at the context-window level): currently the model reads "Own the work completely" twice per turn, and each duplicate halves the attention weight available for the next instruction. Currently there is also no mechanical test for rule placement — the discipline depends on advisory prose, which trust-doctrine.md warns is unreliable over long runs across agent rotation.

### After (target state)

After this ADR, non-path-scoped agent rules live in `AGENTS.md` — the Linux-Foundation-stewarded cross-agent standard (<https://agents.md/>) honored by 25+ agent runtimes (Claude, Codex, Copilot, Cursor, Aider, Zed, Jules, Gemini, etc.) — either at the repo root or in a per-directory AGENTS.md at the narrowest appropriate scope. Allow-list exceptions are recorded in `.gzkit/manifest.json` under `rules.unscoped_allowlist` with rationale and tracking ref. A new mechanical validator (`uv run gz validate --unscoped-rules`) fails closed on any `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` frontmatter, firing at pre-commit and CI. Going forward, new always-on rules cannot silently accrete — authors must either narrow the `paths:` glob, fold the content into AGENTS.md, or add an allow-listed exception with rationale.

The three current always-on files migrate to their proper homes — AGENTS.md (binding content), CLAUDE.md addendum (Claude-specific residue, invariant 10a), and `docs/governance/` (pedagogy + rationale, read on-demand). Inbound references across ~40 live governance files are rewritten; vendor mirrors auto-regenerate cleanly via `gz agent sync control-surfaces`. The target-state per-turn governance preamble shrinks by ~570 lines across every session.

## Decision

Codify the invariant and mechanize it in five parallelizable increments.

### The invariant (canonical statement)

> An agent rule file with `paths: "**"` (or missing/absent `paths:` frontmatter) may not live under any vendor-surface rules directory. Non-path-scoped agent rules live in `AGENTS.md` — root or hierarchical per-directory — at the narrowest appropriate scope. Allow-list exceptions are explicit, manifest-backed, and rationale-required (no silent passlists — trust-doctrine T2).

### Scope boundaries

**IN:**

- `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:`
- `.claude/rules/*.md` mirrors (auto-regenerated from canonical)
- `.github/instructions/*.md` mirrors
- Future `.agents/rules/`
- Rules added post-landing

**OUT:**

- Hierarchical per-directory `AGENTS.md` files (first-class agents.md/ feature)
- Path-scoped rules with concrete globs
- Skill files (governed by `.gzkit/rules/skill-surface-sync.md`)
- Hooks (`.claude/hooks/*.py` — code, not rules)
- Entry points (`CLAUDE.md`, `copilot-instructions.md` — their role is established by ADR-0.17.0)

### Edge cases explicitly addressed

1. **Broad-glob rules** (`paths: src/**`) PASS — the mechanical test is concrete-glob-presence, not glob-narrowness. Narrowness is judgment.
2. **Claude-specific universal rules** must live in path-scoped files with Claude-surface globs (e.g., `paths: [".claude/**", ".gzkit/skills/**"]`), not `paths: "**"`. Being Claude-specific does not grant `paths: "**"` permission.
3. **Transition allow-list:** rules migrating from `paths: "**"` to a new home get temporary entries with `tracking_ref` pointing at this ADR or an OBPI; entries expire when the migration closes.
4. **Root vs. per-directory AGENTS.md:** narrowest-appropriate-scope — universal invariants in root `AGENTS.md`; surface-specific rules in per-directory files (`tests/AGENTS.md`, `src/gzkit/commands/AGENTS.md`, etc.).

### Mechanical backstop

New `gz validate --unscoped-rules` scope:

- Enumerates canonical `.gzkit/rules/*.md` files
- Parses YAML frontmatter
- Classifies PASS (concrete glob) / VIOLATION (missing-paths or universal-glob) / ALLOWLISTED (in manifest allow-list)
- Exit codes per `.gzkit/rules/cli.md` 4-code map: 0 pass, 2 I/O error, 3 policy breach
- Supports `--json` for machine output and `--allowlist-only` for audit listing
- No `--fix` in v1 — the fix is judgment (fold vs. narrow vs. allow-list)
- Integrates into `gz validate --all` and `gz check`
- Mirrors NOT checked directly — the `skill-surface-sync` + pre-commit-sync-guard (GHI #210) contract already guarantees mirror fidelity; checking canonical is the single source of truth

### Allow-list schema

`.gzkit/manifest.json` under `rules.unscoped_allowlist`, a list of entries:

| Field | Type | Required | Constraint |
|---|---|---|---|
| `file` | string | yes | Repo-relative path; must resolve to an existing file under a known rule directory |
| `rationale` | string | yes | Min length 20 chars |
| `tracking_ref` | string | yes | Must match `GHI-\d+` or `ADR-[\d.]+[-\w]*` |
| `added_date` | ISO date | yes | YYYY-MM-DD |

Pydantic-validated under `src/gzkit/validators/unscoped_rules.py` with `ConfigDict(frozen=True, extra="forbid")`. JSON Schema fragment extends `src/gzkit/schemas/manifest.schema.json` so `gz validate --manifest` catches malformed entries at authoring time. No `expires_at` in v1 — tracking_ref resolution is the informal expiry signal; enforced expiry is a follow-up GHI if drift observed.

### Migration path (carried by OBPIs 02/03/04)

The three current `.gzkit/rules/` files with `paths: "**"` (`agent-contract.md`, `attestation-enrichment.md`, `defect-fix-routing.md`) migrate to:

- **AGENTS.md** — binding content (judgment invariants, pattern tables, threshold rules)
- **CLAUDE.md addendum** — Claude-specific residue (primarily invariant 10a: "when a skill step names a tool to invoke, invoke it in the same turn")
- **docs/governance/** — pedagogy, rationale, origin GHI history (three new files)

Inbound references across ~40 live files (Bucket 1 from blast-radius analysis) get rewritten. Vendor mirrors auto-regenerate via `gz agent sync control-surfaces`. Historical artifacts (Bucket 3, ~25 files) are left alone — they reference the rule as it existed at authoring time.

### Five OBPIs decompose the decision

**OBPI-0.0.20-01 — Validator + allow-list foundation (parallel-root).** Pydantic models (`UnscopedAllowlistEntry`, `Violation`, `UnscopedRulesResult`) at `src/gzkit/validators/unscoped_rules.py`; `--unscoped-rules` flag registration in `src/gzkit/cli/parser_validate.py`; manifest schema fragment extending `src/gzkit/schemas/manifest.schema.json`; initial allow-list with three entries (the doomed files, each `rationale="Pending consolidation per OBPI-0X"`, `tracking_ref="ADR-0.0.20"`); table-driven TDD tests at `tests/validators/test_unscoped_rules.py` covering missing-paths, universal-glob (string + list form), concrete-glob, allowlisted-hit, malformed-frontmatter, missing-manifest; scorecard row addition at `docs/governance/advisory-rules-audit.md`; command-doc update at `docs/user/commands/validate.md`. **Acceptance:** `gz validate --unscoped-rules` exits 0 against current repo; coverage ≥40% for new module.

**OBPI-0.0.20-02 — Fold agent-contract.md (depends on OBPI-01).** Judgment invariants migrate into AGENTS.md's existing § Prime Directive / § DO IT RIGHT / § Behavior Rules, deduplicated; invariant 10a (tool-invocation) migrates to CLAUDE.md "Claude Code addendum" section; pedagogy (anti-pattern canon, TASK-driven workflow, Lindsey et al. rationale for 6g/6h) extracts to `docs/governance/agent-contract-rationale.md`; `.gzkit/rules/agent-contract.md` deleted; allow-list entry removed; ~15 inbound Bucket-1 references rewritten; `gz agent sync control-surfaces` regenerates mirrors cleanly.

**OBPI-0.0.20-03 — Fold attestation-enrichment.md (depends on OBPI-01; parallel with 02/04).** Em-dash pattern + canonical invocations table + lane behavior migrate to new AGENTS.md § Attestation; ARB middleware detail (schemas, commands, exit codes, storage paths, rationale) extracts to `docs/governance/arb-middleware.md`; 6 Python docstring citations updated (`parser_arb.py`, `arb/__init__.py`, `arb/validator.py` line 184, `commands/arb.py`, `commands/obpi_precomplete.py`, `features/steps/gz_steps.py`); 8 ARB command docs updated; canonical deleted; allow-list entry removed; ADR-0.36.0-OBPI-08 staleness flagged via GHI (its `.claude/rules/arb.md` premise is broken).

**OBPI-0.0.20-04 — Fold defect-fix-routing.md (depends on OBPI-01; parallel with 02/03).** Two threshold tables (Direct-fix conditions ALL / OBPI-ceremony conditions ANY) + decision protocol migrate to new AGENTS.md § Defect-fix routing; anti-patterns catalog + origin GHI history (#195, OBPI-0.0.16-04→06 precedent) extract to `docs/governance/defect-fix-routing.md`; canonical deleted; allow-list entry removed; inbound references rewritten.

**OBPI-0.0.20-05 — Closeout sweep + downstream flags (depends on 02/03/04).** Final grep sweep confirming no residual references outside Bucket-3 historical artifacts; `gz agent sync control-surfaces` mirror regeneration verified; `gz validate --all` exits 0; three downstream-impact GHIs filed — ADR-0.36.0 WBS refresh (already stale on arb.md; further stale post-ours), ADR-0.38.0-07 baseline note (AGENTS.md comparison runs against normalized gzkit), ADR-0.0.19 reference refresh (cites the now-deleted `behavioral-invariants.md` / `agent-contract.md` lineage); foundation-kind closeout walkthrough per ADR-0.0.18 § Foundation-kind rigor (applies across lanes — Lite lane does not exempt foundation doctrine).

**Parallelism:** OBPI-01 → {02, 03, 04 parallel} → OBPI-05.

### Lane

**Lite.** New `--unscoped-rules` flag is additive on an existing `gz validate` subcommand per `.gzkit/rules/cli.md` § New Flag. No subcommand added, no schema-breaking manifest change (new optional key), no runtime contract change, no external consumer impact. Foundation-kind rigor still applies per ADR-0.0.18 — OBPI-05 walkthrough follows foundation doctrine regardless of Lite lane.

### Scope boundary — what this ADR explicitly does NOT do

- Does NOT replace the three-layer control surface model from ADR-0.17.0 (canonical/mirror/surface unchanged)
- Does NOT promote or supersede any pool ADR (`progressive-context-disclosure`, `focused-context-loader`, `universal-agent-onboarding`, `interpretability-hardened-agent-surfaces` all remain valid for their broader promotions)
- Does NOT change `gz agent sync control-surfaces` mechanism (only consumes it)
- Does NOT add mechanical enforcement for the agents.md/ hierarchical discipline (placement of universal invariants vs. per-directory rules remains judgment — the validator can't litigate AGENTS.md hierarchy placement)
- Does NOT establish a general progressive-disclosure architecture (that's the pool ADR's scope)
- Does NOT enforce allow-list expiry (follow-up GHI if drift observed)
- Does NOT check mirror files independently (sync contract handles fidelity)

### Forcing-function stress tests applied during design

- **Pre-mortem (18 months out):** Failure modes include the allow-list becoming a permanent escape hatch if migration OBPIs don't close; operators adding `paths: src/**` as a sham scope to bypass the validator (broad-but-concrete globs PASS per design, which could be gamed); future ADR authors treating `.claude/rules/` as a first-class home and creating new unscoped rules assuming the invariant won't apply (mitigated by validator firing at CI). Mitigations: follow-up GHI tracks allow-list expiry enforcement; advisory-rules-audit.md scorecard monitors for gaming patterns; validator is fail-closed at Gate 2.
- **What Would Have to Be True:** AGENTS.md hierarchical per-directory discipline is honored by agent runtimes (validated — agents.md/ standard explicitly supports it); the 3 target rule files' content is genuinely duplicative with AGENTS.md (validated — grep audit showed ~60% overlap); the Claude-specific residue (invariant 10a) is genuinely small and non-expanding (**shakiest condition** — future Claude-surface concerns might accrete). For Alternative 4 (inverse — trim AGENTS.md) to have been better: if the current AGENTS.md content were mostly pedagogy rather than binding operational rules.
- **Constraint archaeology:** The `paths: "**"` convention inherited from ADR-0.17.0's three-layer model — load-bearing. The agents.md/ standard adoption is freshly decided (2024 Linux Foundation stewardship). The `.gzkit/manifest.json` as canon storage inherited from ADR-0.0.9 state-doctrine — load-bearing.
- **Assumption surfacing:** Operators re-read this ADR when authoring new rules (if not, future unscoped rules still accrete because authors never see the invariant — mitigated by the validator firing at Gate 2); the validator's classification logic correctly handles all YAML representations of `paths:` (list form, string form, empty string, null — tested in OBPI-01's table-driven tests); `gz agent sync control-surfaces` cleanly handles deleted canonicals (assumption — tested in OBPI-02's acceptance).
- **2am operator:** At 2am, an operator adding a new always-on rule hits the validator at pre-commit, gets the three-option recovery (narrow glob / fold / allow-list), reads this ADR for context. The validator is THE enforcement — no other surface catches this drift.
- **Reversibility:** Two-way door. Deleting the three rule files is reversible (git revert). The validator scope is reversible (feature-flag or remove). The allow-list schema is additive (future field additions don't break the invariant). AGENTS.md content migrations are two-way via git.
- **Scope minimization:** Floor is OBPI-01 + OBPI-05 (validator lands with the three files permanently allow-listed — still captures the anti-regression win for FUTURE rules). Under time pressure, drop OBPI-02/03/04 and ship just the invariant + validator + permanent allow-list for the three inherited files; file a follow-up ADR for the consolidation work.

### Downstream decisions forced by this ADR

1. ADR-0.36.0 WBS refresh (stale on `arb.md`; further stale post-ours) — filed as a GHI under OBPI-05.
2. ADR-0.38.0-07 baseline note — runs against normalized gzkit AGENTS.md after this ADR.
3. ADR-0.0.19 reference refresh — cites `behavioral-invariants.md` / `agent-contract.md` lineage; needs pointer to AGENTS.md.
4. Follow-up GHI for allow-list expiry enforcement if drift observed.
5. Downstream promotion pathway for `ADR-pool.progressive-context-disclosure` unblocked — dynamic L0/L1/L2/L3 now builds on normalized static L0.

## Consequences

### Positive

1. ~570 lines of redundant governance preamble removed from per-turn context load (3 rule files totaling 448 canonical lines + duplication overlap with AGENTS.md across every session).
2. AGENTS.md becomes the single authoritative cross-agent home for universal invariants — matching the Linux Foundation agents.md/ standard's intent and maximizing reach across 25+ honoring agents (Claude, Codex, Copilot, Cursor, Aider, Zed, Jules, Gemini).
3. Anti-regression guarantee: future always-on rules cannot silently accrete into `.claude/rules/` without either path-scoping or an allow-listed exception with rationale and tracking ref. The validator fires at Gate 2 on every commit.
4. Cleaner baseline for downstream ADRs: ADR-0.38.0-07 runs against normalized gzkit AGENTS.md (not a comparison against drift); `progressive-context-disclosure` pool ADR builds on normalized L0 static surface before attempting dynamic L0/L1/L2/L3 tiers.
5. Drift vector closed: no more cross-file synchronization between `agent-contract.md` and AGENTS.md. The current `agent-contract.md` header itself admits "source-of-truth remains AGENTS.md" — this ADR makes the admission structural.
6. Attention-dilution reduced: the model no longer reads "Own the work completely" twice per turn; each invariant has undivided attention weight.
7. `docs/governance/` gains three deep-dive reference files (`agent-contract-rationale.md`, `arb-middleware.md`, `defect-fix-routing.md`) — pedagogy and rationale accessible to humans and on-demand to agents via Read tool, without loading always-on.
8. Scorecard gains a new Mechanical row — advisory-rules-audit.md continues its trajectory toward comprehensive mechanization (59% → 60%+).

### Negative

1. Five OBPIs of execution work — validator + three file migrations + closeout. Total diff size spans ~40 live files (Bucket 1 references), six Python docstrings (Bucket 2), and three new `docs/governance/` files.
2. Inbound reference rewrites: ~40 live governance files need link updates from `.gzkit/rules/*.md` to the new homes (AGENTS.md sections or `docs/governance/` pages). Sweep is mechanical but requires care to avoid missing one.
3. Python docstring citations in `parser_arb.py`, `arb/__init__.py`, `arb/validator.py` (error message at line 184), `commands/arb.py`, `commands/obpi_precomplete.py`, `features/steps/gz_steps.py` need path updates. Non-load-bearing (docstrings don't affect runtime) but visible to operators reading error messages.
4. Downstream ADRs need refresh: ADR-0.36.0 WBS is stale on `.claude/rules/arb.md` (content moved to `attestation-enrichment.md` 2026-04-21); post-ours, the WBS is further stale (arb and other files removed from the reconciliation set). ADR-0.0.19 cites `.gzkit/rules/behavioral-invariants.md` which was merged into `agent-contract.md` pre-our-ADR; our ADR removes that lineage too.
5. Allow-list expiry is not enforced in v1. Entries without resolution could accumulate, turning allow-list into a permanent escape hatch. Follow-up GHI tracks enforcement; current state relies on `tracking_ref` resolution as informal expiry signal.
6. CLAUDE.md gains ~3 lines (invariant 10a in "Claude Code addendum"). Minimal, but a new burden on CLAUDE.md authoring discipline.
7. Foundation-kind closeout ceremony overhead: Lite lane does not exempt foundation doctrine — OBPI-05 runs the foundation walkthrough. Small cost but real.
8. Transition allow-list creates a two-phase validity window: before OBPI-02/03/04 close, the three target files are allow-listed (expected); after close, the entries must be removed. If a migration OBPI stalls, the allow-list entry becomes technical debt masking as compliance.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 9
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

- [ ] OBPI-0.0.20-01: Validator + allow-list foundation — Pydantic models (`UnscopedAllowlistEntry`, `Violation`, `UnscopedRulesResult`); `gz validate --unscoped-rules` flag; manifest schema fragment; initial allow-list with 3 entries (doomed files, `tracking_ref: ADR-0.0.20`); table-driven TDD tests; scorecard row addition; command-doc update.
- [ ] OBPI-0.0.20-02: Fold `agent-contract.md` — migrate judgment invariants to AGENTS.md (§ Prime Directive / § DO IT RIGHT / § Behavior Rules); move invariant 10a to CLAUDE.md addendum; extract pedagogy to `docs/governance/agent-contract-rationale.md`; delete canonical + remove allow-list entry + update inbound references + sync.
- [ ] OBPI-0.0.20-03: Fold `attestation-enrichment.md` — migrate em-dash pattern + canonical invocations table + lane behavior to AGENTS.md § Attestation; move ARB middleware detail to `docs/governance/arb-middleware.md`; update 6 Python docstring citations + 8 ARB command docs; delete canonical + allow-list entry + sync; flag ADR-0.36.0-OBPI-08 staleness.
- [ ] OBPI-0.0.20-04: Fold `defect-fix-routing.md` — migrate threshold tables + decision protocol to AGENTS.md § Defect-fix routing; move anti-patterns + origin GHI history to `docs/governance/defect-fix-routing.md`; delete canonical + allow-list entry + sync; update inbound references.
- [ ] OBPI-0.0.20-05: Closeout sweep + downstream flags — final grep sweep for residual references; verify mirror regeneration; file downstream GHIs (ADR-0.36.0 WBS refresh, ADR-0.38.0 baseline note, ADR-0.0.19 reference refresh); foundation-kind closeout walkthrough per ADR-0.0.18.

## Q&A Transcript

<!-- Interview transcript preserved for context; sourced from adr-interview.json -->

*Interview captured: 2026-04-21 via gz-design dialogue with operator; answers stored at `adr-interview.json` alongside this ADR. Key forcing-function excerpts are inlined in the Decision section above under "Forcing-function stress tests applied during design."*

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

*Populated at OBPI completion and ADR closeout.*

- [ ] Tests: `tests/validators/test_unscoped_rules.py`
- [ ] Docs: `docs/user/commands/validate.md`, `docs/governance/advisory-rules-audit.md` (scorecard row), `docs/governance/agent-contract-rationale.md` (new), `docs/governance/arb-middleware.md` (new), `docs/governance/defect-fix-routing.md` (new)

## Alternatives Considered

1. **Amend ADR-0.17.0 retroactively** — add 6th OBPI carrying the anti-regression invariant under the existing Validated ADR. **Rejected:** ADR-0.17.0 is Validated/Completed per the registry. Amending a completed ADR violates the ADR-as-record principle from ADR-0.0.18 taxonomy doctrine (Validated ADRs are point-in-time decisions; new concerns require new ADRs). Would also bypass the `gz-design` interview that this concern warrants on its own merits.

2. **Fold into ADR-0.36.0 as its 14th OBPI** — make the consolidation a reconciliation exercise under the existing instruction-file-reconciliation ADR. **Rejected** on three mismatches:
   - **Kind:** ADR-0.36.0 is feature-kind (inter-repo content reconciliation with airlineops); ours is foundation-kind (intra-repo structural invariant). Mixing violates ADR-0.0.18 taxonomy binding.
   - **Lane:** ADR-0.36.0 is Heavy per OBPI (13 OBPIs each Heavy); ours is Lite.
   - **Dependency inversion:** ADR-0.36.0 is already stale because its premise (the set of rule files it enumerates, including `.claude/rules/arb.md` which doesn't exist) has drifted; our work changes that set further, creating mid-execution churn for ADR-0.36.0's in-flight reconciliation.

3. **Shrink `agent-contract.md` in place (213 → ~90 lines) without consolidation** — produce a tighter version of the Claude-mirror rule file that keeps only judgment invariants and points at canonical homes for everything else. **Rejected** in earlier dialogue after measuring: ~60% of the 90-line shrunken draft still duplicates AGENTS.md § Prime Directive / § DO IT RIGHT / § Behavior Rules, preserving the drift vector. The bolder move (consolidation) captures ~1.5× more token savings (~183 lines vs. ~123 lines) and eliminates the cross-reference-to-keep-in-sync problem. Same principle that justifies cutting 213 lines justifies cutting the remaining ~50 duplicated lines.

4. **Inverse: trim AGENTS.md and let `agent-contract.md` be the Claude specialist** — move AGENTS.md's behavioral content into `agent-contract.md`, leaving AGENTS.md as a thin philosophical README with pointers. Frame `agent-contract.md` as "the operational contract, Claude-mirror-hosted." **Rejected** after content audit: of 213 lines in `agent-contract.md`, only ~3 are genuinely Claude-specific (invariant 10a references Claude tool names like `EnterPlanMode`). The content IS universal (ownership, craftsmanship, judgment, process/efficiency); making it a "specialist" would require writing Claude-specific content that doesn't currently exist — the wrong direction for solving a duplication problem. AGENTS.md standard's first line literally reads "Universal agent contract" — that is the correct home.

5. **Skip ceremony, do direct fix** — edit AGENTS.md and delete the three rule files in a `fix(governance):` commit. **Rejected** per `.gzkit/rules/defect-fix-routing.md` thresholds: diff size (~40 live files) far exceeds the 10-line direct-fix ceiling; scope crosses foundation agent-contract surfaces; trigger is not a defect surfaced in flight but planned architectural work; coverage needs a new validator scope with new tests. This is textbook OBPI-ceremony territory. It would also be ironic to bypass governance ceremony to clean up governance bloat — the credibility of the resulting invariant depends on the process that produced it.

6. **Park as pool ADR and defer** — file as `ADR-pool.agent-rule-placement-invariant` for later prioritization. **Rejected:** the design is complete (5 approved sections), the OBPI-01 work is scoped, lane is clear, operator directive is "do foundation adr" with "we always immediately book foundation adrs." Pool parking is for fuzzy-scope ideas awaiting prioritization; this is neither.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.20 | Draft | | | |
