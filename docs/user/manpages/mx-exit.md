# gz mx exit

Close the Maintenance Hangar — hard gate.

## Usage

<!-- gz-validate-skip: command-shape -->
```bash
gz mx exit --attestor ATTESTOR
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--attestor ATTESTOR` | Operator identity who signs airworthiness (required; never an agent) |

## Runtime Behavior

- Validates that `--attestor` is non-empty; fails closed (exit 1) if empty or whitespace-only —
  no marker is cleared, no ledger event is emitted.
- Checks the hangar is open (`marker.is_active`). Fails closed (exit 1) if not.
- Holds the marker through the re-run, marked `exiting: true`, so `checkpoint.resolve()`
  demotes nothing — every guard emits at its real `GZ_<LEVEL>` severity (no advisory
  demotion) while the open session stays bound to its marker, never a dangling state.
  This is how `gz obpi complete` holds its lock through its checks (GHI #1257).
- Runs every guard at full strength against the project. A session past its lease is
  announced by `--mx-hardening` and never blocks the exit.
- If any guard is red: puts the marker back as it was, exits 3 — hangar stays open.
- If all guards are green: fires the airlock-OUT membrane (co-equal with airlock-IN, ADR-0.33.0)
  **after** the hard guard-gate passes and **before** the close signature — it is **additive** to
  the hard gate, never a replacement. It books one `airlock_out` L2 event and surfaces any drift
  findings as warnings; it is **diagnostic-only** and never blocks the close (real-entry accounting
  deferred). Then writes one `mx_session_closed` ledger event and only then removes the
  marker; the operator's `--attestor` is the airworthiness signature.
- Before the airlock-OUT and the signature, renders the MX log for the operator, assembled
  from the ledger and the commits between the session's enter and now (OBPI-0.0.74-06). The
  log is the maintenance record's view (RP-12 rulings 166, 189 to 191,
  `docs/governance/harbor-ro12-contractor-kit.md`):
    - **Maintenance record**: the entries booked under this session within its window
      ([`gz wp entry book`](wp-entry-book.md)), grouped by order, each in the block
      [`gz wp entry show`](wp-entry-show.md) writes, its Landed line naming the window commits
      whose subjects name it, `(ENT-<NN>-<slug>)`, or `not landed`. A subject is read as git
      reads it, the first paragraph with its lines joined; an id in the body alone lands nothing.
    - **Unrecorded work**: every window commit whose subject names no entry this session's
      record holds, and every one naming an entry it does not hold (a mistyped id, a voided
      entry, another session's), which says `names <id>, which this session's record does not
      hold`. A commit naming one held and one unheld entry shows in both places: on the held
      entry's Landed line, and here with the unheld id named (rulings 189 and 194).
    - **Fixes**: every window commit with the ADRs, OBPIs and REQs it names, then the
      artifacts touched and the count of ledger events in the window.
- If the maintenance record cannot be read (an `entry_booked` row, or an order's closing
  `order_transitioned` row, does not parse): names the row and the `gz ledger correct` void
  that recovers it, puts the marker back as it was and exits 3. No signature is taken over a
  record that could not be read (ruling 190).
- If git cannot be read (not installed, the project not a repository, one with no commit
  yet, or a commit message carrying git's field or record separator): names the cause
  (`git could not run (<error>)`, `` `git log` exited <code>: <git's message> `` or
  `` a `git log` record did not parse: <record> ``), says the window's commits cannot be read,
  puts the marker back and exits 3. The view is never taken as an empty window (ruling 193).
- The log is printed as written: brackets, `:name:` emoji codes and long lines in an entry or
  a commit subject read as their authors wrote them.

**There is no `--force` flag.** You cannot narrow your way out of a red guard.
**Exit is the ONLY path that clears the marker.** A marker removed without a matching
`mx_session_closed` event is a detected dangling state (ADR-0.0.74 Boundary Invariant #4).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Hangar closed successfully |
| 1 | Validation failure: empty attestor or no active session |
| 2 | System/IO error |
| 3 | Guards reported red, the maintenance record cannot be read, or git cannot be read — hangar remains open |

## Examples

<!-- gz-validate-skip: command-shape -->
```bash
# Close the hangar after completing maintenance work
gz mx exit --attestor g0
```

The MX log it renders before the signature, observed 2026-11-21 through
`gzkit.mx.log.assemble_and_render` in a scratch project set up as
`tests/commands/test_wp_entry.py` sets one up: one entry booked and the commit that landed
it. The test helper opened the marker, so the session id is that fixture's and its reason
and attestor are blank:

```console
=== MX Maintenance Log (complete by construction) ===
Window: 2026-10-31T00:00:00+00:00 → (open)
Session: test-session
Reason:
Attestor at enter:

Maintenance record (1 entry):
  ORD-01-import (WP-01-stamp):
    ENT-01-stamp-import on ORD-01-import (WP-01-stamp)
      Booked:      2026-11-21T08:57:53.030919+00:00
      Performer:   D-7b33cf373c3bfc9a
      Description: The stamp generator imports its template again.
      Before:      tests.test_stamp fails: ImportError on the template
      After:       tests.test_stamp passes, 12 tests
      Witness:     uv run -m unittest tests.test_stamp
      MX session:  test-session
      Landed:      bc048dec67af fix(stamp): the template imports again (ENT-01-stamp-import)
      Gate 5:      not signed

Unrecorded work (0):
  (none)

Fixes (1):
  - bc048dec67af fix(stamp): the template imports again (ENT-01-stamp-import) [(no artifacts named)]

Artifacts touched:
  ADRs:  (none)
  OBPIs: (none)
  REQs:  (none)

Ledger events in window: 9
```

## Related

- [`gz mx`](mx.md) — MX mode command group overview
- [`gz mx enter`](mx-enter.md) — Open the Maintenance Hangar
- [`gz wp entry show`](wp-entry-show.md) — the maintenance record the log renders
- ADR-0.0.74: MX Mode — Maintenance Hangar (design and decision record)
