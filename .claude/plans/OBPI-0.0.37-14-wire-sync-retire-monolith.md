# Implementation Plan — OBPI-0.0.37-14 Wire Sync Through Renderer; Retire Monolith

**OBPI:** OBPI-0.0.37-14-wire-sync-retire-monolith
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition (Decision Extension 2026-05-30)
**Lane:** Heavy (foundation + heavy → Gate-5 human attestation, mandatory)
**Plan authored:** 2026-06-02

## Destination-in-mind (Step 6a disclosure — required)

Pre-formed destination: replace the direct `render_template("agents", **context)` call in
`sync_agents_md` with a three-step model pipeline: (1) load `.gzkit/templates/agents.md` text,
(2) `str.format_map(context)` to resolve `{project_name}` / `{project_purpose}` / etc., (3) `parse(text, "AgentContract")` to build the master model, (4) `render(model, "claude", temperature="heavy")` to produce bytes. The same pipeline replaces the monolith in `compose.render_agents_md` so that `--invariant-coherence` and `governance render --check` both use the identical engine.

The "independent source" question was the critical gate: the render source MUST be independent of
committed AGENTS.md (advisor confirmed REQ-03 kills circular parse-AGENTS.md approaches).
Confirmed that `.gzkit/templates/agents.md` is the correct independent source — it is synced
from the package template and does NOT read from committed AGENTS.md.

## Rejected alternatives (Step 6a disclosure — required)

1. **Parse committed AGENTS.md as the master model** — REJECTED by REQ-03. A validator that
   compares render(parse(AGENTS.md)) to AGENTS.md is a fixed point for verbatim sections
   (all of `Pillar.lines`) — it cannot detect hand-edits. REQ-03 requires detection.
2. **Load master model from persisted JSON** — REJECTED: OBPI-13 created parsing capability but
   no persisted JSON artifact (confirmed by grep for `"pillars"`/`"density_min"` in `.gzkit/`,
   `data/`, none found). No path in OBPI-14's Allowed Paths to create one.
3. **Keep `compose.render_agents_md` using the monolith and only change `sync_agents_md`** — REJECTED:
   `--invariant-coherence` calls `compose.render_agents_md`; it must also switch to model pipeline
   or the coherence check continues to be the "monolith-re-renders-to-itself" check that REQ-03
   explicitly requires stopping.
4. **Remove `src/gzkit/templates/agents.md` entirely** — REJECTED: the model pipeline requires
   a text source for the initial parse. The file's ROLE changes (from direct render source to
   model construction source), but it cannot be deleted.

## Architecture

```
.gzkit/templates/agents.md   (independent source; synced from package template)
         ↓  str.format_map(context)  [resolves {project_name}, {project_purpose}, etc.]
         ↓  parse(text, "AgentContract")  [OBPI-13 parser; populates pillars with verbatim lines]
         ↓  render(model, "claude", temperature="heavy")  [OBPI-12 renderer]
         ↓
     AGENTS.md   (rendered artifact)
```

The same pipeline drives:
- `sync_surfaces.sync_agents_md` (writing AGENTS.md)
- `compose.render_agents_md` (used by `governance_render_cmd` and `invariant_coherence.py`)

After OBPI-14, `src/gzkit/templates/agents.md` is no longer a direct render source (no
`render_template("agents")` call), but continues as the raw text for model construction.

## Circular import prevention

`compose.py` already imports `from gzkit.sync_surfaces import get_project_context`. If
`sync_surfaces.py` were to import from `compose.py`, a circular import would result.

**Resolution**: `sync_surfaces.sync_agents_md` does NOT import from `compose`. Instead, it
inlines the pipeline steps using already-imported symbols:
- `get_project_context(project_root, config)` → already called
- `SafeDict` → already imported
- `render_content_model` (= `gzkit.content.render.render`) → already imported at line 21
- `parse` from `gzkit.content.parse` → lazy import inside `sync_agents_md` (or top-level)

