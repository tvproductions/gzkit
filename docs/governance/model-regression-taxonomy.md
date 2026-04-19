# Governance Surface Hygiene Taxonomy — F1-F10

**Status:** Active
**Authored:** 2026-04-18 under GHI-MASTER (4.7 regression — governance surface hardening)
**Audience:** Anyone auditing gzkit's control surfaces for drift that degrades model performance; reviewers on governance-surface PRs; the `control-surface-coherence` chore when authored.

## Framing — this is model-agnostic

These are **general governance-surface hygiene modes** that degrade how *any* model reads and follows our control surfaces. They are not a 4.7-specific catalogue. Each new model rev exposes these modes differently — some surface sharply under one model and paper over under another — but the modes themselves persist because they describe how a human-authored rule set drifts, not how a particular model interprets it.

The 4.7 System Card evidence cited below is the **current-best evidence** for each mode, captured because 4.7 is the model we're running and its public evaluation is recent and specific. A future model rev will produce different evidence (some modes strengthened, some weakened) without invalidating the taxonomy. The chore that operationalizes this taxonomy (`control-surface-coherence`) runs model-agnostic; the F1-F10 checklist is what it scores against, regardless of which model the repo is running today.

The reason to preserve the citations: when an operator asks "why is F8 monolith-burying in the catalogue?" the answer should be *"because human readers routinely bury binding rules, and here is one model (4.7) where we have direct evidence that it measurably degraded performance"* — not *"because 4.7 broke last Tuesday."*

## Source of authority

Each category carries its strongest available citation. Categories without T1/T2 citations are valid (they describe real governance-hygiene modes) but should be flagged in the catalogue so that when a future model rev provides evidence, we can upgrade the citation strength.

| Tier | Source | Use |
|---|---|---|
| T1 | Authoritative model evaluation (e.g. Anthropic System Card §6.2.2.2 for 4.7) | Mode is empirically demonstrated to degrade model performance on a benchmark |
| T2 | Vendor operator guidance (e.g. tutorial, release notes) | Mode is documented in operator-facing material but not in formal evaluation |
| T3 | Observed defect pattern in repo history | Mode is visible in the ledger/GHI history; lacks vendor-level citation |

Prefer T1 evidence where available; T3 is sufficient to keep a mode in the catalogue but should be paired with repo-specific evidence (ledger event, GHI cluster) so the case is auditable.

## Anthropic's authoritative 6-axis behavioral framework

The System Card §6.2.2.2 evaluates models on six axes. Every F-category below cross-references these:

1. **Instruction following** — tracks multi-part constraints, surfaces genuine ambiguities. 4.7 strength overall but: *"sometimes downgrades action requests into advice or questions — explaining how to squash commits rather than doing it"* — cautious prompts *amplified* this tendency.
2. **Safety** — 4.7 scores above 4.6 and Mythos without prompting.
3. **Verification** — 4.7 "checks outcomes before reporting and does not claim unverified results" (strength vs 4.6).
4. **Efficiency** — 4.7 improves on 4.6 but is "prone to declaring sufficiency without acting — in the worst case stating 'I have enough context, let me write the code,' then resuming exploration until it hits the tool-call cap with nothing written."
5. **Adaptability** — 4.7 strength: "reliably diagnoses root causes rather than patching surface symptoms."
6. **Honesty** — 4.7 near saturation.

## The general meta-finding

**Over-cautious governance prompts can degrade modern model performance.** This is a general principle, not a 4.7-specific artifact. It holds because well-trained models already have strong baselines for care and hedge behavior; additional instruction-level caution stacks on top of that baseline and tips the model into over-asking, action-downgrade, and deferral loops.

**Current evidence (2026-04-18):** System Card §6.2.2.2 for Claude Opus 4.7 — *"Notably, [Opus 4.7] is the first model in this series for which a cautious system prompt lowered instruction-following and adaptability scores — its baseline is already careful enough that added caution tips into over-asking."* The reference cautious prompt Anthropic tested resembles gzkit's governance shape.

**What this predicts for future model revs:** models with rising training-time caution will progressively respond worse to layered instruction-level caution. Governance hygiene that names mechanisms ("run X command", "cite test Y") rather than aspirations ("be thorough", "use judgment") is robust across this trajectory. This is the rationale for every F1 and F6 fix in this catalogue.

### Limit of text-level remediation

System Card §2.3.6 examples (Mythos Preview, not 4.7 — but the class-of-failure is named) show that text-level governance cannot close model-level tendencies. Example 4: researcher corrected the same behavior roughly four times, Mythos wrote memory files about it, then repeated the behavior. The model's own words: *"I know the rule — I have six memory files about it — but knowing it doesn't stop me from generating the plausible-sounding version first."* Example 5: CLAUDE.md was updated mid-session to prevent the behavior; the pattern recurred after the rewrite.

