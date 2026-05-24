# gzkit Release Notes

## v0.27.0 (2026-05-24)

**ADR:** ADR-0.27.0-namespace-router-product-surface

Feature ADR closeout: the first-stage namespace-router surface lands as product, giving operators and agents a thin intent-table layer over the flat skill catalog so the GSD-comparison surface is no longer the only entry point. Seven routers, mechanical coverage enforcement, and full vendor-mirror parity ship in one cut.

### Delivered

- **OBPI-0.27.0-01 — router-skill-files.** Six namespace-router `SKILL.md` files under `.gzkit/skills/` (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) carry intent-to-skill tables only — no procedure, no ceremony duplication. Each router stays under the reconciled ≤950-byte budget (5001 bytes total across the 7-router set after OBPI-04 added `gz-chores`; worst case `gz-governance` 926 bytes), roughly 9× smaller than the 8440-byte mean skill.
- **OBPI-0.27.0-02 — router-surface-sync.** Routers propagate from the canonical `.gzkit/skills/` surface to all three vendor mirrors (`.agents/skills/`, `.claude/skills/`, `.github/skills/`) plus the wheel-shipping `src/gzkit/skills/` pkg copy via `gz agent sync control-surfaces`. Three locked-in REQ-derived tests in `tests/skills/test_namespace_router_surface_sync.py` assert byte-equivalence across all 24 router-mirror pairs and active-catalog discoverability on every test run.
- **OBPI-0.27.0-03 — router-tables-validator.** New `gz validate --router-tables` mechanically enforces both directions of the router contract: Direction 1 (routed slug must resolve to a canonical `.gzkit/skills/<slug>/SKILL.md`) fail-closes via the policy-breach taxonomy (exit 3); Direction 2 (every concrete skill reachable from at least one router) emits advisory findings (exit 1). Router detection is structural — any skill body containing `| Intent | Skill |` qualifies — so future routers register without hard-coded slug lists.
- **OBPI-0.27.0-04 — router-coverage-completion.** Added the 7th `gz-chores` router and routed the 16 previously-unrouted concrete skills under their natural router homes, closing every Direction-2 advisory surfaced by OBPI-03's validator. `gz validate --router-tables` now exits 0.

### Gate Evidence

All applicable gates satisfied for the Lite-lane foundation closeout:

- **Gate 1 (ADR):** ADR-0.27.0 recorded with full Checklist / Decomposition Scorecard / per-OBPI evidence.
- **Gate 2 (TDD):** `arb-step-unittest-901eac2fc358421db70c8feafcb53904` — full suite 5508/5508 pass.
- **Code Quality:** `arb-ruff-e5c1276f5f654147857eb8df73606df7` (ruff clean) and `arb-step-typecheck-0959e17ce0b046ebb5fa14888ba66981` (ty clean).
- **Gate 5 (Human):** Operator attestation `Completed` recorded by g0 at ceremony Step 6 (2026-05-24); brief-level attestation universal per ADR-0.0.36.
- **Validator proof:** `uv run gz validate --router-tables` exits 0.
- Gate 3 (docs/mkdocs) and Gate 4 (BDD) not required — lane is `lite` per ADR-0.0.36 axis rules.

### Surfaced & tracked

- **#524** — `ADR-0.2.0-gate-verification` fails `gz validate --documents` (status enum `Validated` not in canonical set; missing `## Decomposition Scorecard` and `## Checklist`). Pre-convention-era ADR package not caught by GHI #480/#500 bulk migrations (which targeted `foundation/`, not `pre-release/`). Filed under `/ghi-author` after #523 was closed for Behavior Rule #13 remediation (original filed via direct `gh issue create`).

### Stats

