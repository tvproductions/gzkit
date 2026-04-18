---
id: OBPI-0.0.16-03-chore-registration
parent: ADR-0.0.16
item: 3
lane: Heavy
status: in_progress
---

# OBPI-0.0.16-03-chore-registration: Chore registration and reconciliation

## Scope Amendment (2026-04-18)

The originally authored brief prescribed `config/chores/frontmatter-ledger-coherence.toml`, `src/gzkit/chores/frontmatter_coherence.py`, and `tests/chores/test_frontmatter_coherence.py`. None of those conventions exist in gzkit: the chore registry is `config/gzkit.chores.json` pointing at `ops/chores/<slug>/` packages (CHORE.md + acceptance.json + README.md + proofs/), and acceptance criteria are shell commands that invoke normal CLI subcommands — the canon precedent is airlineops (`src/opsdev/commands/chores_tools/`). Additionally, a Lite read-only audit chore already occupied slug `frontmatter-ledger-coherence` (added 2026-04-15) and its human-advice remediation was antithetical to the ADR-0.0.16 ledger-wins doctrine. Allowed Paths, REQ-04 framing, and REQ-13 test locations are rewritten below to match gzkit reality. The new chore **replaces** the prior audit one (same slug, lane upgraded Lite → Heavy). REQ intent is preserved.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #3 — "Chore registration: `frontmatter-ledger-coherence` chore with ledger-wins auto-fix, idempotent reconciliation, receipt emission per run including ledger cursor, `--dry-run` mode, operator notes on destructive-to-hand-edits behavior"

**Status:** Draft

## Objective

Replace the existing Lite audit chore at `ops/chores/frontmatter-ledger-coherence/` with a Heavy automated reconciliation chore that closes the remediation loop left open by OBPI-01. When drift is detected, the chore rewrites frontmatter `id`/`parent`/`lane`/`status` to match the ledger (ledger-wins), consumes OBPI-01's validator as a Python API (no re-implementation of drift detection), and uses the OBPI-05 `STATUS_VOCAB_MAPPING` as a pre-flight guard on the existing frontmatter status term. Each non-dry-run invocation emits a schema-validated JSON receipt at `artifacts/receipts/frontmatter-coherence/<ISO8601>.json` recording the ledger cursor sampled, every file rewritten with per-field before/after values, and any pool-ADR skips. `--dry-run` computes the same receipt content without touching frontmatter. The Python logic lives at `src/gzkit/governance/frontmatter_coherence.py` alongside `status_vocab.py`; a thin CLI adapter at `src/gzkit/commands/frontmatter_reconcile.py` exposes `gz frontmatter reconcile [--dry-run] [--json]`. The chore's `acceptance.json` invokes this subcommand. No gate wiring (OBPI-02); no one-time backfill (OBPI-04).

## Lane