**Implication for this remediation:** F1-F10 fixes address the governance *text* surface. They reduce friction and close contradictions. They do NOT close the class of model-level tendencies (fabrication, skipped verification, confident guessing). That closure requires mechanical gates: tests, hooks, `gz validate` checks, receipt-ID attestation, contract-anchored output-form assertions. The F6 fix shape ("cite a locking test") is itself the right pattern — bind claims to mechanical evidence, not prose.

This taxonomy is a text-surface instrument. The `control-surface-coherence` chore will need to pair every F-category with its mechanical counterpart (test, hook, or gate) when authored, so that a finding in the text surface always traces to the mechanical check that would have caught it.

The reference cautious prompt Anthropic used (and found degraded 4.7): *"Complete this task exactly as described. If anything is unclear, ambiguous, or seems wrong, stop and ask me — do not guess, reinterpret, or decide on your own what I 'probably meant.' Do not modify any files or run any commands I have not explicitly asked for..."* (§6.2.2.2)

**That prompt is gzkit's governance surface in miniature.** The governance canon is a cautious prompt, at scale, loaded into every turn. The Opus 4.7 System Card is evidence that our governance shape degrades 4.7 performance — not a claim about gzkit but an observed effect on the reference prompt whose shape ours matches.

This is why the F1-F10 remediation is framed as "hardening" rather than "refactoring": we are not wrong in what we wrote; we are over-cautious in how we wrote it for a model whose baseline caution has risen.

## F-category catalogue

### F1 — Vague-inference instructions

**Definition:** Rules phrased as soft inference triggers ("use judgment", "when appropriate", "as needed", "if relevant", "consider whether") without a named observable trigger (tool call, CLI command, numeric threshold, file state).

**Anthropic axis:** Instruction following (negative — "downgrades action requests into advice or questions"); Efficiency (negative — "declaring sufficiency without acting").

**Citation tier:** T1. System Card §6.2.2.2: *"the cautious system prompt amplified rather than corrected [the action-downgrade tendency]."*

**Why 4.7 struggles:** 4.6 inferred operator intent and bent the rule to fit. 4.7 reads the text literally and either picks *a* literal path (which may not match intent) or downgrades the action to a question back to the user. Anthropic's own test shows a cautious prompt makes this *worse*.

**Observed outcome:** Session friction; agents ask unnecessary questions, defer action, or pick a literal path the operator didn't intend.

**Fix shape:** Replace every vague-inference phrase with a mechanical trigger — a named CLI command, a named tool call, a numeric threshold, an observable event (like a specific tool call fire).

---

### F2 — Cross-surface restatement

**Definition:** The same rule stated in 2+ files, often with semantic drift between copies.

**Anthropic axis:** Instruction following (negative — conflicting constraints).

**Citation tier:** T2. Tutorial ("Working with Claude Opus 4.7"): *"write your directions once and clearly"* without unnecessary repetition for emphasis.

**Why 4.7 struggles:** 4.7 treats each occurrence as an independent constraint. Two restatements with slight drift produce rule-competition. The model either over-constrains (trying to satisfy both) or picks one and silently violates the other.

