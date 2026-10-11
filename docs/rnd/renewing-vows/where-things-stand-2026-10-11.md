# Where things stand — 2026-10-11

> A dated record, written for the operator on 2026-10-11 after the maintenance work of the R&D
> run `renewing-vows`. Figures are as measured that day; the command beside each gives the live
> value. This page advises and records. It authorizes nothing.

## The three layers

**1. The real work: gzkit 1.0.** The plan is
[`build-to-1.0-campaign-2026-09-20.md`](../../governance/build-to-1.0-campaign-2026-09-20.md).
The feature in flight is `ADR-0.35.0`, the system that builds `AGENTS.md` from recorded entries.
It stands at 10 of 20 work packages (`uv run gz adr status ADR-0.35.0`). The campaign's order
inside it is item 10, then 15 to 20, then 11 to 13. Item 10 has landed, so the next is item 15,
`OBPI-0.35.0-15-pipeline-run-position`. Item 9 was repudiated and holds the closeout until it
is completed again. The maintenance visits below did not touch this ADR.

**2. The detour: the R&D run `renewing-vows`.** Opened 2026-10-06; the record is
[`renewing-vows.md`](../renewing-vows.md). Its finding, in the words accepted on 2026-10-10:
"gzkit's canon disagrees with itself." Three acts of June 2026 (a freeze, a campaign, a command
doctrine) never named one another. The remedy was one merged doctrine. The run ended with six
outcome rows:

- **Row 4, the doctrine. Done 2026-10-10.** The canonical file is
  [`command-doctrine.md`](../../governance/GovZero/command-doctrine.md). With it: the campaign
  plan amended, the PRD repaired, the weaponeering rule landed, the model-selection rule
  corrected.
- **Row 3, maintenance. Done 2026-10-10.** The overdue chores were packaged into five visits
  ([`maintenance-visit-advice.md`](maintenance-visit-advice.md)) and all five were run.
- **Row 5, identifier renaming.** Parked as `ADR-pool.identifier-ladder-migration` until 1.0.
- **Row 1, future ADR work.** Proposed only, to follow items 15 to 20 of `ADR-0.35.0`.
- **Row 2, direct fixes.** Four stale-canon items repaired; the remainder is in the record.
- **Row 6.** Things ruled not to be built.

**3. The clean-up tail, 2026-10-10 and 2026-10-11.** The last visit ran four audits. One read
every skill against every rule and found 35 disagreements. A batch fix of ten was ordered on
2026-10-11; two of the ten needed a ruling because two written rules contradicted each other.
Both rulings are given. 27 of the 35 remain, listed in
`.gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md`.

## Decided on 2026-10-11

- **The skill sweep** (commit `04fda99d3`): ten skills corrected where a rule had moved and
  the skill had not.
- **Distillation** (commit `a87603775`): a recurring complexity distillation pass runs as an
  OBPI the operator initiates, so its attestation is a real Gate 5.
- **Release notes** (commit `bd8b7d902`): `gz-patch-release` owns the notes, the changelog and
  the publication of every release; the closeout ceremony hands over after the version bump.

## Open, and none of it blocks `ADR-0.35.0`

**Decisions waiting on the operator.** Numbers are the run record's.

- (1) and (10): the instruction-file diet. Five entries left `AGENTS.md` on 2026-10-10; what
  remains is whether eight scorecard rows may be re-attributed so the mechanical-scopes list
  can leave too.
- (2) archive 17 superseded pool entries; (3) the memory bands; (4) which dependency bumps to
  take; (5) the OpenAI-tier issue and the Sonnet and Haiku tier scope; (6) a re-read of
  GHI #969.
- (7) two failure families as campaign rows; (8) four evaluation proposals.
- (9) the route for GHI #1190.
- (11) whether the `gh` allowlist is exhaustive; (13) the settings patch; (14) whether writes
  made through the shell need a witness; (17) whether the parity scan's same-cycle tranche
  stands.
- Whether the Gate Covenant bullet restored on 2026-10-10 stays.

**Work only the operator starts.**

- A path in `gz patch release` for a version that is already bumped. Wanted before v0.35.0;
  until then the hand-over from closeout is done by hand.
- The row 1 ADR work, after items 15 to 20.

**Closed later the same day.** GHI #997, closed `fixed` on the operator's word. Verifying it
for closure found that its runner had never read the configured thresholds; that is repaired
in commit `ef5f82fdf`.

**Backlog.** The chore board reads 17 overdue, 11 due, 3 unmeasured and 9 current
(`uv run gz chores status`); it read 2 current and 35 overdue before the visits. 75 issues are
open (`gh issue list --state open`; 74 after GHI #997 closed), GHI #1185 among them from the session before the visits.

## Recommended next step

Stop taking maintenance rulings. In the next session, return to `ADR-0.35.0` at item 15, which
the operator initiates through `gz-obpi-pipeline`. The most recent authored handoff
(`.gzkit/handoffs/20261010T051502Z-scope-gate-and-airlock-exit-built-held-local.md`) predates
everything on this page; read this page and the last entries of the run record in its place.
