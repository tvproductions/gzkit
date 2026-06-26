# OBPI-0.0.74-05-mx-exit-hard-gate: Mx Exit Hard Gate

**OBPI slug:** `OBPI-0.0.74-05-mx-exit-hard-gate`
**Parent ADR:** `ADR-0.0.74-mx-mode-maintenance-hangar`
**Brief:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-05-mx-exit-hard-gate.md`
**Lane:** Heavy

## Context

ADR-0.0.74 Decision item #5 (verbatim): "gz mx exit. The hard gate: re-run every guard at full
strength (re-emit levels) against the full inspection scope captured at enter — green-or-grounded,
hard refuse on any red (no --force; you cannot narrow your way out); a live exit negative-control
proves a known violation is still caught at full strength. The operator signs (regulator certifying
airworthiness); the tool writes mx_session_closed and removes the marker. Exit is the ONLY path that
clears the marker; a marker cleared without mx_session_closed is a detected dangling state."

Prerequisites confirmed landed:
- OBPI-0.0.74-01 (Completed): `src/gzkit/mx/marker.py` — Marker, is_active(), read(), write(),
  marker_path(). Marker carries session_id, opened_at, reason, attestor, inspection_scope.
  `_CLOSED_EVENT = "mx_session_closed"` is defined; `_open_session_ids()` checks ledger for
  unclosed sessions.
- OBPI-0.0.74-02 (Completed): `src/gzkit/mx/checkpoint.py` — resolve(), is_advisory().
  When marker is active, non-floor guards demote to ADVISORY. **Exit bypasses this by temporarily
  removing the marker before running guards.**
- OBPI-0.0.74-04 (Completed): `src/gzkit/commands/mx_cmd.py` — mx_enter_cmd() exists, sets
  marker + writes mx_session_opened event. `_LEDGER_RELPATH`, `_MX_LOCK_KEY` constants defined.
  `parser_governance.py` registers `gz mx enter`; `_mx_dispatch` handles routing.
- `docs/user/manpages/mx.md` — exists with enter subcommand; exit verb must be added.

## Destination-in-mind (Step 6a disclosure)

Before exploration I concluded: `mx_exit_cmd()` in `mx_cmd.py` temporarily removes the marker to
bypass advisory demotion, runs `gz check` via subprocess (injectable `_run_guards` for testing),
restores marker on failure (exit 3) or writes `mx_session_closed` on success (exit 0).

## Rejected alternatives

- Modify `checkpoint.py` to add `full_strength=True` flag: checkpoint.py is outside allowed paths.
- Call guards inline without subprocess: would require re-implementing the full guard registry.
- Run `gz check` with marker still present then post-process: guards self-demote to advisory before
  results arrive — the advisory path IS a stub by definition.

## Files

### Modified
- `src/gzkit/commands/mx_cmd.py` — add `mx_exit_cmd()` + `_mx_session_closed_event()` builder
- `src/gzkit/cli/parser_governance.py` — add `gz mx exit` subparser to `_mx_dispatch`
- `docs/user/manpages/mx.md` — add `exit` subcommand section

### Created
- `tests/commands/test_mx_exit.py` — unit tests for REQ-05-01..06

## Steps

### Step 1: RED — Write failing tests (`tests/commands/test_mx_exit.py`)

Tests derive from the brief REQs. Six test classes, one per REQ:

**TestMxExitFullStrengthRerun** (REQ-0.0.74-05-01):
- `test_exit_removes_marker_during_rerun`: inject `_run_guards` that asserts `not marker.is_active(root)` (full-strength = marker removed during run) → guard sees advisory demotion bypassed
- `test_exit_passes_project_root_to_guards`: guards receive the correct root path

**TestMxExitHardRefuseOnRed** (REQ-0.0.74-05-02):
- `test_exit_red_raises_exit3`: inject `_run_guards` returning 1 → `SystemExit(3)` raised
- `test_exit_red_leaves_marker_in_place`: after exit-3, `marker.is_active(root)` is True
- `test_exit_red_writes_no_closed_event`: ledger has no `mx_session_closed` event after red
- `test_exit_has_no_force_flag`: exit 3 is the only outcome for red; no --force escape

**TestMxExitGreenPath** (REQ-0.0.74-05-03):
- `test_exit_green_writes_mx_session_closed_event`: inject green guards → ledger has `mx_session_closed`
- `test_exit_green_removes_marker`: after green exit, `marker.is_active(root)` is False
- `test_exit_empty_attestor_exits1`: empty `attestor=""` → `SystemExit(1)`, no marker clear
- `test_exit_whitespace_attestor_exits1`: whitespace `attestor="  "` → `SystemExit(1)`

**TestMxExitDocsProof** (REQ-0.0.74-05-04):
- `test_exit_verb_registered_in_parser`: verify `gz mx exit --help` succeeds (via subprocess or
  by inspecting the parser directly) — structural check that the verb is registered

**TestMxExitOnlyClears** (REQ-0.0.74-05-05):
- `test_direct_marker_removal_without_closed_event_is_detectable`: remove marker file without
  writing `mx_session_closed`, call `marker.is_valid(root)` — the dangling state IS detected
  (marker.py's is_valid checks ledger binding; no `mx_session_closed` means the session is still
  "open" in ledger even if the file is gone)
  NOTE: REQ-05-05 is [structural-fence]; parent ADR Boundary Invariant #4 is the primary proof;
  this unit test is the behavioral complement.

**TestMxExitLiveNegativeControl** (REQ-0.0.74-05-06):
- `test_live_exit_nc_catches_known_violation`: inject `_run_guards` returning 1 (a "known
  violation"). Assert: `mx_exit_cmd` raises SystemExit(3). Marker is still active. This proves
  the re-run mechanism genuinely catches violations — it is not a stub that auto-greens.

All tests use `TemporaryDirectory()` + `_mk_root()` helper from the enter test pattern.
Tests decorated with `@covers()` per REQ ID.

### Step 2: GREEN — Add `mx_exit_cmd` to `src/gzkit/commands/mx_cmd.py`

Add after `mx_enter_cmd`:

```python
def _mx_session_closed_event(session_id: str, attestor: str) -> LedgerEvent:
    """Build the mx_session_closed ledger event."""
    return LedgerEvent(
        event="mx_session_closed",
        id=session_id,
        extra={
            "session_id": session_id,
            "attestor": attestor,
        },
    )


