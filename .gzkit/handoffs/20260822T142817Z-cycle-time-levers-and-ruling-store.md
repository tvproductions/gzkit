---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T14:28:17Z'
agent: claude-code
session_id: 6100d587-9db8-4fbe-8a0d-fe5f9925e85c
continues_from: 20260822T132232Z-ghi-852-authorship-floor-and-handoff-ruling-chain.md
---

## Current State Summary

GHI #838 is CLOSED/COMPLETED. Three commits landed on origin/main (HEAD 6db73e06, ahead/behind 0 0, tree clean, no locks, no hangar open); `uv run gz check` exits 0 and the full suite is 8677 tests OK.

What landed: (1) fc3f0956 raised the validate_cmd module-size ratchet entry 1242 -> 1309 on operator override, restoring the 67 lines 602a1c2d had surrendered. (2) c6b3f42a repointed three dangling `GHI #855` citations -- an issue number that was never allocated -- at commit 02ca03ee, the artifact that actually landed the fix. (3) 6db73e06 moved the settled-ruling corpus out of the handoff documents into an append-only store: handoffs drop from 107,480 B to ~9,600 B (91.1%), 461 rulings preserved, nothing retired.

THIS HANDOFF IS THE FIRST ARTIFACT OF THAT CHANGE. Its Settled Rulings section is a pointer, not a corpus. Read the rulings with `uv run gz handoff rulings`.

The session closed on operator feedback about cycle time -- verbatim: 'every fix takes 30, 45, 60 minutes - ridiculous'. That is the subject of the two advised steps below.

## Important Context

THE CYCLE-TIME COMPLAINT IS MEASURED, NOT IMPRESSIONISTIC. On the #838 fix the full unit tier ran 136s and was invoked three times (~7 min of wall clock), plus `gz check`. The first full run returned 21 failures, every one a deterministic consequence of adding ONE CLI verb: `config/doc-coverage.json`, a manpage, the manpage index, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and a wielding skill (Invariant 1 fails `--skill-alignment` without one). None was a surprise. The loop that costs the clock is discover-reactively-then-re-run-the-slow-thing.

THE RULING STORE'S THREE HELD PROPERTIES ARE LOAD-BEARING; do not 'simplify' them. (a) The store is read only when `continues_from` is asserted -- reading it unconditionally is one line shorter and silently repeals the GHI #709 guarantee that an unlinked handoff is a chain root. (b) The legacy prose walk survives, so pre-cutover handoffs still contribute; dropping it makes the transition the largest silent loss in the channel's history. (c) The store is written BEFORE the document, so a failed validation leaves rulings unreferenced (recoverable) rather than a document promising a corpus the store never got (a lost ruling).

`ruling_key` MUST NOT BE WIDENED. GHI #838 rejects that fix by name: a duplicate is visible and harmless, collapsing two distinct rulings drops a booked operator ruling silently. The identity problem is real and unfixed -- it needs the typed `ruling` ledger event that the campaign's Movement D names, and the store is the surface that event replaces.

THE RATCHET RAISE CONTRADICTS A DECLARED INVARIANT AND WAS OPERATOR-RULED. ADR-0.0.73 Boundary Invariant #8 requires 'a monotonic shrink-ratchet (a committed baseline the list can only decrease against)'. The raise makes the baseline increase. It was surfaced with both quotes before the edit and overridden; `fc3f0956` carries the full record. Measured during it: the gate returns exit 0 on an increased entry, because `compute_breaches` never compares an entry against its own history -- so BI #8's monotonic half has no mechanical witness in either direction.

## Decisions Made

