---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T18:54:15Z'
agent: claude-code
session_id: 9e91d721-7d7e-4b94-84f6-7e166a51eb13
continues_from: .gzkit/handoffs/20260821T115954Z-post-mortem-844-847-mx-open.md
---

## Current State Summary

The 715 "unlinked specs" that `gz check` reports as an advisory were inventoried,
enriched with each REQ's declared kind tag (ADR-0.0.59) and its parent ADR's
lifecycle, and written to `docs/governance/uncovered-req-inventory-2026-08-22.md`.

The headline count is not the work. It conflates four populations with different
proof channels and different remedies:

| Population | Count | Gap? |
|---|---:|---|
| BEHAVIOR REQ on an attested-complete brief | 6 | YES, genuine coverage defect |
| BEHAVIOR REQ on an unlanded brief | 64 | No, work not built yet |
| STRUCTURAL-FENCE REQ | 1 | No, proves via parent-ADR Boundary Invariant |
| No kind tag (pre-ADR-0.0.59) | 644 | Undecidable from the tag |

The actionable set is 6 REQs, not 715 — two orders of magnitude smaller than the
advisory suggests. They are REQ-0.0.41-02-07, REQ-0.0.59-03-03, REQ-0.0.63-03-02,
REQ-0.0.63-03-04, REQ-0.0.63-06-01 and REQ-0.0.63-06-02.

Also landed this session and already pushed: commit 89f95120, which lifted
CANONICAL_STEP_COMMANDS off the verifier-pipe-gate hot path (table import 94,743us
to 652us; hook 135ms to 75ms). Full suite green at 8701 tests.

## Important Context

**Why the 715 figure misleads, and why that matters more than the number.**
Per ADR-0.0.59 each REQ declares exactly one of three kinds, and each kind has
exactly one proof channel: BEHAVIOR proves via an @covers test, SUPPORT via a
ledger event plus structural validator, STRUCTURAL-FENCE via a parent-ADR
Boundary Invariants entry. `gz drift` counts every REQ lacking a test, including
the two kinds whose proof channel is not a test. The advisory is therefore
measuring against the wrong authority for 645 of its 715 rows.

**644 REQs carry no kind tag at all.** They predate ADR-0.0.59 and live on 45
mostly-older ADRs (heaviest: ADR-0.18.0 at 81, ADR-0.1.0 at 53, ADR-0.16.0 at 30).
`uv run gz validate --req-kind-discipline` passes clean, so those REQs sit outside
its scope. Whether any is a real gap is a reading per REQ, not something the tag
can decide. Verified by direct read rather than inference: REQ-0.0.2-01-01 in
`docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/obpis/OBPI-0.0.2-01-cli-command-surface-inventory.md`
is authored Gherkin-style with no tag present.

**The 64 BEHAVIOR REQs on unlanded briefs are not drift.** ADR-0.35.0 (1/10),
ADR-0.36.0 (0/9) and ADR-0.37.0 (0/6) are lifecycle Pending. Their tests are
unwritten because the work is unbuilt; they resolve as each OBPI lands through
the gz-obpi-pipeline skill. Counting them as coverage debt double-counts the
backlog.

**The 6 real defects sit on Validated, fully-attested ADRs** — ADR-0.0.41 (4/4),
ADR-0.0.59 (5/5) and ADR-0.0.63 (7/7), all heavy lane. Gate 5 was recorded on
those briefs while a BEHAVIOR REQ's only proof channel was absent. That is the
shape worth a repair route.

**Beware the inverse trap.** ADR-0.0.63 holds four of the six, and it is the ADR
that authored the REQ-evidence-schema and proof-binding machinery. A gap there is
more interesting than a gap elsewhere, not less.

**The inventory is Layer-3.** It is a dated measurement, never an authority.
Regenerate it with `uv run gz drift --json` and re-read lifecycle with
`uv run gz adr status` per ADR rather than trusting its transcribed counts.

## Decisions Made

- [operator-ruled] Place the uncovered REQs into a fresh handoff (verbatim: "place the uncovered REQs into a fresh handoff").
- [operator-ruled] Do not build the hook import-budget check (verbatim: "skip it"). The advisory-scorecard freeze holds: the imbalance to correct is too much mechanism, not too little, and the one observed instance is already witnessed by a per-instance test.
- [agent-chose] Enriched the flat 715 with each REQ's kind tag and parent-ADR lifecycle before inventorying, rather than transcribing the raw list. A flat dump would have carried the advisory's own conflation forward into the handoff.
- [agent-chose] Wrote the full 715-row table to a report artifact and referenced it from here rather than inlining it. GHI #838 records a handoff reaching 91.4% carried corpus; a 715-row table in a handoff body is that same failure mode.
- [agent-chose] Did not file a GHI for the 6 defects. Routing is the operator's call, and per operator canon a GHI is itself a work order, so filing one would pre-empt a decision that has not been made.