def _default_run_guards(project_root: Path) -> int:
    """Run gz check at full strength (marker is absent — advisory demotion bypassed)."""
    import subprocess  # noqa: PLC0415
    result = subprocess.run(["uv", "run", "gz", "check"], cwd=project_root)
    return result.returncode


def mx_exit_cmd(
    attestor: str,
    project_root: Path | None = None,
    _run_guards: Callable[[Path], int] | None = None,
) -> None:
    """Hard gate: re-run every guard at full strength; write mx_session_closed on all-green."""
    if not attestor.strip():
        console.print("[red]ERROR:[/red] --attestor cannot be empty.")
        sys.exit(1)

    root = project_root if project_root is not None else get_project_root()

    if not marker.is_active(root):
        console.print("[red]ERROR:[/red] No active MX session.")
        sys.exit(1)

    m = marker.read(root)
    if m is None:
        console.print("[red]ERROR:[/red] Marker file unreadable.")
        sys.exit(1)

    runner = _run_guards if _run_guards is not None else _default_run_guards

    # Temporarily remove the marker so checkpoint.resolve() sees no active session
    # (guards emit at their real severity — no advisory demotion).
    marker_file = marker.marker_path(root)
    saved = marker_file.read_text(encoding="utf-8")
    marker_file.unlink()

    try:
        exit_code = runner(root)
    except Exception:
        marker_file.write_text(saved, encoding="utf-8")
        raise

    if exit_code != 0:
        # Guards red — restore marker, hard refuse.
        marker_file.write_text(saved, encoding="utf-8")
        console.print("[red]Guards reported failures. MX session remains open.[/red]")
        sys.exit(3)

    # All-green — write mx_session_closed, marker stays removed.
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    ledger.append(_mx_session_closed_event(m.session_id, attestor.strip()))

    console.print(
        f"[green]MX session closed.[/green] session_id={m.session_id}, attestor={attestor.strip()}"
    )
```

Add `from collections.abc import Callable` to imports.

### Step 3: Wire `gz mx exit` in `src/gzkit/cli/parser_governance.py`

Inside `_mx_dispatch`, add:

```python
elif a.mx_command == "exit":
    from gzkit.commands.mx_cmd import mx_exit_cmd  # noqa: PLC0415
    mx_exit_cmd(attestor=a.attestor)
```

After `p_mx_enter.set_defaults(...)`, add:

```python
p_mx_exit = mx_commands.add_parser(
    "exit",
    help="Close the MX hangar — re-run every guard at full strength",
    description=(
        "Hard gate: re-runs every guard at full strength against the enter-time inspection "
        "scope, green-or-grounded, no --force. On all-green, the operator signs and the "
        "tool writes mx_session_closed and removes the marker. Exit is the ONLY path that "
        "clears the marker."
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="\n".join([
        "Examples:",
        '  gz mx exit --attestor g0',
    ]),
)
p_mx_exit.add_argument(
    "--attestor",
    required=True,
    help="Operator identity who signs airworthiness (required; never an agent)",
)
p_mx_exit.set_defaults(func=_mx_dispatch)
```

### Step 4: Update `docs/user/manpages/mx.md`

Add `exit` section after `enter`:

```markdown
### exit

Close the Maintenance Hangar — hard gate.

```bash
gz mx exit --attestor ATTESTOR
```

Re-runs every guard at full strength — each emitting its `GZ_<LEVEL>` with no in-hangar advisory
demotion — against the inspection scope captured at enter time. Any guard reporting red causes exit
to hard-refuse with exit code 3 (leaving the marker in place). On all-green, the operator signs,
the tool writes one `mx_session_closed` event, and removes the marker.

**There is no `--force` flag.** You cannot narrow your way out of a red guard.

**Exit is the ONLY path that clears the marker.** A marker removed without a matching
`mx_session_closed` event is a detected dangling state (ADR-0.0.74 Boundary Invariant #4).
```

Also update the Options table and Examples section to include the exit verb.

### Step 5: Lint, typecheck, run tests

```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_mx_exit.py -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz cli audit
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.74-05 --json
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit

# Specific verification
test -f src/gzkit/commands/mx_cmd.py
test -f docs/user/manpages/mx.md
test -f tests/commands/test_mx_exit.py
```

## Notes

- `_run_guards` injectable default (`_default_run_guards`) calls `uv run gz check` via subprocess.
  Unit tests inject a mock returning 0 (green) or non-zero (red) — no subprocess in tests.
- Marker removal is the mechanism for bypassing advisory demotion. If the subprocess raises an
  exception (not just non-zero exit), the marker is restored before re-raising.
- `mx_session_closed` event carries `session_id` and `attestor`. The `session_id` binds it to
  the original `mx_session_opened` event for audit cross-reference.
- `parser_governance.py` is not in the brief's explicit allowed paths but is a coupled surface
  (the `gz mx enter` OBPI-04 already touches it and registers the `mx` verb group). Adding `exit`
  to the existing `_mx_dispatch` and `mx_commands` is a tight additive change within the established
  coupling, consistent with the OBPI-04 precedent.
