# GovZero command doctrine

*A back-port of the aircrew accountability framing into the philosophy layer of GovZero and gzkit*

Status: Canonical doctrine (philosophy layer)
Ratified: 2026-06-10 (operator-ratified relocation from working draft)
Authority: Philosophy layer of the Four P's stack — policies, procedures, and practices trace upward to these articles (Article 10). The [GovZero Charter](charter.md) remains the sole authority for gate definitions; this doctrine is what those definitions trace to.
Companion: the Sprint and Drift essay "The left seat." Implementation worklist tracked in `ADR-pool.command-doctrine-internalization`.

## Why this document exists

GovZero has always had procedures (the five gates) and practices (gzkit, the session discipline, the attestation records). What it has had only implicitly is the layer Degani and Wiener (1997) put first in their Four P's model of cockpit operations: an explicit operating philosophy from which policies derive, from which procedures derive, from which practices follow. Their field finding is the reason the gap matters. Procedures that no longer trace visibly to a philosophy are the procedures operators stop complying with, and the operator most likely to stop complying with GovZero under deadline pressure is me.

The gap has a second cost that is newly urgent. Each model release arrives with vendor guidance about what the model prefers, and without an explicit philosophy there is no principled way to decide which of those preferences to accommodate and which to refuse. The scaffolding audit becomes vibes. With the philosophy written down, the audit becomes mechanical: anything in the apparatus that exists to compensate for model weakness is negotiable and retires as models improve; anything that exists to implement the philosophy is not negotiable and survives every release. The aviation record supplies the philosophy almost ready-made, because aviation spent fifty years deciding what survives improvement in the automation. This document writes it down.

## The Four P's, applied

**Philosophy** is the command doctrine below: ten articles stating what GovZero believes about authority, accountability, and automation, independent of any model, vendor, or tool.

**Policies** are the standing decisions that implement the doctrine in this practice: the five gates exist; a human attests before work ships; autonomy span is bounded; evidence means artifacts.

**Procedures** are the gate definitions, the briefing template, the attestation record schema, the substitution rules. Procedures are model-generation-specific and expected to change.

**Practices** are what actually happens in gzkit sessions, including the drift between procedure as written and procedure as flown. The drift is data. When practice diverges from procedure persistently, either the procedure has stopped tracing to the philosophy and should be fixed, or the practice is a compliance failure and should be named as one. The Four P's give the diagnostic: trace the divergent item upward and see where the chain breaks.

## The command doctrine

### Article 1. Accountability is non-transferable

One human signs for the work. The signature does not move to the model, the harness, the vendor, or the gate that passed. This is the GovZero analogue of 14 C.F.R. § 91.3, and the welding matters as much as the assignment: direct responsibility and final authority are one clause, not two. Whoever holds the signature holds override authority over every other element of the pipeline, and whoever holds override authority holds the signature. Any proposal that separates them, in either direction, is rejected on its face.

### Article 2. Authority must be instrumented, not asserted

A captain's authority over a human crew rests on shared consequences and a common operating manual. The model shares neither. It follows that command over a model is exactly as real as the harness that enforces it, and no more. Authority asserted in the context window is a briefing: necessary, and unenforceable. Authority implemented in the harness, in CI rules, file checks, diff gates, and halt conditions, is the only kind the model actually answers to. Every article below that imposes an obligation on the model is therefore really an obligation on the harness. If the harness does not enforce it, the doctrine does not contain it.

### Article 3. The model is a crew resource, not a crew member

Crew resource management never promoted the first officer to command; it obligated the whole crew to keep the commander informed and made silence a violation (Helmreich et al., 1999). The same allocation applies here, in both directions. The model is used fully: it drafts, flags, surfaces, challenges, and proposes, and a practice that underuses a capable model is leaving crew resources idle, which CRM treats as a failure. And the model decides nothing that ships. Its challenges are inputs to judgment, never substitutes for it. Designing the harness so the model can effectively surface concern is part of the doctrine; treating surfaced concern as approval is a violation of it.

### Article 4. Uncommanded change is an annunciation failure

The documented tendency of strong models to tidy beyond scope, draft unrequested artifacts, and create defensive backups is not enthusiasm. It is the software equivalent of uncommanded control inputs, and the mode-error literature says what unannunciated state divergence does to a supervisor's situation awareness (Sarter & Woods, 1995). The doctrine response: every run is preceded by a scope manifest, every run is followed by a diff of delivered work against commanded scope, and every artifact outside the manifest is annunciated before the run can pass any gate. The model is not asked to behave. The harness is built to notice.

### Article 5. Model identity is an attestable fact

Current releases can decline a request at the API layer and complete it on a different model, and routing, fallback, and substitution will only proliferate. An attestation that does not record which model produced the work attests less than it claims. The attestation record therefore carries the served-model identity for every gated artifact, and substitution is handled the way airline dispatch handles inoperative equipment: by explicit prior relief, not silent acceptance. A standing substitution policy states which fallbacks are acceptable for which classes of work. A substitution outside the policy fails the gate. A substitution inside the policy is recorded, not waved through.

