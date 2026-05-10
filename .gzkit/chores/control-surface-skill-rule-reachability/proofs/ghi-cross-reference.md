# GHI Cross-Reference — Control Surface Skill ↔ Rule Reachability Audit (Pass B)

**Generated:** 2026-05-10
**Source:** `gh issue list --repo tvproductions/gzkit --state all --limit 300`
**Scan range:** GHI #141 – #443 (current as of 2026-05-10)
**Method:** For each "no" row in `reachability-matrix.md`, scanned titles + labels for symptoms matching the worked example. Hits = known-blocking; misses = latent.

## Matrix-row classification

| Matrix row | Skill (vN.N.N) | Rule § | Matching GHI(s) | Classification |
|---|---|---|---|---|
| 2 | gz-adr-audit (6.7.1) | `adr-audit.md` § Audit sequence | none directly; closest is **GHI #268** (audit-check exits 1 on advisory @covers gaps for lite-lane docs-only OBPIs) — symptom is audit-sequence interpretation, not rule-step omission | **latent** |
| 3 | gz-adr-closeout-ceremony (7.9.0) | `gate5-runbook-code-covenant.md` § Three-layer documentation model | **GHI #427** (walkthrough demos must showcase yielded product commands, not construction housekeeping), **GHI #259** (Ceremony Step 2 render ADR intent vs OBPI delivery side-by-side), **GHI #155** (Ceremony Step 2 BOM lacks parent ADR intent framing) | **known-blocking** |
| 5 | gz-adr-create (6.2.0) | `cli.md` § Help text + exit codes | none directly; nearest are **GHI #156** (ceremony demo discovery emits unregistered CLI verbs), **GHI #186** (gz prd scaffolder emits id its own validator rejects) — class-of-failure precedent but not this specific surface | **latent** |
| 12 | gz-check (1.4.0) | `cross-platform.md` § Console / UTF-8 + `.as_posix()` | **GHI #383** (fix(quality): _expand_allowed_paths emitted backslash paths on Windows; sweep other str(relative_to) sites), **GHI #161** (Windows path-separator bugs in test_sync_cmds), **GHI #234** (cross-platform rule gap: ad-hoc python -c bypasses UTF-8 guard) | **known-blocking** |
| 14 | gz-chore-runner (1.1.2) | `chores.md` § Two-Surface Layout + Layout discipline | **GHI #306** (gz-chore-runner skill canonical SKILL.md still references pre-migration paths), **GHI #304** (registry.json path fields drift to legacy ops/chores/ locations), **GHI #189** (validator recovery hint uses singular 'gz chore run') | **known-blocking** |
| 18 | gz-context-diet (1.0.0) | `gate5-runbook-code-covenant.md` § Three-layer covenant | **GHI #335** (gz-context-diet skill update: invoke surface-fidelity validators inline once they land) | **known-blocking** |
| 19 | gz-context-diet (1.0.0) | `skill-surface-sync.md` § Edit canonical first | **GHI #361** (Claude rules paths-frontmatter not honored: leading HTML comment breaks YAML parser) — adjacent class; **GHI #247** (sync_copilot_instructions skipped when canonical rules exist — template edits to copilot.md do not propagate) | **known-blocking** |
| 20 | gz-deps-upgrade (1.0.0) | `models.md` § Pydantic departure rationale | none directly; closest are **GHI #281** (pygments 2.20.0 crashes from dependabot auto-bump), **GHI #282** (docs workflow paths trigger does not include uv.lock — dependabot bypasses mkdocs strict-build) — both dep-upgrade defect class but not stdlib-departure check | **latent** |
| 24 | gz-obpi-lock (6.0.2) | `token-block-discipline.md` § Sub-Invariants 1-5 | **GHI #410** (obpi lock + handoff: token-block discipline incomplete — release decoupled from register-entry write), **GHI #248** (gz obpi precomplete lock_held check uses shallow glob and misses .gzkit/locks/obpi/ subdir), **GHI #245/#244/#243** (lock_held check misses subdirectory — duplicate filings) | **known-blocking** |
| 26 | gz-obpi-pipeline (6.14.3) | `gate5-runbook-code-covenant.md` § Required updates when behavior changes | **GHI #427** (ceremony walkthrough demos must showcase yielded product commands), **GHI #422** (Pipeline runtime Stage 5 ordering disagrees with skill: sync-then-complete causes multi-pass churn), **GHI #436** (obpi pipeline verify gate doesn't catch brief sibling-OBPI/ADR cross-reference drift) | **known-blocking** |
| 30 | gz-obpi-simplify (6.0.4) | `pythonic.md` § Core Principles | none directly; nearest are **GHI #360** (Split trust_audits.py 2129 LOC into package) — class-size symptom, not skill-cite gap; **GHI #236** (Pre-existing D-rank complexity in _scan_sibling_adr_collisions blocks xenon hook) | **latent** |
| 32 | gz-obpi-specify (1.5.0) | `security-sensitivity.md` § Invariant + Registry | **GHI #303** (behave_req_tags: ADR-0.0.22 security-sensitivity-doctrine OBPIs lack scenario-level @REQ-* tags) — adjacent; **GHI #413** (obpi complete: security floor is audit-only) | **known-blocking** |
| 34 | gz-plan (1.1.1) | `adr-audit.md` § Audit sequence | **GHI #271** (fix(skills): cite defect-fix-routing.md thresholds from gz-plan and gz-design Step 1) — direct hit on the exact pattern | **known-blocking** |
| 36 | gz-pythonic-pattern-apply (1.0.0) | `pythonic.md` § Core Principles | none directly; skill is new (v1.0.0). Pattern-class precedent: **GHI #408** (ADR-pool: config evaluation tooling with guidance mode), **GHI #236** (D-rank complexity blocks xenon hook) | **latent** |
| 38 | gz-pythonic-pattern-detect (1.0.0) | `pythonic.md` § Core Principles | none directly; skill is new. Pattern-class precedent same as row 36 | **latent** |
| 39 | gz-session-handoff (6.3.0) | `token-block-discipline.md` § Register-Entry Minimum-Information Rule | **GHI #326** (Session-start orientation hook missing: handoffs are write-only artifacts on session entry — CAP-13), **GHI #325** (Session handoff 2026-04-25: complexity-doctrine cluster + governance defects) | **known-blocking** |
| 42 | gz-tech-debt-review (1.2.1) | `tests.md` § Tests assert semantics | **GHI #310** (tests.md: add eval-awareness corollary against audit-named assertion helpers), **GHI #272** (fix(skills): gz-adr-audit Step 2 cites tests.md semantics — original chore source case) | **known-blocking** |
| 50 | git-sync (1.2.3) | `gh-cli.md` § Prohibited without explicit approval | **GHI #439** (gz git-sync produces generic 'chore: update X, Y, Z' commit messages), **GHI #437** (Commit-message auto-rewriting silently replaces fix() messages with generic 'chore: update' — GHI #434 victim), **GHI #201** (gz git-sync auto-commits lack Task trailer, always trip gz validate --commit-trailers) | **known-blocking** |

