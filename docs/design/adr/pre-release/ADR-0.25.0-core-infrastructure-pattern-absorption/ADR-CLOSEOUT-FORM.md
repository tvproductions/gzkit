# ADR Closeout Form: ADR-0.25.0-core-infrastructure-pattern-absorption

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.25.0-core-infrastructure-pattern-absorption` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.25.0-01-attestation-pattern](OBPI-0.25.0-01-attestation-pattern.md) | Attestation Pattern | Completed |
| [OBPI-0.25.0-02-progress-pattern](OBPI-0.25.0-02-progress-pattern.md) | Progress Pattern | Completed |
| [OBPI-0.25.0-03-signature-pattern](OBPI-0.25.0-03-signature-pattern.md) | Signature Pattern | Completed |
| [OBPI-0.25.0-04-world-state-pattern](OBPI-0.25.0-04-world-state-pattern.md) | World State Pattern | Completed |
| [OBPI-0.25.0-05-dataset-version-pattern](OBPI-0.25.0-05-dataset-version-pattern.md) | Dataset Version Pattern | Completed |
| [OBPI-0.25.0-06-registry-pattern](OBPI-0.25.0-06-registry-pattern.md) | Registry Pattern | Completed |
| [OBPI-0.25.0-07-types-pattern](OBPI-0.25.0-07-types-pattern.md) | Types Pattern | Completed |
| [OBPI-0.25.0-08-ledger-pattern](OBPI-0.25.0-08-ledger-pattern.md) | Ledger Pattern | Completed |
| [OBPI-0.25.0-09-schema-pattern](OBPI-0.25.0-09-schema-pattern.md) | Schema Pattern | Completed |
| [OBPI-0.25.0-10-errors-pattern](OBPI-0.25.0-10-errors-pattern.md) | Errors Pattern | Completed |
| [OBPI-0.25.0-11-hooks-pattern](OBPI-0.25.0-11-hooks-pattern.md) | Hooks Pattern | Completed |
| [OBPI-0.25.0-12-admission-pattern](OBPI-0.25.0-12-admission-pattern.md) | Admission Pattern | Completed |
| [OBPI-0.25.0-13-qc-pattern](OBPI-0.25.0-13-qc-pattern.md) | QC Pattern | Completed |
| [OBPI-0.25.0-14-os-pattern](OBPI-0.25.0-14-os-pattern.md) | OS Pattern | Completed |
| [OBPI-0.25.0-15-manifests-pattern](OBPI-0.25.0-15-manifests-pattern.md) | Manifests Pattern | Completed |
| [OBPI-0.25.0-16-config-pattern](OBPI-0.25.0-16-config-pattern.md) | Config Pattern | Completed |
| [OBPI-0.25.0-17-console-pattern](OBPI-0.25.0-17-console-pattern.md) | Console Pattern | Completed |
| [OBPI-0.25.0-18-adr-lifecycle-pattern](OBPI-0.25.0-18-adr-lifecycle-pattern.md) | ADR Lifecycle Pattern | Completed |
| [OBPI-0.25.0-19-adr-audit-ledger-pattern](OBPI-0.25.0-19-adr-audit-ledger-pattern.md) | ADR Audit Ledger Pattern | Completed |
| [OBPI-0.25.0-20-adr-governance-pattern](OBPI-0.25.0-20-adr-governance-pattern.md) | ADR Governance Pattern | Completed |
| [OBPI-0.25.0-21-adr-reconciliation-pattern](OBPI-0.25.0-21-adr-reconciliation-pattern.md) | ADR Reconciliation Pattern | Completed |
| [OBPI-0.25.0-22-adr-traceability-pattern](OBPI-0.25.0-22-adr-traceability-pattern.md) | ADR Traceability Pattern | Completed |
| [OBPI-0.25.0-23-artifact-management-pattern](OBPI-0.25.0-23-artifact-management-pattern.md) | Artifact Management Pattern | Completed |
| [OBPI-0.25.0-24-cli-audit-pattern](OBPI-0.25.0-24-cli-audit-pattern.md) | CLI Audit Pattern | Completed |
| [OBPI-0.25.0-25-docs-validation-pattern](OBPI-0.25.0-25-docs-validation-pattern.md) | Documentation Validation Pattern | Completed |
| [OBPI-0.25.0-26-drift-detection-pattern](OBPI-0.25.0-26-drift-detection-pattern.md) | Drift Detection Pattern | Completed |
| [OBPI-0.25.0-27-policy-guards-pattern](OBPI-0.25.0-27-policy-guards-pattern.md) | Policy Guards Pattern | Completed |
| [OBPI-0.25.0-28-layout-verification-pattern](OBPI-0.25.0-28-layout-verification-pattern.md) | Layout Verification Pattern | Completed |
| [OBPI-0.25.0-29-ledger-schema-pattern](OBPI-0.25.0-29-ledger-schema-pattern.md) | Ledger Schema Pattern | Completed |
| [OBPI-0.25.0-30-references-pattern](OBPI-0.25.0-30-references-pattern.md) | References Pattern | Completed |
| [OBPI-0.25.0-31-validation-receipts-pattern](OBPI-0.25.0-31-validation-receipts-pattern.md) | Validation Receipts Pattern | Completed |
| [OBPI-0.25.0-32-handoff-validation-pattern](OBPI-0.25.0-32-handoff-validation-pattern.md) | Handoff Validation Pattern | Completed |
| [OBPI-0.25.0-33-arb-analysis-pattern](OBPI-0.25.0-33-arb-analysis-pattern.md) | ARB Analysis Pattern | Completed |

## Defense Brief

### Closing Arguments

#### OBPI-0.25.0-01-attestation-pattern

airlineops's `core/attestation.py` (511 lines) implements AIRAC-cycle-based attestation and ceremony ledgers using Pydantic models and JSONL append-only storage. gzkit's attestation surface (~2000+ lines across 10+ modules) provides multi-level attestation (ADR + OBPI), structured REQ-proof evidence, a composite state machine with drift detection, transactional OBPI completion with rollback, and an 11-step ceremony pipeline. Every generic pattern in airlineops is already subsumed by gzkit. The remaining airlineops-specific constructs (AIRAC cycle organization, operational attestation responses, world-state and contract hashing) are airline-domain-specific and correctly excluded from absorption. **Decision: Confirm.**

#### OBPI-0.25.0-02-progress-pattern

gzkit's progress infrastructure (`cli/progress.py` and `cli/formatters.py ProgressContext`) already surpasses airlineops's `core/progress.py` on every dimension that matters for a governance CLI toolkit: output-mode integration, context-manager API, TTY fallback, stderr discipline, and architectural UTF-8 handling. The airlineops module's domain-specific helpers (warehouse progress, download progress, SQLite heartbeat) fail the subtraction test — they are airline-specific patterns, not reusable infrastructure. The imperative `ProgressManager` facade is less Pythonic than gzkit's existing context managers. No absorption is warranted; gzkit's implementation is the stronger pattern.

#### OBPI-0.25.0-03-signature-pattern

airlineops's `core/signature.py` (365 lines) computes dataset signatures for airline-specific dataset families using `DatasetFamily` literal types (bts_db1b, bts_db28dm, bts_asqp, bts_db10, bts_db20, faa, exog), 6 family-specific character extractors, catalog loading from `data/datasets/`, and prefix-based family detection. Every construct beyond two trivial utility functions (`_compute_fingerprint` — JSON sort_keys + SHA256, `_timestamp_utc` — UTC ISO format) is tied to airline dataset semantics. gzkit has no dataset signature use case and no existing hashlib usage. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**

#### OBPI-0.25.0-04-world-state-pattern

airlineops's `core/world_state.py` (275 lines) defines world-state identity for AIRAC-orchestrated warehouse pipelines using `WorldState` with airline-specific fields (`airac_cycle`, `contract_hash`, `manifest_hash`, `contract_id`, `manifest_root`), queries the airline registrar (`get_active_contract`, `get_active_manifest_root`), scans airline manifest directories for `.manifest.json` files with dataset fields (`dataset_id`, `contract_hash`, `periods`, `package_names`), and computes semantic no-op detection for warehouse pipeline transitions. Every significant construct beyond ~36 lines of trivial generic primitives (frozen Pydantic model with hash-based equality, deterministic JSON→SHA-256, single-line hash comparison) is tied to airline domain semantics. gzkit has no content-addressable snapshot use case, no `hashlib` usage, and its architectural boundaries indicate state doctrine must be locked before building state-tracking infrastructure. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**

#### OBPI-0.25.0-05-dataset-version-pattern

airlineops's `core/dataset_version.py` (246 lines) defines content-addressable dataset version identity for airline data pipelines using `DatasetVersion` with airline-specific fields (`dataset_id` for BTS/FAA datasets, `source_version` for archive releases, `schema_version` and `etl_version` for ETL pipeline components, `content_hash` for processed output, `version_hash` as composite identity). The factory function `create_dataset_version()` composes these airline-specific components into a deterministic identity hash. The serialization helpers are thin Pydantic wrappers that gzkit already uses by convention. Every significant construct beyond ~33 lines of trivial generic primitives (SHA-256 content hashing, deterministic JSON serialization, frozen Pydantic with hash-based equality, semver/hash format validators) is tied to airline data pipeline semantics. The brief's premise that `lifecycle.py` provides "partial coverage" is incorrect — `lifecycle.py` implements governance artifact state transitions, a completely different concern with zero functional overlap. gzkit has no `hashlib` usage, no content-addressable versioning use case, and no dataset identity requirement. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**

#### OBPI-0.25.0-06-registry-pattern

airlineops's `core/registry.py` (86 lines) defines a `StrategyRegistry` that resolves callable strategy functions from airline profile descriptors using `StrategySpec` (`@dataclass(frozen=True)` with `name`, `fn`, `description`). The convenience getters — `get_bank_window_strategy()`, `get_seasonality_strategy()`, `get_seat_trim_strategy()`, `get_export_hook()` — and the `resolve_strategies()` profile mapper are airline schedule optimization concepts with no governance analogue. gzkit's `ContentTypeRegistry` (217 lines) already implements a more sophisticated registry with Pydantic `ContentType` models, frontmatter validation via `validate_artifact()`, lifecycle states, schema integration, canonical path patterns, and vendor rendering rules across 8 registered governance content types. The two registries share only the generic register/get/list boilerplate (~15 lines), which gzkit already has. The subtraction test is unambiguous: removing gzkit from this module leaves pure airline domain code — strategy resolution for bank windows, seasonality, seat trim, and export hooks. **Decision: Exclude.**

#### OBPI-0.25.0-07-types-pattern

airlineops's `core/types.py` (40 lines) defines a single `LoadResult` dataclass tracking airline dataset load operation results with 15 fields. Every field is an airline ETL pipeline concept: `dataset` and `period` identify the airline dataset and time window, `sqlite_path`/`staging_table`/`plain_table` map to the airline data warehouse schema, `rows_staging`/`rows_curated` count ETL throughput, `parquet_path` references columnar export artifacts, `transport`/`write_mode` control data movement, and `inserted`/`updated`/`dedup_dropped` track mutation counts. The module's docstring confirms its origin: "Extracted from warehouse ingest module to avoid tight coupling and support upcoming modularization." The module uses `@dataclass` rather than Pydantic `BaseModel`, violating gzkit's data model policy. gzkit has no types module, no `LoadResult` equivalent, no ETL/data pipeline use case, and no warehouse infrastructure. There are zero generic constructs to extract. The subtraction test is unambiguous: this is pure airline domain code. **Decision: Exclude.**

#### OBPI-0.25.0-08-ledger-pattern

airlineops's `core/ledger.py` (91 lines) is a thin facade that re-exports four functions from `airlineops.warehouse.ingest.ledger`: `resolve_period_path`, `append_event`, `append_load_event`, and `append_error_event`. Every function deals exclusively with airline warehouse ingest concepts — datasets, periods, base months, load results, ETL error events. The facade contains zero logic; it delegates entirely to the ingest subsystem. gzkit's `ledger.py` (598 lines) plus three sub-modules (`ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`) implements a fundamentally different system: an append-only JSONL governance event ledger with `LedgerEvent` Pydantic models, schema validation, artifact graph construction, rename chain resolution, attestation tracking, closeout lifecycle, and OBPI receipt management. The two modules share only the name "ledger" — their domains, data models, and operational semantics are entirely disjoint. The subtraction test is unambiguous: removing gzkit from the airlineops module leaves a pure airline warehouse ingest facade with no generic patterns worth extracting. **Decision: Exclude.**

#### OBPI-0.25.0-09-schema-pattern

The airlineops `core/schema.py` module provides SQLite DDL helpers for the data
warehouse JSONL-to-SQL ingestion pipeline. gzkit's `schemas/__init__.py` serves
an entirely different purpose: loading JSON Schema files for governance artifact
validation. These modules share no functional overlap. The airlineops module is
used in exactly one place (the warehouse loader), has no governance application,
and introduces a dependency (sqlite3) that gzkit does not use. **Decision:
Exclude** — this is pure airline-domain infrastructure that correctly remains in
airlineops.

#### OBPI-0.25.0-10-errors-pattern

airlineops's `core/errors.py` (53 lines) is a thin UI error rendering facade — not an exception hierarchy as described in the ADR. The module wraps `render_error_panel` from `airlineops.warehouse.bootstrap.common`, taking airline-specific parameters (`dataset` for BTS/FAA dataset names, `period` for data periods, `phase` for processing phases, `exc` for the caught exception) and rendering Rich error panels for warehouse dataset processing failures. It exports only `render_error_panel` and defines zero exception classes, zero error classification, and zero reusable error-handling patterns. gzkit already has `src/gzkit/core/exceptions.py` (96 lines) — a well-structured typed exception hierarchy with six exception classes (`GzkitError`, `ValidationError`, `ResourceNotFoundError`, `PermanentError`, `OperatorError`, `TransientError`, `PolicyBreachError`), exit-code classification aligned to the CLI Standard 4-Code Map, and additional domain exceptions (`GzCliError`, `DatasetValidationError`) in other modules. The subtraction test is unambiguous: every parameter, every delegation target, and every fallback path in the airlineops module is airline-domain-specific. There are no reusable exception patterns to absorb. **Decision: Exclude.**

#### OBPI-0.25.0-11-hooks-pattern

airlineops's `core/hooks.py` (34 lines) is a minimal callback registry for dataset-specific post-load pipeline hooks in the airline data warehouse. The module provides two functions — `register_hook(dataset, name, fn)` and `get_hook(dataset, name)` — backed by a module-level dict keyed by `(dataset_name, hook_name)`. Its only documented usage is in `warehouse/ingest/loader/load_operations.py`, where the `"post_load"` hook runs optional callbacks after airline dataset curation and ledger append. The `dataset` parameter refers to airline datasets (BTS, FAA), and the hook lifecycle is tied to the warehouse ingest pipeline.

gzkit's `hooks/` package (10 files, 482 lines in `core.py` alone) is a comprehensive governance enforcement system providing artifact edit recording with ledger integration, OBPI completion validation gates, evidence enrichment with scope audit and git-sync state, hook script generation for Claude Code and Copilot agents, policy guards, and pipeline gates. These modules share a filename but serve fundamentally different domains — airline data loading callbacks versus governance lifecycle enforcement. The airlineops pattern (register/get from a dict) is trivially generic Python, not infrastructure worth absorbing. The subtraction test is unambiguous: every usage context in airlineops is tied to airline data loading semantics. There are no reusable hook patterns to absorb. **Decision: Exclude.**

#### OBPI-0.25.0-12-admission-pattern

The airlineops `core/admission.py` module provides a single-function facade for
resolving YYYY-MM period tokens via the warehouse cadence configuration. Despite
the generic-sounding module name "admission", the implementation is a 34-line
wrapper around `airlineops.warehouse.ingest.config.cadence.closest_admitted` with
no generic admission control semantics. gzkit has no warehouse, no cadence
configuration, and no period resolution needs. **Decision: Exclude** — this is
pure airline-domain data pipeline infrastructure that correctly remains in
airlineops.

#### OBPI-0.25.0-13-qc-pattern

airlineops's `core/qc.py` (18 lines) is a thin facade that re-exports `run_integrity()` from `airlineops.reporter.reports.integrity_check` for warehouse data integrity checks. It takes airline-domain-specific parameters (`dataset`, `db_path`) and has zero conceptual overlap with gzkit's `quality.py` (773 lines), which provides code quality infrastructure: lint, format, typecheck, test orchestration, AST-based custom lint rules, drift advisory, product proof gates, and eval harness. The "QC" label in airlineops refers to operational quality control (data integrity), not code quality. No reusable patterns exist in the 18-line facade — the subtraction test is definitive. **Decision: Exclude.**

#### OBPI-0.25.0-14-os-pattern

airlineops's `common/os.py` (241 lines) provides UNC/SMB network share handling: `iter_mounts()` enumerates macOS `/Volumes/` mount points, `parse_unc_share()` and `UncShare` parse Windows UNC paths into server/share/remainder triples, `resolve_unc_mount()`/`resolve_unc_path()`/`normalize_unc_path()` resolve and normalize UNC paths to mounted local paths, and `refresh_macos_guest_smb_mount()` refreshes macOS SMB mounts via subprocess calls to `diskutil`, `umount`, and `mount_smbfs`. Every function beyond two trivial platform detection helpers (`is_macos()`, `is_windows()`) serves a deployment scenario where airline servers are accessed via SMB shares on macOS workstations. gzkit works with local files, has no UNC/SMB use case, and its cross-platform needs are comprehensively addressed by `pathlib.Path`, UTF-8 encoding policy, and the existing cross-platform development rule. The subtraction test is unambiguous: this module is pure deployment-environment infrastructure. **Decision: Exclude.**

#### OBPI-0.25.0-15-manifests-pattern

OBPI-0.25.0-15 evaluated airlineops `common/manifests.py` (89 lines) against gzkit's manifest handling across six dimensions: purpose, core function, data model, error handling, cross-platform robustness, and dependencies. The subtraction test conclusively identifies the module as domain-specific: removing airline concerns leaves only trivial SHA256 + JSON primitives previously Excluded in OBPI-0.25.0-03. gzkit's existing Pydantic-based manifest loading and structured validation are more sophisticated for their governance purpose. Decision: **Exclude**.

#### OBPI-0.25.0-16-config-pattern

Configuration loading is definitively generic infrastructure, and gzkit's `config.py` already owns the pattern comprehensively. The Pydantic-based typed model architecture with frozen immutability, `extra="forbid"` validation, and 3-layer precedence (defaults -> file -> CLI) strictly supersedes airlineops's untyped `dict[str, Any]` approach with `_deep_merge`. No airlineops pattern — deep merge, local override file, or broad error catching — adds value that gzkit does not already deliver through stronger architectural means. **Decision: Confirm.**

#### OBPI-0.25.0-17-console-pattern

airlineops's `common/console.py` (45 lines) is a `create_console()` factory that detects terminal encoding on Windows via `sys.stdout.encoding` and configures Rich's `legacy_windows` flag to toggle between full Unicode and ASCII fallback. gzkit handles the same concern with a stronger two-layer approach: `_ensure_utf8_console()` in `cli/main.py:93-100` reconfigures both stdout and stderr to UTF-8 at startup — before any Rich output — which forces UTF-8 at the OS stream level rather than adapting per-Console instance. The module-level Console singleton in `commands/common.py:30-33` adds `NO_COLOR` and `FORCE_COLOR` environment variable support that airlineops lacks. Once `_ensure_utf8_console()` runs, the encoding detection in airlineops's factory becomes redundant — Rich sees a UTF-8 stream regardless of the original terminal encoding. The airlineops factory pattern (new Console per call) is appropriate for multi-Console applications but unnecessary for gzkit's CLI where a single shared Console serves all commands. **Decision: Confirm.**

#### OBPI-0.25.0-18-adr-lifecycle-pattern

airlineops's `opsdev/lib/adr.py` (1603 lines) is a monolithic module that combines ADR discovery, index generation, status table generation, title normalization, reconciliation, drift detection, and Rich Console rendering. It derives ADR state from regex-based markdown file parsing — extracting status, dates, titles, and superseded-by references from markdown body text and generating static artifacts (`adr_index.md`, `adr_status.md`). gzkit's ADR lifecycle surface (~1300+ lines across `registry.py`, `sync.py`, `commands/register.py`, `core/models.py`, `ledger.py`, and `commands/adr_report.py`) is architecturally superior in a fundamental way: state is derived from an append-only ledger (JSONL event log), not parsed from variable markdown formatting. This gives gzkit a composite state machine with 7 runtime states, ledger-based reconciliation with receipt verification, dynamic status views that cannot drift from source-of-truth, Pydantic-validated frontmatter via a content type registry, a 5-gate governance system with per-gate tracking, and transactional OBPI completion with rollback. The monolithic airlineops module conflates discovery, parsing, rendering, and reconciliation — concerns that gzkit correctly separates. airlineops's static index generation directly contradicts gzkit's Architectural Boundary #6: "Do not let derived views silently become source-of-truth." **Decision: Confirm.**

#### OBPI-0.25.0-19-adr-audit-ledger-pattern

**Confirm.** airlineops's `adr_audit_ledger.py` is a 249-line Layer 2
Gate 5 completeness checker that reads a local `obpi-audit.jsonl` to
classify briefs as missing, incomplete, or complete. gzkit's audit surface
(`adr_audit_check` + `validate_ledger` + `obpi_audit_cmd`, ~800+ lines)
already covers this capability and surpasses it: central ledger graph
instead of local audit file, brief content inspection instead of status-only
checks, and `@covers` REQ traceability verification. The airlineops module
uses stdlib `dataclass` and depends on `adr_recon` helpers — absorbing it
would require a full rewrite with no net capability gain.

#### OBPI-0.25.0-20-adr-governance-pattern

**Confirm.** airlineops's `adr_governance.py` is a 535-line module providing
evidence audit, autolink, and verification report capabilities via regex-based
parsing, stdlib dataclass models, and auto-writing Verification sections into
ADR files. gzkit's governance surface (`traceability.py` + `covers.py` +
`adr_audit.py`, ~1010 lines) already covers and surpasses all three
capabilities: AST-based scanning instead of regex, Pydantic models with
runtime REQ validation instead of stdlib dataclass, multi-level coverage
rollups (ADR/OBPI/REQ) instead of flat mapping, and brief content inspection
via the central ledger graph instead of section-presence checks. The
auto-writing feature is specific to airlineops's older workflow and
intentionally not used in gzkit's OBPI-based governance model.

#### OBPI-0.25.0-21-adr-reconciliation-pattern

gzkit's reconciliation surface (`ledger_semantics.py`, `ledger_proof.py`, `obpi_reconcile_cmd`, `_build_adr_status_result`, and `parse_wbs_table`) already surpasses airlineops's `adr_recon.py` on every dimension that matters for a governance toolkit: central event-sourced ledger architecture, rich per-OBPI state derivation with anchor analysis and scope drift, per-OBPI auto-fix reconciliation, and ADR-level aggregation with lifecycle and closeout readiness. The airlineops module's signature capability — writing ledger-derived status back to ADR markdown tables — would violate gzkit's state doctrine by making derived views (L3) masquerade as source-of-truth (L1). gzkit's design computes views on demand from the central ledger, which is architecturally correct and more maintainable. No absorption is warranted; gzkit's implementation is the stronger pattern.

#### OBPI-0.25.0-22-adr-traceability-pattern

gzkit's traceability surface (`triangle.py` at 372 lines and `traceability.py` at 418 lines — 790+ lines total) surpasses airlineops's heuristic inference module (`adr_traceability.py` at 277 lines) on every governance-relevant dimension. The `@covers` decorator provides auditable, precise test-to-REQ linkage; `compute_coverage()` delivers structured multi-level rollups at REQ, OBPI, and ADR levels; `detect_drift()` catches unlinked specs and orphan tests proactively. The airlineops module's unique capability — heuristic keyword scoring — produces fuzzy confidence values unsuitable for governance compliance, and its domain-specific bonuses (`econ`, `ops`, `market`, `qsi`, `gravity`, `shares`) fail the subtraction test. gzkit's `gz-adr-map` skill and `gz state --json` command provide governance-aware ADR-to-artifact mapping through the central ledger, replacing the need for heuristic inference. No absorption is warranted; gzkit's implementation is the stronger pattern.

#### OBPI-0.25.0-23-artifact-management-pattern

airlineops's `opsdev/lib/artifacts.py` (232 lines) provides two capabilities: (1) regex-based scanning of Python source files for `artifacts/` path references and `.sqlite` file references, with usage classification as read/write/mkdir/other via context-aware pattern matching (`open()`, `Path()`, `os.makedirs()`, `shutil.*`); and (2) artifact directory cleanup based on a JSON registry allowlist (`config/artifacts_registry.json`) with hardcoded preserved files (`live_ingest_report.json`, `attestations/`). gzkit's artifact management surface (`registry.py`, 220 lines, + `sync.py` scanning utilities) provides governance content type metadata — Pydantic-modeled type definitions with frontmatter validation, lifecycle states, and canonical path patterns — plus governance artifact discovery via rglob and frontmatter extraction. The modules solve fundamentally different problems with zero functional overlap. The airlineops module uses `@dataclass` (gzkit requires Pydantic) and `shutil.rmtree(ignore_errors=True)` (violates gzkit cross-platform policy). The subtraction test is unambiguous: removing gzkit from airlineops leaves physical file management tied to airlineops's `artifacts/` directory convention. **Decision: Exclude.**

#### OBPI-0.25.0-24-cli-audit-pattern

gzkit's CLI audit surface spans `commands/cli_audit.py` (226 lines) plus the `doc_coverage/` package (~802 lines across 4 modules), providing AST-driven command discovery without private API access, 5-surface documentation coverage (manpage, index_entry, operator_runbook, governance_runbook, docstring), manifest-driven obligations covering 50+ commands via `config/doc-coverage.json`, README Quick Start validation against the live parser, and orphaned documentation detection — backed by 76 tests across 3 files. airlineops's `opsdev/lib/cli_audit.py` (238 lines) provides parser-internal structural consistency checking: `extract_all_arguments()` walks `parser._actions` to extract argument metadata, `audit_parser()` recursively traverses subparsers via `argparse._SubParsersAction`, and `analyze_consistency()` checks naming conventions and cross-command option conflicts. The airlineops module's unique capabilities — naming convention enforcement and cross-command option conflict detection — solve a narrower problem that gzkit's documentation-coverage approach already subsumes in practice: gzkit validates handler docstrings, command syntax via README parsing, and enforces per-surface obligations declaratively rather than through fragile `parser._actions` introspection. With 76 tests vs 1, frozen Pydantic models vs untyped dicts, and manifest-driven obligations vs ad-hoc checks, gzkit's approach is architecturally superior. **Decision: Confirm.**

#### OBPI-0.25.0-25-docs-validation-pattern

gzkit's documentation coverage surface spans the `doc_coverage/` package (802 lines across `scanner.py`, `models.py`, `manifest.py`, `runner.py`), providing AST-driven CLI command discovery without import or execution, 5-surface documentation coverage per command (manpage, index_entry, operator_runbook, governance_runbook, docstring), manifest-driven obligations via `config/doc-coverage.json` declaring 50+ commands with per-surface boolean toggles and exemption support, structured `DocCoverageGapReport` output with both human-readable and JSON formats, and orphaned manpage detection for files with no matching discovered command — backed by 87 tests across 3 dedicated test modules. airlineops's `opsdev/lib/docs.py` (218 lines) provides a fundamentally different and explicitly temporary surface: a single existence check for `docs/index.md` (`check_files`), a subprocess wrapper around `python -m mkdocs build --strict` (`build_site_strict`), and a regex-based markdown link validator with 2-click reachability orphan detection (`parse_links`, `build_graph`, `find_orphans`, `validate_links`, `docs_link_lint`). The module's own docstring labels it an "ultra-minimal Docs gate during 0.0.0 -> 1.0.0 remodel" with explicit TODOs to restore its deep checks. Its link validation capability — the only non-trivial piece — is already solved natively by `mkdocs build --strict`, which gzkit uses in CI and as part of `gz validate --documents`. The remainder (`check_files`, `build_site_strict`) is subsumed by existing gzkit commands. With 87 tests vs a dedicated test module that does not exist, frozen Pydantic models vs plain dict/set/list primitives, manifest-driven obligations vs hardcoded ad-hoc checks, and AST-based CLI coverage vs `sys.exit`-coupled structural stubs, gzkit's approach is architecturally superior in every comparable dimension. Nothing in airlineops `docs.py` is both unique and non-redundant. **Decision: Confirm.**

#### OBPI-0.25.0-26-drift-detection-pattern

gzkit's governance ledger has captured a `{"commit": <short-7>, "tag": <tag>,
"semver": <X.Y.Z>}` anchor inside every `audit_receipt_emitted` and
`obpi_receipt_emitted` event for months, via
`capture_validation_anchor_with_warnings()` in `src/gzkit/utils.py:64-95`. The
data is real — `grep '"anchor"' .gzkit/ledger.jsonl` returns concrete entries
like `{"commit": "19f5230", "semver": "0.7.0"}`. But no detector has ever
read that data back. Operators have had no way to ask "this ADR was validated
weeks ago — is the validation still meaningful at HEAD?" The answer has lived
on disk, unread, since the first anchored receipt was written.

airlineops's `opsdev/lib/drift_detection.py` (384 lines) is the textbook
implementation of exactly that detector. It is a two-layer pure-plus-orchestrator
design: a pure `classify_drift()` function that takes git results as
arguments and returns a frozen Pydantic `DriftResult`, plus thin orchestrators
(`detect_drift`, `detect_obpi_drift`) that perform the I/O and delegate to the
classifier. Every choice in the module — `ConfigDict(extra="forbid", frozen=True)`,
explicit `encoding="utf-8"`, list-form subprocess calls, three-state
`Literal["none", "commits_ahead", "diverged"]` classification with
`commit not found in repo` collapsed into `diverged` — is already a gzkit
convention. The subtraction test passes cleanly: nothing in the module is
airline-domain. Everything operates over git plus a generic validation-receipt
schema gzkit already maintains.

Two integration deltas emerged during absorption and were resolved
mechanically inside the orchestrators while leaving the pure classifier
unchanged. **First**, gzkit stores anchors as **short SHA-7**
(`git rev-parse --short=7 HEAD`), while airlineops compares full SHAs;
`classify_drift`'s `anchor_commit == head_commit` check would never match
short-vs-full. The fix is one helper, `_resolve_full_commit(short)`, that
runs `git rev-parse <short>` and either returns the full SHA or returns
`None` (which the orchestrator threads into `is_ancestor_result=None`,
producing the correct `diverged: anchor commit X not found in repository
history` classification for free). **Second**, airlineops reads per-ADR
`validation-ledger.jsonl` and per-ADR `obpi-audit.jsonl` files inside each
ADR folder; gzkit uses a single event-sourced `.gzkit/ledger.jsonl` filtered
by event type and `id` (or `parent` for OBPI events). The orchestrators in
`temporal_drift.py` use `gzkit.ledger.Ledger.query()` to filter
`audit_receipt_emitted` and `obpi_receipt_emitted` events, walk in reverse
to find the most recent anchored entry per artifact, and pass the result
into the unchanged classifier. The pure classifier is byte-equivalent to
airlineops's; it never had to know about either delta.

Subprocess calls go through `gzkit.utils.git_cmd()` rather than
direct `subprocess.run()`, sharing gzkit's HEAD cache, encoding, and
error-capture conventions. This is the only structural deviation from the
upstream module and it *removes* duplication rather than adding it. The new
module is intentionally library-only — `src/gzkit/temporal_drift.py` is
importable but exposes no CLI surface. Wiring it into a `gz drift --temporal`
or `gz validate --drift` mode is a follow-on OBPI; this brief stays narrow
and the absorbed module ships behind a stable, tested public API
(`DriftStatus`, `DriftResult`, `ObpiDriftResult`, `classify_drift`,
`detect_drift`, `detect_obpi_drift`).

The absorbed module lives at `src/gzkit/temporal_drift.py`, deliberately
separate from `gzkit.triangle` and `gzkit.commands.drift`. The two `drift`
concerns share no state, no functions, and no types. Triangle drift answers
"is the spec/test/code triangle structurally consistent?" Temporal drift
answers "has the codebase moved since validation?" They are orthogonal,
they are now both supported, and they can be wired into the same operator
surface in a future OBPI without coupling. **Decision: Absorb.**

#### OBPI-0.25.0-27-policy-guards-pattern

Both `opsdev/lib/guards.py` and `src/gzkit/hooks/guards.py` scan text files
for pytest usage and reject it. The two files share byte-identical regex
patterns, scan-extension sets, conftest/pyproject short-circuits, and exit
code semantics. They are convergent forks of the same intent. Where they
differ, gzkit has already chosen the better public shape: `forbid_pytest`
takes the scan root as a parameter, not as `Path(__file__).resolve().parents[3]`,
because gzkit removed that anti-pattern in OBPI-0.0.7-04 under
ADR-0.0.7 (config-first-resolution-discipline). A full Absorb that replaced
gzkit's module with airlineops's would erase that governance work. A full
Confirm that kept gzkit unchanged would leave two concrete improvements on
the table — one from airlineops, one exposed by writing the first real
tests for this module.

The airlineops improvement is a seven-line helper called `_safe_print` that
wraps `print(s)` in a `try` / `except UnicodeEncodeError` with an
`s.encode("ascii", "backslashreplace").decode("ascii")` fallback. The
helper exists because `opsdev/lib/guards.py` is invoked outside the CLI
UTF-8 guard, and on Windows cp1252 terminals a finding line that
interpolates a non-ASCII file path or violation text would otherwise crash
the pre-commit hook. gzkit's own `.pre-commit-config.yaml:40` invokes
`uv run -m gzkit.hooks.guards` — the same bypass path. gzkit's
`cross-platform.md` rule explicitly warns about this class of terminal
encoding failure, and the existing gzkit scanner had no defense against it.
The helper is narrow, dependency-free, and strictly additive; the fast
path is unchanged and the fallback fires only where direct `print` would
have raised.

Writing the first test file for `hooks/guards.py` caught a second, latent
defect that was shared by both codebases. `iter_files(root)` documents
`EXCLUDE_DIRS = {".git", ".venv", ...}` as the directory-level exclusion
list, but uses `root.rglob("*")` without pruning descendants. The
`if p.is_dir(): continue` branch only skips the directory *entry*; rglob
walks inside it anyway. A test that planted `.git/hidden.py` under a temp
root and asserted the scanner did not yield it failed on the existing code.
Real gzkit check-outs had never hit the bug in practice because
`EXCLUDE_PATH_SNIPPETS` caught the `.venv/`, `venv/`, `build/`, `dist/`
cases via full-posix matching — but `.git` was not in snippets and was only
protected by the ineffective `EXCLUDE_DIRS` check. Per gzkit's test policy
("flag defects, never excuse them"), the defect could not be rationalized
as pre-existing and had to be fixed in-place. The fix is a four-line
ancestor-parts check against `EXCLUDE_DIRS` before yielding; no API change,
no behavior change on any finding that would have been reported before.

The final shape of the absorption is three changes to `src/gzkit/hooks/guards.py`:
(1) add the `_safe_print` helper; (2) route the two dynamic-content print
calls in `forbid_pytest` (the `- {path}` line and the `    {violation}`
line) through `_safe_print`; (3) add the ancestor-prune check to
`iter_files`. Static header and footer prints are left as plain `print`
because they are ASCII-safe by construction and their `# noqa: T201`
annotations are intentional documentation that the scanner talks to
stdout. `forbid_pytest(root: Path)` signature is untouched. `main()` still
calls `forbid_pytest(Path.cwd())`. The single TDD test file
`tests/test_hooks_guards.py` covers seven test classes: `TestIterFiles`
(4 tests including the directory-prune regression), `TestScanFileSourceLevel`
(7 table-driven pattern-detection tests), `TestScanFileSpecialCases`
(6 tests for conftest, pyproject, and requirements detection),
`TestScanFileReadError` (1 test for OSError fallback), `TestForbidPytest`
(4 integration tests including clean root, bad .py, conftest, and
pyproject), `TestSafePrint` (3 tests including the cp1252 fallback path
exercised via a `gzkit.hooks.guards.print` mock that raises on `\u2713`),
and `TestMain` (1 test that patches `Path.cwd`). Coverage goes from zero
(no test file existed) to ~92% of the module. **Decision: Absorb.**

