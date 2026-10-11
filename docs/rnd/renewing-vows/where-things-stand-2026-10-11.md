# Where things stand — 2026-10-11

> A dated record, written for the operator on 2026-10-11 after the maintenance work of the R&D
> run `renewing-vows`. Figures are as measured that day; the command beside each gives the live
> value. This page advises and records. It authorizes nothing. Updated the afternoon of
> 2026-10-11 for the `gz check` rebalance, which came after the page was first written.

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

- **Patch release** (commit `0efb147ec`): v0.34.9 was approved and published later the same
  day, with 19 issues closed and 3 partial landings.
- **The quality gate** (commits `701d01506`, `c7b643dfe` and `95dcf448d`; GHI #1191 and
  GHI #1192, both closed `fixed`): the operator found `gz check` too heavy for how often it
  runs. Plain `gz check` is now the per-change gate: lint, format, typecheck, every validator,
  the smoke tier and the tests the change touches. `gz check --full` adds the whole unit tier,
  `Behave`, the docs build, `Preflight` and the guard-canary sweep, and runs in CI on every
  code push, at every release and as the `quality-check` chore. The `--fast` flag is retired.
  The scope policy ships inside the package, so a project that installs gzkit runs the same
  per-change gate. This was a detour from the recommendation below, taken on the operator's
  word.

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

- (Done 2026-10-11 on the operator's word.) `gz patch release` now releases a version that
  is already bumped and does not bump it again, so the hand-over from closeout runs through
  the verb.
- The row 1 ADR work, after items 15 to 20.

**Closed later the same day.** GHI #997, closed `fixed` on the operator's word. Verifying it
for closure found that its runner had never read the configured thresholds; that is repaired
in commit `ef5f82fdf`.

**Left open by the `gz check` rebalance.** None has an issue of its own.

- A project gzkit scaffolds has no CI, so nothing runs its whole unit tier on push. Whether
  `gz init` should scaffold a CI workflow is the operator's call; it is recorded in the close
  comment of GHI #1192.
- The tests a change touches are selected by filename match. What that selects in a project
  whose tests are not named after its modules is unmeasured; also in the close comment of
  GHI #1192.
- The unit tier's remaining cost sits in subprocess-heavy governance tests. Recorded as an
  insight under scope "unit tier wall time".
- `ADR-0.39.0`'s Draft briefs still list the scope file among the `data/` settings to migrate;
  the file now lives at `src/gzkit/check_step_scopes.json`.
- Two unexplained multi-minute stalls on the developer host. Recorded as an insight under
  scope "developer host stalls".

**Backlog.** The chore board reads 17 overdue, 13 due, 3 unmeasured and 7 current
(`uv run gz chores status`), as read the afternoon of 2026-10-11. It read 17 overdue, 11 due
and 9 current that morning, and 2 current and 35 overdue before the visits. 73 issues are open
(by the search total, `gh api search/issues`): 75 that morning, 74 after GHI #997 closed,
unchanged by GHI #1191 and GHI #1192, which were filed and closed the same afternoon, and 73
after GHI #1187 closed. GHI #1185 is among them, from the session before the visits.

## Loose ends of the run `renewing-vows`

The run is signed off and its doctrine is ratified. These are what sits beneath or after it,
each with the door canon names for it. None blocks `ADR-0.35.0`. Issue states were read
2026-10-11; `gh issue view` gives the live value.

**Doctrine ratified and not yet connected.**

- (Done 2026-10-11 on the operator's word, "direct fix 1187".) Root `AGENTS.md` names the
  doctrine as the constitution again, under § Governance doctrine surfaces: one corpus entry,
  commit `6948212bb`, GHI #1187 closed `fixed`. The entry is invariant tier, so the floor gate
  holds it in every rendition. Not held: a later rewrite that retires it without recapturing
  it, which is how the pointer was lost on 2026-09-17; recorded as an insight.
- The policy layer is a draft. Parts II to IV of
  [`doctrine-merge.md`](doctrine-merge.md) hold 20 drafted policies and are not ratified. Four
  statements were put and not answered: what a policy is; the reading of the June pairs under
  the five terms; whether changing an article differs from changing a policy; what "encourage"
  consists of. Door: the operator's ratification on the record, as Part 0 entered.
- Eight policies have no witness: 4, 5, 7, 16, 17, 18, 19 and the slower beats of 15. The
  draft's question is whether to build each witness or state the policy as advisory. Door:
  the ruling first, then a pool ADR where a witness is to be built.
- The June worklist of six items is parked in `ADR-pool.command-doctrine-internalization`.
  Door: the campaign, which the operator sequences, then promotion. The record found no run
  of the coherence audit; it is now a task of the maintenance visit.
- The glossary has no home. It is held in `doctrine-merge.md` Part 0 until a DDD-discipline
  R&D run names one, and `docs/rnd/` holds no such run.
- Appendix A of the doctrine was not re-walked and reads Article 3's former title.
- The two slower tiers of the rhythm are advisory until their signals are built. The
  campaign plan's republish was announced as due on 2026-10-10.
- "Built with a released gzkit" (statement of command, line 7) has no witness. Door:
  `ADR-pool.release-governed-construction`, whose first deliverable is its own sizing.

**Proposed ADR work, parked.** Five pool ADRs wait on the operator's promotion:
`ADR-pool.sortie-layer-crew-split`, `ADR-pool.integrity-level-axis` (its bands provisional),
`ADR-pool.maintenance-record-entry` and `ADR-pool.release-governed-construction`, after items
15 to 20; `ADR-pool.identifier-ladder-migration`, at 1.0.

**Issues the run filed or carried, all open.** GHI #1186 (525 `@covers` tags, two routes for
the operator's pick); GHI #1188 (the GovZero directory, stale as a class); GHI #1189 (two
Draft briefs under `ADR-0.39.0` below the sensitivity floor; the brief edit is the
operator's); GHI #1190 (route unruled); GHI #969 (owed a re-read); GHI #1185, which closes at
the next real package completion.

**Maintenance tail.** The numbered rulings above; 27 of 35 skill-to-rule gaps; and the advice
in [`maintenance-visit-advice.md`](maintenance-visit-advice.md) to take fourteen per-flight
checks off the chore board, which was written and not applied. Insights with no go: 38 skill
manpages listing a `.github/skills` mirror; the chore-runner stall; shell-mediated writes
that the write hooks do not see; the bare `python3` rule. Reads the agent still owes: the
campaign amendments older than 2026-09-27, the body of `chore-class-system.md`, and five
outside texts the run cites unread.

## Recommended next step

Stop taking maintenance rulings. In the next session, return to `ADR-0.35.0` at item 15, which
the operator initiates through `gz-obpi-pipeline`. The recommendation is unchanged by the
afternoon's work. The most recent authored handoff is
`.gzkit/handoffs/20261011T172749Z-gz-check-rebalanced-light-gate-full-sweep.md`; it and this
page agree, and the handoff carries the `gz check` detail.