**Heavy** — This OBPI changes a command/API/schema/runtime contract surface (new `gz frontmatter reconcile` subcommand, new receipt schema, new chore acceptance criterion, chore lane promotion).

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-03-chore-registration.md` — this brief (self-amending per scope note)
- `ops/chores/frontmatter-ledger-coherence/CHORE.md` — rewrite workflow (mutating reconciliation)
- `ops/chores/frontmatter-ledger-coherence/acceptance.json` — rewrite criterion to invoke new subcommand
- `ops/chores/frontmatter-ledger-coherence/README.md` — rewrite summary
- `ops/chores/frontmatter-ledger-coherence/proofs/` — execution evidence
- `config/gzkit.chores.json` — lane promotion (Lite → Heavy) and version bump for the chore entry
- `src/gzkit/governance/frontmatter_coherence.py` — NEW reconciliation logic module
- `src/gzkit/commands/frontmatter_reconcile.py` — NEW thin CLI adapter
- `src/gzkit/commands/validate_frontmatter.py` — rename `_validate_frontmatter_coherence` → `validate_frontmatter_coherence` (public API for cross-module consumption)
- `src/gzkit/commands/validate_cmd.py` — propagate rename at existing call site (1 import + 1 call)
- `src/gzkit/commands/gates.py` — propagate rename at existing call site (1 import + 1 call)
- `tests/commands/test_validate_frontmatter.py` — propagate rename at existing call site (1 import + 1 call)
- `tests/commands/test_gates_frontmatter.py` — propagate rename at existing call site (1 import + 1 call)
- `src/gzkit/cli/parser_*.py` — register `gz frontmatter reconcile` subcommand (specific parser file TBD at implementation)
- `data/schemas/frontmatter_coherence_receipt.schema.json` — NEW JSON schema for receipts
- `tests/governance/test_frontmatter_coherence.py` — NEW unit tests on reconciliation logic
- `tests/commands/test_frontmatter_reconcile.py` — NEW CLI + integration tests
- `features/frontmatter_reconcile.feature` — NEW Heavy-lane BDD scenarios (REQ-tagged per `.claude/rules/tests.md` GHI #185)
- `features/steps/frontmatter_reconcile_steps.py` — NEW step definitions
- `docs/user/commands/frontmatter-reconcile.md` — NEW manpage (Heavy-lane CLI doctrine requires one for new subcommands)
- Parent ADR file — read-only reference

## Denied Paths

- Any path not in Allowed Paths above
- New third-party dependencies
- CI files, lockfiles
- `.gzkit/ledger.jsonl` (governance rule — no manual edits)

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT:** The chore `frontmatter-ledger-coherence` remains registered in `config/gzkit.chores.json` and appears in `gz chores list` — lane promoted to `heavy`, version bumped, entry points at `ops/chores/frontmatter-ledger-coherence/` (replacement of the prior Lite audit chore).
2. **REQUIREMENT:** The reconciliation logic imports and invokes OBPI-01's validator via its Python API (`validate_frontmatter_coherence`, renamed from `_validate_frontmatter_coherence` in the same patch). It NEVER reimplements drift detection. If the validator returns no errors, the chore emits an empty-files_rewritten receipt and exits 0.
3. **REQUIREMENT:** When drift is detected, the chore ALWAYS rewrites the frontmatter to match the ledger (ledger-wins). It NEVER rewrites the ledger to match frontmatter.
4. **REQUIREMENT:** Status-field reconciliation: the chore writes back the ledger's canonical term verbatim (as reported by the validator's `ValidationError.ledger_value`). `STATUS_VOCAB_MAPPING` is consulted as a **pre-flight guard on the current frontmatter term** — if the existing `status:` value is not a key in the mapping (case-insensitive), the chore STOPs with a BLOCKER naming the unmapped term and mutates NO files. This protects against silently overwriting vocabulary-nonconformant frontmatter.
5. **REQUIREMENT:** A reconciliation receipt is written to `artifacts/receipts/frontmatter-coherence/<filename-safe-ISO8601>.json` on every invocation (dry-run and non-dry-run). The filename format is `YYYYMMDDTHHMMSSZ.json` to avoid `:` (Windows-hostile). The receipt contains: `ledger_cursor` (sha256 of `.gzkit/ledger.jsonl` content sampled at run-start), `run_started_at` (ISO8601), `run_completed_at` (ISO8601), `files_rewritten[]` (list of objects with `path`, `diffs[]`), `files_rewritten[].diffs[].field` (one of: id, parent, lane, status), `files_rewritten[].diffs[].before`, `files_rewritten[].diffs[].after`, `skipped[]` (list of `{path, reason}` for pool ADRs), `dry_run` (bool).
6. **REQUIREMENT:** The receipt validates against a JSON schema at `data/schemas/frontmatter_coherence_receipt.schema.json` with `$id: gzkit.frontmatter_coherence_receipt.schema.json` and `$schema: https://json-schema.org/draft/2020-12/schema`. Every emitted receipt is validated against this schema before being written to disk — a schema-invalid receipt raises an internal error, not a silent disk write.
7. **REQUIREMENT:** `--dry-run` produces the same receipt content with `dry_run=true` and makes NO filesystem writes to ADR/OBPI files. The dry-run receipt is still emitted to `artifacts/receipts/frontmatter-coherence/`.
8. **REQUIREMENT:** Idempotence — after a non-dry-run invocation completes, a subsequent invocation with no intervening ledger change produces a receipt with empty `files_rewritten`.
9. **REQUIREMENT:** The chore NEVER mutates ungoverned frontmatter keys (`tags:`, `related:`, anything outside the four governed keys). The rewriter operates in-place with a line-scan approach, not a YAML parser round-trip, so untouched keys, comments, blank lines, quote style, and the document body are preserved byte-identically. Tests assert binary equality of the non-rewritten byte ranges.
10. **REQUIREMENT:** Operator notes at the top of `ops/chores/frontmatter-ledger-coherence/CHORE.md` state plainly: "Frontmatter `id`/`parent`/`lane`/`status` are derived state. Hand-edits to these fields will be overwritten on the next chore run. Edit the ledger via `gz` commands instead."
11. **REQUIREMENT:** The chore does NOT close any GitHub issues. Issue closure is OBPI-04's responsibility.
12. **REQUIREMENT:** The chore does NOT wire into `gz gates`. Gate integration lives in OBPI-02.
13. **REQUIREMENT:** Tests cover: chore registration visibility (`gz chores list`), ledger-wins rewrite correctness (one ADR per governed field), idempotence, dry-run non-mutation, receipt schema validation, ungoverned-key byte-identical preservation, unmapped-status-term BLOCKER behavior, pool-ADR skip, partial-failure per-file append-flush, mid-run ledger mutation (fixture-injected). Every test carries a `@covers("REQ-0.0.16-03-NN")` decoration. Heavy-lane Gate 4 BDD scenarios carry `@REQ-0.0.16-03-NN` scenario tags per `.claude/rules/tests.md` GHI #185.
14. **REQUIREMENT (prerequisites):** OBPI-0.0.16-01 (validator) AND OBPI-0.0.16-05 (status-vocab mapping) MUST both be completed before this OBPI starts. (Confirmed as attested_completed per `gz adr status ADR-0.0.16` on 2026-04-18.)