#### OBPI-0.25.0-28-layout-verification-pattern

airlineops's `opsdev/lib/layout_verify.py` (143 lines) provides a single
capability: validating that a repo's tree layout matches an airline-specific
`config/governance/tree_layout.json` file with six hardcoded root keys
(`source_root`, `config_root`, `data_root`, `artifacts_root`, `docs_root`,
`ops_tooling_root`) and a trailing semantic check for an "opsdev package"
under the tooling root. That file does not exist in gzkit, and the root
names do not match gzkit's `GzkitConfig.paths` shape. gzkit's layout
verification surface — `src/gzkit/commands/config_paths.py` (310 lines) +
`src/gzkit/validate_pkg/manifest.py` (116 lines) — is architecturally
superior: it performs schema-driven manifest validation via
`load_schema("manifest")` with typed `ValidationError` results, checks
required directories and files from the typed `GzkitConfig` model,
enforces control-surface path types with explicit dir-vs-file
discrimination for ten named control surfaces, enforces the OBPI path
contract (rejecting deprecated global OBPI paths), and walks
`src/gzkit/**/*.py` with AST parsing to flag string constants looking
like filesystem paths but not covered by any manifest entry — a unique
capability airlineops lacks entirely. airlineops's module still uses
`Path(__file__).resolve().parents[3]` to derive repo root, exactly the
anti-pattern gzkit removed in OBPI-0.0.7-04 as part of ADR-0.0.7's
config-first resolution discipline; absorbing it wholesale would regress
prior governance work. The one isolated robustness helper —
`_is_within()` path escape check (7 lines) — addresses a threat model
that does not apply to gzkit, since config paths come from trusted
in-repo JSON loaded through `GzkitConfig` with schema validation, not
from user-supplied runtime input. Contrast this with OBPI-0.25.0-27,
where airlineops's `_safe_print` was a concrete Windows pre-commit crash
risk that narrowly justified Absorb; no equivalent narrow hardening
candidate exists here. The subtraction test is unambiguous: stripping
airline-specific pieces (tree_layout.json schema, hardcoded root names,
`_repo_root_from_here()`, opsdev package semantic check) leaves only
`_is_within()`, which solves a non-problem for gzkit. **Decision: Exclude.**

