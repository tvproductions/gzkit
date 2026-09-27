# Session end

You are here at the end of a phase or a session.

## At a phase boundary

Work top to bottom; the first that fits wins.

1. **Continue** — the next phase needs this one verbatim (design into booking,
   plan into the pipeline), or there is room left to think clearly.
2. **Clear** — nothing in this session matters to what comes next; the ledger
   and the handoff chain carry the state.
3. **Subagent** — a bounded, independent track that needs no steering,
   dispatched with its Why.
4. **Compact** — the context matters and you stay in the session; tell the
   summary what the next phase needs. `CLAUDE.md` § Compact Instructions lists
   what must survive.

Decide only at a boundary. Mid-phase, continue or split the rest into subagents.

## At the end of a session

1. **`gz-airlock`** — `uv run gz airlock out` accounts for what the transit
   disturbed.
2. **[Commit and sync](commit-and-sync.md)** — land the work.
3. **`gz-session-handoff`** — `uv run gz handoff create` writes the handoff:
   current state, decisions with their attribution, next steps, open loops.
   Use mode `CHECKPOINT` to bookmark mid-flight without concluding.

## Branches

- **Holding an OBPI lock** — the handoff must record the lock state; release
  the lock only through the pipeline's own path.
- **A ruling arrived after the handoff was written** — seat it in the next one
  with `--settled`.

## Only you can

Rule on the next session's advised steps when it resumes.

## Then

[Session start](session-start.md), next time.