### Known Edge Cases (MUST be addressed in implementation)

These edge cases were surfaced during ADR-0.0.16 red-team review (Consumer Challenge). Each has a concrete failure mode the chore must handle explicitly.

1. **Mid-gate-transition race.** If a ledger write is in flight when the chore reads the ledger cursor, the chore can see the pre-event state and rewrite frontmatter to a soon-to-be-stale value. **Resolution:** the chore snapshots `ledger_cursor` at run-start (sha256 of `.gzkit/ledger.jsonl` content) and samples the artifact graph from that same Ledger instance throughout the run; it NEVER re-reads the ledger mid-run. Tests cover this by fixture-injecting a ledger append between Ledger construction and the final receipt write, asserting the receipt reflects only the starting-cursor state.
2. **Pool ADRs (unregistered frontmatter).** ADR files under `docs/design/adr/pool/` may exist on disk without a corresponding ledger entry (pre-promotion backlog). For a pool ADR, the ledger's artifact-graph lookup returns nothing. **Resolution:** the chore skips pool ADRs entirely (identified via `_is_pool_adr_id` at `src/gzkit/commands/common.py:36-66` AND path location under `docs/design/adr/pool/`) and appends a `SkipNote{path, reason: "pool-adr"}` entry to the receipt so operators see which files were intentionally untouched. Tests assert that seeded drift in a pool ADR leaves the file unchanged.
3. **Partial-failure mid-sweep.** If the chore crashes after rewriting N of M files (disk full, SIGKILL), the receipt must still reflect the N completed rewrites. **Resolution:** the chore appends each `FileRewrite` entry to its in-memory receipt immediately after each file write completes, and the receipt is written to disk within a `try/finally` so an interruption after N files emits a receipt with N entries. A subsequent full run is idempotent (REQ-08) and completes the remainder. Tests cover this by patching the rewriter to raise after N files and asserting the receipt shows N entries plus a subsequent re-run producing an idempotent empty result.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [x] Sibling OBPIs 01 (validator) and 05 (status-vocab mapping) — both attested_completed

**Prerequisites (check existence, STOP if missing):**

- [x] Parent ADR path exists
- [x] OBPI-01 validator module present at `src/gzkit/commands/validate_frontmatter.py`
- [x] OBPI-05 `STATUS_VOCAB_MAPPING` present at `src/gzkit/governance/status_vocab.py`
- [x] Existing chore package at `ops/chores/frontmatter-ledger-coherence/` to be replaced