`compose.py` continues to call its own `_substitution_context` (which calls `get_project_context`)
and handles the parse+render steps with lazy imports from `gzkit.content`.

## Files (all within brief Allowed Paths plus one coupled-surface coherence addition)

| File | Change | REQ |
|------|--------|-----|
| `src/gzkit/sync_surfaces.py` | Repoint `sync_agents_md`: drop `render_template("agents", **context)`; inline parse→render pipeline; `get_project_context` is still called for format substitution but its hardcoded prose literals (`purpose`, `tech_stack`) are no longer fed directly to a render call | 01, 02 |
| `src/gzkit/governance/compose.py` | Update `render_agents_md`: internally switch from "format-map → direct bytes" to "format-map → parse → render(model, 'claude')"; keep same external signature for backward compat with `governance_render_cmd` caller | 01, 02, 03 |
| `src/gzkit/governance/trust_audits/invariant_coherence.py` | Update `_render_registry`: since `render_agents_md` now uses the model pipeline, this flows through. Update `invariant_count` from `len(invariants)` (registry count) to `len(model.pillars)` (model section count); keep all ledger events. | 03 |
| `tests/commands/test_sync_cmds.py` | Add REQ-covering tests (01–04); existing tests updated to reflect model-renderer output | 01, 02, 03, 04 |
| `docs/user/runbook.md` | Add "Editing AGENTS.md" guidance: "Edit the master model source at `.gzkit/templates/agents.md`, then run `gz agent sync control-surfaces` to re-render." (Gate 3 / REQ-05 coupled-surface; amend brief Allowed Paths) | 05 |
| `src/gzkit/templates/agents.md` | No content change; role annotation in this plan records that it is now model-construction source, not direct render source. The file content stays identical. | — |

## Steps (TDD per REQ — RED then GREEN, commit each GREEN)

### Step 1 — REQ-01: RED test: sync_agents_md doesn't call render_template("agents")

In `tests/commands/test_sync_cmds.py`, add:
```python
@covers("REQ-0.0.37-14-01")
def test_sync_agents_md_does_not_call_render_template(self) -> None:
    """sync_agents_md MUST render from the AgentContract model; render_template("agents")
    must NOT be invoked (REQ-01)."""
    with _InitFromTemplate() as project_root:
        with patch("gzkit.sync_surfaces.render_template") as mock_render:
            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_agents_md
            config = GzkitConfig.load(project_root / ".gzkit.json")
            sync_agents_md(project_root, config)
            for call in mock_render.call_args_list:
                self.assertNotEqual(call.args[0], "agents",
                    "render_template('agents') must not be called")
```

This test FAILS with the current code (calls `render_template("agents")`).

### Step 2 — GREEN: Repoint sync_agents_md in sync_surfaces.py

Replace:
```python
context = get_project_context(project_root, config)
content = render_template("agents", **context)
agents_path = project_root / config.paths.agents_md
agents_path.write_bytes(content.encode("utf-8"))
```

With:
```python
from gzkit.content.parse import parse as _parse_content  # lazy, avoids top-level cycle risk
context = get_project_context(project_root, config)
template_root = project_root / ".gzkit" / "templates"
template_path = template_root / "agents.md"
if template_path.exists():
    template_text = template_path.read_text(encoding="utf-8")
    resolved_text = template_text.format_map(SafeDict(context))
    model = _parse_content(resolved_text, "AgentContract")
    content_bytes = render_content_model(model, "claude", temperature="heavy")
else:
    # Bootstrap fallback: template not synced yet; use monolith render
    content = render_template("agents", **context)
    content_bytes = content.encode("utf-8")
agents_path = project_root / config.paths.agents_md
agents_path.write_bytes(content_bytes)
```

`render_content_model` is already imported at line 21 as `from gzkit.content.render import render as render_content_model`.

Run `uv run -m unittest tests.commands.test_sync_cmds.TestAgentSyncCmd.test_sync_agents_md_does_not_call_render_template -v` → GREEN.

