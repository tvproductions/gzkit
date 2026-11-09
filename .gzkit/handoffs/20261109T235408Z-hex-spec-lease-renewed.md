---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-09T23:54:08Z'
agent: claude-code
continues_from: .gzkit/handoffs/20261109T110105Z-hex-spec-groups-b-to-d.md
---

## Current State Summary

Successor to `20261109T110105Z-hex-spec-groups-b-to-d.md`, folding its delta: the MX session lease (session 57346836) was renewed on the operator's word for another 24h, no guard run; one `session_exit_bookmark_skipped` event and the `mx_session_lease_renewed` event landed in the ledger. No record entry changed. The hexagonal specification R&D run (house-style row 7(c), gz-rnd) stands where the predecessor left it: groups B, C and D ruled, group E opened with the config question put and unanswered, aggregates and bounded contexts waiting for Khononov's passages, disposition rows 1 to 6 empty, the close not started. Record: `docs/rnd/hexagonal-specification.md`.

## Important Context

- One question at a time, stated first in one sentence, with a recommendation and a rating against the constellation (4/4 hexagonal: Cockburn, Montenegro, Cosmic Python, Khorikov; 6/6 once DDD enters, adding Evans and Khononov). Favour Montenegro unless there is reason to disagree.
- Licensed sources never land in the repo: the Montenegro MEAP, Khorikov and Evans reports are held in the session scratchpad outside the repo, and only short cited key notes enter the record. The licensed PDFs carry a watermark: never copy a name or email from them. Kindle books (Khononov, Cockburn's book) reach the run only as passages the operator pastes; do not work around DRM.
- Two agent citations were wrong this session and corrected in place (Montenegro converts in the handler, not the adapter; no ruled import table existed). Read the source pages before citing a position.
- Ask before each commit and before each push unless the operator says both; the auto-mode classifier refused a push the operator had not asked for.
- The run executes nothing: every consequence is carried to the disposition map. Canon rule 7 and the canon page stay unchanged until a row-level go.
- The mx-session lease expired (MX session 57346836); renew or exit only through gz-mx on the operator's word.

## Decisions Made

- [operator-ruled] Renew the MX session lease, write a successor handoff and git sync (verbatim: "renew, new handoff, and git sync").

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with `uv run gz handoff decide`.
2. On the operator's go, resume the run under gz-rnd: append a decision entry quoting the resume words, check the record against git, and recompute the frontier.
3. Put the open config question again: config read only at startup by the configurator through a config adapter, merged (gzkit defaults, adopter overrides), validated into frozen settings and passed as values (59 modules read config files today).
4. Continue group E (integration events and external contracts, bootstrapping and what `gz init` scaffolds), then F (enforcement, uv-build, architecture tests, BDD/TDD and mocking detail) and G (transforming gzkit).
5. When the operator pastes Khononov's passages (ch. 3, ch. 4, aggregates and event sourcing), take aggregates and bounded contexts, including assigning each of the 78 ledger event types an owning entity and a drydock name.

## Pending Work / Open Loops

- The predecessor handoff's advisement (resume the run) has no booked `gz handoff decide` ruling; the operator's words this session asked for renewal and a handoff, not a resume.
- Open question: the config ruling (put, unanswered): config read only at startup by the configurator through a config adapter, merged, validated into frozen settings and passed as values.
- Held for the bounded-context question: the ontology's DDD role; "one team per context" for one operator and many agents; the 78 ledger event types' owners and drydock names.
- Held for the disposition map: gzkit consuming rhea (not now; revisit on a rhea write side or several backends); rhea's runtime `py-gzkit` dependency (row 2, in rhea); whether `@advances` fulfils its declared intent (row 2); the closed-set widening rule and validator (row 4, commissioned); the proving-ground work in rhea (route open).
- Carried unexecuted from earlier sessions: rule 7 and the canon page rewritten; the formatter port; the airlock split; GzkitError leaves core; Harness-Purity renamed; ADR-pool.hexagonal-folder-structure-realization read before cited; the migration through a classic ADR.
- The MX session's advisory debt keeps aging; the renewal ran no guard, and `gz mx exit` through gz-mx remains the full-strength gate.
- Other house-style rows and both drydock change orders wait for the operator's go on each.

## Verification Checklist

- `git log --oneline -4` shows `df0719fe6` and the handoff commit on main, level with origin.
- `grep -c '^## decision' docs/rnd/hexagonal-specification.md` counts the decision entries; the newest is the outside-in build order.
- `grep -n '| 7 |' docs/rnd/hexagonal-specification.md` shows row 7 commissioned with (a) and (b).
- `uv run gz handoff rulings --search "kernel"` returns this session's booked rulings.

## Evidence / Artifacts

- `docs/rnd/hexagonal-specification.md`
- `docs/rnd/hexagonal-specification/sources/cosmic-python-reading-2026-11-08.md`
- `src/gzkit/core/models.py`
- `src/gzkit/schemas/obpi.json`
- `src/gzkit/commands/obpi_complete.py`
- `tests/policy/test_import_boundaries.py`

## Settled Rulings

2135 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
