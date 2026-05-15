# Plan: OBPI-0.0.33-03 Pointer Integrity Validator

**OBPI:** OBPI-0.0.33-03-pointer-integrity-validator
**ADR:** ADR-0.0.33-agent-control-surface-fidelity
**Lane:** Heavy
**Checklist Item:** #3 — Pointer-integrity validator (`gz validate --pointer-anchors`) — parse `> See [...]` blockquotes, resolve anchors, reverse-check `<!-- lifted-from: -->` back-pointers, exit 3 on unresolved

## Context

ADR-0.0.33 Invariant 3 requires a pointer-integrity validator that:
- Walks the per-turn surface corpus (AGENTS.md, CLAUDE.md, .claude/rules/**)
- Parses every `> See [...]` blockquote line containing a markdown link with `#anchor`
- Resolves each `path#anchor` to an existing heading in the destination file using mkdocs slugification (lowercase, strip non-alphanumeric except hyphens, replace spaces with hyphens)
- Reverse-checks: every destination file referenced by a forward pointer must carry a `<!-- lifted-from: <source-path>#<anchor> -->` comment
- Exits 3 on any unresolved pointer OR missing back-pointer
- Error messages must name both halves: source `file:line` AND destination path

The per-turn surface already contains many `> See [...]` pointers: AGENTS.md lines 69, 82, 117, 334 and .claude/rules/** files (agent-failure-modes.md, tool-skill-runbook-alignment.md, security-sensitivity.md, complexity-doctrine.md, cross-platform.md, tests.md, complexity-thresholds.md). The validator must handle all of them correctly.

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Approach: follow the bullet_retention.py / surface_weight.py pattern exactly — single-responsibility module in trust_audits/, re-export from __init__.py, wire into parser_maintenance.py and validate_cmd.py, update manpage. The pointer parser uses a regex on blockquote lines; anchor resolution uses a regex on destination headings; contextlib.suppress for OS errors.

## Rejected alternatives

- Using a full markdown parser (mistune/markdown-it): rejected — stdlib-first doctrine; a regex on `> See [link](path#anchor)` blockquote lines is sufficient and bounded
- Checking all markdown links (not just blockquote-`See` form): rejected — REQ-4 explicitly bounds scope to `> See [...]` blockquote form only; widening breaks the corpus boundary contract
- Walking all destination headings via a third-party library: rejected — mkdocs slug rule is simple and can be implemented in one function using stdlib `re`

## Files

### New
- `src/gzkit/governance/trust_audits/pointer_integrity.py`
- `tests/governance/test_pointer_integrity.py`

### Modified
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_pointer_integrity`
- `src/gzkit/cli/parser_maintenance.py` — add `--pointer-anchors` flag and dispatch
- `src/gzkit/commands/validate_cmd.py` — add `check_pointer_anchors` param + runner at all 4 threading points
- `docs/user/manpages/validate.md` — add `--pointer-anchors` section

## Steps

### Step 1: TDD — Write failing tests (Red phase)

Write `tests/governance/test_pointer_integrity.py` with synthetic temp-tree fixtures covering all 5 REQs:

- **REQ-0.0.33-03-01**: Forward pointer with matching destination heading → exits 0
  - `@covers("REQ-0.0.33-03-01")`
  - Temp tree: AGENTS.md with `> See [desc](docs/governance/some-doc.md#some-heading)`, destination file with `## Some Heading` heading, AND `<!-- lifted-from: AGENTS.md#some-heading -->` back-pointer → validate returns `[]`

- **REQ-0.0.33-03-02**: Pointer to non-existent file or absent anchor → exit-3 ValidationError naming both halves
  - `@covers("REQ-0.0.33-03-02")`
  - Sub-case A: destination path does not exist → error with type="pointer_anchors", message includes source file:line and destination
  - Sub-case B: destination exists but anchor slug absent → same error shape

- **REQ-0.0.33-03-03**: Destination exists and anchor resolves but lacks `<!-- lifted-from: -->` → exit-3 ValidationError naming missing back-pointer
  - `@covers("REQ-0.0.33-03-03")`
  - Temp tree with valid forward pointer + heading but no back-pointer comment → error type="pointer_anchors"

- **REQ-0.0.33-03-04**: Non-blockquote `[link](path#anchor)` NOT checked
  - `@covers("REQ-0.0.33-03-04")`
  - Inline link without `> See` prefix → validate returns `[]` (not checked)

- **REQ-0.0.33-03-05**: `validate_pointer_integrity` importable from `gzkit.governance.trust_audits`
  - `@covers("REQ-0.0.33-03-05")`
  - Import and assert callable; check function signature accepts `project_root: Path`

All tests use `tempfile.TemporaryDirectory()` — never touch the live repo root.

### Step 2: Implement pointer_integrity.py (Green phase)

Create `src/gzkit/governance/trust_audits/pointer_integrity.py`:

```python
"""Pointer-integrity validator — ADR-0.0.33 Invariant 3."""
```

Key components:
- `validate_pointer_integrity(project_root: Path) -> list[ValidationError]`
- `_collect_surface_corpus(project_root)` — yields (path, line_no, line) for AGENTS.md, CLAUDE.md, .claude/rules/**
- `_parse_see_pointers(path, lines)` — regex `^>\s+See\s+.*\(([^)]+#[^)]+)\)` on each blockquote line, returns list of (line_no, dest_path_str, anchor_str)
- `_slugify(text)` — mkdocs-compatible: lowercase, `re.sub(r'[^\w\s-]', '', text)`, `re.sub(r'\s+', '-', text)`, collapse hyphens
- `_heading_slugs(path)` — read destination file, extract `## Heading` lines, return set of slugs
- `_has_back_pointer(dest_path, source_path, anchor)` — check destination for `<!-- lifted-from: <source_path>#<anchor> -->`
- Each pointer failure → `ValidationError(type="pointer_anchors", artifact=source_file:line, message=...both halves named...)`

### Step 3: Re-export from __init__.py

Add after the `validate_surface_weight` import:
```python
from gzkit.governance.trust_audits.pointer_integrity import validate_pointer_integrity
```

### Step 4: Wire CLI flag in parser_maintenance.py

After the `--surface-weight` block (line 579–584), add:
```python
p_validate.add_argument(
    "--pointer-anchors",
    dest="check_pointer_anchors",
    action="store_true",
    help="Pointer-integrity audit: resolve > See [...] anchors + lifted-from back-pointers (ADR-0.0.33-03).",
)
```

In `set_defaults` lambda (after `check_surface_weight=a.check_surface_weight`):
```python
check_pointer_anchors=a.check_pointer_anchors,
```

### Step 5: Wire dispatch in validate_cmd.py

Four threading points:

**A. `_collect_errors()` signature** (after line 421, `check_surface_weight: bool = False`):
```python
check_pointer_anchors: bool = False,
```

**B. `_collect_errors()` explicit_scopes dict** (after line 478, `"surface_weight": check_surface_weight`):
```python
"pointer_anchors": check_pointer_anchors,
```

**C. `_explicit_scope_runners()` dict** (after line 568, `"surface_weight": lambda...`):
```python
"pointer_anchors": lambda: trust_audits.validate_pointer_integrity(project_root),
```

**D. `validate()` function** — three sub-points:
- signature: add `check_pointer_anchors: bool = False,` after `check_surface_weight: bool = False,` (line 1293)
- `_other_scopes_active` list: add `check_pointer_anchors,` after `check_surface_weight,` (line 1362)
- `_collect_errors()` call: add `check_pointer_anchors=check_pointer_anchors,` after `check_surface_weight=check_surface_weight,` (line 1432)
- `checks` dict: add `"pointer_anchors": check_pointer_anchors,` after `"surface_weight": check_surface_weight,` (line 1504)

### Step 6: Update manpage

In `docs/user/manpages/validate.md`, add a `--pointer-anchors` section following the same pattern as `--bullet-retention` and `--surface-weight`. Include: flag name, description, exit codes (0 = clean, 3 = unresolved pointer or missing back-pointer), and a usage example.

### Step 7: Present OBPI Acceptance Ceremony

Run quality checks (arb:ruff, arb:typecheck, arb:unittest) and present Stage 4 evidence for human attestation.