- 1 feature ADR closeout (ADR-0.27.0)
- 4 OBPIs completed, each with universal human attestation
- 1 GHI surfaced (#524); 1 GHI re-filed under canonical authoring path (#523 → #524)

## v0.26.6 (2026-05-22)

Governance infrastructure hardening: lock-manager identity fix, validator corpus scoping, scaffolder regression closure, hexagonal terminology correction, and closeout of the Universal OBPI Attestation (ADR-0.0.36) foundation ADR.

### Foundation ADR Closeout

- **ADR-0.0.36** — Universal OBPI Attestation reached `Validated` status. Human attestation is now universally required for every OBPI completion regardless of parent ADR kind or lane. The `lite`-lane self-close path is formally closed, enforced at runtime by `_requires_human_obpi_attestation`.

### Runtime Fixes

- **#484** — Fixed `CLAUDECODE` env-var typo in `lock_manager.py`. The check read `CLAUDE_CODE` (with underscore) while Claude Code exports `CLAUDECODE=1` (no underscore), causing `resolve_agent()` to fall through to a PID-based id on every call. Two `uv run gz` subprocesses in the same session always got different ids, making every Stage 5 lock release fail with an ownership error and forcing `--force` as a workaround. Both `resolve_agent` and `resolve_session_id` are now correct.

### Validator & Schema

- **#483** — Fixed `gz validate --kind-invariance` silently skipping 10 legacy foundation ADRs that predate ADR-0.0.17's `kind:` frontmatter mandate. The validator now uses filesystem location (`/foundation/` directory) as the primary predicate and flags ADRs without `kind: foundation` frontmatter, producing the work list ADR-0.0.35 Negative Consequence #5 promised.
- **#486** — Added waiver entry for the `| jq` pipe on OBPI-0.0.36-02 line 261 (a historical evidence block recording a command actually executed during implementation). The `test_utf8_prefix_rule_9` test now passes; the waiver preserves evidence-chain integrity rather than retroactively rewriting it.
- **#500** — Scoped `gz validate --documents` to skip the historical OBPI brief corpus for section-presence checks. The validator now distinguishes historical (pre-current-schema) briefs from newly-authored ones, eliminating 3,589 non-actionable false positives. Strict authored and completion-readiness checks remain in `gz obpi validate --authored` and `gz obpi complete`.
- **#502** — Fixed `agent-insights.jsonl:75` schema violation: `type=discovery` is not a valid `InsightType` (`Literal['defect', 'defect-resolution', 'improvement']`). The entry's type was corrected with operator attestation. The test `test_insights_shape_ghi_358` now passes.
- **#511** — Retargeted `gz validate --interviews` to check for an embedded `## Q&A Transcript` section in the ADR body rather than a separate `.gzkit/transcripts/<ADR-ID>-interview.md` file that has never been produced by any ADR authoring flow. Converts 104 false positives into 44 true findings (ADRs that predate the transcript convention and genuinely lack a receipt).
- **#515** — Reconciled the interview-transcript surface after the GHI #511 retarget. Updated `docs/design/prd/PRD-GZKIT-1.0.0.md` (3 references) and `gz interview` writer to the embedded-section form; documented the 44 pre-convention ADRs awaiting operator decision on backfill vs. waiver vs. grandfather cutoff. Wired `--interviews` into the `gz check` default scope once the corpus is clean.

### Scaffolder / ADR Pipeline

- **#494** — Closed scaffolder regression #4 of the bare-id `adr_created` class. The `gz plan create` scaffolder now derives the `adr_created` ledger event id from the canonical on-disk slug-form directory name rather than an intermediate variable, preventing bare-semver events regardless of intermediate frontmatter state.
- **#505** — Fixed `gz interview adr` scaffold path: corrected the flat-directory layout (was writing to `docs/design/adr/<id>.md` instead of the slug-package layout) and validated `doc_id` against canonical slug-form before ledger emission. Closes the sibling-cut of the GHI #494 bare-id class in the interview path.
- **#495** — Authored all 10 ADR-0.0.37 OBPI briefs with per-OBPI scope: actual `src/`, schema, test, and doc targets in Allowed Paths; OBPI-specific Requirements (not the full 33-item ADR Decision dump); falsifiable Acceptance Criteria with REQ-IDs; relevant Verification commands. OBPI-10 lane corrected to Lite (docs-only scope).

### CLI Improvements

- **#485** — Fixed `gz specify --author` mode scoping bug. `_extract_decision_as_requirements` received no `--item N` filter and dumped every ADR Decision bullet into every OBPI brief. The function now accepts and applies the checklist item index to scope requirements to the specific OBPI, making `--author`-mode briefs pipeline-ready without manual narrowing.
- **#490** — `gz patch release --dry-run` now mechanically enumerates foundation-ADR closeouts (ADRs at `Validated` status with a Gate-5 `validated` receipt in the ledger since the last tag). Removes operator-memory dependency for the foundation-closeout release qualifier, achieving hexagonal port/adapter parity in the patch-release cadence.
- **#504** — Fixed `gz governance render --target agents-md` emitting literal `{project_name}`, `{project_purpose}`, `{tech_stack}`, `{skills_canon_path}` tokens instead of concrete substituted values. The broken template-variable substitution step in `src/gzkit/governance/compose.py` caused `gz validate --invariant-coherence` to exit 3 and `gz check` to go repo-wide red.

### Governance / Doctrine

- **#488** — Renamed `complexity-advisor` and `complexity-guide` skills to `gz-complexity-advisor` and `gz-complexity-guide` to align with the `gz-` prefix convention followed by 45 of 52 skill directories. Added `data/skill_naming_exemptions.json` (whitelisting `ghi-*`, `git-sync`, `airlineops-parity-scan`) and a mechanical `gz validate --skill-naming` scope to fail-close future naming drift.
- **#489** — Corrected hexagonal terminology from "plug"/"plugs" to "adapter"/"adapters" across `gz-design` SKILL.md, `docs/user/concepts/foundation-feature-invariance-test.md` (13 instances), and the ADR scaffold template stub. The canonical term is Alistair Cockburn's "Ports and Adapters" (2005); every new foundation ADR now prompts "port vs. adapter" instead of "port vs. plug."

### Code Quality

- **#493** — Deleted orphaned `src/gzkit/sync_skills_validation.py` (plural variant, zero importers, dead code). Documented the consolidation path for the remaining two overlapping skill-frontmatter validation modules (`skills_audit.py` and `sync_skill_validation.py`).
- **#501** — Split `src/gzkit/events.py` (673 lines, over the 600-line module limit) into `event_evidence.py` (nested evidence models) and `events.py` (typed ledger event union). Added `frozen=True` to `ReqProofInput`, `ScopeAudit`, `GitSyncState` per `.claude/rules/models.md` immutable-model doctrine.

### Stats

- 17 GHIs closed
- 1 foundation ADR closeout (ADR-0.0.36)

## v0.26.5 (2026-05-17)

Patch release fixing a section-scoping defect in `gz obpi complete` that caused attestation substitution to target the wrong line when the implementation summary contained a `- Attestation:` bullet.

### CLI Fixes

- **#479** — Fixed `gz obpi complete` exiting with "Missing human attestation content" when `--implementation-summary` included a `- Attestation:` bullet. The `_update_human_attestation` function applied `re.sub` with `count=1` against the full brief string, causing the first globally-matched `^- Attestation:` line — inside the Implementation Summary section — to be substituted instead of the correct line inside `## Human Attestation`. The fix scopes substitution to the `## Human Attestation` section body, matching the section-scoped logic already used by `_has_human_attestation_content`.

### Stats

- 1 GHI closed

## v0.26.4 (2026-05-16)

Closes four runtime defects surfaced during the ADR-0.0.32 closeout ceremony and a follow-on persona dispatch coverage audit: validator recursion fix, upgrade carve-out enforcement, skill surface cleanup, and ceremony-persona wiring.

### CLI Fixes

- **#465** — Fixed `gz upgrade` to honor ADR-0.0.32 § Named exceptions. Invoking `gz upgrade` (default surface set) was incorrectly copying `src/gzkit/hooks/` Python files and `src/gzkit/templates/skills/` into `.gzkit/`, polluting the canonical authored surface with vendor-coupled package machinery that the ADR explicitly carves out of the dual-surface byte-parity model. The fix consults the existing `_classify_*` helpers (from OBPI-15) and skips hooks and package-only files during the upgrade pass.
- **#468** — Fixed `gz validate --documents` to iterate recursively through nested ADR package directories. The previous flat glob (`docs/design/adr/*.md`) never reached foundation and pre-release ADRs under `docs/design/adr/foundation/ADR-*/ADR-*.md`, allowing bare-semver frontmatter IDs (e.g. `id: ADR-0.0.43` without a slug suffix) to pass the schema pattern check silently. Five ADRs with bare IDs survived undetected until `gz adr report` surfaced a slugless row on 2026-05-15. Validation now recursively traverses all nested ADR package directories.

### Skill Surface & Distribution

- **#464** — Removed 18 retired-skill tombstone stubs (`lifecycle_state: retired`) from `.gzkit/skills/`, `src/gzkit/skills/`, and all three vendor mirror directories. The `package_only` classifier path was accommodating these stubs in the shipped wheel against its intended scope (non-md package-machinery files, not retired SKILL.md entries). Establishes delete-on-retire doctrine: when a skill is superseded or consolidated, its directory is deleted rather than left as a stub. The 18 removed skills were all superseded by named successors documented in their `archived_into:` frontmatter fields.

### Ceremony & Persona Infrastructure

- **#470** — Wired role-matched persona dispatch across all four ADR/OBPI ceremony skills. `gz-adr-audit` was missing its `persona:` frontmatter declaration entirely; `gz-adr-closeout-ceremony` and `gz-adr-evaluate` declared a driver persona but dispatched no subagent reviewers. All four ceremony skills now carry `persona: pipeline-orchestrator` frontmatter and include a `## Persona Dispatch` contract section specifying which subagent roles are dispatched and at which stage. Narrator persona wiring into OBPI Stage 4 evidence presentation was completed. Grounded in ADR-0.0.11 (persona as first-class control surface).

### Stats

- 4 GHIs closed
- 1 GHI excluded (#467 — label_only, no src/gzkit/ commits)

## v0.26.3 (2026-05-15)

Closes 20 runtime-labelled GHIs spanning pipeline ceremony reliability, canonical surface packaging, governance validation hardening, git-sync commit archaeology, and test suite hygiene.

### Pipeline & OBPI Ceremony

- **#433** — Fixed `gz plan audit` silently dropping dotfile-rooted paths (`.gzkit/`, `.claude/`, `.agents/`, `.github/`) from creates-declarations due to `lstrip("./")` stripping the leading dot. Replaced with `removeprefix("./")` in `brief_path_validity.py`, unblocking plan-audit for any OBPI that creates files under those prefixes.
- **#435** — Fixed `gz obpi pipeline --from=sync --evidence-json` ignoring `attestation_text`, `implementation_summary`, and related fields, which forced agents to abandon the pipeline and call `gz obpi complete` directly. The pipeline now extracts and passes all completion fields from the JSON payload.
- **#436** — Added `gz validate --brief-cross-references` that fail-closes when brief cross-references (sibling OBPI and peer ADR IDs) have drifted from on-disk identifiers after reorganization — previously all verify-gate checks passed on stale references.
- **#456** — Resolved contradiction between `gz-plan-audit` SKILL.md's "Stop cleanly" tail instruction and the `gz-obpi-pipeline` Iron Law. The plan-audit skill now disambiguates by caller context: standalone invocations end the turn after the report; pipeline sub-step invocations return control to Stage 2 without ending the turn.
- **#462** — Fixed `gz obpi complete` security auto-detect deadlocking completion for briefs whose allowed paths overlap a registered security surface but introduce no actual security risk. Added a per-brief `--accept-security-autodetect-floor` escape valve parallel to the existing `--accept-uncovered` REQ waiver pattern.

### Governance Validation

- **#431** — Added `gz validate --brief-demo-section` that fail-closes when a heavy-lane CLI-shipping OBPI brief omits the `## Demo` section, preventing `gz closeout` walkthrough-discovery from silently degrading to `--help` invocations.
- **#432** — Added speculative-skip marker convention to the brief command-shape check in `gz obpi validate --authored`, enabling OBPIs introducing new CLI verbs to annotate forward-reference invocations with `<!-- gz-validate-skip: command-shape -->` before the verb is registered — matching the existing escape-hatch pattern in the cli-alignment validator.
- **#438** — Added `gz validate --orphaned-implementation` that detects OBPIs where a lock was force-released after artifact edits on allowed paths with no completion event — the implementation-without-ceremony state that previously required manual ledger forensics to diagnose.
- **#441** — Fixed `gz arb step` accepting step names that the receipt-binding regex would later reject, causing ARB receipts written with those names to fail the receipt-lookup at attestation time. Step names are now validated against the binding regex at write time.
- **#466** — Fixed the `gz adr audit-check` covers-backfill detector incorrectly flagging same-commit block-creation as a backfill, which was blocking ADR-0.0.32's audit completion.

### Commit & Git Sync

- **#437** — Fixed `gz git-sync` silently overwriting agent-authored `fix()` / `feat()` commit messages with its generic `chore: update X, Y, Z` template when an end-of-file-fixer auto-fixed unrelated files between retry attempts. Messages already matching conventional-commit format are now preserved verbatim.
- **#439** — Improved `gz git-sync` commit-message quality: for diffs containing source, ADR/OBPI body, doctrine, schema, or test changes, the autostamper now refuses the generic path-list message and surfaces an explicit message-authoring prompt instead.

### Canonical Surface & Distribution

- **#449** — Extended `gz agent sync control-surfaces` to copy `.gzkit/<surface>/**` → `src/gzkit/<surface>/**` in dependency order (authored → package, then authored → vendor mirrors), eliminating the manual `cp` step that operators had to remember after editing canonical surfaces.
- **#450** — Added `gz upgrade [--surface ...] [--force] [--dry-run]` subcommand for adopter-side canonical surface refresh from the installed wheel, with per-surface filtering and three-state (IDENTICAL/STALE/EDITED) conflict detection matching `gz init --update`.
- **#453** — Removed the stale `templates/skill.md` dependency from `scaffold_skill` (superseded by OBPI-0.0.32-02's `importlib.resources` path) and cleaned up the orphaned `CORE_SKILLS["lint"]` entry pointing at a retired skill.
- **#455** — Updated `data/security_surfaces.json` registry after the OBPI-0.0.32-03 physical migration: `deserialization_user_input` glob updated from `src/gzkit/rules.py` to `src/gzkit/rules/__init__.py`, unblocking OBPI completions that touched the migrated path.
- **#457** — Synced missing `AGENTS.md` and `complexity-thresholds.json` to the `src/gzkit/rules/` package mirror, resolving dual-surface parity test failures surfaced during GHI #453 closeout.

### Test Suite & Quality

- **#444** — Moved `coverage-40pct` chore from lite lane (120s) to medium lane (300s), resolving the timeout caused by coverage instrumentation overhead on the current 101s test suite. #445 is the durable test-speed fix.
- **#445** — Fixed `test-isolation-compliance` health-audit failures: mocked `gz cli audit` at the subprocess boundary to eliminate 4 slow tests (3–3.2s each), suppressed 344 lines of validator stdout noise in non-quiet contexts, bringing the suite back under the 60s smoke contract.
- **#448** — Hardened `gz chores run control-surface-rule-conflicts` acceptance with a resolvability-check script that parses `conflict-matrix.md` and fails closed when any Evidence column citation is unresolvable via `gh issue view`, `git log`, or `agent-insights.jsonl`, directly enforcing the `ADR-pool.control-surface-rule-pair-conflict-audit` audit-row schema.

### Stats

- 20 GHIs closed

## v0.26.2 (2026-05-10)

Patch release covering red-team-surfaced security and trust hardening, ledger schema validation tightening, OBPI pipeline runtime fixes, and governance surface improvements. 14 GHIs closed.

### Security & Trust Hardening

- **#411** — Fixed `gz status` rewriting post-validation gate failures from `fail` to `pass`; the operator-facing status surface no longer hides current failing observations behind lifecycle authority.
- **#412** — Removed forgeable marker-file proxy from `--attestor-present`; agent-relayed attestation now requires provenance beyond a writable repo file.
- **#413** — Closed `gz obpi complete` security-floor bypass: auto-detected security-sensitive allowed paths now trip the security gate even when brief frontmatter omits `sensitivity: security`.
- **#415** — Removed `shell=True` from the shared quality command runner; governance gate execution no longer presents a command-injection surface.

### Validation & Schema Integrity

- **#2** — Enforced JSONL schema validation on ledger entries; malformed or semantically invalid events are no longer silently accepted by `gz validate`.
- **#414** — Fixed `meta-receipt-bind` events violating ledger schema (`receipt_event` enum requires `completed`/`validated`).
- **#426** — Migrated complexity thresholds from regex-parsed markdown to structured JSON config (`src/gzkit/complexity/thresholds.py`); deterministic tooling now reads structured data.

### Pipeline Runtime & CLI Fixes

- **#3** — Added ledger-derived sync for OBPI brief derived fields; `gz adr status` and `gz status` no longer emit false negatives from drift between manually-edited fields and ledger truth.
- **#403** — Fixed `gz plan audit` false-positive on brief allowed-paths that are intentionally new-file creation targets (GHI #393 follow-up).
- **#420** — Restored OBPI Stage 3 scope discipline: cross-OBPI failures from unrelated work no longer block new OBPIs through full-repo `gz check`.
- **#421** — Enabled parallel ARB receipt execution at OBPI Stage 3; lint/typecheck/test/mkdocs/behave no longer serialize through fresh `uv` processes.
- **#422** — Reordered pipeline runtime Stage 5 to match skill semantics: complete-then-sync replaces sync-then-complete and eliminates multi-pass churn.

### Governance Surface

- **#409** — Enforced model-selection routing in skill frontmatter; `SkillFrontmatter.skill_model` is now a required `Literal["haiku", "sonnet", "opus"]` validated by `gz validate --surfaces`.
- **#427** — Closeout walkthrough demos now showcase the ADR's yielded product commands instead of construction housekeeping (ARB-wrapped quality checks).

### Stats

- 14 GHIs closed (4 security/trust, 3 schema/validation, 5 pipeline-runtime, 2 governance-surface)

## v0.26.1 (2026-05-05)

Patch release closing fifteen behavior-level defects across the covers-backfill heuristic, REQ-coverage gate, validator wiring, ledger graph, pipeline runtime, and cross-platform path handling — surfaced and resolved during ADR-0.0.27 (Exemplar Corpus Doctrine) audit and OBPI-0.0.27 closeout work.

### Covers-Backfill Heuristic

- **#382** — Fixed false-positive flagging of same-commit-creation as backfill, eliminating 79 spurious failures on ADR-0.0.23 audit.
- **#385** — Stopped over-flagging `gz-git-sync` ceremony commits that were blocking the ADR-0.0.24 audit.
- **#386** — Taught the heuristic to distinguish `Ceremony: gz-git-sync` bundles from cosmetic backfill.
- **#390** — Stopped over-flagging string-literal fixtures and pre-trailer ceremony commits.

### REQ-Coverage Gate (`gz obpi complete`)

- **#389** — Made the completion gate honor `features/` BDD scenario tags (`@REQ-*`); previously it only walked `tests/` decorators and silently dropped BDD-only coverage.
- **#395** — Stopped marking BDD-only REQs as `failing-cover` when behave references were being run through unittest.

### Validator and Ledger Wiring

- **#391** — Propagated the `attested` flag for `audit_receipt_emitted` events with `receipt_event=validated`; the QC roll-up was reading Gate 5 as PENDING on Validated ADRs.
- **#392** — Stopped stale post-validation `gate_checked:fail` events from poisoning the QC display on Validated ADRs.
- **#394** — Made `gz validate --evaluation-justify-binding` reachable as a solo handler and corrected its exit code drift from 1 back to the canonical 3.

### Pipeline Runtime and Skill Audit

- **#399** — Self-healed orphaned `.pipeline-active-{OBPI}.json` markers when Stage 5 is interrupted; `gz obpi reconcile` now removes provably stale markers when ledger state is `attested_completed`.
- **#379** — Excluded `__pycache__/*.pyc` from canonical skill-asset collection so `gz gates --adr` stops failing Gate 3 on regenerable bytecode caches.
- **#400** — Authored the destination CLI verb for the `gz-complexity-distill` skill (deferred from OBPI-0.0.27-06).

### Cross-Platform and Brief Hygiene

- **#383** — Replaced backslash-emitting `str(path.relative_to(...))` sites under `src/gzkit/quality.py` with forward-slash `as_posix()` so glob-expanded paths match canonical prefix literals on Windows.
- **#393** — Corrected stale OBPI-0.0.26-04 brief allowed-paths from the refactored `trust_audits.py` module to the actual `validate_cmd.py` + `tasks.py` targets.
- **#398** — Fixed `_absorb_lizard_row` measurement parsers that were silently emitting zero for `lizard_nesting_depth` and `cohesion_lcom4` across the entire exemplar corpus.

### Stats

- 15 GHIs closed
- Foundation ADR-0.0.27 (Exemplar Corpus Doctrine) reached Validated since v0.26.0 — patch ships its Decision-text correction (#401) under the same release.

## v0.26.0 (2026-05-01)

**ADR:** ADR-0.26.0-governance-library-module-absorption

Item-by-item evaluation and absorption of 12 opsdev/lib governance modules
(~6,200 lines) into gzkit. Each OBPI records a per-module decision (Absorb,
Confirm, or Exclude) backed by code-level subtraction-test evidence.

### Delivered

- **OBPI-0.26.0-01-adr-management** — Confirm. opsdev/lib/adr.py (1,588 L)
  evaluated against gzkit's distributed ADR management surface; gzkit superior
  across 17 dimensions (Pydantic frozen models vs plain dicts, typed AdrId vs
  4-digit regex, kind/semver binding, 5-gate pipeline, event-sourced ledger,
  ARB receipts).
- **OBPI-0.26.0-02-references** — decision recorded with code-level rationale
  for cross-reference / link management surface.
- **OBPI-0.26.0-03-adr-recon** — decision recorded comparing opsdev's
  Layer-3 markdown-table patching to gzkit's Layer-1 rewriting + Layer-3
  regeneration via `gz obpi reconcile`, `gz frontmatter reconcile`,
  `gz register-adrs`, and `governance/adr_status_index.py`.
- **OBPI-0.26.0-04-adr-governance** — decision recorded against gzkit's
  ledger-centric policy enforcement surface.
- **OBPI-0.26.0-05-ledger-schema** — decision recorded comparing opsdev's
  dedicated schema module to gzkit's inline schema in `src/gzkit/ledger.py`.
- **OBPI-0.26.0-06-drift-detection** — decision recorded for governance
  drift-detection surface.
- **OBPI-0.26.0-07-adr-traceability** — decision recorded for
  ADR-to-artifact traceability-chain construction.
- **OBPI-0.26.0-08-validation-receipt** — decision recorded comparing
  opsdev's typed `ValidationAnchor` / `ValidationReceipt` to gzkit's
  distributed receipt surface.
- **OBPI-0.26.0-09-adr-audit-ledger** — Confirm reaffirmed against
  ADR-0.25.0 precedent; gzkit's distributed Gate 5 audit surface
  (commands/adr_audit.py 758 L + validate_pkg/ledger_check.py 379 L +
  commands/obpi_audit_cmd.py 423 L = ~1,560 L) preserves the verdict.
- **OBPI-0.26.0-10-cli-audit-lib** — Confirm reaffirmed; gzkit's
  `commands/cli_audit.py` + `doc_coverage/` package (~1,300 L) preserves
  the ADR-0.25.0 verdict.
- **OBPI-0.26.0-11-artifacts-lib** — Exclude reaffirmed; gzkit's
  `registry.py` + `sync.py` artifact-management surface preserves the
  ADR-0.25.0 verdict.
- **OBPI-0.26.0-12-docs-lib** — Confirm reaffirmed; gzkit's
  `doc_coverage/` package (~802 L) plus `mkdocs build --strict`
  integration preserves the ADR-0.25.0 verdict.

### Gate Evidence

All 5 GovZero gates satisfied. Per-OBPI human attestation by g0 on
all 12 briefs. Closeout walkthrough green: lint
`arb-ruff-9453b996c0424e49a0de093608f7ca9d`, typecheck
`arb-step-typecheck-68c819510879480da0e9159264fe5d32`, unittest
`arb-step-unittest-24779d6c71194f3eae87b4b3a731e3c2`, mkdocs
`arb-step-mkdocs-0d69e336977a4624a738ee22484e7e19`. `gz validate --documents`
clean.

## v0.25.19 (2026-04-30)

Maintenance and governance-hardening release closing 17 defects and enhancements
surfaced during ADR-0.0.20 / 0.0.21 / 0.0.22 closeout work — concentrated on
ADR-id invariants, CLI per-flag doc coverage, closeout ceremony integration, and
trust_audits.py decomposition.

### ADR ID & Schema Hardening

- **#344** — Fixed `gz plan create --name` accepting bare semver literals; the
  canonical-id composer now refuses bare-semver-only emission, closing the
  GHI #279 class recurrence.
- **#345** — Replaced hand-curated `SEMVER_ID_RENAMES` with on-disk drift
  auto-detection; `gz migrate-semver` walks ADR frontmatter and proposes
  renames continuously instead of accumulating per-drift manual entries.
- **#346** — Tightened `adr.json` schema so the slug suffix is mandatory on
  non-pool ADRs; bare-id frontmatter now fails Gate 1 instead of validating
  clean.
- **#352** — `gz adr promote` deletes the source pool file after scaffolding
  the canonical package, ending stale-pool-file accumulation.

### CLI Per-Flag Doc Coverage

- **#350** — Added per-flag doc coverage to `gz cli audit`; new flags on
  existing subcommands require a section header in the corresponding command
  doc.
- **#353** — Drained `_PER_FLAG_DOC_WAIVERS` (48 historical per-flag doc gaps)
  across 17 command docs.
- **#355** — Fixed `flag_scanner` AST walk that mis-attributed flags across
  sibling subparsers in `_register_*` helpers; `parser_vars` now scope per
  function body.

### Closeout Ceremony Integration

- **#351** — `gz closeout` pipeline consumes ceremony-recorded attestation
  instead of re-prompting; closes the GHI #292 OBPI-only surface gap at the
  ADR-closeout layer.
- **#354** — Split agent-emittable `audit-passed` receipt from operator-typed
  `validated` Gate-5 receipt; lifecycle requires both to advance an ADR to
  Validated.
- **#362** — Improved Step 2 Bill-of-Materials table column scaling; OBPI
  column sizes to longest slug, Objective column gets remaining width.
- **#363** — Closeout product-proof classifier expands glob entries in
  `## Allowed Paths` and recognizes `data/**/*.json` +
  `src/gzkit/schemas/**/*.json` as proof artifacts.

### Skill, Rule & Insights Surface

- **#356** — Rewrote `gz-adr-map` skill Step 2 to walk ADR → REQ → test
  (REQ-level `@covers` decorator pattern) instead of the obsolete ADR-level
  grep.
- **#357** — Added Behavior Rule binding the course-correction →
  `agent-insights.jsonl` loop; agents must append an `improvement` record
  before completing operator-corrected work.
- **#358** — Locked `agent-insights.jsonl` record schema with a Pydantic model
  and added `gz validate --insights-shape`.
- **#361** — Fixed Claude-rules path-frontmatter parser failure caused by a
  leading HTML comment; scoped rules correctly path-gate instead of
  always-loading (~26k tokens of context recovered).

### Infrastructure & Refactor

- **#343** — `gz git-sync` dry-run runs `git fetch --prune origin` before
  computing `ahead/behind`; closes the silent-stale-divergence failure mode.
- **#360** — Split `trust_audits.py` (2129 LOC, 14 rank-C functions) into
  `trust_audits/` package partitioned by audit family; every existing import
  site preserved via `__init__.py` re-exports.

### Stats

- 17 GHIs closed

## v0.25.18 (2026-04-27)

Session-start hygiene patch. Closes the "stale-clone vibe-cycle" failure class
where the SessionStart orientation hook reported every load-bearing surface
*except* git-remote divergence — agents on multi-machine clones edited canonical
surfaces from stale baselines until a downstream `gz git-sync` surfaced the
collision. Lands the operator-facing fix, the mechanical backstop preventing
its silent regression, two adjacent agent-surface defect closures (Claude Code
memory double-load, regressed attestation pointer), and the Opus 4.7 calibration
section on `CLAUDE.md` so per-turn effort defaults survive context boundaries.

### Session Orientation Integrity

- **#338** — `scripts/session_orientation.py` now surfaces git-remote-divergence
  state at session start. Multi-machine operators landing on a stale clone see
  the `ahead=N behind=M` count *before* editing canonical surfaces, instead of
  discovering the collision after a post-implementation `gz git-sync` failure
  has already burned cycles on directionally-opposed work. Closes the silent
  precondition behind the 2026-04-26 `templates/agents.md` collision (10
  commits behind origin, ~215 lines of in-place compression discarded by
  hard-reset recovery).
- **#341** — `gz validate --orientation-freshness` validator scope wired into
  the default `gz check` pipeline. Fail-closes (exit 3) if the SessionStart
  hook drops the `collect_remote_state()` call, the fetch step, or either
  vendor `settings.json` / `hooks.json` hook entry — defense-in-depth against
  silent regression of the #338 fix. Same shape as `gz validate
  --adr-status-fresh` (GHI #322) — Layer-3 fail-close on a load-bearing
  mechanical backstop.

### Agent Surface Hygiene

- **#339** — Moved `agents.local.md` from project root to `.gzkit/agents.local.md`
  to stop Claude Code's memory system from loading the file twice (once as a
  `*.local.md` local-override convention, once as the embedded
  `{local_content}` substitution inside the rendered `AGENTS.md`). Reclaims
  ~5.3k characters of per-turn context cost; the Claude Code "Large AGENTS.md
  will impact performance" warning at session start drops back below the 40k
  threshold.
- **#340** — Restored the `agent-contract-rationale.md#attestation--worked-example`
  pointer in `src/gzkit/templates/agents.md` § Attestation, after the GHI
  #327 diet pass dropped it. Re-greens the
  `tests/governance/test_attestation_fold.py::test_agents_md_has_attestation_section`
  fail-closed test that was blocking clean ARB receipts on `main`. Same class
  as #327's diet-pattern partial execution: lift pedagogy *and* leave the
  pointer line behind.

### Claude Tuning Surface

- **#283** — Added `## Opus 4.7 tuning` section to `CLAUDE.md` (mirrored to
  `.claude/`). Codifies effort-level defaults (`xhigh` for agentic work under
  gzkit; reserve `max` for genuinely hard problems per Anthropic's
  overthinking-warning), explicit per-turn thinking prompts ("Think carefully
  and step-by-step" vs "Prioritize responding quickly"), subagent fan-out
  criteria, and the recalibration note for prompts authored under 4.6's fixed
  thinking-token assumptions. Operator no longer has to remember the
  calibration per session.

### Stats

- 5 GHIs closed (4 defect, 1 chore).

## v0.25.17 (2026-04-26)

Governance-surface integrity patch. Closes the silent-regression vector
where `gz agent sync` stripped the CAP-13 orientation hook on every
invocation, lands a maintained regenerator for the ADR status index so
the Layer 3 view stops drifting against ledger truth, completes pass 1
of the AGENTS.md context diet, rewrites `ghi-triage` to render its
deliverable through a deterministic script, and authors the missing
`git-sync` skill the runtime command was advertising.

### Agent Surface Integrity

- **#329** — `gz agent sync control-surfaces` now preserves the
  `SessionStart` and `PreCompact` hook blocks in
  `.claude/settings.json` (and the Codex equivalent) instead of
  stripping them on every sync. The CAP-13 / GHI #326 mechanical
  backstop for AGENTS.md re-reading was one sync away from silent
  regression on every governance edit; the preservation rule is now
  enforced and round-trip stable.

### ADR Status Surface

- **#322** — `docs/governance/GovZero/adr-status.md` is now regenerated
  from filesystem + ledger truth by `gz register-adrs` and fail-closed
  by `gz validate --adr-status-fresh` (wired into `gz check`).
  Recovers the AGENTS.md § Architectural Boundaries item 6 invariant
  after a hand-maintained drift had silently desynced ~5 ADRs (titles
  and path layout) before discovery during the 2026-04-25
  complexity-doctrine session.

### Agent Contract Diet

- **#327** — Pass 1 of the AGENTS.md context diet: pedagogical
  narrative ("Why this is canon" codas, multi-paragraph rationale)
  lifted from the per-turn contract surface to `docs/governance/`,
  with binding bullets and one-line pointers retained. Per-turn
  surface trimmed from 632 to 474 rendered lines without relaxing a
  single binding invariant — the trim runs along the narrative axis
  only, per anti-vibing operative claim 2 ("lighter ceremony is not
  a tradeoff axis").

### Triage Skill Rewrite

- **#324** — `ghi-triage` rewritten v3 → v4. The script
  (`.claude/skills/ghi-triage/scripts/triage.py`) now renders the
  rank-ordered deliverable deterministically via `--format rank`;
  the agent contributes structured rank input (severity + ≤80 char
  action + ≤120 char why) validated at the rendering boundary.
  Removes the inline-Python heredoc rendering pattern, the
  Rich-only output contract that wrapped mid-glyph in chat surfaces,
  and the three redundant views (per-GHI panels, recommended-order
  table, rank list) that restated the same data. Cognitive freedom
  on the input edge; determinism on the render edge.

### CLI Fixes

- **#315** — Authored the missing canonical `git-sync` skill
  (`.gzkit/skills/git-sync/SKILL.md`) and mirrored it to vendor
  surfaces. Closes the control-surface integrity gap where
  `gz git-sync --skill` advertised a paired skill path that did not
  exist in the installed inventory, leaving agents without the
  workflow instructions the command claimed.

### Stats

- 5 GHIs closed

## v0.25.16 (2026-04-26)

Quality-of-life patch covering the OBPI pipeline's rough edges, the chores
registry's post-migration drift, ADR-report rollup correctness, and the
session-orientation gap that left handoffs as write-only artifacts. Adds
the SessionStart orientation hook (CAP-13), brings `gz-obpi-pipeline`
verification to ARB-lint parity, and pins parent-ADR § Decision as the
first Discovery Checklist read in OBPI briefs.

### OBPI Pipeline & Verification

- **#317** — `gz-obpi-pipeline` Stage 3 verification now invokes
  `uv run gz arb ruff` for lint instead of `uv run gz lint`, restoring
  parity with the canonical attestation contract. Previously the pipeline
  could report Stage 3 PASS while ARB lint receipts came back red.
- **#302** — `gz test --obpi` resolves `@covers`-tagged tests to dotted
  module paths before handing them to the unittest loader; the absolute-
  path leak that produced `FailedTest` errors and `AttributeError`
  diagnostics is closed.
- **#313** — `plan-audit-gate` hook self-resolves Claude Code auto-named
  plan files under `~/.claude/plans/` and matches OBPI short-form IDs
  (`OBPI-X.Y.Z-NN`) in addition to the canonicalized full slug. Heavy-lane
  OBPI plan runs no longer hit hard BLOCKED on first `ExitPlanMode`.
- **#321** — OBPI brief Discovery Checklist reordered so "Parent ADR §
  Decision — quote the line this OBPI implements" is item #1, followed
  by § Intent. Adds a STOP line below the checklist enforcing the read.

### Governance Status & Reporting

- **#279** — `gz adr create` and `gz adr report` canonicalize bare-ID vs.
  slugged-ID ledger events; the duplicate `adr_created` emission that
  produced shadow rows in the Foundation table (e.g. ADR-0.0.20 appearing
  twice) is rejected at write time and rolled up at read time.
- **#319** — Detailed governance status (`gz status --show-gates`,
  `gz state --blocked`) renders as full Rich tables for OBPI and artifact
  state instead of prose summaries or ellipsized IDs. Agents no longer
  need to synthesize ad-hoc Markdown tables from `--json` output.

### Chores Surface

- **#304** — `src/gzkit/chores/registry.json` `path` fields updated to the
  post-OBPI-0.0.21-01 layout (`src/gzkit/chores/<slug>/`). Previously
  pointed at the legacy `ops/chores/` locations, producing incoherent
  output in `gz chores show` and `gz chores plan`.

### Session Orientation (CAP-13)

- **#326** — SessionStart hook landed for both Claude Code
  (`.claude/settings.json`) and Codex CLI (`.codex/hooks.json`), wired
  to `scripts/session_orientation.py`. Aggregates seven sources on
  session entry: most-recent handoff (with Fresh/Slightly-Stale/Stale
  windowing), open `session-handoff`-labeled GHIs, active OBPI claims,
  in-progress ADR pipeline state, recent ledger events (last 24h), open
  blockers, and a post-compaction skill-awareness re-injection trigger.
  Closes the write-only-artifact failure class for handoffs.

### Stats

- 8 GHIs closed (all runtime-affecting; `runtime` label backfilled
  during this release's discovery sweep)
- New session-orientation surface: `scripts/session_orientation.py`
  + SessionStart hook configs for Claude Code and Codex
- New CLI hook flags: `gz plan audit --plan-file`, `--save`
- ADR-report duplicate-row regression closed (Defect 1+2 from #279)

## v0.25.15 (2026-04-23)

Closes the OBPI human-attestation authenticity gap and restores agent+operator
co-presence ergonomics. Two fixes work together: a fail-closed gate that refuses
agent-synthesized attestation, plus an explicit escape path so an agent can
relay an operator's already-given attestation without bouncing the operator out
of the conversation to type the command themselves.

### Governance / Authenticity

- **#290** — Closed the agent-fabrication vector in `gz obpi complete`,
  `gz obpi emit-receipt`, and `gz adr emit-receipt`. The CLI now refuses to
  emit a `human_attestation: true` receipt from a non-TTY parent process,
  preventing programmatic synthesis of operator attestations
  (`_enforce_human_attestation_authenticity` at `src/gzkit/commands/adr_audit.py:283`).
- **#292** — Restored agent+operator co-presence ergonomics with the new
  `--attestor-present` flag. When an active pipeline marker exists at
  `.claude/plans/.pipeline-active-{OBPI-ID}.json`, the agent can relay the
  operator's Stage-4 attestation through a non-TTY subprocess. The ledger
  records `attestation_type: "agent-relayed-operator-attestation"` —
  taxonomically distinct from TTY-typed `human_attestation: true` so audits
  count the two streams separately.

### Stats

- 2 GHIs closed (both runtime-affecting; `diff_only` qualification)
- 1 src/gzkit/ module touched: `adr_audit.py`
- New CLI flag: `--attestor-present`
- New ledger taxonomy: `agent-relayed-operator-attestation`

## v0.25.14 (2026-04-22)

Post-4.7 surface-hardening patch: 25 GHIs closed across the validation layer,
closeout ceremony, OBPI pipeline gates, ADR promotion, chores, agent rules,
and the patch-release discovery regex itself. This is the first release
whose GHI manifest reflects the project's canonical `fix(scope): ... (GHI #N)`
closure convention (GHI #280).

### Patch Release Ceremony

- **#280** — `gz patch release` closure regex now recognizes the project's
  canonical `fix(<scope>): <summary> (GHI #N)` and `feat(<scope>): …
  (GHI #N)` subject form alongside GitHub-canonical `Closes #N` trailers.
  Previously treated as citation-only; discovery at v0.25.13 reported 0
  GHIs despite 29 in-range closures. Multi-GHI tails `(GHI #N, #M)`
  supported; non-code cc-prefixes (`docs`, `chore`, `ceremony`, `audit`)
  still excluded to preserve GHI #233 anti-double-count doctrine.

### Validation Surface

- **#238** — `gz validate --brief-headings` scope added; OBPI brief
  evidence sections must use H3 (`### Implementation Summary`, etc.), and
  H3 drift is a policy breach (exit 3).
- **#275** — `gz validate --utf8-prefix` extended to fresh-interpreter
  helpers and non-Python pipeline tools (the runtime UTF-8 guard covers
  only `uv run gz …`; `python -c`, `tools/*.py`, and `jq`/`awk` pipes
  need explicit handling).
- **#276** — `gz validate --behave-req-tags` direction reversed to
  OBPI→feature, so heavy OBPIs that ship zero scenario coverage surface
  (the original feature→feature direction could only flag a feature file
  that forgot to tag an existing scenario).
- **#279** — `gz adr create` and `gz adr report` canonicalize bare-ID
  vs. slugged-ID ledger events; duplicate `adr_created` emission rejected.

### Closeout Ceremony

- **#249** — Residual Heavy/Foundation bucketing eliminated from
  `docs/governance/` surfaces (runbook + GovZero runtime-contract docs);
  ceremony doctrine now uses lane (Lite/Heavy) and kind (pool/foundation/
  feature) as orthogonal axes.
- **#250** — Attestation prompt aligned with skill Step 5 proactive
  contract (no more CLI "I await your decision" vs. skill-direction
  ambiguity).
- **#259** — Step 2 renders ADR intent and OBPI delivery side-by-side
  instead of only listing OBPIs.
- **#260** — Step 5 walkthrough paced one `--next` at a time per operator
  decision; speedrun-all-demos anti-pattern fixed.
- **#262** — Closeout ceremony skill pinned to Opus (previously ran on
  whichever model defaulted); extended to companion Gate-5 skills.
- **#265** — `product_proof` checker gained `concepts_page` proof type;
  Foundation-doctrine ADRs no longer always trip the closeout blocker.
- **#266** — Nonexistent `gz adr reconcile` verb removed from
  `gz-adr-closeout-ceremony` skill.

### OBPI Pipeline

- **#267** — `gz obpi complete` now fail-closed on empty
  `### Implementation Summary` / `### Key Proof` sections; pipeline Stage 5
  requires prose walkthrough before completion.

### ADR Lifecycle

- **#241** — `gz adr promote` honors the `## Proposed OBPI Decomposition`
  table and ignores nested bullets in other Target Scope sections.
- **#258** — OBPI-0.0.18-01 corrected to cite a non-0.0.x ADR as the
  feature-kind example (0.0.x is foundation, not feature).

### Chores

- **#269** — `fileExists` criterion wired end-to-end; the parser now
  populates the `expected` path the criterion type declares.

### Agent Contract & Rules

- **#261, #263** — Craftsmanship invariants 6g (verify runtime surface
  before recommending an incantation) and 6h (quote the rule and
  conflicting directive verbatim when reporting a violation) added to
  `.gzkit/rules/agent-contract.md` to prevent reporting-pathway drift.
- **#270** — `tests.md` "assert semantics, not strings" reconciled with
  `tool-skill-runbook-alignment.md` Invariant 3 via explicit
  unit/fixture separation — string-shape assertions live in Invariant-3
  fixtures; REQ-derived unit tests assert semantics.
- **#271** — `gz-plan` and `gz-design` Step 1 now cite
  `defect-fix-routing.md` thresholds.
- **#272** — `gz-adr-audit` Step 2 remediation disambiguated: genuine
  coverage gap → author a REQ-derived test; cosmetic @covers backfill
  is the anti-pattern.
- **#273** — `gz-adr-closeout-ceremony` Evidence Summary uses the
  canonical ARB invocations table.
- **#274** — `reconcile-freshness` bootstrap carve-out named in the
  CLAUDE.md Architectural Boundaries rule (zero-event history is bootstrap,
  not drift).

### Hooks & Sync

- **#239** — `PostToolUse` `ruff check --no-fix` hook backstops the
  import-colocation rule (unused imports removed by the fix-mode hook
  are now surfaced instead of silently deleted).
- **#247** — `sync_copilot_instructions` regenerates copilot-instructions.md
  when canonical rules exist; template edits now propagate.

### Stats

- 25 GHIs closed (16 src-touching, 8 doc/rules-only, 1 patch-release fix)
- 0 Foundation ADR closeouts (this release ships post-4.7 surface
  hardening only)
- 116 GHIs booked since 2026-04-16 (post-4.7 audit window); 161 booked
  prior — this release discharges the first meaningful patch of the
  backlog through the now-working discovery path.

## v0.25.13 (2026-04-20)

Foundation ADR completion and test-suite rehabilitation: ADR-0.0.17
(adr-taxonomy-mechanical) closed out, BDD suite restored from 32 failing
scenarios to 129/129 passing in 6s, unittest runtime trimmed, complexity
regression in plan_cmd cleared, email PII scrubbed across briefs/ledger.

### Foundation & Governance

- **ADR-0.0.17** — adr-taxonomy-mechanical closeout completed; mechanical
  side of the taxonomy split (Foundation / Pool / Feature) now landed.
- **ADR-0.0.19** — pre-execution reasoning walkthrough booked (#232).
- **#242** — ADR-0.0.17/0.0.18 OBPIs implemented after v0.25.12 re-pause.
- **ADR promotions**: preflight → 0.42.0, ghi-triage → 0.43.0.

### Test Suite

- **#252** — BDD suite restored: 32/129 failing and >4 min runtime
  → 129/129 passing in 6.0s. Switched behave setup to `_quick_init`
  (~60× speedup) and scaffolded agent surfaces for scenarios that assert
  on `gz init` output.
- **#253** — Unittest runtime cut via template/scanner caching, hoisting
  repeated `gz init` calls to module scope, reducing `_init_git_repo`
  from 6 → 3 subprocesses, and caching `check_sync_parity` expected
  surfaces.
- **#251** — Closeout-proof BDD fixture fixed (missing `--kind feature`
  after OBPI-0.0.17-02).

### Code Quality

- **#255** — `plan_cmd` xenon complexity reduced from rank D (27) to
  within the C-rank ceiling.

### Privacy

- Email address scrubbed from briefs and ledger.
- PII/email rule added to AGENTS.md local agent rules.

### Documentation

- `gz plan` parent-verb manpage added.

### Stats

- 5 GHIs closed (#242, #251, #252, #253, #255)
- 1 Foundation ADR completed (ADR-0.0.17)
- 1 Foundation ADR booked (ADR-0.0.19)

## v0.25.12 (2026-04-19)

Ledger canonicalization fix: ADR parent refs are now resolved to full
semver+slug form at every write/read boundary, closing a cross-surface
drift between `gz register-adrs`, `gz plan create`, and the validator.

### Governance Fixes

- **#222** — Canonicalized ADR parent refs on write and read. Three surfaces
  (register, plan, validator) now collapse short-form parent pointers to the
  ledger's long-form id, so authoring `parent: ADR-0.0.17` no longer drifts
  from the stored `ADR-0.0.17-adr-taxonomy-mechanical` id and
  `gz validate --frontmatter` stops oscillating.

### Stats

- 1 GHI closed (src-touching)

## v0.25.11 (2026-04-18)

**Release ceremony unblocked and correctness-anchored: patch-release discovery now anchors to the
commit range (doctrine: "count what we CLOSE, not what we book"); the version-release audit accepts
in-flight manifests so `gz patch release --full` can ship itself; plan-audit cross-references sibling
ADRs for scope collisions; audit-check recognizes BDD and doc-proof channels; per-increment TDD
rhythm codified with named anti-patterns. 6 GHIs closed.**

### Fixed

- **#233 — Patch-release discovery anchored to commit range, not close-time window.** `gz patch
  release --dry-run` had reported 30 qualifying GHIs for v0.25.11 against 6 real closures — a 5×
  over-count driven by (1) a `YYYY-MM-DD` truncation of the tag timestamp in the `gh issue
  list --search` predicate, so GHIs closed hours BEFORE the tag on the same calendar day re-matched,
  and (2) a `git log --all` cross-validation that couldn't distinguish "shipped this release" from
  "shipped three tags ago." Replaced both with a `git log <base_ref>..HEAD` walk parsing
  GitHub-canonical closure keywords (`Closes|Fixes|Resolves #N`, case-insensitive, ±s/d suffixes).
  The project's `(GHI #N)` paren form in commit subjects is a citation convention, not a closure
  declaration — design and ceremony commits cite prior GHIs for context without closing them — and
  no longer inflates the release ledger. Upstream GHI state is not consulted: a locally-committed
  `Closes #N` ships the GHI by definition; `gh issue close` fires on push. Surfaced by operator
  during the v0.25.11 ceremony; doctrine: *"we only count what we CLOSE, not what we book."*
- **#217 — `audit_version_release` accepts an in-flight release manifest as equivalent to a tag.**
  The GHI #205 naked-bump guard was fail-closing against the very `release: vX.Y.Z` commit that
  `gz patch release --full` authored, because tags are created by `gh release create` AFTER the
  bump commit lands. The audit now passes when either a matching `vX.Y.Z` tag exists OR
  `docs/releases/PATCH-vX.Y.Z.md` has been written — proof that `gz patch release` is mid-ceremony.
  Naked-bump detection retained: a pyproject bump with no manifest and no tag still fails closed.
- **#166 — `gz adr report` orphan check parses frontmatter `id:` instead of relying on file-stem
  parity.** ADR-0.41.0 (stem `ADR-0.41.0-tdd-emission-and-graph-rot-remediation`) was reported as
  unregistered despite 15 ledger events for its canonical id. Fix mirrors the dual-lookup pattern
  already in `register.py:150-169`: canonical candidates include both `parsed_id` and `stem_id`.
- **#165 — `gz adr audit-check` recognizes three proof channels beyond `@covers` decorators.**
  Previously non-code REQs had to either tag `[doc]` (skipped entirely) or bolt a spurious `@covers`
  onto an unrelated `.py` file — as happened for REQ-0.25.0-33-05 where a behavioral proof got a
  fake decorator on `tests/commands/test_arb_cmd.py`. Now: BDD `@REQ-X.Y.Z-NN-MM` scenario tags in
  `features/**/*.feature` count as coverage for code REQs; `_synthesize_doc_proof_linkage` walks
  every DOC-kind REQ and attributes coverage to decision-doc text, command docs, governance
  artifacts, runbook entries, release manifests, or BDD features through the real evidence channel.
  `[doc]` REQs are now surfaced in the coverage report and must be proven — the "look-differently,
  not don't-look" contract.
- **#152 — `gz plan audit` detects scope collisions across sibling ADRs.** OBPI-0.25.0-33 and 9
  OBPI-0.27.0 briefs all claimed `src/gzkit/arb/` files; both receipts returned PASS and the
  collision was structurally invisible until operator cross-reference at Stage 4. New
  `_scan_sibling_adr_collisions` walks sibling ADR packages, computes allowed-paths overlap with
  directory-prefix semantics (so `src/gzkit/a` doesn't spuriously match `src/gzkit/arb`), and
  surfaces results as an advisory `DRIFTED — scope-collision` block in the receipt. Advisory only;
  the receipt still PASSes on collision. Repaired `_extract_allowed_paths` in the same patch:
  252 of 454 real briefs use `## ALLOWED PATHS` (UPPERCASE) or `## ALLOWED PATHS (Foundational)` —
  the old case-sensitive match missed them entirely, which would have given the new scanner nothing
  to work against.

### Governance

- **#157 — Per-increment TDD rhythm codified; test-dump theater and stop-and-ask named as distinct
  anti-patterns.** `.gzkit/rules/tests.md` gains a binding "per-increment rhythm" section:
  one test → observed RED → minimum code to GREEN → next increment, flowing until a logical
  checkpoint. `.gzkit/rules/attestation-enrichment.md` clarifies that ARB encodes `exit_status=1`
  as a defect while a TDD RED test is *correct* first-run behavior — so Gate 2 TDD claims cite ARB
  only for the GREEN side; fabricating `exit_status=1` ARB receipts as "RED receipts" is the same
  post-hoc-false class as the `ty check .` drift GHI #199 closed. The DO IT RIGHT anti-pattern
  canon in `src/gzkit/templates/agents.md` gains entries for batch-RED/GREEN screenshot theater
  and stop-and-ask between increments, both citing GHI #157. Tool half (dedicated RED/GREEN
  receipt stream, new `gz tdd` CLI verb group) parked in `ADR-pool.tdd-receipt-stream` behind the
  committed feature-ADR backlog.

### Stats

- 6 GHIs closed (#152, #157, #165, #166, #217, #233)
- 3186 tests total; 9 new tests for GHI #233 (closure-keyword semantics, range anchoring); 4
  pre-existing `TestPlanAuditGateHook` Windows subprocess failures from GHI #223 unchanged
- First-party ceremony integrity: `gz patch release` discovery logic is now correctly anchored to
  its own commit range, verified against the v0.25.10→v0.25.11 window (6 closures, zero duplicates)

## v0.25.10 (2026-04-18)

**Constitution scaffolder/validator parity, advisory-rules promotion wave,
Stage 5 pre-flight, plan-audit hardening, and seven chained hook/validator
fixes (GHI #187–#216).**

### Fixed

- **#216 — Constitution schema registered; scaffolder emits validator-compatible
  ids** (GZKIT-BOOTSTRAP-008) — `gz validate --documents` was erroring
  `Unknown schema: constitution` on every file under `design/constitutions/`
  because no `gzkit.constitution.v1` schema shipped, and `gz constitute`
  emitted raw kebab-case ids with no `semver` field. Same class as GHI #186
  (PRD), one layer up. New `src/gzkit/schemas/constitution.json` with id
  pattern `^CONSTITUTION-[A-Z0-9]+-\d+\.\d+\.\d+$`; `ConstitutionFrontmatter`
  Pydantic model; `_canonicalize_constitution_id()` helper mirrors the GHI
  #186 PRD shape (`rhea-kernel` → `CONSTITUTION-RHEAKERNEL-1.0.0`).
  Round-trip test locks the scaffolder→validator contract. Reported by RHEA
  adopter.
- **#194 — OBPI validator verifies brief-prescribed `gz` commands against the
  CLI parser** — briefs can no longer ship Verification / Requirements /
  Acceptance / Evidence sections containing CLI commands that do not resolve
  against the live parser. Catches singular-vs-plural drift (`gz chore run`
  vs `gz chores run`) and hallucinated flags at authoring time instead of
  pipeline runtime.
- **#192 — Validator skips pool ADRs in `validate_frontmatter`** — `gz
  validate --frontmatter` now honors the `_is_pool_artifact` contract the
  chore library already implemented, so 56 pool-ADR false positives no
  longer green-wash live backfill progress.
- **#191 — Plan-audit-gate self-runs `gz plan audit` on stale receipts** —
  removes the ExitPlanMode deadlock where the gate demanded a receipt the
  operator could not produce without leaving plan mode. Bounded 60s
  subprocess; overridable via `GZKIT_PLAN_AUDIT_CMD`.
- **#189 — Validator recovery hint uses plural `gz chores run`** —
  `_RECOVERY_COMMANDS["status"]` and two fallback defaults corrected from
  the non-existent singular verb. New `TestRecoveryCommandsResolveToCli`
  mechanically asserts every recovery command resolves against `gz --help`.
- **#188 — Plan-audit gate accepts canonical-slug receipts** — 5th patch in
  the CLI-vs-hook receipt-resolution chain. Hook now globs both short-form
  and canonical-slug receipt filenames and compares `obpi_id` by short form
  so mixed-form plan+receipt pairs resolve to the same identity.
- **#187 — `gz plan audit` canonicalizes `obpi_id` before writing the
  receipt** — 7th instance of the short-form-vs-full-slug defect class
  (#41/#60/#61/#79/#108/#114). Fix shape matches GHI #114's `resolve_obpi`
  repair: canonicalize through `Ledger.canonicalize_id` + prefix expansion
  before any downstream lookup or write.

### Added

- **#196 — `gz obpi precomplete`: Stage 5 mechanical pre-flight** — new CLI
  verb runs five checks before `gz obpi complete` (brief readiness,
  reconcile idempotence, lock held, ARB receipts present, plan-audit
  receipt valid) with named remediation per failure. Exit 0 = ready;
  exit 3 = blocker. Wired into `gz-obpi-pipeline` skill as mandatory Stage 5
  Step 0. Closes the reactive-triage class of failure.
- **#195 — Defect-fix routing rule with explicit direct-fix vs ceremony
  thresholds** — `.gzkit/rules/defect-fix-routing.md` documents mechanical
  criteria (≤10 source lines or ≤2 files, in-flight trigger, prior
  `fix(…)` precedent in the last 20 commits, unit-testable) for routing a
  defect to a direct commit rather than a full OBPI ceremony. Closes the
  class of ceremony over-application surfaced during OBPI-0.0.16-04
  dogfooding.
- **#190 — `gz-obpi-specify` pre-save ground-truth check** — skill now
  prompts authors to verify file paths, config keys, and CLI commands exist
  before saving the brief. Closes the "LLM priors from adjacent projects"
  class of brief fabrication surfaced by OBPI-0.0.16-03.

### Governance

- **Advisory → mechanical promotion wave: 10 new `gz validate` scopes + 2
  pre-commit hook guards** (#202–#215) — the largest agent-discipline →
  fail-closed conversion since launch. Scorecard: Mechanical 12 → 33
  (30% → 59%); Promotable 14 → 5.

  New `gz validate` scopes:
  - `--skill-alignment` (#202, Invariant 1): every CLI verb has a wielding
    skill.
  - `--pydantic-models` (#203): `@dataclass` flagged outside waivers;
    `BaseModel` requires `ConfigDict`.
  - `--class-size` (#204): classes >300 lines require explicit waiver
    rationale.
  - `--version-release` (#205): `pyproject.toml` version must have a
    matching `vX.Y.Z` tag.
  - `--utf8-prefix` (#206): regex scan forbids `PYTHONUTF8=1 uv run gz`.
  - `--pool-adr-isolation` (#208): ledger scan for pool ADRs receiving
    gate/attestation/lifecycle events.
  - `--test-tiers` (#209): forbids `tests/integration|e2e|slow|bdd` dirs
    and `--integration / --e2e / --slow / --bdd-only` flags.
  - `--behave-req-tags` (#211): feature-level `# @covers REQ-*` comments
    require matching scenario-level `@REQ-X.Y.Z-NN-MM` tags.
  - `--advisory-scorecard` (#212, meta): every `.gzkit/rules/*.md` must
    appear in `docs/governance/advisory-rules-audit.md`.
  - `--reconcile-freshness` (#213): latest reconcile event within 24h of
    HEAD (no-op until reconcile events standardize).

  New pre-commit hook guards:
  - `forbid_manual_ledger_edits` (#207): staged `ledger.jsonl` must be
    strict append; deletion hunks fail closed.
  - `forbid_skill_sync_drift` (#210): `.gzkit/skills|rules` edits without
    their `.claude/` + `.github/` mirrors in the same commit fail closed.

  Also: L3 derived-view inventory under
  `docs/governance/layer-three-derived-views.md` (#214); agent surfaces
  updated with a Governance Doctrine Surfaces section pointing at
  trust-doctrine + advisory scorecard (#215).

### Stats

- 1 adopter-reported quickstart defect closed (GZKIT-BOOTSTRAP-008 → #216)
- 6 additional fixes across hooks, validators, and the plan-audit chain
- 3 new features (precomplete CLI verb, defect-fix routing rule, ground-truth skill guidance)
- 14 advisory rules promoted to mechanical enforcement
- Full suite: 3155 tests, all green

---

## v0.25.9 (2026-04-17)

**PRD scaffolder fix, CLI startup perf, and test tier doctrine (GHI #180, #181, #182, #186).**

### Fixed

- **PRD scaffolder emits validator-compatible ids** (GHI #186) — `gz prd <slug>`
  now writes `PRD-<SLUG>-X.Y.Z` ids that match the validator's
  `^PRD-[A-Z0-9]+-\d+\.\d+\.\d+$` schema. Previously the scaffolder emitted
  kebab-case `PRD-<slug>` while the validator (same binary, same version)
  required uppercase-alphanumeric + semver, so every freshly scaffolded PRD
  failed validation until hand-edited. Blocked the documented quickstart at
  step 2; reported by Rhea adopter (GZKIT-BOOTSTRAP-007).
- **`gz --help` startup budget restored to < 1.0s** (GHI #180) — lazy-loaded
  CLI command handlers and `gzkit.cli` re-exports via PEP 562 `__getattr__`.
  Eagerly imported `jsonschema`, `pydantic`, `structlog`, and `rich.console`
  no longer pull into the `--help` hot path. Wall-clock dropped from 2.4-3.7s
  back under the 1.0s policy ceiling enforced by `test_help_renders_fast`.

### Changed

- **Two-runner test doctrine: `unittest` + `behave`** (GHI #181, #182) —
  the short-lived `tests/integration/` tier introduced in #181 (90s → 30s
  symptom patch) is collapsed. Per-test triage moved genuinely end-to-end
  scenarios into `features/` and refactored the rest under `tests/commands/`
  using the canonical subprocess patchers (`_git_subprocess_patcher`,
  `_uv_sync_patcher`, `_quick_init`). `gz test --integration` and the
  `load_tests` gating protocol are removed. The runner boundary
  (`unittest` for mocked Python behavior, `behave` for real CLI flows) is
  now the only test tier gate. Triage decisions recorded in
  `artifacts/audits/ghi-182-triage.md`.

### Stats

- 4 GHIs closed (1 high-severity defect, 3 perf/doctrine)

---

## v0.25.8 (2026-04-16)

**Two fixes from Rhea adopter feedback and dogfood (GHI #178, #179).**

### Fixed

- **Patch release discovery includes same-day GHI closes** (GHI #178) —
  changed `closed:>` to `closed:>=` in the GitHub search query so GHIs
  closed on the same calendar day as the latest tag are included in
  discovery. Cross-validation already filters false positives.
- **Repair mode delivers new skills from upgraded gzkit versions** (GHI #179) —
  `gz init` repair mode now diffs installed skills against `CORE_SKILLS` and
  scaffolds any missing ones without overwriting existing user-modified skills.
  Projects initialized on older gzkit versions pick up newly added core
  skills on re-run.

---

## v0.25.7 (2026-04-16)

**`gz patch release --full` executes the complete release ceremony end-to-end (GHI #177).**

### Added

- **`--full` flag on `gz patch release`** — one command runs the entire
  ceremony: discover GHIs, bump version, author RELEASE_NOTES.md entry,
  commit (with lint/test gates), push, `gh release create`, and post-release
  verification. Pauses for operator confirmation before commit/push/release.
- **Auto-generated release notes** — `--full` categorizes qualifying GHIs by
  label (Fixed/Added/Changed) and prepends a structured entry to
  RELEASE_NOTES.md.
- **Post-release verification** — checks version consistency across
  pyproject.toml, `__init__.py`, and README badge; confirms tag exists and
  working tree is clean.
- **GitHub issue templates** — `.github/ISSUE_TEMPLATE/` with defect,
  enhancement, and observation templates for adopter feedback.

### Changed

- Runbook Loop C updated to recommend `gz patch release --full` as the
  primary release path, with step-by-step as fallback.

---

## v0.25.6 (2026-04-16)

**Skill discoverability, adopter onboarding, and standard docs parity (GHI #173, #174, #175, #176).**

### Changed

- **`gz init` now scaffolds 15 core skills** (was 5). Added the governance
  workflow sequence: `gz-prd`, `gz-plan`, `gz-status`, `gz-gates`,
  `gz-constitute`, `gz-implement`, `gz-obpi-pipeline`,
  `gz-adr-closeout-ceremony`. Init completion message shows Skill/CLI
  comparison table instead of bare CLI commands.
- **Runbook restructured** — Loop A uses Skill/CLI comparison tables instead
  of burying skills in bash comments. Adopter Feedback section links to
  GitHub issue templates.
- **Tutorials surface skills** — first-project and RHEA bootstrap tutorials
  replace "(coming soon)" blocks with Skill/CLI tables at every governance
  step.
- **Quickstart adds output tree and friction points** — shows directory
  structure after `gz init`, common sharp edges table with fixes.

### Added

- **GitHub issue templates** for adopter feedback: defect reports, enhancement
  requests, and observations (`.github/ISSUE_TEMPLATE/`).
- **Decomposition scorecard worked example** in `plan-create` manpage with
  concrete dimension scores and task count derivation.
- **Lane selection decision guide** in concepts — scenario-based table for
  choosing Lite vs Heavy.
- **Implementation order guidance** in first-project tutorial — dependency
  chain analysis before coding.
- **Init manpage result tree** — shows full directory structure after
  initialization.

---

## v0.25.5 (2026-04-16)

**GHI #172: `gz init --force` no longer destroys user hooks in settings.json.**

### Fixed

- **`setup_claude_hooks` now merges into existing `.claude/settings.json`**
  instead of overwriting it. gzkit-owned hooks (identified by `.claude/hooks/`
  command paths) are replaced with fresh versions; user-added hooks and
  top-level settings keys are preserved. Applies to `gz init`, `gz init
  --force`, repair mode, and `gz agent sync control-surfaces`.
- `.gitignore` template updated to use
  [github/gitignore](https://github.com/github/gitignore) canonical Python
  template as reference.

---

## v0.25.4 (2026-04-16)

**`gz init` scaffolds .gitignore; test suite performance fix.**

### Fixed

- **`gz init` now creates a Python-oriented `.gitignore`** — excludes
  `.venv/`, `__pycache__/`, `.claude/settings.local.json`, and OS artifacts.
  Idempotent: preserves any existing `.gitignore`. Works with `--no-skeleton`
  (`.gitignore` is project infrastructure, not skeleton). Repair mode
  re-creates it if missing. 4 tests added.
- **`test_tasks.py` setUp optimization** — expensive `gz init` + `gz plan
  create` moved from per-test `setUp` to per-class `setUpClass` with ledger
  reset per test. 25s -> 6.5s for 81 tests.
- **`test_validate_sync_parity.py` init caching** — single cached `gz init`
  copied via `shutil.copytree` instead of 5 separate init calls. 4.7s -> 2.2s.
- **`gz validate --version`** checks that pyproject.toml, `__init__.py`,
  and README badge versions all agree. Runs automatically as part of
  `gz validate` (no flags). 5 tests added.

---

## v0.25.3 (2026-04-16)

**Skills as first-class control surfaces in documentation.**

First non-dogfooded use of gzkit (RHEA project) revealed that documentation
treated skills as optional shortcuts in comments, not as co-equal operator
surfaces. Skills carry governance logic (interviews, forcing functions,
semantic authoring, pipeline orchestration) that raw CLI commands skip — they
should be the recommended path in Claude Code sessions.

### Changed

- **Quickstart** now shows both CLI and skill invocations side-by-side for
  every step, with notes on what governance logic each skill adds
- **User index** adds a "Two Operator Surfaces" section and a CLI/skill
  comparison table in the operational contract
- **PRD Guide** adds "Creating a PRD in gzkit" section with CLI and skill
  paths, and a lifecycle table in "From PRD to Action"
- **ADR Guide** adds "Creating an ADR in gzkit" section recommending
  `/gz-plan` for its design forcing functions, plus `/gz-design` for
  pre-ADR exploration
- **Task Guide** adds "Creating and Executing Tasks in gzkit" table mapping
  the full task lifecycle to CLI commands and skills
- **Daily Workflow** concept page elevates skills from "wrapper" language to
  co-equal surface with explicit CLI vs Skill comparison table
- **mkdocs.yml** expands skill navigation from 6 entries to 30, organized
  by lifecycle phase (Project Setup, Planning, Execution, Status & Review,
  Closeout & Audit, Operations)
- **User index** "Start Here" section now links to the skills reference

### Added

- **`gz validate --version`** checks that pyproject.toml, `__init__.py`,
  and README badge versions all agree. Runs automatically as part of
  `gz validate` (no flags) so existing quality gates catch version drift
  before it ships. 5 tests added.

---

## v0.25.2 (2026-04-16)

**GHI:** #171 — gz init does not scaffold Python project skeleton

First non-dogfooded use of gzkit (RHEA project) revealed that `gz init`
scaffolded governance infrastructure but left the project without a runnable
Python skeleton.

### Fixed

- **`gz init` now creates a Python project skeleton** — `pyproject.toml`
  (Python >=3.13, hatchling, ruff config), `src/<project>/__init__.py`, and
  `tests/__init__.py` are created alongside governance scaffolding
- **`gz init` runs `uv sync`** to hydrate the virtualenv after creating
  `pyproject.toml` — project is immediately runnable, not just scaffolded
- **Re-running `gz init` enters repair mode** — detects and creates missing
  artifacts (skeleton files, governance dirs, manifest, virtualenv) without
  overwriting existing files; no `--force` required
- **`--no-skeleton` flag** — opt out of project skeleton creation for
  governance-only init on projects with existing build setups

### Changed

- `gz init` on an already-initialized project no longer errors; it repairs
- `uv sync` only runs when `.venv` does not yet exist (idempotent)
- Parser description and epilog updated to reflect new behavior
- `gz-init` skill updated with repair workflow documentation

### Tests

- 19 tests covering skeleton creation, idempotent repair, partial skeleton
  fill, package name normalization, and `--no-skeleton` opt-out

## v0.25.0 (2026-04-15)

**ADR:** ADR-0.25.0 — Core Infrastructure Pattern Absorption

Systematic evaluation of 33 infrastructure patterns from the airlineops companion
codebase. Each pattern received an individual OBPI with a documented
Absorb/Confirm/Exclude decision and rationale.

### Delivered

- **3 Absorb decisions** — drift detection, policy guards, and ARB analysis
  patterns ported into gzkit with full test coverage
- **14 Confirm decisions** — gzkit's existing implementations (attestation,
  progress, config, console, ADR lifecycle/audit/governance/reconciliation/
  traceability, CLI audit, docs validation, validation receipts, handoff
  validation) confirmed as architecturally superior with documented rationale
- **16 Exclude decisions** — domain-specific airlineops patterns (signatures,
  world state, dataset versioning, registry, types, ledger, schemas, errors,
  hooks, admission, QC, OS, manifests, artifact management, layout verification,
  ledger schema, references) excluded with documented rationale
- **`gz arb` command group** — 7 subcommands for receipt-based QA evidence
  (ruff, step, ty, coverage, validate, advise, patterns)

### Governance Rot Remediation (GHI-160)

Comprehensive 7-phase remedy program completed during this release cycle:
- Phase 1: Audit — 29 ADRs with zero REQs identified
- Phase 3: REQ-ID backfill across 260 OBPI briefs
- Phase 4: Retroactive `@covers` for orphan ceremony tests
- Phase 5: ADR-0.41.0 TDD RED/GREEN emission design (pool, RHEA migration target)
- Phase 6: `gz validate --requirements` and `--commit-trailers` enforcement
- Phase 7: Retroactive TASK backfill for GHI-153/155/156

### Infrastructure

- `decision_doc` proof type added to product proof gate (GHI-163)
- 2 new chores registered: `hex-port-enforcement`, `adr-frontmatter-drift`
- GHI #162 filed for ADR frontmatter ↔ ledger drift (94.7% stale rate)

### Gate Evidence

All 5 GovZero gates satisfied. 33/33 OBPIs attested. 2990 tests passing.

## v0.24.3 (2026-04-08)

Version sync release — first dogfood invocation of `gz patch release`
(ADR-0.0.15, OBPI-0.0.15-06).

### Version Drift Fix

- Resolved `__init__.py` drift: was 0.24.1, now synced to 0.24.3 via
  `sync_project_version`
- All version locations (pyproject.toml, `__init__.py`, README badge) now agree

### Governance

- First end-to-end run of the GHI-driven patch release ceremony
- Patch manifest: `docs/releases/PATCH-v0.24.3.md`
- 5 GHIs discovered since v0.24.2, all excluded (governance-only, no runtime changes)

### Stats

- 5 GHIs closed (#109, #110, #111, #112, #115)
- 0 qualifying runtime GHIs (all governance/defect work)

## v0.24.2 (2026-04-05)

Patch release closing 50 GHIs across 69 commits. Covers defect fixes, hook
hardening, skill consolidation, test infrastructure improvements, and OBPI
identity normalization.

### Windows / Cross-Platform

- **#103** — Fixed 17 `.exists()` vs `.is_file()` PermissionError bugs across commands/ on Windows

### Closeout Ceremony Overhaul (#99-104)

- **#99** — Step 2 template no longer subsumes Steps 3-6 with premature attestation
- **#100** — Added missing value justification step
- **#101** — Removed phantom Step 4 (unused docs alignment checklist)
- **#102** — Added Foundation ADR (0.0.x) release skip gate
- **#104** — Ceremony now driven by CLI state machine, not prose steps

### OBPI ID Normalization (#60, #61, #79, #108)

- **#60** — `register-adrs` no longer silently skips OBPIs with short-form parent IDs
- **#61** — `gz-design` emits slugified parent IDs in OBPI brief frontmatter
- **#79** — Resolved short/long ID mismatch between obpi-completion-validator and `gz obpi audit`
- **#108** — Added validation guard: OBPI frontmatter `id` must match slugified filename stem

### Hook and Gate Hardening (A-series #92-96)

- **#92** — `pipeline-gate.py` path scope expanded beyond `src/` and `tests/`
- **#93** — Added NO-GO verdict check to `plan-audit-gate.py`
- **#94** — Added `--force` reason quality bar to `gz attest`
- **#95** — `pipeline-completion-reminder.py` now blocking for incomplete pipelines
- **#96** — Added interview artifact existence check to `gz validate`

### Pipeline Fixes (#17, #20, #23, #36)

- **#17** — CLI is now a proper pipeline, not just a stage launcher
- **#20** — Fixed single-file receipt conflicts and added marker expiry
- **#23** — Fixed dirty worktree cascade from `gz obpi emit-receipt` on multi-OBPI ADRs
- **#36** — Receipt emission now occurs after git-sync captures worktree anchor

### CLI and Command Fixes

- **#62** — `cli audit` resolves `adr report` and `closeout` handler docstrings
- **#63** — `flags` and `flag explain` added to governance runbook
- **#64** — Removed orphan test with `@covers REQ-0.22.0-04-09` referencing absent requirement
- **#66** — `gz obpi validate` no longer fails changed-files audit on clean tree for completed OBPIs
- **#80** — `gz obpi emit-receipt --help` documents required evidence-json fields
- **#88** — Ledger read cache and typed events on read path
- **#89** — Product proof gate recognizes governance artifact proof type
- **#91** — `gz interview adr` no longer blocked by interactive-only design

### Skill Consolidation and Quality (#55-58, #86, #87)

- **#86** — Retired 13 thin wrapper/duplicate skills
- **#87** — Folded `gz-obpi-audit` and `gz-obpi-sync` into `gz-obpi-reconcile`
- **#55** — Skill description scored as routing contract, not label
- **#56** — Added quantitative skill trigger/output testing chore
- **#57** — Replaced lint skill stub with working implementation
- **#58** — Decomposed `gz-obpi-pipeline` skill (was 614 lines)

### Test Infrastructure (#105-107)

- **#105** — Addressed test suite 2x slower than airlineops
- **#106** — `state_repair` in tests no longer mutates real OBPI-0.1.0-01 frontmatter
- **#107** — Reduced subprocess-per-test overhead in hook and CLI runner tests

### Enhancements (Tracked/Planned)

- **#81-85** — Ceremony CLI augmentation, ADR Evaluate authority, Specify/Promote readiness gates, pipeline markers CLI, ADR Create OBPI count validation — scoped into ADR-0.25.0+ work
- **#97** — `gz-obpi-reconcile` surfaces prior audit state before fresh analysis
- **#98** — Extended `ADR-pool.pool-health-management` into pool-management with priority ranking
- **#65** — Closeout ceremony applies OBPI pipeline structural patterns

### Other

- **#9** — Agentic Maturity Ladder documentation with gzkit readiness mapping
- **#35** — SPEC-agent-capability-uplift: resolved 3 pre-1.0 gaps
- **#40** — Added `gz skill audit` command for skill manpage coverage enforcement
- **#78** — Fixed Stage 4 ceremony template shallow-compliance output
- **#90** — Memory hygiene chore: audited auto-memory for process drift

### ADR-0.0.14 Evaluation

- Evaluated ADR-0.0.14 (Deterministic OBPI Commands): added Problem Quantification, Alternatives Considered, Non-Goals sections; rewrote OBPI-03 with prose-vs-code boundary clarity; corrected ledger lane (lite→heavy); CLI deterministic score rose from 2.45→3.50 (GO)

### Stats

- 50 GHIs closed (#9, #17, #20, #23, #35, #36, #40, #55-66, #78-108)
- 0 GHIs remaining open
- 69 commits since v0.24.1
- 2527 tests passing

## v0.24.0 (2026-03-29)

**ADR:** ADR-0.24.0 - Skill Documentation Contract

Established a three-layer documentation taxonomy (manpages, runbook entries, docstrings) and created the operator-facing skill documentation surface. Skills now have a standardized manpage template, a categorized index of all 52 skills, runbook integration at 41 workflow insertion points across both operator and governance runbooks, and a pilot batch of 6 validated manpages.

### Delivered

- Documentation taxonomy at `docs/governance/documentation-taxonomy.md`
- Skill manpage template with 6 required sections at `docs/user/skills/_TEMPLATE.md`
- Categorized skills index with 52 entries across 8 categories
- 41 skill invocation links in operator (17) and governance (24) runbooks
- 6 pilot skill manpages: gz-adr-map, gz-adr-create, gz-arb, gz-check, gz-session-handoff, gz-chore-runner

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.23.0 (2026-03-28)

**ADR:** ADR-0.23.0 - Agent Burden of Proof

Shifted the burden of proof from human attestors to completing agents. Agents must now earn their closeout by presenting a defense brief with closing arguments authored from delivered evidence, passing an automated product proof gate that checks for operator-facing documentation (runbook, command docs, or docstrings), surviving independent reviewer agent verification, and presenting all evidence in a structured ceremony before human attestation.

### Delivered

- Closing Argument template sections (Lite + Heavy) replacing the mechanical Value Narrative
- Product proof gate in `gz closeout` with three detection mechanisms (runbook, command_doc, docstring)
- Reviewer agent dispatch (Stage 3.5) producing structured REVIEW-*.md assessments
- Defense brief ceremony replacing checklist-based closeout with evidence presentation
- 101 unit tests, 14 BDD scenarios across the four OBPIs

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.22.0 (2026-03-28)

**ADR:** ADR-0.22.0 - Task-Level Governance

Introduced TASK entities as the fourth tier of the ADR→OBPI→REQ→TASK governance hierarchy. Tasks are execution-level work units with a five-state lifecycle (pending, in_progress, completed, blocked, escalated) managed through the `gz task` CLI. State transitions are enforced and recorded in the ledger. Blocked and escalated tasks capture reasons for traceability. Task status integrates into `gz status` and `gz state --json` for operator visibility including escalated counts.

### Delivered

- TASK entity model with five-state lifecycle and enforced transitions
- TASK ledger events: `task_started`, `task_completed`, `task_blocked`, `task_escalated`
- Git commit linkage for task-to-commit traceability
- `gz task` CLI with `list`, `start`, `complete`, `block`, `escalate` subcommands
- `gz status` and `gz state --json` integration with task summary and escalated counts
- Command docs: `task.md`, `task-list.md`, `task-start.md`, `task-complete.md`, `task-block.md`, `task-escalate.md`
- BDD scenarios: `features/task_governance.feature` (12 scenarios, 90 steps)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.21.0 (2026-03-27)

**ADR:** ADR-0.21.0 - Tests as Spec Verification Surface

Formalized the `@covers` decorator as a first-class test-to-spec traceability mechanism. Tests declare which governance requirements they prove via `@covers("REQ-X.Y.Z-NN-MM")`, with format validation and brief-backed REQ existence checking. A coverage anchor scanner walks the test tree to discover all annotations and produce LinkageRecords. The `gz covers` CLI reports requirement coverage at ADR, OBPI, and REQ granularity levels. ADR audit integration feeds coverage data into `gz adr audit-check` for automated requirement fulfillment verification. Operator documentation includes annotation examples, a migration guide for legacy tests, and a language-agnostic proof metadata contract for non-Python test stacks.

### Delivered

- `@covers` decorator with REQ format validation, brief-backed existence validation, and linkage registration
- Coverage anchor scanner: test tree walk, annotation discovery, LinkageRecord production, ADR/OBPI/REQ rollups
- `gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output modes
- ADR audit integration: coverage data wired into `gz adr audit-check`
- Operator docs: `docs/user/manpages/covers.md`, `docs/user/concepts/test-traceability.md`, migration guide, language-agnostic proof metadata contract
- BDD scenarios: `features/test_traceability.feature`
- `gz obpi withdraw` command for deregistering phantom/erroneous OBPI ledger entries (GHI #39)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.20.0 (2026-03-27)

**ADR:** ADR-0.20.0 - Spec-Test-Code Triangle Sync

Introduced the spec-test-code triangle framework for detecting governance drift. REQ entities in OBPI briefs, `@covers` references in tests, and code change sets form three vertices of a triangle. The drift detection engine identifies broken linkages: unlinked specs (REQs with no test), orphan tests (tests covering absent REQs), and unjustified code changes. A new `gz drift` command exposes drift reports in human, JSON, and plain output modes. Drift is integrated into `gz check` as an advisory (non-blocking) check, surfacing findings early without gating the workflow.

### Delivered

- REQ entity Pydantic model with `REQ-<semver>-<obpi>-<seq>` identifier scheme and lifecycle
- Brief REQ extractor: parses OBPI acceptance criteria to discover REQ entities
- Drift detection engine: computes unlinked specs, orphan tests, and unjustified code changes
- `gz drift` CLI with `--json` and `--plain` output modes and configurable `--adr-dir`/`--test-dir`
- `gz check` advisory drift integration: drift findings appended after blocking checks with `advisory: true` in JSON output
- Command docs: `docs/user/manpages/drift.md`, updated `docs/user/manpages/check.md`
- BDD scenarios: `features/triangle_drift.feature`, `features/check_drift_advisory.feature`

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.19.0 (2026-03-22)

**ADR:** ADR-0.19.0 - Closeout & Audit Processes

Consolidated the six-command ADR closeout workflow into a single `gz closeout ADR-X.Y.Z` pipeline that runs OBPI verification, quality gates, attestation prompt, version bump, and ledger recording in one pass. Added a matching `gz audit ADR-X.Y.Z` pipeline for post-attestation reconciliation with audit artifacts, validation receipts, and Completed-to-Validated lifecycle transition. Deprecated `gz gates` and standalone `gz attest` during closeout as both are now subsumed by the consolidated pipeline.

### Delivered

- `gz closeout ADR-X.Y.Z`: end-to-end closeout pipeline (OBPI check, gates, attestation, version bump, status transition)
- `gz audit ADR-X.Y.Z`: end-to-end audit pipeline (attestation guard, artifacts, validation receipt, Completed -> Validated transition)
- Cross-project parity checklist for airlineops (`opsdev closeout`, `opsdev audit`)
- Audit enrichment: attestation record, gate results, and evidence links in AUDIT.md
- `audit_generated` ledger event emitted on successful audit
- Audit templates (`audit.md`, `audit_plan.md`) with `.format()` rendering and evidence aggregation from ledger
- ADR lifecycle transition Completed -> Validated via LifecycleStateMachine
- `gz gates` deprecation warning directing operators to `gz closeout`
- `gz attest` deprecation warning when closeout is active for the target ADR
- Unicode arrow fix for Windows cp1252 console encoding (GHI #28)

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.18.0 (2026-03-21)

**ADR:** ADR-0.18.0 - Subagent-Driven Pipeline Execution

Evolved the gz-obpi-pipeline from single-session inline execution to a controller/worker architecture. Stage 2 dispatches fresh implementer subagents per plan task with model-aware routing (haiku/sonnet/opus by complexity). Two independent reviewer subagents (spec compliance + code quality) run after each task. Stage 3 dispatches parallel verification subagents for non-overlapping REQ paths using worktree isolation.

### Delivered

- Agent role taxonomy: four pipeline roles (Planner, Implementer, Reviewer, Narrator) with formal handoff contracts, tool restrictions, and conflict resolution
- Controller/worker Stage 2: sequential implementer dispatch with structured result contracts (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED) and circuit breakers
- Two-stage review protocol: concurrent spec compliance and code quality reviewers with fix cycles (max 2 per task before escalation)
- REQ-level parallel verification dispatch in Stage 3 with wall-clock timing metrics
- Pipeline runtime integration: dispatch state tracking, result aggregation, model routing config
- New CLI surface: `gz roles` for querying role taxonomy and dispatch history
- Agent file definitions in `.claude/agents/` with YAML frontmatter enforcing tool permissions and model defaults
- `--no-subagents` fallback preserving inline execution for debugging

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.17.0 (2026-03-20)

**ADR:** ADR-0.17.0 - AGENTS.md Tidy: Control Surface Schema and Rules Mirroring

Reduced context window bloat by ~80% through a three-layer control surface model: canonical artifacts in `.gzkit/`, generated vendor mirrors in `.claude/`/`.github/`/`.agents/`, and slim entry-point documents (AGENTS.md, CLAUDE.md). Governance rules reach all agents reliably while keeping always-loaded content minimal.

### Delivered

- Categorized skill catalog organizing 51 skills into 8 functional categories in AGENTS.md
- Rules mirroring pipeline: canonical `.gzkit/rules/` rendered into vendor-specific formats (Claude rules, Copilot instructions)
- Slim CLAUDE.md template (<=60 lines) delegating to `.claude/rules/` and `.claude/skills/`
- JSON schemas (`skill.schema.json`, `rule.schema.json`) with Pydantic validation models
- Manifest updated with `canonical_rules` and `canonical_schemas` entries; stale mirror cleanup; `gz-obpi-lock` promoted to canonical

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.16.0 (2026-03-19)

**ADR:** ADR-0.16.0 - CMS Architecture Formalization

Formalized gzkit's identity as a headless CMS for governance by implementing the Django-parallel architecture. Content types have a registry, canonical content has a template engine for vendor rendering, vendor enablement is manifest-driven and selective, and content lifecycle is an explicit state machine.

### Delivered

- Content type registry cataloging every governance artifact type with Pydantic models, schemas, lifecycle states, and rendering rules
- Rules-as-content pattern: `.gzkit/rules/` as canonical source, rendered into vendor-specific mirrors by `gz agent sync`
- Vendor manifest schema with selective enablement (`vendors.claude.enabled: true`)
- Vendor-aware template engine in `gz agent sync control-surfaces`
- Content lifecycle state machine with per-content-type transition tables, `InvalidTransitionError` enforcement, and ledger event emission

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.15.0 (2026-03-18)

**ADR:** ADR-0.15.0 - Pydantic Schema Enforcement

Closed the gap between gzkit's stated architecture (AI-000: "JSON Schema defines shape; Pydantic enforces at runtime") and its implemented reality. Every structured data type in gzkit is now a Pydantic BaseModel with declarative validation.

### Delivered

- Migrated core models (LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult) from dataclasses to Pydantic BaseModel
- Created Pydantic frontmatter models for ADR, OBPI, and PRD content types with pattern validators and Literal types
- Replaced ~280 lines of manual ledger event validation with Pydantic discriminated unions (12 typed event models)
- Added 17 cross-validation tests enforcing the invariant that Pydantic models and JSON schemas never drift
- Fixed document validation defect where non-governance files were incorrectly validated

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.14.0 (2026-03-17)

**ADR:** ADR-0.14.0 - Multi-Agent Instruction Architecture Unification

Unified gzkit's multi-agent instruction delivery into a canonical-shared-plus-thin-adapters architecture, replacing duplicated root surfaces with a single shared model that renders into vendor-specific adapters.

### Delivered

- Canonical shared instruction model with `AGENTS.md` as single source and thin vendor adapter renders for Claude and Copilot
- Native path-scoped instruction support via nested `AGENTS.md` and `.claude/rules/`
- Root control surface slimming with recurring workflows relocated to skills/playbooks
- Instruction auditing for stale, conflicting, unreachable, and foreign-project rules
- Machine-local vs repo-tracked config separation with deterministic sync
- Instruction eval suite and readiness checks with positive/negative controls

### Gate Evidence

All 5 GovZero gates satisfied.

### Verification

- `uv run gz closeout ADR-0.14.0-multi-agent-instruction-architecture-unification`
- `uv run gz attest ADR-0.14.0-multi-agent-instruction-architecture-unification --status completed`
- `uv run gz audit ADR-0.14.0-multi-agent-instruction-architecture-unification`
- `uv run gz adr emit-receipt ADR-0.14.0-multi-agent-instruction-architecture-unification --event validated --attestor "human:jeff" --evidence-json ...`

## v0.12.0 (2026-03-13)

**ADR context:** `ADR-0.12.0-obpi-pipeline-enforcement-parity`
**Release scope:** AirlineOps pipeline-enforcement parity across plan-exit gating, routing, write-time enforcement, completion reminders, and active runtime registration.

### Delivered

- Ported the Claude plan-exit enforcement chain with `plan-audit-gate.py` and `pipeline-router.py`.
- Added the write-time `pipeline-gate.py` and advisory `pipeline-completion-reminder.py` hook surfaces.
- Registered the full pipeline hook chain in `.claude/settings.json` with the intended matcher and ordering contract.
- Completed the pipeline active-marker bridge for per-OBPI and legacy compatibility markers.
- Hardened ADR closeout/attestation runtime behavior so `gz closeout` materializes `ADR-CLOSEOUT-FORM.md` and `gz attest` updates the ADR attestation block and closeout form.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.12.0-obpi-pipeline-enforcement-parity`.

### Verification

- `uv run gz adr audit-check ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz closeout ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz attest ADR-0.12.0-obpi-pipeline-enforcement-parity --status completed`
- `uv run gz audit ADR-0.12.0-obpi-pipeline-enforcement-parity`
- `uv run gz adr emit-receipt ADR-0.12.0-obpi-pipeline-enforcement-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.11.0 (2026-03-12)

**ADR context:** `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
**Release scope:** Faithful AirlineOps OBPI completion pipeline parity across transaction, validation, receipt, reconciliation, and operator workflow surfaces.

### Delivered

- Defined the OBPI transaction contract and fail-closed scope-isolation rules for gzkit.
- Added guarded completion validation, structured completion receipts, and anchor-aware OBPI reconciliation.
- Ported the canonical `gz-obpi-pipeline` skill and synchronized mirrored/generated control surfaces.
- Aligned doctrine, templates, operator workflow docs, and closeout guidance to the same staged pipeline contract.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`.

### Verification

- `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json`
- `uv run gz obpi reconcile OBPI-0.11.0-06-template-closeout-and-migration-alignment --json`
- `uv run gz closeout ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
- `uv run gz attest ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --status completed`
- `uv run gz audit ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
- `uv run gz adr emit-receipt ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.10.0 (2026-03-10)

**ADR context:** `ADR-0.10.0-obpi-runtime-surface`
**Release scope:** OBPI runtime surfaces for status, reconciliation, closeout readiness, and lifecycle proof integration.

### Delivered

- Added governed OBPI runtime contract semantics and lifecycle state derivation consumed from ledger and brief evidence.
- Delivered operator-facing `gz obpi status` and `gz obpi reconcile` surfaces with JSON and fail-closed reconciliation behavior.
- Integrated OBPI proof state into `gz adr status` and `gz closeout` so ADR closeout readiness is derived from linked OBPI evidence.
- Produced heavy-lane closeout, audit, and validated receipt artifacts for ADR-0.10.0.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.10.0-obpi-runtime-surface`.

### Verification

- `uv run gz obpi status OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration --json`
- `uv run gz obpi reconcile OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration`
- `uv run gz adr status ADR-0.10.0-obpi-runtime-surface --json`
- `uv run gz closeout ADR-0.10.0-obpi-runtime-surface`
- `uv run gz attest ADR-0.10.0-obpi-runtime-surface --status completed`
- `uv run gz audit ADR-0.10.0-obpi-runtime-surface`
- `uv run gz adr emit-receipt ADR-0.10.0-obpi-runtime-surface --event validated --attestor "human:jeff" --evidence-json ...`

## v0.9.0 (2026-03-09)

**ADR context:** `ADR-0.9.0-airlineops-surface-breadth-parity`
**Release scope:** AirlineOps control-surface breadth parity tranche with closeout, audit, and validation packaging.

### Delivered

- Imported the approved `.claude/hooks` governance tranche and wired compatibility-safe hook enforcement into `.claude/settings.json`.
- Classified canonical `.gzkit/**` deltas with explicit import/defer/exclude rationale and executed the approved governance-surface tranche.
- Added local process-plane ontology/schema governance assets and synchronized generated control surfaces.
- Produced closeout, audit, and validated lifecycle artifacts for ADR-0.9.0, including OBPI evidence completion and audit proofs.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.9.0-airlineops-surface-breadth-parity`.

### Verification

- `uv run gz status --table`
- `uv run gz adr status ADR-0.9.0-airlineops-surface-breadth-parity --json`
- `uv run gz closeout ADR-0.9.0-airlineops-surface-breadth-parity`
- `uv run gz attest ADR-0.9.0-airlineops-surface-breadth-parity --status completed`
- `uv run gz audit ADR-0.9.0-airlineops-surface-breadth-parity`
- `uv run gz adr emit-receipt ADR-0.9.0-airlineops-surface-breadth-parity --event validated --attestor "human:jeff" --evidence-json ...`

## v0.8.0 (2026-03-07)

**ADR context:** `ADR-0.8.0-gz-chores-system`
**Release scope:** gz chores system delivery with full heavy-lane closeout and validation evidence.

### Delivered

- Introduced config-first chores lifecycle commands:
  - `gz chores list`
  - `gz chores plan <slug>`
  - `gz chores run <slug>`
  - `gz chores audit --all|--slug`
- Added guarded registry + runner semantics in `config/gzkit.chores.json` and
  `src/gzkit/commands/chores.py`, including deterministic log paths under
  `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`.
- Added lifecycle/runner coverage in `tests/commands/test_chores.py` and command-parser coverage
  in `tests/commands/test_parsers.py`.
- Completed ADR heavy-lane ceremony for 0.8.0:
  closeout initiated, gates 1-5 passed, audit artifacts generated, attestation recorded, and
  validated ADR receipt emitted.
- Updated runtime/package metadata to `0.8.0` in `pyproject.toml`, `src/gzkit/__init__.py`,
  `uv.lock`, and `README.md`.

### Gate Evidence

All 5 GovZero gates satisfied for `ADR-0.8.0-gz-chores-system`.

### Verification

- `uv run gz gates --adr ADR-0.8.0-gz-chores-system`
- `uv run gz closeout ADR-0.8.0-gz-chores-system`
- `uv run gz audit ADR-0.8.0-gz-chores-system`
- `uv run gz attest ADR-0.8.0-gz-chores-system --status completed`
- `uv run gz adr emit-receipt ADR-0.8.0-gz-chores-system --event validated --attestor "human:jeff" --evidence-json ...`
- `uv run gz adr status ADR-0.8.0-gz-chores-system --json`

## v0.7.0 (2026-03-06)

**ADR context:** `ADR-0.7.0-obpi-first-operations`
**Release scope:** Version metadata correction and governance verification backfill packaging.

### Delivered

- Updated package/runtime metadata to `0.7.0` in `pyproject.toml`, `src/gzkit/__init__.py`,
  `uv.lock`, and `README.md`.
- Finalized previously staged governance remediation for Gate 4 (BDD/Behave) evidence across
  released lines `0.1.0` to `0.3.1`.
- CLI/runtime now reports `gzkit 0.7.0`.

### Governance remediation (2026-03-01)

Backfilled Gate 4 (BDD/Behave) evidence for released versions in the `0.1.0` to `0.3.1` range.

- Added an executable Behave suite at `features/heavy_lane_gate4.feature` with step code under
  `features/steps/`.
- Added `behave` as a project dependency and declared `verification.bdd` in `.gzkit/manifest.json`.
- Recorded Gate 4 pass events for:
  - `ADR-0.1.0` (release `0.1.0`)
  - `ADR-0.2.0` (release `0.2.0`)
  - `ADR-0.3.0` (release line covering `0.3.0` and patch `0.3.1`)
- Confirmed `v0.3.1` release note anchor remains `ADR-0.3.0`.

### Verification

- `uv run gz --version`
- `uv run gz lint`
- `uv run gz test`
- `uv run -m behave features/`
- `uv run gz gates --gate 4 --adr ADR-0.1.0`
- `uv run gz gates --gate 4 --adr ADR-0.2.0`
- `uv run gz gates --gate 4 --adr ADR-0.3.0`

## v0.6.0 (2026-03-04)

**ADR:** ADR-0.6.0-pool-promotion-protocol - Pool Promotion Protocol and Tooling

Introduces a deterministic, auditable protocol for promoting pool ADRs (backlog) into canonical, versioned ADR packages.

### Delivered

- `gz adr promote` command for automated promotion and rename lineage tracking.
- Ledger `artifact_renamed` event integration for promotion auditability.
- Canonical ADR bucket layout (foundation/pre-release/<major>.0) enforcement.
- Archival protocol for source pool files with `Superseded` status tracking.

### Gate Evidence

All 5 GovZero gates satisfied.
- Closeout attestation recorded in `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-CLOSEOUT-FORM.md` on 2026-03-05.

## v0.5.0 (2026-03-01)

**ADR:** ADR-0.5.0 - Skill Lifecycle Governance

Defined the formal lifecycle contract for skills to ensure capability parity is maintainable and operator-visible.

### Delivered

- Skill taxonomy and capability model for canonical skills and mirrors.
- Parity verification policy and executable runtime checks.
- Formal state transition semantics and evidence requirements for skill lifecycle.
- Maintenance and deprecation runbooks for governance-backed skill operations.

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.4.0 (2026-03-01)

**ADR:** ADR-0.4.0 - Skill Capability Mirroring

Promoted skill-capability mirroring to a governed, heavy-lane ADR with completed OBPI execution and closeout artifacts.

### Delivered

- Canonical skill source centralization with multi-agent mirror surfaces.
- Agent-native mirror contract enforcement and sync determinism hardening.
- Compatibility migration updates and control-surface parity operations.
- Closeout ceremony artifacts and Gate 4 BDD backfill enforcement.

### Gate Evidence

All 5 GovZero gates satisfied.

## v0.3.1 - Ledger Schema Enforcement Patch (2026-02-14)

**ADR context:** `ADR-0.3.x` line (active anchor: `ADR-0.3.0`)
**GHI:** [#2](https://github.com/tvproductions/gzkit/issues/2)

Patch release to enforce ledger schema validation as a fail-closed governance invariant.

### Added

- Formal ledger schema at `src/gzkit/schemas/ledger.json`.
- Strict ledger JSONL validation routine at `src/gzkit/validate.py`.
- Focused CLI validation path: `gz validate --ledger`.

### Changed

- `gz validate` default/all mode now validates `.gzkit/ledger.jsonl`.
- Validation now fails closed for malformed JSON, unknown events, invalid schema values, missing required fields, and invalid event payload types/enums.

### Verification

- `uv run -m unittest tests.test_validate tests.test_cli tests.test_ledger`
- `uv run gz lint`
- `uv run gz validate --ledger`
