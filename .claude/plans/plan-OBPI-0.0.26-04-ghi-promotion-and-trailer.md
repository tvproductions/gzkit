# Plan: OBPI-0.0.26-04 — Cluster → GHI proposals + provenance trailer

**OBPI:** `OBPI-0.0.26-04-ghi-promotion-and-trailer`
**Parent ADR:** `ADR-0.0.26-evaluation-feedback-loop-doctrine`
**Lane:** Heavy
**Date:** 2026-05-03

---

## Context

OBPI-03 has landed the `eval-feedback-cluster` chore:
- Python module: `src/gzkit/chores/eval_feedback_cluster_lib.py`
- Model: `ProposalRecord` (frozen Pydantic, fields: `cluster_key`, `recurrence_count`,
  `source_artifact_ids`, `source_artifact_paths`, `summary`, `proposed_rule_target`,
  `content_hash`)
- Proposal records written to `.gzkit/chores/eval-feedback-cluster/proofs/proposal-<ts>.json`
- Chore data: `src/gzkit/chores/eval-feedback-cluster/` (DENIED — do not touch)

Commit-trailer validator: `src/gzkit/commands/validate_cmd.py:_validate_commit_trailers`
Trailer parsers: `src/gzkit/tasks.py` — `parse_task_trailers`, `parse_ceremony_trailers`

**Path drift note:** Brief lists `src/gzkit/governance/trust_audits.py` — the actual commit-trailer
validator lives in `src/gzkit/commands/validate_cmd.py`. Brief lists `.claude/rules/tests.md` —
the canonical edit surface is `.gzkit/rules/tests.md` (sync mirrors to `.claude/`).

---

## Files (Allowed Paths)

| File | Change |
|------|--------|
| `src/gzkit/chores/eval_feedback_cluster_lib.py` | Add `filed`, `ghi_url`, `advisory` optional fields to `ProposalRecord` |
| `src/gzkit/commands/chores.py` | Add `propose-ghi` subcommand + parser registration |
| `src/gzkit/commands/validate_cmd.py` | Add `parse_eval_feedback_source_trailers`; extend `_validate_commit_trailers` to recognize the new key and enforce the rule-edit constraint |
| `AGENTS.md` | § Behavior Rules — Always: add trailer convention item |
| `.gzkit/rules/tests.md` | § Governance-intent trailers: expand trailer table with `Eval-feedback-source:` |
| `docs/governance/arb-middleware.md` | Cross-reference the eval feedback loop |
| `tests/commands/test_chores_propose_ghi.py` | NEW — propose-ghi tests |
| `tests/governance/test_eval_feedback_trailer.py` | NEW — trailer validator tests |
| `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/obpis/OBPI-0.0.26-04-ghi-promotion-and-trailer.md` | Update checklist at completion |

---

## Implementation Steps

### Step 1: Extend `ProposalRecord` model
**File:** `src/gzkit/chores/eval_feedback_cluster_lib.py`

Add optional fields to `ProposalRecord` (keep `frozen=True`; fields have defaults so existing
JSON files parse without error):
```python
filed: bool = Field(default=False, description="Whether a GHI has been filed")
ghi_url: str | None = Field(default=None, description="GitHub issue URL if filed")
advisory: bool = Field(default=False, description="Marked advisory-only in headless run")
```

### Step 2: Add `parse_eval_feedback_source_trailers` to `src/gzkit/tasks.py`
New function parallel to `parse_ceremony_trailers`:
```python
_EVAL_FEEDBACK_SOURCE_TRAILER_RE = re.compile(r"^Eval-feedback-source:\s*(?P<value>\S+)\s*$")

def parse_eval_feedback_source_trailers(commit_message: str) -> list[str]:
    """Extract Eval-feedback-source: values from a commit's trailer block."""
```

### Step 3: Add `propose-ghi` subcommand to `src/gzkit/commands/chores.py`
New function `chores_propose_ghi(slug: str) -> None`:
1. Resolve slug → proofs dir: `.gzkit/chores/{slug}/proofs/`
2. Glob `proposal-*.json`, parse each as `ProposalRecord`
3. Filter: skip `filed=True` proposals
4. For each unfiled proposal:
   - TTY check: `sys.stdin.isatty() and sys.stdout.isatty()`
   - **TTY mode:** Display cluster_key, recurrence_count, summary, proposed_rule_target
     Prompt "File GHI? [PROPOSE/skip]". On `PROPOSE`:
     ```
     gh issue create
       --title "eval-feedback: {summary} (recurrence ≥ {recurrence_count})"
       --body "<body with cluster_key, recurrence_count, source_artifact_ids, summary, proposed_rule_target>"
       --label enhancement
       --label eval-feedback
     ```
     Capture GHI URL from stdout. Update JSON file: new `ProposalRecord(**record.model_dump() | {"filed": True, "ghi_url": url})`.
   - **Headless mode:** Print advisory output. Update JSON: `{"advisory": True}`.

