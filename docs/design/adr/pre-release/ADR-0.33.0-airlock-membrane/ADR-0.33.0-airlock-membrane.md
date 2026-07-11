---
id: ADR-0.33.0-airlock-membrane
status: Draft
kind: feature
semver: 0.33.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-07-08
---

# ADR-0.33.0-airlock-membrane: the airlock — entry/exit membrane for agent sorties

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. This ADR builds the membrane that makes an agent's every entry accountable, so author it in that spirit: the airlock earns trust by **biting**, never by ceremony — a gate that cannot refuse GO is theater. Extract the primitive from the pipeline's proven geometry; never invent a parallel surface the doors would drift from. Hold the two hardest lines without flinching: the airlock **never writes L1 canon** (it proposes; the captain ratifies), and its **acknowledge-and-decide gate is never dressed as completion-attestation** (the sacred word stays reserved). Same shape both ways — airlock-in and airlock-out are co-equal. The seam-map is the externalized working set the model cannot hold in its head; keep it honest about what it sees (edges) and what it cannot (bodies), never laundering a blind spot into false confidence.

## Intent

An agent cannot hold a model of the project resident across sorties -- operator verbatim: 'the model's inability to retain a model of the project without having to reconstruct it on each sortie.' Unable to hold the whole picture, it patches locally, perturbs laterally, and discovers the damage late (the 'prior ecosystems of upsets'). gzkit governs artifacts (vertical traceability) and execution (the OBPI pipeline) well, but there is no membrane on ENTRY into the project ecosystem. This ADR builds that membrane -- the airlock -- as prosthetic memory: on the way IN it pings the shape and reconciles the agent's expectation against reality so the model need not hold everything (the seam-map IS the externalized working set); on the way OUT it accounts for what was disturbed and updates the maps, so map-maintenance becomes an unavoidable byproduct of any work rather than a separate chore (Architectural Boundary #4). The governing principle is the operator's, verbatim: 'The airlock fires because an agent is entering the project ecosystem -- full stop. The reason for entry selects the door; it never decides whether the airlock fires.' Three entry-reasons, three doors: pipeline (design implementation -- intentional change), mx/ghi (defect repair -- correction to a desired state), and permitted-entry (ad-hoc/spurious -- reconnaissance for comprehension with light repair at most, bracketing action: upstream of planning and downstream of action). The pipeline already IS an airlock silhouette (Stage 1 pre-flight, Stage 5 exit); mx has an enter-gate; but ad-hoc entry crosses no membrane at all -- the silent-bypass surface. This ADR names what the pipeline already does, extracts it as a reusable primitive, and closes the bypass. It also makes work-phases-and-airlock.md and four-phases-of-work.md lawful -- the campaign's Movement III section-8 '1.0 gate' -- and binds the section-5 enforcement-claim primitive (un-accounted seam -> real entry -> assert refuses GO).

## Decision

Extract ONE symmetric airlock primitive (airlock-IN + airlock-OUT, co-equal 'same shape both ways') FROM the pipeline's already-proven Stage-1 (pre-flight) / Stage-5 (exit) geometry -- the pipeline is the canonical door and the calibration reference (operator: the airlock 'was written with the pipeline in mind'; section-7 apparatus scan: 'the process that had MOST earned its keep'). mx and permitted-entry adapt to the airlock; the airlock is never forked per-door. AIRLOCK-IN is a three-beat, not a single compute: (1) DECLARE intent + expectation; (2) PING the shape via the HULL sonar (gz ontology sense/reach) -- state-doctrine Rule 5: the L3 projection INFORMS, it never DECIDES; (3) RECONCILE the ping against the assumptions the plan permitted -> refresh the L3 map + re-plan; then the gate. AIRLOCK-OUT (co-equal): drift-diff push-minus-pull -> findings + recommendations -> a decision menu (leave-it-be | modify | repair | adjust-maps) -> route any discovered correction as a FRESH transit through the right door (never smuggled inline; 'better housekeeping/bookkeeping') -> log to L2. The gate is ACKNOWLEDGE-AND-DECIDE (proceed | pause | hold | revert), a DIFFERENT sort of operator input from Gate-5 completion attestation ('we are at a gate; here is the current reality we've found -- acknowledge it and its impact, then proceed, OR acknowledge and pause/hold/revert'); keeping the two distinct PRESERVES the force of the sacrosanct completion-attestation. The gate is universal in nature, variable in execution: ceremony scales by door (pipeline tight; mx corrective; permitted-entry permissive), calibrated to the pipeline; blast_radius is the DELEGATION dial (small+fully-accounted may auto-proceed, logged), never a responsibility dial -- the captain owns every outcome. State-doctrine boundary (fail-closed by BI): the airlock ALWAYS logs what it encounters to the L2 ledger (L3 recomputes from L1+L2); it NEVER rewrites L1 canon -- it reports findings and proposes governed, attested amendments only. The seam-map carries BOTH senses of 'seam' (operator refinement): seam-as-BODY (a contiguous region of similarity = the FOOTPRINT; for the pipeline door these are the OBPI brief's DECLARED Allowed Paths, not an inferred guess) and seam-as-BOUNDARY (the push/pull edges = the join). PUSH edges come from gz ontology reach (computed blast radius); PULL edges from the brief + parent-ADR invariants. An un-accounted seam makes GO STRUCTURALLY UNREACHABLE -- the airlock blocks until the declarer accounts for it, then the captain/delegate decides (the section-5 live negative control: omit a real reach push edge from a real entry, un-forced production, assert GO cannot be reached). Tracer-first (KEEL/ADR-0.31.0 discipline): the FIRST slice is the PIPELINE door, in+out co-equal, piercing declare->ping->reconcile->gate->L2 and drift-diff->decision->L2, with the section-5 @enforces live NC as the landing keystone; mx, permitted-entry, and the doctrine-lawful promotion are gated-breadth OBPIs that do not begin until the NC bites live. Diagnostic refusal is a requirement, not a nicety (2am finding): a NO-GO names the exact un-accounted seam + its provenance + a one-command re-sense to rule out stale L3, and any captain override is LOGGED and revocable (ADR-0.29.0 witnessed-override precedent). NO new runtime dependency: the tracer stands on gz ontology reach (already-attested HULL floor) + declared Allowed Paths + brief/ADR invariants; graspologic stays ruled out (3.13-incompatible; statistical inference has no place in a gating path); if undeclared-body auto-detection is ever built it is networkx.algorithms.community (already in the floor), strictly L3-advisory, never gating.

## Consequences

### Positive

1. Prosthetic memory: the model no longer must reconstruct the whole project each sortie -- it is HANDED the bounded seam-set on entry and accounts for exactly those. Map-maintenance becomes an unavoidable byproduct of any work, so the map cannot go stale -- closing Architectural Boundary #4 ('do not let reconciliation remain a maintenance chore') structurally, stronger than a reconciliation cron.
2. The silent-bypass hole closes: ad-hoc/spurious entry (permitted-entry) finally crosses a membrane. A gate with a hole is not a gate; this makes the airlock total rather than mostly.
3. The attestation canon is PRESERVED, not diluted: the acknowledge-and-decide gate is a distinct sort from completion-attestation, so the every-transit gate never spends the sacred word 'attest completed' and never cheapens it.
4. The pipeline's earned geometry is GENERALIZED, not forked -- one extracted primitive, three doors, no per-door drift.
5. Almost the entire feature is a two-way door: the mechanism (verb + events + primitive) is reversible and never writes L1; only the doctrine-lawful promotion (FC-6) is one-way, and it is sequenced LAST behind a proven live NC.
What would have to be true for this to be right (WWHTBT), in order of shakiness: (a) gz ontology reach yields a seam-map complete/accurate enough that 'accounted' is meaningful -- the load-bearing condition; the body-seam gap concentrates the risk; (b) the section-5 NC genuinely cannot be forced (un-forced production, meta-validated); (c) the permissive end (permitted-entry) stays light enough that agents don't route around it yet present enough to still account -- the core tension; (d) 'account for a seam' is an act agents can perform reliably; (e) the pipeline geometry generalizes to the other doors without forking.

> **Calibration frontier (FC-2 tracer finding, operator-attested 2026-07-10).** WWHTBT-(a) is now concrete, not hypothetical. The FC-2 tracer proved the primitive's decision logic bites (the section-5 live NC PASSES un-forced: `outcome=PASS facade=0`), but the wired Stage-1 gate does not yet bite on a real OBPI entry: `gz ontology reach(<obpi-id>)` returns transitive *dependents*, of which a leaf OBPI has none, so `push_edges` is empty; and the gate does not pass `parent_invariants`, so `pull_edges` is empty. A real entry therefore computes an empty seam-map and always PROCEEDs. Determining what reach (and which pull edges) yield a *meaningful* seam-map at a real entry IS condition (a) -- deferred past the tracer. Until it lands, the Stage-1 call site is **diagnostic-only** (logs a NO-GO, never `SystemExit(3)`) so a mis-calibrated gate cannot 2am-wall a real pipeline (§ Negative #5). The FC-2 landing keystone is the proven *mechanism*, not a calibrated production gate; calibration is a named successor increment.

### Negative

1. Theater (the load-bearing pre-mortem): seam-maps rubber-stamped, GO always reached, the section-5 NC mocked rather than real -- the membrane exists but does not bite. Mitigation hardened into the landing keystone: the live NC runs un-forced through the section-5 meta-validator (ADR-0.0.74), and ALL deferred breadth (mx / permitted-entry / doctrine-lawful) is gated behind the NC biting live.
2. Body-blindness / laundered blind spot (assumption-surfacing): the tool computes EDGE-seams only, so an intra-body refactor that preserves every edge but reshapes a region sails through 'accounted' -- worse than before because it is now TRUSTED (the 'unaccounted refactoring smuggled inside a build/fix' failure, section-4). Mitigation: bodies = the DECLARED Allowed Paths (operator intent, L1), not a statistical inference; undeclared-body auto-detection is a future L3-ADVISORY enrichment (networkx-community), explicitly kept OUT of the gating path.
3. Door drift: three doors could grow divergent airlock variants. Mitigation: one extracted primitive that the doors CALL, never fork (Boundary Invariant).
4. Ceremony-creep bypass: if permitted-entry grows heavy, agents route around it and the silent bypass returns. Mitigation: permissive calibration relative to the pipeline; the totality of the membrane is a first-class acceptance concern.
5. Operational (2am): a NO-GO the operator cannot diagnose. Mitigation (requirement, not nicety): the refusal names the exact un-accounted seam + provenance + a one-command re-sense to rule out stale L3, and the captain override is logged + revocable (ADR-0.29.0 precedent) -- never a 2am hard wall.
6. The doctrine-lawful promotion (FC-6) is the one true one-way door: un-drafting a lawful North Star is costly. Mitigation: it is sequenced LAST and does not fire until the tracer + live NC have earned it.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **The airlock never writes L1 canon.** Every encounter is logged to the L2 ledger (L3
   recomputes from L1+L2); the airlock only PROPOSES L1 amendments for governed attestation.
   No airlock path mutates an ADR, invariant, or canon surface directly — canon changes by
   attestation alone (state-doctrine).
2. **The gate fires on every entry; the reason/door selects ceremony weight, never whether
   the gate fires.** No entry-reason, blast radius, or door may set the gate to "skip." (The
   structural parallel to the Gate Covenant: kind/lane select *which* gates fire, never
   *whether* Gate 5 fires.)
3. **The airlock gate is acknowledge-and-decide, never completion attestation.** Gate-5
   completion attestation fires only where completed planned work exists to certify (the
   pipeline's Stage 4/5). The airlock's every-transit gate is never emitted or recorded as a
   completion attestation — this preserves the force of the sacrosanct word.
4. **An un-accounted seam makes GO structurally unreachable.** With a real push/pull edge
   present and absent from the declared seam-set, no path reaches GO (the section-5 live
   negative control, un-forced production; its behavioral proof lands in FC-2).
5. **Discovered correction routes as a fresh transit.** Work discovered mid-sortie is never
   smuggled into the current transit; airlock-OUT recommends a fresh transit through the
   appropriate door ("better housekeeping/bookkeeping").
6. **The L3 ontology projection informs the gate; it never gates.** The sonar ping is
   advisory input to the acknowledge-and-decide decision; no `gz validate` scope, gate, or
   closeout step consumes the airlock's L3 seam-map as fail-closing enforcement evidence
   (state-doctrine Rule 5).

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Airlock-IN's ping consumes the HULL sonar (`gz ontology reach`), which is present (green now — anchors the reach dependency) | uv run gz ontology reach ADR-0.32.0-gzkit-ontology | 0 |
| Airlock-IN computes the seam-map and reaches a go/no-go at the pipeline door | uv run gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run | 0 |
| The section-5 enforcement floor verifies the airlock-in-unaccounted-seam live NC (registered by OBPI-02) among its passing claim set | uv run gz validate --qc-binding | 0 |
| Airlock-OUT emits the drift-diff and logs to L2 at the pipeline exit | uv run gz airlock out --target OBPI-0.33.0-01 --dry-run | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 8
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] Data model + ledger events: Pydantic SeamEdge (kind push|pull; provenance LAW|OBSERVED, non-erasable per state-doctrine section-2 guard), SeamMap (two-layer: bodies = declared regions + push/pull edges + unaccounted), Preflight (seam_map, blast_radius=delegation dial, authority captain|delegated, decision), DriftDiff (drift, verdict, resolutions) + airlock_in / airlock_out L2 event schemas under src/gzkit/schemas/. [SUPPORT; MVP spine]
- [ ] Airlock-IN primitive: declare(intent+expectation) -> ping(gz ontology sense/reach) -> reconcile(L1<->L3 vs plan assumptions -> refresh L3 + re-plan) -> acknowledge-and-decide gate; two-layer seam-map (bodies = declared Allowed Paths, push from reach, pull from brief + parent-ADR invariants); section-5 @enforces claim + live NC (un-accounted seam -> GO structurally unreachable, un-forced production); diagnostic refusal (names seam + provenance + one-command re-sense) + logged/revocable captain override; wired into pipeline Stage 1. [BEHAVIOR; MVP spine; landing keystone -- gates all deferred breadth]
- [ ] Airlock-OUT primitive (co-equal): drift-diff push-minus-pull -> findings + recommendations -> decision menu (leave-it-be | modify | repair | adjust-maps) -> fresh-transit routing for discovered correction -> log to L2; wired into pipeline Stage 5. [BEHAVIOR; MVP spine]
- [ ] mx door: wire airlock enter/exit into gz mx enter/exit (corrective-scoped ceremony). [BEHAVIOR; gated-breadth]
- [ ] permitted-entry door (new surface): the ad-hoc/spurious entry -- reconnaissance-first, light-repair-at-most, permissive ceremony; closes the silent-bypass hole; a discovered need beyond light repair trips a fresh transit through pipeline/mx. [BEHAVIOR; gated-breadth]
- [ ] Doctrine made lawful (section-8 gate): promote work-phases-and-airlock.md + four-phases-of-work.md from Draft North Star to binding, including the section-2 seam = BODY-and-BOUNDARY widening; register the section-5 @enforces claim binding. [STRUCTURAL-FENCE; the one-way door -- sequenced last, behind the proven NC]

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-07-08T05:17:29.647999*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.33.0-airlock-membrane

### Q: What is the title of this ADR?

**A:** the airlock — entry/exit membrane for agent sorties

### Q: What is the semantic version?

**A:** 0.33.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** An agent cannot hold a model of the project resident across sorties -- operator verbatim: 'the model's inability to retain a model of the project without having to reconstruct it on each sortie.' Unable to hold the whole picture, it patches locally, perturbs laterally, and discovers the damage late (the 'prior ecosystems of upsets'). gzkit governs artifacts (vertical traceability) and execution (the OBPI pipeline) well, but there is no membrane on ENTRY into the project ecosystem. This ADR builds that membrane -- the airlock -- as prosthetic memory: on the way IN it pings the shape and reconciles the agent's expectation against reality so the model need not hold everything (the seam-map IS the externalized working set); on the way OUT it accounts for what was disturbed and updates the maps, so map-maintenance becomes an unavoidable byproduct of any work rather than a separate chore (Architectural Boundary #4). The governing principle is the operator's, verbatim: 'The airlock fires because an agent is entering the project ecosystem -- full stop. The reason for entry selects the door; it never decides whether the airlock fires.' Three entry-reasons, three doors: pipeline (design implementation -- intentional change), mx/ghi (defect repair -- correction to a desired state), and permitted-entry (ad-hoc/spurious -- reconnaissance for comprehension with light repair at most, bracketing action: upstream of planning and downstream of action). The pipeline already IS an airlock silhouette (Stage 1 pre-flight, Stage 5 exit); mx has an enter-gate; but ad-hoc entry crosses no membrane at all -- the silent-bypass surface. This ADR names what the pipeline already does, extracts it as a reusable primitive, and closes the bypass. It also makes work-phases-and-airlock.md and four-phases-of-work.md lawful -- the campaign's Movement III section-8 '1.0 gate' -- and binds the section-5 enforcement-claim primitive (un-accounted seam -> real entry -> assert refuses GO).

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Extract ONE symmetric airlock primitive (airlock-IN + airlock-OUT, co-equal 'same shape both ways') FROM the pipeline's already-proven Stage-1 (pre-flight) / Stage-5 (exit) geometry -- the pipeline is the canonical door and the calibration reference (operator: the airlock 'was written with the pipeline in mind'; section-7 apparatus scan: 'the process that had MOST earned its keep'). mx and permitted-entry adapt to the airlock; the airlock is never forked per-door. AIRLOCK-IN is a three-beat, not a single compute: (1) DECLARE intent + expectation; (2) PING the shape via the HULL sonar (gz ontology sense/reach) -- state-doctrine Rule 5: the L3 projection INFORMS, it never DECIDES; (3) RECONCILE the ping against the assumptions the plan permitted -> refresh the L3 map + re-plan; then the gate. AIRLOCK-OUT (co-equal): drift-diff push-minus-pull -> findings + recommendations -> a decision menu (leave-it-be | modify | repair | adjust-maps) -> route any discovered correction as a FRESH transit through the right door (never smuggled inline; 'better housekeeping/bookkeeping') -> log to L2. The gate is ACKNOWLEDGE-AND-DECIDE (proceed | pause | hold | revert), a DIFFERENT sort of operator input from Gate-5 completion attestation ('we are at a gate; here is the current reality we've found -- acknowledge it and its impact, then proceed, OR acknowledge and pause/hold/revert'); keeping the two distinct PRESERVES the force of the sacrosanct completion-attestation. The gate is universal in nature, variable in execution: ceremony scales by door (pipeline tight; mx corrective; permitted-entry permissive), calibrated to the pipeline; blast_radius is the DELEGATION dial (small+fully-accounted may auto-proceed, logged), never a responsibility dial -- the captain owns every outcome. State-doctrine boundary (fail-closed by BI): the airlock ALWAYS logs what it encounters to the L2 ledger (L3 recomputes from L1+L2); it NEVER rewrites L1 canon -- it reports findings and proposes governed, attested amendments only. The seam-map carries BOTH senses of 'seam' (operator refinement): seam-as-BODY (a contiguous region of similarity = the FOOTPRINT; for the pipeline door these are the OBPI brief's DECLARED Allowed Paths, not an inferred guess) and seam-as-BOUNDARY (the push/pull edges = the join). PUSH edges come from gz ontology reach (computed blast radius); PULL edges from the brief + parent-ADR invariants. An un-accounted seam makes GO STRUCTURALLY UNREACHABLE -- the airlock blocks until the declarer accounts for it, then the captain/delegate decides (the section-5 live negative control: omit a real reach push edge from a real entry, un-forced production, assert GO cannot be reached). Tracer-first (KEEL/ADR-0.31.0 discipline): the FIRST slice is the PIPELINE door, in+out co-equal, piercing declare->ping->reconcile->gate->L2 and drift-diff->decision->L2, with the section-5 @enforces live NC as the landing keystone; mx, permitted-entry, and the doctrine-lawful promotion are gated-breadth OBPIs that do not begin until the NC bites live. Diagnostic refusal is a requirement, not a nicety (2am finding): a NO-GO names the exact un-accounted seam + its provenance + a one-command re-sense to rule out stale L3, and any captain override is LOGGED and revocable (ADR-0.29.0 witnessed-override precedent). NO new runtime dependency: the tracer stands on gz ontology reach (already-attested HULL floor) + declared Allowed Paths + brief/ADR invariants; graspologic stays ruled out (3.13-incompatible; statistical inference has no place in a gating path); if undeclared-body auto-detection is ever built it is networkx.algorithms.community (already in the floor), strictly L3-advisory, never gating.

### Q: What good things result from this decision? List benefits.

**A:** 1. Prosthetic memory: the model no longer must reconstruct the whole project each sortie -- it is HANDED the bounded seam-set on entry and accounts for exactly those. Map-maintenance becomes an unavoidable byproduct of any work, so the map cannot go stale -- closing Architectural Boundary #4 ('do not let reconciliation remain a maintenance chore') structurally, stronger than a reconciliation cron.
2. The silent-bypass hole closes: ad-hoc/spurious entry (permitted-entry) finally crosses a membrane. A gate with a hole is not a gate; this makes the airlock total rather than mostly.
3. The attestation canon is PRESERVED, not diluted: the acknowledge-and-decide gate is a distinct sort from completion-attestation, so the every-transit gate never spends the sacred word 'attest completed' and never cheapens it.
4. The pipeline's earned geometry is GENERALIZED, not forked -- one extracted primitive, three doors, no per-door drift.
5. Almost the entire feature is a two-way door: the mechanism (verb + events + primitive) is reversible and never writes L1; only the doctrine-lawful promotion (FC-6) is one-way, and it is sequenced LAST behind a proven live NC.
What would have to be true for this to be right (WWHTBT), in order of shakiness: (a) gz ontology reach yields a seam-map complete/accurate enough that 'accounted' is meaningful -- the load-bearing condition; the body-seam gap concentrates the risk; (b) the section-5 NC genuinely cannot be forced (un-forced production, meta-validated); (c) the permissive end (permitted-entry) stays light enough that agents don't route around it yet present enough to still account -- the core tension; (d) 'account for a seam' is an act agents can perform reliably; (e) the pipeline geometry generalizes to the other doors without forking.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Theater (the load-bearing pre-mortem): seam-maps rubber-stamped, GO always reached, the section-5 NC mocked rather than real -- the membrane exists but does not bite. Mitigation hardened into the landing keystone: the live NC runs un-forced through the section-5 meta-validator (ADR-0.0.74), and ALL deferred breadth (mx / permitted-entry / doctrine-lawful) is gated behind the NC biting live.
2. Body-blindness / laundered blind spot (assumption-surfacing): the tool computes EDGE-seams only, so an intra-body refactor that preserves every edge but reshapes a region sails through 'accounted' -- worse than before because it is now TRUSTED (the 'unaccounted refactoring smuggled inside a build/fix' failure, section-4). Mitigation: bodies = the DECLARED Allowed Paths (operator intent, L1), not a statistical inference; undeclared-body auto-detection is a future L3-ADVISORY enrichment (networkx-community), explicitly kept OUT of the gating path.
3. Door drift: three doors could grow divergent airlock variants. Mitigation: one extracted primitive that the doors CALL, never fork (Boundary Invariant).
4. Ceremony-creep bypass: if permitted-entry grows heavy, agents route around it and the silent bypass returns. Mitigation: permissive calibration relative to the pipeline; the totality of the membrane is a first-class acceptance concern.
5. Operational (2am): a NO-GO the operator cannot diagnose. Mitigation (requirement, not nicety): the refusal names the exact un-accounted seam + provenance + a one-command re-sense to rule out stale L3, and the captain override is logged + revocable (ADR-0.29.0 precedent) -- never a 2am hard wall.
6. The doctrine-lawful promotion (FC-6) is the one true one-way door: un-drafting a lawful North Star is costly. Mitigation: it is sequenced LAST and does not fire until the tracer + live NC have earned it.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Data model + ledger events: Pydantic SeamEdge (kind push|pull; provenance LAW|OBSERVED, non-erasable per state-doctrine section-2 guard), SeamMap (two-layer: bodies = declared regions + push/pull edges + unaccounted), Preflight (seam_map, blast_radius=delegation dial, authority captain|delegated, decision), DriftDiff (drift, verdict, resolutions) + airlock_in / airlock_out L2 event schemas under src/gzkit/schemas/. [SUPPORT; MVP spine]
2. Airlock-IN primitive: declare(intent+expectation) -> ping(gz ontology sense/reach) -> reconcile(L1<->L3 vs plan assumptions -> refresh L3 + re-plan) -> acknowledge-and-decide gate; two-layer seam-map (bodies = declared Allowed Paths, push from reach, pull from brief + parent-ADR invariants); section-5 @enforces claim + live NC (un-accounted seam -> GO structurally unreachable, un-forced production); diagnostic refusal (names seam + provenance + one-command re-sense) + logged/revocable captain override; wired into pipeline Stage 1. [BEHAVIOR; MVP spine; landing keystone -- gates all deferred breadth]
3. Airlock-OUT primitive (co-equal): drift-diff push-minus-pull -> findings + recommendations -> decision menu (leave-it-be | modify | repair | adjust-maps) -> fresh-transit routing for discovered correction -> log to L2; wired into pipeline Stage 5. [BEHAVIOR; MVP spine]
4. mx door: wire airlock enter/exit into gz mx enter/exit (corrective-scoped ceremony). [BEHAVIOR; gated-breadth]
5. permitted-entry door (new surface): the ad-hoc/spurious entry -- reconnaissance-first, light-repair-at-most, permissive ceremony; closes the silent-bypass hole; a discovered need beyond light repair trips a fresh transit through pipeline/mx. [BEHAVIOR; gated-breadth]
6. Doctrine made lawful (section-8 gate): promote work-phases-and-airlock.md + four-phases-of-work.md from Draft North Star to binding, including the section-2 seam = BODY-and-BOUNDARY widening; register the section-5 @enforces claim binding. [STRUCTURAL-FENCE; the one-way door -- sequenced last, behind the proven NC]

### Q: What alternatives were considered and why were they rejected?

**A:** Generic 'gz airlock' verb as the primary surface (REJECTED): the airlock was designed FOR the pipeline (operator, verbatim: no mistake it 'was written with the pipeline in mind') -- the pipeline is the canonical door and the calibration reference; a generic verb demotes the origin to an afterthought and invites the doors to drift. The primitive is EXTRACTED from the pipeline; the other doors adapt to it. Embed-per-door with no shared core (REJECTED): three doors each with their own pre-flight would drift apart -- the exact fragmentation the design exists to prevent; one extracted primitive the doors CALL is the anti-drift move. Permitted-entry (formerly 'hall pass') as the first tracer (REJECTED): greenfield-appealing and highest-value-gap, but the pipeline is the proven geometry and calibration reference; tracer-first belongs where the pattern has earned its keep, and the attested Phase-0/airlock-in reach already named the pipeline Stage-1/Stage-5 slice. Fold the airlock gate into KEEL's state-machine transitions (REJECTED): the airlock is an ENTRY-MEMBRANE concern orthogonal to OBPI LIFECYCLE-STATE; conflation overloads the state machine -- new airlock_in/airlock_out events, witnessed by but distinct from the ADR-0.31.0 TransitionMonitor (the airlock GO can be a precondition witness, not a transition). Call the airlock gate an 'attestation' (REJECTED -- doctrine violation): completion-attestation is sacrosanct and reserved for claims about completed planned work; the airlock's every-transit gate is acknowledge-and-decide, a different sort -- conflating them would spend and cheapen the sacred word. graspologic for body-seam / community detection (REJECTED, and previously ruled out): 3.13-incompatible (graphify #290) AND a category error -- statistical inference has no place in a gating path; if undeclared-body detection is ever built it is networkx.algorithms.community (already in the attested floor), strictly L3-advisory, never gating. Airlock-OUT as a thin / deferred afterthought (REJECTED): the operator ruled airlock-IN and airlock-OUT CO-EQUAL ('same shape both ways'); the exit membrane is first-class design, not a stub bolted after in.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

Generic 'gz airlock' verb as the primary surface (REJECTED): the airlock was designed FOR the pipeline (operator, verbatim: no mistake it 'was written with the pipeline in mind') -- the pipeline is the canonical door and the calibration reference; a generic verb demotes the origin to an afterthought and invites the doors to drift. The primitive is EXTRACTED from the pipeline; the other doors adapt to it. Embed-per-door with no shared core (REJECTED): three doors each with their own pre-flight would drift apart -- the exact fragmentation the design exists to prevent; one extracted primitive the doors CALL is the anti-drift move. Permitted-entry (formerly 'hall pass') as the first tracer (REJECTED): greenfield-appealing and highest-value-gap, but the pipeline is the proven geometry and calibration reference; tracer-first belongs where the pattern has earned its keep, and the attested Phase-0/airlock-in reach already named the pipeline Stage-1/Stage-5 slice. Fold the airlock gate into KEEL's state-machine transitions (REJECTED): the airlock is an ENTRY-MEMBRANE concern orthogonal to OBPI LIFECYCLE-STATE; conflation overloads the state machine -- new airlock_in/airlock_out events, witnessed by but distinct from the ADR-0.31.0 TransitionMonitor (the airlock GO can be a precondition witness, not a transition). Call the airlock gate an 'attestation' (REJECTED -- doctrine violation): completion-attestation is sacrosanct and reserved for claims about completed planned work; the airlock's every-transit gate is acknowledge-and-decide, a different sort -- conflating them would spend and cheapen the sacred word. graspologic for body-seam / community detection (REJECTED, and previously ruled out): 3.13-incompatible (graphify #290) AND a category error -- statistical inference has no place in a gating path; if undeclared-body detection is ever built it is networkx.algorithms.community (already in the attested floor), strictly L3-advisory, never gating. Airlock-OUT as a thin / deferred afterthought (REJECTED): the operator ruled airlock-IN and airlock-OUT CO-EQUAL ('same shape both ways'); the exit membrane is first-class design, not a stub bolted after in.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.33.0 | Pending | | | |
