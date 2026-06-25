# OBPI-0.0.74-04-mx-enter: Mx Enter

**OBPI slug:** `OBPI-0.0.74-04-mx-enter`
**Parent ADR:** `ADR-0.0.74-mx-mode-maintenance-hangar`
**Brief:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-04-mx-enter.md`
**Lane:** Heavy

## Context

ADR-0.0.74 Decision item #4 (verbatim): "gz mx enter. The operator opens the door
(reason + attestor); the tool sets the marker, writes mx_session_opened, and captures the
inspection scope. The agent never opens the hangar on its own."

Prerequisites landed:
- OBPI-01 (Completed): `src/gzkit/mx/marker.py` — `Marker`, `is_active()`, `read()`, `write()`,
  `marker_path()`, ledger-binding `is_valid()`. Marker schema already has `session_id`, `opened_at`,
  `reason`, `attestor`, `inspection_scope` fields.
- OBPI-02 (Completed): `src/gzkit/mx/checkpoint.py` — `resolve()`, `is_advisory()`, `GATE5_INVARIANTS`.

Lock infrastructure: `gzkit.lock_manager` provides `resolve_session_id()`, `resolve_agent()`,
`write_lock()`, `read_lock()`, `LockData` — the existing token rail to serialize concurrent MX entry.

Ledger infrastructure: `gzkit.ledger.Ledger.append()` and `gzkit.ledger_events` builders. The
`mx_session_opened` event type is referenced in `marker.py` as `_OPENED_EVENT = "mx_session_opened"`;
no builder exists yet in `ledger_events.py` (not in allowed paths), so a module-local builder
function will be added in `mx_cmd.py`.

## Files

### Created
- `src/gzkit/commands/mx_cmd.py` — gz mx command group + enter handler
- `docs/user/manpages/mx.md` — manpage for the mx verb group
- `tests/commands/test_mx_enter.py` — unit tests for all 5 REQs

### Modified
- `src/gzkit/cli/parser_governance.py` — register `gz mx` + `gz mx enter` verb

## Destination-in-mind (Step 6a disclosure)

Before exploration I had concluded: create `mx_cmd.py` with `mx_enter_cmd()`, add
`mx_session_opened_event` builder locally (ledger_events.py is outside allowed paths), register in
parser_governance, create manpage. That destination was correct.

## Rejected alternatives

- Add `mx_session_opened_event` to `ledger_events.py`: consistent with codebase pattern but requires
  a brief amendment (file not in allowed paths). Local builder in `mx_cmd.py` avoids amendment
  and keeps the surface change within allowed paths.
- Use a hand-rolled lock file for concurrency: rejected per REQ-04-04 (must use lock_manager).
- Defer inspection scope to a second flag (`--scope`) vs. accepting varargs: chose optional `--scope`
  flag (0 or more values) so the demo works without scope and real sessions can name ADRs under repair.

## Steps

### Step 1: RED — Write failing tests (`tests/commands/test_mx_enter.py`)

Author the test file FIRST. Tests derive from brief REQs, not from implementation.

Four test classes:

**TestMxEnterSetsMarkerAndEvent** (REQ-0.0.74-04-01):
- `test_enter_sets_marker`: mx_enter_cmd writes marker; `marker.is_active(root)` is True after
- `test_enter_writes_mx_session_opened_event`: ledger contains one `mx_session_opened` event after enter
- `test_enter_captures_inspection_scope`: marker's `inspection_scope` matches the arg passed
- `test_enter_outside_hangar`: enter on a root with no pre-existing marker succeeds

**TestMxEnterRequiresAttestor** (REQ-0.0.74-04-02):
- `test_enter_without_attestor_exits_1`: calling with `attestor=""` raises SystemExit(1)
- `test_no_marker_written_without_attestor`: no marker file after enter refuses

**TestMxEnterFailsClosedOnEmpty** (REQ-0.0.74-04-03):
- `test_empty_reason_exits_1`: empty reason → SystemExit(1), no marker, no event
- `test_empty_attestor_exits_1`: empty attestor → SystemExit(1), no marker, no event
- `test_whitespace_only_reason_exits_1`: whitespace-only reason → SystemExit(1)

**TestMxEnterUsesLockManagerRail** (REQ-0.0.74-04-04):
- `test_enter_acquires_lock_via_lock_manager`: `lock_manager.write_lock` is called during enter
  (mock or inspect lock file at `.gzkit/locks/mx-session.json`)
- `test_second_enter_while_active_is_rejected`: if marker is already active, enter exits 1

All tests use `TemporaryDirectory()` and `_mk_root()` helper; tests decorated with `@covers()`.

### Step 2: GREEN — Implement `mx_cmd.py` (`src/gzkit/commands/mx_cmd.py`)

```
# Module structure:
# 1. _MX_LOCK_KEY = "mx-session"  — lock identity on the token rail
# 2. _mx_session_opened_event(session_id, reason, attestor, inspection_scope) -> LedgerEvent
#    — local builder (ledger_events.py is outside allowed paths)
# 3. mx_enter_cmd(reason, attestor, inspection_scope, project_root=None) -> None:
#    a. Validate non-empty reason and attestor → sys.exit(1) if either empty/whitespace
#    b. Get project_root via get_project_root() if not supplied; ensure_initialized()
#    c. Check marker not already active: marker.is_active(project_root) → sys.exit(1) if True
#    d. session_id = lock_manager.resolve_session_id()
#    e. Acquire lock: write_lock(project_root, LockData(obpi_id=_MX_LOCK_KEY, ...))
#       — serializes concurrent MX entry on the existing rail
#    f. m = Marker(session_id=session_id, opened_at=<ISO UTC>, reason=reason,
#                  attestor=attestor, inspection_scope=list(inspection_scope))
#    g. marker.write(m, project_root)
#    h. ledger = Ledger(project_root / config.paths.ledger)
#       ledger.append(_mx_session_opened_event(session_id, reason, attestor, inspection_scope))
#    i. console.print("MX session opened ...")
```

Run `uv run ruff check . --fix && uv run ruff format .` after implementation.
Run `uv run -m unittest tests/commands/test_mx_enter.py -v` to confirm GREEN.

### Step 3: Register parser (`src/gzkit/cli/parser_governance.py`)

After the existing `plan` block (or any other block — alphabetically `mx` fits after the existing
command groups), add:

```python
# gz mx  ---------------------------------------------------------------
p_mx = commands.add_parser("mx", help="Maintenance Hangar: MX mode operations")
mx_commands = p_mx.add_subparsers(dest="mx_command")

