---
id: ADR-pool.rule-surface-aging-clock
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.rule-surface-aging-clock: Rule-Surface Aging Clock

## Status

Pool

## Intent

**Give `.gzkit/rules/**` a review clock. Today it has none, and the skill
surface has had one all along.**

The asymmetry is total. Skills carry `last_reviewed:` in frontmatter, a 90-day
staleness audit (`DEFAULT_MAX_REVIEW_AGE_DAYS = 90`,
`src/gzkit/skills_audit.py:18`), and a gate wiring that fail-closes the
mandatory control-surface sync (`src/gzkit/commands/gates.py:204`). Rules carry
none of the three: `RuleFrontmatter` (`src/gzkit/rules/__init__.py:501-513`) is
exactly `id`, `paths`, `description` under `extra="forbid"`. There is no field
to stamp, nothing to audit, and nothing to fail.

The exclusion is **deliberate and stated**. `.gzkit/rules/skill-surface-sync.md`
§ Non-negotiable rules #6 ends: *"Rules do not carry `last_reviewed:` (no schema
field) — this clause applies to skills only."* This ADR is the design home for
retiring that carve-out.

### Class of failure addressed

**Prose describing code that no longer exists, with no clock forcing a
re-read.**

The natural experiment is on the record. The same doctrine drift — ADR-0.0.24's
ARB receipt gate, which made bare commands emit no receipt — hit both surfaces.
The skill side caught it: `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
reconciled to *"bare (non-ARB) commands do not satisfy this requirement."* The
rule side did not: `.gzkit/rules/gate5-runbook-code-covenant.md` § Validation
bundle still prescribed a bare-command sequence that was **mechanically
unrunnable on the ADRs it governs**, and stayed that way for months until
`1ddb407d` repaired it. The only structural difference between the two surfaces
is that one ages and one does not.

The Pass A conflict-matrix re-run (2026-07-16,
`.gzkit/chores/control-surface-rule-conflicts/proofs/summary.md`) found 25 rows,
12 blocking, and nearly every one is this shape — `governance-core.md` carrying
the same staleness in different grammar and contradicting its own next bullet;
`chores.md` describing a sync direction the code inverts; `pythonic.md`
asserting size limits nothing enforces; `adr-audit.md` prescribing a Gate-5
sequence that exits 3; `task-discovery.md` presenting an optional trailer anchor
as mandatory, driving agents into a GHI-filing moratorium violation.

The rules are not wrong about *intent*. They are stale against *implementation*,
and nothing re-reads them when the code moves. This is the
T1-doctrine-with-no-T2-fail-close class (`AGENTS.md` § MAKE LLM STOCHASTIC VIBES
INERT, operative claim 3: *doctrine drift is invariant drift*).

### What is already landed, and why it is not this

`1ddb407d` landed `gz validate --rule-version-markers`, closing the
*declared-but-unenforced* half: `skill-surface-sync.md` #2 mandates the
`<!-- rule-version: X.Y.Z -->` marker, four rules shipped without one, and
nothing checked. All 25 canonical rules now carry an agreeing marker + block
quote, enforced in `gz check`.

**A version marker is not a clock.** It proves an editor bumped a number; it
cannot prove anyone re-read the rule against current code. Three of the four
markerless rules (`adr-audit.md`, `cli.md`, `pythonic.md`) were among the
worst-drifted — correlation worth noting — but adding markers does not, by
itself, make anyone look again.

### Correction to the three-tier framing (recorded here because two ADRs inherited it)

`ADR-pool.artifact-staleness-propagation` (ADR-0.0.52) § *Why foundation tier?*
justifies itself on a three-tier model: *"Invariant 1a (coupled-surface
coherence) holds at the file level; the `last_reviewed` ↔ skill-version coupling
holds at the rule level; the artifact-graph tier … is the missing third tier."*

`ADR-pool.skill-version-review-coupling` already caught that this premise is
false once — the coupling is doctrine-only, with no mechanical backstop, which
is that ADR's whole reason to exist.

**It is false twice over.** The field named as the rule-level witness does not
exist on rules at all; it governs *skills*. "Rule level" in ADR-0.0.52 means
"the level governed by rule #6 of `skill-surface-sync.md`" — and rule #6's own
final clause scopes itself to skills only. So ADR-0.0.52's middle tier names a
surface that has never had a mechanism, and both ADRs inherited the mislabel.

This ADR supplies the genuinely-missing rule-surface tier. Promoting it and
`ADR-pool.skill-version-review-coupling` together is what makes ADR-0.0.52's
three-tier framing true.

## Decision

Add a review clock to the canonical rule surface, on the parameters booked by
operator ruling on GHI #691 (2026-07-27).

### Booked parameters (operator-ruled; not to be re-adjudicated)

| Parameter | Ruling |
|---|---|
| Field | `last_reviewed: date` added to `RuleFrontmatter` |
| Window | **90 days**, inherited from the skill-side precedent (`DEFAULT_MAX_REVIEW_AGE_DAYS`) |
| Backfill | **Honest** — each rule stamped with its own last *substantive* review date, not a uniform stamp |
| Enforcement | **Advisory first**, flipped fail-closed once the stale set is cleared |

The operator's ruling names the reasoning for the backfill choice directly: a
uniform today's-date stamp across all 25 rules *"buys 90 days of silence on
rules that are stale right now."* Making several rules immediately stale is the
intended output, not a side effect — that count **is** the finding.

Declined at ruling time: uniform today's-date stamp with immediate gating;
attesting a re-read on edit instead of a clock (catches only rules someone
already chose to touch, which is the drift class least at risk); won't-fix.

### Design constraint discovered after the ruling: "substantive" needs a definition

The ruling says *last substantive commit date*. Implementing that as
`git log -1 -- <rule>` is **not honest, and would launder the very staleness the
backfill exists to expose.**

Observed 2026-08-04 against the live tree:

- `b89754166 chore(diet): lift rule version history; reclaim 97 lines of surface
  headroom` touched **9 canonical rules in one mechanical pass** —
  `adr-audit`, `chores`, `cli`, `gate5-runbook-code-covenant`, `gh-cli`,
  `governance-core`, `hexagonal-architecture`, `pythonic`, `task-discovery` —
  and only *deleted* version-history prose into a doc. No line was re-read
  against code.
- A naive last-commit backfill stamps all 9 fresh as of 2026-08-02, buying them
  the full 90 days.
- Those 9 include `pythonic.md`, `cli.md`, and `adr-audit.md` — three of the
  four rules GHI #691 names as *worst-drifted*.

Bulk mechanical passes are routine on this surface (`1ddb407d` reconcile,
`gz agent sync control-surfaces` propagation, diet passes). Any backfill or
ongoing stamp that treats "the file changed" as "someone reviewed it" reproduces
the marker-is-not-a-clock defect one layer up. **The promotion must define and
mechanize `substantive` — the design question this ADR carries forward, and the
one the GHI body could not have known, because the diet pass postdates it.**

Naive last-commit dates as observed (raw input to the backfill, **not** the
backfill itself): 3 rules in May 2026, 2 in June, 5 in July, 15 in August, and
the August cluster is dominated by exactly the bulk passes named above.

### Atomic-landing constraint

`RuleFrontmatter` is `frozen=True, extra="forbid"`. The field cannot land
incrementally: the first rule to carry `last_reviewed` makes the other 24 fail
to parse. All 25 canonical rules change in one landing, together with the
schema. This is what converts a ~10-line model edit into a
schema/runtime-contract change, and is why GHI #691 could not route to direct
fix.

(`.gzkit/rules/AGENTS.md` is a generated subtree-instructions file with no YAML
frontmatter and is **not** one of the 25 — it is out of scope for the field.)

### Routing facts carried forward to the promotion's plan/OBPI

- **Estimated diff:** ~100–150 lines, plus 25 frontmatter additions.
- **Surfaces touched:** `src/gzkit/rules/__init__.py` (`RuleFrontmatter`),
  `src/gzkit/validators/rule_version_markers.py` (extend, or add a sibling
  scope), `.gzkit/rules/*.md` (25 files, frontmatter add),
  `.gzkit/rules/skill-surface-sync.md` § #6 (retire the "skills only"
  carve-out), `AGENTS.md` § Mechanical scopes, `docs/governance/advisory-rules-audit.md`.
- **Lane:** heavy — schema contract change plus a `gz validate` scope wired into
  `gz check`.
- **Sequencing:** the advisory→fail-closed flip is a second landing, gated on
  the stale set reaching zero. Shipping the flip in the same OBPI would block
  day-one work on rules that are stale precisely because nobody had a reason to
  look.

## Alternatives Considered

1. **Fold into `ADR-pool.skill-version-review-coupling`.** Rejected: that ADR
   owns the *skill*-side, *edit-time* coupling (does a `skill-version` bump
   carry a `last_reviewed` bump). Its own § Notes already draws this boundary
   against the calendar class — *"#492 (this ADR) enforces the coupling at
   *edit* time; #503 is the symptom when no edit happens for 90 days. … Treat
   that as adjacent scope, not a blocker for this ADR."* Folding the rule-surface
   clock in would override that ADR's stated boundary and conflate two different
   triggers (commit-diff vs. calendar) on two different surfaces.

2. **Fold into `ADR-pool.artifact-staleness-propagation` (ADR-0.0.52).**
   Rejected: 0.0.52 owns the artifact-graph tier and *consumes* the rule tier as
   an assumed-true premise. An ADR cannot supply the premise it assumes. The
   correction to its three-tier framing is recorded above and should propagate
   to 0.0.52 at promotion, but the mechanism belongs here.

3. **Uniform today's-date backfill with immediate fail-closed gating.**
   Rejected at operator ruling: buys 90 days of silence on rules that are stale
   right now, and suppresses the count that is the actual finding.

4. **Attest a re-read at edit time instead of running a clock.** Rejected at
   operator ruling: catches only rules someone already chose to touch, which is
   the drift class *least* at risk. The dangerous rules are the ones nobody has
   opened since the code beneath them moved — precisely the population an
   edit-time trigger cannot see.

5. **Won't-fix — treat `--rule-version-markers` plus the Pass A/B/C/D chore
   sweep as sufficient aging pressure.** Rejected at operator ruling. A marker
   proves a number was bumped; a chore sweep is operator-initiated and
   unscheduled. Neither is a clock, and GHI #691's own body is the argument:
   the marker half landed and the drift class stayed open.

6. **Advisory forever (never flip fail-closed).** Rejected. GHI #737 documents
   what the far end of permanent-advisory looks like after ~14 months:
   `CorpusEntry.classification` shipped required and identity-fingerprinted with
   no consumer, and 36 of 52 corpus rows now sit at the capture default,
   undetectably. An aging clock landed advisory-only would be the same shape —
   which is why the ruling names the flip as a scheduled second step, not an
   open option.

## ADR Relationships

- **`ADR-pool.skill-version-review-coupling`** — sibling, not parent. That ADR
  mechanizes the skill-side edit-time coupling; this one adds the rule-side
  calendar clock. Both are needed to make ADR-0.0.52's three-tier framing true,
  and both edit the same bullet (`skill-surface-sync.md` § #6) from opposite
  directions — that ADR promotes its *coupling* clause, this one retires its
  *"skills only"* carve-out. **Coupled-surface coherence (Invariant 1a): whichever
  promotes second must reconcile against the first's edit to #6.**
- **`ADR-pool.artifact-staleness-propagation` (ADR-0.0.52)** — consumer of the
  tier this ADR supplies; carries the mislabel corrected above.
- **`docs/governance/advisory-rules-audit.md`** — the Promotable→Mechanical
  scorecard pattern this ADR instantiates; the promotion adds the new scope to
  the audit catalogue and to `AGENTS.md` § Mechanical scopes.
- **`1ddb407d`** — the already-landed marker half. Adjacent, not superseded:
  the marker invariant stays; the clock is additive.

## Notes

### Related GHIs (snapshot 2026-08-04 — re-check before promotion)

- **#691** — the originating issue; closed `superseded` against this ADR.
  Carries the operator ruling of 2026-07-27 verbatim.
- **#503** — the skill-side precedent for what the clock does when it fires: 10
  skills sharing `last_reviewed: 2026-02-18` all crossed the threshold on the
  same tick. The wave shape this ADR should expect at its own first fire.
- **#492** — the skill-side coupling, homed at
  `ADR-pool.skill-version-review-coupling`.
- **#669** — sibling cut, same root class: mechanical audit absent,
  convention-only enforcement.
- **#690** — permission-surface cut of the same class (closed; routed to the
  Pass D chore).
- **#693** — sibling cut: `gz cli audit` verifies a flag is *mentioned*, never
  that its description is *true*.
- **#727** — the class-level cut: the absent *record* of what each mechanism is
  for and how far it reaches.
- **#737** — inverse cut, and the load-bearing evidence for Alternative 6:
  a field that exists, is required, and has no reader.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
