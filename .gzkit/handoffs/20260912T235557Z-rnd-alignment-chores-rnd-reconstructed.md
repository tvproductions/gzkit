---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-12T23:55:57Z'
agent: claude-code
session_id: bdd5d76b-125a-44fc-8aad-1cb21c2d5000
continues_from: .gzkit/handoffs/20260912T215448Z-rnd-chore-class-and-mpas.md
---

## Current State Summary

**This handoff supersedes `20260912T215448Z-rnd-chore-class-and-mpas.md`, which the operator rejected** — verbatim: "shitty handoff that misses the major chore and R&D work - very disappointing". It is reconstructed from the session 5f61ae2b transcript (every operator turn 20:01Z–21:49Z and the agent's design replies), not from the rejected document, which was a thin pointer to two design records and relayed as a six-step chore checklist.

Session 5f61ae2b was an R&D run. It opened with the operator pasting a "Python Codebase Architecture Guidelines" document against the pythonic chores, and the operator widened it to the question actually being asked (20:22Z): "I am trying to get front end and audit/refactor back-end alignment. Ensure that rules, tools, audits and refactors all agree. I am trying to tighten up how gzkit does its best to have good Python/software architectures and implmentation, as much as possible."

Three threads came out of it, and all three carry operator rulings:

1. **Rules / tools / audits / refactors alignment — the originating goal.** A mile-high map of four estates and the edges missing between them, plus a disposition of the pasted document. **Recorded in no committed artifact; this handoff is its only carrier.**
2. **The chore class system.** Five classes, four rungs, staleness as an announced indicator, the suppression prohibition. Recorded in `docs/governance/chore-class-system.md`, but that record's body omits the operator's conversion directives and several research findings (see Important Context).
3. **The R&D discipline.** R&D named as the headwater of most gzkit design, to be governed by a new standalone agent skill built on gzkit-aligned appropriation of Matt Pocock's skills (MPAS). Recorded in part in `docs/governance/mpas-appropriation-analysis.md`; the rejected handoff demoted it to a trailing "then" item with three open forks.

Nothing was implemented. After authoring the rejected handoff, session 5f61ae2b did unrelated repair (commits `56af8297c` Codex role fidelity, `c3b6f86c8` negative-controls fixture), filed GHI #998, and ended in git-sync friction. At this authoring: no OBPI locks held, `main` level with origin.

## Important Context

### Thread 1 — alignment of rules, tools, audits and refactors (in no document)

Operator framing (20:15Z): "although this analysis was likely meant to be authoring advice, we resort to refactoring if agents/rules arent effective, do we have pythonic rules on the frontend? do we have any chore that aligns authoring rules to audit/refactoring chores?"

Findings, measured by session 5f61ae2b on 2026-09-12 — re-measure before citing any figure:

- **Four estates, three wired together.** Rules (`.gzkit/rules/*.md`, 163 scored clauses in the advisory scorecard), tools (ruff, ty, xenon, `gz validate` scopes), audits (the control-surface passes, tech-debt-review, intent-trace), refactors (the code-quality chores). Edges that exist: rule↔rule (Pass A, `control-surface-rule-conflicts`), skill↔rule (Pass B), rule prose↔check (Pass C plus the scorecard), check↔commit path (`control-surface-validator-reachability`). **Edges that do not: rule↔chore, and chore↔cadence.** The registry has no field in which a chore can name the rule it serves.
- **The asymmetry.** gzkit governs its governance more rigorously than its own code architecture. Control-surface chores ran within the month; most code-quality chores last ran 2026-07-31; the only `pythonic-design-pattern-detection` candidates report is dated 2026-04-26. 12 of 40 chores cite any rule file, and 5 of those 12 are the control-surface family. Clean lint reads as healthy code.
- **The weakest-witnessed family is the primary architecture directive.** `.gzkit/rules/hexagonal-architecture.md` scorecard rows 64–64e: 1 Mechanical, 3 Promotable, 2 Judgment. No `gz validate` scope can see a port. `pythonic.md` size limits (rows 19 and 20) are Judgment.
- **The missing middle scale.** Small scale (idiom, types) is claimed by `pythonic.md` and witnessed by ruff and ty on every commit. Large scale (ports and adapters) is claimed by `hexagonal-architecture.md`. The module/package boundary scale in between has **no rule and no witness**. Re-measured this session: 14 of 42 `__init__.py` under `src/gzkit` declare no `__all__` (including the package root and `commands/`); `src/gzkit/commands/common.py` is 702 lines. The session measured 94 of 99 `commands/` modules importing it; a narrower grep this session counts 74 — a probe difference, not yet a drift claim.
- **A mirror family, named in session: "mechanism running without doctrine."** A chore can refactor toward a shape no rule declares and leave a full proofs trail doing it. And the campaign box "Close the doctrine-declared-without-mechanism family" scores rule prose against validators only, so it can go green while the chore estate is never scored at all.
- **Disposition of the pasted document.** Already covered: `typing.Protocol` dependency inversion (hexagonal #4), functional core / imperative shell (pythonic #2), no implicit globals (pythonic #10), Singleton detection. Ruled against: group-by-domain folders and "screaming architecture" (hexagonal #7: `core/` stays; no domain/application/adapters folder partitions). Canon-closed: circular and lazy imports (`pythonic.md` § Imports, posture ACCEPTED 2026-08-08, reclassify "not on the count moving"). gzkit is better: hexagonal #5, formalize a port only on the second adapter. **The document is better on two points absent from every rule file:** declaring a package's public API (`__all__` plus `_`-prefixed internals), and prohibiting catch-all `utils` / `common` / `helpers` modules, with fan-in rather than length as the signal. Its numbers (500 lines, 10–15 imports) are not to be imported: thresholds come from `.gzkit/rules/complexity-thresholds.json`, never from a pasted document.

Operator ruling on this thread (20:30Z): witness, hexagonal, and rule-home questions are chore subjects under standing chore authorization, not doctrinal forks to put to the operator.

### Thread 2 — the chore class system: what the design record does not carry

- **Operator conversion directive (20:41Z), verbatim:** "the control-surface five stay diagnostic, the rest convert - update readme if we now see it as inadequate." Qualified in the same message: "the control-surface five *might* be exceptions, but they also may not. We need big picture calibration here." And: "Most should be suggesting fixes and solutions even if they stop at audit. even when they stop with results the intention is almost always a subsequent fix phase." And on the contradictory chores: "please fix/make consistent."
- **Class awareness, operator verbatim (20:53Z):** "uniformity within class is important to me - the chore system should be aware of these classes, how/why each class of chore should be handled uniformly and what the consequences of staleness means per class".
- **The five control-surface chores are not uniform.** `control-surface-rule-conflicts`, `control-surface-skill-rule-reachability` and `control-surface-validator-reachability` end in recommendations; `control-surface-rule-vs-check-drift` ends at a parity table and is one of the nine stop-at-data chores; `control-surface-permission-consent-drift` is audit-only and routes remediation to a GHI. `control-surface-validator-reachability` is not a sixth class: it is Coherence carrying a ratchet, and a ratchet is a policy on a finding count, not a class.
- **Research findings argued in session that appear only in the record's Sources list, not its body:**
  - Two separate licenses. **Idempotence licenses scheduling** (Google SRE ch. 7: fix scripts safe to run every 15 minutes). **Reversibility licenses writing** (OpenAI, Practices for Governing Agentic AI Systems). The session said each chore should declare both; the ratified field list carries neither explicitly. Reconcile against the ratified schema; do not add fields on this note alone.
  - **Consultation points are pre-declared in the chore definition, never computed at runtime from agent confidence** (Bainbridge, Ironies of Automation, 1983).
  - **Each consultation point names what the operator is for there** (Crootof, Kaminski & Price, 2023), otherwise it decays into a "stand-in". Curation is the likeliest rubber-stamp site.
  - **Consent versus exception** (Billings, 1997): the literature prefers management by consent; the operator wants management by exception; the reconciliation is predictable scope plus mandatory disclosure, and the staleness announcement and the ledger are the disclosure.
  - Escalate where the operator holds information the agent structurally cannot (Feng, McDonald & Zhang, 2025). Renovate's automerge rule is the operational form of pre-authorization; Terraform plan/apply is the mature form of the detection→application split.
- **Found this session (bdd5d76b):** GHI #936 (open, defect), "chore currency gates are only readable by running the chore they gate", is already the work order for the status verb, and its Expected section puts the overdue announcement in `scripts/session_orientation.py`. GHI #997 (`eval-feedback-cluster` runs fixtures, not live clustering) and GHI #808 overlap members of the nine.
- **The rejected handoff's eleven operator rulings can never reach the rulings store.** Its Decisions Made entries had list markers but no `[operator-ruled]` attribution, so they parse as unattributed and are never promoted: `gz handoff rulings --search "class seams"` returns nothing. This handoff re-states them attributed; `create_handoff` promotes a handoff's `[operator-ruled]` decisions into the store when its SUCCESSOR is authored, so they arrive with the next handoff, not this one.
- The canonical registry is `src/gzkit/chores/registry.json`; `.gzkit/chores/registry.json` is the project-local surface. Schema work must respect the two-surface layout in `src/gzkit/chores/README.md`.

### Thread 3 — the R&D discipline: what the rejected handoff demoted

- **Operator (21:29Z), verbatim:** "R&D leads to: ==> 1)adr/opbi || 2)ghi/direct fix || 3)chores || 4)control surface/rules/docs/skills/structures/hooks || 5)broad one-shot refactorings/recalibations that are often system wide. Any of 1-5 could be impacted by an R&D run. So, I wouldn't trivialize the use of an R&D run, and I think an R&D run now MUST be governed by an overarching new AGENT SKILL, but I want to codify this and use gzkit-aligned appropriatios of selet MPS (Matt Pocock Skills) as a foundational basis." Take no action is a common sixth outcome.
- **Why it matters, operator verbatim:** "In fact MOST future ADRs come form work exactly like this work." And: "I suspect these Matt Pocock appropriations will become a new vector for how things enter into gzkit moving forward. not to replace gzkit workflow direction items and artifacts, but to have better structure to the exploratory and discursive sessions that usually predicate how new things, or refinements, enter into gzkit."
- **The trigger:** "Often I will drop in a large copy and paste and say 'let's consider this for gzkit' (I've done this VERY OFTEN), that is almost always an occasion for R&D EVEN IF the outcome is 'take no action'". Session 5f61ae2b is itself the worked exemplar: an externally motivated paste produced outcomes in class 2 (GHI #998), class 3 (the chore class system), class 4 (two design records), and class 5 in prospect (the middle scale).
- **Routing, with who initiates:** 1 ADR/OBPI — operator only (IRON LAW). 2 GHI — agent may file through `/ghi-author`. 3 chore — operator directs, R&D may advise, admission on recurrence evidence. 4 control, rule or intent surface — agent may draft. 5 one-shot refactoring or recalibration — direct engineering work, not a chore. R&D produces refactoring programs; chores produce refactoring candidates.
- **R&D sits at the propose rung.** The campaign's Workflow fronts already says research "does not automatically authorize a new ADR or implementation."
- **The "sensing but also direct executable" tension was tentatively resolved in session, not left open** as the rejected handoff claimed. Under MPAS's invocation-class invariant, sensing lives in model-invoked disciplines and direct execution in one user-invoked orchestrator that reaches only disciplines (`mpas-appropriation-analysis.md`, The mechanical rules worth taking wholesale, rule 1). Awaiting operator confirmation.
- **Agent self-correction in session:** hiding the downstream step is about separate skills, not separate contexts. MPAS keeps grill → spec → tickets in one unbroken context; hard breaks come at implementation and between wayfinder tickets.
- MPAS has no `/plan` and no `/refactor` skill: planning is `to-tickets` (one session) and `wayfinder` (many). `wayfinder` is the chargé d'affaires shape, and its "Plan, don't do" refusal is overridable in agent-written Notes, so gzkit's appropriation must carry a hard stop the source lacks.
- MPAS `domain-modeling` writes an ADR only when all three hold: hard to reverse, surprising without context, the result of a real trade-off.
- **Operator answer on which MPAS shapes to take:** "the whole system, but let's not get ahead of the subagents findings".
- `docs/governance/capability-control-review-2026-09-12.md` is an existing R&D artifact. Its "What this record does not license" section should be a required section of the R&D shape.
- **Promised in session and never delivered:** a `docs/governance/rnd-discipline.md` record, and campaign amendment text for the R&D front description "so you can ratify or redraft it in one pass".

## Decisions Made

- [operator-ruled] Ratified the chore class system in full: "I think the entire system surfaced from our discussion, and from the research is outstanding. I ratify, with great enthusiasm, the entire plan. I love the inclusion of suppression. I love the references to the external systems/exemplars and hope to maximally benefit from then."
- [operator-ruled] A chore is authorized maintenance labor, not an inspection: "A chore is authorized to find, analyze, solve and fix. I don't need to debate colling and taking out the trash from the house on a regular basis, I need to organize that tidying." A chore files a GHI "sparringly and in consultation with the operator".
- [operator-ruled] Witness, hexagonal and rule-home questions are chore subjects under standing authorization: "so witness, hexagonal, and rule would all be subject to this same pattern and premise to chores."
- [operator-ruled] Conversion directive: "the control-surface five stay diagnostic, the rest convert - update readme if we now see it as inadequate", qualified as "the control-surface five *might* be exceptions, but they also may not. We need big picture calibration here."
- [operator-ruled] Fix the internally contradictory chores: "so with 1. please fix/make consistent."
- [operator-ruled] Audit chores should still recommend: "Most should be suggesting fixes and solutions even if they stop at audit." The nine that stop at data are "an addressable shortcoming and needs rememdy".
- [operator-ruled] Every chore indicates its last run: "I maintain frequency, but each should at least indicate a 'last run' for relative staleness."
- [operator-ruled] Staleness is an announced indicator, gating only where the subject decays: "indicators, chores shouldn't have a bunch of gates like the adr/obpi system" and "staleness should be announced."
- [operator-ruled] Conversion is blast-radius dependent, option (c), governed by "chores likely organize along class seams"; "uniformity within class is important to me".
- [operator-ruled] The detection→application split stays: "that split is fine, it makes room for pause and operator consultation."
- [operator-ruled] Not all refactorings are chores: "not all refactorings are chores, but most chores cab lead to refactorings."
- [operator-ruled] Route for the chore class system: "Movement C box — discharge it there, no new ADR. but is not likely simple."
- [operator-ruled] New chores are operator-directed: "I will almost always direct that new chores are made, but I don't mind them being advise."
- [operator-ruled] An R&D run must be governed by a new overarching agent skill on a basis of gzkit-aligned MPAS appropriation: "I think an R&D run now MUST be governed by an overarching new AGENT SKILL".
- [operator-ruled] The R&D skill stands alone, with no ADR: "NO, the R&D skill stands alone and now assumes a great deal of power and responsibility - it is a chargé d'affaires for retaining and organizing possible outcomes from an R&D designing session." It "should be sensing but also direct executable."
- [operator-ruled] MPAS is appropriated, never onboarded: "I DO NOT want to onboard Matt's skills directly, but think we can appropriate" and "we'll examine what is appropriate for gzkit, and not the other way around".
- [operator-ruled] The R&D artifact form is deferred: "it is a document and maybe an artifact, it is premature at this stage. It will VERY LIKELY be first class (or the ledger will miss it, but don't forget out it can fan out."
- [operator-ruled] Take no action is a legitimate R&D outcome: "that is almost always an occasion for R&D EVEN IF the outcome is 'take no action,' which is also common."
- [operator-ruled] The design belongs in docs at full richness and the handoff prioritizes continuation: "write the FULL RICHNESS of the desing to a design documentment within the docs and point a fresh handoff to immediate prioritization of implementation" and "h/o should prioritize this work coninuation."
- [operator-ruled] The prior handoff is rejected: "shitty handoff that misses the major chore and R&D work - very disappointing".
- [agent-chose] Rebuilt this handoff from the session 5f61ae2b transcript rather than editing the rejected document, and left both committed design records unedited until the operator rules on folding the missing content into them.

## Immediate Next Steps

1. **Put the lost substance into durable records.** The operator asked for the design "at FULL RICHNESS" in docs; today this handoff is the only carrier of Thread 1 and of the Thread 2 research findings. Advised: add the alignment map and pasted-document disposition, the operator's conversion directives, and the licenses / consultation-point findings to `docs/governance/chore-class-system.md` (or a sibling alignment record), and the R&D routing table, worked exemplar and in-session resolutions to `docs/governance/mpas-appropriation-analysis.md`. Operator rules on placement.
2. **Chore class system, cadence before content — the ratified order.** (a) Registry schema: `class`, `rung`, `staleness.{signal,period,grace,paused}`, `remediation` (enum including `no_fix_planned` and `none_available`, details required), `non_authority`, `governing_rule`; an undeclared chore does not run. (b) `gz chores status` rendering current / due / overdue / paused, deriving last-run from proof commit dates by generalising `scripts/check_proof_freshness.py`, announcing and never gating, with the overdue announcement in `scripts/session_orientation.py` — this discharges GHI #936. (c) Class-conformance validator: a chore whose `CHORE.md` contradicts its declared rung fails. (d) `src/gzkit/chores/README.md` states what a chore is: classes, rungs, admission criterion, declaration requirement. (e) Per-chore declarations applying the conversion directive, fixing the three contradictory chores and remedying the nine. (f) The suppression prohibition written into a rule file.
3. **Alignment arm, once `governing_rule` exists.** A Pass D rule↔chore audit: chores with no governing rule, and rules whose only witness is a chore. The two middle-scale rule clauses — package API declaration into `hexagonal-architecture.md`, catch-all module prohibition with a fan-in signal into `pythonic.md` — land only together with their witness, because the Movement C box forbids adding Promotable rows. Then hexagonal's three Promotable rows.
4. **R&D skill design, in a fresh session.** Read both design records and Thread 3 of this handoff; confirm or overturn the tentative orchestrator-over-disciplines resolution; settle one skill versus orchestrator plus namespace; rule on `.out-of-scope/`; draft the campaign R&D-front amendment text for operator ratification.

## Pending Work / Open Loops

- **Work order for step 2.** GHI #936 covers the status verb. The schema, conformance validator, README, per-chore declarations and suppression rule have no GHI. The Movement C box discharges through "GHI-shaped direct repair"; one issue through `/ghi-author` is advised and unruled.
- **The nine stop-at-data chores, unfixed:** cli-contract-governance, control-surface-rule-vs-check-drift, dependency-currency, eval-feedback-cluster (see GHI #997), evidence-integrity-audit, frontmatter-ledger-coherence, repository-structure-normalization, skill-command-doc-parity, skill-trigger-testing.
- **The three contradictory chores, unfixed and operator-directed to fix:** frontmatter-ledger-coherence, repository-structure-normalization, skill-command-doc-parity.
- **Calibrate the control-surface five** against the class system before declaring them diagnostic; the operator said they "might" be exceptions.
- **Unreconciled:** the scheduling and writing licenses versus the ratified field list.
- **Campaign capture gap:** the Workflow fronts entry describes R&D as carrying hypotheses from one review document; the operator describes it as the headwater of most ADRs. Amendment text was promised in session and never drafted; ratification is the operator's.
- **Unratified proposal:** a durable `.out-of-scope/` record of rejected work, from MPAS `triage`.
- **Campaign box "Oversized modules"** owns the size-limit authority conflict (600 in `pythonic.md` versus the corpus table).
- **GHI #998** (waiver-ratchet gates debt volume, never coverage) is open; the arm choice is a design conversation. Related: #948 [settled], #969.
- **Handoff tooling gap observed:** a Decisions Made section with list markers but no attribution silently drops every operator ruling from the rulings store, and `validate_decision_markers` does not refuse that shape by design. Separately, a defect insight recorded 2026-09-12T23:19Z: backticked dotted governance identifiers in Evidence / Artifacts are read as missing file paths.
- **MPAS reading gaps:** two videos unreachable, including "I stopped using /grill-me for coding", the likeliest statement of the interrogation shape's limits.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz handoff rulings --search "class seams"
gh issue view 936 --json state,title
gh issue view 998 --json state,title
python3 -c "import json,pathlib;r=json.loads(pathlib.Path('src/gzkit/chores/registry.json').read_text());print(len(r['chores']))"
grep -rn "noqa: PLC0415" src/gzkit --include="*.py" | wc -l
grep -L "__all__" $(find src/gzkit -name __init__.py) | wc -l
wc -l < src/gzkit/commands/common.py
uv run gz validate --advisory-scorecard
```

Expected at authoring: `0 0`; no active locks; the "class seams" search empty until a successor to this handoff is authored, then present; #936 and #998 OPEN; 393 PLC0415 suppressions; 14 `__init__.py` without `__all__`; `common.py` at 702 lines. Re-run rather than trust these transcriptions.

## Evidence / Artifacts

- `docs/governance/chore-class-system.md` — the chore class system design record (Thread 2).
- `docs/governance/mpas-appropriation-analysis.md` — the MPAS anatomy and proposed disposition (Thread 3).
- `docs/governance/capability-control-review-2026-09-12.md` — existing R&D artifact carrying the does-not-license section.
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — Movement C and the Workflow fronts R&D entry.
- `docs/governance/advisory-rules-audit.md` — the scorecard rows cited in Thread 1.
- `.gzkit/rules/hexagonal-architecture.md` and `.gzkit/rules/pythonic.md` — the front-end rules Thread 1 measured.
- `src/gzkit/chores/registry.json`, `.gzkit/chores/registry.json`, `src/gzkit/chores/README.md` — the registry and authoring contract to extend.
- `scripts/check_proof_freshness.py` and `scripts/session_orientation.py` — the staleness mechanism to generalise and the announcement site GHI #936 names.
- `src/gzkit/commands/common.py` — the catch-all module measured in Thread 1.
- `.gzkit/handoffs/20260912T215448Z-rnd-chore-class-and-mpas.md` — the rejected handoff this one supersedes.
- `.gzkit/insights/agent-insights.jsonl` — improvement record 2026-09-12T23:50Z capturing the operator's rejection.
- Session transcript 5f61ae2b-9fc7-4646-8f2a-40d07743daaf in the harness transcript store — the primary source for this reconstruction.
- GitHub issues #936, #997, #998 and #808.

## Settled Rulings

803 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