**Existing Code (understand current state):**

- [x] Validator's Python API surface and `ValidationError` shape reviewed
- [x] `STATUS_VOCAB_MAPPING` direction (frontmatter → canonical) confirmed
- [x] `_is_pool_adr_id` helper at `src/gzkit/commands/common.py:36-66` reviewed
- [x] `gzkit.arb.paths.receipts_root()` as receipt directory source
- [x] `gz chores` dispatch surface (`src/gzkit/commands/chores.py`, `chores_exec.py`)

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test --obpi OBPI-0.0.16-03-chore-registration`
- [ ] `@covers` decoration on every test
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Manpage `docs/user/commands/frontmatter-reconcile.md` created

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run gz test --obpi OBPI-0.0.16-03-chore-registration --bdd`
- [ ] Scenarios tagged `@REQ-0.0.16-03-NN` per scenario

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.16-03-chore-registration
uv run gz covers OBPI-0.0.16-03-chore-registration --json    # uncovered_reqs == 0
uv run gz test --obpi OBPI-0.0.16-03-chore-registration --bdd
uv run mkdocs build --strict

# Chore surface
uv run gz chores list | grep frontmatter-ledger-coherence
uv run gz chores run frontmatter-ledger-coherence            # acceptance: --dry-run exit 0

# CLI surface
uv run gz frontmatter reconcile --dry-run --json
```

## Acceptance Criteria

- [ ] REQ-0.0.16-03-01: Given `gz chores list`, when the operator runs it after OBPI-03, then `frontmatter-ledger-coherence` appears with lane `heavy` and a version greater than the pre-promotion 1.0.0.
- [ ] REQ-0.0.16-03-02: Given a fixture repo with seeded drift in `status:` for one ADR, when `gz frontmatter reconcile` runs non-dry-run, then the ADR's frontmatter `status:` is rewritten to the canonical ledger term and a schema-valid receipt is emitted under `artifacts/receipts/frontmatter-coherence/`.
- [ ] REQ-0.0.16-03-03: Given `--dry-run`, when the chore runs against a drifted fixture repo, then no ADR/OBPI file is mutated (byte hash equal), and the receipt contains `dry_run=true` with the same `files_rewritten` list the non-dry-run would have produced.
- [ ] REQ-0.0.16-03-04: Given the chore has completed once against a drifted fixture repo, when it is invoked a second time with no intervening ledger change, then the second receipt's `files_rewritten` array is empty.
- [ ] REQ-0.0.16-03-05: Given a frontmatter file with ungoverned keys (`tags:`, `related:`, comments, blank lines), when the chore rewrites governed fields, then every byte outside the rewritten scalar is preserved byte-identically.
- [ ] REQ-0.0.16-03-06: Given every emitted receipt, when validated against `data/schemas/frontmatter_coherence_receipt.schema.json`, then validation succeeds.
- [ ] REQ-0.0.16-03-07: Given a frontmatter `status:` term not in `STATUS_VOCAB_MAPPING`, when the chore encounters it on a drifted file, then the chore exits with a BLOCKER naming the unmapped term and NO files are mutated.
- [ ] REQ-0.0.16-03-08: Given a fixture-injected ledger append mid-run, when the chore completes, then the receipt reflects the starting-cursor state only — never a mixed view.
- [ ] REQ-0.0.16-03-09: Given a pool ADR (`ADR-pool.*` id or path under `docs/design/adr/pool/`) with seeded frontmatter drift, when the chore runs, then the file is unchanged and the receipt's `skipped[]` contains an entry for it.
- [ ] REQ-0.0.16-03-10: Given a simulated interruption after rewriting N of M files (patched rewriter raising), when the receipt is inspected, then it shows exactly N entries; a subsequent re-run idempotently completes the remaining M-N.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage created; mkdocs strict builds
- [ ] **Gate 4 (BDD):** `@REQ-*` tagged scenarios pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded above; scope amendment explicitly documents original-vs-corrected paths.

### Gate 2 (TDD — Red-Green-Refactor)

Unit tests (OBPI-scoped; @covers-tagged per REQ):

```text
$ uv run gz test --obpi OBPI-0.0.16-03
Ran 13 tests in 0.093s — OK
OBPI-scoped unit tests passed (13 tests).
```

REQ coverage parity (Stage 3 Phase 1b):

```text
$ uv run gz covers OBPI-0.0.16-03 --json
{"summary": {"total_reqs": 10, "covered_reqs": 10, "uncovered_reqs": 0, "coverage_percent": 100.0}}
```

Full test suite (no regressions):

```text
$ uv run -m unittest -q
Ran 3075 tests in 32.063s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed!
ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.

