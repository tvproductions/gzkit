# Plan: OBPI-0.0.37-22 — Committed-Rendition Store + Deterministic Playback + Freshness Gate

## Context

ADR-0.0.37 § Decision Re-Alignment (2026-06-03) establishes a four-part CMS pipeline:
`corpus → compress → committed rendition → deterministic playback → rendered surface`.

OBPI-21 (complete) delivers the authoring-time composer. This OBPI delivers the
**rendition + playback** end: a durable committed-rendition store, deterministic
playback (no LLM), and a freshness gate that fails `gz check` when the corpus has
drifted from its committed rendition. It also re-points `--invariant-coherence` from
the registry-re-render byte-compare to the rendition-playback-vs-committed-surface diff.

OBPI-26 (complete) seeded the interim rendition at
`docs/design/adr/.../renditions/agentcontract-codex-root-interim.md` (codex consumer).

## Files changed

### CREATE (new modules)

**`src/gzkit/content/rendition_store.py`**
Mirror of `corpus_store.py` but for renditions:
```python
def rendition_path(root: Path, surface: str, consumer: str) -> Path:
    return root / ".gzkit" / "renditions" / surface / f"{consumer}.md"

def rendition_exists(root: Path, surface: str, consumer: str) -> bool: ...
def load_rendition(root: Path, surface: str, consumer: str) -> bytes:
    # fail-closed: raises FileNotFoundError when artifact is absent
def save_rendition(root: Path, surface: str, consumer: str, content: bytes) -> None:
    # creates dir, writes file
```

**`src/gzkit/governance/trust_audits/rendition_freshness.py`**
Corpus↔rendition drift gate (follows `reconcile.py` / `taxonomy.py` mtime pattern):
```python
def validate_rendition_freshness(root: Path) -> list[ValidationError]:
    # For each known (surface, consumer):
    #   corpus = corpus_path(root, surface)
    #   rendition = rendition_path(root, surface, consumer)
    #   if corpus.exists() and rendition.exists() and corpus.stat().st_mtime > rendition.stat().st_mtime:
    #       emit composition_drift_detected event (reuse existing factory)
    #       return [ValidationError(type="rendition_freshness", ...recovery hint...)]
    # Exit 0 when corpus absent, rendition absent, or timestamps agree
```
Reuses `emit_composition_drift_detected` from `gzkit.governance.events`.

**`tests/content/test_rendition_store.py`** — REQ-0.0.37-22-01 BEHAVIOR tests:
- `@covers("REQ-0.0.37-22-01")` on: store round-trip (bytes in == bytes out), determinism (same file = same bytes), fail-closed absent (FileNotFoundError when no artifact), `rendition_exists` True/False.

**`tests/governance/test_rendition_freshness.py`** — REQ-0.0.37-22-03 BEHAVIOR tests:
- `@covers("REQ-0.0.37-22-03")` on: drift detected (corpus newer → exit 3), no drift (rendition newer → exit 0), no corpus (exit 0), no rendition (exit 0).

**`features/rendition_playback.feature`** — Heavy-lane BDD (REQ-01 through REQ-04):
```gherkin
@REQ-0.0.37-22-01
Scenario: Rendition store loads byte-identically
@REQ-0.0.37-22-02
Scenario: sync_agents_md produces byte-identical output from same rendition
@REQ-0.0.37-22-03
Scenario: Freshness gate exits 3 on corpus drift
@REQ-0.0.37-22-04
Scenario: --invariant-coherence exits 3 on playback-vs-committed-surface diff
```

**`features/steps/rendition_playback_steps.py`** — step definitions for the above.

### EDIT (existing modules)

**`src/gzkit/governance/compose.py` — `render_agents_md`** (lines ~51-72)
Replace template pipeline with rendition playback. New body:
```python
def render_agents_md(invariants, template_root, project_root):
    from gzkit.content.rendition_store import load_rendition, rendition_exists
    if rendition_exists(project_root, "AGENTS.md", "claude"):
        return load_rendition(project_root, "AGENTS.md", "claude")
    return b""  # bootstrap-safe
```
`invariants` and `template_root` params kept for backward compat with existing callers
(`governance_render_cmd` still passes them); they are unused in playback mode.

