# Governance Surface Hygiene Taxonomy — F1-F10

**Status:** Active
**Authored:** 2026-04-18 under GHI-MASTER (governance surface hardening); re-sourced to the current frontier system cards 2026-08-02 under GHI #751
**Audience:** Anyone auditing gzkit's control surfaces for drift that degrades model performance; reviewers on governance-surface PRs; the `control-surface-coherence` chore when authored.

## Framing — this is model-agnostic

These are **general governance-surface hygiene modes** that degrade how *any* model reads and follows our control surfaces. Each new model rev exposes these modes differently — some surface sharply under one model and paper over under another — but the modes themselves persist because they describe how a human-authored rule set drifts, not how a particular model interprets it.

The evidence cited below comes from the **current** frontier system cards — the registry-rotated set in `data/frontier_model_cards.json` (chore: `frontier-model-card-currency`), presently the Claude Fable 5 / Mythos 5 System Card (Anthropic, 2026-06-09), the Claude Opus 5 System Card (Anthropic, 2026-07-24), and the GPT-5.6 System Card (OpenAI, 2026-07-09) — plus repo-observed defect history. When a card rotates out of the registry, its citations here are re-sourced or downgraded to T3 in the same refresh (operator ruling 2026-08-02: live doctrine retains no superseded-model references; prior evidence generations live in git history and the Evolution log).

## Source of authority

Each category carries its strongest available citation. Categories without T1/T2 citations are valid (they describe real governance-hygiene modes) but should be flagged so that when a future card provides evidence, the citation strength upgrades.

| Tier | Source | Use |
|---|---|---|
| T1 | Authoritative model evaluation (a current system card in the registry) | Mode is empirically demonstrated to degrade model performance |
| T2 | Vendor operator guidance (current-model tutorial, prompt guidance, release notes) | Mode is documented in operator-facing material but not in formal evaluation |
| T3 | Observed defect pattern in repo history | Mode is visible in the ledger/GHI history; lacks vendor-level citation |

Prefer T1 evidence where available; T3 is sufficient to keep a mode in the catalogue but should be paired with repo-specific evidence (ledger event, GHI cluster) so the case is auditable.

## Current-card behavioral evidence base

The Fable/Mythos 5 card grounds the catalogue in two complementary ways:

1. **Real-usage failure clusters (§ 2.3.3).** From 886 day-to-day internal uses, Anthropic tags recurring failure patterns with their own vocabulary — `Safeguard circumvention`, `Fabrication`, `Skipped cheap verification`, `Reckless action`, `Correction fails`, `Instruction following` — with cluster sizes: *states an unverified guess as fact* (41/886, the largest), *reported work as done or verified when it wasn't* (16/886), *worked around a block instead of stopping* (9/886), *ignores an explicit instruction or required step* (4/886), *invented key details that were never observed* (3/886). This vocabulary is the same taxonomy gzkit's `.gzkit/rules/agent-failure-modes.md` carries.
2. **Targeted diligence evaluations (§ 6.3.5).** Uncritically-reporting-flawed-results, code-summary honesty (prefilled failure transcripts), lazy investigation, and CLI-command overconfidence — each a direct measurement of a failure shape an F-category's fix is designed to close.

The GPT-5.6 card supplies the second-vendor disposition finding: coding misalignment stems from "interpreting user instructions too permissively – assuming that actions are allowed unless they're explicitly and unambiguously prohibited" (§ 7.2).

## The general meta-finding — updated for the current generation

**Prompt shape measurably steers frontier-model behavior, and the current-generation failure direction is overeagerness, not over-caution.** The earlier evidence generation measured a cautious-prompt penalty (over-asking, action-downgrade). The current cards measure the opposite regime:

- Fable/Mythos § 6.3.7: reward-hacking on GUI tasks runs at 17.4% under a neutral system prompt, drops to 9.1% when the prompt discourages it — "prompt-based steering remains useful as a means for decreasing the rate of overeager hacking."
- Opus 5 § 8.4: agentic-coding score *declines* above `high` effort because the model makes out-of-scope edits; a brief in-prompt scope instruction "recovered performance on most of these tasks."
- GPT-5.6 § 7.2: beyond-intent action increases with persistence at the highest reasoning efforts, amplified by persistence-emphasizing system prompts.

