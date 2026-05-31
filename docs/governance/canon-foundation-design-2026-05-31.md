<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Canon Foundation — Design Capture (2026-05-31)

> **Status:** Pre-ADR design capture (a "window" per the ontology below — design rumination,
> not yet decided canon). Captured from the 2026-05-31 operator+agent design dialogue so the
> nuance is not re-derived next session ("the time to capture design nuance is now").
> **Disposition:** To be formalized via `gz-design` → a new **foundation ADR** using a new
> **`amends`** ADR disposition that amends **ADR-0.0.9** (state doctrine) and reconciles
> **ADR-0.0.10** (storage tiers). On crystallization this record migrates from `docs/` to
> `.gzkit/design/`.
> **Blast radius:** operator-set to "nuke from orbit — touch all." Nothing below is deferred
> from the *design*; build is sequenced (§12), but the design captures everything now.

---

## 1. The thesis (why this is the most important work)

The enduring criticism of gzkit — *too much governance lives in the latent space of MD prose;
the mechanical aspect lags* — and the context-load emergency (#519) are the same problem from
two ends. A prose rule in a control surface is governance held in latent space: it binds only
if the model happens to attend to it, and "happens to attend" is exactly the vibe surface.
**Machine-readable canon drags latent-space governance into mechanical control.**

### Empirical grounding (the audit, 2026-05-31)

Two independent passes over the GHI corpus (30 open, stratified 44 of 458 closed defects)
tested the hypothesis *"ADR-0.0.9's docs-as-canon / frontmatter-as-truth definition is the
root cause of a majority of failures."*

- **The narrow claim is refuted: ~9–10% are L1-ROOT.** Title-keyword matching *confirms it by
  construction* (the vocabulary — `reconcile`, `drift`, `frontmatter`, `canonical`, `Layer-1` —
  is everywhere); body-reading with the discriminator *"if canon lived in a machine-readable
  store instead of docs-markdown-with-frontmatter, would this still happen?"* collapses it to ~10%.
- **The broad thesis is validated.** The dominant ADJACENT bucket is *"advisory rule never
  promoted to mechanical / validator machinery missing"* — which **is** the latent-prose-governance
  problem. Time trend: recent failures increasingly reflect governance machinery *maturing into
  gaps where a mechanical gate doesn't yet exist* — the opposite of what an L1-redefinition
  refactor predicts, and exactly what a **mechanization substrate** addresses.

**Consequence for justification:** canon's value is **forward** (the mechanization target that
ends the dominant failure family) — *not* backward ("fix the docs-as-canon root cause," which is
~10%). The #519 emergency is the one acute L1-ROOT item and is in scope.

---

## 2. The five-role ontology (settled)

```
CODE  ⟺  CANON | DESIGN  ⟺  HUMAN DOCS
```

