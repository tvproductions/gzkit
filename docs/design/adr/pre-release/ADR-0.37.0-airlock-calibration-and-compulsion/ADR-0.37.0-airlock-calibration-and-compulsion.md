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

> **Amended 2026-08-15.** D1 and D2 below are the REVISED decisions; D1's original
> inverse-reach form is withdrawn on measurement. The `## Q&A Transcript` further down
> preserves the 2026-08-14 authoring interview UNEDITED and therefore still records the
> original D1/D2 — it is a historical record, not current decision text. Where the two
> disagree, this section governs. See § Amendment 2026-08-15 for the measurements, the
> two independent reviews that forced the revision, and the operator rulings.

Sequenced calibrate-then-compel. Widening an uncalibrated gate installs more inert gates (ADR-0.33.0 Negative #1, the load-bearing pre-mortem: 'seam-maps rubber-stamped, GO always reached'); calibrating without compelling leaves a sharp gate nobody walks through.

D1 -- A SEAM IS DECLARED LAW THE WORK MAY BREACH (revised 2026-08-15). The PULL arm is load-bearing; the PUSH arm is not its equal. Thread `parent_invariants` from the parent ADR's `## Boundary Invariants` section through all FIVE `airlock_enter` call sites -- `pipeline_runtime.py:590` and `:592`, `commands/permitted_entry.py:243`, `commands/mx_cmd.py:108`, and `commands/airlock.py:95`. The fifth backs `gz airlock in` and is the door this ADR's own Fidelity Assertions measure through; an implementation scoped to "all four" leaves the observing door unthreaded and reports `pull: 0` after calibration lands. The ELEMENT of `parent_invariants` is ONE NUMBERED INVARIANT of that section, and its identity for accounting is the `OBPI-NN` binding token, never the prose (D2) -- so no paragraph is ever carried into an L2 `SeamEdge.target`.

The ORIGINAL D1 proposed inverting `reach` so push edges became what the target depends on. It is WITHDRAWN on measurement, not argument. Measured 2026-08-15 against the live projection: `reachable_from(<OBPI>)` returns `[]` -- the confirmed cause of the 20-of-23 empty maps -- and the proposed inverse returns exactly `{<parent ADR>, PRD-GZKIT-1.0.0}`, IDENTICAL for `OBPI-0.37.0-01`, `-02` and `-05`, because the ancestors of an OBPI are its lineage chain: a function of the artifact tree alone. **A blast-radius proxy must vary with the change; artifact lineage cannot.** The predicate then auto-accounts the first of the two -- the parent ADR id occurs 11 times in a scaffold brief by construction -- leaving `PRD-GZKIT-1.0.0` as a single content-free constant seam on every entry in the repo. Inverting reach converts an EMPTY seam-map into a CONSTANT one: it satisfies a non-emptiness assertion while deciding nothing, which is ADR-0.33.0 § Negative #1 reproduced inside its own repair.

`SeamKind.PUSH` REMAINS in the model and is NOT deleted. ADR-0.33.0's attested checklist commits to it (`SeamEdge (kind push|pull …)` [SUPPORT]; `push from reach` [BEHAVIOR]) and BI #4 speaks of "a real push/pull edge". What ADR-0.33.0 DEFERRED is which source yields a meaningful map -- verbatim: *"Determining what reach (and which pull edges) yield a meaningful seam-map at a real entry IS condition (a)"*. Choosing a different source is inside that deferral; deleting the edge kind would not be. The push arm stays structurally present and carries NO calibrated source in this ADR. A file-coupling source was priced and is deferred WITH AN OWNER in § Alternatives Considered -- never left open.

D2 -- INVERT THE ACCOUNTING PREDICATE, DO NOT MERELY TIGHTEN IT (revised 2026-08-15). `_reconcile` computes `accounted = inv in brief_text` (`src/gzkit/airlock/enter.py:146`), a raw substring test over the whole brief. Narrowing it to the brief's declarative sections -- the original D2 -- does not fix the defect, because the defect is DIRECTION, not SCOPE: under any substring rule the brief accounts for a seam by NAMING it, and the brief is a file the entering agent controls. The cheapest way to clear six invariants would be to paste six headings. Retire the substring test. An invariant is accounted for an entry iff EITHER arm holds:

* **Arm 1 -- the parent binds it.** The parent ADR's `## Boundary Invariants` section names this OBPI against that invariant, in the `(OBPI-NN)` form `_fence_obpi_anchored` (`src/gzkit/req_kind_fence.py:43`) already parses. This arm is reused UNCHANGED, and it carries GHI #538's lesson in its own docstring: *"Heading presence alone is NOT proof -- an invariant list naming no OBPI cannot say which invariant proves which fence."* That is exactly the discipline the airlock's predicate lacked.
* **Arm 2 -- the brief fences it.** The brief carries a STRUCTURAL-FENCE REQ citing that invariant. This is the existing REQ-kind proof channel (ADR-0.0.59: STRUCTURAL-FENCE -> parent-ADR `## Boundary Invariants` entry), already validated by `gz validate --req-kind-discipline`, so the arm cannot be satisfied by prose.

Arm 1's binding lives in the PARENT, which the entering work does not own; Arm 2 is real authoring work with an existing validator behind it. Neither is clearable by paste. **Consequence, load-bearing:** no OBPI under this ADR may hold write access to its own parent ADR. All six briefs currently carry `…/ADR-0.37.0-…/**` in their allowlist, which would let an OBPI edit the very Boundary Invariants section that grants it accounting. Correcting those allowlists is a precondition of this predicate, not cosmetic hygiene.

This is coupled-surface correctness under AGENTS.md DO IT RIGHT 1a: D1 is what converts a latent defect into a live one, and 1a requires verifying the consumer's check in the same change.

D2a -- SEVERITY IS GRADUATED, AND STAGED (added 2026-08-15). Three outcomes, not two:

| Parent ADR state | Entry outcome |
|---|---|
| declares law; invariant accounted by Arm 1 or 2 | PROCEED |
| declares law; invariant unaccounted | **WARN now; HOLD after the § Flip Criteria threshold** |
| declares NO `## Boundary Invariants` section | PROCEED + a counted L2 warning naming the gap |

The third row exists because only **19 of 166** ADRs declare Boundary Invariants at all (measured 2026-08-15); a pure law seam is a no-op on the other ~88%, which would relocate ADR-0.33.0's inert gate rather than repair it. Holding there instead would put ~88% of entries at NO-GO on day one and make the override the default verb. Counting the absence makes the gap visible and countable without manufacturing that friction.

The second row ships WARN because the corpus is not ready: modeled across the 19 law-declaring ADRs, **89 of 93 entries (95%) would HOLD**, median ~4 unaccounted invariants, because invariants are rarely bound to an OBPI (ADR-0.37.0 itself binds 1 of 6). Shipping HOLD into that state is § Negative #1 by construction. WARN-then-flip against a written, measured threshold is the same staging D4 applies to the trailer gate, and it is *calibrate before widen* applied to the gate's own severity.

D3 -- COMPEL AT TWO GRANULARITIES. (a) A `Transit:` commit trailer on `src/**` and `tests/**` commits, producer-stamped by the door and validated by `gz validate`. This is the exact cumulative-with-a-floor shape of the existing `Task:` trailer invariant (.gzkit/rules/task-discovery.md), reusing its producer-stamped pattern, its validator and its scope rather than inventing a parallel mechanism. Commit granularity is chosen because the 525-commits/zero-transits failure is MEASURED in commits. (b) A session-entry door: SessionStart fires airlock-IN, and the handoff-resume-gate's surviving `Write|Edit|NotebookEdit` arm RETIRES INTO it. That arm is an improvisation of Movement B item 3 ('Session entry triggers the airlock'); removing it before the governed door exists would open a gap in front of the door, so the improvisation and the hole close in one move.

D4 -- WARN, THEN FLIP ON WRITTEN EVIDENCE. Both gates ship warning-only and flip fail-closed in OBPI-06 OF THIS SAME ADR, against the thresholds in **§ Flip Criteria** below -- which are now WRITTEN, with measured baselines, rather than referenced. Staging precedent is OBPI-0.0.41-02 -> -03. The flip is an OBPI inside this ADR rather than a successor promise, so the ADR cannot reach 6/6 while carrying a warning-only gate. This is deliberate: an unowned deferral inside an attested artifact is the exact failure ADR-0.33.0 demonstrates and GHI #804 was filed to prevent.

**Correction, 2026-08-15.** Until this amendment the three sites above claimed a criterion "written into the ADR body" and Positive #6 asserted "the flip criterion is written and owned" -- and NO criterion text existed anywhere in the file. All four mentions were references to an unauthored text, so the ADR's own structural defence against reproducing GHI #804's defect was itself an unowned deferral. The claim that "the criterion is owned by GHI #804 independently" is also withdrawn: #804 asks that a deferred frontier NAME an owner; it does not supply this ADR's numeric thresholds. § Flip Criteria discharges both.

EXPLICITLY OUT OF SCOPE. (i) Reopening ADR-0.33.0 or editing any of its attested REQ text. (ii) The 23-in/5-out transit accounting gap: it remains a Movement B checkbox because it is a PAIRED-EVENT defect shared with `session_exit` (38 skips / 0 writes) and the resume gate's former 160 lifts / 0 blocks, and that family deserves one disposition rather than three. (iii) Widening to Movement B's remaining doors -- the whole ruling was calibrate before widen.

## Consequences

### Positive

1. The gate becomes capable of holding ON LAW. A leaf OBPI entry under a law-declaring parent yields pull edges that a brief must account for by BINDING or FENCING, not by naming -- converting the measured 20-of-23 vacuous PROCEEDs into decisions with a remedy. **Non-emptiness is explicitly NOT the claim** (amended 2026-08-15): the withdrawn D1 would have produced a non-empty map that decided nothing, so "yields a non-empty seam-map" is no longer offered as a benefit and is no longer what the Fidelity Assertions measure.
2. The 525-commits/zero-transits number becomes both visible and, after the flip, structurally impossible -- measured at the same granularity it was observed.
3. A latent accounting defect is closed at the moment it becomes load-bearing, rather than after it has silently accounted for real seams.
4. The handoff-resume-gate improvisation is retired into a governed door, closing the last forked variant of the airlock's decision grammar without opening a gap.
5. ADR-0.33.0's attestations remain honest and untouched; the residual is re-homed rather than the ADR reopened.
6. The flip criteria are written IN THIS FILE with measured baselines (§ Flip Criteria), so the deferral this ADR repairs cannot recur inside the repair itself. **Amended 2026-08-15:** as originally authored this claim was FALSE -- no criterion text existed anywhere in the file, and the sentence asserted its own contents.
7. The accounting predicate cannot be self-granted. Both arms bind through a surface the entering work does not own (the parent's `## Boundary Invariants`) or one an existing validator already checks (`gz validate --req-kind-discipline`), so "account for a seam" stops being an act of narration -- WWHTBT-(d) from ADR-0.33.0, which asked whether that act can be performed reliably.
8. Two existing primitives are reused rather than invented: `_fence_obpi_anchored` supplies the binding grammar and the STRUCTURAL-FENCE channel supplies the brief-side proof. This carries GHI #538's naming-is-not-proof lesson into the airlock instead of relearning it there.
9. The ~88% of ADRs that declare no law stop being invisible. Today they are indistinguishable from compliant entries; under D2a they emit a counted L2 warning, which is the evidence base for later flipping absence itself to a hold.

### Negative

1. OVERRIDE THEATER. If a calibrated entry presents many unaccounted edges at once, operators reach for CaptainOverride reflexively and the override becomes the new rubber stamp -- ADR-0.33.0 Negative #1 arriving through the override door instead of the empty-map door. **THE BOUND IS NOW STATED, and it is structural rather than a tuned constant** (amended 2026-08-15): pull edges are exactly the parent ADR's numbered `## Boundary Invariants`, an AUTHORED list, so the per-entry ceiling is that ADR's invariant count -- measured 1 to 10 across the 19 law-declaring ADRs, median 4 unaccounted per entry. No unbounded case exists by construction, which is the property the withdrawn coupling source could not offer (68-270 edges per brief, measured). OBPI-02's live NC asserts the per-entry pull-edge count never exceeds the parent's declared invariant count; it does NOT assert a magic number derived from a run of the code (AGENTS.md DO IT RIGHT #6). Override frequency is a tracked signal -- owned by checklist item 3, not asserted here without an owner.
2. THE FLIP MAY NOT LAND. OBPI-06 could stall, leaving a warning-only gate and reproducing ADR-0.33.0's failure one ADR later. Mitigated structurally: 6/6 is unreachable without it, and § Flip Criteria states the thresholds in this file so a successor session cannot invent them.
3. THE PUSH ARM CARRIES NO CALIBRATED SOURCE (revised 2026-08-15). This ADR calibrates LAW and leaves observed coupling uncalibrated: `SeamKind.PUSH` remains in the model per ADR-0.33.0's attested text, but nothing feeds it a source that varies with the work. So the question "what will this break?" is still unanswered -- only "what law might this breach?" is. The file-coupling source that answers it directly was measured (`coupling_edges`, 3947 edges already built; 68-270 per brief) and deferred as unbounded. **Deferred WITH AN OWNER, not open:** § Alternatives Considered names the owner and the bounding question it must answer first.
4. THE HOLD RATE IS 95% TODAY AND THE GATE SHIPS WARN BECAUSE OF IT. Modeled across the 19 law-declaring ADRs, 89 of 93 entries carry at least one unaccounted invariant. The design is therefore knowingly non-biting at landing, and the WARN window is a real exposure: if § Flip Criteria is never met, this ADR closes having built a gate that warns forever. That is the same shape as ADR-0.33.0's diagnostic-only Stage-1 call site, and it is why the flip is an OBPI in this ADR rather than a successor promise.
5. TRAILER FRICTION. A per-commit trailer adds a stamp to every src/** commit. Producer-stamping keeps it off the author, but a stamping failure becomes a commit-time failure. The producer is `.gzkit/hooks/prepare-commit-msg-task-trailers`, whose every failure path is a silent no-op -- correct for an advisory trailer, but pairing a silently-failing producer with a fail-closed validator strands the operator. OBPI-04 owns the recovery path, and § Flip Criteria gate 2 will not flip without it.
6. HISTORY IS ONE-WAY. After the flip, ~90 days of commits carry Transit: trailers; the gate is a flag and reverts cheaply, but the trailer data does not.
7. THE ENTRY-PREDICTION ASSUMPTION IS UNPROVEN. The design assumes a seam-map computed at ENTRY predicts what the work will disturb. If work routinely discovers its real blast radius mid-flight, the EXIT accounting is the load-bearing half -- and that is precisely the 23/5 gap this ADR scopes out.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

**This section is load-bearing twice.** It states the fences, and — because D1 threads
`parent_invariants` from the parent ADR's `## Boundary Invariants` — it is also the literal
source of the PULL edges every OBPI under this ADR will be gated against. An ADR-0.37.0 with
no Boundary Invariants section would give its own briefs empty pull edges, reproducing the
exact defect this ADR exists to repair.

**Every invariant below names the OBPIs it fences (amended 2026-08-15).** That is not
decoration: under D2 Arm 1 the `(OBPI-NN)` token IS the accounting grammar, so an invariant
naming no OBPI is unaccountable for every entry under this ADR. As originally authored this
section bound 1 of 6, which would have put all six of its own briefs at NO-GO on nearly
every invariant. An ADR that introduces this predicate and does not satisfy it is the
`gz validate --advisory-scorecard` "declared without mechanism" family arriving in the
repair itself.

1. **ADR-0.33.0 is never reopened and its attested text is never edited.**
   (OBPI-01, OBPI-02, OBPI-03, OBPI-04, OBPI-05, OBPI-06.) No OBPI here may
   modify a REQ, acceptance criterion, or attestation under `ADR-0.33.0-airlock-membrane`.
   The residual is RE-HOMED (the `ADR-0.0.37` → `ADR-0.35.0` precedent); reopening would
   drag a `Validated` ADR to `Pending` and retroactively falsify an honest attestation.
2. **One primitive; doors CALL and never fork.** Restated from ADR-0.33.0 (OBPI-05). The
   session-entry door added by OBPI-05 consumes `gzkit.airlock.enter.airlock_enter` and
   defines no local weight, profile, or decision grammar of its own — the
   `handoff-resume-gate` arm it retires was a forked variant, and retiring it must not
   create a second one. **Provenance corrected 2026-08-15:** this was labelled "inherited
   unchanged" but is NOT in ADR-0.33.0's numbered Boundary Invariants — it appears there
   only inside the § Negative #3 mitigation. It is restated here as a fence on its own
   authority, not carried as a borrowed number.
3. **The reason and the door select ceremony WEIGHT, never WHETHER the gate fires.**
   Restated from ADR-0.33.0 #5 (OBPI-05, OBPI-06). No entry reason, blast radius, door, or
   trailer state may set the gate to "skip". **Amended 2026-08-15:** reworded rather than
   inherited verbatim; where this wording and ADR-0.33.0's differ, ADR-0.33.0's governs for
   work under ADR-0.33.0.
4. **The L3 ontology projection INFORMS the gate and never IS the gate.**
   (OBPI-01, OBPI-02, OBPI-03.) Architectural Boundary 6. Calibration changes what the
   projection reports; it never promotes the projection to source-of-truth, and no gate
   decision may trace to Layer 3 alone.
5. **`gz git-sync` is never gated by any mechanism in this ADR.**
   (OBPI-04, OBPI-05, OBPI-06.) Standing operator ruling, verbatim: *"I EXPLICITLY want
   this"*, and *"handoffs should never, never, never, ever, block git-sync. NEVER."* The
   Transit: trailer gate and the session-entry door both exempt it unconditionally.
6. **No mechanism here may require a TTY, PTY, or interactive terminal.**
   (OBPI-04, OBPI-05, OBPI-06.) Operator canon at invariant tier. A refusal must be
   recoverable, and a human decision recordable, with no interactive transport available.
7. **The airlock never writes L1 canon.** (OBPI-01, OBPI-02, OBPI-03, OBPI-04, OBPI-05,
   OBPI-06.) **Restored 2026-08-15** — this is ADR-0.33.0's Boundary Invariant #1 and it was
   DROPPED when this ADR's list was authored. Every encounter is logged to L2; the airlock
   reports findings and proposes governed, attested amendments only. It is the most relevant
   fence for OBPI-04, which stamps into commit history, and for OBPI-05, which fires at
   session entry — precisely the two increments that were left ungated by the omission.
8. **The gate is ACKNOWLEDGE-AND-DECIDE, never a completion attestation.**
   (OBPI-05, OBPI-06.) **Restored 2026-08-15** — ADR-0.33.0's Boundary Invariant #3, also
   dropped. `proceed | pause | hold | revert` is a different act from Gate-5, and keeping
   the two distinct is what PRESERVES the force of the sacrosanct completion attestation.
   No transit decision may be recorded, rendered, or counted as a Gate-5 attestation.
9. **No OBPI may hold write access to the ADR that grants its accounting.**
   (OBPI-01, OBPI-02, OBPI-03, OBPI-04, OBPI-05, OBPI-06.) **Added 2026-08-15.** Under D2
   Arm 1 the parent's `## Boundary Invariants` section is the source of an entry's pull
   edges, so a brief that can edit its parent can grant itself accounting — the
   accounting-by-boilerplate anti-pattern with a larger hammer. No brief under this ADR may
   carry this ADR's own file, or a glob covering it, in its `allowlist`. All six briefs
   carried `…/ADR-0.37.0-…/**` at authoring; correcting that is a precondition of OBPI-02,
   not hygiene.

## Flip Criteria

**Added 2026-08-15.** D4 ships both gates warning-only and flips them fail-closed in
OBPI-06. Until this amendment D4, § Positive #6 and Checklist item 6 each referenced "a
criterion written into the ADR body" and **no such text existed** — the ADR's own defence
against reproducing GHI #804's unowned-deferral defect was itself an unowned deferral.
These are the thresholds. They are stated as MEASUREMENTS with baselines and a recompute
path, so a successor session reads them rather than inventing them.

### Gate 1 — pull-arm severity: WARN → HOLD

**Flip when the modeled would-hold rate across law-declaring ADRs falls below 25%** — that
is, at least three quarters of entries have every parent invariant either bound to them
(D2 Arm 1) or fenced by a STRUCTURAL-FENCE REQ (D2 Arm 2).

- **Baseline measured 2026-08-15: 95%** — 89 of 93 entries across the 19 ADRs that declare
  a `## Boundary Invariants` section carry at least one unaccounted invariant; median ~4,
  distribution 0:4, 1:8, 2:13, 3:11, 4:14, 5:3, 6:11, 7:2, 8:11, 9:11, 10:5.
- **Recompute:** enumerate every OBPI under an ADR carrying a `## Boundary Invariants`
  section; for each, count invariants whose text names neither that OBPI (via the
  `_fence_obpi_anchored` grammar) nor a STRUCTURAL-FENCE REQ in its brief. The rate is
  entries-with-≥1-unaccounted over entries-modeled. OBPI-03 owns landing this as a
  runnable count; the figure is fenced by that recompute and **never transcribed** (the
  GHI #768 ruling on this exact class: *stop writing the number down*).
- **Why 25% and not 0%:** requiring zero would make the flip hostage to a single unbound
  invariant anywhere in the corpus, which is a hostage the corpus can always take. 25%
  leaves headroom for genuinely new ADRs authored between the measurement and the flip.

### Gate 2 — Transit: trailer gate: WARN → HOLD

**Flip when BOTH hold:** (a) ≥90% of `src/**` and `tests/**` commits in a trailing 30-day
window carry a door-stamped `Transit:` trailer, and (b) the stamp-failure recovery path
(§ Negative #5) is landed and exercised — an operator whose stamp silently no-ops must be
able to recover without knowing a transit id.

- **Baseline measured 2026-08-15: 0%** — 525 `fix` commits in 90 days across zero transits.
- **Why the (b) conjunct is not optional:** the trailer producer's every failure path is a
  silent no-op, which is correct for an advisory trailer and strands the operator under a
  fail-closed validator. Flipping on (a) alone converts a silent producer failure into an
  unrecoverable commit refusal.
- **Threshold (a) is AGENT-PROPOSED and awaits operator ratification.** Gate 1's 25% was
  ratified in the 2026-08-15 design dialogue; this number was not put to the operator and
  is recorded as a draft, not a ruling.

### What neither gate may be

Neither gate may flip on elapsed time, on a count of landed OBPIs, or on an agent's
judgment that "the corpus looks ready". Each names a measurement with a baseline and a
recompute path; a flip proposed on any other evidence is the defect this section exists
to prevent.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

Each row is RED today and goes green as its owning OBPI lands.

**Rows 2 and 2b are the ADR's thesis, and they are a DIFFERENTIAL PAIR (amended
2026-08-15).** The original row 2 asserted `d['push'] or d['pull']` — non-emptiness — which
is exactly what the withdrawn D1 would have satisfied while deciding nothing, and it was
ALSO a disjunction under a decision whose own text said "both arms are required", so it
could go green with only one arm wired. **Non-emptiness cannot distinguish a gate that
bites from a constant that does not.** A differential can: the same command must PROCEED on
an entry whose law is accounted and HOLD on one whose law is not. Baseline measured live
2026-08-14 on a real OBPI: `"push": 0, "pull": 0, "unaccounted": 0, "decision": "proceed"`.

| Claim | Command | Expected exit |
|-------|---------|---------------|
| `parent_invariants` reaches the OBSERVING door — `gz airlock in` computes one pull edge per declared invariant, count DERIVED from the parent, never transcribed (OBPI-01) | uv run python -c "import json,re,subprocess; from pathlib import Path; s=Path('docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md').read_text(encoding='utf-8'); sec=re.search(r'^## Boundary Invariants\b(.*?)(?=^## )', s, re.S\|re.M).group(1); n=len(re.findall(r'^\d+\. \*\*', sec, re.M)); d=json.loads(subprocess.run(['uv','run','gz','airlock','in','--target','OBPI-0.37.0-02-airlock-seam-calibration','--dry-run','--json'],capture_output=True,text=True).stdout)['seam_map']; raise SystemExit(0 if n and len(d['pull']) == n else 1)" | 0 |
| DIFFERENTIAL a — an entry whose parent BINDS its law to this OBPI reaches PROCEED (OBPI-02) | uv run python -c "import json,subprocess; d=json.loads(subprocess.run(['uv','run','gz','airlock','in','--target','OBPI-0.37.0-02-airlock-seam-calibration','--dry-run','--json'],capture_output=True,text=True).stdout); raise SystemExit(0 if d['decision'] == 'proceed' and not d['seam_map']['unaccounted'] else 1)" | 0 |
| DIFFERENTIAL b — the SAME primitive HOLDs when ONE invariant is unaccounted; GO is unreachable (OBPI-02, OBPI-03) | uv run python -c "from pathlib import Path; from gzkit.airlock.enter import airlock_enter; p=airlock_enter('OBPI-0.37.0-02-airlock-seam-calibration', Path('docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/obpis/OBPI-0.37.0-02-airlock-seam-calibration.md'), parent_invariants=('SENTINEL-UNBOUND-INVARIANT',)); raise SystemExit(0 if p.decision != 'proceed' else 1)" | 0 |
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

> **Items 1, 2 and 3 were re-scoped 2026-08-15** by the D1/D2 revision. The count stays at
> 6 and the 1:1 map to the six brief files on disk is unchanged; item 1 is REPURPOSED rather
> than withdrawn (operator ruling), so its brief keeps id `OBPI-0.37.0-01-ontology-inverse-reach`
> while its content becomes the invariant-threading work. **The slug now understates the
> item** — a rename is tracked debt, not an open question, and must go through
> `gz migrate-semver` because `obpi_created` for the current id is already in L2.

- [ ] OBPI-0.37.0-01 parent-invariant-threading -- thread parent_invariants from the parent ADR's `## Boundary Invariants` through all FIVE airlock_enter call sites, including commands/airlock.py:95 (the door `gz airlock in` uses, omitted from the original "all four"); the element is one numbered invariant, identified by its (OBPI-NN) binding token, never its prose
- [ ] OBPI-0.37.0-02 airlock-seam-calibration -- replace `accounted = inv in brief_text` with the two-arm predicate (parent binds the invariant to this OBPI via `_fence_obpi_anchored`, OR the brief carries a STRUCTURAL-FENCE REQ citing it); live NC asserts the DIFFERENTIAL pair -- accounted entry PROCEEDs, one unaccounted invariant makes GO unreachable -- and that per-entry pull edges never exceed the parent's declared invariant count
- [ ] OBPI-0.37.0-03 seam-accounting-predicate -- the graduated severity ladder: unaccounted law WARNs (pending the § Flip Criteria threshold), a parent declaring NO `## Boundary Invariants` section PROCEEDs and emits a counted L2 warning naming the gap; plus override-frequency tracking, so Negative #1's mitigation has an owner
- [ ] OBPI-0.37.0-04 transit-trailer-stamp -- door stamps the Transit: trailer; gz validate warns on src/** and tests/** commits lacking it; carries the stamp-failure recovery path (the producer's failure paths are silent no-ops today)
- [ ] OBPI-0.37.0-05 session-entry-door -- SessionStart fires airlock-IN; the handoff-resume-gate Write|Edit|NotebookEdit arm retires into it
- [ ] OBPI-0.37.0-06 transit-gate-flip -- flip items 3 and 4 fail-closed against § Flip Criteria; live NC asserts un-triggered entry makes the claim fail

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

> **Re-scored 2026-08-15.** Alternative 1 is now ADOPTED and alternative 2's rejection
> reason is replaced by a measurement. The original rejections were written before the
> seam sources had been measured; the numbers below are what changed the ranking.

1. KEEP DESCENDANTS, WIRE PULL ONLY. **ADOPTED 2026-08-15 (was REJECTED).** The original
   rejection read: *"a leaf OBPI still contributes zero push edges, so the gate bites on LAW
   while the observed-coupling arm stays exactly as inert as today. Half a calibration is an
   inert gate with better paperwork."* The premise was right and the conclusion inverted:
   inverting reach does NOT fix the observed-coupling arm — measured, it yields
   `{<parent ADR>, PRD-GZKIT-1.0.0}`, constant across OBPIs and half auto-accounted. Both
   candidate push sources were therefore inert-or-unbounded, so "bite on LAW" was never half
   a calibration against the other half; it was the only arm with a bounded, meaningful,
   already-built source. Note the original row 2 fidelity assertion would have certified
   THIS alternative as success while its own Decision text called it rejected — a
   disjunction (`push or pull`) under a decision demanding both arms.

2. SEAMS FROM FILE-LEVEL IMPORT COUPLING. Compute seams from who imports the brief's
   declared Allowed Paths, rather than from the ontology graph. **DEFERRED, WITH AN OWNER
   (re-scored 2026-08-15)** — not rejected on architecture. Measured: the index already
   exists (`.gzkit/ontology/source_anchors.json`, `coupling_edges`, 3947 edges) and it
   genuinely varies with the work (68, 98, 101, 248, 258, 270 direct-coupling neighbours
   across real briefs). It fails on BOUNDEDNESS, not on merit: a 270-edge seam-map is not
   reviewable, and § Negative #1's ceiling has no structural source there the way the
   parent's authored invariant list supplies one. **Owner: this alternative may be adopted
   only by an ADR that first answers the bounding question — which narrowing (depth, package
   granularity, or intersection with other in-flight work) yields a reviewable map — and
   states the resulting ceiling as a measurement.** It is named here so the push arm's
   uncalibrated state (§ Negative #3) has a destination rather than an open frontier, which
   is the GHI #804 discipline applied to this ADR's own residual.

2a. SEAMS FROM BRIEF TERRITORY OVERLAP. Compute seams from which OTHER briefs claim
   overlapping Allowed Paths — governance-native, answering "who else owns this ground".
   **REJECTED on measurement 2026-08-15:** median 86 co-claimants per brief, max 173 of 174,
   because allowlists are `src/gzkit/**`-coarse. The signal is real but unusable until
   allowlist tightening lands corpus-wide, which is a far larger campaign than this ADR and
   is not a prerequisite anyone has scoped.

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

## Amendment 2026-08-16 — OBPI-01's slug corrected to match its repurposed content

**Rename debt from the 2026-08-15 amendment, discharged.** That amendment repurposed
OBPI-01 rather than withdrawing it (operator ruling: *"Book it, but repurpose OBPI-01"*),
keeping six OBPIs and the Feature Checklist 1:1 with the briefs on disk — and accepted the
resulting slug/content mismatch as tracked debt. The brief threads `parent_invariants`,
which is the PULL arm; `ontology-inverse-reach` named the PUSH-arm design that amendment
**withdrew on measurement**. The id therefore advertised the one thing the brief had stopped
doing, and a slug is what `rg` finds.

`OBPI-0.37.0-01-ontology-inverse-reach` → **`OBPI-0.37.0-01-parent-invariant-threading`**,
recorded as a forward `artifact_renamed` event (the ledger is append-only; nothing was
rewritten). Renamed on the **live decision surfaces only** — the brief and the Feature
Checklist. The `## Q&A Transcript` above still says `ontology-inverse-reach` and **is
correct as it stands**: that section is declared preserved UNEDITED, it records the
2026-08-14 interview in which OBPI-01 genuinely *was* the inverse-`reach` work, and
rewriting a primary source to match a later decision is exactly what the preservation rule
forbids. `EVALUATION_SCORECARD.md` and `EVALUATION_SUBSTANCE.md` likewise keep the old slug
because they are dated measurements of the brief set as it stood.

**A latent defect surfaced doing this and was fixed in the same change.**
`orphaned_obpi_ids` resolved `artifact_renamed` chains for an OBPI's *parent* but not for
the OBPI *itself*, so a renamed brief read as a deleted one and `gz check` fail-closed on an
honest rename. It had never fired because the census short-circuits on disposition and every
previously renamed OBPI was already terminal or completed; an undisposed `Draft` brief is
the first shape that can reach the arm. Fixed at `src/gzkit/obpi_lifecycle.py` with a
covering test family, per AGENTS.md DO IT RIGHT 1a — the consumer's check verified in the
same commit as the change that made it reachable.

## Amendment 2026-08-15 — D1 withdrawn on measurement; the seam is declared law

**Status when amended:** `Draft`, 0/6, unattested. No Gate-5 attestation exists to falsify,
so this is an in-place revision of a Draft ADR, not a re-homing and not a repudiation.

**What forced it.** The ADR was authored and self-scored by one session in a single pass;
its own `EVALUATION_SCORECARD.md` records `DISPATCH MODE: SINGLE-DRIVER — 0 of 3 mandated
personas produced receipted independent input`, with both substance dimensions `UNGRADED`.
The operator ruled that gap closed before the six briefs were authored. Both mandated
Step-2 personas were then dispatched and **both returned FAIL, independently**. The
decisive finding was measured rather than argued.

**The measurements (2026-08-15, live, re-runnable — do not transcribe, recompute):**

| Claim | Measured |
|---|---|
| `reachable_from(<OBPI>)` — today's push source | `[]` for every OBPI tested — the confirmed cause of the 20-of-23 empty maps |
| Proposed inverse (ancestors) | exactly `{<parent ADR>, PRD-GZKIT-1.0.0}` — IDENTICAL for OBPI-01, -02, -05 |
| Parent ADR id in a scaffold brief | 11 occurrences → auto-accounted by `inv in brief_text` |
| `PRD-GZKIT-1.0.0` in a scaffold brief | 0 occurrences → one constant unaccounted seam, repo-wide |
| File-coupling alternative (`coupling_edges`, already built) | 3947 edges; 68–270 per brief — varies with the work, but unbounded |
| Brief-territory-overlap alternative | median 86 co-claimants, max 173 of 174 — swamped by coarse `src/gzkit/**` allowlists |
| ADRs declaring `## Boundary Invariants` | 19 of 166 |
| Modeled hold rate under the new predicate | 89 of 93 entries (95%), median ~4 unaccounted |

**Operator rulings booked in the dialogue.** (1) A seam is *declared law the work may
breach* — the pull arm is load-bearing, the push arm is not its equal. (2) Severity is
graduated: HOLD on unaddressed law, WARN where the parent declares none. (3) The brief
earns accounting through a STRUCTURAL-FENCE REQ as a second arm, and severity is staged
WARN→HOLD against a written criterion. (4) OBPI-01 is REPURPOSED, not withdrawn, keeping
six OBPIs and the checklist 1:1 with the briefs on disk.

**Claims corrected, not merely revised.** Three statements the artifact made about its own
contents were false and are recorded here rather than silently overwritten: *"the flip
criterion is written and owned"* (no criterion existed — § Flip Criteria now supplies it);
*"all four call sites"* (there are five; `commands/airlock.py:95`, the door this ADR's own
fidelity commands measure through, was omitted); and *"Inherited unchanged from ADR-0.33.0"*
on Boundary Invariants #2 and #3 (#2 is not in ADR-0.33.0's numbered list at all, #3 was
reworded). ADR-0.33.0's Boundary Invariants #1 and #3 had also been DROPPED and are restored
here as #7 and #8 — the two most relevant to OBPI-04 and OBPI-05, the increments the
omission left ungated.

**What this amendment does NOT do.** It does not reopen ADR-0.33.0 or touch its attested
text. It does not delete `SeamKind.PUSH`, which ADR-0.33.0's attested checklist commits to;
it changes only the source feeding it, which is inside the calibration frontier ADR-0.33.0
explicitly deferred. It does not disturb D3's compulsion design, which was out of the
dialogue's scope. Repairs still owed from the two reviews and deliberately NOT folded in
here — `airlock_exit` carrying the identical empty-`parent_invariants` defect, the six
briefs' allowlists and their tautological `verification:`, and missing REQ-kind tags on the
checklist items — are carried as tracked work, not as silent scope.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.37.0 | Pending | | | |