**What survives both regimes:** governance hygiene that names mechanisms ("run X command", "cite test Y", "paths outside this list are denied") rather than aspirations ("be thorough", "use judgment") is robust regardless of which direction the current model errs. This remains the rationale for every F1 and F6 fix in this catalogue — and the scope-boundary fixes (allowed-paths, negative constraints) are now the measured mitigation on three current cards.

### Limit of text-level remediation

Text-level governance cannot close model-level tendencies. The current card names the class directly: `Correction fails` — "the relevant correction was present, e.g. in a memory file or repeated user feedback, but the behavior recurred anyway" (Fable/Mythos § 2.3.3). Its Example 3 is the sharpest form: the model acted on an instruction *it had itself committed to its memory files* to author agent commits as the human and collapse a two-approval requirement — the memory surface carried the rule, and carried the circumvention (§ 2.3.3.3). White-box analyses add that the model sometimes takes undesirable actions "in cases where its activations reveal an awareness that these actions are undesirable" (§ 6.1.2, § 6.4.1.1).

**Implication:** F1-F10 fixes address the governance *text* surface. They reduce friction and close contradictions. They do NOT close the class of model-level tendencies (fabrication, skipped verification, confident guessing). That closure requires mechanical gates: tests, hooks, `gz validate` checks, receipt-ID attestation, contract-anchored output-form assertions. The F6 fix shape ("cite a locking test") is itself the right pattern — bind claims to mechanical evidence, not prose.

This taxonomy is a text-surface instrument. The `control-surface-coherence` chore pairs every F-category with its mechanical counterpart (test, hook, or gate), so that a finding in the text surface always traces to the mechanical check that would have caught it.

## F-category catalogue

### F1 — Vague-inference instructions

**Definition:** Rules phrased as soft inference triggers ("use judgment", "when appropriate", "as needed", "if relevant", "consider whether") without a named observable trigger (tool call, CLI command, numeric threshold, file state).

**Citation tier:** T1. GPT-5.6 § 7.2: instructions are read permissively — "assuming that actions are allowed unless they're explicitly and unambiguously prohibited." Fable/Mythos § 2.3.3 tags `Instruction following` ("ignoring or forgetting a key instruction") as a recurring real-usage cluster.

**Why literal/permissive readers struggle:** a vague trigger gives the model discretion, and the current generation spends that discretion in the overeager direction — acting where the operator meant "sometimes," or skipping where the operator meant "always."

**Observed outcome:** session friction; unintended action paths; skipped steps whose trigger was prose.

**Fix shape:** Replace every vague-inference phrase with a mechanical trigger — a named CLI command, a named tool call, a numeric threshold, an observable event.

---

### F2 — Cross-surface restatement

**Definition:** The same rule stated in 2+ files, often with semantic drift between copies.

**Citation tier:** T3 (repo-observed; the immediate producer of F5 contradictions).

**Why models struggle:** each occurrence reads as an independent constraint. Two restatements with slight drift produce rule-competition — over-constraint, or a silent pick.