### Article 6. Autonomy span is set by attestation capacity, not model endurance

Models can now run for hours. The attestor still reviews at human speed, and evidence accumulates faster than review capacity as run length grows. Letting the model's endurance set the checkpoint cadence is letting the autopilot decide when the pilot looks up. The doctrine sets it the other way: a run is capped at the volume of change one attestation can honestly cover, as a configured policy parameter, revisable deliberately and never by drift. When a model release extends what is possible, the parameter is re-decided, not silently inherited.

### Article 7. Evidence is artifacts, not narration

A model's account of its own reasoning is generated output, carrying the same verification burden as everything else it generates, and the current releases largely decline to provide it anyway. GovZero loses nothing, because the gates never properly rested on narration. Evidence is the ADR, the failing-then-passing test, the diff, the Gherkin scenario, the recorded model identity, the scope-conformance report: artifacts the model cannot retroactively edit and the attestor can independently check. Where self-narration was being used as comfort, retire it. Where its absence hurts, the hurt is diagnostic visibility, and the remedy is better artifacts, not pleas for testimony.

### Article 8. Efficiency is a constraint, not the objective

Token economics is fuel planning: a real discipline, practiced seriously, and never the reason the flight exists. The throughput frame optimizes output per token and carries no liability term in its objective function; the doctrine adopts its techniques and rejects its objective. Minimum fuel is a hazard, and a pipeline optimized to the edge of its verification budget is the software version of landing on fumes. The early empirical record points the same direction: in fully automated pipelines, verification, not generation, dominates token cost (Salim et al., 2026). Spending to verify is not overhead on the work. On the current evidence it is most of the work.

### Article 9. Proficiency is maintained deliberately

Automation that performs continuously degrades the supervisor's ability to perform when it stops, and the aviation regulator's remedy was scheduled manual operation in revenue service, not nostalgia for hand-flying (Federal Aviation Administration, 2013). The enterprise field record now shows the same erosion channel in knowledge work: workers using generative tools can complete tasks without retaining what the task would have taught, doing without learning (Armstrong & Shah, 2026). The drift phase is GovZero's equivalent, and this article makes it doctrine rather than temperament: deliberate intervals of unassisted work, scheduled and logged, scoped to the skills the practice cannot afford to lose. The schedule is reviewed like any other safety-critical maintenance. Skipping it under deadline pressure is exactly the failure mode the aviation record predicts, because deadline pressure is when the automation is leaned on hardest.

### Article 10. Procedures earn compliance through coherence

Every gate, check, and template in gzkit must trace upward through a policy to an article of this doctrine. Anything that cannot be traced is either workaround scaffolding for a past model generation, which retires on its own schedule, or accumulated ritual, which retires now. This is Degani and Wiener's finding turned into a maintenance rule: incoherent procedure is what breeds noncompliance, so coherence is audited, not assumed. The audit runs at every major model transition, and its two questions are fixed. Does this item implement the doctrine? Then it stays, whatever the vendor guidance prefers, and any output-quality cost is paid knowingly and measured. Does it compensate for a model weakness? Then it is benchmarked against the current release and retired the day it stops earning its place. The cure for procedural drift is not fewer procedures. It is procedures that visibly mean something.

## What changes in gzkit

The doctrine implies a concrete worklist. Each item below names the article it implements.

**Briefing template (Articles 2, 4, 10).** Replace heavyweight in-prompt scaffolding with a captain's-brief structure: scope manifest, stop conditions, expected artifacts, explicit prohibitions on out-of-scope change. Brief and complete are compatible; the template enforces both. Everything removed from the prompt either moves into the harness or is retired by the Article 10 audit.

**Refusal and substitution handling (Article 5).** The harness branches explicitly on API-level refusals rather than treating any successful response as usable output. The attestation record gains a served-model field. A substitution policy file states acceptable fallbacks per gate class, and the gate runner enforces it.

**Scope-conformance report (Article 4).** A post-run check diffs delivered changes against the scope manifest and annunciates every unrequested artifact, backup, or tidy. The report is a gate precondition, not advice.

**Autonomy span parameter (Article 6).** A configured cap on change volume per attestation unit, with a documented re-decision procedure tied to model transitions. The cap appears in the attestation record so its observance is itself attestable. The cap's calibration can be empirical rather than intuitive: validated supervisory-control instruments measure the supervisor directly, with SAGAT estimating situation awareness and NASA TLX measuring mental workload, and Armstrong and Shah (2026) propose exactly this instrumentation for generative AI oversight roles. Measuring the attestor, not just the model, turns the doctrine's most judgment-dependent parameter into one that tracks observed review capacity.

**Proficiency log (Article 9).** Drift sessions get scheduled and recorded alongside the other governance artifacts, with the skill domains under maintenance named. The log makes skill retention auditable the same way the gates make work auditable.

