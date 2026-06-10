# Plan: OBPI-0.0.69-03-closeout-proof-derived-view

**OBPI:** OBPI-0.0.69-03-closeout-proof-derived-view
**Parent ADR:** ADR-0.0.69-channels-first-closeout-proof
**Lane:** Heavy
**Date:** 2026-06-10

## Context

Implements the derived `gz validate --closeout-proof` view that recomputes per-REQ
proof for in-closeout ADRs over the three REQ-kind channels on every `gz check` run.
Prereqs OBPI-01 (SUPPORT arm) and OBPI-02 (FENCE arm) are ATTESTED COMPLETED.

ADR-0.0.69 § Decision item (3) (quoted verbatim):
> Derived `gz validate --closeout-proof` view (OBPI-0.0.69-03, Heavy). A new
> `trust_audits/closeout_proof.py` view computes per-REQ proof for in-closeout ADRs over
> the three channels and JOINS the `gz check` default set (always dispatched, memoized
> per scope per run — ruling 6.1-A). The ceremony gate `_gate_proof_binding`
> (`closeout_ceremony.py:264-290`, wired at `_commit_advance:336`) is replaced by
> `_gate_closeout_proof` on the **same EXECUTE->ATTESTATION edge**, same fail-close shape;
> ADR-0.0.68's session-green gate is left untouched (honoring REQ-0.0.68-02-04's
> zero-rewiring fence). The fail-open seam at `trust_audits/cli.py:222-225` (bare
> `except` -> `return []` in `audit_skill_alignment`) is fixed to surface `ValidationError`,
> with a covering test. ADR-0.0.41 OBPI-02/03 verification text is repointed from the
> removed flag to `--closeout-proof` (else `--cli-alignment` exits 3), and the manpage is
> added. Output is a frozen `CloseoutProofReport` reusing the existing `ReqCoverageRecord`:
> per-REQ table + `--json`; exit 0 (all proven) / 3 (any unproven) / 2 (dispatch I/O
> error). The output MUST print the exact re-run command per failed SUPPORT REQ so a 2am
> on-call operator can reproduce the failing channel in one paste; full stderr inlining is
> explicitly out of scope (ruling 6.2-A). Before the ceremony-gate repoint lands, OBPI-03
> runs the new view READ-ONLY against all 19 `ln`-carrying briefs and surfaces/fixes any
> unprovable REQs (ruling 6.1-A pre-audit) so no real closeout goes red on first contact.

## Files

### Created
- `src/gzkit/governance/trust_audits/closeout_proof.py`

### Modified
- `src/gzkit/governance/trust_audits/__init__.py`
- `src/gzkit/governance/trust_audits/cli.py` (fix fail-open seam lines 222-225)
- `src/gzkit/quality.py` (add `run_closeout_proof_audit`)
- `src/gzkit/commands/quality.py` (add to `_build_check_steps()`)
- `src/gzkit/commands/validate_cmd.py` (add `--closeout-proof` scope dispatch)
- `src/gzkit/cli/parser_maintenance.py` (register `--closeout-proof` flag)
- `src/gzkit/commands/closeout_ceremony.py` (swap `_gate_proof_binding` → `_gate_closeout_proof`)
- `tests/` (new tests for all 7 REQs)
- `docs/user/manpages/validate.md` (document new scope)
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/obpis/OBPI-0.0.41-02-claim-release-safety-primitives.md`
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/obpis/OBPI-0.0.41-03-release-fail-closed-and-reaping.md`

## Steps

### Step 1: TDD RED — Write failing tests for all 7 REQs

Create `tests/governance/test_closeout_proof_view.py` with tests derived from the
brief's acceptance criteria (REQ-0.0.69-03-01 through -07). Tests must fail before
implementation. Tests check:
- REQ-01: exit 0 (all proven) / 3 (any unproven) / 2 (I/O error)
- REQ-02: per-failed-SUPPORT-REQ re-run command in output; no stderr inlining
- REQ-03: `--closeout-proof` is in `_build_check_steps()` return value
- REQ-04: `ValidationError` raised by `_known_cli_verb_paths()` is not swallowed
- REQ-07: REQ with no inline `[kind]` tag reports unproven (exit 3)

Separate regression test in `tests/governance/` for the fail-open seam (REQ-04).

### Step 2: CREATE `src/gzkit/governance/trust_audits/closeout_proof.py`

Implement:
- `CloseoutProofReport(BaseModel, frozen=True, extra="forbid")` — reuses
  `ReqCoverageRecord` from `gzkit.req_kind`; fields: `adr_id`, `entries`, `all_proven`,
  `unproven_count`, summary stats
- `validate_closeout_proof(project_root: Path) -> list[ValidationError]` — dispatches
  over in-closeout ADRs, recomputes per-REQ proof from the three channels, formats
  the re-run command per failed SUPPORT REQ, returns ValidationError list
- Exit contract: 0 (all proven), 3 (any unproven), 2 (dispatch I/O error)
- No disk write of `CloseoutProofReport` (Boundary Invariant 2)
- Uses `run_req_kind_discipline_audit` for dispatched-validator checking pattern