- [operator-ruled] Raise the module-size ratchet entry (verbatim: 'just raise whatever limit this is'), against the agent's recommendation to leave validate_cmd.py at zero headroom and against ADR-0.0.73 Boundary Invariant #8. Booked as an explicit override in fc3f0956; the concern was surfaced with both quotes before any edit.
- [operator-ruled] Do the GHI #838 transport fix (verbatim: 'do the 838 transport fix'), selected after the agent recommended it over the three retirement-rule alternatives.
- [operator-ruled] Fix a surfaced defect rather than presenting it as a menu (verbatim: 'why can't you do aything right?' -- spelling preserved -- on being offered two options for the dangling GHI #855 citation instead of a repair). The Prime Directive already binds this; the agent asked anyway.
- [operator-ruled] Ruling on the resumed handoff: proceed on three of five advised steps; steps 4 (hangar demoting post-authoring-src-commits) and 5 (resume ADR-0.35.0) set aside. Booked via gz handoff decide, session 6100d587.
- [agent-chose] Answered #838 by fixing the TRANSPORT rather than the RETENTION. The literal question -- should a booked ruling ever stop carrying forward -- is answered NO; every retirement rule available either needs an identity model the code deliberately refuses or risks the silent-loss direction #838 names as worse.
- [agent-chose] Put ruling identity (`ruling_key`, `dedup_rulings`) in the new storage module rather than leaving it in handoff_api. The layer that must not write a ruling twice is the layer that owns what 'twice' means.
- [agent-chose] Repaired the two existing test suites that asserted against the document body rather than deleting them. The property they protect is unchanged; only the surface it lives on moved.
- [agent-chose] Did NOT file a successor GHI for the ruling-identity gap. Its destination is already named in the campaign's Movement D, and a GHI that shadow-tracks a named destination is the long-lived-tracker anti-pattern ghi-author forbids.

## Immediate Next Steps

1. Build the new-CLI-verb coupled-surface list. Six surfaces are fixed and enumerable for every new verb: `config/doc-coverage.json`, `docs/user/manpages/<verb>.md`, `docs/user/manpages/index.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and a wielding skill under `.gzkit/skills/**`. A checklist in `.claude/rules/cli.md` is the floor; a `gz` verb that scaffolds all six is the better shape. This collapses three full-suite runs into one and is the cheaper of the two levers.
2. Evaluate parallel test execution and GHI #835 for the DEV LOOP, not for the budget. `.gzkit/rules/tests.md` records the unit tier at 268.1s serial versus 71.4s across 32 processes, and rules parallelism out on the ground that a ratcheting workload cannot hold a constant ceiling. That reasoning is about the smoke budget and says nothing about iteration speed. GHI #835 (roughly 46 serial validator steps in gz check) is the same lever on the other gate and has been open and untouched.
3. Decide whether the module-size ratchet's raise direction should have a mechanical witness. `compute_breaches` compares current SLOC against the listed entry and never against the entry's own history, so an entry that INCREASED passes at exit 0 -- measured during fc3f0956. GHI #853 carries the other half (nothing reports an entry looser than its module; 861 lines unrecorded across three entries). A fence would have to diff the entry against git history.
4. Rule on whether an open hangar should be able to demote post-authoring-src-commits, the Stage-2 production-code fence. Currently pinned CRITICAL to preserve prior behaviour; the mx-mode declared default for a non-floor guard points the other way. Carried unresolved across three sessions.
5. Resume ADR-0.35.0-canon-entry-corpus-landing -- the lowest-semver feature ADR holding unlanded work, so ascending-semver order puts it ahead of ADR-0.36.0 and ADR-0.37.0. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for live lifecycle; no count is transcribed here.

## Pending Work / Open Loops

GHI #853 -- filed this session, open. The module-size ratchet has no arm reporting an entry looser than its module; 861 lines of measured improvement sit unrecorded across parser_artifacts.py (666), obpi_complete.py (127) and parser_maintenance.py (68). Its comment thread also records that the raise direction passes at exit 0.

The ruling-identity gap -- unfixed and deliberately unfiled. GHI #838 [settled]'s worked example (one decision re-derived by three sessions in three phrasings) needs the typed `ruling` ledger event; the destination is the campaign's Movement D, and the new store is the surface that event replaces.

GHI #849 (ARB RED witness inert on landed work) and GHI #835 (roughly 46 serial validator steps) -- both open, both carried unchanged across four handoffs, both untouched. The #835 measurements still live only in the db6ec623 and 4b543052 commit bodies, never posted to the issue.

GHI #611 -- open; still the genuine governed route out of a mis-ordered ledger.

GHI #847 [settled]'s ledger-writer arm -- still dead-lettered. Named in a closed issue's comments and in successive handoffs, tracked nowhere.

Two advisory findings gz check reports and this session did not address, both pre-existing: AGENTS.md renders 42235 B against the codex 32768 B delivery cap, with the operator-doctrine-verbatim-canon section straddling it and architectural-boundaries starting past it, so undelivered canon is not in force; and 715 REQs carry no covering test.

adr_audit.py remains at 1034 == 1034 -- the other zero-headroom grandfather entry, untouched because nothing is trying to add a line there.

## Verification Checklist

uv run gz check  # expect: exit 0, 'All checks passed'
uv run -m unittest -q  # expect: 8677 tests, OK
uv run -m unittest tests.governance.test_handoff_ruling_store  # expect: OK, 12 tests
uv run gz handoff rulings --limit 3  # expect: the three most recent operator rulings
gh issue view 838 --json state,stateReason  # expect: CLOSED/COMPLETED
gh issue view 853 --json state  # expect: OPEN
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0
uv run gz obpi lock list  # expect: No active locks

## Evidence / Artifacts

`src/gzkit/handoff_rulings.py` -- the append-only store and ruling identity (new)
`src/gzkit/handoff_api.py` -- composition unions store, legacy prose, and author-seated rulings under the lineage precondition
`src/gzkit/commands/handoff.py` -- the rulings reader verb and the capped resume preview
`src/gzkit/cli/parser_handoff.py` -- gz handoff rulings registration
`tests/governance/test_handoff_ruling_store.py` -- twelve tests, written RED first (new)
`.gzkit/handoffs/rulings.jsonl` -- the corpus, 461 rulings (new)
`docs/user/manpages/handoff-rulings.md` -- operator surface for the new verb (new)
`data/module_size_grandfather.json` -- validate_cmd entry raised 1242 to 1309 on operator override
`.gzkit/handoffs/20260822T132232Z-ghi-852-authorship-floor-and-handoff-ruling-chain.md` -- predecessor, the last handoff to carry its corpus as prose

## Settled Rulings

461 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
