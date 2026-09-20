# gzkit — Big-Picture Assessment: Correction to 2026-09-20

**Date:** 2026-09-20 · **Report:** third in the `big-picture` series
**Corrects:** `docs/reports/big-picture/2026-09-20.md`
**Evidence cutoff:** 2026-09-20, `main` at `0ea44b2ea`, working tree clean

> This is a linked correction, not a reassessment. The report it corrects is
> retained unchanged and remains the record of what was assessed and published.
> This report identifies what was wrong, what the evidence actually supports, and
> what still stands. It re-argues nothing else.

---

## What prompted it

The 2026-09-20 report's central finding was a class of four mechanisms described as
*"built, tested, registered, and structurally unable to do their job because nothing
populates their input."* Routing those findings to the tracker through `ghi-author`
required its Step 0 prior-art pre-flight, which searches authored OBPI briefs for the
surface. That search returned live briefs owning two of the four, and reading their
acceptance criteria showed one of the four is not a defect at all.

The pre-flight is the mechanism that caught this. It ran because filing required it,
not because the report invited re-examination.

---

## Correction 1 — rendition lineage is not a vacuous mechanism

**What the report said:**

> "**Rendition lineage.** The grading gate for control-surface provenance reports
> **0 of 22 sections owned, 0 of 19,872 bytes (0.0%)**, with 20 sections ungraded
> because the lineage artifact does not exist — and exits 0. … The gate is
> well-built. Its input is empty."

**What is true.** The measurement is correct. The characterisation is not.
`OBPI-0.35.0-06-validate-rendition-lineage` is `status: Completed`, and exiting 0 on
ungraded and unowned bytes is a declared, attested property of that OBPI rather than
a failure to fire:

> REQ-0.35.0-06-03 [behavior]: "Given a committed rendition in which an UNOWNED
> section carries arbitrary hand-authored prose, when the scope runs, then it exits 0
> and reports those bytes as **measured debt** — unowned text never fails the gate."

> REQ-0.35.0-06-08 [structural-fence]: "The fail-closed reach of
> `--rendition-lineage` is owned sections only, and no ADR-0.35.0 OBPI extends it
> over unowned bytes. **The gate's partial scope is a declared property of the whole
> decomposition** — OBPI-0.35.0-04 sets the scope, 05 supplies the comparison
> artifact, 07 consumes the result — so it is audited at ADR closeout, not
> per-OBPI."

The 0.0% is the measured-debt figure the gate was built to report. The report read a
designed, attested reporting behaviour as evidence of a mechanism that cannot fire.
That instance is removed from the class.

The validator's honesty, which the report credited, was the clue it misread: the gate
says plainly that counting those sections as owned *"would claim proof this gate does
not have."* That is a gate describing its own declared scope, not one apologising for
a gap.

## Correction 2 — the class was one shape too broad

**What the report said**, in its summary:

> "four mechanisms are built and unwired, and they share one signature: a declared
> parameter with a permissive default that nothing populates."

**What is true.** After removing rendition lineage, three findings remain, and they do
not share one signature. They are two distinct shapes, and conflating them was an
overreach:

| Shape | Instance | Evidence |
|---|---|---|
| **Unwired input** — the mechanism is invoked with an empty argument | Airlock | `parent_invariants` defaults to `()` and is passed by no caller in `src/`; `blast_radius` and `override` likewise; two sites compute reach as `lambda _node: []` |
| **Uninvoked mechanism** — the member is registered but the gate path never calls it | 51 of 99 validator scopes; 10 of 77 declared ledger event types | Bare `gz validate` runs 15 of 97 registry entries; the reachability and inertness chores measure the rest |

The permissive-default signature describes the airlock only. The two registry
findings have nothing wrong with their inputs — they are simply never called. The
repairs differ accordingly: one threads a value through call sites, the other
compares two populations at gate time.

## Correction 3 — the airlock repair is designed, briefed, and anticipated the trap

The report said `ADR-0.37.0` *"exists precisely for this"* and that *"nothing is
built."* Both remain true. What the report did not know, and what bears on how the
finding should be read, is how specifically the repair is already specified. Three
briefs own the surface, all `status: Draft`:

- `OBPI-0.37.0-01-parent-invariant-threading` — threads `parent_invariants` through
  **five** call sites, and its REQ notes the ADR's original text named only four,
  leaving `gz airlock in` reporting `pull: []`.