### Step 3: UPDATE `src/gzkit/governance/trust_audits/__init__.py`

Add `from gzkit.governance.trust_audits.closeout_proof import validate_closeout_proof`
alongside the existing `validate_closeout_proof_binding` re-export.

### Step 4: FIX `src/gzkit/governance/trust_audits/cli.py` fail-open seam

Replace the bare `except` at lines 222-225 with:
```python
except ValidationError:
    raise
except Exception:
    return []
```
So `ValidationError` propagates (REQ-04) while other I/O errors still degrade gracefully.

### Step 5: UPDATE `src/gzkit/quality.py`

Add `run_closeout_proof_audit` following the exact pattern of `run_session_green_gate_audit`:
```python
def run_closeout_proof_audit(project_root: Path) -> QualityResult:
    """Run the closeout-proof derived view (ADR-0.0.69 / OBPI-0.0.69-03)."""
    return run_command("uv run gz validate --closeout-proof", cwd=project_root)
```

### Step 6: UPDATE `src/gzkit/commands/quality.py`

Add `run_closeout_proof_audit` import and entry to `_build_check_steps()`:
```python
("Closeout proof", run_closeout_proof_audit),
```
Memoized per scope per run via the existing `gz check` memoization (ruling 6.1-A).

### Step 7: UPDATE `src/gzkit/commands/validate_cmd.py`

Follow the `check_session_green_gate` / `check_adr_status_fresh` precedent:
- Add `check_closeout_proof: bool = False` parameter to `validate_documents`
- Add `"closeout_proof": lambda: trust_audits.validate_closeout_proof(project_root)` to the dispatch map
- Wire through the pass-through plumbing (function signature + pass-through call chain)

### Step 8: UPDATE `src/gzkit/cli/parser_maintenance.py`

Register `--closeout-proof` flag following the `--session-green-gate` pattern:
```python
parser.add_argument(
    "--closeout-proof",
    dest="check_closeout_proof",
    action="store_true",
    default=False,
    help="Recompute per-REQ proof for in-closeout ADRs over three channels. "
         "Exit 0: all proven. Exit 3: any unproven. Exit 2: dispatch I/O error.",
)
```

### Step 9: SWAP gate in `src/gzkit/commands/closeout_ceremony.py`

Replace `_gate_proof_binding` with `_gate_closeout_proof` at line 336.
New `_gate_closeout_proof` function (lines 264-290 region):
```python
def _gate_closeout_proof(project_root: Path, state: CeremonyState) -> None:
    """Fail-close EXECUTE -> ATTESTATION via the derived closeout-proof view."""
    if state.current_step != CeremonyStep.EXECUTE:
        return
    from gzkit.governance.trust_audits.closeout_proof import validate_closeout_proof
    errors = validate_closeout_proof(project_root, adr_id=state.adr_id)
    if not errors:
        return
    from gzkit.core.exceptions import PolicyBreachError
    unbound = [e.message for e in errors[:5]]
    raise PolicyBreachError(
        "EXECUTE -> ATTESTATION transition blocked: closeout proof incomplete.\n"
        + "\n".join(f"  {m}" for m in unbound)
        + (f"\n  ... and {len(errors) - 5} more" if len(errors) > 5 else "")
    )
```
DO NOT touch `_gate_attestation_boundary`, `.pre-commit-config.yaml`, or ADR-0.0.68 surfaces.

### Step 10: TDD GREEN — Run tests

```bash
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_closeout_proof_view -v
uv run gz arb ruff
uv run gz arb typecheck
```
Fix failures (max 2 rounds). If still failing after 2 rounds, halt.

### Step 11: PRE-AUDIT — Run READ-ONLY against ln-carrying briefs

Before the ceremony-gate repoint lands, run:
```bash
uv run gz validate --closeout-proof --json
```
Review any unproven REQs. If ADR-0.0.41's REQs are untagged, add `[kind]` tags
to their Acceptance Criteria inline (OBPI brief, not ceremony). This is the
ruling 6.1-A pre-audit that prevents real closeouts from going red on first contact.

### Step 12: REPOINT ADR-0.0.41 OBPI-02/03 verification text

Replace `uv run gz validate --closeout-proof-binding` with `uv run gz validate --closeout-proof`
in the Verification sections of:
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/obpis/OBPI-0.0.41-02-claim-release-safety-primitives.md`
- `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/obpis/OBPI-0.0.41-03-release-fail-closed-and-reaping.md`

Run `uv run gz validate --cli-alignment` to confirm exit 0.

### Step 13: UPDATE `docs/user/manpages/validate.md`

Document the `--closeout-proof` scope: purpose, exit codes (0/3/2), re-run command
output example, and relationship to `gz check` default scope.

### Step 14: Final verification

```bash
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --cli-alignment
uv run gz validate --documents
uv run gz cli audit
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --closeout-proof
uv run gz validate --cli-alignment
uv run gz cli audit
```