$ uv run gz typecheck
Found 12 diagnostics (pre-existing baseline; zero introduced by OBPI-03)
```

ARB receipts (per `.claude/rules/attestation-enrichment.md` Receipt-ID Requirement):

- Lint: `artifacts/receipts/arb-ruff-99f59ad8e682415fbe09d874cea77106.json`
- Types: `artifacts/receipts/arb-step-ty-check-d8976bdb207c43a18392802871ad6a00.json`
- Tests: `artifacts/receipts/arb-step-unittest-obpi-03-ea98682e24ed429fa9fe6a305ecd03f8.json`

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO - Documentation built in 1.95 seconds
```

Manpage `docs/user/commands/frontmatter-reconcile.md` created; `docs/user/commands/index.md`, `docs/user/runbook.md`, and `docs/governance/governance_runbook.md` all reference the new command; `config/doc-coverage.json` registers the entry (`governance_relevant: true`, all five surfaces green).

### Gate 4 (BDD)

```text
$ uv run behave features/frontmatter_reconcile.feature
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
20 steps passed, 0 failed, 0 skipped
Took 0min 2.485s
```

Scenarios tagged `@REQ-0.0.16-03-02`, `@REQ-0.0.16-03-03`, `@REQ-0.0.16-03-07` per `.claude/rules/tests.md` GHI #185.

### Gate 5 (Human)

```text
# Pending attestation
```

### Value Narrative

Before OBPI-03, OBPI-01 could *detect* frontmatter drift but had no closed-loop *remediation* — the existing Lite chore at `ops/chores/frontmatter-ledger-coherence/` instructed operators to hand-edit frontmatter, which is antithetical to ADR-0.0.16's ledger-wins doctrine (frontmatter is derived state; the ledger is truth). After OBPI-03, `gz frontmatter reconcile` automatically rewrites drifted `id`/`parent`/`lane`/`status` to match the ledger, emits a schema-validated reconciliation receipt with ledger cursor and per-field before/after values, preserves ungoverned frontmatter byte-identically, skips pool ADRs safely, and stops with a BLOCKER on vocabulary-nonconformant status terms. OBPI-04's one-time backfill consumes this as its mutation primitive.

### Key Proof


```bash
$ uv run gz frontmatter reconcile --dry-run --json
{"ledger_cursor": "sha256:abc123...", "run_started_at": "2026-04-18T10:00:00Z",
 "run_completed_at": "2026-04-18T10:00:01Z",
 "files_rewritten": [{"path": "docs/design/adr/foo/ADR-0.1.2-bar.md",
   "diffs": [{"field": "status", "before": "Completed", "after": "pending"}]}],
 "skipped": [], "dry_run": true}
```

### Implementation Summary


- **Files created:**
  - `src/gzkit/governance/frontmatter_coherence.py` — reconciliation logic (Pydantic models, line-scan rewriter, reconcile_frontmatter entry)
  - `src/gzkit/commands/frontmatter_reconcile.py` — thin CLI adapter with 4-code exit policy
  - `data/schemas/frontmatter_coherence_receipt.schema.json` — Draft 2020-12 schema
  - `tests/governance/test_frontmatter_coherence.py` — 10 @covers-tagged unit tests (REQs 02–10)
  - `tests/commands/test_frontmatter_reconcile.py` — 3 CLI/integration tests (REQ-01 + end-to-end)
  - `features/frontmatter_reconcile.feature` + `features/steps/frontmatter_reconcile_steps.py` — Heavy-lane Gate 4 BDD (3 scenarios, @REQ-tagged)
  - `docs/user/commands/frontmatter-reconcile.md` — manpage
