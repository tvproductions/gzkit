---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-31T09:32:59Z'
agent: claude-code
session_id: c015e4e7-5a55-42ba-b7f2-51b6be9855d0
continues_from: .gzkit/handoffs/20260831T083104Z-control-surface-rationalization-uncoordinated-ghi-family.md
---

## Current State Summary

Tree is clean and synced: `git status --short` empty, `git rev-list --left-right --count origin/main...HEAD` returns `0 0`, `uv run gz obpi lock list` reports no active locks. No pipeline marker, no OBPI scope, no open TASK. HEAD is `764bcef4`.

One commit landed and was pushed this session, as two separate operator authorizations:

- `764bcef4` fix(content): enforce corpus entry-id uniqueness (GHI #874)

That commit adds Algebra 1 (IDENTITY) to `validate_tombstone_algebra`, checked ahead of Algebra 2/3/7. Both callers of that function route through it, so the read boundary (`Corpus.loads`) and the write boundary (`corpus_store.append_entry`) are closed by one edit. `uv run gz check` exits 0 on the tree, and the pre-push gate passed.

Four GHIs were closed: #923, #863, #874, #878. Two were filed: #925 and #926. One disposition was recorded without work starting: #873.

THE FINDING THAT MATTERS MORE THAN ANY SINGLE ITEM. Of the four corpus-cluster GHIs the operator cleared for work, only ONE needed code written. #863 was fixed nine days earlier in `a68cb860`; #878's ruled remedy was already built under #885 in `1fb42c25`, and the repair verb's own help text names GHI #878 as its subject. #923 was likewise already fixed before this session. Three of the seven items touched were open issues whose work had shipped days earlier and which nobody closed. The handoff this session resumed framed the family's incoherence as work done in isolation; the same failure also appears as work done and never BOOKED, which leaves a stale GHI body reading as current to the next session.

## Important Context

RE-DERIVE EVERY GHI PREMISE BEFORE WORKING IT. This is the session's load-bearing lesson and it cost four commands to learn. #863's body still asserted "`retire` imports none of it" nine days after `retire.py:451` began importing `warn_on_rendition_drift`. #878's body said "Not a patch. It needs a ruling on posture first" and enumerated three postures; the ruled posture was already implemented. An agent that trusts a GHI body as current will rebuild landed work.

THE ROUTING PRECONDITION IS NOT A FILE-PATH CHECK. AGENTS.md § Defect-fix routing says to surface the DISPOSITION, never the bare match. Applied to the corpus cluster: five live ADR-0.35.0 briefs (03 and 08 Active; 04, 05, 06, 07, 10 Draft) touch `src/gzkit/content/models/corpus.py` and `src/gzkit/content/corpus_store.py`. But `grep -rn "uniqueness\|unique id\|duplicate id\|id collision"` across every ADR-0.35.0 brief AND the ADR body returns ZERO hits. The live briefs share the SURFACE with GHI #874, not the SUBJECT. Reading only the file overlap would have stopped work that was clear; skipping the check entirely would have started work the briefs own.

WHY #873 IS NOT GHI DIRECT REPAIR, DESPITE GHIs BEING AUTHORIZED FOR DIRECT REPAIR ALWAYS. The implementation is FAITHFUL to the pinned algebra; the defect is in `ADR-0.35.0` § "Tombstone fold algebra (binding)" itself. The current behaviour is pinned by `tests/content/test_corpus_model.py::test_superseding_a_replacement_restores_the_original_row`, landed under OBPI-0.35.0-01, which is Completed and attested. Amending the clause unpins attested work and ripples into Draft briefs 04, 05 and 10. That is OBPI territory, and the IRON LAW reserves initiation to the operator.

THE TRACTABILITY ASYMMETRY THAT SCOPED #926. GHI #878's own detection argument was grounded in a property the corpus has: a retraction row carries `retires`, so a reconciler has something to enumerate. That does NOT transfer to `register.py:316-323` or `adr_demote.py:486-496` — a renamed artifact carries no pointer to its former name, and a parked OBPI carries no marker naming its demotion. A validator copying `corpus_retirement_witness.py`'s shape there would have no left-hand side. This is why the corpus fix does not close the class by extension, and why #926 needs a posture ruling of its own rather than a patch.

THE #925 COUPLING TO #924, RESTATED BECAUSE IT IS EASY TO LOSE. `_foreign_vendor_roots` (`src/gzkit/rules/__init__.py:492`) derives the no-Claude-redirect set from the DECLARED vendor set. #924 removes the Copilot vendor from that set, which makes `.github` newly eligible for a redirect. #925 reports that the skill-mirror pass already bypasses the same exclusion downstream. Both remedies read one derivation from opposite ends; rule them together.

COMMIT TRAILER CONVENTION. The Claude Code harness asks for a `Claude-Session:` trailer. Recent repo commits (`97cbfede`, `a68cb860`, `764bcef4`) carry none, `gz validate --commit-trailers` is active, and the repo uses `Task:` in slug form for direct-fix work outside OBPI scope. This session followed repo convention and surfaced the divergence to the operator rather than resolving it silently. No ruling was given.

INHERITED CAUTIONS THAT STILL BIND. `gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status <ADR-ID>` instead. Any commit touching `src/**` or `tests/**` needs a `Task:` trailer. A verifier piped into another process is refused by `.claude/hooks/verifier-pipe-gate.py`; use `set -o pipefail`, or capture to a file and echo the real exit. This gate fired twice this session, on `unittest` and on `ruff format`.

## Decisions Made

- [operator-ruled] Proceed with the agent-drafted cluster sequence rather than the handoff's advised order, taking GHI #923's close first (verbatim: "proceed with your sequence, close 923 first"). Booked to Layer 2 via `gz handoff decide`.
- [operator-ruled] Take GHI #874 now rather than deferring it until ADR-0.35.0 briefs 03 and 08 land. Chosen against the alternative of deferring on file adjacency, after the routing precondition showed no brief REQ owns id uniqueness.
- [operator-ruled] GHI #873 is dispositioned as an operator-led amendment to Algebra 6 — distinguish a `supersedes` row's tombstone role from its content role — rather than an agent direct fix or a keep-and-document acceptance. The issue stays OPEN; the agent recorded the ruling and started nothing.
- [operator-ruled] GHI #878 takes the detect-and-repair posture, option (a) of the three its body enumerated, over write-ahead and over accept-and-disclose.
- [operator-ruled] Push `764bcef4`, then close GHI #874 and start GHI #878 (verbatim: "push it, then close 874 and start 878"). Commit and push remain separate authorizations in this repo.
- [agent-chose] Enforced id uniqueness inside `validate_tombstone_algebra` rather than adding a Pydantic model validator or a check at each call site, because both existing callers already route through that one function — one edit closes the read and write boundaries together.
- [agent-chose] Ordered the identity clause FIRST, ahead of Algebra 2/3/7, because every later clause reads ids through a set or a dict and a clause running after those are built is one the alias has already corrupted.
- [agent-chose] Closed GHI #878 as fixed for its corpus member and routed the class remainder to a new child issue (#926) rather than holding #878 open, because its title, its measured evidence and the operator's ruling are all corpus-scoped.
- [agent-chose] Filed #925 rather than fixing the mirror leak in flight, despite it passing every direct-fix threshold, because its remedy couples to the vendor-set change in #924 and burning it down alone reproduces the incoherence the operator named.
- [agent-chose] Followed the repo's `Task:` trailer convention and omitted the harness-requested `Claude-Session:` trailer, surfacing the divergence to the operator instead of deciding it silently.

## Immediate Next Steps

1. RE-DERIVE EACH REMAINING FAMILY GHI'S PREMISE AGAINST THE TREE BEFORE SEQUENCING THEM. This session found three of seven items already discharged. Any plan built on the open-issue list as written will contain work that no longer exists. Read the surface each body cites and confirm the defect is still present; the cost is a few commands per issue and it changes what the plan should contain.
2. Rule whether GHI #922 retargets into GHI #921. Carried unchanged from the predecessor handoff and still unruled. It was filed as a validator-coverage gap, then measurement showed the shape witness audits the adopter bootstrap template and gzkit's Layer-3 only, never gzkit's own Layer-1 corpus, which may make it ADR-0.35.0 work rather than a validator patch.
3. Rule GHI #924 and GHI #925 together. `_foreign_vendor_roots` derives from the declared vendor set; #924 changes that set and #925 fixes who honours it. Ruling them apart lets #924's removal hand #925 a fresh foreign root to leak into.
4. Take GHI #926 only after a posture ruling, exactly as GHI #878 [settled] needed one. Its detection strategy is undecided and the strategy determines the diff; the candidate grounds are named in its body and none is measured.
5. Hold the long-standing operator-held items: the design spike, whose premise no agent assertion can correct, and whether a delivery-cap breach on must-survive canon stays advisory (GHI #815).

## Pending Work / Open Loops

OPEN, and still the operator's headline concern: the control-surface family has no cohesive plan. Four of the original eleven are now closed, two children were filed, so the open family is GHI #924, #922, #921, #907, #836, #815, #873, #925, #926 — nine items. They remain individually evidenced and collectively unsequenced.

OPEN, filed this session: GHI #925 (the skill-mirror pass copies generated `CLAUDE.md` into `.agents/skills/**`, bypassing the `_foreign_vendor_roots` exclusion the nested writer honours) and GHI #926 (multi-event witness loops outside the corpus have no detection arm; carries the class remainder of its parent).

OPEN by deliberate disposition: GHI #873. Ruled as an operator-led Algebra 6 amendment. Nothing further is agent-workable on it; the next move is operator-initiated via the `gz-obpi-pipeline` skill or an ADR amendment ceremony.

OPEN, inherited and untouched this session: GHI #921 (`.gzkit/rules/**` uncorpused; its corpus half is booked to ADR-0.35.0 and corpus onboarding is held for operator discussion), GHI #815 (must-survive canon renders past the codex cap), plus GHI #907, #836, #922 and #924.

OPEN, unrouted spike residual, carried unchanged: nested projection shape doctrine. `.claude/rules/agents-md-map-doctrine.md` declares paths for AGENTS.md, CLAUDE.md and `.claude/rules/*.md` while `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` pins the rendered path to root AGENTS.md alone. Partly subsumed by GHI #922.

OPEN, unruled: whether commits should carry the harness-requested `Claude-Session:` trailer alongside the repo's `Task:` trailer. Surfaced to the operator this session; no ruling given, so repo convention stands.

STRUCK, DO NOT RE-INVESTIGATE. The `surface_content_types` compose blocker was measured false on both halves. The retained off-route codex rendition is a deliberately sealed record. `gz validate --brief-reconcile` exiting 0 on a Draft brief is correct by design.

PRE-EXISTING and untouched: `gz check` reports 696 unlinked specs as advisory drift, plus one unjustified code change.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expects `0 0`. Anything else means work landed after this document was written.

`git status --short` expects empty output.

`git log --oneline -1` expects `764bcef4` at authoring time.

`uv run gz obpi lock list` expects no active locks.

`uv run gz check` expects exit 0. Pipe it only with `set -o pipefail`, or capture to a file and echo the real exit; the verifier-pipe-gate hook refuses a bare pipe.

`uv run python -m unittest tests.content.test_corpus_model.TestEntryIdsAddressExactlyOneRow tests.content.test_corpus_store.TestDuplicateIdNeverReachesDisk` expects 6 tests OK — the covering set for the commit this session landed.

`uv run gz validate --corpus-retirement-witness` expects exit 0; it is the detection arm cited when closing the corpus witness gap.

`gh issue list --state open --limit 40` re-derives family membership rather than trusting the nine ids listed above.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` is where lifecycle and landed count are read, never from a figure transcribed in prose.

`uv run gz handoff rulings --search "corpus"` checks the settled corpus before re-arguing any ownership question.

## Evidence / Artifacts

Surfaces changed and committed this session:

- `src/gzkit/content/models/corpus.py` — Algebra 1 (IDENTITY) and the docstring recording why it is checked first
- `tests/content/test_corpus_model.py` — the model-side covering tests
- `tests/content/test_corpus_store.py` — the write-boundary covering test

Surfaces read and verified unchanged:

- `src/gzkit/commands/content/retire.py` — carries the drift advisory the closed guidance issue said it lacked
- `src/gzkit/governance/trust_audits/corpus_retirement_witness.py` — the detection arm
- `src/gzkit/commands/register.py` and `src/gzkit/commands/adr_demote.py` — the two unguarded witness loops routed to the new child issue
- `src/gzkit/rules/__init__.py` — the nested surface writer and its foreign-vendor-root exclusion
- `src/gzkit/sync_skills.py` — the mirror pass that bypasses that exclusion

Handoff chain and Layer-2 records:

- `.gzkit/handoffs/20260831T083104Z-control-surface-rationalization-uncoordinated-ghi-family.md` — the resumed predecessor
- `.gzkit/ledger.jsonl` — the `handoff_resume_decided` row booking this session's ruling
- `.gzkit/handoffs/rulings.jsonl` — the append-only settled-ruling store

## Settled Rulings

631 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