Parser registration: add `propose-ghi` subcommand under `gz chores`.

### Step 4: Extend `_validate_commit_trailers` in `src/gzkit/commands/validate_cmd.py`
Add two behaviors:
1. **Recognize key:** `Eval-feedback-source:` is a valid governance-intent trailer (no error if present alongside Task:/Ceremony:)
2. **New rule — rule-edit + eval-feedback close:** If HEAD commit:
   - touches `.gzkit/rules/` or `AGENTS.md`, AND
   - closes/fixes a GHI number (pattern `(?:closes|fixes)\s+#(\d+)` in message), AND
   - that GHI has label `eval-feedback` (checked via `gh issue view {n} --json labels`)
   → require at least one `Eval-feedback-source:` trailer

Import and use `parse_eval_feedback_source_trailers` from `gzkit.tasks`.

### Step 5: Update docs
- `AGENTS.md` § Behavior Rules — Always: add bullet for the `Eval-feedback-source:` trailer
  convention (after existing trailer items, before or near the rule-authoring guidance)
- `.gzkit/rules/tests.md` § Governance-intent trailers: expand table with
  `Eval-feedback-source: <event-id-or-artifact-path>` row
- `docs/governance/arb-middleware.md`: add cross-reference paragraph mentioning eval
  feedback loop doctrine (ADR-0.0.26) and the `Eval-feedback-source:` trailer
- Run `uv run gz agent sync control-surfaces` to propagate `.gzkit/rules/tests.md` changes
  to `.claude/rules/tests.md`

---

## TDD Discipline

Tests are written BEFORE implementation (Red → Green → Refactor).

### `tests/commands/test_chores_propose_ghi.py`

```python
@covers("REQ-0.0.26-04-01")
def test_tty_confirm_files_ghi(self): ...

@covers("REQ-0.0.26-04-02")
def test_headless_advisory_only(self): ...

@covers("REQ-0.0.26-04-03")
def test_refile_idempotent(self): ...

@covers("REQ-0.0.26-04-01")
def test_ghi_title_pattern(self): ...  # "eval-feedback: <summary> (recurrence ≥ N)"

@covers("REQ-0.0.26-04-02")
def test_ghi_body_shape(self): ...  # body includes all required fields
```

All tests mock `subprocess.run` at the `gh` boundary — never hit real GitHub API (REQ-09).

### `tests/governance/test_eval_feedback_trailer.py`

```python
@covers("REQ-0.0.26-04-05")
def test_recognizes_eval_feedback_source_trailer(self): ...

@covers("REQ-0.0.26-04-04")
def test_fails_rule_edit_closing_eval_feedback_ghi_without_trailer(self): ...

@covers("REQ-0.0.26-04-05")
def test_passes_rule_edit_closing_eval_feedback_ghi_with_trailer(self): ...
```

---

## Verification Commands (from brief)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_eval_feedback_trailer.py tests/commands/test_chores_propose_ghi.py -v
uv run gz validate --commit-trailers
```

---

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

**Destination already formed:** Extend `ProposalRecord` with `filed`/`ghi_url`/`advisory` fields,
add `propose-ghi` subcommand in `chores.py`, extend `_validate_commit_trailers` in `validate_cmd.py`.

**Rejected alternatives considered:**
1. Store filing state in sidecar files (e.g., `.filed` next to the proposal JSON) — rejected
   because REQ-04 explicitly says "the proposal record is marked `filed`," implying in-place
   annotation. Sidecar files would split state across two artifacts.
2. Require `Eval-feedback-source:` on ALL rule-edit commits (not just eval-feedback closes) —
   rejected as overbroad; would add noise and require every rule edit to trace back to an
   evaluation event.
3. Add `Eval-feedback-source:` parsing to `tasks.py` as a standalone function vs. inlining in
   `validate_cmd.py` — chose `tasks.py` because it mirrors the `parse_task_trailers` /
   `parse_ceremony_trailers` pattern; `validate_cmd.py` imports from there already.

---

## Notes

- `eval_feedback_cluster_lib.py` module is NOT in the denied paths; the denied path is the
  chore data directory `src/gzkit/chores/eval-feedback-cluster/` (with dashes). Safe to extend.
- `ProposalRecord` uses `frozen=True`; updates use `model.model_dump() | {new_fields}` pattern.
- The `propose-ghi` verb triggers Heavy-lane: add to `docs/user/manpages/gz-chores.md` if
  the manpage covers individual subcommands (check during implementation).
- `cli audit` must pass after adding the new verb — update manpage coverage if needed.
