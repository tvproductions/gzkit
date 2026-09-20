# Big-picture skill: bounded synthetic writing evaluation

Date: 2026-09-19. Persona: main-session — craftsperson, governance-aware, whole-file-reasoning, direct.

## Scope and method

Read the complete canonical [skill](../../.gzkit/skills/gz-big-picture/SKILL.md), including its inline examples and quality guidance (version 0.1.1). The examples were initially read as a reference file and were reread after being moved unchanged into the self-contained skill. Applied its writing instructions to the two supplied synthetic cases below, with no other project facts. The evaluator authored the samples and assessed them; this is not a blinded comparison or an independent human usefulness verdict.

These are fictional evaluation specimens, not reports about gzkit or an actual adopting project. They are retained here as evaluation evidence only. No publication command was invoked, no report-history entry was created, and no ledger event was emitted by this evaluation.

The inputs have no reporting dates, revisions, detailed architecture documents, or primary observation records. Both samples make that limitation visible. Their evidence cutoff is the supplied fixture as read on this evaluation date, not a claim that the fictional observations occurred today.

## Case 1: software delivery and adoption diverge

### Supplied fixture

> “software project has 200 merged commits/500 passing tests, onboarding still requires maintainer help for 4 of 5 new users; prior report predicted self-service; new architecture separates adapters but no external deployment yet.”

### Sample narrative

The project has made substantial implementation progress, but its intended move toward self-service use remains unfulfilled in the observed onboarding cases. Four of five new users still needed maintainer help. That experience outweighs the volume of merged changes when assessing the earlier report's expectation that users could get started independently.

The 200 merged commits and 500 passing tests establish delivery activity and reported verification. They do not tell us how much new user value was delivered or whether the tests cover the difficulties encountered during onboarding. The project's underlying customer problem is absent from this evidence, so its broader value proposition cannot yet be assessed. What is clear is that independent adoption remains a practical constraint: maintainers are still part of most observed users' route into the product.

Separating adapters gives the architecture a clearer boundary around integration-specific behavior. That could make adoption across environments easier, but no external deployment has yet tested that possibility. The observed onboarding difficulties may sit in integration, documentation, packaging, or another part of the experience; the evidence does not locate their cause. The architectural question is whether the new boundary resolves real adoption friction or mainly improves internal organization.

The earlier self-service expectation therefore needs revision. The project is progressing as an implementation, while independent use remains unproven and most observed onboarding attempts required assistance. The consequential next evidence would connect the points where users needed help to the changes intended to remove that dependency, then show what happens when a new user encounters the product without that help.

### Evidence appendix

| Source | Supports | Limits |
|---|---|---|
| Supplied case 1 fixture, delivery counts | 200 merged commits; 500 passing tests | No commit period, test scope, or verified artifacts supplied |
| Supplied case 1 fixture, onboarding observation | Maintainer assistance for 4 of 5 new users | Small observed group; cause and sampling method unavailable |
| Supplied case 1 fixture, prior-report statement | Earlier expectation of self-service | Original wording, date, and forecast horizon unavailable |
| Supplied case 1 fixture, architecture and deployment | Adapter separation; no external deployment yet | No measured effect on adoption or architectural implementation details |

### Assessment

**Factual support:** The sample preserves every supplied fact without presenting counts as outcomes. It qualifies the prior forecast because its date and horizon are unknown. The potential benefit of adapter separation is explicitly hypothetical. It does not infer a particular onboarding root cause or invent the product's purpose.

**Explanatory usefulness:** The main tension is immediately visible: implementation progress and independent adoption are different dimensions. The narrative connects architectural investment to the user outcome it might enable and identifies evidence that would resolve the uncertainty. Its admitted inability to assess the broader value proposition is more useful than a fabricated mission statement.

## Case 2: scientific adopter with limited evidence

### Supplied fixture

> “scientific adopting project has reproducible rerun of 1 dataset, documentation for 3 instruments, only 1 adapter actually tested; no campaign or prior report.”

### Sample narrative

The project's strongest demonstrated value is a reproducible rerun of one dataset. That provides a concrete basis for confidence in repeating work within the observed setting. It is an initial capability worth preserving, although the evidence does not establish whether the scientific result is valid, whether another dataset would behave the same way, or whether another research group can reproduce the process.

The available materials suggest an ambition to serve several instruments: three are documented, while only one adapter has been tested. Documentation makes the intended reach visible; observed behavior currently supports a narrower claim. The identities of the documented instruments, the tested adapter, and the rerun dataset are not provided, so even their relationship remains uncertain.

The adapter boundary is the architectural point where broader applicability will need evidence. It may let the project accommodate instrument differences without changing the rest of the workflow, but that design benefit has not been demonstrated by the supplied facts. A successful rerun and a successful adapter test answer different questions; neither alone establishes portable scientific use.

This first report establishes a baseline rather than a trend. There is no prior report or dated sequence from which to infer acceleration, delay, or improvement. The project has evidence of repeatability in one setting and documented intentions beyond it. Its next significant increase in demonstrated value would be showing that the approach works across another relevant instrument or dataset, with enough provenance to explain what was reproduced and under which conditions.

### Evidence appendix

| Source | Supports | Limits |
|---|---|---|
| Supplied case 2 fixture, rerun | Reproducible rerun of one dataset | No scientific validation, independent replication, or provenance details supplied |
| Supplied case 2 fixture, documentation | Three instruments documented | Documentation does not establish implementation or operation |
| Supplied case 2 fixture, adapter testing | One adapter tested | Its identity, test scope, and connection to the dataset are unspecified |
| Supplied case 2 fixture, planning/history | No campaign or prior report | Baseline only; no observed longitudinal trajectory |

### Assessment

**Factual support:** The sample does not import the writing reference's fictional provenance implementation, acquisition/analysis separation, previous report, or delivered traceability. It names the missing relationships among dataset, instrument, and adapter. Scientific validity and repeatability remain distinct.

**Explanatory usefulness:** It explains why the observed capability matters while keeping the applicability claim appropriately narrow. It uses scientific terminology without requiring campaign machinery. Architecture is discussed as a question to investigate, not as an invented implementation fact.

## Findings and limits

No actionable defect in the skill's writing instructions was demonstrated by these two exercises. The instructions successfully supported different narratives, contrary evidence, a missing purpose statement, an absent campaign, and an absent prior report. The reference examples did not force either sample to repeat their factual claims.

The instruction to cover purpose is compatible with stating that purpose evidence is missing; it should not be interpreted as permission to invent it. The instruction to discuss trajectory likewise permits a first-report baseline with no longitudinal claim. Both boundaries are already supported by the skill's requirement to disclose unavailable evidence.

This bounded evaluation establishes that one evaluator could apply the instructions coherently to two supplied cases. It does not establish repeatability across models, reliable source retrieval, actual operator usefulness, or successful publication and retention. Those claims require their own evidence. No numerical score is assigned because no calibrated scoring scale or independent grader was supplied.