#### OBPI-0.25.0-29-ledger-schema-pattern

gzkit's ledger surface — `events.py` (470 L typed event models),
`ledger.py` (598 L `Ledger` class with append/read/query/graph), and
`schemas/ledger.json` (220 L per-event JSON schema) — is a functional
superset of airlineops's `opsdev/lib/ledger_schema.py` (501 L audit-only
schema) for the governance lifecycle ledger problem. Every capability
airlineops provides — discriminated typed unions, ID pattern validation,
nested evidence models, legacy entry handling, frozen models — gzkit
provides in richer form, over more entry types, with a persistence class
and derivation pipeline airlineops does not ship. Absorbing the airlineops
module would not add capability; it would add a parallel per-ADR storage
layout that conflicts with gzkit's Layer 2 state doctrine (CLAUDE.md
§ Architectural Boundaries item 6). More importantly, gzkit is governance
tooling that downstream projects adopt, while airlineops's
`ledger_schema.py` is a consumer-layer audit extension specific to
airlineops's operational needs — absorbing it would push a
consumer-layer storage assumption (per-ADR `logs/obpi-audit.jsonl`) into
the tooling layer, which is architecturally backwards for a framework
designed to leave storage layout decisions to its adopters. The
doctrinally-coherent outcome is to Exclude — treat airlineops's
audit-specific schema as a domain choice that made sense for its
per-ADR audit-log layout, and leave gzkit's lifecycle ledger
undisturbed.

