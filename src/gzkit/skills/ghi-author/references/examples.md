# ghi-author — worked examples

Reference material for `ghi-author`, extracted from `SKILL.md` when the skill
body reached the `SKILL_BODY_MAX_LINES` ceiling in `gzkit.skill_contract`.
These are orientation reading, not per-invocation procedure: the binding steps,
constraints and red flags stay in `SKILL.md`.

### Example 1 — Correction within the active OBPI

**Input**: Review finds that a corpus-generator test derives expected boundaries
from the same production parser it is supposed to check.

**Output**: Keep the finding attached to the generator's boundary obligation.
Repair the test using contract-derived expectations, demonstrate sensitivity to
the production fault, and obtain the required independent closure. Record the
change and proof/closure references in the OBPI change log. No GHI is needed.

### Example 1a — Independent infrastructure defect surfaced mid-pipeline

**Input**: During OBPI-0.0.16-04 implementation, `uv run gz validate --documents` flagged a pool ADR for drifted frontmatter. Pool ADRs are supposed to skip that check per schema.

**Output**: The validator defect needs its own disposition beyond the OBPI's
deliverable. After ownership/prior-art lookup, file `defect` GHI titled
`validator: frontmatter check does not skip pool ADRs`, with observed output and
the pool-skip rule. Link the independent issue from the brief's Tracked Defects
section. The GHI's direct-repair authority applies; discovery during the pipeline
does not make the validator repair a new OBPI.

### Example 2 — Enhancement for a working surface

**Input**: `gz adr status` renders a Rich table correctly, but the lane column abbreviates "heavy" to "H" which operators consistently misread.

**Output**: File `enhancement` GHI titled `gz adr status: lane column abbreviation hurts legibility`. Body includes a screenshot/paste, the operator feedback, and a proposal ("spell out heavy/lite; alignment issue only, no schema change"). Not a defect — the verb does what it says; the taste is off.

### Example 3 — Investigation, root cause unknown

**Input**: Reconciliation caches are regenerating at 3x the expected rate across sessions. No specific failure observed; the cost signal is what surfaced it.

**Output**: File `investigation` GHI titled `reconcile: cache regenerates more often than expected`. Body skips "Expected" (no canonical baseline yet); includes the cost signal, the observation window, and candidate hypotheses. The GHI is the home for the investigation itself — closing it will produce either a defect GHI with a known fix or a documentation update explaining the observed rate as correct.

### Example 4 — Architectural absence, route to pool ADR + close in same session

**Input**: During OBPI-0.0.21-08 closeout, the operator surfaced that gzkit's governance surface is "choreographed not state-machined" — there is no canonical state machine, no runtime invariant monitor, and silent state demotions go unnoticed (concrete symptom: `gz frontmatter reconcile` rewrote a hand-marked `Withdrawn` brief to `pending` because no withdrawal transition exists).

**Output**: This is two findings — a concrete observed symptom and a class-level architectural absence. File **two GHIs**, one per finding shape:
1. A `defect` GHI for the silent demotion (concrete reproduction, expected vs. observed, citation of ADR-0.0.9 Rule 1 the reconciler was honoring).
2. An architectural-absence GHI listing the symptom-class with citations across `STATUS_VOCAB_MAPPING`, GHI #290/#292 bolted-on guards, reconcile-then-precomplete loops, frontmatter rewrite cascades.

**Same-session routing:** the right destination is a pool ADR (the design conversation is genuinely architectural, but no existing ADR absorbs it). Author it via `uv run gz plan create obpi-state-machine --kind pool --lane heavy --title "OBPI State Machine and Runtime Invariant Monitor"`, populate Intent / Decision / four rejected alternatives / ADR relationship matrix / OBPI promotion plan grounded in the GHIs' evidence, commit. Then close **both** GHIs `superseded` citing the pool ADR ID. The GHIs' purpose (route the observations to a durable home) is fulfilled; the pool ADR's lifecycle (promotion → gates → OBPI ceremony) owns implementation.

**Anti-pattern this example replaces:** filing the architectural-absence GHI with an acceptance criterion of "closes when state machine ships" and leaving it open for months as a stale tracker. The pool ADR is the tracker; the GHI was the routing artifact, and routing is complete.
