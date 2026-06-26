# Plan: OBPI-0.0.74-06-mx-log-auto-assembled

**OBPI:** OBPI-0.0.74-06-mx-log-auto-assembled
**ADR:** ADR-0.0.74-mx-mode-maintenance-hangar
**Decision item #6 (verbatim):** "The auto-assembled MX log. Built at exit from the ledger events + commits between enter and exit — complete by construction, cannot be narrated or forgotten — naming every fix and the ADRs/OBPIs/REQs it touched. The operator reviews it before signing."
**Lane:** Heavy

## Destination-in-mind

Approach formed from reading the brief + existing mx code: add typed event classes to `events.py`
for `mx_session_opened`/`mx_session_closed`, create `src/gzkit/mx/log.py` with the window
assembler (reads ledger events + git commits), and wire the render call into `mx_exit_cmd` before
writing the `mx_session_closed` event.

## Rejected Alternatives

- Inline the log assembly into `mx_exit_cmd` directly → rejected: a separate `log.py` module is
  explicitly named in the allowed paths and keeps the assembler independently testable
- Injectable callback pattern for the assembler (like `_run_guards`) → rejected: the log always
  runs at exit, no test variation needed; simpler to import directly
- Skip typed event classes and leave bare string `LedgerEvent` usage → rejected: REQ-06-04
  explicitly requires typed classes with window fields in `events.py`

## ⚠️ Allowed-Paths Gap (requires operator resolution)

`mx_cmd.py` is NOT in the brief's allowed paths, but wiring REQ-06-03 ("log rendered before
signature") requires calling the assembler from `mx_exit_cmd`. Recommendation: add
`src/gzkit/commands/mx_cmd.py` to allowed paths with a brief amendment before Stage 2 begins.

## Context

- `src/gzkit/mx/log.py` — CREATE new module; no gzkit.* import restriction here (marker.py has
  that constraint, not log.py); can freely import `gzkit.ledger`
- `src/gzkit/events.py` — add `MxSessionOpenedEvent` + `MxSessionClosedEvent` typed classes;
  add to `TypedLedgerEvent` union; update `mx_cmd.py` to use them
- `src/gzkit/commands/mx_cmd.py` — import + call `log.assemble_and_render` before writing the
  closed event (NEEDED but not in current allowlist — see gap above)
- `tests/mx/test_mx_log.py` — CREATE unit tests for all four REQs; follows pattern of
  `tests/commands/test_mx_exit.py` (TemporaryDirectory, direct function calls, injectable
  collaborators)

## Files

- `src/gzkit/mx/log.py` — CREATE
- `src/gzkit/events.py` — MODIFY (add typed event classes)
- `src/gzkit/commands/mx_cmd.py` — MODIFY (wire log render into mx_exit_cmd)
- `tests/mx/test_mx_log.py` — CREATE

## Steps

### Task 1: Add MxSessionOpenedEvent + MxSessionClosedEvent to events.py (REQ-06-04)

1. RED: write test in `test_mx_log.py` that imports `MxSessionOpenedEvent` from `gzkit.events`,
   constructs one with `session_id`, `reason`, `attestor`, `inspection_scope`, `opened_at`; asserts
   the `event` discriminator is `"mx_session_opened"`. Run → ImportError (class missing).
2. GREEN: add `MxSessionOpenedEvent` class to `events.py` with those fields + `Literal["mx_session_opened"]`.
3. RED: test `MxSessionClosedEvent` with `session_id`, `attestor`, `closed_at`; assert `event` is
   `"mx_session_closed"`. Run → ImportError.
4. GREEN: add `MxSessionClosedEvent`, add both to `TypedLedgerEvent` union.
5. REFACTOR: update `mx_cmd.py`'s `_mx_session_opened_event` and `_mx_session_closed_event` to
   use the typed classes (emit via `ledger.append`).

### Task 2: Create src/gzkit/mx/log.py — window assembler (REQ-06-01 + REQ-06-02)

Window assembly logic:
- `assemble_window(ledger_path, session_id, git_root)` → reads ledger raw (stdlib json line by line)
  for events after the `mx_session_opened` for `session_id` up to but not including
  `mx_session_closed`; reads git log between those timestamps (`git log --after=<open_ts>
  --before=<close_ts>` or just `--after=<open_ts>` if session still open); returns a `MxLog` datamodel.
- `parse_artifacts(commit_msg)` → extracts ADR-*, OBPI-*, REQ-* refs from commit message via regex.
- `render(log)` → returns a human-readable string summary for console display.

6. RED: test that `assemble_window` with a fake ledger containing only open event + one non-MX
   event (no git commits) returns a `MxLog` with the event in its window. Watch ImportError on
   `from gzkit.mx.log import assemble_window` → create stub.
7. Watch assertion-level failure → GREEN: implement assemble_window to read ledger by session_id.
8. RED: test `parse_artifacts("fix: repair ADR-0.0.74 — closes REQ-06-01 (OBPI-0.0.74-06)")` →
   asserts `{"ADR": ["ADR-0.0.74"], "OBPI": ["OBPI-0.0.74-06"], "REQ": ["REQ-06-01"]}`.
9. GREEN: implement `parse_artifacts` with regex patterns for ADR-*.*.*, OBPI-*.*.*, REQ-*.
10. RED: test `render(log)` contains `"Window:"` header and any events/commits found.
11. GREEN: implement `render`.

### Task 3: Wire log render into mx_exit_cmd (REQ-06-03)

12. RED: test in `test_mx_log.py` that when `mx_exit_cmd` is called (green guards), a mock
    assembler is called BEFORE `mx_session_closed` is written to ledger. Use call-ordering sentinel
    (list that accumulates `"log"` then `"closed"`; assert `log` first).
13. GREEN: in `mx_exit_cmd`, after guards pass, call `assemble_and_render` and `console.print` the
    result, then write `mx_session_closed`.
14. REFACTOR: extract `assemble_and_render(root, session_id)` as a single entry point in log.py.

### Task 4: Verification pass

```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --ledger
uv run gz validate --documents
uv run mkdocs build --strict
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --ledger
test -f src/gzkit/mx/log.py
test -f tests/mx/test_mx_log.py
uv run gz covers OBPI-0.0.74-06-mx-log-auto-assembled --json
```

## Notes

- `log.py` MAY use `gzkit.ledger` freely (no isolation constraint like marker.py)
- Git calls use list form subprocess (no shell=True; cross-platform per cross-platform.md)
- Typed events use `_EventBase` pattern; fields flattened by `_serialize`; add to `TypedLedgerEvent` union
- The `opened_at` in `MxSessionOpenedEvent` is the `ts` field of the event (= `_EventBase.ts`);
  the typed class can expose it as a dedicated field or use the inherited `ts`
- Tests use `TemporaryDirectory`, `json.dumps` ledger lines, no real git operations (git
  calls mocked or git log run against a temp repo)
- ALL FOUR REQs: 01+02+03 are BEHAVIOR (→ @covers unit tests); 04 is SUPPORT (→ ledger event
  + gz validate --ledger exit 0)