#### OBPI-0.25.0-30-references-pattern

The capability airlineops's `references.py` hints at — curated
bibliography management for design references — is legitimately useful to
gzkit. gzkit has been running design reviews grounded in external
engineering literature (Anthropic's alignment and context-engineering
articles among them), and that body of material deserves a durable,
citable surface. But airlineops's specific 797-line implementation is the
wrong vehicle for that capability in gzkit. It is a PDF-scan pipeline:
`pypdf` metadata extraction, `docs/references/*.pdf` file-glob indexing,
APA *journal article* formatting, and a hardcoded
`ROSETTA_REFERENCES_LIST` of aviation-industry textbooks
(`references.py:56-63`) feeding a `docs/airlineops_rosetta_stone.md`
rewriter. gzkit's consumer pattern is URL-first, article-first, and
engineering-literature-first — none of which airlineops's machinery
serves. Absorbing the module would inflate `pyproject.toml` with
`pypdf`, import 797 lines that are mostly dead against gzkit's consumer
pattern, and commit gzkit to airlineops's format/layout choices before
gzkit has deliberated on its own. The doctrinally-coherent outcome is
Exclude *this specific implementation* and book the capability into a
dedicated follow-up:
`docs/design/adr/pool/ADR-pool.design-references-bibliography.md`. That
pool ADR captures the need at the right granularity — gzkit-native
design, seeded with material that has already grounded design reviews,
unburdened by a consumer project's implementation choices — and pulls
only the twelve-line `_replace_block()` marker pattern from airlineops
if it turns out to be useful, re-implemented in gzkit style. The
subtraction test fails here at a more precise granularity than the
initial framing suggested: the *capability* generalizes, the *specific
implementation* does not.