- `OBPI-0.37.0-02-airlock-seam-calibration` — replaces the accounting predicate.
- `OBPI-0.37.0-03-seam-accounting-predicate` — the only brief naming `blast_radius`,
  `override` and `reach_fn`.

REQ-0.37.0-02-02 states the trap this report's predecessor thought it had found first:

> "**The pair is the assertion.** A single non-emptiness check cannot distinguish a
> gate that bites from a constant that does not: the withdrawn inverse-reach D1 would
> have produced a non-empty seam-map on every entry and satisfied it."

The project identified the failure mode, designed against it, and wrote the
differential control into the acceptance criteria. The finding is therefore a
**delivery** observation, not a discovery: the specification is ahead of the build by
37 days. That is a materially different claim from the one the predecessor made, and
a less alarming one.

---

## What still stands

Unchanged and re-verified:

- **The airlock measurement.** 71 transits; all 53 `proceed` decisions on an empty
  seam-map, all 18 `hold`s non-empty; 29 exits, all `verdict: clean`. The membrane has
  never evaluated a populated map and chosen to proceed.
- **The registry findings.** 97 registered validator scopes against 15 reached by a
  bare run; 51 of 99 runnable flags ungated; 10 declared event types never fired.
  Filed 2026-09-20 as a class-level issue, left open with a blocker because the
  architectural-absence route its skill prescribes collides with the standing
  boundary against adding pool ADRs to the runtime track.
- **The positive findings.** Attestation engages maximally — the waiver branch was
  deleted, not defaulted. The hooks refused five commands during the predecessor's
  production and three more during this correction's.
- **Everything in the predecessor's description of what gzkit is and does.** No
  figure in its capability, architecture or condition sections is affected.

And the general claim survives the correction intact, in narrower form: **no gzkit
witness asks whether a mechanism ever fires on a non-empty input.** Three instances
support it rather than four, in two shapes rather than one.

---

## How the error happened

Worth recording, because it is the project's own named failure class arriving in a
report about that class.

The predecessor measured `--rendition-lineage` correctly and read its output without
reading the acceptance criteria of the OBPI that built it. A gate reporting 0.0%
coverage and exiting 0 is ambiguous between two states — a gate that cannot fire, and
a gate reporting declared debt exactly as specified — and the output alone does not
distinguish them. The brief does, in one sentence.

That is trust-chain poisoning in the shape `docs/governance/trust-doctrine.md`
defines: *"Each layer is individually correct. The composition is wrong because no
layer independently tests that its inputs are what it assumes."* The measurement was
right; the assumption about what it meant was never tested against the authority.

The predecessor's limitations section already warned that its four-mechanism list was
not exhaustive and that "vacuous" was a claim about input wiring. It did not warn that
an instance might be designed behaviour. That is the gap this correction closes.

---

## Evidence appendix

| Observation | Source |
|---|---|
| `OBPI-0.35.0-06` status `Completed`; REQ-03 and REQ-08 verbatim | `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-06-validate-rendition-lineage.md` |
| Six `ADR-0.37.0` briefs, all `status: Draft` | `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/` |
| REQ-0.37.0-01-01 (five call sites) and REQ-0.37.0-02-02 (the differential pair) | the briefs above |
| 97 registry scopes, 15 default / 82 explicit | `VALIDATOR_REGISTRY`, `src/gzkit/commands/validate_cmd.py` |
| Bare run reports 15 scopes | `uv run gz validate` |
| 51 of 99 ungated | `src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report` |
| 77 declared event types, 10 never fired | `src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report` |
| Airlock 53 proceed / 18 hold, emptiness cross-tabulated | `.gzkit/ledger.jsonl` |
| `AGENTS.md:189` — "`uv run gz check` runs every registered validator" | `AGENTS.md` |

### Material limitations

1. **This corrects three claims; it does not re-audit the predecessor.** Sections not
   named here were not re-examined, and their limitations still apply as published.
2. **The correction was prompted by a routing pre-flight, not by a review pass.** Had
   these findings not been filed, the error would have stood. That is a statement
   about how this error was caught, and it does not generalise to the other claims.
3. **No new measurement window.** Same tree, same cutoff, same day as the report it
   corrects.