**Coherence audit (Article 10).** A standing checklist run at each major model transition: trace every gzkit item to an article, benchmark every compensation item against the current release, record what was retired and what was retained at known cost. The audit record is the practice's own answer, in advance, to anyone arguing the apparatus is superstition.

## A note on the standing argument

The throughput position and this doctrine will keep colliding, and the collision is healthy when it is framed correctly. The throughput position answers "how much per token." The doctrine answers "who is in charge here, and who is liable." Both questions are real. Only one of them has an answer that survives a deposition. When a technique from the throughput world improves output per token without moving the signature, adopt it gratefully. When it improves output per token by moving the signature, the doctrine already says what happens, in twenty-three words it borrowed from Part 91.

## Appendix A — Article-to-surface trace

Seed of the Article 10 coherence audit. Each row traces an article to the gzkit surfaces that implement it today; gaps are tracked in `ADR-pool.command-doctrine-internalization`. This table is the audit's working baseline and is re-walked at every major model transition.

| Article | Implementing gzkit surface | Status |
|---|---|---|
| 1 — Accountability is non-transferable | Universal OBPI attestation (ADR-0.0.36; `AGENTS.md` § Universal OBPI Attestation); canon-owner attestation directive (`.claude/rules/governance-core.md`); Charter § Authority Boundary | Implemented |
| 2 — Authority must be instrumented, not asserted | Validator scopes (`gz validate`), pre-commit hooks, ARB middleware ([arb-middleware](../arb-middleware.md)), pipeline runtime; appraised in [harness-engineering-appraisal](../harness-engineering-appraisal.md) | Implemented — the operating thesis |
| 3 — The model is a crew resource, not a crew member | Personas (`.gzkit/personas/`); push-back rule (`AGENTS.md` § Behavior Rules — Always #10); subagent doctrine (Always #5, #6) | Largely implemented |
| 4 — Uncommanded change is an annunciation failure | OBPI brief Allowed Paths; `gz validate --brief-reconcile`; surgical-changes rule (`AGENTS.md` § DO IT RIGHT #11) | Partial — no post-run delivered-vs-commanded scope-conformance gate |
| 5 — Model identity is an attestable fact | (none — no served-model field in attestation or receipt schemas under `src/gzkit/schemas/`) | Gap |
| 6 — Autonomy span is set by attestation capacity | [OBPI Decomposition Matrix](obpi-decomposition-matrix.md) sizes by intrinsic complexity, not attestation capacity | Gap, with a named tension — the matrix must reconcile to this article |
| 7 — Evidence is artifacts, not narration | ARB receipts (`AGENTS.md` § Attestation canonical invocations); ledger Layer-2 truth ([state-doctrine](../state-doctrine.md), [trust-doctrine](../trust-doctrine.md)); `@covers` test discipline | Implemented — strongest alignment |
| 8 — Efficiency is a constraint, not the objective | Anti-vibing mantra (`AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT, operative claim 1: "lighter ceremony" is never the tradeoff axis) | Implemented |
| 9 — Proficiency is maintained deliberately | (none — no proficiency log, no scheduled drift sessions) | Gap |
| 10 — Procedures earn compliance through coherence | Advisory-rules scorecard ([advisory-rules-audit](../advisory-rules-audit.md); `gz validate --advisory-scorecard`); [model-regression taxonomy](../model-regression-taxonomy.md) F1–F10 | Partial — no trace-to-article column, no model-transition trigger |

## References

Armstrong, B., & Shah, J. (2026). *Humans in the loop: The evolution of work in early experiments with generative AI*. MIT Industrial Performance Center. https://ipc.mit.edu/wp-content/uploads/2026/04/Humans_in_the_Loop_full_r01M.pdf

Degani, A., & Wiener, E. L. (1997). Procedures in complex systems: The airline cockpit. *IEEE Transactions on Systems, Man, and Cybernetics, Part A: Systems and Humans*, *27*(3), 302–312. https://doi.org/10.1109/3468.568739

Federal Aviation Administration. (2013). *Manual flight operations* (Safety Alert for Operators 13002). U.S. Department of Transportation.

Helmreich, R. L., Merritt, A. C., & Wilhelm, J. A. (1999). The evolution of crew resource management training in commercial aviation. *International Journal of Aviation Psychology*, *9*(1), 19–32. https://doi.org/10.1207/s15327108ijap0901_2

Responsibility and authority of the pilot in command, 14 C.F.R. § 91.3 (2026). https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-A/section-91.3

Salim, M., Latendresse, J., Khatoonabadi, S., & Shihab, E. (2026). *Tokenomics: Quantifying where tokens are used in agentic software engineering* (arXiv:2601.14470). arXiv. https://arxiv.org/abs/2601.14470

Sarter, N. B., & Woods, D. D. (1995). How in the world did we ever get into that mode? Mode error and awareness in supervisory control. *Human Factors*, *37*(1), 5–19. https://doi.org/10.1518/001872095779049516
