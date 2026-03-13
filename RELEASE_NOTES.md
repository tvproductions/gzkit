# gzkit Release Notes

## Unreleased

_No unreleased entries._

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