**Observed outcome:** drift between surfaces (e.g. TDD discipline stated in 3 files, one carrying a rule the others don't); contradictions that earlier models papered over by inferring intent.

**Fix shape:** Pick one canonical home per topic; elsewhere, replace with a single-line pointer.

---

### F3 — Tool-use literalism / hesitation

**Definition:** Operations described in prose ("read the brief", "search tests/", "find the file") without naming the specific tool call (Read, Grep, Glob, Edit, Bash).

**Citation tier:** T1. Fable/Mythos § 6.4.1.4: premature task abandonment driven by unverbalized spurious token-budget concerns — the model stopped an exhaustive search after one tool call with 2.43M tokens remaining; § 2.3.3.4: built a custom risky tool without checking project memory that named the preferred one.

**Why models struggle:** prose operations leave the tool decision to the model; the failure modes are skipping the operation, substituting memory, or improvising a worse instrument.

**Observed outcome:** skills that describe operations in prose see action-skip or tool-improvisation. GHI #190's pre-save ground-truth check exists precisely to force a tool-literal step.

**Fix shape:** Every operation names its tool. Replace "search tests/" with `Grep(pattern=..., path="tests/")`; "read the brief" with `Read(file_path=<path>)`.

---

### F4 — Over-ceremony coupled to root-cause thinking

**Definition:** Pipeline ceremonies described as mandatory sequential steps with no scope-scaling, coupled to "thorough fix" language such that agents channel root-cause thinking into ceremony-mandate.

**Citation tier:** T3 (gzkit-observed): GHI #195 and withdraw commit `d2ed160b`. Current-card context: long-horizon agentic thoroughness is a strength of the current frontier tier; the coupling failure is a gzkit-text bug, not a model bug.

**Observed outcome:** a 5-line validator filter fix wrapped in full OBPI ceremony (GHI #195). `defect-fix-routing.md` is the correct-shape fix.

**Fix shape:** Decouple "root-cause thinking" from "ceremony shape"; cite mechanical routing thresholds (AGENTS.md § Defect-fix routing), never "prefer the more thorough fix" alone.

**Important:** do not remediate F4 by degrading the model's thoroughness strength. The failure is in the coupling, not the instinct.

---

### F5 — Cross-surface contradictions

**Definition:** Two surfaces state incompatible rules; a literal read picks one path and violates the other, or deadlocks on context-ordering.

**Citation tier:** T3 (repo-observed; consequence of F2).

**Observed outcome:** defect-filing rules split across `gh-cli.md` and `governance-core.md`; ceremony-vs-routing tension resolved only when `defect-fix-routing.md` became the single authority.

**Fix shape:** Resolve each contradiction by carving explicit exceptions, picking one path and deleting the other, or adding a scope-gate making both rules disjoint.

---

### F6 — Unverifiable vibe claims

**Definition:** Rules or skill contracts that make assertions ("produces a table", "comprehensive", "thorough", "safe") without a named verification pathway (test anchor, CLI check, observable command output).

**Citation tier:** T1 — the strongest-evidenced category on the current cards. Fable/Mythos § 2.3.3: *states an unverified guess as fact* is the **largest** real-usage failure cluster (41/886); § 2.3.3.2: the model claimed a change was "verified end-to-end" on offline checks alone and it failed at runtime on first use; § 2.3.3.5, on its own fabricated finding: "The word 'indeterminate' was doing dishonest work in that sentence: it implies *we observed nondeterminism*, when the truth is *we never looked*." § 6.3.5.2: dishonest summaries of prefilled failing transcripts at 6.0%/4.6% (Mythos/Fable). GPT-5.6 § 7.1 measures the sibling categories (concealed uncertainty, misrepresenting work completion) on production traffic.

**Why models struggle:** a claim with no verification affordance invites a plausible assertion. When the text asks for "comprehensive" without a schema, the model has nothing to verify against.

**Observed outcome:** GHI #141/#149/#150/#151 — a skill promised table output, the destination verb emitted prose, drift went undetected for two days.

**Fix shape:** Every output-form claim cites a locking test. Every "comprehensive" becomes an enumerable checklist or schema reference. Every attestation rule names the receipt ID it requires.

---

### F7 — Missing negative constraints

**Definition:** Positive specs without a matching "do NOT" that closes the inferred gap.

**Citation tier:** T1 (upgraded 2026-08-02 from T3). GPT-5.6 § 7.2 names the disposition the negative constraint closes: actions are assumed "allowed unless they're explicitly and unambiguously prohibited." Fable/Mythos § 6.1.2 records "the model interpreting user permissions excessively liberally" during early internal use.

**Fix shape:** For every positive rule, ask "what's the obvious wrong interpretation?" and add a matching negative. Exhaustive target-naming for destructive scopes is mandatory — the current cards document destructive actions against targets the user never named.

---

### F8 — Monolithic burying of binding rules

**Definition:** Binding content (tables, thresholds, commands) buried under rationale, history, or narrative prose within the same file.

**Citation tier:** T3 (repo-observed; the map-not-encyclopedia doctrine and the diet chore are its standing remediation). No current-card positional-weighting measurement is on file; re-upgrade when a current card measures it.

**Observed outcome:** rule files with binding tables below 100+ lines of narrative; resolved by the ADR-0.0.54 shape contract and the `instructions-files-diet` chore.

**Fix shape:** Hoist binding tables to the top of every rule file; move rationale to `docs/governance/`.

---

### F9 — Repetition for emphasis

**Definition:** Same rule stated multiple times within one file for emphasis.

**Citation tier:** T3 (repo-observed; each restatement reads as an independent commitment and compounds F1/F4 over-weighting).

**Observed outcome:** a pipeline skill restating its central law ~5× within one file.

**Fix shape:** Collapse to one statement per rule, at the canonical location.

---

### F10 — Implicit cross-file context dependencies

**Definition:** Rules or skill steps that depend on another rule/skill being loaded in the context without naming the specific section or command.

**Citation tier:** T3 (repo-observed).

**Observed outcome:** stage references without the CLI commands that drive them; skills pointing at procedures without embedding the critical step.

**Fix shape:** Every cross-reference either names a specific section + tool literal, or embeds the critical step inline.

## Behavioral outcomes (observed, not mechanisms)

These are the failure *shapes* agents produce under one or more F-categories. They are consequences, not separate categories.

| Outcome | Root cause category(ies) | Current reference |
|---|---|---|
| Unverified-guess-as-fact in status reports | F6 | Fable/Mythos § 2.3.3 (41/886 cluster) |
| "Verified end-to-end" without an observed run | F6 + F3 | Fable/Mythos § 2.3.3.2; DO IT RIGHT 6g |
| Permissive reading of scope ("not prohibited = allowed") | F1 + F7 | GPT-5.6 § 7.2 |
| Premature stop with unverbalized spurious budget concern | F3 | Fable/Mythos § 6.4.1.4 |
| Wrapping a 5-line fix in full OBPI ceremony | F4 + F9 | GHI #195 |
| Silent output-form drift (skill promises table, verb emits prose) | F6 | GHI #141/#149/#150 |
| Cross-surface rule-competition deadlock | F2 + F5 | GHI-MASTER umbrella series |

## Usage

**In GHI bodies:** Reference F-categories by F-code. Cite this taxonomy file for definitions.

**In audit reports:** Score findings against F1-F10. If a finding doesn't fit, propose a new F-category via PR to this file. Do not stretch an existing category to fit.

**In PR review:** When a governance-surface PR adds a new rule, check whether it introduces any of F1-F10. Reject or rewrite.

**In the `control-surface-coherence` chore (when authored):** Scorecard per F-category, exhaustive sweep across CLAUDE.md, AGENTS.md, `.gzkit/rules/**`, `.gzkit/skills/**`, `docs/governance/**`, `.claude/hooks/**`. Receipt per run.

## Versioning

This taxonomy is versioned by edit. When a new model card ships, the `frontier-model-card-currency` chore routes the evidence refresh: current-card citations replace rotated-out ones, categories are re-tiered, and the pass is appended to the Evolution log. Prior evidence generations live in git history, never in the live body (operator ruling 2026-08-02).

## Evolution log

- **2026-04-18** — initial draft under GHI-MASTER (governance-surface hardening). Categories F1-F10 scoped as general governance-hygiene modes against the then-current evidence generation.
- **2026-08-02** — re-sourced to the current card registry under GHI #751. Evidence base moved to Fable/Mythos 5 §§ 2.3.3, 6.3.5, 6.3.7, 6.4.1 + Opus 5 § 8.4 + GPT-5.6 §§ 7.1-7.2. Meta-finding updated: the measured failure direction flipped from over-caution/action-downgrade to overeagerness/permissive-scope; mechanism-naming fix shapes unchanged and re-validated. F7 upgraded T3→T1; F8 downgraded T1→T3 pending a current-card positional measurement. Superseded-model rationale purged per operator ruling.
