# Parity Diff (Prose ↔ Mechanical Check)

**Generated:** 2026-05-10

For each prose assertion in `prose-assertions.md`, the mapped promoted check
(from `promoted-inventory.md`) and the gap class:

- `in-parity` — prose and check assert the same invariant at the same scope
- `prose-wider` — prose says X, check enforces a subset X'
- `check-wider` — check enforces Y, no prose explicitly states it (rule lags)
- `mismatched` — prose and check both exist but assert different things
- `prose-only` — no mechanical check exists
- `check-only` — check exists, no rule prose states it

Path renderings use POSIX form.

| # | Assertion | Source rule file | Mapped check | Gap class |
|---|-----------|------------------|--------------|-----------|
| 1 | No bare `except:` / `except Exception:` outside CLI | `.gzkit/rules/pythonic.md` | ruff BLE001 (external) | in-parity (delegated to ruff) |
| 2 | Functions <=50 lines | `.gzkit/rules/pythonic.md` | xenon / radon pre-commit (external) | in-parity (delegated; `--class-size` covers classes only) |
| 3 | Modules <=600 lines | `.gzkit/rules/pythonic.md` | pre-commit module-size hook (external) | in-parity (delegated) |
| 4 | Classes <=300 lines | `.gzkit/rules/pythonic.md` | `--class-size` (`audit_class_size`) | in-parity |
| 5 | Top-level imports only; no lazy imports | `.gzkit/rules/pythonic.md` | ruff PLC0415 (partial) | prose-wider (rule says "no lazy imports", PLC0415 has carve-outs) |
| 6 | No `# type: ignore[<code>]` bracketed form | `.gzkit/rules/pythonic.md` | `--type-ignores` (`audit_type_ignores`) | in-parity |
| 7 | Use Pydantic `BaseModel`; no stdlib dataclass | `.gzkit/rules/models.md` | `--pydantic-models` | in-parity |
| 8 | Use `ConfigDict(frozen=True, extra="forbid")` for immutable | `.gzkit/rules/models.md` | `--pydantic-models` (presence-of-`model_config` only) | **prose-wider** (check verifies model_config exists; does NOT verify `frozen=True` or `extra="forbid"` content) |
| 9 | Use `Field(...)` with descriptions; `Field(None, ...)` for optional | `.gzkit/rules/models.md` | no mechanical check | prose-only |
| 10 | `str \| None` not `Optional[str]` | `.gzkit/rules/models.md` | ruff UP007 (external) | in-parity (delegated) |
| 11 | Run `gz cli audit` before landing new flag/subcommand | `.gzkit/rules/cli.md` | `gz cli audit` (CLI command, not validate scope) | in-parity (delegated to gz cli audit) |
| 12 | Exit-code map (0/1/2/3) | `.gzkit/rules/cli.md` | no mechanical check | prose-only |
| 13 | Flag conventions `--quiet`/`--verbose`/`--dry-run`/`--json`/`--help` | `.gzkit/rules/cli.md` | no mechanical check | prose-only |
| 14 | `--json` valid JSON to stdout, logs to stderr | `.gzkit/rules/cli.md` | no mechanical check | prose-only |
| 15 | Every command responds to `-h`/`--help` with description, usage, options, example | `.gzkit/rules/cli.md` | partially via `gz cli audit` | prose-wider |
| 16 | Paths via `Path("dir") / "file"` | `.gzkit/rules/cross-platform.md` | ruff PTH rules (external) | in-parity (delegated) |
| 17 | Relative paths via `.relative_to(root).as_posix()` | `.gzkit/rules/cross-platform.md` | `tests/governance/test_path_separator_portability.py` (test, not validate scope) | in-parity (delegated to test) |
| 18 | File I/O `encoding="utf-8"` | `.gzkit/rules/cross-platform.md` | ruff (partial) | prose-wider |
| 19 | Temp files use context managers | `.gzkit/rules/cross-platform.md` | no mechanical check | prose-only |
| 20 | No `shell=True`; no bare `python` | `.gzkit/rules/cross-platform.md` | ruff S602/S603 (external) | in-parity (delegated) |
| 21 | No `PYTHONUTF8=1 uv run gz` prefix | `.gzkit/rules/cross-platform.md` + `AGENTS.md` Local rules | `--utf8-prefix` (`audit_utf8_prefix`) | in-parity |
| 22 | Fresh `python -c` / helpers need `sys.stdout.reconfigure` | `.gzkit/rules/cross-platform.md` | `--utf8-prefix` (extended scope, GHI #275) | in-parity |
| 23 | Use stdlib `unittest`; no pytest | `.gzkit/rules/tests.md` | `forbid-pytest` pre-commit hook (external) | in-parity (delegated) |
| 24 | Smoke/BVT <=60s | `.gzkit/rules/tests.md` | no mechanical check (rule notes "not an agent-introspected clock") | prose-only by design |
| 25 | Unit tests MUST use `tempfile` temp DBs | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 26 | NEVER use raw `shutil.rmtree()` in tearDown | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 27 | Coverage floor >=40% | `.gzkit/rules/tests.md` | pre-commit coverage hook (external) | in-parity (delegated) |
| 28 | Red-Green-Refactor discipline | `.gzkit/rules/tests.md` | no mechanical check (scored Judgment in scorecard #34) | prose-only |
| 29 | Test cases derive from OBPI brief acceptance criteria | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 30 | Tests assert semantics, not strings | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 31 | Audit-helper names MUST NOT pattern-match audit-step names | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 32 | Commit trailer (`Task:`/`Ceremony:`/`Eval-feedback-source:`) | `.gzkit/rules/tests.md` + `AGENTS.md` Always #12 | `--commit-trailers` | in-parity |
| 33 | Mock every subprocess boundary; <200ms; deterministic | `.gzkit/rules/tests.md` | no mechanical check | prose-only |
| 34 | Behave scenarios carry `@REQ-X.Y.Z-NN-MM` tag | `.gzkit/rules/tests.md` | `--behave-req-tags` | in-parity |
| 35 | Read AGENTS.md before implementation | `.gzkit/rules/governance-core.md` | SessionStart hook (external) | in-parity (delegated to hook) |
| 36 | Use `uv run` for Python execution | `.gzkit/rules/governance-core.md` | `--cli-alignment` (partially — only checks `gz <verb>` resolution) | prose-wider |
| 37 | Do not bypass Gate 5 for heavy/foundation | `.gzkit/rules/governance-core.md` | `gz closeout` runtime gate (external) | in-parity (delegated to runtime) |
| 38 | Do not edit `.gzkit/ledger.jsonl` manually | `.gzkit/rules/governance-core.md` | `.githooks/pre-commit-ledger-guard` (external hook) | in-parity (delegated to git hook) |
| 39 | Every defect must be trackable | `.gzkit/rules/governance-core.md` | no mechanical check (Judgment #17) | prose-only by design |
| 40 | `gz <verb>` references resolve | `.gzkit/rules/governance-core.md` | `--cli-alignment` | in-parity |
| 41 | Multi-word subcommands count | `.gzkit/rules/governance-core.md` | `--cli-alignment` — first-token only | **mismatched** (rule says multi-word subcommands count; regex captures only first verb token) |
| 42 | `adr-status.md` is Layer 3 derived; never source-of-truth | `.gzkit/rules/governance-core.md` | `--adr-status-fresh` | in-parity |
| 43 | Adr audit-check sequence (audit-check → quality → closeout → emit) | `.gzkit/rules/adr-audit.md` | no mechanical check (Judgment #40) | prose-only by design |
| 44 | Do not run `gz audit` before attestation | `.gzkit/rules/adr-audit.md` | runtime gate in `gz audit` (external) | in-parity (delegated to runtime) |
| 45 | Never backfill cosmetic `@covers` to silence audit-check | `.gzkit/rules/adr-audit.md` | no mechanical check | prose-only |
| 46 | Brief evidence sections H3, not H2 | `.gzkit/rules/brief-heading-conventions.md` | `--brief-headings` | in-parity |
| 47 | Canonical evidence headings: Implementation Summary / Key Proof / Closing Argument | `.gzkit/rules/brief-heading-conventions.md` | `--brief-headings` | in-parity |
| 48 | Edit `.gzkit/` first; never edit vendor mirrors | `.gzkit/rules/skill-surface-sync.md` | `gz agent sync control-surfaces` drift detection (external) | in-parity (delegated) |
| 49 | Bump `skill-version:` on every skill edit | `.gzkit/rules/skill-surface-sync.md` | skill-version frontmatter validation via `--surfaces` schema | in-parity (delegated) |
| 50 | Bump rule body-level `<!-- rule-version: X.Y.Z -->` on every rule edit | `.gzkit/rules/skill-surface-sync.md` | no mechanical check | **prose-only** (rule says required, no validator enforces presence/bump) |
| 51 | Run `gz agent sync control-surfaces` after every edit | `.gzkit/rules/skill-surface-sync.md` | `.githooks/pre-commit-sync-guard` (external hook) | in-parity (delegated to git hook) |
| 52 | Lite by default: `unittest -q` only | `.gzkit/rules/chores.md` | lane config in `gz chores plan` (external) | in-parity (delegated) |
| 53 | Stray `CHORE.md`/`acceptance.json` outside canonical roots is defect | `.gzkit/rules/chores.md` | `--chores-layout` | in-parity |
| 54 | Each chore slug MUST contain CHORE.md, acceptance.json, README.md | `.gzkit/rules/chores.md` | `gz chores doctor` (external) | in-parity (delegated) |
| 55 | Invariant 1: every CLI verb has wielding skill | `.gzkit/rules/tool-skill-runbook-alignment.md` | `--skill-alignment` | in-parity |
| 56 | Invariant 2: skill `gz_command:` matches runbook-prescribed verb | `.gzkit/rules/tool-skill-runbook-alignment.md` | no mechanical check (Promotable #29) | prose-only |
| 57 | Invariant 3: destination verb's output form honors skill Output Contract | `.gzkit/rules/tool-skill-runbook-alignment.md` | no mechanical check (Promotable #30) | prose-only |
| 58 | Use `gh` only when explicitly requested | `.gzkit/rules/gh-cli.md` | no mechanical check (Judgment #51) | prose-only by design |
| 59 | Prohibited gh commands (settings mutations, etc.) | `.gzkit/rules/gh-cli.md` | permission model in `.claude/settings.json` (external) | in-parity (delegated to permissions) |
| 60 | Cross-repo gzkit defects via `gz issue file` | `.gzkit/rules/gh-cli.md` | `gz issue file` runtime validation (external) | in-parity (delegated) |
| 61 | Operator PII — never include personal email | `.gzkit/rules/gh-cli.md` + `AGENTS.md` Local rules | no mechanical check | **prose-only** (high-impact: leak requires filter-repo rewrite — see 2026-04-19 incident) |
| 62 | Security work needs heightened review regardless of lane/kind | `.gzkit/rules/security-sensitivity.md` | `--sensitivity` + audit OR-branch | in-parity |
| 63 | Briefs overlapping security surfaces MUST declare `sensitivity: security` | `.gzkit/rules/security-sensitivity.md` | `--sensitivity` (auto-detect floor) | in-parity |
| 64 | Editing `data/security_surfaces.json` requires `sensitivity: security` brief | `.gzkit/rules/security-sensitivity.md` | `--sensitivity` (registry self-bootstrap) | in-parity |
| 65 | Heightened Gate 5 walkthrough for `sensitivity: security` | `.gzkit/rules/security-sensitivity.md` | `gz obpi complete` runtime gate (external) | in-parity (delegated to runtime) |
| 66 | Scanner-unavailable is fail-closed | `.gzkit/rules/security-sensitivity.md` | reserved `arb-step-security-scan-*` ARB slot (external) | in-parity (delegated) |
| 67 | Six-pattern failure-mode vocabulary | `.gzkit/rules/agent-failure-modes.md` | no mechanical check (Judgment #49) | prose-only by design |
| 68 | Exemplar-corpus selection: all 7 criteria | `.gzkit/rules/complexity-doctrine.md` | no mechanical check | **prose-only** (high-impact: corpus integrity has no on-disk check) |
| 69 | Corpus anti-patterns disqualify | `.gzkit/rules/complexity-doctrine.md` | no mechanical check | prose-only |
| 70 | Re-distillation triggers (annual / drift>25% / judgment) | `.gzkit/rules/complexity-doctrine.md` | no mechanical check (advisor verdict-frequency drift tracked separately) | prose-only |
| 71 | Downstream ADRs cite distilled-characteristics doc | `.gzkit/rules/complexity-doctrine.md` | `--complexity-doctrine-links` | in-parity |
| 72 | Citation tuple `(path, anchor, corpus_revision)` | `.gzkit/rules/complexity-doctrine.md` | `--complexity-doctrine-links` + Pydantic `Citation` model | in-parity |
| 73 | Percentile + absolute pairing | `.gzkit/rules/complexity-doctrine.md` | `--complexity-thresholds` (via per-band schema) | in-parity |
| 74 | Citation valid at corpus_revision N and N+1 | `.gzkit/rules/complexity-doctrine.md` | `--complexity-doctrine-links` (portability window) | in-parity |
| 75 | One canonical threshold table; trigger vocabulary `block`/`warn`/`advise` | `.gzkit/rules/complexity-thresholds.md` | `--complexity-thresholds` | in-parity |
| 76 | Every metric MUST carry `block` band | `.gzkit/rules/complexity-thresholds.md` | `--complexity-thresholds` (loader fail-closed) | in-parity |
| 77 | Silent amendments forbidden | `.gzkit/rules/complexity-thresholds.md` | `--complexity-thresholds` | in-parity |
| 78 | Docs update when command output changes | `.gzkit/rules/gate5-runbook-code-covenant.md` | no mechanical check (Judgment #48) | prose-only by design |
| 79 | No placeholder output examples | `.gzkit/rules/gate5-runbook-code-covenant.md` | no mechanical check (Promotable #49) | prose-only |
| 80 | Heavy/foundation requires human attestation | `.gzkit/rules/gate5-runbook-code-covenant.md` | `gz closeout` runtime gate (external) | in-parity (delegated) |
| 81 | Token-block: release fail-closed without handoff | `.gzkit/rules/token-block-discipline.md` | `gz validate --lock-handoff-coupling` (planned OBPI-0.0.41-04) | **prose-only** (validator not yet implemented; rule references future scope) |
| 82 | Token-block: register entry minimum-information rule (4 fields) | `.gzkit/rules/token-block-discipline.md` | `gz validate --lock-handoff-coupling` (planned) | prose-only |
| 83 | Token-block: abandon category enum closed | `.gzkit/rules/token-block-discipline.md` | CLI parsing fail-closed (planned OBPI-0.0.41-02) | prose-only |
| 84 | Token-block: reaping requires degenerate register entry | `.gzkit/rules/token-block-discipline.md` | runtime fail-closed (planned) | prose-only |
| 85 | Skills SKILL.md must declare `model:` frontmatter | `.gzkit/rules/model-selection.md` | `--surfaces` Pydantic `SkillFrontmatter` | in-parity |
| 86 | Valid model values: haiku/sonnet/opus | `.gzkit/rules/model-selection.md` | `--surfaces` Literal validation | in-parity |
| 87 | Subagent prompts specify effort, not model ID | `.gzkit/rules/model-selection.md` | no mechanical check | prose-only |
| 88 | Model tier determined by decision complexity, not task size | `.gzkit/rules/model-selection.md` | no mechanical check | prose-only by design (judgment) |
| 89 | `.gzkit/rules/*.md` carry scoped `paths:`; no `paths: "**"` | implicit / ADR-0.0.20 | `--unscoped-rules` | in-parity |
| 90 | Every rule file in scorecard | implicit / GHI #212 | `--advisory-scorecard` (presence-only) | **prose-wider** (rule says "with a score"; check verifies stem mention only — does NOT verify scored) |
| 91 | Pool ADRs never receive runtime-track events | `AGENTS.md` § Architectural Boundaries #1-2 | `--pool-adr-isolation` | in-parity |
| 92 | Do not build graph engine without state-doctrine lock | `AGENTS.md` § Architectural Boundaries #3 | no mechanical check (Judgment) | prose-only by design |
| 93 | Reconciliation is not maintenance chore | `AGENTS.md` § Architectural Boundaries #4 | `--reconcile-freshness` | in-parity |
| 94 | Do not let derived views silently become source-of-truth | `AGENTS.md` § Architectural Boundaries #6 | `--frontmatter` + `--event-handlers` + `--validator-fields` | in-parity |
| 95 | ADR taxonomy kind/semver/id-prefix consistency | `AGENTS.md` § Gate Covenant — kinds | `--taxonomy` | in-parity |
| 96 | Order versioned identifiers semantically | `AGENTS.md` Local rules | `tests/test_adr_status.py` (test) | in-parity (delegated to test) |
| 97 | Add imports with usage in same Edit | `AGENTS.md` Local rules | post-edit ruff hook removes unused imports (external) | in-parity (delegated) |
| 98 | Every version bump → GitHub release | `AGENTS.md` Local rules | `--version-release` | in-parity |
| 99 | Operator PII — never personal email in repo artifacts | `AGENTS.md` Local rules | no mechanical check | **prose-only** (HIGH IMPACT — recovery requires filter-repo + force-push) |
| 100 | Prime directive 1-6 (own work, complete fully, never excuse) | `AGENTS.md` | no mechanical check (judgment) | prose-only by design |
| 101 | DO IT RIGHT 1-9 (class of failure, no vibe coding, etc.) | `AGENTS.md` | no mechanical check (judgment) | prose-only by design |
| 102 | Anti-vibing: 5:1 ratio, smallest-vibing-surface | `AGENTS.md` | partial via `--instructions-files-budget` (size only) | prose-wider |
| 103 | Stdlib-first doctrine: default is stdlib | `AGENTS.md` | no mechanical check | prose-only |
| 104 | Operator economy: agent drafts, operator reviews | `AGENTS.md` | no mechanical check | prose-only by design |
| 105 | Always #6: include 'Why' in subagent prompts | `AGENTS.md` | no mechanical check | prose-only |
| 106 | Always #7: <90% sure → ask human | `AGENTS.md` | no mechanical check (judgment) | prose-only by design |
| 107 | Always #11: course-correction insight record | `AGENTS.md` | `--insights-shape` (shape-only, not presence) | **prose-wider** (rule requires record on every course-correction; check only validates shape when written) |
| 108 | Always #12: Eval-feedback-source trailer on eval-feedback rule edits | `AGENTS.md` | `--commit-trailers` (partial — trailer presence only) | prose-wider |
| 109 | Never #5: don't summarize after Stage 2/3 and stop | `AGENTS.md` | runtime stage discipline (external) | in-parity (delegated) |
| 110 | Never #6: don't work around hook blocks | `AGENTS.md` | no mechanical check (judgment) | prose-only by design |
| 111 | Never #7: don't read frontmatter status as completion proof | `AGENTS.md` | `--frontmatter` (frontmatter-vs-ledger drift) | in-parity |
| 112 | Attestation: canonical receipt-prefix table | `AGENTS.md` § Attestation | `--attestation-receipts` (validates receipt IDs resolve) | in-parity (heavy-lane); partial (lite-lane warn only) |
| 113 | Defect-fix routing thresholds (<=10 lines, <=2 files, etc.) | `AGENTS.md` § Defect-fix routing | no mechanical check | prose-only by design (judgment) |
| 114 | AGENTS.md/CLAUDE.md/rule files per-file char budget | implicit / GHI #373 | `--instructions-files-budget` | in-parity |
| 115 | SessionStart orientation hook + script wired | implicit / GHI #341 | `--orientation-freshness` | in-parity |
| 116 | Invariant 10a — skill-tool-invoke-same-turn | `CLAUDE.md` | no mechanical check (Promotable) | prose-only |
| 117 | Compact instructions preserve pipeline/OBPI/gate state | `CLAUDE.md` | no mechanical check | prose-only by design |
| 118 | Two test runners (unittest + behave); no third tier | `.gzkit/rules/tests.md` § Two runners | `--test-tiers` | in-parity |
| 119 | Cross-repo absorption: same opsdev source across parent ADRs needs `paired_with:` | implicit / GHI #376 | `--absorption-duplicates` | in-parity (check-only relative to rule prose) |
| 120 | Decommissioned `docs/user/commands/` must not exist | implicit / GHI #418 | `--doc-surface-parity` | **check-only** (no rule prose anywhere in `.gzkit/rules/`; lives only in code + GHI) |
| 121 | Low ADR evaluation scores require justify artifact | implicit / ADR-0.0.26 | `--evaluation-justify-binding` | check-only (lives in ADR, not rule prose) |
| 122 | Advisor diagnoses require non-empty proof | implicit / ADR-0.0.29 OBPI-08 | `--advisor-proof-binding` | check-only (lives in ADR, not rule prose) |
| 123 | Ledger event types have matching schemas | implicit / GHI #374 | `--audits` → `audit_event_schemas` | check-only |

## Drift summary

- Mechanically-mismatched: row 41 (multi-word subcommand check captures first token only).
- Prose-wider with material consequence: rows 8, 50, 61/99, 81-84, 90, 102, 107, 108 — each represents a rule that *looks* promoted but the check is narrower than the prose.
- Check-only: rows 120, 121, 122, 123 — checks exist but no corresponding rule prose in `.gzkit/rules/*.md` (the canon is buried in ADR/GHI).
- Highest-impact prose-only: row 99 (operator PII), row 50 (rule-version bump), row 68 (corpus selection criteria).