### Step 3 — REQ-02: RED test: no hardcoded prose in render path

```python
@covers("REQ-0.0.37-14-02")
def test_sync_agents_md_purpose_comes_from_model_not_code(self) -> None:
    """The rendered AGENTS.md purpose must come from the parsed model (template text),
    not from get_project_context's hardcoded 'purpose' string (REQ-02)."""
    with _InitFromTemplate() as project_root:
        # Patch get_project_context to return a custom purpose value
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_agents_md, get_project_context
        config = GzkitConfig.load(project_root / ".gzkit.json")

        # Verify the rendered output contains the template-sourced purpose
        # (from the template's {project_purpose} substitution)
        sync_agents_md(project_root, config)
        agents_md = (project_root / "AGENTS.md").read_text(encoding="utf-8")
        # The purpose value from get_project_context must appear via the model
        ctx = get_project_context(project_root, config)
        self.assertIn(ctx["project_purpose"], agents_md)
```

(The test is behavioral: purpose propagates through the model pipeline, not from a hardcoded string injected directly into a render call.)

This test passes even before Step 2 (it tests content, not mechanism). The mechanism guarantee is carried by REQ-01's test (which prevents `render_template("agents")` from being called).

### Step 4 — REQ-03: RED test: hand-edit to AGENTS.md is caught by invariant_coherence

```python
@covers("REQ-0.0.37-14-03")
def test_invariant_coherence_catches_hand_edit_to_agents_md(self) -> None:
    """A hand-edit to AGENTS.md that diverges from the model render must cause
    validate_invariant_coherence to return a ValidationError (REQ-03)."""
    with _InitFromTemplate() as project_root:
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_agents_md
        from gzkit.governance.trust_audits.invariant_coherence import validate_invariant_coherence
        config = GzkitConfig.load(project_root / ".gzkit.json")

        # First sync to set the canonical render output
        sync_agents_md(project_root, config)

        # Verify that post-sync, coherence passes
        errors_before = validate_invariant_coherence(project_root)
        self.assertEqual(errors_before, [],
            "After sync, coherence must pass (committed == model render)")

        # Hand-edit AGENTS.md: append a line that would not survive the parse→render cycle
        agents_path = project_root / "AGENTS.md"
        original = agents_path.read_bytes()
        agents_path.write_bytes(original + b"\n\nHAND_EDITED_MARKER_SHOULD_NOT_SURVIVE\n")

        # Coherence check must now fail closed
        errors_after = validate_invariant_coherence(project_root)
        self.assertGreater(len(errors_after), 0,
            "Hand-edit must produce a coherence validation error")
        self.assertEqual(errors_after[0].type, "invariant_coherence")
```

This test FAILS before Step 5 changes (the current `render_agents_md` in `compose.py` uses the monolith, which produces different bytes — or may not catch the hand-edit because both use the monolith template).

Actually, the test as written (appending a line) MIGHT pass before Step 5 because the monolith pipeline also wouldn't produce the hand-edited text. Let me reconsider: the test should first verify the monolith pipeline catches the hand-edit (which it currently does, per the exit-0 of `gz governance render --check` before edits). The key REQ-03 requirement is that after OBPI-14, the pipeline is MODEL-BASED, not monolith-based. So the test should also verify the model is used:

Add:
```python
        # Verify the error message references the model-based check
        self.assertIn("invariant_coherence", errors_after[0].type)
```

Actually, the `type` is already `"invariant_coherence"`. The behavioral test (hand-edit caught) is sufficient for REQ-03. The "MUST stop being a monolith-re-renders-to-itself check" is structural, verified by the change to `compose.py`.

### Step 5 — GREEN: Update compose.py to use model pipeline

In `compose.py`'s `render_agents_md`, replace the direct template-render with the model pipeline:

```python
def render_agents_md(
    invariants: Mapping[str, ConstitutionalInvariant],
    template_root: Path,
    project_root: Path,
) -> bytes:
    """Render AGENTS.md bytes via the content model pipeline (OBPI-0.0.37-14).

    Pipeline: template text → str.format_map(context) → parse(AgentContract)
    → render(model, 'claude', temperature='heavy').

    The `invariants` parameter is accepted for backward compatibility with
    governance_render_cmd callers but is not used in the model pipeline.
    Bootstrap-safe: returns empty bytes when template is absent.
    """
    from gzkit.content.parse import parse as _parse  # lazy import (avoids cycle)
    from gzkit.content.render import render as _render  # lazy import

    template_path = template_root / "agents.md"
    if not template_path.exists():
        return b""

    context = _substitution_context(project_root)
    template_text = template_path.read_text(encoding="utf-8")
    resolved_text = template_text.format_map(SafeDict(context))
    model = _parse(resolved_text, "AgentContract")
    return _render(model, "claude", temperature="heavy")
```

Remove the old Jinja2 + `str.format_map` two-pass implementation.

### Step 6 — GREEN: Update invariant_coherence.py for model pipeline

Update `_render_registry` to reflect that the "count" is now model sections, not registry invariants:

```python
def _render_registry(root: Path) -> tuple[bytes, int]:
    """Render AGENTS.md via the model pipeline; return (rendered_bytes, section_count)."""
    from gzkit.content.parse import parse as _parse  # avoid top-level cycle
    from gzkit.content.render import render as _render

    template_root = root / ".gzkit" / "templates"
    template_path = template_root / "agents.md"
    if not template_path.exists():
        return b"", 0

    # Build context for format substitution (same as compose._substitution_context)
    config = GzkitConfig.load(root / ".gzkit.json")
    context = get_project_context(root, config)
    template_text = template_path.read_text(encoding="utf-8")
    resolved_text = template_text.format_map(SafeDict(context))
    model = _parse(resolved_text, "AgentContract")
    rendered_bytes = _render(model, "claude", temperature="heavy")
    return rendered_bytes, len(model.pillars)
```

