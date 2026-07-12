# Plan: OBPI-0.33.0-06-airlock-doctrine-lawful

**OBPI:** OBPI-0.33.0-06-airlock-doctrine-lawful
**Parent ADR:** ADR-0.33.0-airlock-membrane
**Lane:** Heavy
**Kind of REQs:** STRUCTURAL-FENCE (REQ-01, REQ-02) + SUPPORT (REQ-03, REQ-04)

## Context

The one-way door of the airlock ADR. Promotes the two North Star docs from
Draft to BINDING doctrine, carries the §2 seam BODY-and-BOUNDARY widening in the
same promotion, asserts the doctrinal binding to the already-registered
`airlock-in-unaccounted-seam` floor claim (OBPI-02's landing keystone), and
discharges the campaign §8 gate. Ships NO runtime code and edits NO runtime
surface — the section-5 claim + its floor-wiring are owned by OBPI-02.

**One-way-door precondition — VERIFIED before planning:**
- OBPI-02 `Completed` (brief frontmatter + `**Status:** Completed`).
- `airlock-in-unaccounted-seam` registered at `src/gzkit/airlock/enter.py:210`
  and floor-wired (`_ep_airlock_unaccounted_seam`).
- `enforcement_claim_verified` ledger events `outcome:PASS` (2026-07-11).
- `uv run gz validate --qc-binding` → exit 0.
The live NC bites un-forced in production; the one-way door may open.

**Operator ruling (2026-07-12):** REQ-04 checks the Phase 3 HATCH campaign box
AND minimally updates the box narrative for coherence (a checked box must not
still read "stays unchecked until Validated"); the `/gz-adr-audit` Validated
receipt still follows at ADR closeout.

### Step 6a disclosures (plan-before-exploration)

- **Destination-in-mind:** A surgical documentation-promotion — status-line
  flips + one §2 definition-sentence widening + campaign box + a tripwire
  regression test. The brief is prescriptive; the destination is largely the
  brief's own Allowed Paths and Acceptance Criteria.
- **Rejected alternatives:** (a) minting a brand-new "Binding" status format by
  copying another doc's status shape — rejected; no clean precedent exists and
  REQ-01 only requires the "Draft North Star"/"Draft theory" strings gone plus a
  binding assertion. (b) Rewriting §2's edge table to add body-sense rows —
  rejected as scope creep; the table correctly describes the BOUNDARY (edge)
  sense, so only the definition sentence widens. (c) Literal box-flip vs
  coherent narrative — operator ratified coherent narrative.

## Files

- `docs/governance/work-phases-and-airlock.md` — promote `**Status:**` line
  (drop "Draft North Star", assert BINDING/lawful) AND widen the §2 line-27
  seam definition to BODY-and-BOUNDARY.
- `docs/governance/four-phases-of-work.md` — promote `**Status:**` line (drop
  "Draft theory", assert BINDING/lawful); no body change beyond status.
- `docs/governance/build-to-1.0-campaign-2026-06-30.md` — flip Phase 3 HATCH
  checkbox `- [ ]` → `- [x]` AND update the box narrative for coherence.
- `tests/test_airlock_doctrine_lawful.py` — **CREATE** the one-way-door
  regression guard.

## Steps

1. **RED** — author `tests/test_airlock_doctrine_lawful.py` with assertions
   derived from the Acceptance Criteria: (a) neither doc carries a
   "Draft North Star"/"Draft theory" status line; (b) the §2 "a seam is both a
   BODY" widening string is present in work-phases-and-airlock.md; (c) the
   Phase 3 HATCH campaign checkbox is checked. Watch each assertion fail on its
   own assertion (not import error) against the un-promoted docs.
2. **GREEN** — promote work-phases-and-airlock.md status line + widen §2.
3. **GREEN** — promote four-phases-of-work.md status line.
4. **GREEN** — flip the campaign Phase 3 HATCH checkbox + coherent narrative.
5. **REFACTOR** — confirm the regression test passes green; tidy.

## Verification

```
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --qc-binding
uv run -m unittest tests.test_airlock_doctrine_lawful -v
uv run mkdocs build --strict
```

## Notes

- STRUCTURAL-FENCE REQs (01, 02) prove via parent-ADR `## Boundary Invariants`
  #2/#4, audited at ADR closeout — NOT via a per-OBPI behavior test. The
  regression test is a tripwire guard, not the REQ's proof channel.
- SUPPORT REQs (03, 04) prove via ledger event + structural validator:
  REQ-03 → `qc-binding` exit 0 + `enforcement_claim_verified` citing the claim;
  REQ-04 → `validate --documents` exit 0 + `artifact_edited` citing the campaign.
- NEVER edit `src/gzkit/enforcement.py`, `src/gzkit/airlock/**`, the parent ADR,
  the mx door, or the permitted-entry door.