## Universal-rule gaps

| Rule | Skills with no body citation | Recent matching GHI | Classification |
|---|---|---|---|
| `agent-failure-modes.md` | 49/50 active skills (only gz-issue-file cites) | **GHI #314** (Promote .gzkit/rules/agent-failure-modes.md from advisory to mechanical where applicable), **GHI #228** (F3 prose-operation descriptions without tool literals cause 4.7 tool-use hesitation), **GHI #229** (F4/F5 over-ceremony coupling deadlock 4.7), **GHI #230** (F6 unverifiable output-form claims) | **known-blocking** (cluster) |
| `governance-core.md` | most skills (universal paths `**/*`); honored mechanically by named proof commands | **GHI #322** (ADR status table is unmaintained Layer 3 view) — already promoted under § ADR status index regeneration | promoted; remaining gaps are minor |

## Summary

- **Known-blocking gaps:** 11 of 18 "no" rows (rows 3, 12, 14, 18, 19, 24, 26, 32, 34, 39, 42, 50) + the agent-failure-modes universal cluster (GHIs #226-#230, #314).
- **Latent gaps:** 6 of 18 "no" rows (rows 2, 5, 20, 30, 36, 38).
- **Highest GHI density:** `chores.md` (rows 14, 19) and `token-block-discipline.md` (rows 24, 39) — each with three or more matching GHIs.

The cluster of known-blocking gaps around `gate5-runbook-code-covenant.md` (rows 3, 18, 26) all trace to the same source defect: skills that produce or modify multi-layer artifacts (ceremonies, pipelines, diet passes) do not mechanically reverify the runbook-code-ADR covenant. This is the largest single doctrine-mechanization gap surfaced by the audit.