#### OBPI-0.25.0-31-validation-receipts-pattern

`airlineops/src/opsdev/lib/validation_receipt.py` is a 274-line library
module that defines a typed `ValidationAnchor`, a `ValidationReceipt`
extending a shared `LedgerEntryBase`, JSONL persistence, and a per-ADR
storage convention (`{adr-folder}/logs/adr-validation.jsonl`). gzkit
already implements every one of those capabilities — and substantially
more — across an ~1396-line distributed surface: `events.py` defines a
17+ entry discriminated union of lifecycle events whose
`ObpiReceiptEmittedEvent` and `AuditReceiptEmittedEvent` carry richly
typed `ObpiReceiptEvidence` payloads with nested `ScopeAudit`,
`GitSyncState`, and `ReqProofInput` models; `commands/obpi_complete.py`
performs an atomic three-step transaction (audit ledger entry + brief
content + main ledger receipt event) with `OSError` rollback;
`utils.capture_validation_anchor()` builds anchor data with graceful
degradation rather than raising; `temporal_drift.py` (already absorbed
via OBPI-0.25.0-26) consumes anchors from the central
`.gzkit/ledger.jsonl` to classify drift; and the surface is reached
operationally through `gz obpi complete`, `gz adr emit-receipt`, `gz obpi
reconcile`, and `gz adr status`. The single narrow place where airlineops
has more typing rigor — `ValidationAnchor` as a frozen Pydantic model
instead of gzkit's `anchor: dict[str, str] | None` — is structurally
entangled with every existing receipt event in the gzkit ledger, and
hardening it is a direct schema edit to gzkit that does not require
importing any airlineops code. The doctrinally-coherent outcome is
Confirm: gzkit's receipt surface is the canonical implementation of the
validation anchoring schema pattern, and absorbing 274 lines of a
parallel per-ADR storage system would contradict gzkit's central-ledger
doctrine instead of strengthening it. The subtraction test
(*if it is not airline-specific, it belongs in gzkit*) does not require a
copy when gzkit already owns the capability at greater fidelity. The
opportunity to type the anchor field on `events.py:362, 373` is a
refactor of an existing capability rather than a new feature, and is
tracked as a defect on the GHI track (gh#143) for future remediation —
scoped independently of this absorption decision.

#### OBPI-0.25.0-32-handoff-validation-pattern

OBPI-0.25.0-32 absorbs `airlineops/opsdev/governance/handoff_validation.py`
(312 lines) into `src/gzkit/handoff_validation.py` (320 lines after two
adaptations) and adds the missing `tests/governance/test_handoff_validation.py`
tree (54 tests, 8 classes, `@covers`-parity with REQ-01/02/03/05).

The decision is **Absorb** rather than Confirm or Exclude because gzkit had
already written the specification at `docs/governance/GovZero/handoff-validation.md`
describing this exact validator contract, while implementing **zero** of its
six fail-closed checks: `HandoffFrontmatter` Pydantic schema, placeholder scan,
secret scan, required-sections check, referenced-file existence, and the
fail-closed orchestrator. The generic `parse_frontmatter()` helper in
`core/validation_rules.py` returns a raw tuple and performs no schema
validation; it is not a handoff validator.

The absorbed module ships with near-zero adaptation cost. airlineops already
used Pydantic `BaseModel` with `ConfigDict(extra="forbid", frozen=True)`,
`pathlib.Path`, `from __future__ import annotations`, and module-level
`re.compile`. The only gzkit adaptations are: (a) dual `@covers` lineage in the
module docstring, preserving the original `@covers ADR-0.0.25 (OBPI-0.0.25-06)`
provenance and adding `@covers ADR-0.25.0 (OBPI-0.25.0-32)` absorption; and
(b) CRLF normalization (`content = content.replace("\r\n", "\n")`) as the
first executable statement in every public validator function, as required by
`.gzkit/rules/cross-platform.md` for any content flowing through `re.MULTILINE`
patterns on Windows hosts.

Gate 4 (BDD) is **N/A** with explicit rationale: the absorbed module is a
**library function only** — it is not wired into any CLI surface in this OBPI.
`gz validate --documents --surfaces` continues to route through
`validate_pkg/document.py`; wiring `validate_handoff_document()` into that
command path is a future integration task with its own OBPI. Because there is
**no operator-visible CLI surface change** and **no external-surface change**,
no behavioral proof is required.

A notable provenance artifact of this OBPI is the **Comparison Target
Correction** section above. The brief's original "gzkit equivalent" pointer
at `pipeline_dispatch.py / lock_manager.py / interview_cmd.py` was factually
incorrect — those modules handle pipeline dispatch, work-lock management, and
interactive interview flows, not handoff-document validation. The Stage 1
subagent sweep surfaced the discrepancy; the corrected comparison target (spec
doc present, implementation absent) is what the decision rationale is grounded
in. The incorrect pointer is preserved in the brief so future readers can
trace the provenance of the correction.

Post-absorption state: ADR-0.25.0 moves from 31/33 to 32/33 OBPIs complete.
Only `OBPI-0.25.0-33-arb-analysis-pattern` remains before closeout.

#### OBPI-0.25.0-33-arb-analysis-pattern

`airlineops/src/opsdev/arb/` is a ~1039-line package across seven core files (`advise.py`, `validate.py`, `patterns.py`, `paths.py`, `ruff_reporter.py`, `step_reporter.py`, `__init__.py`) that implements agent self-reporting middleware — wrap any QA command, emit a schema-validated JSON receipt, aggregate recent receipts into actionable lint-pattern guidance. gzkit had none of this: `uv run gz arb` was an invalid CLI choice, `data/schemas/arb_*.json` did not exist, `src/gzkit/arb/` was not a package. And yet `.gzkit/rules/arb.md` v1.0 Active documented the full seven-verb surface, and `.claude/rules/attestation-enrichment.md` hardened its receipt-ID requirement to fail-closed for Heavy-lane attestations — a rule contract the repository could not fulfill.

The forensic trace is unambiguous: a control-surface regeneration on 2026-03-15 (commit `37c891ca`) copied the airlineops arb rule wholesale into gzkit, a mechanical find-and-replace on 2026-03-18 (commit `4700b623`) rewrote `opsdev` → `gzkit` in an auto-commit whose message carried no semantic signal, and the attestation-enrichment hardening (commits `4c7573fc`, `f350cf44`) was written against the phantom surface without verification. The later 2026-04-03 skill consolidation marked `gz-arb` as retired/"consolidated into gz-check" — but `gz check` never implemented any of it. The consolidation was nominal; the drift was substantive.

This OBPI closes the vacuum by making the rule real. `src/gzkit/arb/` is now a proper gzkit package (Pydantic `BaseModel(frozen=True, extra="forbid")`, `pathlib.Path`, `encoding="utf-8"`, typed `GzkitConfig.arb` section). `src/gzkit/commands/arb.py` dispatches seven CLI verbs with deterministic exit codes (0 success, 1 command failure, 2 ARB internal). `src/gzkit/cli/parser_arb.py` registers the verbs in the main parser tree as a dedicated module because `parser_maintenance.py` was already past the 600L soft cap. `data/schemas/arb_lint_receipt.schema.json` and `arb_step_receipt.schema.json` carry the Draft 2020-12 contracts with gzkit schema IDs. 54 tests across 11 test modules enforce Red→Green discipline. `features/arb.feature` provides Gate 4 behavioral proof with 6 scenarios. `docs/user/commands/arb.md`, `docs/user/manpages/arb.md`, and `docs/user/runbook.md` satisfy the Gate 5 runbook-code covenant. `.gzkit/rules/arb.md` is bumped 1.0 → 1.1 with the new `patterns` verb and a truthful last-reviewed date. `.gzkit/skills/gz-arb/SKILL.md` is revived from retired to active with a revival note citing this OBPI.

The Absorb decision is doctrinally correct — ADR-0.25.0 line 64 pre-declared `src/gzkit/arb/` as an integration point, the subtraction test favors absorption (ARB is not airline-specific), and both the attestation rule and the rule contract are non-executable without this surface. The consequence is that every future Heavy-lane attestation in this repository can honestly satisfy the attestation-enrichment receipt-ID requirement — and the first such attestation is this OBPI's own Stage 4 ceremony, citing receipts from the very surface it just created. ADR-0.25.0 closes by eating its own dog food.

**ADR-0.27.0 collision (discovered 2026-04-14 during Stage 4 demonstration).** The operator surfaced a sibling ADR — `ADR-0.27.0-arb-receipt-system-absorption`, status Proposed, 0/13 — which was intended to perform the same absorption as 13 separate per-module OBPIs. Twelve of ADR-0.27.0's briefs are skeletal decision-brief templates (~60 lines each, boilerplate Objective/Source/Requirements/Quality Gates with `*To be authored at completion from delivered evidence.*` placeholder closing arguments). The sole exception is `OBPI-0.27.0-09-arb-telemetry-sync`, which contains genuine architectural design work: a pivot from the opsdev Supabase approach to **Pydantic Logfire** as the L3 retention backend, with state-doctrine alignment (Logfire as derived/rebuildable L3, ledger.jsonl as L2 source of truth), TOML configuration model, env overrides (`GZKIT_TELEMETRY_ENABLED`, `LOGFIRE_TOKEN`), graceful-degradation contract (`ImportError` → no-op emitter), and free-tier volume estimate (10M spans/month, ~10-20 spans per pipeline run). OBPI-0.25.0-33 did **not** implement this Logfire work and did **not** displace it.

The reconciliation: ADR-0.27.0 OBPIs 01/02/03/04/05/10/11/12/13 have been retroactively annotated with `Decision: Absorb (executed under OBPI-0.25.0-33)` cross-references preserving the per-module audit trail ADR-0.27.0's structure intended. Each of the 9 cross-referenced briefs now records which concrete gzkit file implements it (e.g., OBPI-0.27.0-01 → `src/gzkit/arb/ruff_reporter.py`), which Red→Green tests cover it, which dog-food receipts prove it, and how it differs from the opsdev source (schema rename, Pydantic conversion, path resolution via `get_project_root()`, drop of airlineops-infra imports, ruff binary vs. module invocation). ADR-0.27.0 OBPIs 06 (tidy), 07 (expunge), 08 (github-issues), and 09 (telemetry-sync/Logfire) remain `Pending` as legitimate follow-up work — none were implemented under OBPI-0.25.0-33, and OBPI-0.27.0-09 specifically preserves design thinking that deserves its own implementation pass with `logfire` added as an optional dependency and telemetry span emission from each wrapped step.

The collision surfaced a defect in the plan-audit surface (tracked as **GHI #152**): `/gz-plan-audit` checks ADR ↔ OBPI ↔ Plan alignment for the named OBPI, but does not cross-reference against sibling ADRs for scope collisions. If it had, ADR-0.27.0 would have been surfaced during OBPI-0.25.0-33's Stage 1 context load and the work could have been routed to its correct ADR home from the start. The governance lesson is that `Absorb` decisions in ADR-0.25.0 (the Tier 1 core-infrastructure pattern-harvest ADR) must cross-check against any Tier 2 dedicated-absorption ADRs that exist for the same opsdev module — ADR-0.25.0 is Tier 1 and ADR-0.27.0 is Tier 2 (per line 25 of each ADR's "Area" header), and the two-tier structure means OBPIs can scope-collide across tiers when operators run them in isolation.

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.25.0-01-attestation-pattern | decision_doc | FOUND |
| OBPI-0.25.0-02-progress-pattern | decision_doc | FOUND |
| OBPI-0.25.0-03-signature-pattern | decision_doc | FOUND |
| OBPI-0.25.0-04-world-state-pattern | decision_doc | FOUND |
| OBPI-0.25.0-05-dataset-version-pattern | decision_doc | FOUND |
| OBPI-0.25.0-06-registry-pattern | decision_doc | FOUND |
| OBPI-0.25.0-07-types-pattern | decision_doc | FOUND |
| OBPI-0.25.0-08-ledger-pattern | decision_doc | FOUND |
| OBPI-0.25.0-09-schema-pattern | decision_doc | FOUND |
| OBPI-0.25.0-10-errors-pattern | decision_doc | FOUND |
| OBPI-0.25.0-11-hooks-pattern | decision_doc | FOUND |
| OBPI-0.25.0-12-admission-pattern | decision_doc | FOUND |
| OBPI-0.25.0-13-qc-pattern | decision_doc | FOUND |
| OBPI-0.25.0-14-os-pattern | decision_doc | FOUND |
| OBPI-0.25.0-15-manifests-pattern | decision_doc | FOUND |
| OBPI-0.25.0-16-config-pattern | decision_doc | FOUND |
| OBPI-0.25.0-17-console-pattern | decision_doc | FOUND |
| OBPI-0.25.0-18-adr-lifecycle-pattern | decision_doc | FOUND |
| OBPI-0.25.0-19-adr-audit-ledger-pattern | decision_doc | FOUND |
| OBPI-0.25.0-20-adr-governance-pattern | decision_doc | FOUND |
| OBPI-0.25.0-21-adr-reconciliation-pattern | decision_doc | FOUND |
| OBPI-0.25.0-22-adr-traceability-pattern | decision_doc | FOUND |
| OBPI-0.25.0-23-artifact-management-pattern | decision_doc | FOUND |
| OBPI-0.25.0-24-cli-audit-pattern | decision_doc | FOUND |
| OBPI-0.25.0-25-docs-validation-pattern | decision_doc | FOUND |
| OBPI-0.25.0-26-drift-detection-pattern | decision_doc | FOUND |
| OBPI-0.25.0-27-policy-guards-pattern | decision_doc | FOUND |
| OBPI-0.25.0-28-layout-verification-pattern | decision_doc | FOUND |
| OBPI-0.25.0-29-ledger-schema-pattern | decision_doc | FOUND |
| OBPI-0.25.0-30-references-pattern | decision_doc | FOUND |
| OBPI-0.25.0-31-validation-receipts-pattern | decision_doc | FOUND |
| OBPI-0.25.0-32-handoff-validation-pattern | decision_doc | FOUND |
| OBPI-0.25.0-33-arb-analysis-pattern | command_doc | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `completed`

**Attested by**: Jeffry
**Timestamp (UTC)**: 2026-04-16T02:42:30Z
