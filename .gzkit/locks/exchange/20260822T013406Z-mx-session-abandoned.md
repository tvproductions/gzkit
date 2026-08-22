---
mode: CREATE
adr_id: ADR-unknown
obpi_id: mx-session
branch: main
timestamp: '2026-08-22T01:34:06Z'
agent: claude-code-3c344686
abandoned: true
category: reaping
reason: 'orphan left by gz mx exit, which never released the lock it claimed (GHI
  #848)'
last_lock_event_timestamp: '2026-08-21T08:56:53.699735+00:00'
last_commit_sha: 6a03b24c40c17c138cab3dbab882e6c6a8929398
---

<!-- Degenerate exchange record for mx-session — abandon path -->

## Current State Summary

Lock surrender via `--abandon reaping:orphan left by gz mx exit, which never released the lock it claimed (GHI #848)` by agent `claude-code-3c344686`.

## Important Context

Degenerate exchange record written as the register-entry pairing for an abandoned lock release (token-block discipline; see `.gzkit/rules/token-block-discipline.md` § Sub-Invariant 1).

## Decisions Made

- Lock for mx-session abandoned by claude-code-3c344686 (category=reaping, reason=orphan left by gz mx exit, which never released the lock it claimed (GHI #848)).

## Immediate Next Steps

1. Operator review of the abandonment reason.
2. If recovery is intended, re-claim the lock via `gz obpi lock claim`.

## Pending Work / Open Loops

- OBPI mx-session was abandoned mid-traversal; resume work requires re-claim plus a fresh exchange record at completion.

## Verification Checklist

- [ ] `git rev-parse HEAD` returns `6a03b24c40c17c138cab3dbab882e6c6a8929398` (or operator explains drift).
- [ ] Branch matches `main`.

## Evidence / Artifacts

- `.gzkit/locks/obpi/mx-session.lock.json` — lock file at abandon (deleted on release).
