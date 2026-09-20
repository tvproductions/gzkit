---
id: ADR-0.39.0-gzkit-internal-config-surface
status: Draft
kind: feature
semver: 0.39.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-09-20
---

# ADR-0.39.0-gzkit-internal-config-surface: gzkit-internal config surface

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.

This ADR replaces an accreted surface with a designed one, so the standard it is held to is evidence over plausibility. Every count in it traces to a re-runnable script rather than a transcribed figure, every constraint is classified as real, inherited or assumed before it is treated as binding, and a stated separation is never accepted where a mechanical one is required. The settings/debt boundary is the seam this work lives or dies on; prose describing it is not a deliverable.

## Intent

gzkit reads its own configuration from 48 files under data/ plus 56 numeric constants hardcoded in module bodies, with no entry point, no loader and no coherence gate. Nineteen of the 48 record no derivation, so no reader can tell a deliberate choice from an inherited accident; the 56 constants are unreachable by data/config_registry.json, which declares itself exhaustive over data/*.json alone. Operator, 2026-09-20, verbatim: 'gzkit lacks a comprehensive and all-encompassing config system like airlineops had, we need to adopt this as a pre-requisite for 1.0. this is inexcusable. there are so many janky and undocumented rules, thresholds and pseudo-settings handing around gzkit. it is a travesty'. Scoped the same day: 'I want a single configuration surface for the whole project. implementers would develop their own, so this is a gzkit-interal config.' The subject is what gzkit reads ABOUT ITSELF, never what gz init scaffolds for an adopter. Measured at docs/governance/config-derivation-census-2026-09-20.md; re-run its script rather than trusting a transcribed figure.

## Decision

1. Adopt the five ../airlineops/config principles verbatim as the contract: single entry point, categorical subdirectories, no parallel systems, config is not documentation, no duplication.
2. `.gzkit/config/settings.json` is THE entry point, and is a SINGLE FLAT FILE — no categorical subdirectories. RE-AMENDED 2026-09-20, operator verbatim: 'one "mega" settings.json file is fine, subdirectories are not needed' (operator corrected 'file' to 'fine' in the same exchange). This is a DELIBERATE DEPARTURE from the second of the five airlineops principles adopted verbatim in item 1, recorded as a departure so a later reader does not read it as an implementation that ignored its own adopted principle. The departure is coherent with this ADR's own reversibility finding: logical keys make layout invisible to callers, so subdividing later costs nothing and subdividing now would fix category names before the 56-constant triage reveals what the categories actually are. The fence is unaffected — item 4 sends the 29 rosters OUT of the settings surface to debt/, a separate location rather than a subdirectory, so a flat settings.json and a separate debt class are compatible. Merge order: init-scaffolded defaults, then settings.json, then optional settings.local.json. AMENDED 2026-09-20 by operator ruling from the interview's assumption-surfacing pass, verbatim: 'this is config for gzkit, it should live in .gzkit/config, adopters will develop their own approach.' The prior text placed the entry point at config/ in the repository root. `.gzkit/config` is chosen because `project_root / '.gzkit' / 'config'` denotes THIS project's config in both the self-hosting and the adopter context, where `project_root / 'data'` denotes gzkit's development thresholds in one and a non-existent path in the other. The subdirectory `governance/` is renamed `policy/` in the same amendment: `.gzkit/governance/` already exists as a sibling, and two 'governance' surfaces one directory apart would read as an error.
3. gzkit.registries.load_registry addresses LOGICAL KEYS ('thresholds.audit'), never filenames; the entry point owns the key-to-path mapping (operator ruling 2026-09-20).
4. The 29 waiver/grandfather/baseline rosters are a SEPARATE CLASS — debt state, not settings — and leave the settings surface for debt/, indexed by the waiver ratchet.
5. gzkit's own .gzkit.json instance folds in; GzkitConfig remains the adopter-facing schema.
6. The 56 module constants are triaged one at a time against the shrink-only roster: operator-tunable values become settings, correctness-critical values stay in code with a comment, and every timeout becomes a setting.
7. SCOPE FENCE (operator ruling 2026-09-20): this ADR stays gzkit-internal. `gz init` scaffolding strongly opinionated adopter defaults, in the django-cookiecutter manner the operator named, is DOWNSTREAM work under a named successor ADR and is not a checklist item here. The authored intent's exclusion — 'never what gz init scaffolds for an adopter' — stands unamended.

## Consequences

### Positive

1. Closes a class rather than instances: GHI #929's loader and coherence halves, #1064, #1065 and #1066 were all the same wound, and #929 closed with only the ownership half built.
2. A reader can tell a deliberate threshold from an inherited accident, which today they cannot for 19 of 48 registries.
3. Logical keys make file layout an implementation detail, so a later reorganisation costs no caller changes.
4. Discharges a declared 1.0 gate (campaign § 5, added 2026-09-20) with a Movement tracking it (Movement F).

### Negative

1. THE DEBT CLASS LEAKS BACK IN — operator-identified as the LIKELIEST failure mode (2026-09-20, ranking the pre-mortem scenarios). 'Separate class' is prose, and prose without a mechanism is the doctrine-declared-without-mechanism family this campaign exists to close. A roster needs a threshold, the threshold goes in the roster, and the shrink-only ratchets start carrying tunables that cannot be edited safely. This ADR must ship a MECHANICAL fence on the boundary, not a stated one.
2. A 49th parallel system: the surface lands and the 49 readers never migrate, because migration is always less urgent than the next defect.
3. The key-to-path mapping becomes the only thing that knows the layout, with no witness of its own.
4. The 56 constants sit at 56 indefinitely, because triage is judgment work and the roster permits sitting.
5. Completion is gated behind four unlanded feature ADRs: authoring was excepted from ADR order on 2026-09-20, completion explicitly was NOT.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Exhaustive registry ownership still holds after the relocation | uv run gz validate --config-registry | 0 |
| The waiver ratchet still indexes the rosters after they move to debt/ | uv run gz validate --waiver-ratchet | 0 |

<!-- INCOMPLETE. The two rows above name commands that exist today and act as
     regression fences: both pass now and must still pass after the rosters move.
<!-- gz-validate-skip: command-shape -->
     Assertions for this ADR's own thesis are NOT yet written. `gz config show` is
     sanctioned by checklist item 4, but the validator flag names for the tolerance
     contract and the fence have not been decided, and inventing them here would put
     fabricated commands into a table that `gz adr fidelity` executes. They are
     authored when their owning OBPI names its surface. -->

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 7

Split scoring, operator-ruled 2026-09-20. The scaffolder defaults all four overlays to 0
because they are author judgment. Mapping the seven checklist items onto the matrix's
Rule-of-Three baseline: item 1 is Registry/Interface, items 2-3 are Core Execution, items
4-7 are Lifecycle/Operations. Each overlay has a citable violation in that mapping.

- **Single-Narrative**: items 5, 6 and 7 are three objectives joined by "and".
- **Testability Ceiling**: item 2 (absent and malformed) plus item 3 (a fence refused in
  both directions) exceed the five-cluster ceiling for one unit.
- **State Anchor**: item 5 relocates 29 roster files, which is persistent-state work.
- **Surface Boundary**: item 4 is an external CLI surface sitting with internal logic.

RECORDED PROVENANCE: the agent produced this mapping AFTER the target of 7 was already
set, and 4 is the maximum split total the formula can yield. The operator ruled on it with
that disclosure stated. A later reader weighing whether this ADR is over-decomposed should
know the scores were reached in that order, and that the matrix's stated Heavy-lane
standard is 3-5.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps.
     The box is a ROW MARKER, never a status claim: leave it `- [ ]`. Completion
     lives in the ledger — read it with `uv run gz adr status`, never from this
     page. A `[x]` here is rejected by `gz validate --documents` (GHI #928). -->

- [ ] 1. Entry point and key grammar: `.gzkit/config/settings.json` as a SINGLE FLAT FILE, `load_registry` addressing logical keys rather than filenames, and the key-naming discipline fixed before any caller adopts it.
- [ ] 2. Tolerance contract: the loader's behaviour for an ABSENT and for a MALFORMED surface is specified and tested, so a single entry point is not a regression against the 49-reader status quo.
- [ ] 3. Settings/debt fence: a mechanical check refusing a tunable inside a debt roster and a debt roster inside the settings surface, carrying the existing exhaustive-ownership mechanism forward and reaching the module-constant channel. LOAD-BEARING.
<!-- gz-validate-skip: command-shape -->
- [ ] 4. `gz config show <key>` reports the effective value and the merge layer that supplied it.
- [ ] 5. Roster relocation: the 29 waiver/grandfather/baseline rosters leave the settings surface for `debt/`, with the exhaustiveness scope moving in the same change.
- [ ] 6. Reader migration: the 49 rostered direct-reach modules move to the entry point, once, after the surface exists.
- [ ] 7. Constant triage: the 56 rostered module constants are triaged against the shrink-only roster; every timeout becomes a setting.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-09-20T13:38:41.655655*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.39.0-gzkit-internal-config-surface

### Q: What is the title of this ADR?

**A:** gzkit-internal config surface

### Q: What is the semantic version?

**A:** 0.39.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit reads its own configuration from 48 files under data/ plus 56 numeric constants hardcoded in module bodies, with no entry point, no loader and no coherence gate. Nineteen of the 48 record no derivation, so no reader can tell a deliberate choice from an inherited accident; the 56 constants are unreachable by data/config_registry.json, which declares itself exhaustive over data/*.json alone. Operator, 2026-09-20, verbatim: 'gzkit lacks a comprehensive and all-encompassing config system like airlineops had, we need to adopt this as a pre-requisite for 1.0. this is inexcusable. there are so many janky and undocumented rules, thresholds and pseudo-settings handing around gzkit. it is a travesty'. Scoped the same day: 'I want a single configuration surface for the whole project. implementers would develop their own, so this is a gzkit-interal config.' The subject is what gzkit reads ABOUT ITSELF, never what gz init scaffolds for an adopter. Measured at docs/governance/config-derivation-census-2026-09-20.md; re-run its script rather than trusting a transcribed figure.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** 1. Adopt the five ../airlineops/config principles verbatim as the contract: single entry point, categorical subdirectories, no parallel systems, config is not documentation, no duplication.
2. `.gzkit/config/settings.json` is THE entry point, and is a SINGLE FLAT FILE — no categorical subdirectories. RE-AMENDED 2026-09-20, operator verbatim: 'one "mega" settings.json file is fine, subdirectories are not needed' (operator corrected 'file' to 'fine' in the same exchange). This is a DELIBERATE DEPARTURE from the second of the five airlineops principles adopted verbatim in item 1, recorded as a departure so a later reader does not read it as an implementation that ignored its own adopted principle. The departure is coherent with this ADR's own reversibility finding: logical keys make layout invisible to callers, so subdividing later costs nothing and subdividing now would fix category names before the 56-constant triage reveals what the categories actually are. The fence is unaffected — item 4 sends the 29 rosters OUT of the settings surface to debt/, a separate location rather than a subdirectory, so a flat settings.json and a separate debt class are compatible. Merge order: init-scaffolded defaults, then settings.json, then optional settings.local.json. AMENDED 2026-09-20 by operator ruling from the interview's assumption-surfacing pass, verbatim: 'this is config for gzkit, it should live in .gzkit/config, adopters will develop their own approach.' The prior text placed the entry point at config/ in the repository root. `.gzkit/config` is chosen because `project_root / '.gzkit' / 'config'` denotes THIS project's config in both the self-hosting and the adopter context, where `project_root / 'data'` denotes gzkit's development thresholds in one and a non-existent path in the other. The subdirectory `governance/` is renamed `policy/` in the same amendment: `.gzkit/governance/` already exists as a sibling, and two 'governance' surfaces one directory apart would read as an error.
3. gzkit.registries.load_registry addresses LOGICAL KEYS ('thresholds.audit'), never filenames; the entry point owns the key-to-path mapping (operator ruling 2026-09-20).
4. The 29 waiver/grandfather/baseline rosters are a SEPARATE CLASS — debt state, not settings — and leave the settings surface for debt/, indexed by the waiver ratchet.
5. gzkit's own .gzkit.json instance folds in; GzkitConfig remains the adopter-facing schema.
6. The 56 module constants are triaged one at a time against the shrink-only roster: operator-tunable values become settings, correctness-critical values stay in code with a comment, and every timeout becomes a setting.
7. SCOPE FENCE (operator ruling 2026-09-20): this ADR stays gzkit-internal. `gz init` scaffolding strongly opinionated adopter defaults, in the django-cookiecutter manner the operator named, is DOWNSTREAM work under a named successor ADR and is not a checklist item here. The authored intent's exclusion — 'never what gz init scaffolds for an adopter' — stands unamended.

### Q: What good things result from this decision? List benefits.

**A:** 1. Closes a class rather than instances: GHI #929's loader and coherence halves, #1064, #1065 and #1066 were all the same wound, and #929 closed with only the ownership half built.
2. A reader can tell a deliberate threshold from an inherited accident, which today they cannot for 19 of 48 registries.
3. Logical keys make file layout an implementation detail, so a later reorganisation costs no caller changes.
4. Discharges a declared 1.0 gate (campaign § 5, added 2026-09-20) with a Movement tracking it (Movement F).

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. THE DEBT CLASS LEAKS BACK IN — operator-identified as the LIKELIEST failure mode (2026-09-20, ranking the pre-mortem scenarios). 'Separate class' is prose, and prose without a mechanism is the doctrine-declared-without-mechanism family this campaign exists to close. A roster needs a threshold, the threshold goes in the roster, and the shrink-only ratchets start carrying tunables that cannot be edited safely. This ADR must ship a MECHANICAL fence on the boundary, not a stated one.
2. A 49th parallel system: the surface lands and the 49 readers never migrate, because migration is always less urgent than the next defect.
3. The key-to-path mapping becomes the only thing that knows the layout, with no witness of its own.
4. The 56 constants sit at 56 indefinitely, because triage is judgment work and the roster permits sitting.
5. Completion is gated behind four unlanded feature ADRs: authoring was excepted from ADR order on 2026-09-20, completion explicitly was NOT.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** Seven items, ordered core-first. Items 1-4 close the class (entry point and key grammar; tolerance contract; settings/debt fence; the read path). Items 5-7 are the interruptible tail (roster relocation; reader migration; constant triage). Full text in the Checklist section above.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. FILENAME ADDRESSING (load_registry(root, 'audit_thresholds.json')): REJECTED by operator ruling 2026-09-20. Callers would never change again, but the post-config API would permanently encode the pre-config layout, and every reader migrates exactly once anyway.
2. ONE PHYSICAL FILE: REJECTED — mixes tunable thresholds with 50-entry shrink-only rosters in one document.
3. ENTRY POINT, FILES STAY PUT: REJECTED — 'single surface' becomes a code contract with no visible directory, which is the state that produced the problem.
4. ROSTERS INSIDE THE SETTINGS SURFACE: REJECTED by operator ruling — nobody tunes measured debt, and housing it as settings invites editing it as settings, the laundering ADR-0.0.73 Boundary Invariant #8 forbids.
5. DO NOTHING BEYOND THE 2026-09-20 FENCES: REJECTED — the three ratchets stop growth but repair nothing; 19 unsourced registries and 56 constants remain.

### Q: Pre-mortem (Klein): it is 18 months from now and this decision has failed spectacularly. Why? Name the mitigation.

**A:** OPERATOR-RANKED 2026-09-20, verbatim: '2 is the likeliest — the debt class leaking back in.' The agent drafted four scenarios and the operator selected the boundary leak over the unmigrated-readers, drifted-mapping and untriaged-constants failures. CONSEQUENCE FOR THE DESIGN: the settings/debt boundary is the ADR's load-bearing seam and must carry a mechanical witness, not a stated separation. A check that refuses a tunable value inside a debt roster, and a debt roster inside the settings surface, is a REQUIRED deliverable rather than a hardening nicety. Precedent for what happens without one: the 'no parallel systems' discipline has been declared in .gzkit/chores/hardcoded-root-eradication since 2026-04 and had 50 live violations on 2026-09-20.

### Q: What would have to be true (Martin) for this to be the right decision — and which of those conditions is shakiest?

**A:** Four conditions must hold for the logical-key entry point with debt as a separate class. (A) The settings/debt split is decidable by a mechanical rule rather than per-file judgment. (B) Logical keys outlive the file layout, so the key vocabulary is more durable than the directories and callers migrate exactly once. (C) Each of the 56 rostered constants falls cleanly into operator-tunable or correctness-critical. (D) A single entry point does not become something readers route around for import-cycle or load-order reasons. OPERATOR-RANKED 2026-09-20: A is the shakiest. This does not add a second risk; it converges with the operator's pre-mortem ranking on the same seam, so the settings/debt boundary is both the likeliest failure and the condition the decision most depends on. CONSEQUENCE: the ADR cannot discharge this by stating a rule in prose. The rule must be executable, and if the distinction turns out to require case-by-case judgment, the load-bearing deliverable cannot be built as specified and the decision itself needs revisiting rather than the implementation. MIRROR (for filename addressing to have been better): the current layout would have to be already correct and stable, so encoding it in the API cost nothing later. That condition is false as measured — 19 of 48 registries record no derivation, so the layout encodes inherited accidents rather than decisions. See docs/governance/config-derivation-census-2026-09-20.md; re-run its census script rather than trusting a transcribed figure.

### Q: Constraint archaeology: is each constraint here real, inherited, or assumed? When was it last tested?

**A:** THREE CONSTRAINTS, CLASSIFIED. (1) The five airlineops principles — INHERITED, adopted verbatim by operator ruling, never re-tested in gzkit's context. Their last test was against airline datasets, not governance thresholds. The verbatim adoption is ruled and not reopened here; the inheritance is recorded so a later reader knows it was adopted rather than derived. (2) data/ as the config location — NEVER DECIDED. No ADR chooses it; it is where the first file landed and everything followed. OPERATOR RULING 2026-09-20, verbatim: 'everything living in data/ in airlineops had to do with its own history. if config/ makes more sense, then we don't have to continue the legacy.' Moving to config/ therefore overturns a habit, not a decision, and the legacy arrangement carries no preservation weight of its own. (3) Exhaustive ownership of data/*.json — REAL, decided 2026-09-20 under GHI #929, actively enforced by `gz validate --config-registry`. config_registry.json owns policy and thresholds; waiver_ratchet_registry.json owns the waiver/grandfather family; the two declare themselves jointly exhaustive and the gate fail-closes on any undeclared top-level registry. FINDING THAT CHANGES THE DESIGN: the settings/debt partition ALREADY EXISTS MECHANICALLY for top-level data/*.json. The shakiest WWHTBT condition is therefore not 'can a decidable rule be invented' but 'can the rule that already decides this be carried forward'. CONSEQUENCE: the MECHANISM carries forward — exhaustive declared ownership with consumers verified rather than asserted — while its data/-shaped implementation does not, per ruling (2). Building a second mechanism deciding the same question is refused by the 'no parallel systems' principle already adopted in the Decision, so that option needs no separate ruling. COUPLED RISK (DO IT RIGHT 1a): that exhaustiveness is scoped to TOP-LEVEL data/*.json by filename glob. Moving files into categorical subdirectories breaks the glob, silently un-fencing the exact boundary this ADR depends on. The registry's scope must move in the same change as the files, and the fence must additionally reach the module-constant channel, which no data/*.json glob can see.

### Q: Assumption surfacing: which assumptions are implicit and undocumented? What if the opposite of the core assumption were true?

**A:** THE UNDOCUMENTED ASSUMPTION: every reader of gzkit's self-config tolerates that config being ABSENT. In an adopter repository `project_root / 'data'` does not exist, and the built wheel carries ZERO data/ entries (measured against dist/py_gzkit-0.34.7-py3-none-any.whl, 2026-09-20). Each of the 49 rostered readers returns a documented default instead of failing. This holds by CONVENTION — 49 authors each remembering — with no invariant stating it and no gate enforcing it. src/gzkit/quality.py states the consequence in its own docstring: 'this speedup is gzkit's own and adopters are unaffected rather than broken. Shipping it to them would mean inventing a package-data surface, which is scope this change does not carry.' INVERSION (what if the opposite were true): a single entry point moves this risk in both directions at once. One loader can enforce absent-surface tolerance in ONE place rather than 49, which is strictly better than the status quo. But a loader that hard-fails on a missing surface converts 49 independent safe defaults into ONE shared hard failure in every adopter repo. Absent-surface tolerance must therefore be a tested invariant of the entry point, not a property the implementation happens to have. OPERATOR RULING 2026-09-20, verbatim: 'this is config for gzkit, it should live in .gzkit/config, adopters will develop their own approach. However, gzkit's init will provide strongly opinionated defaults the same way django-cookie-cutter does/did. make sense? I know this is hard because gzkit is being used to bootstrap gzkit.' WHY THIS DISSOLVES THE AMBIGUITY RATHER THAN MANAGING IT: today `project_root / 'data'` means 'gzkit's development thresholds' when self-hosting and 'a path that does not exist' in an adopter repo — one expression with two meanings, which is what made the tolerance invariant invisible. `project_root / '.gzkit' / 'config'` means 'THIS project's config' in BOTH contexts and is correct in both. The packaging question does not need a package-data surface: the wheel ships TEMPLATES and `gz init` scaffolds opinionated defaults, which is the mechanism .gzkit/ already uses for every other governance surface it holds. COLLISION TO RESOLVE AT DECOMPOSITION: `.gzkit/governance/` already exists as a sibling, so a `.gzkit/config/governance/` subdirectory would place two different 'governance' surfaces one level apart. The categorical subdirectory names must be chosen against the existing .gzkit/ tree, not against a bare config/ root.

### Q: The 2am operator question: you are on-call at 2am and this is broken. What do you need that the design does not provide?

<!-- gz-validate-skip: command-shape -->
**A:** REQUIRED DELIVERABLES (operator ruling 2026-09-20, selecting from five drafted needs): (1) MALFORMED-SURFACE BEHAVIOUR IS A SPECIFIED, TESTED CONTRACT. Absent-surface tolerance covers a MISSING file; a syntactically invalid settings.json is a different failure and the likelier one at 2am, because the operator editing it caused it. Left unspecified, a trailing comma bricks every gz command at once — strictly WORSE than the 49-reader status quo it replaces, where one malformed file broke one reader. A single entry point concentrates this risk and must therefore carry the contract explicitly rather than inheriting whatever json.loads raises. (2) `gz config show <key>` REPORTS THE EFFECTIVE VALUE AND ITS SOURCE LAYER. With three merge levels (init-scaffolded defaults, settings.json, settings.local.json) a failing threshold could come from any of them, and nothing in the design provides provenance on read. Without this the 2am path is reading three files and simulating the merge mentally. The same command answers the second 2am question — whether a knob exists at all — which the operator cannot be expected to remember across a 56-entry triage. NOTED, NOT REQUIRED (operator declined as deliverables; recorded so the decomposition sees them): (a) The local override is not gitignored. Verified 2026-09-20: .gitignore covers `.gzkit.yaml.local` and `.claude/settings.local.json`, with no pattern matching `.gzkit/config/settings.local.json`. Whoever lands the surface should treat this as coupled under DO IT RIGHT 1a rather than a separate task, since an un-ignored override is committed by accident on first use. (b) Threshold failures naming their logical key in the message, consistent with the existing rule that a validator's message names the rule and its recovery. Touches many call sites; a candidate for its own pass.

### Q: Reversibility: one-way door or two-way? If this must be reversed in 12 months, what does that cost?

**A:** ASYMMETRIC: the directory is a two-way door, the key vocabulary is a one-way door. DIRECTORY — TWO-WAY AND CHEAP. Logical keys make file layout an implementation detail, so reorganising .gzkit/config/ later costs no caller changes. This was demonstrated rather than asserted: the entry point moved from config/ to .gzkit/config mid-interview at zero cost, precisely because nothing addresses a file by name yet. KEY VOCABULARY — ONE-WAY. Once 49 readers call load_registry('thresholds.audit'), that string is the API. Renaming a key is a breaking change in a way moving a file is not. The expensive mistake available in this ADR is naming keys badly, not laying out directories badly. MIGRATION — IN BETWEEN. Reverting means touching 49 call sites again: tedious, not blocked. TIMING IS THE DECIDING FACTOR. Nothing outside gzkit depends on the key vocabulary today, so it is still fully reversible. When the downstream init ADR ships opinionated defaults to adopters, those keys become a public contract and the door closes. Landing this ADR BEFORE that one is what keeps the vocabulary two-way, which is a property of the sequencing already chosen rather than a new constraint. OPERATOR RULING 2026-09-20: the reading holds, and a KEY-NAMING DISCIPLINE is a required checklist deliverable — fixing the key grammar before 49 callers adopt it: what a segment denotes, how many levels a key carries, singular versus plural, and how a key is retired when it turns out wrong. Cheap to decide now and unpayable once keys reach adopters. Deciding it once is the difference between one vocabulary and 49 individual choices, the latter being how the present 48-file sprawl accumulated.

### Q: Scope minimization: what is the smallest version that delivers value? If you had half the time, what would you cut?

**A:** IRREDUCIBLE CORE — FOUR THINGS: the entry point, the key grammar, the mechanical settings/debt fence, and the tolerance contract covering BOTH absent and malformed surfaces. The fence because the operator's pre-mortem ranking and the shakiest WWHTBT condition converged on that same seam independently. The key grammar because it is the one-way door. The tolerance contract because without it a single entry point is a REGRESSION against the 49-reader status quo rather than an improvement. CUT UNDER HALF THE TIME, IN ORDER: (1) The 56-constant triage — judgment work, already rostered and shrink-only, proceeds one constant at a time indefinitely once the surface exists. Cutting it blocks nothing. (2) The 49-reader migration — the operator's migrate-once-after-the-surface ruling means the surface must exist first regardless, and once the vocabulary is fixed the migration is mechanical. (3) The categorical subdirectories — start flat. Keys hide layout, and that door was demonstrated two-way when the entry point moved from config/ to .gzkit/config mid-interview at zero cost. Three of the four authored subdirectories are an organisational preference, not a requirement, because the addressing scheme already makes layout invisible to callers. CANNOT BE CUT AT ANY BUDGET: the fence, the tolerance contract, the key grammar. If only those three land, the class is closed and everything remaining is cleanup that can proceed at leisure. OPERATOR RULING 2026-09-20: the core holds, and the CHECKLIST IS ORDERED CORE-FIRST — briefs sequenced so entry point, key grammar, fence and tolerance contract land before migration and triage. The class closes at the earliest possible point and the remaining work becomes interruptible without leaving a half-built surface; migration and triage are the tail, never the gate.

### Q: Closing question: what subsequent decisions does this force? What ADRs will we need to write because of this one?

**A:** TWO FORCED ADRs (operator ruling 2026-09-20: both are real, record both). (A) INIT-SCAFFOLDED ADOPTER DEFAULTS. Operator-ruled downstream during this interview. This decision creates a config shape adopters need and `gz init` does not provide, to be delivered 'the same way django-cookie-cutter does/did' (operator verbatim). Forced because the internal surface establishes a shape that adopters must be given deliberately rather than left to reinvent. (B) WHETHER GzkitConfig AND .gzkit/config CONVERGE. Decision item 5 keeps GzkitConfig as the adopter-facing schema while this ADR builds a separate internal surface. That is coherent while the surface is gzkit-only. The moment ADR (A) ships .gzkit/config to adopters, an adopter repository holds TWO config concepts, and something must rule whether that is intentional layering or duplication — the latter being refused by the 'no duplication' principle adopted in item 1. This question is invisible today precisely because only gzkit has the internal surface, and it becomes unavoidable exactly one ADR later. Recorded now so it is a known commitment rather than a surprise found after adopters already hold both. FORCED WORK THAT IS NOT AN ADR (routes as GHI or chore, per the canon that a GHI is its own work order and needs no ceremony wrapped around it): the 56-constant triage against the shrink-only roster; the 49-reader migration; retiring data/ once emptied, together with moving the config_registry/waiver_ratchet exhaustiveness scope off it in the same change; and the pass making threshold failures name their logical key, noted but not required by the 2am ruling.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. FILENAME ADDRESSING (load_registry(root, 'audit_thresholds.json')): REJECTED by operator ruling 2026-09-20. Callers would never change again, but the post-config API would permanently encode the pre-config layout, and every reader migrates exactly once anyway.
2. ONE PHYSICAL FILE: REJECTED — mixes tunable thresholds with 50-entry shrink-only rosters in one document.
3. ENTRY POINT, FILES STAY PUT: REJECTED — 'single surface' becomes a code contract with no visible directory, which is the state that produced the problem.
4. ROSTERS INSIDE THE SETTINGS SURFACE: REJECTED by operator ruling — nobody tunes measured debt, and housing it as settings invites editing it as settings, the laundering ADR-0.0.73 Boundary Invariant #8 forbids.
5. DO NOTHING BEYOND THE 2026-09-20 FENCES: REJECTED — the three ratchets stop growth but repair nothing; 19 unsourced registries and 56 constants remain.

## Forcing Functions

<!-- The seven techniques `gz-adr-create` SKILL.md declares non-negotiable, plus
     its closing question. Agent drafts each against session evidence; the
     operator audits, names what was missed, and confirms
     (AGENTS.md § OPERATOR ECONOMY OF EFFORT #4) — this is agent labor, not
     operator typing. -->

### Pre-Mortem

OPERATOR-RANKED 2026-09-20, verbatim: '2 is the likeliest — the debt class leaking back in.' The agent drafted four scenarios and the operator selected the boundary leak over the unmigrated-readers, drifted-mapping and untriaged-constants failures. CONSEQUENCE FOR THE DESIGN: the settings/debt boundary is the ADR's load-bearing seam and must carry a mechanical witness, not a stated separation. A check that refuses a tunable value inside a debt roster, and a debt roster inside the settings surface, is a REQUIRED deliverable rather than a hardening nicety. Precedent for what happens without one: the 'no parallel systems' discipline has been declared in .gzkit/chores/hardcoded-root-eradication since 2026-04 and had 50 live violations on 2026-09-20.

### What Would Have to Be True

Four conditions must hold for the logical-key entry point with debt as a separate class. (A) The settings/debt split is decidable by a mechanical rule rather than per-file judgment. (B) Logical keys outlive the file layout, so the key vocabulary is more durable than the directories and callers migrate exactly once. (C) Each of the 56 rostered constants falls cleanly into operator-tunable or correctness-critical. (D) A single entry point does not become something readers route around for import-cycle or load-order reasons. OPERATOR-RANKED 2026-09-20: A is the shakiest. This does not add a second risk; it converges with the operator's pre-mortem ranking on the same seam, so the settings/debt boundary is both the likeliest failure and the condition the decision most depends on. CONSEQUENCE: the ADR cannot discharge this by stating a rule in prose. The rule must be executable, and if the distinction turns out to require case-by-case judgment, the load-bearing deliverable cannot be built as specified and the decision itself needs revisiting rather than the implementation. MIRROR (for filename addressing to have been better): the current layout would have to be already correct and stable, so encoding it in the API cost nothing later. That condition is false as measured — 19 of 48 registries record no derivation, so the layout encodes inherited accidents rather than decisions. See docs/governance/config-derivation-census-2026-09-20.md; re-run its census script rather than trusting a transcribed figure.

### Constraint Archaeology

THREE CONSTRAINTS, CLASSIFIED. (1) The five airlineops principles — INHERITED, adopted verbatim by operator ruling, never re-tested in gzkit's context. Their last test was against airline datasets, not governance thresholds. The verbatim adoption is ruled and not reopened here; the inheritance is recorded so a later reader knows it was adopted rather than derived. (2) data/ as the config location — NEVER DECIDED. No ADR chooses it; it is where the first file landed and everything followed. OPERATOR RULING 2026-09-20, verbatim: 'everything living in data/ in airlineops had to do with its own history. if config/ makes more sense, then we don't have to continue the legacy.' Moving to config/ therefore overturns a habit, not a decision, and the legacy arrangement carries no preservation weight of its own. (3) Exhaustive ownership of data/*.json — REAL, decided 2026-09-20 under GHI #929, actively enforced by `gz validate --config-registry`. config_registry.json owns policy and thresholds; waiver_ratchet_registry.json owns the waiver/grandfather family; the two declare themselves jointly exhaustive and the gate fail-closes on any undeclared top-level registry. FINDING THAT CHANGES THE DESIGN: the settings/debt partition ALREADY EXISTS MECHANICALLY for top-level data/*.json. The shakiest WWHTBT condition is therefore not 'can a decidable rule be invented' but 'can the rule that already decides this be carried forward'. CONSEQUENCE: the MECHANISM carries forward — exhaustive declared ownership with consumers verified rather than asserted — while its data/-shaped implementation does not, per ruling (2). Building a second mechanism deciding the same question is refused by the 'no parallel systems' principle already adopted in the Decision, so that option needs no separate ruling. COUPLED RISK (DO IT RIGHT 1a): that exhaustiveness is scoped to TOP-LEVEL data/*.json by filename glob. Moving files into categorical subdirectories breaks the glob, silently un-fencing the exact boundary this ADR depends on. The registry's scope must move in the same change as the files, and the fence must additionally reach the module-constant channel, which no data/*.json glob can see.

### Assumption Surfacing

THE UNDOCUMENTED ASSUMPTION: every reader of gzkit's self-config tolerates that config being ABSENT. In an adopter repository `project_root / 'data'` does not exist, and the built wheel carries ZERO data/ entries (measured against dist/py_gzkit-0.34.7-py3-none-any.whl, 2026-09-20). Each of the 49 rostered readers returns a documented default instead of failing. This holds by CONVENTION — 49 authors each remembering — with no invariant stating it and no gate enforcing it. src/gzkit/quality.py states the consequence in its own docstring: 'this speedup is gzkit's own and adopters are unaffected rather than broken. Shipping it to them would mean inventing a package-data surface, which is scope this change does not carry.' INVERSION (what if the opposite were true): a single entry point moves this risk in both directions at once. One loader can enforce absent-surface tolerance in ONE place rather than 49, which is strictly better than the status quo. But a loader that hard-fails on a missing surface converts 49 independent safe defaults into ONE shared hard failure in every adopter repo. Absent-surface tolerance must therefore be a tested invariant of the entry point, not a property the implementation happens to have. OPERATOR RULING 2026-09-20, verbatim: 'this is config for gzkit, it should live in .gzkit/config, adopters will develop their own approach. However, gzkit's init will provide strongly opinionated defaults the same way django-cookie-cutter does/did. make sense? I know this is hard because gzkit is being used to bootstrap gzkit.' WHY THIS DISSOLVES THE AMBIGUITY RATHER THAN MANAGING IT: today `project_root / 'data'` means 'gzkit's development thresholds' when self-hosting and 'a path that does not exist' in an adopter repo — one expression with two meanings, which is what made the tolerance invariant invisible. `project_root / '.gzkit' / 'config'` means 'THIS project's config' in BOTH contexts and is correct in both. The packaging question does not need a package-data surface: the wheel ships TEMPLATES and `gz init` scaffolds opinionated defaults, which is the mechanism .gzkit/ already uses for every other governance surface it holds. COLLISION TO RESOLVE AT DECOMPOSITION: `.gzkit/governance/` already exists as a sibling, so a `.gzkit/config/governance/` subdirectory would place two different 'governance' surfaces one level apart. The categorical subdirectory names must be chosen against the existing .gzkit/ tree, not against a bare config/ root.

### The 2am Operator Question

<!-- gz-validate-skip: command-shape -->
REQUIRED DELIVERABLES (operator ruling 2026-09-20, selecting from five drafted needs): (1) MALFORMED-SURFACE BEHAVIOUR IS A SPECIFIED, TESTED CONTRACT. Absent-surface tolerance covers a MISSING file; a syntactically invalid settings.json is a different failure and the likelier one at 2am, because the operator editing it caused it. Left unspecified, a trailing comma bricks every gz command at once — strictly WORSE than the 49-reader status quo it replaces, where one malformed file broke one reader. A single entry point concentrates this risk and must therefore carry the contract explicitly rather than inheriting whatever json.loads raises. (2) `gz config show <key>` REPORTS THE EFFECTIVE VALUE AND ITS SOURCE LAYER. With three merge levels (init-scaffolded defaults, settings.json, settings.local.json) a failing threshold could come from any of them, and nothing in the design provides provenance on read. Without this the 2am path is reading three files and simulating the merge mentally. The same command answers the second 2am question — whether a knob exists at all — which the operator cannot be expected to remember across a 56-entry triage. NOTED, NOT REQUIRED (operator declined as deliverables; recorded so the decomposition sees them): (a) The local override is not gitignored. Verified 2026-09-20: .gitignore covers `.gzkit.yaml.local` and `.claude/settings.local.json`, with no pattern matching `.gzkit/config/settings.local.json`. Whoever lands the surface should treat this as coupled under DO IT RIGHT 1a rather than a separate task, since an un-ignored override is committed by accident on first use. (b) Threshold failures naming their logical key in the message, consistent with the existing rule that a validator's message names the rule and its recovery. Touches many call sites; a candidate for its own pass.

### Reversibility

ASYMMETRIC: the directory is a two-way door, the key vocabulary is a one-way door. DIRECTORY — TWO-WAY AND CHEAP. Logical keys make file layout an implementation detail, so reorganising .gzkit/config/ later costs no caller changes. This was demonstrated rather than asserted: the entry point moved from config/ to .gzkit/config mid-interview at zero cost, precisely because nothing addresses a file by name yet. KEY VOCABULARY — ONE-WAY. Once 49 readers call load_registry('thresholds.audit'), that string is the API. Renaming a key is a breaking change in a way moving a file is not. The expensive mistake available in this ADR is naming keys badly, not laying out directories badly. MIGRATION — IN BETWEEN. Reverting means touching 49 call sites again: tedious, not blocked. TIMING IS THE DECIDING FACTOR. Nothing outside gzkit depends on the key vocabulary today, so it is still fully reversible. When the downstream init ADR ships opinionated defaults to adopters, those keys become a public contract and the door closes. Landing this ADR BEFORE that one is what keeps the vocabulary two-way, which is a property of the sequencing already chosen rather than a new constraint. OPERATOR RULING 2026-09-20: the reading holds, and a KEY-NAMING DISCIPLINE is a required checklist deliverable — fixing the key grammar before 49 callers adopt it: what a segment denotes, how many levels a key carries, singular versus plural, and how a key is retired when it turns out wrong. Cheap to decide now and unpayable once keys reach adopters. Deciding it once is the difference between one vocabulary and 49 individual choices, the latter being how the present 48-file sprawl accumulated.

### Scope Minimization

IRREDUCIBLE CORE — FOUR THINGS: the entry point, the key grammar, the mechanical settings/debt fence, and the tolerance contract covering BOTH absent and malformed surfaces. The fence because the operator's pre-mortem ranking and the shakiest WWHTBT condition converged on that same seam independently. The key grammar because it is the one-way door. The tolerance contract because without it a single entry point is a REGRESSION against the 49-reader status quo rather than an improvement. CUT UNDER HALF THE TIME, IN ORDER: (1) The 56-constant triage — judgment work, already rostered and shrink-only, proceeds one constant at a time indefinitely once the surface exists. Cutting it blocks nothing. (2) The 49-reader migration — the operator's migrate-once-after-the-surface ruling means the surface must exist first regardless, and once the vocabulary is fixed the migration is mechanical. (3) The categorical subdirectories — start flat. Keys hide layout, and that door was demonstrated two-way when the entry point moved from config/ to .gzkit/config mid-interview at zero cost. Three of the four authored subdirectories are an organisational preference, not a requirement, because the addressing scheme already makes layout invisible to callers. CANNOT BE CUT AT ANY BUDGET: the fence, the tolerance contract, the key grammar. If only those three land, the class is closed and everything remaining is cleanup that can proceed at leisure. OPERATOR RULING 2026-09-20: the core holds, and the CHECKLIST IS ORDERED CORE-FIRST — briefs sequenced so entry point, key grammar, fence and tolerance contract land before migration and triage. The class closes at the earliest possible point and the remaining work becomes interruptible without leaving a half-built surface; migration and triage are the tail, never the gate.

### Downstream Decisions Forced

TWO FORCED ADRs (operator ruling 2026-09-20: both are real, record both). (A) INIT-SCAFFOLDED ADOPTER DEFAULTS. Operator-ruled downstream during this interview. This decision creates a config shape adopters need and `gz init` does not provide, to be delivered 'the same way django-cookie-cutter does/did' (operator verbatim). Forced because the internal surface establishes a shape that adopters must be given deliberately rather than left to reinvent. (B) WHETHER GzkitConfig AND .gzkit/config CONVERGE. Decision item 5 keeps GzkitConfig as the adopter-facing schema while this ADR builds a separate internal surface. That is coherent while the surface is gzkit-only. The moment ADR (A) ships .gzkit/config to adopters, an adopter repository holds TWO config concepts, and something must rule whether that is intentional layering or duplication — the latter being refused by the 'no duplication' principle adopted in item 1. This question is invisible today precisely because only gzkit has the internal surface, and it becomes unavoidable exactly one ADR later. Recorded now so it is a known commitment rather than a surprise found after adopters already hold both. FORCED WORK THAT IS NOT AN ADR (routes as GHI or chore, per the canon that a GHI is its own work order and needs no ceremony wrapped around it): the 56-constant triage against the shrink-only roster; the 49-reader migration; retiring data/ once emptied, together with moving the config_registry/waiver_ratchet exhaustiveness scope off it in the same change; and the pass making threshold failures name their logical key, noted but not required by the 2am ruling.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.39.0 | Pending | | | |
