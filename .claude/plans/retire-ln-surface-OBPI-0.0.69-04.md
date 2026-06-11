# Implementation Plan: OBPI-0.0.69-04-retire-ln-closeout-proof-binding-surface

**OBPI:** OBPI-0.0.69-04-retire-ln-closeout-proof-binding-surface
**ADR:** ADR-0.0.69-channels-first-closeout-proof
**Lane:** Heavy

**Approach committed before plan was written:** Strip-guard-then-delete: collect all `ln:`-carrying briefs by grep, strip `ln:` blocks using `_strip_existing_ln` before the function is deleted, then delete all production code and tests in one pass, then update docs.

**Rejected alternatives:**
1. Schema-first deletion (delete schema, then model, then flag) — rejected because `_strip_existing_ln` must run while still in `obpi_complete.py`; decoupling the strip from the deletion creates ordering ambiguity that leads to leftover `ln:` blocks.
2. Keep `ln:` schema as deprecated-inert (Option B from ADR-0.0.69 § Alternatives Considered) — explicitly rejected by the 2026-06-09 operator sunset ruling: storing derived evidence as canon is the Layer-3-as-source-of-truth anti-pattern.

---

## Files

| Path | Action |
|------|--------|
| `tests/governance/test_retire_ln_surface.py` | **Create** — REQ-derived absence tests (RED before Step 3, GREEN after) |
| `src/gzkit/governance/trust_audits/closeout_proof_binding.py` | **DELETE** |
| `src/gzkit/governance/trust_audits/__init__.py` | **Modify** — remove `closeout_proof_binding` import + re-export |
| `src/gzkit/governance/brief_structure.py` | **Modify** — delete `ReqEvidence` class and `BriefStructure.ln` field |
| `src/gzkit/schemas/obpi_brief_structure.json` | **Modify** — delete `ln` property |
| `src/gzkit/cli/parser_maintenance.py` | **Modify** — delete `--closeout-proof-binding` flag + `dest` + arg-namespace line |
| `src/gzkit/commands/validate_cmd.py` | **Modify** — delete `check_closeout_proof_binding` parameter, dispatch entry, and scope-list entries (all occurrences) |
| `src/gzkit/commands/obpi_complete.py` | **Modify** — delete `_inject_ln_block` call (line ~1143) and the three producer functions (~1465–1523) |
| `tests/governance/test_closeout_proof_binding.py` | **DELETE** (333 lines — tests for the retired module) |
| 22 `ln:`-carrying OBPI briefs (enumerate by grep) | **Modify** — strip `ln:` frontmatter block in one pass |
| `docs/user/manpages/validate.md` | **Modify** — remove `--closeout-proof-binding` section + table entry |
| `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` | **Modify** — remove `ln:`/`--closeout-proof-binding` paragraph (line ~328) |
| `docs/design/restore-health-convergence-roadmap.md` | **Modify** — note that `ln:` retirement has landed, update count |
| ADR-0.0.63 package OBPI briefs (if `ln:`-carrying) | **Modify** — stripped in the brief-strip pass above |

---

## Steps

### Step 1: Write RED tests asserting absence (TDD)

**File:** `tests/governance/test_retire_ln_surface.py`

These tests are RED before Steps 3–4; GREEN after.

1. `TestRetireLnSurface.test_closeout_proof_binding_module_absent`
   - `with self.assertRaises(ImportError): import gzkit.governance.trust_audits.closeout_proof_binding`
   - Covers REQ-0.0.69-04-01

2. `TestRetireLnSurface.test_req_evidence_and_ln_field_absent`
   - Assert `not hasattr(gzkit.governance.brief_structure, "ReqEvidence")`
   - Assert `"ln"` is not in `BriefStructure.model_fields`
   - Covers REQ-0.0.69-04-01

3. `TestRetireLnSurface.test_closeout_proof_binding_flag_unknown`
   - Build parser via `build_validate_parser()` and assert `--closeout-proof-binding` is not registered (ArgumentError on parse attempt)
   - Covers REQ-0.0.69-04-02

4. `TestRetireLnSurface.test_inject_ln_functions_absent`
   - Import `gzkit.commands.obpi_complete`; assert `_inject_ln_block`, `_render_ln_block`, `_strip_existing_ln` are not present as module attributes
   - Covers REQ-0.0.69-04-03

5. `TestRetireLnSurface.test_ln_frontmatter_fails_validate_documents`
   - Write a tmp brief with `ln: []` in YAML frontmatter + valid required fields
   - Run `gz validate --documents` against a tmp root containing it
   - Assert exit 3 (schema `additionalProperties: false` rejects `ln`)
   - Covers REQ-0.0.69-04-04

Run: `uv run -m unittest tests/governance/test_retire_ln_surface.py -v` → expect 5 failures (RED).

### Step 2: Strip ln: blocks from all ln:-carrying briefs

Before deleting `_strip_existing_ln`:

1. Enumerate: `grep -r "^ln:" docs/design/adr --include="*.md" -l` — ground-truth count (expect 22, not 19 as the brief states; the brief itself warns to trust grep over its own count).
2. For each file: read frontmatter, apply `_strip_existing_ln`, write back.
3. Verify: `grep -r "^ln:" docs/design/adr --include="*.md" | wc -l` → 0.
4. Run `uv run gz validate --documents` to confirm clean.

> REQ-0.0.69-04-05 support proof: `artifact_edited` ledger events for stripped briefs + `gz validate --documents` exit 0.

### Step 3: Delete production code

Delete in this order:

**3a.** Delete `src/gzkit/governance/trust_audits/closeout_proof_binding.py`.

**3b.** Edit `src/gzkit/governance/trust_audits/__init__.py`:
- Remove `from gzkit.governance.trust_audits.closeout_proof_binding import (validate_closeout_proof_binding,)` (lines ~59-60)
- Remove `"validate_closeout_proof_binding"` from `__all__` (line ~192)

**3c.** Edit `src/gzkit/governance/brief_structure.py`:
- Delete `ReqEvidence` class (~lines 23-53)
- Delete `BriefStructure.ln` field (~line 86) and its `Field(...)` declaration

**3d.** Edit `src/gzkit/schemas/obpi_brief_structure.json`:
- Delete the `ln` property block (~lines 61-85)

**3e.** Edit `src/gzkit/cli/parser_maintenance.py`:
- Delete `"--closeout-proof-binding"` `add_argument` call (~lines 601-602)
- Delete `dest="check_closeout_proof_binding"` line (same block)
- Delete `check_closeout_proof_binding=a.check_closeout_proof_binding` from the args namespace line (~line 802)

**3f.** Edit `src/gzkit/commands/validate_cmd.py` (all occurrences):
- Delete `check_closeout_proof_binding: bool = False` parameter from both function signatures (~lines 193, 1170)
- Delete `"closeout_proof_binding": check_closeout_proof_binding` from kwargs dicts (~lines 271, 1437)
- Delete `"closeout_proof_binding": lambda: trust_audits.validate_closeout_proof_binding(...)` dispatch entry (~line 389)
- Delete `"closeout_proof_binding"` from scope-list entries (~lines 875, 933)
- Delete `check_closeout_proof_binding=check_closeout_proof_binding` from call site (~line 1346)

**3g.** Edit `src/gzkit/commands/obpi_complete.py`:
- Delete the `_inject_ln_block(...)` call at ~line 1143
- Delete functions `_render_ln_block`, `_strip_existing_ln`, `_inject_ln_block` (~lines 1465–1523)

Run `uv run ruff check . --fix && uv run ruff format .` after all 3g edits to fix unused-import lint drift.

### Step 4: Delete binding tests → confirm RED→GREEN

1. Delete `tests/governance/test_closeout_proof_binding.py`.
2. Run `uv run -m unittest tests/governance/test_retire_ln_surface.py -v` → expect all 5 PASS (GREEN).
3. Run `uv run gz arb step --name unittest -- uv run -m unittest -q` → full suite green.

### Step 5: Update docs

**5a.** `docs/user/manpages/validate.md`:
- Remove the `### --closeout-proof-binding` section (~lines 1050-1073)
- Remove `--closeout-proof-binding` row from the scope table (~line 1462)

**5b.** `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`:
- Remove paragraph at ~line 328 instructing operators to run `gz validate --closeout-proof-binding`

**5c.** `docs/design/restore-health-convergence-roadmap.md`:
- Update §3 sunset rationale to note retirement landed via OBPI-0.0.69-04
- Update "19 briefs" to the actual stripped count

**5d.** Check `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/*.md` for any current-instruction (non-attested) text pointing operators to run `--closeout-proof-binding`; update those. Historical attested records (`ADR-CLOSEOUT-FORM.md` attestation text) are preserved verbatim.

Run `uv run mkdocs build --strict` after all doc edits.

> REQ-0.0.69-04-06 support proof: `artifact_edited` ledger events + `mkdocs build --strict` + `gz cli audit` + `gz validate --cli-alignment` all exit 0.

### Step 6: Supersede #599, strike #593 premise

6a. Supersede GHI #599: comment "Superseded by ADR-0.0.69 OBPI-0.0.69-04. The `_inject_ln_block`/`_render_ln_block`/`_strip_existing_ln` producer was deleted; all `ln:` blocks stripped from 22 briefs. Closeout proof now lives exclusively in `gz validate --closeout-proof`."

6b. Strike GHI #593 premise: comment "Premise struck by ADR-0.0.69 OBPI-0.0.69-04 — the stored `ln:` block no longer exists, so the attested-record-edit-doctrine question is moot."

### Step 7: Full verification pass

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --cli-alignment
uv run gz cli audit
uv run mkdocs build --strict
```

### Step 8: Present OBPI Acceptance Ceremony