## Immediate Next Steps

1. Read section 1 of `docs/governance/uncovered-req-inventory-2026-08-22.md` and decide the route for the 6 genuine defects. Per AGENTS.md operator doctrine the intent test applies: a BEHAVIOR REQ attested without its only proof channel is a correction under the owning ADR, never an enhancement and never a fresh pool ADR.
2. Decide whether the 4 defects on ADR-0.0.63 are one repair or four. They cluster on OBPI-03 (two) and OBPI-06 (two), which suggests two brief-scoped repairs rather than four REQ-scoped ones.
3. Rule on whether the 644 untagged REQs are in scope at all. They fall outside `gz validate --req-kind-discipline`, which passes clean, so leaving them untagged is a defensible steady state; back-tagging 644 REQs across 45 ADRs is a large sweep for uncertain mechanical gain.
4. Consider whether `gz drift` should report by REQ kind rather than as a flat count. It currently overstates the real gap by roughly 100x, which is the kind of false signal that trains an operator to ignore an advisory.
5. Resume ADR-0.35.0-canon-entry-corpus-landing, which remains the work by ascending-semver ADR order. Read its live landed count with `uv run gz adr status` rather than trusting any figure written here.

## Pending Work / Open Loops

- **The 6 genuine coverage defects are unrouted.** No GHI filed and no repair started. They are listed in section 1 of the inventory report.
- **`gz check` runtime is unaddressed.** Measured at 3m29s across 56 serial validators, and the OBPI pipeline calls verification twice per brief. This is the dominant contributor to the session-cost complaint that opened this session and nothing was done about it. A `gz smoke` tier exists but the attestation path still calls full `gz check`.
- **Two hook import chains remain heavy**, both measured and both left alone deliberately: gzkit.mx.awareness at 48ms on every user prompt, and gzkit.pipeline_runtime at 74ms on ExitPlanMode. Neither is a constant-move; both need real restructuring.
- **`src/gzkit/arb/__init__.py` imports eagerly.** Any gzkit.arb submodule import pulls the whole validator chain. Making it lazy would help every consumer, not only the one path repaired this session. Not attempted.
- **GHI #847 [settled] remains open** — four sibling hooks still key on tool_input file_path and are bypassed by Bash writes. The ledger-writer hook is the consequential one.
- **Uncommitted at handoff time**: `.gzkit/ledger.jsonl`, `.claude/plans/.plan-audit-receipt-OBPI-0.26.0-12-docs-lib.json`, and two hook-generated session-exit bookmarks under the handoffs directory.

## Verification Checklist

Re-derive the inventory rather than trusting its transcribed counts. Expect the
four-way split 6 / 64 / 1 / 644 at scan time, and expect the flat total to have
grown if new briefs landed since:

```bash
uv run gz drift --json
```

Confirm the kind-discipline validator still passes, which is what places the 644
untagged REQs outside its scope:

```bash
uv run gz validate --req-kind-discipline
```

Confirm the three ADRs holding the genuine defects are still Validated and fully
attested. Expect ADR-0.0.41 at 4/4, ADR-0.0.59 at 5/5, ADR-0.0.63 at 7/7:

```bash
uv run gz adr status ADR-0.0.63
```

Confirm this session's landed commit is present and pushed:

```bash
git log -1 --format=%h 89f95120
```

Re-run the suite before and after touching any REQ coverage. Expect 8701 passing:

```bash
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Evidence / Artifacts

- `docs/governance/uncovered-req-inventory-2026-08-22.md` — the full 715-row inventory, enriched with REQ kind and parent-ADR lifecycle; sections 1 through 3 carry the four-way decomposition.
- `src/gzkit/canonical_steps.py` — new leaf module created this session; holds CANONICAL_STEP_COMMANDS off the hook hot path.
- `tests/arb/test_canonical_steps_leaf_import.py` — pins the leaf import against regrowth and asserts every consumer holds the same object.
- `docs/governance/req-scope-discipline.md` — the canonical expansion for REQ kinds and their proof channels; the authority the inventory's classification reads against.
- Commit 89f95120 — "fix(arb): lift CANONICAL_STEP_COMMANDS off the hook hot path", pushed to origin/main.
- ARB receipt arb-step-unittest-0b4b465a9d624ea5856f637192bbcb49 — 8701 tests, exit_status 0, 145.307s.

## Settled Rulings

474 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