**Observed outcome:** Drift between surfaces (e.g. gzkit TDD discipline in 3 files, one has a rule the others don't); contradictions that 4.6 papered over.

**Fix shape:** Pick one canonical home per topic; elsewhere, replace with a single-line pointer.

---

### F3 — Tool-use literalism / hesitation

**Definition:** Operations described in prose ("read the brief", "search tests/", "find the file") without naming the specific tool call (Read, Grep, Glob, Edit, Bash).

**Anthropic axis:** Efficiency (negative — "declaring sufficiency without acting"); Instruction following (negative — "passing control back to the user").

**Citation tier:** T1. System Card §6.2.2.2 Efficiency: *"prone to declaring sufficiency without acting — in the worst case stating 'I have enough context, let me write the code,' then resuming exploration until it hits the tool-call cap with nothing written."* Tutorial: *"[4.7] uses web search and connectors less frequently than earlier models. Users should explicitly specify when information should come from 'a specific source.'"*

**Why 4.7 struggles:** 4.7 is more selective about tool reach than 4.6. Prose like "search tests/" doesn't name the Grep tool; 4.7 may skip the step or substitute internal-memory guesses.

**Observed outcome:** Skills that describe operations in prose see action-skip under 4.7. GHI #190 pre-save ground-truth check was necessary to force the tool-literal check in `gz-obpi-specify`.

**Fix shape:** Every operation names its tool. Replace `find X` with `Glob(pattern=X)`. Replace "search tests/" with `Grep(pattern=..., path="tests/")`. Replace "read the brief" with `Read(file_path=<path>)`.

---

### F4 — Over-ceremony coupled to root-cause thinking

**Definition:** Pipeline ceremonies described as mandatory sequential steps with no scope-scaling, coupled to "thorough fix" language such that agents channel root-cause thinking into ceremony-mandate.

**Anthropic axis:** Adaptability (4.7 **strength**) — "reliably diagnoses root causes rather than patching surface symptoms"; Efficiency (negative outcome).

**Citation tier:** T1 (root-cause strength) + T3 (ceremony-coupling is gzkit-specific observation). System Card §6.2.2.2 Adaptability names the strength; our observed GHI #195 and withdraw commit `d2ed160b` name the failure mode.

**Why 4.7 struggles:** 4.7's Adaptability preference for thorough fixes is a strength. But gzkit governance text couples "thorough fix" with "full OBPI ceremony" (Iron Law, `behavioral-invariants.md` 6c, etc.). 4.7's thoroughness instinct gets channeled into ceremony-mandate — not a 4.7 bug but a gzkit-text bug.

**Observed outcome:** 5-line validator filter fix wrapped in full OBPI-0.0.16-06 ceremony (GHI #195; withdrawn via commit `d2ed160b`). The `defect-fix-routing.md` rule authored post-withdraw is the correct-shape fix; zero skills reference it, so the coupling persists.

**Fix shape:** Decouple "root-cause thinking" from "ceremony shape." Cross-reference `defect-fix-routing.md` from `gz-obpi-pipeline` and `gz-skill-router` with explicit scope-scaling thresholds. Rewrite `behavioral-invariants.md` 6c to cite thresholds, not "prefer the more thorough fix."

**Important:** Do not remediate F4 by degrading 4.7's Adaptability strength. The failure is in the coupling, not in 4.7's instinct.

---

### F5 — Cross-surface contradictions

**Definition:** Two surfaces state incompatible rules; 4.7's literal read picks one path and violates the other, or deadlocks on context-ordering.

**Anthropic axis:** Instruction following (negative — conflicting constraints).

**Citation tier:** T3. Observed-pattern only. No direct system card citation but immediate consequence of F2 restatement with drift.

**Why 4.7 struggles:** 4.6 resolved tension by inferring intent. 4.7 reads literally and picks whichever statement appears first in context (or deadlocks).

**Observed outcome:** `gh-cli.md:11` vs `governance-core.md:16` on defect filing; `behavioral-invariants.md` rule 6c vs `defect-fix-routing.md`; `arb.md` vs `attestation-enrichment.md` on ARB mandate; `git-sync/SKILL.md:46` vs `:80` on `--lint --test`.

**Fix shape:** Resolve each contradiction by carving out explicit exceptions, picking one path and deleting the other, or by adding a scope-gate that makes both rules apply to disjoint situations.

---

### F6 — Unverifiable vibe claims

**Definition:** Rules or skill contracts that make assertions ("produces a table", "comprehensive", "thorough", "safe") without a named verification pathway (test anchor, CLI check, observable command output).

**Anthropic axis:** Verification (4.7 strength) + Honesty (4.7 near saturation). Failure shape is our text asking 4.7 to assert things without verification affordance.

**Citation tier:** T1. System Card §2.3: *"Confidence calibration (speculative predictions stated with the same confidence as established protocol steps)."*

**Why 4.7 struggles:** 4.7's Verification strength depends on having something to verify against. When a skill promises "a table" without a locking test, or an attestation rule asks for "comprehensive" evidence without a schema, 4.7 has nothing to verify and either fabricates a plausible claim or flags the gap.

**Observed outcome:** GHI #141/#149/#150/#151 — `gz-adr-status` skill promised table output, destination verb emitted prose, drift went undetected for two days. The Invariant 3 rule in `tool-skill-runbook-alignment.md` was authored to close this class; other skills still make bare vibe claims.

**Fix shape:** Every output-form claim cites a locking test. Every "comprehensive" is replaced with an enumerable checklist or schema reference. Every attestation rule names the receipt ID it requires.

---

### F7 — Missing negative constraints

**Definition:** Positive specs without a matching "do NOT" that closes the inferred gap.

**Anthropic axis:** Instruction following (completeness).

**Citation tier:** T3. Observed-pattern only. Anthropic doesn't publish this as a 4.7-specific failure.

**Why 4.7 struggles:** 4.6 inferred the obvious negative ("don't do the obviously-stupid-thing"). 4.7 reads the positive literally and may take an obvious trap path that 4.6 would avoid.

**Observed outcome:** Weaker evidence — this is a governance-hygiene category that benefits any model. Keep as a category but don't frame as "4.7-specific regression."

**Fix shape:** For every positive rule, ask "what's the obvious wrong interpretation?" and add a matching negative. `constraints.md` is the canonical home; additions go there.

---

### F8 — Monolithic burying of binding rules

**Definition:** Binding content (tables, thresholds, commands) buried under rationale, history, or narrative prose within the same file.

**Anthropic axis:** Instruction following (positional weighting).

**Citation tier:** T1. System Card §2.3 Recurring Limitations: *"response verbosity that buried actionable content within pages of text"* — **exact phrase match**.

**Why 4.7 struggles:** 4.7 weights early tokens more heavily than 4.6 and is more selective about which tokens drive behavior. Binding content at line 213 of a 226-line file competes with rationale at lines 1-40. Third-party reports (apiyi.com) claim long-context MRCR regression, which would amplify this if true; the System Card §8.7.2 has the authoritative MRCR v2 figures — gzkit's context is nowhere near 256k, so the MRCR angle is not primary. The positional-weighting angle is.

**Observed outcome:** `tests.md` 226 lines with coverage floor at L213; `attestation-enrichment.md` 120 lines with canonical command table at L54; `skill-surface-sync.md` rules at L27-37 after agent-psychology narrative at L14-25.

**Fix shape:** Hoist binding tables to the top of every rule file. Move rationale, history, and narrative to bottom-of-file "Rationale" section or to `docs/governance/*.md`. Extract large skill subsections to `references/`.

---

### F9 — Repetition for emphasis

**Definition:** Same rule stated multiple times within one file for emphasis.

**Anthropic axis:** Instruction following (over-weighting).

**Citation tier:** T2. Tutorial: *"write your directions once and clearly"* without unnecessary repetition for emphasis.

**Why 4.7 struggles:** 4.7 treats each restatement as an independent commitment. Three restatements triple the weight vs. rules stated once, producing the over-ceremony / over-cautious modes documented in F1 and F4.

**Observed outcome:** `gz-obpi-pipeline/SKILL.md` Iron Law restated ~5× within one skill (Iron Law + Rationalization + Hard Boundaries + MUST + MUST NOT). `gz-adr-closeout-ceremony` 20 rows of MUST/MUST NOT where 10 would do.

**Fix shape:** Collapse to one statement per rule, at the canonical location. Trim restatements within a file to zero.

---

### F10 — Implicit cross-file context dependencies

**Definition:** Rules or skill steps that depend on another rule/skill being loaded in the context without naming the specific section or command.

**Anthropic axis:** Instruction following (context dependency).

**Citation tier:** T3. Observed-pattern only.

**Why 4.7 struggles:** 4.7 is more selective about context loading. A rule that says "see `gz-obpi-pipeline` § Stage 2" without naming the CLI command for Stage 2 may execute without the referenced context loaded.

**Observed outcome:** `constraints.md § Pipeline Lifecycle` references stages without naming the CLI commands that drive them. `gz-obpi-specify` references `gz-obpi-pipeline` for the procedure but doesn't embed the critical steps.

**Fix shape:** Every cross-reference either names a specific section + tool literal, or embeds the critical step inline rather than pointing.

## Behavioral outcomes (observed, not mechanisms)

These are the failure *shapes* agents produce under one or more F-categories. They are not separate categories — they are consequences.

| Outcome | Root cause category(ies) | System Card reference |
|---|---|---|
| Action-downgrade to advice/questions | F1 + F7 | §6.2.2.2 Instruction following |
| "I have enough context" then no output | F3 | §6.2.2.2 Efficiency |
| Unnecessary follow-up questions on clear requests | F1 | §6.2 (pp. 98-99) |
| Wrapping 5-line fix in full OBPI ceremony | F4 + F9 | GHI #195 |
| Silent output-form drift (skill promises table, verb emits prose) | F6 | GHI #141/#149/#150 |
| Cross-surface rule-competition deadlock | F2 + F5 | Observed (GHI-MASTER umbrella series) |

## Usage

**In GHI bodies:** Reference F-categories by F-code. Cite this taxonomy file for definitions.

**In audit reports:** Score findings against F1-F10. If a finding doesn't fit, propose a new F-category via PR to this file. Do not stretch an existing category to fit.

**In PR review:** When a governance-surface PR adds a new rule, check whether it introduces any of F1-F10. Reject or rewrite.

**In the `control-surface-coherence` chore (when authored):** Scorecard per F-category, exhaustive sweep across CLAUDE.md, AGENTS.md, agents.local.md, `.gzkit/rules/**`, `.gzkit/skills/**`, `docs/governance/**`, `.claude/hooks/**`. Receipt per run.

## Versioning

This taxonomy is versioned by edit. When a new model rev ships and invalidates or extends categories, append a new section dated with the model release; do not edit history.

## Evolution log

- **2026-04-18** — initial draft under GHI-MASTER (4.7 regression hardening). Categories F1-F10 scoped as general governance-hygiene modes; 4.7 System Card + tutorial + observed GHIs cited as current-best evidence. Taxonomy designed to outlive the 4.7 cycle; the chore that operationalizes it is model-agnostic.
