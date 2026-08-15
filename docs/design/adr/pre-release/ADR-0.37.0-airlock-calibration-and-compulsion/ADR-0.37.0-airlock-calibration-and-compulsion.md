---
id: ADR-0.37.0-airlock-calibration-and-compulsion
status: Draft
kind: feature
semver: 0.37.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-08-14
---

# ADR-0.37.0-airlock-calibration-and-compulsion: Airlock Calibration and Compulsion

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

Adopt `main-session` (craftsperson, governance-aware, whole-file-reasoning, direct), with one
trait sharpened for this ADR: **an instrument that reports green is not thereby working.**

Every increment here repairs a mechanism that passed its own tests while never biting. Work on
this ADR therefore verifies by *observing the instrument fire on real input* — run
`uv run gz airlock in --target <a real OBPI> --dry-run --json` and read the seam-map counts —
never by reading the code and concluding it should. The measurement that opened this ADR was
exactly that: `push: 0, pull: 0, unaccounted: 0, decision: proceed` on a live OBPI, from a
gate whose 49 unit tests were green.

Corollary the persona must hold: a gate this ADR makes sharper is a gate someone will want to
route around. Prefer the change that makes routing-around visible over the change that makes
the gate louder.

## Intent

ADR-0.33.0 built the airlock membrane and installed it on one door. It is Validated 6/6 and its attestations stand. It disclosed two residuals in its own attested text and scheduled neither.

FIRST: the gate cannot bite. `airlock_enter` takes `parent_invariants: tuple[str, ...] = ()` and no call site passes it (pipeline_runtime.py:590 and :592, permitted_entry.py:243, mx_cmd.py:108), so `pull_edges` is empty at every door. `OntologyGraph.reachable_from` is `nx.descendants` -- transitive dependents, of which a leaf OBPI has none -- so `push_edges` is empty too. `_reconcile` therefore returns an empty `unaccounted` tuple and the fail-closed `_decide` returns PROCEED vacuously. Measured live 2026-08-14: 20 of 23 recorded transits computed an EMPTY seam-map and auto-proceeded; only 3 bit (3, 4 and 7 unaccounted seams -> HOLD). The logic is sound; the input set is empty, and a fail-closed decision over an empty input is vacuously open.

SECOND: nothing compels transit. Measured live 2026-08-14: 525 `fix` commits in 90 days crossed zero transits. 'Wire the door' was in ADR-0.33.0's checklist; 'entry triggers the door' never was.

This ADR RE-HOMES that residual as a feature rather than reopening ADR-0.33.0. Re-homing is this repository's precedent: ADR-0.35.0 exists because ADR-0.0.37's composition engine was withdrawn and re-homed. Appending an OBPI to a Validated ADR would drag it back to Pending and retroactively falsify an operator attestation that was honest when it was given -- the frontier was DISCLOSED in the attested REQ text, so the artifact told the truth and the residual is unscheduled work, not a defective attestation. Foundation is sealed by ADR-0.34.0, so a feature ADR is the only available kind.

## Decision