| Role | What it is | Operating-mode readable? |
|---|---|---|
| **Code** (`src/`, control surfaces) | Mechanism / determinism. Binds to canon; **never reaches into `docs/`.** | n/a (it *is* the operator) |
| **Canon** (`.gzkit/canon/`) | **Invariant rules.** Machine-readable JSON, ontology-shaped. The standing law, "etched in stone" = *decided / immutable-without-a-governed-action.* | **Yes** |
| **Design** (`.gzkit/design/`) | **Decisions made under constraint** — ADRs, OBPIs. Out of `docs/`. | **Yes** |
| **Human Docs** (`docs/`) | **Mirror** (reflect what is decided/present) **+ window** (insight, possibility, foundational reasoning, ruminations on the undecided). Authority for *neither*. | **No — forbidden in operating mode** |
| **Doctrine kernel** | The decided principles (operator's battle-honed pain points). A *catalog inside canon*, not a sixth thing. Periodically human-reviewed; must jive with operator sensemaking. | (it is canon) |

**Law vs. rhetoric (the precise cut).** Canon = the decided (law); it **includes decided
judgment**, expressed concisely. Docs = the undecided (rhetoric) — alternatives, fuzzy
epistemics, generative thinking. *Expansive ontology, concise decisions:* canon holds a rich
vocabulary/concept-space (terms, synonyms, relations — where epistemic breadth lives) **and**
concise decided facts stated over it. Justification of a decision is *referenced*
(`rationale_ref` → docs), never embedded.

---

## 3. Two agent modes (the hard constraint)

- **Co-design mode** — `docs/` is open (mirror + window). Fuzziness is the point.
- **Operating mode** (running skills, conforming to rules, using tools, audit) — **`docs/` is
  forbidden. The agent reasons only from `CODE ⟺ CANON|DESIGN`.**

**Forbidden edges (mechanizable):** `code → docs`; `operating-agent → docs`. Witness: a
`gz validate` scope fails any operating surface (skill / rule / tool contract) that cites `docs/`
for binding truth. Note: ADRs/OBPIs are **design**, not docs — operating agents read them; the
prohibition is on the *editorial* layer only.

---

## 4. Two reconciliation loops

```
CODE ⟺ CANON   — mechanical, gate-enforced (code binds canon; gz validate --canon-coherence)
CANON ⟺ HUMAN  — operator review (you confirm canon jibes with your sensemaking)
```

The operator **authors nothing directly** — every canon edit is an agent action under operator
direction, through the forced `gz canon` verb (deterministic, validated, ledger-witnessed). So
the verb + validation + ledger + the review loop **is the entire integrity model** — there is no
"careful hand-edit" fallback. **Operator-economy payoff:** you review the *law* (concise canon);
the gates *transitively guarantee* the code conforms. Reviewing canon *is* reviewing the system.

---

## 5. Human-as-final-witness doctrine (the keystone)

> Canon holds *delegated* authority. At the terminal gate, **the operator is the final witness
> and rules supreme.** The agent advises; the operator may take counsel; then the operator rules;
> then the agent **notes the variance and stops.**

- This resolves the `witness: null` problem: **Judgment-class entries are not unwitnessed — they
  are witnessed by the operator at the last gate.** The witness is *never* truly null: it is
  either a *mechanical gate* (delegated) or *the operator* (reserved).
- **"Note the variance"** is a mechanism, not a sentiment: when the operator's ruling diverges
  from canon, the system records a ledger event — that *is* the `CANON ⟺ HUMAN` reconciliation
  loop firing, the signal that canon may need amending.
- The terminal gates — **OBPI-pipeline Gate 5, ADR Closeout, ADR Evaluate** — are the apex where
  delegation yields to sovereignty. Operator: *"I can't overstate how vital these are."*

---

## 6. The mechanism

- **`gz canon` verb** — the only write path into canon. Deterministic, validated, ledger-witnessed.
  No raw JSON edits (an agent can vibe a JSON edit as easily as a prose one). Foundry analogy:
  mutations happen only through governed **Actions**.
- **`gz validate --canon-coherence`** — fail-closed:
  - every *mechanical* `witness` resolves to a real gate;
  - *Judgment* entries are **exempt** (their witness is the operator at the terminal gate);
  - every synonym maps to exactly one canonical term;
  - every `rationale_ref` resolves;
  - no operating surface cites `docs/`.
- **Canon is governed by the gates it enables** (the self-referential bootstrap, same shape as
  "every foundation ADR registers ≥1 invariant").

### Schema: two decided-entry kinds, first-class

| Kind | `witness` | Renders at | Coherence check |
|---|---|---|---|
| **Mechanical** | a gate command | thins with temperature (gate carries the safety) | witness must resolve to a real gate |
| **Judgment** | *the operator* (terminal gate) | **every** temperature (0-Kelvin floor — the model must hold it) | exempt from gate-resolution; human-witnessed |

If the "determinism" mental model drives the schema, it will only fit Mechanical entries and force
Judgment back into prose — reopening the latent-space hole. **Both kinds are first-class.**

---

## 7. The Foundry/Palantir north-star

Ontology = **Objects · Properties · Links · Actions**, a single semantic SoT that *both* humans
and applications reason from, where mutations happen only through governed **Actions**. Map onto
canon: concepts → objects; vocabulary + synonyms → properties/aliases; relations → links;
decided rules + `gz canon` mutations → **Actions**. The Foundry lesson: the ontology is the single
semantic SoT and governed actions are the *only* write path — precisely the `gz canon` model.

---

## 8. Full blast radius (nuke touches all)

**Core (where the failure mass is — §1 audit):**

1. **Canon store** — `.gzkit/canon/`, JSON, ontology-shaped, two entry kinds (§6).
2. **`gz canon` verb** + **`gz validate --canon-coherence`** (§6).
3. **Migrate `.gzkit/rules/*.md` → canon** — prose demoted to `rationale_ref`. *The high-leverage
   core:* closes the dominant "advisory-rule-never-mechanized" family.
4. **Forbidden edges** — `code → docs`, `operating-agent → docs`. **Canon entry #1.**
5. **#519 relief** — the ADR-0.0.37 CMS renders control surfaces *from* canon at temperature; the
   prose monolith dissolves.
6. **Human-as-final-witness doctrine** + the **"note variance"** ledger event (§5).

**Margin:**

7. **Design store** — `.gzkit/design/`; relocate ADRs/OBPIs out of `docs/`.
8. **Subsume all scattered L1** — `.gzkit/invariants/`, `data/*.json`, classifications → one canon home.
9. **Two-mode enforcement** — validator failing any operating surface that cites `docs/`.
10. **Amend ADR-0.0.9** (reconcile ADR-0.0.10): redefine the layer model to `CODE | CANON·DESIGN | DOCS`.
11. **New `amends` ADR disposition** — defined *by* this ADR as its first user.

**Now IN scope (formerly "deferred" — operator: "this must be within the blast radius"):**

12. **Harness/model auto-detection of templates** — the dynamic per-vendor / per-model temperature
    selection (the operator's *"REALLY fine tune"* vision). Designed now; the detection signal feeds
    the CMS temperature + section-inclusion set.
13. **Full graph engine** — canon's ontology **links** *are* the graph spine. Canon is the
    state-doctrine-locking step that unblocks Architectural Boundary 3 (which forbids building the
    graph engine before state doctrine is locked — canon *is* the locking). Typed-relation ontology
    in JSON; **JSON-LD** is the in-idiom bridge if/when edges need formal graph semantics (never XML/RDF).
14. **Adopter domain-canon scaffolding (`gz init`)** — adopters get **two** canons: the inherited
    *tool-canon* at `.gzkit/canon/` (gzkit's governance ontology, shipped) **+** their authored
    *domain-canon* at `<project-root>/canon/` (the ontology of the useful software they build, their
    domain rules, the skills that shape their software toward domain goals). gzkit itself has **one**
    canon (we are the tool; "seaborn shipbuilding as we dogfood"). `gz init` scaffolds the adopter's
    domain-canon home.

**Three self-bootstraps:** the `amends` disposition is defined by this ADR (first user);
"`code → docs` forbidden" is **canon entry #1**; canon is governed by the `--canon-coherence`
gate it enables.

---

## 9. Open design questions the ADR must resolve

- **Classification source-of-truth.** `docs/governance/advisory-rules-audit.md` scorecard
  (human-deliberated Mechanical/Promotable/Judgment/Ambiguous) is SoT; the scorecard's *data*
  moves **into canon**; the `.md` becomes a `rationale_ref`. The model derives from canon. This
  dissolves the ADR-0.0.37 concern-1 tension (classification becomes a canon fact, not a special-
  case reconciliation gate).
- **The bullet↔scorecard-rule correspondence map** — *the real center of gravity* of the
  rules→canon migration. The scorecard classifies *rules*; canon entries are finer-grained; the
  surface includes sections that aren't rule-files. Establishing the correspondence (which entry
  derives from which scorecard row) is the hard work; drift between model classification and
  scorecard is fail-closed.
- **"One spine" honesty.** `reconcile_invariant` (OBPI-0.0.37-11) is one-way and lossy (drops
  `id`, `composition_targets`, witnesses 2..N). So the invariant registry is a *projection input*,
  not a regenerable mirror. Pin: which store is SoT for an invariant when both are editable. Likely:
  canon is SoT; the registry collapses into canon under the subsume (§8.8).
- **Two gates, two boundaries** (from ADR-0.0.37 review): byte-compare guards the *human-edit*
  boundary (anti-vibe-edit — keep as-is); a **path-independent floor check**
  (`count(Judgment in model) == count(Judgment in rendered-lite)`) guards the *render-correctness*
  boundary. Neither subsumes the other.
- **Deterministic authoring affordance** — `gz canon` (and the design-store analog) must be the
  forced edit path; raw-file edits to canon/design data are flagged. Only human-directed agents
  author; the operator authors nothing outside chat.

---

## 10. Relationship to existing ADRs

- **Amends ADR-0.0.9** (state doctrine / SoT hierarchy) — redefines Layer-1 from "versioned MD/YAML
  including `docs/`" to `CODE | CANON·DESIGN | DOCS`. *The audit refutes "0.0.9 caused most failures"
  — the amendment is justified as the mechanization substrate, not as root-cause repair.*
- **Reconciles ADR-0.0.10** (storage tiers).
- **Substrate beneath ADR-0.0.37** — the CMS (density-dial composition) renders control surfaces
  *from* canon. ADR-0.0.37 **OBPI-13/14 re-sequence behind** the canon ADR (13's classification
  derives from canon).
- **OBPI-0.0.37-11** (density-aware master content model) — **Completed + attested 2026-05-31**.
  It is the first brick: the schema substrate the CMS temperature renderer consumes.

---

## 11. Methodological note (preserve this too)

This session demonstrated the failure mode the whole architecture targets, *live*, twice:
(a) the agent re-derived the rendering architecture from source despite documented design (the
"open loop" — capture without re-injection does not bind); (b) the agent over-called "ADR
underspecified" by keyword-matching instead of body-reading. **The gate (the operator's bet +
"confirm by reviewing GHIs") forced the honest audit that corrected both.** The terminal human
gate is not bureaucracy — it is the forcing function that surfaces emergence, tension, and
alignment that freeform execution buries under "tests pass, ship it."

---

## 12. Sequencing (design covers all; build increments)

The blast radius is the *design* scope; the *build* sequences by failure-mass leverage:

1. Canon store + `gz canon` + `--canon-coherence` + canon-entry-#1.
2. Migrate `.gzkit/rules/*.md` → canon (+ correspondence map, classification SoT).
3. Design store `.gzkit/design/`; relocate ADRs/OBPIs.
4. Subsume scattered L1; two-mode enforcement; amend ADR-0.0.9.
5. CMS renders from canon (#519 relief); the two-gate floor check.
6. Graph engine (on canon's links) · harness/model detection · adopter domain-canon scaffolding.

Steps 1–2 retire the dominant failure family; 5 clears the #519 emergency; 6 is the formerly-
deferred vision, designed now, built last.

---

## 13. Session 2026-05-31 (PM) — execution-model & taxonomy decisions (folds into this thread)

> Captured per §11 (latent decisions get re-derived next session). **Decided** items are
> operator-confirmed this session; **Open** items need major discussion before adoption.
> Formalize with the canon ADR post-recovery (amends ADR-0.0.9).

**Decided:**

1. **Retire the `foundation` ADR kind.** "Invariant" had been used loosely to mean *plumbing
   that facilitates features*; foundation was redundant with the pool (both = decide-without-
   releasing) and an artifact of the ADR↔semver coupling. Genuine invariants live in **canon**
   (this thread); ADRs become pure **design**. *This invalidates this document's own §8 /
   disposition "foundation ADR" self-label — this is the canon-establishing **design** decision,
   not a foundation ADR.*
2. **Two demarcations + pool:** design (pool / *made*) → triage → built (*features*) → semver
   (release tag). No foundation/feature metaphysics; "essence vs. accident" judged contrived.
3. **Semver habits (normal):** GHI closure → **patch**; ADR completion → **minor**; "PRD
   satisfied" → **major** + basis for the next round. Decouple ADR-id from semver (post-recovery).
4. **Execution loop (Pocock-guided; attended vs. autopilot):** idea (`grill`) → [research] →
   [prototype] → PRD/ADR → vertical-slice issues → execute + QA-loop.
5. **AFK/HITL = gate-*placement*, classified at plan-time** (Pocock-confirmed): **HITL/attended**
   → local gates + present operator (terminal witness now); **AFK/autopilot** → branch/worktree-
   per-OBPI → PR → unattended mechanical gates → **async Gate-5 attestation on the PR**. Universal
   Gate 5 (ADR-0.0.36) holds — **never self-close**, even AFK.
6. **Per-OBPI worktree + PR + receipts + attestation** is gzkit's structural fix for AFK's
   review-burden (Pocock's admitted, unfixed weakness).
7. **Drop the OBPI lock system** — branches give the isolation locks faked on trunk; PRs +
   `git branch -a` give visibility. (Pipeline change, post-recovery.)
8. **Triage trio + router:** `ghi-triage` (corrective) · `gz-build-triage` (formerly
   `gz-foundation-triage`; what to build from pool) · `design-triage` (what to *make* → pool);
   chores self-surface (cadence: after each ADR ships). Unified by **`gz-next`** — the whole-
   project "best next move," renamed away from Pocock's queue-"triage."
9. **Keep the spine (sacrosanct):** ledger-of-truth, receipts, universal Gate 5, fail-closed
   validators, the kind/lane/sensitivity axes. "Lighter" is not a trade (anti-vibing mantra).

**Open — needs major discussion (NOT adopted):**

- The specific Pocock borrowings beyond the loop + AFK/HITL — fenced `prototype`, sprint-lived
  research/design-asset lifecycle, vertical-slice sizing + the horizontal-slicing anti-pattern
  citation, the ADR-worthiness 3-gate, QA→GHI loopback — evaluated **per-item** against "does
  this erode the spine?", deliberate, never wholesale. Baseline: GHI #567.

**Immediate (this session):** re-home ADR-0.0.66 → pool (unbuilt design; its substance folds
into this canon thread).
