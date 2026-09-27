# Session start

You are here at the start of a session: before any work, you need the last
session's memory and the project's current state.

## Steps

1. **Orientation arrives on its own.** A SessionStart hook prints the active
   campaign, the newest handoff and its freshness.
2. **`gz-session-handoff`** (resume) — read the handoff and its lineage, check
   each claim it makes against the ledger, and present its advised steps. A
   handoff advises; it never authorizes. Book the operator's ruling with
   `uv run gz handoff decide`.
3. **`gz-status`** — the workflow fronts, blockers and next actions, read from
   the ledger and the campaign plan.
4. **`gz-airlock`** — `uv run gz airlock in` before touching a target, to see
   its seam-map.

## Branches

- **One ADR's full context in one document** → `uv run gz context <ADR-ID>`.
- **Relationships and readiness** → `gz-state`; **one ADR** →
  `gz-adr-status`. See [Traceability](traceability.md).
- **The whole-project view** — what gzkit is becoming and where design and
  reality diverge → `gz-big-picture` (operator-invoked).
- **The handoff is stale** — re-verify more deeply before presenting it; its
  age never waives the operator's ruling.

## Only you can

Rule on the handoff's advised steps: proceed, pause, hold or revert. Choose the
next piece of work.

## Then

Whichever flow the chosen work belongs to. At the end of the session,
[Session end](session-end.md).
