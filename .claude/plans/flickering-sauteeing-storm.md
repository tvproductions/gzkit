# OBPI-0.0.16-03 — frontmatter-ledger-coherence chore (reconciliation)

## Context

The authored OBPI-0.0.16-03 brief is **mis-specified against gzkit reality**. It names `config/chores/frontmatter-ledger-coherence.toml` (no TOML chore registry exists), `src/gzkit/chores/frontmatter_coherence.py` (no such module tree exists), and `tests/chores/test_frontmatter_coherence.py` (no such test tree exists). Neither gzkit nor the airlineops canon uses TOML chores or per-chore Python modules. Both use `ops/chores/<slug>/` packages (CHORE.md + acceptance.json + README.md + proofs/) registered via `config/gzkit.chores.json`, with acceptance criteria that are shell commands invoking normal CLI subcommands. The brief was authored without reading the existing framework.

The **intent**, however, is sound and load-bearing for ADR-0.0.16:

- The existing chore at `ops/chores/frontmatter-ledger-coherence/` (Lite, added 2026-04-15) is borderline useless — when it finds drift it tells a human to hand-edit frontmatter, which is antithetical to the whole ADR-0.0.16 doctrine (ledger-wins; frontmatter is derived state). It's a placeholder.
- The OBPI-01 validator's own recovery hint already names this chore as the closed-loop fix (`src/gzkit/commands/validate_frontmatter.py:26`). The chore is the validator's intended partner.
- ADR-0.0.16's 5-OBPI split makes OBPI-03 the *mutation primitive* that OBPI-04 (one-time backfill) consumes.

**This plan therefore does two things:**

1. **Rewrite the OBPI-03 brief** in place, replacing fabricated paths with real ones, resolving REQ-04's status-vocab-direction ambiguity, and scoping an explicit *replacement* of the Lite audit chore (slug preserved, lane upgraded, behavior changed).
2. **Execute** the rewritten brief to deliver the mutating reconciler.

A post-completion defect GHI will flag the fabricated-brief authoring failure mode so the brief-authoring skill absorbs a ground-truth check.

---

## Scope Amendment (to brief)

### Allowed Paths — corrected

- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-03-chore-registration.md` — rewrite brief (self-editing allowed)
- `ops/chores/frontmatter-ledger-coherence/CHORE.md` — rewrite workflow to document mutating behavior
- `ops/chores/frontmatter-ledger-coherence/acceptance.json` — rewrite to exercise `gz frontmatter reconcile --dry-run` (exit 0 = no drift remaining)
- `ops/chores/frontmatter-ledger-coherence/README.md` — rewrite summary
- `ops/chores/frontmatter-ledger-coherence/proofs/` — used by chore runner, no manual edits required
- `config/gzkit.chores.json` — promote this chore's registry entry from Lite to Heavy; version bump
- `src/gzkit/governance/frontmatter_coherence.py` — NEW, the reconciliation logic module (sits next to `status_vocab.py`)
- `src/gzkit/commands/frontmatter_reconcile.py` — NEW, thin CLI adapter exposing `gz frontmatter reconcile`
- `src/gzkit/cli/parser_maintenance.py` — register new subcommand (confirm location during implementation; may be a different parser file)
- `data/schemas/frontmatter_coherence_receipt.schema.json` — NEW, JSON schema for receipts
- `tests/governance/test_frontmatter_coherence.py` — NEW, unit tests on the mutation logic
- `tests/commands/test_frontmatter_reconcile.py` — NEW, CLI + integration tests
- `features/frontmatter_reconcile.feature` — NEW, Heavy-lane BDD scenarios with `@REQ-0.0.16-03-*` tags (per `.claude/rules/tests.md` GHI #185)
- `features/steps/frontmatter_reconcile_steps.py` — NEW
- `docs/user/commands/frontmatter-reconcile.md` — NEW manpage (Heavy-lane CLI doctrine — `.claude/rules/cli.md` requires one for new subcommands)
- Parent ADR: read-only reference

### REQ clarifications

- **REQ-04 (status rewrite semantics)** — Resolved direction: the chore writes back the **ledger's canonical term verbatim** (what the validator returns as `ValidationError.ledger_value`). `STATUS_VOCAB_MAPPING` is applied as a **pre-flight guard on the existing frontmatter term** — if the current frontmatter `status:` value is not a key in the mapping, the chore STOPs with a BLOCKER naming the unmapped term (REQ-07 preserved; no files mutated).
- **REQ-07 (`--dry-run`)** — Implemented as a CLI flag on `gz frontmatter reconcile`, not as a per-chore framework flag. The `gz chores advise` surface is unchanged.
- **REQ-05 (receipt location)** — `artifacts/receipts/frontmatter-coherence/<ISO8601>.json` with ISO format that avoids `:` (filename-safe): `YYYYMMDDTHHMMSSZ.json`. Matches ARB receipt root resolution via `gzkit.arb.paths.receipts_root()`.

### Removed / demoted

- REQ-11 (chore does NOT close GH issues) — kept; unchanged.
- REQ-12 (chore does NOT wire into `gz gates`) — kept; unchanged.

---

## Implementation Design

### Module layout

```
src/gzkit/governance/frontmatter_coherence.py    # pure logic, Pydantic models
src/gzkit/commands/frontmatter_reconcile.py      # CLI adapter, exit codes, --dry-run, --json
src/gzkit/cli/parser_*.py                        # subcommand registration
data/schemas/frontmatter_coherence_receipt.schema.json
```

### Public API (`src/gzkit/governance/frontmatter_coherence.py`)

```python
class FieldDiff(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    field: Literal["id", "parent", "lane", "status"]
    before: str
    after: str

class FileRewrite(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str
    diffs: list[FieldDiff]

class SkipNote(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str
    reason: Literal["pool-adr"]

class ReconciliationReceipt(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    ledger_cursor: str
    run_started_at: str
    run_completed_at: str
    files_rewritten: list[FileRewrite]
    skipped: list[SkipNote]
    dry_run: bool

class UnmappedStatusBlocker(Exception):
    def __init__(self, artifact: str, term: str): ...

def reconcile_frontmatter(project_root: Path, *, dry_run: bool) -> ReconciliationReceipt: ...
```

### Logic flow

1. **Sample ledger cursor at run-start** — compute sha256 of `.gzkit/ledger.jsonl` content (or read last event's hash if events carry one). Any subsequent mid-run ledger mutation does not influence this run. Record in receipt as `ledger_cursor`.
2. **Invoke validator** — `from gzkit.commands.validate_frontmatter import _validate_frontmatter_coherence` (rename to a public name in the same patch — drop the leading underscore; it's being consumed cross-module). Returns `list[ValidationError]`.
3. **Group errors by file path.** For each file with errors:
   - **Pool check** — use `gzkit.commands.common._is_pool_adr_id` against the artifact id AND check if path is under `docs/design/adr/pool/`. If pool → append `SkipNote`, continue.
   - **Pre-flight status guard** — if any error is on `status`, look up the *current* frontmatter term in `STATUS_VOCAB_MAPPING`. If unmapped → raise `UnmappedStatusBlocker`; no files mutated.
4. **For each non-pool, pre-flight-clean drift file:**
   - Compute the `FileRewrite` entry (`diffs` list of `FieldDiff(field, before=fm_value, after=ledger_value)`).
   - If `dry_run=False`: call the **in-place rewriter** (below).
   - Append `FileRewrite` to `files_rewritten` immediately — **per-file append** (REQ-10 partial-failure semantics).
5. **Emit receipt** to `artifacts/receipts/frontmatter-coherence/<filename-safe-iso>.json`. Validate against the new schema before writing.

### Frontmatter in-place rewriter (the hard part)

**Why custom:** `gzkit.core.validation_rules.parse_frontmatter` is regex-based, doesn't preserve key order, comments, quote style, or blank lines. REQ-09 (byte-identical ungoverned keys) is unsatisfiable through that path.

**Approach:** line-scan the raw file text. Locate the frontmatter block (opening `---` at line 1, closing `---` on some later line). For each governed key the chore needs to rewrite, regex-match the line's scalar portion only and replace. Everything else — including ungoverned keys, blank lines, trailing comments, quote style, and the body after the closing `---` — is passed through verbatim.

```python
_FM_LINE_RE = re.compile(r"^(\s*(?P<key>[A-Za-z_][\w-]*)\s*:\s*)(?P<val>.*?)(?P<trail>\s*(?:#.*)?)$")

def _rewrite_fm_lines(lines: list[str], edits: dict[str, str]) -> list[str]:
    """Rewrite only the scalar after ': ' for governed keys present in edits.
    Preserves original leading indent, spacing, trailing comment, and line ending.
    """
```

Tests assert **binary equality** of the body region and of every untouched line in the frontmatter block.

### CLI adapter (`src/gzkit/commands/frontmatter_reconcile.py`)

- Subcommand: `gz frontmatter reconcile [--dry-run] [--json]`
- Exit codes (per `.claude/rules/cli.md`):
  - `0` — success (no drift, OR drift resolved, OR dry-run with drift enumerated)
  - `1` — user/config error (not-a-gzkit-project, bad flag)
  - `2` — system/IO error (ledger unreadable, write failure)
  - `3` — policy breach (`UnmappedStatusBlocker` — names the unmapped term in stderr)
- `--json` — emit the receipt JSON to stdout; human-readable table by default
- Manpage at `docs/user/commands/frontmatter-reconcile.md` — heavy lane doctrine requires one

### Chore package update

- **`ops/chores/frontmatter-ledger-coherence/acceptance.json`** — single criterion:
  ```json
  {"criteria": [{"type": "exitCodeEquals", "command": "uv run gz frontmatter reconcile --dry-run", "expected": 0}]}
  ```
  Exit code 0 means no drift would be rewritten. If drift exists, the operator runs `gz frontmatter reconcile` (non-dry-run) to resolve.
- **`CHORE.md`** — rewrite to document: the chore runs ledger-wins reconciliation; `gz chores run` asserts no drift remains; mutation is via `gz frontmatter reconcile`; receipts land in `artifacts/receipts/frontmatter-coherence/`; operator notes explain that hand-edits to `id`/`parent`/`lane`/`status` will be overwritten.
- **`README.md`** — mirror the new summary.
- **`config/gzkit.chores.json`** — lane `Lite` → `heavy`; version `1.0.0` → `2.0.0`.

### Receipt JSON schema

`data/schemas/frontmatter_coherence_receipt.schema.json` with `$id: gzkit.frontmatter_coherence_receipt.schema.json` and `$schema: https://json-schema.org/draft/2020-12/schema`. Required top-level fields: `ledger_cursor`, `run_started_at`, `run_completed_at`, `files_rewritten`, `skipped`, `dry_run`. `files_rewritten[]` requires `path`, `diffs[]` with `field` (enum: id/parent/lane/status), `before`, `after`.

---

## Test Plan (Gate 2 TDD — Red first, per REQ)

Tests derive from brief requirements, NOT from implementation. Follow Red → Green → Refactor per increment. Every test decorated with `@covers("REQ-0.0.16-03-NN")`.

| REQ | Test |
|-----|------|
| 01 | `test_chore_appears_in_gz_chores_list` — `gz chores list` output contains `frontmatter-ledger-coherence` with heavy lane |
| 02 | `test_reconcile_rewrites_drifted_status` — seed ADR drift; assert `status:` line rewritten to ledger value; receipt emitted |
| 03 | `test_dry_run_emits_receipt_without_mutation` — seed drift; dry-run; assert file on disk unchanged (hash equal); assert receipt contains `dry_run=true` and same `files_rewritten` |
| 04 | `test_second_run_produces_empty_receipt` — run twice back-to-back with no ledger change; assert second receipt's `files_rewritten` is empty |
| 05 | `test_ungoverned_keys_preserved_byte_identical` — seed drift on `status`; add `tags:` and trailing blank lines and a comment in frontmatter; assert every byte outside the rewritten scalar is identical |
| 06 | `test_receipt_validates_against_schema` — validate every emitted receipt against the schema file |
| 07 | `test_unmapped_status_term_raises_blocker` — seed frontmatter with `status: Whatever` (not in STATUS_VOCAB_MAPPING) + drift; assert blocker raised, exit code 3, zero files mutated |
| 08 | `test_mid_run_ledger_mutation_ignored` — fixture injects a ledger append during iteration; assert receipt reflects only the starting cursor's state |
| 09 | `test_pool_adr_skipped` — seed drift in a file under `docs/design/adr/pool/` with `id: ADR-pool.foo`; assert file unchanged; receipt contains `SkipNote` |
| 10 | `test_partial_failure_shows_per_file_entries` — patch rewriter to raise after N files; assert receipt shows N entries; second full run completes idempotently |
| plus | `test_cli_exit_codes_per_doctrine` — matrix test (success/user/system/policy) |
| plus | BDD: `features/frontmatter_reconcile.feature` with `@REQ-0.0.16-03-*` scenario tags covering REQs 02, 03, 07, 09 as end-to-end operator flows |

### Verification commands

```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.16-03-chore-registration
uv run gz covers OBPI-0.0.16-03-chore-registration --json     # 0 uncovered REQs
uv run gz test --obpi OBPI-0.0.16-03-chore-registration --bdd  # heavy lane
uv run gz validate --documents
uv run mkdocs build --strict

# chore end-to-end
uv run gz chores list | grep frontmatter-ledger-coherence
uv run gz chores run frontmatter-ledger-coherence          # acceptance: dry-run exit 0

# mutation end-to-end (on a seeded drift fixture; not the real repo)
uv run gz frontmatter reconcile --dry-run --json
```

---

## Execution Order

1. **Rewrite the brief** (`docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-03-chore-registration.md`) with corrected allowed paths, clarified REQ-04, and a scope-amendment note at the top documenting why the original was rewritten. This is Step 1 because every subsequent step must match the corrected brief, and the plan-audit receipt should be against the corrected brief's shape.
2. **Declare** `_validate_frontmatter_coherence` as public — rename to `validate_frontmatter_coherence` in `src/gzkit/commands/validate_frontmatter.py` (1-line symbol rename + update internal call site). Heavy-lane honest: this is a small API surface change to permit reuse without leading underscore access.
3. **Write the schema** first (`data/schemas/frontmatter_coherence_receipt.schema.json`), then the Pydantic models that mirror it (`src/gzkit/governance/frontmatter_coherence.py`), then the tests that assert schema↔model parity. Red the schema-validation tests first.
4. **Red the logic tests** — test_reconcile_rewrites_drifted_status, test_dry_run, test_pool_skip, test_unmapped_blocker, test_ungoverned_preserved — let them all fail.
5. **Green in order** — ledger cursor, validator invocation, pool/unmapped guards, rewriter, receipt emission. Refactor between increments.
6. **CLI adapter** + register subcommand + exit-code tests (all Red first).
7. **Chore package rewrite** + registry bump + `gz chores list` test.
8. **Manpage** + mkdocs strict build.
9. **BDD scenarios** + step definitions + `@REQ-*` tags + `gz test --bdd`.
10. **Covers parity gate** — `gz covers OBPI-0.0.16-03-chore-registration --json` must show `uncovered_reqs == 0`.
11. **Defect GHI** — file against `_RECOVERY_COMMANDS["status"]` for `"gz chore run ..."` → `"gz chores run ..."` fix (singular → plural). Include in Tracked Defects section.
12. **Defect GHI (process)** — file against the ADR/OBPI brief-authoring skill: the authored brief contained fabricated framework paths. The skill should do a pre-flight check that every Allowed Paths entry either exists or is explicitly a green-field path consistent with adjacent conventions. Include in Tracked Defects.

---

## Risks and Trade-offs

- **Renaming `_validate_frontmatter_coherence`**: small API surface change. Mitigation: update in one patch; grep the codebase for the old symbol to confirm only the intra-file call site uses it.
- **Frontmatter rewriter correctness**: the line-scan rewriter is bespoke code handling a YAML-adjacent format. Mitigation: test matrix covering quoted values, unquoted values, trailing comments, CRLF files (unlikely in this repo but defensive), and a round-trip byte-identity fuzz test on real ADR/OBPI files (`hypothesis`-style but simpler — iterate all real frontmatters with no drift, run rewriter with `edits={}`, assert file bytes equal).
- **`ledger_cursor` stability under concurrency**: gzkit operations are single-agent per lock; no real concurrency risk. Mitigation: the fixture-injected mutation test is sufficient.
- **Schema drift**: schema edits and Pydantic model edits must stay in lockstep. Mitigation: a single parity test that loads the schema and validates a receipt built from the model — if either drifts, the test breaks.
- **Chore lane promotion** (Lite→Heavy): existing operators may expect a fast pass. Mitigation: the acceptance criterion is still `--dry-run`, which does not mutate and is fast. The mutation run is operator-initiated.

---

## Critical files to read during implementation

- `src/gzkit/commands/validate_frontmatter.py` — the existing validator (reuse, do not reimplement)
- `src/gzkit/governance/status_vocab.py` — `STATUS_VOCAB_MAPPING` and `canonicalize_status`
- `src/gzkit/commands/common.py:36-66` — `_is_pool_adr_id` and `ADR_POOL_ID_RE`
- `src/gzkit/ledger.py` — `Ledger` read API, cursor semantics
- `src/gzkit/arb/paths.py` — `receipts_root()` for receipt output directory resolution
- `src/gzkit/commands/chores.py` and `chores_exec.py` — chore discovery, `gz chores run` dispatch, criterion evaluation
- `config/gzkit.chores.json` — registry schema for the lane/version bump
- `ops/chores/frontmatter-ledger-coherence/` — the existing package being replaced

---

## Completion definition

The OBPI is complete when:

1. Rewritten brief merged; plan-audit receipt has OBPI-0.0.16-03 and verdict PASS.
2. `gz test --obpi OBPI-0.0.16-03-chore-registration` passes (all REQs covered).
3. `gz covers OBPI-0.0.16-03-chore-registration --json` shows zero uncovered REQs.
4. Heavy-lane gates: `gz lint`, `gz typecheck`, `gz validate --documents`, `mkdocs build --strict`, `gz test --bdd` all green.
5. `gz chores run frontmatter-ledger-coherence` exits 0 on the current clean repo.
6. `gz frontmatter reconcile --dry-run` on a seeded drift fixture produces a schema-valid receipt.
7. Two defect GHIs filed (recovery-hint singular/plural typo; brief-authoring ground-truth check).
8. Gate 5 human attestation recorded.