**`src/gzkit/sync_surfaces.py` — `sync_agents_md`** (lines ~352-381)
Replace template-model pipeline with rendition playback:
```python
from gzkit.content.rendition_store import load_rendition, rendition_exists
if rendition_exists(project_root, "AGENTS.md", "claude"):
    content_bytes = load_rendition(project_root, "AGENTS.md", "claude")
else:
    content_bytes = render_template("agents", **context).encode("utf-8")  # bootstrap only
agents_path.write_bytes(content_bytes)
```
The `render_content_model(model, "claude", ...)` call is retired in favour of rendition
playback; monolith fallback is kept ONLY for fresh-init (no committed rendition yet).

**`src/gzkit/governance/trust_audits/invariant_coherence.py`**
Re-point from registry-re-render to rendition playback-vs-committed-surface diff:
```python
# old: rendered_bytes, count = _render_registry(root)
# new:
from gzkit.governance.compose import render_agents_md  # already imported
# render_agents_md now returns committed rendition bytes (playback)
rendered_bytes = render_agents_md({}, Path(), root)
# bootstrap skip: if render returns b"", no rendition yet — skip
```
The `_render_registry` helper and `load_invariants` import become unused → remove.
Event semantics unchanged: `composition_rendered` + `composition_drift_detected`.

**`tests/governance/test_invariant_coherence.py`**
Update fixtures to rendition-playback semantics:
- Seed `.gzkit/renditions/AGENTS.md/claude.md` in TempDir instead of seeding invariants registry.
- Coherence test: rendition bytes ≠ AGENTS.md bytes → exit 3; identical → exit 0.

**`tests/commands/test_sync_cmds.py`**
Update `sync_agents_md` tests:
- Seed `.gzkit/renditions/AGENTS.md/claude.md` in TempDir.
- Assert AGENTS.md bytes == rendition bytes (not template output).
- Test fallback path when no rendition: asserts AGENTS.md is written (monolith).

**`src/gzkit/governance/trust_audits/__init__.py`**
Add export:
```python
from gzkit.governance.trust_audits.rendition_freshness import validate_rendition_freshness
```

**`src/gzkit/cli/parser_maintenance.py`**
Add flag (after `--setpoint-coherence` block, ~line 676):
```python
p_validate.add_argument(
    "--rendition-freshness",
    dest="check_rendition_freshness",
    action="store_true",
    default=False,
    help="Fail-closed when corpus has drifted since the committed rendition (OBPI-0.0.37-22).",
)
```

**`src/gzkit/commands/validate_cmd.py`**
Add `check_rendition_freshness: bool = False` param + runner:
```python
def _rendition_freshness_runner(project_root: Path) -> list[ValidationError]:
    from gzkit.governance import trust_audits
    return trust_audits.validate_rendition_freshness(project_root)
```
Wire into dispatch table (follow `_invariant_coherence_runner` pattern):
```python
"rendition_freshness": lambda: _rendition_freshness_runner(project_root),
```
Add to `default_scopes` (same tier as `setpoint_coherence`).
Pass through in the validate call chain (the three locations where `check_setpoint_coherence` appears).

**`src/gzkit/commands/quality.py` — `_build_check_steps`**
Add `("Rendition freshness", run_rendition_freshness_audit)` to the steps list.
Add to `src/gzkit/quality.py` (follows pattern of `run_adr_status_fresh_audit`, line ~574):
```python
def run_rendition_freshness_audit(project_root: Path) -> QualityResult:
    """Fails closed (exit 3) when corpus drifted since committed rendition. Recovery: gz content compose."""
    return run_command("uv run gz validate --rendition-freshness", cwd=project_root)
```

**`data/behave_coverage_waivers.json`**
Add SUPPORT REQ waivers for REQ-0.0.37-22-05 and REQ-0.0.37-22-06
(no Gherkin-observable BDD scenario for these; proven by ledger event + `gz validate --documents`).

