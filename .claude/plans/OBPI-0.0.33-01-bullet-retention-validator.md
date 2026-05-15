# Plan: OBPI-0.0.33-01 — Bullet Retention Validator

**OBPI:** OBPI-0.0.33-01-bullet-retention-validator
**Parent ADR:** ADR-0.0.33-agent-control-surface-fidelity
**Lane:** Heavy
**Date:** 2026-05-15

## Context

Implement `gz validate --bullet-retention` — Invariant 1 of ADR-0.0.33.

The validator reads `docs/governance/advisory-rules-audit.md`, extracts every
bullet classified **Mechanical** or **Promotable**, asserts each bullet's
normalized text is present verbatim in the per-turn surface corpus
(`AGENTS.md`, `CLAUDE.md`, `.claude/rules/**`), and exits 3 on any missing
bullet with a `ValidationError(type="bullet_retention")`.

**ADR Decision item (verbatim):**
> "1. **Bullet retention** — every bullet on `docs/governance/advisory-rules-audit.md`
> classified Mechanical or Promotable is present verbatim in the per-turn
> surface (Era 1) or registered as a `Bullet` instance in the canonical
> Pydantic content model (Era 2 onward, per ADR-0.0.34). Validator:
> `gz validate --bullet-retention`."

## Path note

Brief lists `docs/user/manpages/gz-validate.md` as the allowed manpage path.
The canonical manpage for `gz validate` is `docs/user/manpages/validate.md`
(pre-existing, contains all existing `--*` flag sections). This plan updates
`validate.md` — the same practice as OBPI-0.0.32-07. The brief path is a
naming artifact; `validate.md` is the operational surface.

## Files

**New files (allowed by brief):**
- `src/gzkit/governance/trust_audits/bullet_retention.py` — validator module
- `tests/governance/test_bullet_retention.py` — Gate-2 TDD asset

**Modified files:**
- `src/gzkit/governance/trust_audits/__init__.py` — add `validate_bullet_retention` re-export
- `src/gzkit/cli/parser_maintenance.py` — register `--bullet-retention` flag
- `docs/user/manpages/validate.md` — add `--bullet-retention` section and Scopes Reference row

## Steps

### Step 1: Author tests (TDD Red phase)

Create `tests/governance/test_bullet_retention.py` using temp directories with
synthetic `advisory-rules-audit.md` and per-turn surface files.

Test cases derived from brief REQs (no implementation-first):

- `TestBulletRetentionPresent` (REQ-0.0.33-01-01): Mechanical/Promotable
  bullet verbatim in surface → no errors, exit 0.
- `TestBulletRetentionMissing` (REQ-0.0.33-01-02): Mechanical/Promotable
  bullet absent from surface → one `ValidationError(type="bullet_retention")`,
  names missing bullet and source classification.
- `TestBulletRetentionJudgment` (REQ-0.0.33-01-03): Judgment/Ambiguous bullets
  in scorecard → NOT enforced (empty error list).
- `TestBulletRetentionImport` (REQ-0.0.33-01-04): `gzkit.governance.trust_audits.validate_bullet_retention` resolves and is callable.
- `TestBulletRetentionCLIFlag` (REQ-0.0.33-01-05): `--bullet-retention` present
  in `gz validate --help` output.

Tests use a shared `_make_tree(tmp, scorecard_content, surface_content)` helper
that writes synthetic files into a temp project root. No live filesystem reads
in unit tests — all fixtures are synthetic.

### Step 2: Implement `bullet_retention.py`

```
validate_bullet_retention(project_root: Path) -> list[ValidationError]
```

Internal helpers (all private, `_`-prefixed):

- `_parse_scorecard(audit_path: Path) -> list[tuple[str, str]]`
  Parse every `| N | rule text | **Classification** | notes |` table row from
  `docs/governance/advisory-rules-audit.md`. Return `(rule_text, classification)`
  pairs. Skip header, separator, and non-table lines. Classification is the
  de-bolded inner text (strip `**`).

- `_collect_surface_corpus(project_root: Path) -> str`
  Read `AGENTS.md`, `CLAUDE.md`, and all `*.md` under `.claude/rules/` into one
  concatenated string. Return empty string if none exist (fail-open for new
  projects).

- `_normalize(text: str) -> str`
  Strip leading `- `, `* `, `1.` bullet markers; collapse runs of whitespace
  to single space; strip leading/trailing whitespace. Preserves semantic text.

- `_is_enforced(classification: str) -> bool`
  True iff classification.lower() in {"mechanical", "promotable"}.

Flow: parse scorecard → for each enforced bullet → normalize → check substring
in normalized corpus → emit ValidationError if absent.

### Step 3: Wire into `trust_audits/__init__.py`

Add import and `__all__` entry for `validate_bullet_retention` following the
existing `validate_advisor_proof_binding` pattern.

### Step 4: Register CLI flag in `parser_maintenance.py`

Add `--bullet-retention` to the validate argument group (near `--distribution`,
`--advisor-proof-binding`). Dispatch: call `validate_bullet_retention(project_root)`,
format ValidationErrors per existing pattern, exit 3 on errors.

Short help text: `"Assert every Mechanical/Promotable bullet in advisory-rules-audit.md is verbatim in per-turn surface (ADR-0.0.33-01)."`.

### Step 5: Update `docs/user/manpages/validate.md`

Add `### --bullet-retention` section with:
- What it checks
- Format: parsed from `docs/governance/advisory-rules-audit.md` table
- Normalization: whitespace/marker difference ok; semantic match required
- Exit codes table
- Two examples (clean tree → exit 0; missing bullet → exit 3)

Update the Scopes Reference table: add `--bullet-retention` row (opt-in).

### Step 6: ARB quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_bullet_retention -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --bullet-retention   # must exit 0 on clean tree
uv run mkdocs build --strict
```

## Destination-in-mind disclosure (Step 6a)

Before exploring the codebase, I expected:
- A simple substring check against the per-turn surface
- Parse the 4-column scorecard table with a regex split on `|`
- Use the same `validate_X(project_root: Path) -> list[ValidationError]` signature established by `validate_advisor_proof_binding`

## Rejected alternatives

- **Read `.gzkit/rules/**` instead of `.claude/rules/**`**: The per-turn surface is
  what Claude Code loads (`.claude/rules/**`), not the canonical source. The
  `--surfaces` validator already ensures sync parity; checking the canonical source
  would double-check the wrong layer.
- **Hard-code Mechanical/Promotable bullet list in Python**: REQ-04 explicitly
  forbids this; the scorecard is the source of truth.
- **Use a BDD `.feature` file for all REQs**: Not needed at OBPI stage; unit tests
  cover all 5 REQs. BDD is deferred to ADR-0.0.33 closeout.
