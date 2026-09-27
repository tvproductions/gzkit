# Repair

You are here when governance itself needs repair: state that gates refuse, a
completion that should not stand, or a surface you must touch outside a planned
unit of work.

## Steps

- **Governance repair** → **`gz-mx`**: `uv run gz mx enter` opens the
  maintenance hangar, where ERROR-level checks report without failing so the
  repair can land; `uv run gz mx exit` closes it.
- **Reconnaissance with light repair at most** → **`gz-airlock`**:
  `uv run gz permitted-entry`.
- **Undo a completion** — two verbs, not interchangeable (`AGENTS.md` § Gate
  Covenant):
  - `uv run gz obpi withdraw` retires an OBPI permanently: superseded, phantom
    or duplicate.
  - `uv run gz obpi repudiate` reverses a completion whose attestation or
    evidence was invalid while the work still stands; it can be completed again
    by a genuine attestation.

## Branches

- **A hook blocks you** — it means evidence or pipeline state is missing;
  diagnose it, never hand-write the marker or the ledger row.

## Only you can

Repudiate a Gate 5 attestation; the attestor and reason are required.

## Then

[Commit and sync](commit-and-sync.md), then back to the interrupted flow.