**`docs/user/manpages/validate.md`**
Add `--rendition-freshness` scope entry (exit codes, recovery hint: `gz content compose <surface>`).
Update `--invariant-coherence` description to reflect playback-vs-committed-surface semantics
(was: "re-renders registry"; now: "diffs committed rendition playback against committed surface").

**`docs/user/runbook.md`**
Add operator runbook entry for recompose-on-drift flow:
```
If `gz check` or `gz validate --rendition-freshness` exits 3:
  uv run gz content compose <surface>   # recompose + attest
  # Then re-run gz check to confirm drift cleared
```

### Net-new files committed to `.gzkit/renditions/`

As part of the implementation, seed the initial committed rendition artifacts:
- `.gzkit/renditions/AGENTS.md/claude.md` — seeded from current committed AGENTS.md content
- `.gzkit/renditions/AGENTS.md/codex.md` — seeded from OBPI-26 interim at
  `docs/design/adr/.../renditions/agentcontract-codex-root-interim.md`

These are the Layer-1 committed rendition artifacts the store contract lives on.

## Implementation Order (TDD — Red→Green)

1. **Task 1 (REQ-01):** Create `rendition_store.py` + `test_rendition_store.py`.
   Write tests RED → implement store → GREEN.

2. **Task 2 (REQ-02):** Edit `compose.py::render_agents_md` + `sync_surfaces.py::sync_agents_md`.
   Write/update `test_sync_cmds.py` RED → implement playback → GREEN.
   Seed `.gzkit/renditions/AGENTS.md/claude.md` from current AGENTS.md.

3. **Task 3 (REQ-03):** Create `rendition_freshness.py` + `test_rendition_freshness.py`.
   Write tests RED → implement drift gate → GREEN.

4. **Task 4 (REQ-04):** Edit `invariant_coherence.py`.
   Update `test_invariant_coherence.py` RED → repoint → GREEN.
   Remove now-unused `_render_registry` / `load_invariants` from coherence module.

5. **Task 5 (REQ-05, SUPPORT):** Wire CLI (parser_maintenance.py, validate_cmd.py, quality.py,
   trust_audits/__init__.py). Wire events (compose_drift_detected reuse confirmed — no new
   ledger event type needed). Add to `gz check` via quality module.
   Waive REQ-05 in behave_coverage_waivers.json.

6. **Task 6 (REQ-06, SUPPORT):** Docs (validate.md, runbook.md).
   Waive REQ-06 in behave_coverage_waivers.json.

7. **Task 7 (Heavy BDD):** Create `features/rendition_playback.feature` + step definitions
   for REQ-01 through REQ-04.

## No new events or ledger schema changes needed

`composition_drift_detected` (existing in `events.py` + `ledger.json`) fits the rendition
freshness drift shape: `target` + `diff_first_50_lines`. The rendition freshness gate reuses
`emit_composition_drift_detected` from `gzkit.governance.events`. No new event type, no
`events.py` or `ledger.json` schema change required.

## Open Implementation Decision (operator confirmation at Gate 5)

Brief's two open choices, both recommended options adopted here:
- **(A) Store location:** `.gzkit/renditions/<surface>/<consumer>.md` ✓
- **(B) Freshness scope:** dedicated `--rendition-freshness` scope, not folded into `--invariant-coherence` ✓

## Verification

```bash
uv run -m unittest tests.content.test_rendition_store -v
uv run -m unittest tests.governance.test_rendition_freshness -v
uv run -m unittest tests.governance.test_invariant_coherence -v
uv run -m unittest tests.commands.test_sync_cmds -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --rendition-freshness
uv run gz validate --invariant-coherence
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run gz covers OBPI-0.0.37-22-committed-rendition-store-deterministic-playback --json
uv run -m behave --tags=@REQ-0.0.37-22-01,@REQ-0.0.37-22-02,@REQ-0.0.37-22-03,@REQ-0.0.37-22-04 features/
uv run mkdocs build --strict
uv run gz check
```