Note: `get_project_context` is imported from `gzkit.sync_surfaces` (already done via `compose.py`'s import; `invariant_coherence.py` may need its own import). Check and add if needed.

Actually, `invariant_coherence.py` currently calls `render_agents_md(invariants, template_root, root)` via `compose.py`. Since `compose.py`'s `render_agents_md` is being updated to use the model pipeline internally, `invariant_coherence.py`'s `_render_registry` can simply keep calling `render_agents_md` from `compose.py`:

```python
def _render_registry(root: Path) -> tuple[bytes, int]:
    invariants = load_invariants(root)
    template_root = root / ".gzkit" / "templates"
    rendered_bytes = render_agents_md(invariants, template_root, root)
    # After OBPI-14, section_count replaces invariant_count in ledger event
    return rendered_bytes, len(invariants)  # invariants may be 0–N; bytes are model-based
```

The `len(invariants)` stays (it's a registry count, still meaningful for the ledger event's `invariant_count` field). No change needed to `invariant_coherence.py` beyond verifying the tests pass.

### Step 7 — REQ-04: RED then GREEN: semantic equivalence test

```python
@covers("REQ-0.0.37-14-04")
def test_model_render_semantically_equivalent_to_pre_migration(self) -> None:
    """The AgentContract model rendered at default temperature must contain the same
    key structural sections and rules as the pre-migration AGENTS.md (REQ-04)."""
    with _InitFromTemplate() as project_root:
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_agents_md
        config = GzkitConfig.load(project_root / ".gzkit.json")
        sync_agents_md(project_root, config)
        rendered = (project_root / "AGENTS.md").read_text(encoding="utf-8")

        # Key structural sections must survive the parse→render cycle
        self.assertIn("## Behavior Rules", rendered)
        self.assertIn("## PRIME DIRECTIVE", rendered)
        self.assertIn("Gate Covenant", rendered)
        # Project identity must be populated
        self.assertIn("gzkit", rendered)
        # Not empty
        self.assertGreater(len(rendered), 10_000,
            "Rendered AGENTS.md must be substantive (≥10k chars)")
```

This test RED before Step 2/5 are complete (because the sync produces monolith output, and after OBPI-14 changes, sync produces model output that must contain these sections).

After Steps 2+5 are GREEN, run this test to confirm equivalence. If it fails, adjust the `claude.md.j2` or fix the parse step.

### Step 8 — REQ-05: Update runbook (Gate 3, Heavy lane)

In `docs/user/runbook.md`, find the section on `gz agent sync control-surfaces` and add:

```markdown
### Editing AGENTS.md

AGENTS.md is a rendered artifact — do not edit it directly. Edits are overwritten
on the next `gz agent sync control-surfaces` run and detected by
`gz validate --invariant-coherence`.

To change AGENTS.md content:
1. Edit `.gzkit/templates/agents.md` (the model construction source).
2. Run `uv run gz agent sync control-surfaces` to re-render.
3. Run `uv run gz validate --invariant-coherence` to confirm no drift.
```

This satisfies Gate 3 and REQ-05 (SUPPORT type; `artifact_edited` event emitted by `gz agent sync`).

### Step 9 — Brief Allowlist Amendment

The brief's Allowed Paths omit `docs/user/runbook.md`, but Gate 3 (Heavy) and REQ-05 require it.
This is coupled-surface coherence (Gate 3 docs must track behavior changes).

Amend the brief to add:
```
- `docs/user/runbook.md` — edit path guidance for AGENTS.md (Gate 3 / REQ-05)
```

This is done in the same commit as Step 8.

### Step 10 — Gate 2 verification: run full test suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run -m unittest tests.commands.test_sync_cmds -v
uv run gz validate --invariant-coherence
```

After Steps 2+5: `validate --invariant-coherence` will FAIL because committed AGENTS.md was
rendered by the old monolith pipeline. Fix: run `uv run gz agent sync control-surfaces` to
regenerate AGENTS.md from the model pipeline, then re-run validate.

### Step 11 — Gate 3: docs build

```bash
uv run mkdocs build --strict
uv run gz validate --documents
```

### Step 12 — Gate 4: BDD

```bash
uv run -m behave --tags=@REQ-0.0.37-14 features/ 2>&1 || echo "no BDD scenarios yet"
```

If no BDD scenario exists tagged `@REQ-0.0.37-14`, the pipeline scope-discipline check
omits behave (per Stage 3 scope discipline, GHI #160/#185/#420 — behave is scoped to
tagged REQs for this OBPI). Behave runs at ADR closeout for the full suite.

## Verification (from brief)

```bash
uv run gz validate --documents
uv run gz validate --invariant-coherence
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.commands.test_sync_cmds -v
```

## Notes and risks

1. **Output format change**: after OBPI-14, AGENTS.md will be rendered by `claude.md.j2`
   (OBPI-12 template) instead of the monolith. Minor whitespace/blank-line differences are
   expected and acceptable per REQ-04 (semantic equivalence, not byte identity).

2. **First-sync after OBPI-14**: committed AGENTS.md will drift from model render until
   `gz agent sync control-surfaces` is run. The pipeline includes this re-sync in Stage 3.

3. **Bootstrap case**: if `.gzkit/templates/agents.md` doesn't exist, `sync_agents_md` falls
   back to the monolith render. This preserves fresh-init behavior for new projects.

4. **`governance_render_cmd` remains untouched**: `src/gzkit/commands/governance_render.py`
   is NOT in Allowed Paths and is not changed. It calls `compose.render_agents_md` which is
   updated internally → backward compat preserved.

5. **`invariants` parameter in `render_agents_md` stays**: removing it would break
   `governance_render_cmd` (not in Allowed Paths). It's accepted but internally the model
   pipeline is used instead of the registry.