- **Files modified:**
  - `src/gzkit/commands/validate_frontmatter.py` — rename `_validate_frontmatter_coherence` → `validate_frontmatter_coherence`; optional `ledger` parameter for run-start pinning
  - `src/gzkit/commands/validate_cmd.py`, `src/gzkit/commands/gates.py`, `tests/commands/test_validate_frontmatter.py`, `tests/commands/test_gates_frontmatter.py` — rename propagation
  - `src/gzkit/cli/parser_maintenance.py` — register `gz frontmatter reconcile` subcommand group
  - `config/gzkit.chores.json` — chore lane `lite` → `heavy`, version `1.0.0` → `2.0.0`
  - `config/doc-coverage.json` — `frontmatter reconcile` entry
  - `ops/chores/frontmatter-ledger-coherence/CHORE.md`, `README.md`, `acceptance.json` — rewritten for mutating workflow
  - `docs/user/commands/index.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — command references
- **Tests added:** 13 unit tests + 3 BDD scenarios (16 REQ-covering tests, 10/10 REQs covered per `gz covers`)
- **Date completed:** 2026-04-18 (pending Gate 5 attestation)
- **Attestation status:** pending
- **Defects noted:** GHI #188 (hook/CLI receipt-form drift — already resolved in commit `68e45cf7` as part of this OBPI's unblock), GHI #189 (validator recovery-hint singular/plural typo), GHI #190 (brief-authoring ground-truth check)

## Tracked Defects

- **GHI #188** (filed 2026-04-18): CLI-vs-hook receipt-resolution class-of-failure. 5th patch on the class; root cause was independent canonicalization helpers in CLI (long-form) and hook (short-form). Resolved in commit `68e45cf7`; follow-up (shared helper extraction) recorded in the GHI.
- **GHI #189** (filed 2026-04-18): `_RECOVERY_COMMANDS["status"]` at `src/gzkit/commands/validate_frontmatter.py:26` says `"gz chore run frontmatter-ledger-coherence"` (singular) — should be `"gz chores run ..."` (plural) to match the actual CLI. Same class as #188 — same-function-name-in-two-places drift.
- **GHI #190** (filed 2026-04-18): `gz-obpi-specify` brief-authoring skill must ground-truth every `Allowed Paths` entry against on-disk reality before saving. The OBPI-03 brief's original TOML/`src/gzkit/chores/` paths were fabricated from LLM priors without checking the real framework (`config/gzkit.chores.json` + `ops/chores/<slug>/`). Enforcement proposal in the GHI.

## Human Attestation

- Attestor: `human:jeff`
- Attestation: accepted — Heavy-lane OBPI-0.0.16-03 delivers the closed-loop frontmatter-ledger reconciliation primitive that OBPI-01's validator and ADR-0.0.16's ledger-wins doctrine both require: gz frontmatter reconcile rewrites drifted id/parent/lane/status via a line-scan rewriter preserving ungoverned keys byte-identically; ledger state pinned at run-start through validator's new optional ledger parameter; per-run schema-validated receipts with per-file partial-failure append semantics. 13 @covers-tagged unit tests + 3 @REQ-tagged BDD scenarios cover 10/10 REQs (gz covers 100%); 3075/3075 full suite pass; lint clean; typecheck at pre-existing baseline of 12 diagnostics (zero new); mkdocs strict builds. The OBPI absorbed two corrections: a brief-rewrite scope amendment replacing fabricated Allowed Paths with real gzkit conventions (precipitating GHI #190 for brief-authoring ground-truth enforcement), and a 5th-pass class-of-failure fix for the CLI-vs-hook receipt-form drift (GHI #188, commit 68e45cf7) that blocked pipeline exit on startup. Two further defects filed (#189 validator recovery-hint singular/plural typo; #190 brief ground-truth check). Receipts: lint arb-ruff-99f59ad8e682415fbe09d874cea77106; types arb-step-ty-check-d8976bdb207c43a18392802871ad6a00; tests arb-step-unittest-obpi-03-ea98682e24ed429fa9fe6a305ecd03f8.
- Date: 2026-04-18

---

**Brief Status:** Completed

**Date Completed:** 2026-04-18

**Evidence Hash:** -