p_mx_enter = mx_commands.add_parser("enter", help="Open the MX hangar (operator only)")
p_mx_enter.add_argument("--reason", required=True, help="Reason for entering MX mode")
p_mx_enter.add_argument("--attestor", required=True, help="Operator identity (never an agent)")
p_mx_enter.add_argument(
    "--scope",
    dest="inspection_scope",
    nargs="*",
    default=[],
    metavar="ADR_OR_OBPI",
    help="ADRs/OBPIs under inspection (optional; 0 or more)",
)
p_mx_enter.set_defaults(
    func=lambda a: _lazy("mx_cmd")(
        reason=a.reason, attestor=a.attestor, inspection_scope=a.inspection_scope
    )
)
```

Where `_lazy("mx_cmd")` calls the `mx_enter_cmd` function (consistent with the `_lazy` dispatch
pattern used throughout `parser_governance.py`).

Run `uv run gz mx enter --help` to confirm registration.

### Step 4: Create manpage (`docs/user/manpages/mx.md`)

Create the manpage following the existing manpage format in `docs/user/manpages/`. Include:
- Synopsis: `gz mx <subcommand>`
- Subcommands: `enter` (with all flags described)
- Description of the MX mode concept
- Examples matching the Demo in the brief
- Exit codes
- See also: linked to other mx subcommands (enter/exit when landed)

Also update `docs/user/manpages/index.md` to include the `mx` entry.

### Step 5: Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz cli audit
uv run gz validate --documents
uv run mkdocs build --strict
test -f src/gzkit/commands/mx_cmd.py
test -f docs/user/manpages/mx.md
test -f tests/commands/test_mx_enter.py
uv run gz covers OBPI-0.0.74-04 --json
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
uv run gz mx enter --reason "re-true ledger-proof locks under ADR-0.0.74" --attestor g0
```

## Notes

- `ledger_events.py` is outside allowed paths. The `mx_session_opened_event` builder is a
  module-local function in `mx_cmd.py` (prefix `_`). This is a deliberate allowed-path constraint.
- `inspection_scope` defaults to `[]` when `--scope` is not supplied (matches the Marker schema
  default_factory=list).
- The lock key `"mx-session"` is a singleton string on the lock_manager rail; `_adr_id_from_obpi`
  will return None for it (graceful no-op in list_locks grouping).
- Marker `opened_at` is an ISO-8601 UTC timestamp generated at enter time
  (`datetime.now(timezone.utc).isoformat()`).
