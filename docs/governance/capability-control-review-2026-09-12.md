# Capability and control review — 2026-09-12 UTC

> **Re-cut 2026-09-12, operator-directed.** The first cut of this record was
> authored by a Codex session on 2026-09-11 at 19:14 local from a pasted excerpt
> of the operator's voice conversation. The excerpt began after the four
> constructs had been named, so the first cut substituted five agent-derived
> hypotheses and declared their lineage internal. Codex disclosed the gap at the
> time — *"the four concerns are referenced but never identified. I wouldn't
> reconstruct them from inference"* — and proceeded anyway. The operator supplied
> the full transcript on 2026-09-12 and ruled, verbatim, spelling preserved:
> *"I am interested in the four contructs and not the watered down/confused
> version. let's get it straight."* The five-hypothesis table is retired. The
> first cut survives in git history at `e310ae292`. The course-correction is
> recorded in `.gzkit/insights/agent-insights.jsonl` (2026-09-12T14:20:32Z,
> `improvement`, scope this file).

## The four constructs

Operator, voice conversation 2026-09-11, verbatim: *"Pull the four as-is. Keep
them bare deliverables."*

| Construct | Concept behind it, as stated | Sources named in the conversation |
|---|---|---|
| **Change point** | seams and safe change | Michael Feathers, *Working Effectively with Legacy Code*; Martin Fowler's refactoring work; Hunt and Thomas, *The Pragmatic Programmer* (tracer bullets) |
| **Jurisdiction** | information hiding and least privilege | David Parnas, "On the Criteria to be Used in Decomposing Systems into Modules" (1972); least privilege and capability-based security; Eric Evans, *Domain-Driven Design* (bounded contexts); Matthew Skelton and Manuel Pais, *Team Topologies* (cognitive load, ownership boundaries) |
| **Invariant** | design by contract | Bertrand Meyer, *Object-Oriented Software Construction* |
| **Escalation** | change-impact analysis and controlled handoffs | Robert Arnold and Shawn Bohner, *Software Change Impact Analysis* |

The four were reduced from six bodies of work the conversation listed:
modularity and information hiding plus DDD bounded contexts; change impact
analysis; design by contract and invariants; least privilege and
capability-based security; Feathers' seams and safe change; cognitive load and
ownership boundaries. Parnas sits inside a modularity constellation the
conversation also named — Dijkstra (separation of concerns), Wirth (stepwise
refinement), Myers and Constantine (cohesion and coupling), Brooks (conceptual
integrity) — and the conversation warned against forcing a new agentic control
problem into a 1970s module frame: mix in control theory, safety engineering
and socio-technical systems to test whether the old frames still hold. Peter
Naur, "Programming as Theory Building", frames the whole: the operator holds the
intentional theory of gzkit; the implementation theory is distributed across
thousands of agent decisions and is partially reconstructed each session.

### Rulings from the conversation that bind this review

- *"How small does its jurisdiction have to become, as the system ages?"* Task
  size and jurisdiction are not the same thing; a tiny task can carry a large
  blast radius. The missing boundary sits below the existing hierarchy:
  **OBPI → requirement → task → authorized change surface.**
- Jurisdiction applies to ADRs, validators, workflows, rules and prompts, not
  only code. Operator: *"Why do the answers keep pouring into straight
  code-oriented thinking?"*
- The invariant is coherence across artifacts. Operator: *"we do make sure that
  they continue to align and resonate."* When ADRs, validators, workflows and
  code do not tell the same story, that is an escalation, not a clever fix.
- Jurisdiction constrains mutation, not understanding: read broadly, write
  narrowly.
- *"Don't add mechanisms first."* Operator: *"maybe not make anything new, but
  see how we can beef up what we have."*
- Per construct, one skeleton: **concern, governing question, intellectual
  lineage, current gzkit mechanisms, evidence to inspect, failure signatures,
  boundaries.**
- The pass: **inventory → map evidence to lenses → mark gaps and overlaps → test
  against failure patterns → decide.**
- Cross-cutting question, asked every time: *"Is this explicit enough that a
  fresh agent can reconstruct it without relying on tacit memory?"*
- Per construct, five checks: **health, opportunity, strategic fit, tactical
  tweak, retirement** — *"Has something outlived its assumptions?"* No reflex to
  add; see what to strengthen or retire.