Sequenced calibrate-then-compel. Widening an uncalibrated gate installs more inert gates (ADR-0.33.0 Negative #1, the load-bearing pre-mortem: 'seam-maps rubber-stamped, GO always reached'); calibrating without compelling leaves a sharp gate nobody walks through.

D1 -- CALIBRATE THE SEAM-MAP, BOTH ARMS. Add `OntologyGraph.reaching(node_id) -> set[str]` (networkx ancestors), the inverse of the existing `reachable_from`. It returns a domain type, so no networkx type crosses the port (hexagonal rule 3). Point the airlock's default reach adapter at it: push edges become what the target DEPENDS ON, which a leaf OBPI has. Separately, thread `parent_invariants` from the parent ADR's `## Boundary Invariants` section through all four call sites so pull edges carry LAW. Both arms are required: wiring pull alone leaves the observed-coupling arm exactly as inert as today.

D2 -- TIGHTEN THE ACCOUNTING PREDICATE. `_reconcile` computes `accounted=dep in brief_text`, a raw substring test over the entire brief. It has been harmless only because the edge sets were empty; the moment D1 lands it becomes load-bearing, and an id appearing inside a rejected-alternatives paragraph would silently account for a seam it does not address. Accounting must key on the brief's declarative sections rather than on any occurrence anywhere in the document. This is coupled-surface correctness under AGENTS.md DO IT RIGHT 1a, not scope creep: D1 is what converts a latent defect into a live one, and 1a requires verifying the consumer's check in the same change.

D3 -- COMPEL AT TWO GRANULARITIES. (a) A `Transit:` commit trailer on `src/**` and `tests/**` commits, producer-stamped by the door and validated by `gz validate`. This is the exact cumulative-with-a-floor shape of the existing `Task:` trailer invariant (.gzkit/rules/task-discovery.md), reusing its producer-stamped pattern, its validator and its scope rather than inventing a parallel mechanism. Commit granularity is chosen because the 525-commits/zero-transits failure is MEASURED in commits. (b) A session-entry door: SessionStart fires airlock-IN, and the handoff-resume-gate's surviving `Write|Edit|NotebookEdit` arm RETIRES INTO it. That arm is an improvisation of Movement B item 3 ('Session entry triggers the airlock'); removing it before the governed door exists would open a gap in front of the door, so the improvisation and the hole close in one move.

D4 -- WARN, THEN FLIP ON WRITTEN EVIDENCE. The trailer gate ships warning-only and flips fail-closed in OBPI-06 OF THIS SAME ADR, against a criterion written into the ADR body. Staging precedent is OBPI-0.0.41-02 -> -03. The flip is an OBPI inside this ADR rather than a successor promise, so the ADR cannot reach 6/6 while carrying a warning-only gate; and the criterion is owned by GHI #804 independently. This is deliberate: an unowned deferral inside an attested artifact is the exact failure ADR-0.33.0 demonstrates and GHI #804 was filed to prevent.

EXPLICITLY OUT OF SCOPE. (i) Reopening ADR-0.33.0 or editing any of its attested REQ text. (ii) The 23-in/5-out transit accounting gap: it remains a Movement B checkbox because it is a PAIRED-EVENT defect shared with `session_exit` (38 skips / 0 writes) and the resume gate's former 160 lifts / 0 blocks, and that family deserves one disposition rather than three. (iii) Widening to Movement B's remaining doors -- the whole ruling was calibrate before widen.

## Consequences

### Positive

1. The gate becomes capable of holding. A leaf OBPI entry yields a non-empty seam-map from surfaces that already exist, converting the measured 20-of-23 vacuous PROCEEDs into real decisions.
2. The 525-commits/zero-transits number becomes both visible and, after the flip, structurally impossible -- measured at the same granularity it was observed.
3. A latent accounting defect is closed at the moment it becomes load-bearing, rather than after it has silently accounted for real seams.
4. The handoff-resume-gate improvisation is retired into a governed door, closing the last forked variant of the airlock's decision grammar without opening a gap.
5. ADR-0.33.0's attestations remain honest and untouched; the residual is re-homed rather than the ADR reopened.
6. The flip criterion is written and owned, so the deferral this ADR repairs cannot recur inside the repair itself.

### Negative

1. OVERRIDE THEATER. If calibration produces 15-20 unaccounted edges per entry, operators will reach for CaptainOverride reflexively and the override becomes the new rubber stamp -- ADR-0.33.0 Negative #1 arriving through the override door instead of the empty-map door. OBPI-02's live NC must assert a BOUNDED non-empty seam-map, and override frequency is a tracked signal rather than a free escape.
2. THE FLIP MAY NOT LAND. OBPI-06 could stall, leaving a warning-only gate and reproducing ADR-0.33.0's failure one ADR later. Mitigated structurally: 6/6 is unreachable without it, and GHI #804 owns the criterion outside this ADR.
3. ANCESTOR-REACH IS A PROXY, NOT THE ANSWER. Ancestors answer 'what does this depend on', which is not the same question as 'what will this break'. The rejected file-coupling alternative answers the second question more directly, and the divergence between the two has NOT been measured.
4. TRAILER FRICTION. A per-commit trailer adds a stamp to every src/** commit. Producer-stamping keeps it off the author, but a stamping failure becomes a commit-time failure.
5. HISTORY IS ONE-WAY. After the flip, ~90 days of commits carry Transit: trailers; the gate is a flag and reverts cheaply, but the trailer data does not.
6. THE ENTRY-PREDICTION ASSUMPTION IS UNPROVEN. The design assumes a seam-map computed at ENTRY predicts what the work will disturb. If work routinely discovers its real blast radius mid-flight, the EXIT accounting is the load-bearing half -- and that is precisely the 23/5 gap this ADR scopes out.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

**This section is load-bearing twice.** It states the fences, and — because D1 threads
`parent_invariants` from the parent ADR's `## Boundary Invariants` — it is also the literal
source of the PULL edges every OBPI under this ADR will be gated against. An ADR-0.37.0 with
no Boundary Invariants section would give its own briefs empty pull edges, reproducing the
exact defect this ADR exists to repair.

1. **ADR-0.33.0 is never reopened and its attested text is never edited.** No OBPI here may
   modify a REQ, acceptance criterion, or attestation under `ADR-0.33.0-airlock-membrane`.
   The residual is RE-HOMED (the `ADR-0.0.37` → `ADR-0.35.0` precedent); reopening would
   drag a `Validated` ADR to `Pending` and retroactively falsify an honest attestation.
2. **One primitive; doors CALL and never fork.** Inherited unchanged from ADR-0.33.0. The
   session-entry door added by OBPI-05 consumes `gzkit.airlock.enter.airlock_enter` and
   defines no local weight, profile, or decision grammar of its own — the
   `handoff-resume-gate` arm it retires was a forked variant, and retiring it must not
   create a second one.
3. **The reason and the door select ceremony WEIGHT, never WHETHER the gate fires.**
   Inherited unchanged from ADR-0.33.0. No entry reason, blast radius, door, or trailer
   state may set the gate to "skip".
4. **The L3 ontology projection INFORMS the gate and never IS the gate.** Architectural
   Boundary 6. Calibration changes what the projection reports; it never promotes the
   projection to source-of-truth, and no gate decision may trace to Layer 3 alone.
5. **`gz git-sync` is never gated by any mechanism in this ADR.** Standing operator ruling,
   verbatim: *"I EXPLICITLY want this"*, and *"handoffs should never, never, never, ever,
   block git-sync. NEVER."* The Transit: trailer gate and the session-entry door both
   exempt it unconditionally.
6. **No mechanism here may require a TTY, PTY, or interactive terminal.** Operator canon at
   invariant tier. A refusal must be recoverable, and a human decision recordable, with no
   interactive transport available.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

Each row is RED today and goes green as its owning OBPI lands. Row 2 is the ADR's thesis:
measured live 2026-08-14 on a real OBPI, the same command returned
`"push": 0, "pull": 0, "unaccounted": 0, "decision": "proceed"`.

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The ontology exposes an inverse traversal (OBPI-01) | uv run python -c "from gzkit.ontology.graph import OntologyGraph; raise SystemExit(0 if hasattr(OntologyGraph, 'reaching') else 1)" | 0 |
| A real OBPI entry computes a NON-EMPTY seam-map (OBPI-02) | uv run python -c "import json,subprocess; d=json.loads(subprocess.run(['uv','run','gz','airlock','in','--target','OBPI-0.37.0-01-ontology-inverse-reach','--dry-run','--json'],capture_output=True,text=True).stdout)['seam_map']; raise SystemExit(0 if d['push'] or d['pull'] else 1)" | 0 |
| A src/** commit carries a door-stamped Transit: trailer (OBPI-04) | uv run python -c "import subprocess; m=subprocess.run(['git','log','-1','--format=%B','--','src/'],capture_output=True,text=True).stdout; raise SystemExit(0 if 'Transit:' in m else 1)" | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 6

Scoring notes (why these numbers, not the template defaults):

- **Logic/Engine 2** — two distinct engines change: the reach direction and the accounting
  predicate. They are independently wrong today and independently testable.
- **Interface 2** — three operator-visible surfaces (a commit trailer, a SessionStart door,
  a `gz validate` refusal), not one.
- **Observability 2** — the ADR adds two live negative controls and changes what the
  transit ledger events mean.
- **Split Single-Narrative 1** — *calibrate* and *compel* are two narratives, and the
  operator ruling sequences them deliberately. They must not share a brief.
- **Split Surface Boundary 1** — the work crosses `ontology/` → `airlock/` → hooks →
  `governance/` validators. Each boundary is a natural brief edge.
- **Final count 6, not 4** — the two splits carry the baseline from 4 to 6. This
  supersedes the template's default of 3, which was not scored against this ADR.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.37.0-01 ontology-inverse-reach -- add OntologyGraph.reaching() returning set[str] (networkx ancestors), the inverse of reachable_from; core exercisable with no projection built
- [ ] OBPI-0.37.0-02 airlock-seam-calibration -- point the default reach adapter at the inverse and thread parent_invariants through all four call sites; live NC asserts a leaf-OBPI entry computes a bounded non-empty seam-map
- [ ] OBPI-0.37.0-03 seam-accounting-predicate -- accounting keys on the brief's declarative sections rather than any substring occurrence
- [ ] OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it
- [ ] OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it
- [ ] OBPI-0.37.0-06 transit-gate-flip -- flip item 4 fail-closed against the written criterion; live NC asserts un-triggered entry makes the claim fail

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-08-14T19:19:56.561279*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.37.0-airlock-calibration-and-compulsion

### Q: What is the title of this ADR?

**A:** Airlock Calibration and Compulsion

### Q: What is the semantic version?

**A:** 0.37.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** ADR-0.33.0 built the airlock membrane and installed it on one door. It is Validated 6/6 and its attestations stand. It disclosed two residuals in its own attested text and scheduled neither.

FIRST: the gate cannot bite. `airlock_enter` takes `parent_invariants: tuple[str, ...] = ()` and no call site passes it (pipeline_runtime.py:590 and :592, permitted_entry.py:243, mx_cmd.py:108), so `pull_edges` is empty at every door. `OntologyGraph.reachable_from` is `nx.descendants` -- transitive dependents, of which a leaf OBPI has none -- so `push_edges` is empty too. `_reconcile` therefore returns an empty `unaccounted` tuple and the fail-closed `_decide` returns PROCEED vacuously. Measured live 2026-08-14: 20 of 23 recorded transits computed an EMPTY seam-map and auto-proceeded; only 3 bit (3, 4 and 7 unaccounted seams -> HOLD). The logic is sound; the input set is empty, and a fail-closed decision over an empty input is vacuously open.

SECOND: nothing compels transit. Measured live 2026-08-14: 525 `fix` commits in 90 days crossed zero transits. 'Wire the door' was in ADR-0.33.0's checklist; 'entry triggers the door' never was.

This ADR RE-HOMES that residual as a feature rather than reopening ADR-0.33.0. Re-homing is this repository's precedent: ADR-0.35.0 exists because ADR-0.0.37's composition engine was withdrawn and re-homed. Appending an OBPI to a Validated ADR would drag it back to Pending and retroactively falsify an operator attestation that was honest when it was given -- the frontier was DISCLOSED in the attested REQ text, so the artifact told the truth and the residual is unscheduled work, not a defective attestation. Foundation is sealed by ADR-0.34.0, so a feature ADR is the only available kind.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Sequenced calibrate-then-compel. Widening an uncalibrated gate installs more inert gates (ADR-0.33.0 Negative #1, the load-bearing pre-mortem: 'seam-maps rubber-stamped, GO always reached'); calibrating without compelling leaves a sharp gate nobody walks through.

D1 -- CALIBRATE THE SEAM-MAP, BOTH ARMS. Add `OntologyGraph.reaching(node_id) -> set[str]` (networkx ancestors), the inverse of the existing `reachable_from`. It returns a domain type, so no networkx type crosses the port (hexagonal rule 3). Point the airlock's default reach adapter at it: push edges become what the target DEPENDS ON, which a leaf OBPI has. Separately, thread `parent_invariants` from the parent ADR's `## Boundary Invariants` section through all four call sites so pull edges carry LAW. Both arms are required: wiring pull alone leaves the observed-coupling arm exactly as inert as today.

D2 -- TIGHTEN THE ACCOUNTING PREDICATE. `_reconcile` computes `accounted=dep in brief_text`, a raw substring test over the entire brief. It has been harmless only because the edge sets were empty; the moment D1 lands it becomes load-bearing, and an id appearing inside a rejected-alternatives paragraph would silently account for a seam it does not address. Accounting must key on the brief's declarative sections rather than on any occurrence anywhere in the document. This is coupled-surface correctness under AGENTS.md DO IT RIGHT 1a, not scope creep: D1 is what converts a latent defect into a live one, and 1a requires verifying the consumer's check in the same change.

D3 -- COMPEL AT TWO GRANULARITIES. (a) A `Transit:` commit trailer on `src/**` and `tests/**` commits, producer-stamped by the door and validated by `gz validate`. This is the exact cumulative-with-a-floor shape of the existing `Task:` trailer invariant (.gzkit/rules/task-discovery.md), reusing its producer-stamped pattern, its validator and its scope rather than inventing a parallel mechanism. Commit granularity is chosen because the 525-commits/zero-transits failure is MEASURED in commits. (b) A session-entry door: SessionStart fires airlock-IN, and the handoff-resume-gate's surviving `Write|Edit|NotebookEdit` arm RETIRES INTO it. That arm is an improvisation of Movement B item 3 ('Session entry triggers the airlock'); removing it before the governed door exists would open a gap in front of the door, so the improvisation and the hole close in one move.

D4 -- WARN, THEN FLIP ON WRITTEN EVIDENCE. The trailer gate ships warning-only and flips fail-closed in OBPI-06 OF THIS SAME ADR, against a criterion written into the ADR body. Staging precedent is OBPI-0.0.41-02 -> -03. The flip is an OBPI inside this ADR rather than a successor promise, so the ADR cannot reach 6/6 while carrying a warning-only gate; and the criterion is owned by GHI #804 independently. This is deliberate: an unowned deferral inside an attested artifact is the exact failure ADR-0.33.0 demonstrates and GHI #804 was filed to prevent.

EXPLICITLY OUT OF SCOPE. (i) Reopening ADR-0.33.0 or editing any of its attested REQ text. (ii) The 23-in/5-out transit accounting gap: it remains a Movement B checkbox because it is a PAIRED-EVENT defect shared with `session_exit` (38 skips / 0 writes) and the resume gate's former 160 lifts / 0 blocks, and that family deserves one disposition rather than three. (iii) Widening to Movement B's remaining doors -- the whole ruling was calibrate before widen.

### Q: What good things result from this decision? List benefits.

**A:** 1. The gate becomes capable of holding. A leaf OBPI entry yields a non-empty seam-map from surfaces that already exist, converting the measured 20-of-23 vacuous PROCEEDs into real decisions.
2. The 525-commits/zero-transits number becomes both visible and, after the flip, structurally impossible -- measured at the same granularity it was observed.
3. A latent accounting defect is closed at the moment it becomes load-bearing, rather than after it has silently accounted for real seams.
4. The handoff-resume-gate improvisation is retired into a governed door, closing the last forked variant of the airlock's decision grammar without opening a gap.
5. ADR-0.33.0's attestations remain honest and untouched; the residual is re-homed rather than the ADR reopened.
6. The flip criterion is written and owned, so the deferral this ADR repairs cannot recur inside the repair itself.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. OVERRIDE THEATER. If calibration produces 15-20 unaccounted edges per entry, operators will reach for CaptainOverride reflexively and the override becomes the new rubber stamp -- ADR-0.33.0 Negative #1 arriving through the override door instead of the empty-map door. OBPI-02's live NC must assert a BOUNDED non-empty seam-map, and override frequency is a tracked signal rather than a free escape.
2. THE FLIP MAY NOT LAND. OBPI-06 could stall, leaving a warning-only gate and reproducing ADR-0.33.0's failure one ADR later. Mitigated structurally: 6/6 is unreachable without it, and GHI #804 owns the criterion outside this ADR.
3. ANCESTOR-REACH IS A PROXY, NOT THE ANSWER. Ancestors answer 'what does this depend on', which is not the same question as 'what will this break'. The rejected file-coupling alternative answers the second question more directly, and the divergence between the two has NOT been measured.
4. TRAILER FRICTION. A per-commit trailer adds a stamp to every src/** commit. Producer-stamping keeps it off the author, but a stamping failure becomes a commit-time failure.
5. HISTORY IS ONE-WAY. After the flip, ~90 days of commits carry Transit: trailers; the gate is a flag and reverts cheaply, but the trailer data does not.
6. THE ENTRY-PREDICTION ASSUMPTION IS UNPROVEN. The design assumes a seam-map computed at ENTRY predicts what the work will disturb. If work routinely discovers its real blast radius mid-flight, the EXIT accounting is the load-bearing half -- and that is precisely the 23/5 gap this ADR scopes out.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OBPI-0.37.0-01 ontology-inverse-reach -- add OntologyGraph.reaching() returning set[str] (networkx ancestors), the inverse of reachable_from; core exercisable with no projection built
2. OBPI-0.37.0-02 airlock-seam-calibration -- point the default reach adapter at the inverse and thread parent_invariants through all four call sites; live NC asserts a leaf-OBPI entry computes a bounded non-empty seam-map
3. OBPI-0.37.0-03 seam-accounting-predicate -- accounting keys on the brief's declarative sections rather than any substring occurrence
4. OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it
5. OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it
6. OBPI-0.37.0-06 transit-gate-flip -- flip item 4 fail-closed against the written criterion; live NC asserts un-triggered entry makes the claim fail

### Q: What alternatives were considered and why were they rejected?

**A:** 1. KEEP DESCENDANTS, WIRE PULL ONLY. Smallest diff: leave reachable_from alone and only thread parent_invariants. REJECTED -- a leaf OBPI still contributes zero push edges, so the gate bites on LAW while the observed-coupling arm stays exactly as inert as today. Half a calibration is an inert gate with better paperwork.

2. SEAMS FROM FILE-LEVEL IMPORT COUPLING. Compute seams from who imports the brief's declared Allowed Paths, rather than from the ontology graph. REJECTED AS THE FIRST INCREMENT, not on merit -- it answers 'what will this disturb' more directly than artifact adjacency does, and is the strongest successor candidate. It replaces the seam SOURCE, which is a larger re-architecture than calibrating the source that already exists, and ADR-0.33.0's Boundary Invariant ties all doors to one primitive.

3. UNION THE ONTOLOGY GRAPH AND FILE COUPLING. REJECTED -- most complete blast radius, largest increment, and the most ways to generate noise an operator must dismiss, on a gate whose named failure mode is already rubber-stamping.

4. FAIL-CLOSED IMMEDIATELY. REJECTED on ADR-0.33.0 Negative #5 in its own words: a mis-calibrated gate must not '2am-wall a real pipeline'. The CaptainOverride escape exists, but the pressure under a bad wall is to disable the mechanism rather than fix it, and this ADR's entire purpose is that the mechanism survive and bite.

5. FAIL-CLOSED ON A NARROW PATH SCOPE. Bite immediately but only on src/gzkit/airlock/** and the governance validators, widening later by editing a list. REJECTED as a close second -- the calibration work ITSELF lands in src/gzkit/airlock/**, so the gate would fire on its own construction.

6. MEASURE ONLY; COMPEL IN A SUCCESSOR ADR. REJECTED -- this is what ADR-0.33.0 did. A successor that will compel later with no named owner is precisely GHI #804's shape, and repeating it inside the repair would be self-refuting.

7. THE MX DOOR AS THE COMPULSION POINT. Route direct-fix work through gz mx enter, which already calls airlock-IN for any --reason. REJECTED as the mechanism -- nothing forces gz mx enter either, so compulsion just moves one step back and the same question re-appears there. Retained as a CONSUMER of the trailer rather than as the compelling mechanism.

### Q: Pre-mortem (Klein): it is 18 months from now and this decision has failed spectacularly. Why? Name the mitigation.

**A:** Two failure paths, both named with mitigations.

(a) THE FLIP NEVER HAPPENS. OBPI-06 stalls; ADR-0.37.0 closes Validated carrying a warning-only gate, reproducing ADR-0.33.0's exact failure one ADR later. MITIGATION: the flip is an OBPI inside this ADR rather than a successor promise, so the ADR's own completion count blocks on it; and GHI #804 owns the criterion independently of this ADR's lifecycle.

(b) OVERRIDE THEATER -- the sharper path. Calibration succeeds too well: every entry surfaces 15-20 unaccounted ancestor edges, operators learn to reach for CaptainOverride reflexively, and the override becomes the new rubber stamp. Negative #1 arrives through the override door instead of the empty-map door, and the ADR that was written to make the gate bite is what taught everyone to bypass it. MITIGATION: OBPI-02's live negative control asserts a BOUNDED non-empty seam-map, not merely a non-empty one; override frequency is a tracked signal rather than a free escape.

### Q: What would have to be true (Martin) for this to be the right decision — and which of those conditions is shakiest?

**A:** FOR THIS TO BE THE RIGHT DECISION, three conditions must hold: (a) ancestor-reach is a meaningful blast-radius proxy; (b) a brief's declarative sections genuinely name what the work will disturb; (c) the commit is the right unit for compulsion.

THE SHAKIEST IS (a), and it is named here rather than buried. Ancestors answer 'what does this depend on'. That is NOT the same question as 'what will this break'. The design proceeds on the judgment that dependency is a usable proxy for disturbance at OBPI granularity, and that judgment is the largest single risk in the ADR.

FOR ALTERNATIVE 2 (file-level import coupling) TO HAVE BEEN BETTER, code coupling would have to diverge materially from artifact-graph adjacency. That divergence is MEASURABLE and has NOT been measured. Measuring it is the named precondition for the successor ADR.

### Q: Constraint archaeology: is each constraint here real, inherited, or assumed? When was it last tested?

**A:** REAL AND LOAD-BEARING, re-tested this session: one primitive that doors CALL and never fork (ADR-0.33.0 Boundary Invariant -- verified live, all four call sites reach the same gzkit.airlock.enter.airlock_enter); the L3 ontology projection INFORMS the gate and never IS the gate (Architectural Boundary 6); foundation is sealed (ADR-0.34.0, enforced at both adr_created ingresses and by gz validate --taxonomy, so gz plan create --kind foundation exits 1).

ASSUMED AND NEVER RE-TESTED: that the ontology projection is the right seam SOURCE at all. That choice was inherited wholesale from ADR-0.33.0 and has never been re-examined -- this ADR keeps it, and says so out loud rather than letting inheritance pass for a decision. Alternative 2 is the standing challenge to it.

INHERITED AND STILL CORRECT: the diagnostic-only posture at the pipeline call site, adopted so a mis-calibrated gate could not wall a real pipeline. D4 keeps it during the warn phase for exactly the original reason.

### Q: Assumption surfacing: which assumptions are implicit and undocumented? What if the opposite of the core assumption were true?

**A:** THE IMPLICIT, UNDOCUMENTED ASSUMPTION: that a seam-map computed AT ENTRY predicts what the work will disturb -- that intent declared up front matches actual blast radius.

IF THE OPPOSITE WERE TRUE -- if work routinely discovers its real blast radius mid-flight -- then an entry gate is the wrong instrument and the EXIT accounting is the load-bearing half. That is precisely the 23-in/5-out gap this ADR scopes OUT, which makes the scoping decision load-bearing rather than administrative. The 18 unaccounted exits are the only existing evidence about this assumption, and they are evidence AGAINST it being safe to ignore.

SECOND SURFACED ASSUMPTION: that a brief's declarative sections are written with enough care to serve as the accounting authority. D2 raises the stakes on brief-authoring quality without adding any check on it.

### Q: The 2am operator question: you are on-call at 2am and this is broken. What do you need that the design does not provide?

**A:** IT IS 2AM AND THE TRAILER GATE HAS REFUSED A COMMIT. What the design must provide and must never require:

1. The refusal prose must print the EXACT transit command to run and the override path, per .gzkit/rules/guardrail-feedback-prose.md (what failed / why it is forbidden, cited / the governed next step, runnable). A bare exit code at 2am is how a mechanism gets disabled.
2. It must NEVER require a TTY or an interactive terminal. Operator canon is verbatim and absolute: no transport mechanism may EVER be cited as a reason a human decision cannot be recorded.
3. `gz git-sync` MUST NEVER BE GATED. Standing operator ruling, verbatim: 'I EXPLICITLY want this', and separately 'handoffs should never, never, never, ever, block git-sync. NEVER.' A gate that walls sync at 2am is the single most likely cause of the whole mechanism being ripped out.
4. The override must be reachable without reading the ADR -- the refusal names it inline.

### Q: Reversibility: one-way door or two-way? If this must be reversed in 12 months, what does that cost?

**A:** MOSTLY A TWO-WAY DOOR. D1 (reach direction, parent_invariants threading) and D2 (accounting predicate) are predicate and wiring changes, revertible in a single commit with no data consequence. The D3 warn phase emits a trailer and a warning; reverting costs nothing.

THE ASYMMETRY IS DATA, NOT THE GATE. After the flip, roughly 90 days of commits carry Transit: trailers. The GATE is a flag and reverts cheaply; the HISTORY does not -- un-stamping would be a history rewrite, which this repository does only under a PII incident. Reversal cost is therefore bounded to the gate, and the residue is inert metadata in commit messages.

At 12 months the realistic reversal is 'stop enforcing, keep stamping', which is cheap and loses nothing but the compulsion.

### Q: Scope minimization: what is the smallest version that delivers value? If you had half the time, what would you cut?

**A:** THE SMALLEST VERSION THAT DELIVERS VALUE IS OBPI-01 + OBPI-02 ALONE. Those two convert the measured 20-of-23 vacuous PROCEEDs into real decisions and constitute the entirety of 'calibrate before widening'. Everything after them is compulsion, which is worthless if the gate cannot bite -- so this is also the correct build order, not merely the minimal cut.

WITH HALF THE TIME: cut OBPI-03 (accounting predicate) and file it as a GHI with the D2 evidence. NEVER cut OBPI-06 -- cutting the flip IS the failure mode this ADR exists to repair, and a warning-only gate shipped as 'done' is ADR-0.33.0 repeating itself.

### Q: Closing question: what subsequent decisions does this force? What ADRs will we need to write because of this one?

**A:** 1. A SUCCESSOR FEATURE ADR FOR FILE-COUPLING SEAMS (rejected alternative 2), gated on first MEASURING the divergence between code coupling and artifact-graph adjacency. Without that measurement it is a preference, not a decision.
2. A SINGLE HOME FOR THE PAIRED-EVENT FAMILY. Three instances found on one day: the resume gate (160 lifts / 0 blocks, fixed), session_exit (38 skips / 0 writes, GHI #766 open), and the airlock (23 in / 5 out). No owner currently asks 'does this event's decision have a counterpart for its other branch?'. This ADR deliberately does not absorb it.
3. WIDENING TO MOVEMENT B'S REMAINING DOORS -- the GHI/MX door and the ad-hoc/permitted door -- which becomes safe only once this ADR's calibration has a measured track record.
4. Possibly a brief-authoring-quality check, since D2 raises the stakes on declarative sections without adding any check on them (surfaced in assumption_surfacing).


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. KEEP DESCENDANTS, WIRE PULL ONLY. Smallest diff: leave reachable_from alone and only thread parent_invariants. REJECTED -- a leaf OBPI still contributes zero push edges, so the gate bites on LAW while the observed-coupling arm stays exactly as inert as today. Half a calibration is an inert gate with better paperwork.

2. SEAMS FROM FILE-LEVEL IMPORT COUPLING. Compute seams from who imports the brief's declared Allowed Paths, rather than from the ontology graph. REJECTED AS THE FIRST INCREMENT, not on merit -- it answers 'what will this disturb' more directly than artifact adjacency does, and is the strongest successor candidate. It replaces the seam SOURCE, which is a larger re-architecture than calibrating the source that already exists, and ADR-0.33.0's Boundary Invariant ties all doors to one primitive.

3. UNION THE ONTOLOGY GRAPH AND FILE COUPLING. REJECTED -- most complete blast radius, largest increment, and the most ways to generate noise an operator must dismiss, on a gate whose named failure mode is already rubber-stamping.

4. FAIL-CLOSED IMMEDIATELY. REJECTED on ADR-0.33.0 Negative #5 in its own words: a mis-calibrated gate must not '2am-wall a real pipeline'. The CaptainOverride escape exists, but the pressure under a bad wall is to disable the mechanism rather than fix it, and this ADR's entire purpose is that the mechanism survive and bite.

5. FAIL-CLOSED ON A NARROW PATH SCOPE. Bite immediately but only on src/gzkit/airlock/** and the governance validators, widening later by editing a list. REJECTED as a close second -- the calibration work ITSELF lands in src/gzkit/airlock/**, so the gate would fire on its own construction.

6. MEASURE ONLY; COMPEL IN A SUCCESSOR ADR. REJECTED -- this is what ADR-0.33.0 did. A successor that will compel later with no named owner is precisely GHI #804's shape, and repeating it inside the repair would be self-refuting.

7. THE MX DOOR AS THE COMPULSION POINT. Route direct-fix work through gz mx enter, which already calls airlock-IN for any --reason. REJECTED as the mechanism -- nothing forces gz mx enter either, so compulsion just moves one step back and the same question re-appears there. Retained as a CONSUMER of the trailer rather than as the compelling mechanism.

## Forcing Functions

<!-- The seven techniques `gz-adr-create` SKILL.md declares non-negotiable, plus
     its closing question. Agent drafts each against session evidence; the
     operator audits, names what was missed, and confirms
     (AGENTS.md § OPERATOR ECONOMY OF EFFORT #4) — this is agent labor, not
     operator typing. -->

### Pre-Mortem

Two failure paths, both named with mitigations.

(a) THE FLIP NEVER HAPPENS. OBPI-06 stalls; ADR-0.37.0 closes Validated carrying a warning-only gate, reproducing ADR-0.33.0's exact failure one ADR later. MITIGATION: the flip is an OBPI inside this ADR rather than a successor promise, so the ADR's own completion count blocks on it; and GHI #804 owns the criterion independently of this ADR's lifecycle.

(b) OVERRIDE THEATER -- the sharper path. Calibration succeeds too well: every entry surfaces 15-20 unaccounted ancestor edges, operators learn to reach for CaptainOverride reflexively, and the override becomes the new rubber stamp. Negative #1 arrives through the override door instead of the empty-map door, and the ADR that was written to make the gate bite is what taught everyone to bypass it. MITIGATION: OBPI-02's live negative control asserts a BOUNDED non-empty seam-map, not merely a non-empty one; override frequency is a tracked signal rather than a free escape.

### What Would Have to Be True

FOR THIS TO BE THE RIGHT DECISION, three conditions must hold: (a) ancestor-reach is a meaningful blast-radius proxy; (b) a brief's declarative sections genuinely name what the work will disturb; (c) the commit is the right unit for compulsion.

THE SHAKIEST IS (a), and it is named here rather than buried. Ancestors answer 'what does this depend on'. That is NOT the same question as 'what will this break'. The design proceeds on the judgment that dependency is a usable proxy for disturbance at OBPI granularity, and that judgment is the largest single risk in the ADR.

FOR ALTERNATIVE 2 (file-level import coupling) TO HAVE BEEN BETTER, code coupling would have to diverge materially from artifact-graph adjacency. That divergence is MEASURABLE and has NOT been measured. Measuring it is the named precondition for the successor ADR.

### Constraint Archaeology

REAL AND LOAD-BEARING, re-tested this session: one primitive that doors CALL and never fork (ADR-0.33.0 Boundary Invariant -- verified live, all four call sites reach the same gzkit.airlock.enter.airlock_enter); the L3 ontology projection INFORMS the gate and never IS the gate (Architectural Boundary 6); foundation is sealed (ADR-0.34.0, enforced at both adr_created ingresses and by gz validate --taxonomy, so gz plan create --kind foundation exits 1).

ASSUMED AND NEVER RE-TESTED: that the ontology projection is the right seam SOURCE at all. That choice was inherited wholesale from ADR-0.33.0 and has never been re-examined -- this ADR keeps it, and says so out loud rather than letting inheritance pass for a decision. Alternative 2 is the standing challenge to it.

INHERITED AND STILL CORRECT: the diagnostic-only posture at the pipeline call site, adopted so a mis-calibrated gate could not wall a real pipeline. D4 keeps it during the warn phase for exactly the original reason.

### Assumption Surfacing

THE IMPLICIT, UNDOCUMENTED ASSUMPTION: that a seam-map computed AT ENTRY predicts what the work will disturb -- that intent declared up front matches actual blast radius.

IF THE OPPOSITE WERE TRUE -- if work routinely discovers its real blast radius mid-flight -- then an entry gate is the wrong instrument and the EXIT accounting is the load-bearing half. That is precisely the 23-in/5-out gap this ADR scopes OUT, which makes the scoping decision load-bearing rather than administrative. The 18 unaccounted exits are the only existing evidence about this assumption, and they are evidence AGAINST it being safe to ignore.

SECOND SURFACED ASSUMPTION: that a brief's declarative sections are written with enough care to serve as the accounting authority. D2 raises the stakes on brief-authoring quality without adding any check on it.

### The 2am Operator Question

IT IS 2AM AND THE TRAILER GATE HAS REFUSED A COMMIT. What the design must provide and must never require:

1. The refusal prose must print the EXACT transit command to run and the override path, per .gzkit/rules/guardrail-feedback-prose.md (what failed / why it is forbidden, cited / the governed next step, runnable). A bare exit code at 2am is how a mechanism gets disabled.
2. It must NEVER require a TTY or an interactive terminal. Operator canon is verbatim and absolute: no transport mechanism may EVER be cited as a reason a human decision cannot be recorded.
3. `gz git-sync` MUST NEVER BE GATED. Standing operator ruling, verbatim: 'I EXPLICITLY want this', and separately 'handoffs should never, never, never, ever, block git-sync. NEVER.' A gate that walls sync at 2am is the single most likely cause of the whole mechanism being ripped out.
4. The override must be reachable without reading the ADR -- the refusal names it inline.

### Reversibility

MOSTLY A TWO-WAY DOOR. D1 (reach direction, parent_invariants threading) and D2 (accounting predicate) are predicate and wiring changes, revertible in a single commit with no data consequence. The D3 warn phase emits a trailer and a warning; reverting costs nothing.

THE ASYMMETRY IS DATA, NOT THE GATE. After the flip, roughly 90 days of commits carry Transit: trailers. The GATE is a flag and reverts cheaply; the HISTORY does not -- un-stamping would be a history rewrite, which this repository does only under a PII incident. Reversal cost is therefore bounded to the gate, and the residue is inert metadata in commit messages.

At 12 months the realistic reversal is 'stop enforcing, keep stamping', which is cheap and loses nothing but the compulsion.

### Scope Minimization

THE SMALLEST VERSION THAT DELIVERS VALUE IS OBPI-01 + OBPI-02 ALONE. Those two convert the measured 20-of-23 vacuous PROCEEDs into real decisions and constitute the entirety of 'calibrate before widening'. Everything after them is compulsion, which is worthless if the gate cannot bite -- so this is also the correct build order, not merely the minimal cut.

WITH HALF THE TIME: cut OBPI-03 (accounting predicate) and file it as a GHI with the D2 evidence. NEVER cut OBPI-06 -- cutting the flip IS the failure mode this ADR exists to repair, and a warning-only gate shipped as 'done' is ADR-0.33.0 repeating itself.

### Downstream Decisions Forced

1. A SUCCESSOR FEATURE ADR FOR FILE-COUPLING SEAMS (rejected alternative 2), gated on first MEASURING the divergence between code coupling and artifact-graph adjacency. Without that measurement it is a preference, not a decision.
2. A SINGLE HOME FOR THE PAIRED-EVENT FAMILY. Three instances found on one day: the resume gate (160 lifts / 0 blocks, fixed), session_exit (38 skips / 0 writes, GHI #766 open), and the airlock (23 in / 5 out). No owner currently asks 'does this event's decision have a counterpart for its other branch?'. This ADR deliberately does not absorb it.
3. WIDENING TO MOVEMENT B'S REMAINING DOORS -- the GHI/MX door and the ad-hoc/permitted door -- which becomes safe only once this ADR's calibration has a measured track record.
4. Possibly a brief-authoring-quality check, since D2 raises the stakes on declarative sections without adding any check on them (surfaced in assumption_surfacing).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.37.0 | Pending | | | |