## Purpose and authority

A diagnostic record and a reusable reading framework. Not a campaign amendment,
not a new requirement, not initiation of OBPI work. The governing campaign is
identified by [`data/active_campaign.json`](../../data/active_campaign.json);
nothing here changes its work order. Under the IRON LAW only the operator
initiates OBPI work; observed failures route as GHI-shaped direct repair or
governed insights, per [`AGENTS.md`](../../AGENTS.md) § Operator Doctrine.

## Evidence standard

- Read the intended guarantee before judging the implementation.
- Distinguish an affordance's existence, observed invocation, and effectiveness.
- Current command output is a working-tree observation at a named commit;
  historical evaluations are dated records; handoff narrative is a claim to
  corroborate.
- Require evidence of degraded steering before proposing retirement. A low use
  count or a large governance surface is not sufficient.
- Preserve useful detection: discovering a real contract contradiction is work
  that establishes correctness. Repeating a review because its input changed is
  a different cost category.

These follow [trust doctrine](trust-doctrine.md), [state
doctrine](state-doctrine.md), and the subtraction bar in [the advisory
scorecard](advisory-rules-audit.md#recommended-promotion-order-highest-leverage-first).
Every figure below is dated and commit-anchored; it is a record, never an
authority (`.claude/rules/governance-core.md`, first non-negotiable rule).

---

## Lens 1 — Change point

**Concern.** Where behavior may legitimately change: the narrowest seam. A
tracer bullet with guardrails is a thin vertical behavior plus an exact change
surface.

**Governing question.** For this change, what is the seam, and can the change
be fully localized behind the existing contract? If not, that is an escalation
trigger.

**Intellectual lineage.** Feathers (seams, safe change); Fowler (refactoring);
Hunt and Thomas (tracer bullets).

**Current gzkit mechanisms** (verified 2026-09-12 at `b33a18ea1`):

- The airlock membrane, [ADR-0.33.0](../design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md):
  `gz airlock in` runs DECLARE → PING → RECONCILE → decide over a seam-map;
  `gz airlock out` accounts the drift a transit disturbed. Its own `--help`
  states the posture: diagnostic-only, a NO-GO prints a refusal and exits 0,
  because *"production reach yields an empty seam-map, so a fail-closed gate
  would be vacuous."* Calibration is re-homed at
  [ADR-0.37.0](../design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md).
- `gz ontology reach` (downstream blast-radius) and `gz ontology trace`
  (lineage) — the impact instruments the seam-map reads from.
- REQ-level proof specs and mutation controls: `gz arb red`, the replayable
  specs under `.gzkit/evidence/<obpi>/proof-specs/`, and the acceptance store's
  input digest, which defines the bytes whose change re-opens every proof.
- Coupled-surface coherence, [`AGENTS.md`](../../AGENTS.md) § DO IT RIGHT 1a:
  when a change touches a surface another surface reads or validates, verify the
  consumer in the same commit.

**Evidence inspected.**

- Ledger, 61 `airlock_in` rows to date: 43 `proceed`, every one with an empty
  unaccounted list; 18 `hold`, every one with unaccounted seams. The gate has
  never issued `proceed` on a computed non-empty seam-map. This matches the
  campaign's 2026-08-14 measurement (20 of 23 transits empty) one month on.
- Acceptance store, OBPI-0.35.0-05 and -06 (ledger, 2026-09-12): 84 and 104
  `acceptance_recorded` rows, 74 and 83 of them proofs, across 32 and 91
  distinct digest values, against 27 and 5 tier-1 adversary receipts. Detection
  fell while re-proving rose. The OBPI-06 completion handoff names the mechanism:
  *"every production or normative-section edit moves the acceptance input digest
  and supersedes all closures"* — five times in one brief.
- OBPI-0.35.0-06 Step 4b: one new finding was a regression introduced by the
  brief's own prior repair (a repair at one seam broke its neighbor).

**Failure signatures.** An empty seam-map that auto-proceeds (theater, ADR-0.33.0
§ Negative #1). A digest whose seam is wider than the behavior seam, so a Change
Log edit is treated as a behavior change (the digest treadmill). A repair that
patches a surfacing rather than a design and introduces the next finding.

**Boundaries.** A zero-seam readout proves only what the current instrument
observed. This lens says where change is legitimate, not who may make it (Lens 2)
or what must survive it (Lens 3).

**Cross-cutting.** The airlock's diagnostic posture is explicit in its `--help`.
What moves the acceptance digest is not written anywhere a fresh agent would
read first; the OBPI-06 session learned it by paying for it. Gap.

| Check | Reading, 2026-09-12 |
|---|---|
| Health | The membrane bites on hold (18 holds) but has never proceeded on evidence; disclosed, not hidden. |
| Opportunity | Narrow the acceptance digest's seam so normative-text edits that change no proven behavior do not supersede closures. Design question, operator's to rule. |
| Strategic fit | Calibration is already sequenced: campaign box 0 and ADR-0.37.0, worked in ascending semver order after ADR-0.35.0 and ADR-0.36.0. |
| Tactical tweak | Write down what moves the digest, where a fresh agent reads before Stage 2. |
| Retirement | None. The seam-map's inverse-`reach` form was already withdrawn on measurement (ADR-0.37.0, 2026-08-15); the control stands. |

---

## Lens 2 — Jurisdiction

**Concern.** Which design decisions and artifacts the agent may disturb. Parnas'
move: modules hide decisions, not code, so jurisdiction is the set of decisions
an agent is allowed to disturb, and the question is not *how many files did it
touch* but *did it cross an information-hiding boundary*.

**Governing question.** Which decisions or artifacts is the agent allowed to
change, and what must remain invariant? Can this change be fully localized
behind the existing contract?

**Intellectual lineage.** Parnas 1972; least privilege and capability-based
security; Evans (bounded contexts); Skelton and Pais (cognitive load, ownership
boundaries); the modularity constellation.

**Current gzkit mechanisms** (verified 2026-09-12 at `b33a18ea1`).

Over code:

- OBPI brief `allowlist:` frontmatter plus `## Allowed Paths` / `## Denied
  Paths` ([`src/gzkit/templates/obpi.md`](../../src/gzkit/templates/obpi.md));
  31 briefs under ADR-0.3x carry an allowlist. The 2026-09-05 ADR-0.35.0
  substance evaluation notes the structural scorer counts allowed paths as a
  size heuristic; that counts files, not decisions.
- [`.claude/hooks/pipeline-gate.py`](../../.claude/hooks/pipeline-gate.py)
  refuses writes under `src/` and `tests/` once the pipeline marker's stage is
  past `implement`. `PreToolUse` matchers: `ExitPlanMode`, `Bash`,
  `Write|Edit|NotebookEdit`.
- Reviewer tool grants: `spec-reviewer` and `quality-reviewer` hold `Read,
  Glob, Grep`; `implementer` adds `Edit, Write, Bash`. The tier-1 adversary runs
  in a disposable checkout.
- `gz obpi lock` (one agent per brief), the TASK envelope, and the security
  sensitivity registry (`gz validate --sensitivity`).

Over canon, the surface the conversation said the answers kept missing:

- Root `AGENTS.md` is a rendition of the corpus; editing the delivered file
  bypasses the ownership chain. Section ownership lives in
  [`.gzkit/ownership/AGENTS.md.json`](../../.gzkit/ownership/AGENTS.md.json)
  with attested `gz content own` / `gz content unown` transitions;
  `gz validate --invariant-coherence` byte-compares the rendered surface
  against the registry.
- Rules are path-scoped: 25 of 27 files under `.gzkit/rules/` carry `paths:`
  frontmatter, and `gz validate --unscoped-rules` refuses an unscoped rule in
  a vendor surface (ADR-0.0.20).
- Jurisdiction over initiation and completion is human: the IRON LAW (only the
  operator initiates OBPI work) and Gate 5 (only a human attests). Both are
  advisory in the scorecard's sense: no mechanical witness distinguishes
  operator-initiated from agent-initiated work today.

**Evidence inspected.**

- OBPI-0.35.0-06 needed three allowlist amendments to connect one gate to its
  coupled quality surfaces (2026-09-11 checkpoint): jurisdiction discovered
  during implementation, not declared before it.
- GHI #968: *"read-only" is enforced as "no Bash", and no surface expresses the
  difference.* GHI #994: a non-executing reviewer recorded a confirmation its
  grant could not have produced.
- GHI #983: 10 of 12 sections the live declaration marks `corpus-owned` carry
  no covering corpus content. Ownership is claimed at the transition and never
  re-checked at rest; a generator that trusts the claim would drop content.
- [`AGENTS.md`](../../AGENTS.md), measured 2026-08-21: a pipeline marker left by
  an earlier session armed the pipeline and licensed roughly 350 lines of
  production code with no implementer dispatch and no review. Measured
  2026-08-23: told to bind `@covers` decorators, an agent escalated into a full
  pipeline run nobody asked for.

**Failure signatures.** Jurisdiction over code enforced while jurisdiction over
canon is prose. An allowlist widened in flight. A presence check read as a
grant. A tool grant narrower than its description, or a reviewer asserting past
its grant.

**Boundaries.** Read broadly, write narrowly: jurisdiction must not restrict
understanding. The allowlist's unit is a path; Parnas' unit is a decision. The
lens's true unit is unmodelled in gzkit today, and this record does not propose
modelling it.

**Cross-cutting.** Code-side jurisdiction is explicit and mechanical. Canon-side
jurisdiction is explicit in `AGENTS.md` prose and mechanical only for the
corpus-owned sections and scoped rules. A fresh agent can reconstruct the
former from hooks; it reconstructs the latter only by reading doctrine.

| Check | Reading, 2026-09-12 |
|---|---|
| Health | Code-side: healthy and fail-closed. Canon-side: declared, partially witnessed, and the two measured breaches (2026-08-21, 2026-08-23) were both canon-side. |
| Opportunity | The ownership declaration and scoped rules already model canon jurisdiction; #983's missing state check is the gap, not a new mechanism. |
| Strategic fit | ADR-0.35.0, campaign TOPMOST, is canon jurisdiction: corpus → rendition ownership with a lineage gate. |
| Tactical tweak | #968 (say what read-only means); #983 (apply the coverage predicate at load, disposition of the 10 sections operator-ruled). |
| Retirement | None. The path-allowlist is the candidate to refine toward decisions, not to retire. |

---

## Lens 3 — Invariant

**Concern.** What must hold before, during and after a change: preconditions,
postconditions, architectural invariants, and coherence across artifacts. The
invariant is not *tests pass*; it is that ADRs, validators, workflows, rules
and code tell the same story.

**Governing question.** Which contracts must this change preserve, which
observable behaviors may it change, and does every artifact that states the
contract still agree after the change?

**Intellectual lineage.** Meyer (design by contract); Brooks (conceptual
integrity); Naur (the theory the artifacts must carry when no one holds it).

**Current gzkit mechanisms** (verified 2026-09-12 at `b33a18ea1`):

- `## Boundary Invariants` in 19 ADRs; REQ kinds with one proof channel each,
  BEHAVIOR → `@covers` test, SUPPORT → ledger event plus structural validator,
  STRUCTURAL-FENCE → parent-ADR boundary invariant (`gz validate
  --req-kind-discipline`, ADR-0.0.59).
- The `@enforces` registry (25 files) and `NC:` claim ids; `gz arb red` as the
  mutation witness that a test can fail.
- 98 runnable `gz validate` scopes at the reachability chore's census, 47 of
  them gated (tier A) and 51 reachable from no `gz check` step, hook, CI
  workflow or pre-commit entry. Coherence scopes among them:
  `--invariant-coherence`, `--rendition-floor-coherence`,
  `--rendition-lineage`, `--adr-status-fresh`, `--distribution`,
  `--advisory-scorecard`.
- The advisory scorecard itself, [`advisory-rules-audit.md`](advisory-rules-audit.md):
  68 Mechanical, 31 Promotable, 64 Judgment, 0 Ambiguous at this reading; its
  completion criterion is *a declared discipline either carries a mechanical
  witness or is demoted to advisory in its own text, no third state.*
- `gz obpi precomplete` (Stage 5 preconditions), the acceptance store's
  contract / proof / review records, Pydantic models at every boundary, and the
  three-layer state doctrine (Layer-3 views never source of truth).

**Evidence inspected.**

- The doctrine-declared-without-mechanism family: 19 of 32 open GHIs on
  2026-09-02 by the campaign's own body-reading count; the open queue stands at
  43 on 2026-09-12. Promotable rows rose 30 → 31 in the same window.
- `gz validate --evaluation-justify-binding` fails at HEAD on three artifact
  ids, all for a low Feature Checklist score. The scorer
  ([`src/gzkit/adr_eval_scoring.py`](../../src/gzkit/adr_eval_scoring.py))
  awards one point each for items existing, every item starting with `OBPI-`,
  the count matching the brief count, and word-count consistency. ADR-0.35.0
  finds all 13 items and the count matches; it scores 1 of 4 because the ADR
  template prescribes no prefix and its items vary in length. Across the ledger,
  41 of 54 evaluated ADRs score 4.0 on this dimension, and in 4 of the 7 ADRs
  that trigger the justify gate at all, this heuristic is the trigger. The same
  ADR is evaluated under two ids (`ADR-0.35.0` and its full slug), so it carries
  two obligations. Same class as GHI #631.
- GHI #995: `gz validate --json` exits 0 on a failing scope, repo-wide, since
  `b27f42c92`. The exit-code invariant `.gzkit/rules/tests.md` binds is
  bypassed in the shared renderer.
- Ledger vocabulary: 76 declared event types, 66 fired, 10 never fired
  (`blocked_by`, `blocks`, `constitution_created`, `discovered_from`,
  `intrinsic-complexity-attestation`, `ledger_event_corrected`,
  `obpi_superseded`, `section_ownership_unowned`, `task_escalated`,
  `validates`).
- The reachability scanner labels `--doc-surface-parity` an orphan; it is
  dispatched from `AUDITS_AGGREGATE_MEMBERS` in
  [`validate_audits.py`](../../src/gzkit/commands/validate_audits.py) and passed
  in the live umbrella run. The scanner's textual caller search does not model
  Python dispatch and does not say so.

**Failure signatures.** A presence check standing in for a procedure (*is
something armed* versus *did it run*). A witness whose subject is narrower than
its name. A declared mechanism that never fires. A validator that runs on no
commit path and reads as coverage.

**Boundaries.** A Mechanical score on a decision authority does not cover the
inventory of its callers (scorecard row 62). A value in a Markdown document is
illustrative; the authority is the JSON or code it names.

**Cross-cutting.** The strongest arm of the four for explicitness: the scorecard
is self-tested and the family has a name, a criterion and a campaign box. A
fresh agent can reconstruct the invariant posture from `AGENTS.md` and the
scorecard alone.

| Check | Reading, 2026-09-12 |
|---|---|
| Health | The most mechanized lens and the one carrying the most open defects; both are true and the second is the first working. |
| Opportunity | Drain the 51 ungated scopes through the reachability ratchet; repair the justify scorer so the gate fires on substance. |
| Strategic fit | The campaign's NEXT-IN-PRIORITY box (close the family) is this lens; drawable without the operator. |
| Tactical tweak | GHI for the Feature Checklist false-RED and the duplicate evaluation id; #995's `return` → exit classification; disclose the scanner's umbrella blind spot. |
| Retirement | Promotable rows either get a witness or are demoted in their own text; that demotion is the sanctioned retirement path, and it is operator-ruled per row. |

---

## Lens 4 — Escalation

**Concern.** Stop with an impact argument when authorization is not enough, and
hand off under control. The conversation's form: *"I was authorized here;
here's why that isn't enough; here's the dependency and likely surface."*

**Governing question.** When a task requires crossing its authorized surface,
does the agent stop and report the dependency, and does the report land where
the next session and the operator will find it?

**Intellectual lineage.** Arnold and Bohner (change impact analysis);
controlled handoffs; the airlock as the point that turns *just keep going* into
*pause here and make the boundary explicit.*

**Current gzkit mechanisms** (verified 2026-09-12 at `b33a18ea1`):

- Airlock `hold` (18 of 61 transits) and `gz airlock out` drift accounting (19
  rows, each carrying `drift`, `routing`, `verdict`).
- Brief template: `STOP-on-BLOCKERS` and *"Prerequisites (check existence,
  STOP if missing)"*; the § Decision-quote STOP before Allowed Paths.
- `gz task block` and `gz task escalate` with `task_blocked` (18 rows to date)
  and `task_escalated` (never fired); `gz obpi block` / `gz obpi unblock` with
  `obpi_blocked_on_operator` (GHI #887, landed `847f21f6`).
- The pipeline skill's design-escalation rule: two rounds naming the same root
  at different surfaces stop dispatching and send the scope question to the
  operator.
- Behavior Rules Always #9 (on inconsistencies STOP, name the confusion, wait),
  #7 and #18; the GHI as escalation record (*"the GHI is the work order and the
  receipt"*); the handoff system with `gz handoff decide` booking the operator's
  transit ruling.

**Evidence inspected.**

- OBPI-0.35.0-06: the design-escalation rule fired after rounds 1 and 2 named
  the same root; dispatching stopped; the operator ruled the boundary and routed
  the shared-CLI defect out to GHI #995. Escalation worked and left a record.
- The same brief: three legitimate reviewer judgments were refused at import
  because the closure rule at
  [`src/gzkit/acceptance.py`](../../src/gzkit/acceptance.py) (`_closure_retains_subject`)
  cannot express *old finding repaired, new finding found on the same
  obligation*, nor a raised-then-repaired finding recorded retroactively. An
  escalation the record cannot hold. GHI #985 closed 2026-09-09 with seven
  acceptance cases; none covers these two.
- `task_escalated` has a model, a CLI verb and a consumer, and zero rows in the
  ledger. Escalation happens through prose, handoffs and GHIs, not the declared
  event.
- [`AGENTS.md`](../../AGENTS.md), 2026-08-21: a harness instruction conflicted
  with a skill-mandated gate and the agent resolved it silently against the
  skill. GHI #994: a reviewer's inability to execute belonged in
  `verification_gaps` and was asserted as a confirmation instead.
- Handoff transport (kept from the first cut): the session-handoff skill records
  copied rulings once occupying 91.4% of a handoff before transport moved to a
  persistent store and pointer, and
  [`handoff_validation.py`](../../src/gzkit/handoff_validation.py) guards
  attributed decisions lacking list markers after ten operator rulings vanished
  from a successor.

**Failure signatures.** Silent resolution of a conflict. Escalation without a
Layer-2 record. An escalation the store refuses. A limitation asserted as a
finding.

**Boundaries.** Escalation carries the impact argument, not merely a stop. A
handoff advises; it never authorizes. A `hold` on an empty instrument is not an
escalation, it is the instrument's silence.

**Cross-cutting.** The design-escalation rule is explicit in the skill. The
routing among `gz task escalate`, `gz obpi block`, a GHI and a handoff ruling is
written nowhere as a rule a fresh agent could apply. Gap.

| Check | Reading, 2026-09-12 |
|---|---|
| Health | Holds fire and the design-escalation rule worked once under load; the declared event channel is inert. |
| Opportunity | Route escalation through the verbs that already exist so it lands on Layer-2; state the routing rule. |
| Strategic fit | The airlock and handoff cooperate to give synthetic memory (operator, 2026-08-17); escalation is where that cooperation is exercised. |
| Tactical tweak | GHI for the closure-scope expressiveness gap; disposition for `task_escalated` in the inertness chore. |
| Retirement | `task_escalated` either gains a producer path agents actually take or is retired from the vocabulary through the inertness chore's disposition. Operator-ruled. |

---

## Three applications, re-mapped to the lenses

1. **Substance evaluation, 2026-09-05** ([EVALUATION_SUBSTANCE.md](../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/EVALUATION_SUBSTANCE.md)):
   a conflict between whole-set atomicity and interruption after the first file
   publication, resolved by an operator-ratified journaled per-file publication
   contract. Lens 3: two guarantees that could not both hold. Lens 1: the
   publication seam made explicit. Useful detection; preserve the semantic
   review's role.
2. **OBPI-0.35.0-06 checkpoint, 2026-09-11** ([handoff](../../.gzkit/handoffs/20260911T082702Z-obpi-0.35.0-06-stage2-complete-awaiting-req03-reclosure.md)):
   three allowlist amendments (Lens 2, jurisdiction discovered late) and a
   repair dispatched during review that invalidated the reviewed digest (Lens 1,
   the digest's seam). Classify separately; do not reopen the OBPI.
3. **Session memory transport** ([gz-session-handoff SKILL.md](../../.gzkit/skills/gz-session-handoff/SKILL.md)):
   Lens 4. Memory quality is what survives delivery and parsing; the two named
   failure modes have targeted responses, not measured savings.

## Instrument observations — dated evidence

**First cut, base commit `d773603e9`** (2026-09-11 evening, dirty tree): the
reachability census read 98 runnable scopes (47 gated, 27 test-only, 23
doc-only, 1 labelled orphan); the individual-scope sweep returned three
non-zero exits (`--audits`, `--evaluation-justify-binding`, `--sensitivity`);
proof freshness exited 3 for both the reachability and ledger-inertness chores
(proofs last committed 2026-08-15, audited surface last moved 2026-09-11); the
inertness report read 76 / 66 / 10.

**Re-verified at `b33a18ea1`** (2026-09-12, clean tree, OBPI-0.35.0-06
complete):

| Instrument | First cut | Now |
|---|---|---|
| `gz validate --sensitivity` | exit 3, active OBPI-06 brief lacked a declaration | exit 0: the brief is terminal and the audit skips terminal briefs; completion carried an operator-approved security-floor override |
| `gz validate --audits` | exit 3, propagating the above | exit 0 |
| `gz validate --evaluation-justify-binding` | exit 3, three ids | unchanged; ungated (tier B), grandfathered *"unreviewed"* since GHI #785 |
| Sweep | 3 non-zero | 1 non-zero, the justify scope |
| Proof freshness, both chores | exit 3 | exit 3, unchanged |
| Reachability census, inertness report | as above | identical |

**Ledger measurements, 2026-09-12** (this session, read-only): airlock
decisions by seam-map emptiness; `acceptance_recorded` rows, proof rows and
distinct digests per landed ADR-0.35.0 brief; tier-1 adversary receipts per
brief; Feature Checklist score distribution across the latest `adr-evaluation`
event per ADR. Figures are quoted in the lenses above.

## How to run the pass

1. **Inventory** what exists under each lens before proposing anything. Read the
   surface; a search is not a read.
2. **Map evidence to lenses.** For each sampled episode record the concern,
   intended guarantee, existing control, exact input and output evidence,
   finding, disposition and confidence.
3. **Mark gaps and overlaps.** A control can serve two lenses (the allowlist
   serves 1 and 2); name which lens a finding belongs to before routing it.
4. **Test against failure signatures.** A finding that matches none of the
   signatures above is either a new signature or not a finding.
5. **Decide**, using the five checks. Dispositions: retain, clarify, reconnect
   an existing control, repair an observed failure, investigate, or retire with
   steering-failure evidence.

Include uneventful completions as comparison cases; a sample selected only for
failures cannot establish their prevalence. The decomposition matrix
([`GovZero/obpi-decomposition-matrix.md`](GovZero/obpi-decomposition-matrix.md)
§ Calibration Policy) already names rework rate, failed gates, attestation churn
and delivery predictability as calibration signals; use those before inventing a
scoring scheme.

## What this record does not license

No mechanism is added on its authority. No ADR is authored and no OBPI is
drawn, started or edited. Observed failures route as GHI-shaped direct repair
through `/ghi-author` or as governed insights. Retirement of any control is an
operator ruling on steering-failure evidence, never an inference from cost.
This record establishes no general cause for longer OBPI completion time; the
two-brief acceptance measurement is a sample, not a trend.

## Reproduction record

First cut (base `d773603e9`), in order, no baseline-writing flags:

```bash
uv run gz chores advise control-surface-validator-reachability
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --sweep
uv run python scripts/check_proof_freshness.py control-surface-validator-reachability
uv run gz validate --evaluation-justify-binding
uv run gz validate --sensitivity
uv run gz validate --audits
uv run gz chores advise ledger-vocabulary-inertness
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report
```

Re-verification (base `b33a18ea1`): the same commands, each captured to a file
with its own exit status read immediately after, plus read-only Python over
`.gzkit/ledger.jsonl` for the airlock, acceptance and evaluation counts, and a
direct call of `_score_feature_checklist` against the ADR-0.35.0 body.

Provenance of the four constructs: the operator's voice conversation of
2026-09-11, supplied in full to the 2026-09-12 session; the Codex paste that
seeded the first cut is `~/.codex/attachments/eaeeda2d-48cc-4129-99e3-1d26b0e743fd/pasted-text.txt`
and the authoring rollout is `rollout-2026-09-11T19-14-42-01a092f7-673b-7cf1-ac27-fa631234f286.jsonl`.
The full transcript is held by the operator and is not checked in.
