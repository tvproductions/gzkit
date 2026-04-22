---
id: ADR-0.0.19
status: Draft
kind: foundation
semver: 0.0.19
lane: heavy
parent: GHI-232
date: 2026-04-19
---

# ADR-0.0.19: Pre-execution reasoning walkthrough (gz justify)

## Persona

**Active persona:** `main-session` — craftsperson who reads the anchor before proposing a change, treats "confident-wrong-direction" as a first-class defect class rather than a cosmetic misfire, and distinguishes reasoning evidence (why the change should happen) from QA evidence (that the change was built correctly). This ADR formalizes the 8-section walkthrough structure extracted from the 4.7 governance hardening audit (umbrella GHI #224, sub-GHIs #225-#230) and makes it available as a durable skill without collapsing it into an enforced governance gate.

This ADR is a Foundation addition. Foundations are baseline assumptions about good app substrates — the Prime Directive invariant 11 ("if <90% sure, ask the human") has existed in `.gzkit/rules/behavioral-invariants.md` for months but has no mechanical surface; this ADR provides one without imposing universal friction. The 2am-operator rubric is load-bearing: actual 2am use is reading commit bodies, so justify's value is *pre-2am* (before the confident-wrong-direction commit), not during.

## Intent

Prime Directive invariant 11 ("if <90% sure, ask the human") is unenforced in gzkit today. Agents routinely produce confident-wrong-direction runs that waste session context and ship discarded work. An 8-section walkthrough structure developed ad-hoc during the 4.7 governance hardening audit (umbrella GHI #224, sub-GHIs #225-#230) repeatedly caught reasoning errors that would have shipped (e.g. the `chores.md:19` correction where the original fix shape "drop the threshold" was wrong and the operator's observation "tools have a clock via arb receipts" surfaced the correct fix). The pattern is reusable across any change anchor (GHI, OBPI, or draft description) but only if formalized as a durable surface. **After this ADR, `gz justify` produces an evidence-grounded 8-section scaffold for any GHI/OBPI/draft; operators and agents fill the reasoning blocks; filled walkthroughs are greppable for audit replay via `gz justify validate <file>`.** The skill is advisory — not a mechanical gate — and is suggested by upstream skills (`gz-adr-evaluate` on low scores, `gz-obpi-pipeline` on low agent confidence) rather than enforced by hook.

## Decision

Build a hybrid CLI + skill shape with a tool/agent split: the CLI (Pydantic + Jinja2) produces a deterministic 8-section scaffold populated with pre-gathered evidence; the agent or operator fills the `_[To be filled]_` reasoning blocks. The CLI never invokes an LLM. The `gz justify validate` subcommand (v1, elevated from extension point by operator request) reverse-parses filled markdown back into the Pydantic model to check structural completeness for downstream skills that want to cite the walkthrough.

**Anchor scope is deliberately narrow:** accepts GHI, OBPI, or `--draft` only. Never accepts ADR anchors — reasoning about an ADR routes through its tracking GHI or an OBPI beneath it. Attempting `gz justify ADR-X.Y.Z` errors with guidance rather than silently accepting.

**Five OBPIs decompose the decision:**

**OBPI-01 — Anchor resolution + evidence gathering:** Pydantic models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`) plus resolvers for the three anchor kinds: `gh issue view` for GHI, filesystem lookup for OBPI briefs under `docs/design/adr/<series>/ADR-*/obpis/`, and literal-text pass-through for `--draft`. Grounding gather runs five sources concurrently: rules matched by `paths:` frontmatter against anchor surface, ledger events via `gz state --json` (OBPI only), `git log --since='60 days ago'` scoped to anchor identifiers, `--related` anchors resolved recursively, and a reference to `docs/governance/model-regression-taxonomy.md`. Missing sources are non-fatal and annotated in the scaffold. **Parallel-root: no predecessor; can start alongside OBPI-04.**

**OBPI-02 — Scaffold rendering:** `WalkthroughSection` and `Walkthrough` Pydantic models with `frozen=True, extra='forbid'` and a `@model_validator` enforcing exactly 8 sections with ordinals 1-8. Jinja2 template at `src/gzkit/justify/templates/walkthrough.md.j2` renders the Walkthrough model to deterministic markdown: YAML frontmatter with anchor ID and `generated_at`; H2 section headers; evidence blocks with file:line citations; reasoning blocks as `_[To be filled]_` placeholders. CLI surface: `gz justify <anchor>` (stdout), `--save` (auto-name to `artifacts/justify/<anchor>-<ISO8601>.md`), `--output <path>`, `--related <list>`, `--draft '<text>' --draft-slug <slug>` (draft-slug required whenever `--save` + `--draft` combine). ADR anchor rejection with exit 1 and named recovery guidance. **Depends on OBPI-01.**

**OBPI-03 — Validate subcommand:** `gz justify validate <file>` reverse-parses filled markdown into a `Walkthrough` instance by consuming YAML frontmatter and walking H2 section headers with deterministic sub-block markers (`**Evidence:**` / `**Prompt:**` / reasoning). `is_complete()` checks that every section's reasoning is non-empty and contains no `_[To be filled]_` marker. `--json` mode emits a structured completeness report. Exit codes: 0 complete, 1 incomplete (lists unfilled ordinals), 2 unparseable. Roundtrip test: render Walkthrough → parse → check identity. **Depends on OBPI-02.**

**OBPI-04 — Skill definition + upstream integrations:** `.gzkit/skills/gz-justify/SKILL.md` with `main-session` persona, Common Rationalizations table, Red Flags, body instructing the agent to read the scaffold and fill each `_[To be filled]_` block using the gathered evidence via the Edit tool. Upstream integration 1: `gz-adr-evaluate` scorecard with weighted score <3.0 AND the ADR having a tracking GHI or OBPIs appends a footer `"Consider: uv run gz justify <GHI or OBPI>"`. Upstream integration 2: `gz-obpi-pipeline` skill body instructs the agent to run `gz justify <current OBPI>` when self-reported confidence <90% per Prime Directive invariant 11. Surface sync via `gz agent sync control-surfaces`. **Parallel-root: no predecessor; can start alongside OBPI-01.**

**OBPI-05 — Docs + BDD + Heavy-lane closeout:** Command manpage at `docs/user/manpages/gz-justify.md`, command doc at `docs/user/commands/justify.md`, runbook entries in `docs/user/runbook.md` describing operator flow, governance runbook note in `docs/governance/governance_runbook.md`. BDD scenarios at `features/justify.feature` covering: invoke with GHI, invoke with OBPI, invoke with `--draft`, reject ADR anchor, `--save` path with `--draft-slug`, `validate` on complete walkthrough, `validate` on incomplete walkthrough, `validate` on malformed input. Gate 5 Heavy-lane attestation package: ARB receipts for lint/typecheck/tests/coverage/mkdocs; ADR audit-check passing; human attestation via `gz attest`. **Depends on OBPI-01, OBPI-02, OBPI-03, OBPI-04 (chain-tail Heavy-lane closeout).**

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT make `gz justify` a mechanical gate on Heavy-lane OBPIs (operator explicitly rejected governance-gate framing; advisory only). A later ADR may add a hook if the advisory shape proves insufficient.
- Does NOT integrate with ARB receipts (operator correction: ARB is QA evidence, justify is reasoning evidence; different categories).
- Does NOT accept ADR anchors (scope is change instances: GHI, OBPI, draft).
- Does NOT invoke an LLM from within the CLI (deterministic, testable, runs in CI).
- Does NOT produce a JSON schema for justify receipts (markdown is the artifact; Pydantic is internal).

**Forcing-function stress tests applied during design:**

- **Pre-mortem:** 18 months out, failure modes include scaffold format drift across versions breaking `validate` on old `--save` artifacts; low-confidence trigger firing so often that operators develop "justify fatigue" and skip it; agents fabricating filled reasoning that passes `is_complete()` structurally but is semantically empty (the "tests assert semantics, not strings" invariant applies to walkthroughs too); evidence gathering latency (gh API, git log on large repos) killing the "curious operator" flow; 8-section form bending reasoning to the template even when the change doesn't fit. Mitigations: version the scaffold format and handle multi-version in validate; use discoverability not friction (runbook reference, skill suggestion) rather than enforced invocation; `is_complete()` is structural only (document that reasoning quality is human-judged); concurrent evidence gather with <3s latency target; flag the template fit issue in the skill body.
- **WWHTBT:** Operators actually invoke it from curiosity (needs discoverability via `gz --help` + runbook); scaffolded reasoning is empirically higher-quality than unscaffolded agent reasoning (**shakiest condition** — only empirical evidence is the 4.7 audit practice, which may be F-taxonomy-specific); saved markdown artifacts are greppable enough to justify `--save` (holds — existing audit patterns like `artifacts/receipts/` and `artifacts/audits/` already use this shape). For Alternative B (pure skill prompt) to have been better: if walkthroughs are never re-read after the session that produced them, CLI + file artifact is dead weight.
- **Constraint archaeology:** 8-section structure is inherited from GHI #232 and tested only by the 4.7 audit practice — lightly load-bearing. Locked for v1; v2 can bump scaffold format version. Terminal parity requirement is freshly decided (operator confirmed). Advisory-not-enforcing is freshly decided (operator correction away from universal hook).
- **Assumption surfacing:** Operators will re-read `--save` artifacts (if not, `--save` is theatre); scaffolding improves reasoning (opposite could be true — scaffold bends reasoning to predefined shape); `gh issue view` is available (not true in air-gapped contexts); 4.7 audit experience generalizes to arbitrary OBPIs (could be F-taxonomy-specific).
- **2am operator:** Actual 2am flow is operator reads commit body, not `gz justify`. Value is *pre-2am* (before the confident-wrong-direction commit), not during. This is correct for intended use; the skill is upstream of incidents, not remediation.
- **Reversibility:** CLI surface is two-way (deprecate with notice). Scaffold format is two-way with cost (old `--save` artifacts may not parse under new validator; mitigation = version the scaffold). Pydantic models are one-way door if external callers import them; mitigation = keep them private under `gzkit.justify._internal` and expose stable DTOs only if needed later. Skill body is two-way (skill-version bump + sync).
- **Scope minimization:** Floor is OBPI-01 + OBPI-02 (anchor resolution + scaffold rendering — CLI works end-to-end). OBPI-03 (validate) is operator-elevated to v1 because structural completeness checking unlocks downstream citation. OBPI-04 (skill + upstream integrations) is the discoverability layer. OBPI-05 is Heavy-lane ceremony. Under time pressure, drop OBPI-04 upstream integrations first (keep skill definition for slash-command access); OBPI-05 docs subset drops next (manpage + BDD required; runbook entries second); OBPI-03 validate drops last (standalone `gz justify` still functions without it, walkthroughs are just manually audited).

**Downstream decisions forced by this ADR:**

1. Possible follow-on ADR for hook-based automatic invocation if the advisory shape proves insufficient in operation (revisit in 6-12 months).
1. Optional ADR for domain-specific section variants (security-justify, infra-justify) if the 8-section mold bends arbitrary changes poorly.
1. Chore or ADR for auto-prune of stale `artifacts/justify/` files (storage hygiene) once `--save` adoption data exists.
1. Potential ADR to formalize the "tool + Pydantic + Jinja2 + agent-reasoning" split as a reusable pattern for other skills. This ADR sets the precedent but does not generalize it.
1. Possible schema versioning ADR for scaffold formats if v2 happens (how to parse multiple versions in one validator).

## Consequences

### Positive

1. Prime Directive invariant 11 ("if <90% sure, ask") gets a concrete mechanical surface that agents can invoke without operator intervention — the forcing function for honest calibration moves from advisory prose to a deterministic scaffold.
1. Closes the class of "confident-wrong-direction" runs by surfacing residual uncertainty as a named section — agents that cannot articulate what is uncertain have not understood the change.
1. Tool/agent split is architecturally clean: CLI does deterministic work (evidence gathering, scaffold rendering, validation); agent does non-deterministic work (reasoning). Neither overreaches into the other's responsibility.
1. Terminal parity via `gz justify` means curious operators and doubtful auditors can invoke the skill outside Claude Code — walkthroughs have a life beyond the conversation transcript.
1. `--save` persistence + `gz justify validate` together turn walkthroughs into verifiable artifacts for audit replay weeks or months later.
1. No hook friction: advisory shape respects `defect-fix-routing.md` thresholds and does not impose ceremony on direct-fix commits.
1. Upstream integration with `gz-adr-evaluate` (low-score trigger) and `gz-obpi-pipeline` (low-confidence trigger) makes the skill discoverable at the moments it matters most, without mandatory invocation.
1. Dogfood precedent: the ADR itself is designed to be justified via a future `gz justify GHI-232` invocation once the skill lands — closing the loop on its own intent.

### Negative

1. New CLI surface, skill, manpage, command doc, and BDD scenarios to maintain — Heavy-lane ceremony produces audit weight proportional to scope.
1. Markdown scaffold format becomes a reverse-parseable contract. Changing section headers, frontmatter fields, or sub-block markers breaks `validate` against older `--save` artifacts. Mitigation: version the scaffold format in frontmatter; `validate` dispatches on version and supports at least the current + previous.
1. 8-section structure may subtly bias agent reasoning toward predefined shape even when the change doesn't fit — a 5-line pool-ADR-skip fix doesn't need 8 sections of reasoning. Mitigation: skill body notes that section brevity is acceptable; empty-reasoning is a structural fail but "this section does not apply" is acceptable.
1. Evidence gathering has real cost: `gh issue view`, `gz state --json`, `git log --since='60 days ago'` all run on every invocation. Concurrent execution caps at network latency (<3s target) but CI or air-gapped contexts may struggle.
1. `is_complete()` is structural, not semantic. An agent that fills every reasoning block with "I don't know" passes validation. Semantic quality remains a human judgment call; the skill cannot enforce it without becoming an evaluator (which would duplicate `gz-adr-evaluate`).
1. Scaffold storage grows over time. Without prune policy, `artifacts/justify/` accumulates indefinitely. Mitigation deferred to a later chore; acknowledged explicitly.
1. Upstream integration touches two other skills (`gz-adr-evaluate`, `gz-obpi-pipeline`) — changes to those skills may require coordinated edits to justify's suggestion logic.
1. Dogfood recursion: the skill that would justify a proposed change cannot exist until after the change lands. The ADR-0.0.19 creation itself cannot be justified by `gz justify GHI-232` because `gz justify` does not yet exist. Acceptable one-time bootstrap cost; future ADRs can dogfood.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.19-01: Anchor resolution + evidence gathering — Pydantic models (`AnchorRef`, `EvidenceBundle`, `RuleCitation`, `CommitRef`, `LedgerEvent`); GHI/OBPI/draft resolvers; five-source concurrent grounding gather with graceful degradation for missing sources.
- [ ] OBPI-0.0.19-02: Scaffold rendering — `WalkthroughSection` + `Walkthrough` Pydantic models with 8-section validator; Jinja2 template at `src/gzkit/justify/templates/walkthrough.md.j2`; `gz justify <anchor>` CLI with `--save`, `--output`, `--related`, `--draft`/`--draft-slug`; ADR-anchor rejection with named recovery guidance.
- [ ] OBPI-0.0.19-03: Validate subcommand — `gz justify validate <file>` reverse-parses markdown to `Walkthrough`; `is_complete()` structural check; `--json` output; exit codes 0 complete / 1 incomplete / 2 unparseable per CLI doctrine 4-code map.
- [ ] OBPI-0.0.19-04: Skill definition + upstream integrations — `.gzkit/skills/gz-justify/SKILL.md` with persona and Edit-tool-driven fill body; `gz-adr-evaluate` low-score footer; `gz-obpi-pipeline` low-confidence prompt; surface sync via `gz agent sync control-surfaces`.
- [ ] OBPI-0.0.19-05: Docs + BDD + Heavy-lane closeout — manpage, command doc, runbook entries, governance runbook note; BDD scenarios covering all invocation paths + failure modes; Gate 5 attestation with ARB receipts for lint/typecheck/tests/coverage/mkdocs and human `gz attest`.

## Q&A Transcript

<!-- Interview transcript preserved for context; sourced from adr-interview.json -->

*Interview captured: 2026-04-19 via gz-design dialogue with operator; answers stored at `adr-interview.json` alongside this ADR.*

Full answer text is available in `adr-interview.json`. Key forcing-function excerpts are inlined in the Decision section above under "Forcing-function stress tests applied during design."

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

### OBPI completion

| OBPI | Brief | Status |
|------|-------|--------|
| OBPI-0.0.19-01 | obpis/OBPI-0.0.19-01-anchor-resolution-and-evidence.md | attested_completed |
| OBPI-0.0.19-02 | obpis/OBPI-0.0.19-02-scaffold-rendering.md | attested_completed |
| OBPI-0.0.19-03 | obpis/OBPI-0.0.19-03-validate-subcommand.md | attested_completed |
| OBPI-0.0.19-04 | obpis/OBPI-0.0.19-04-skill-and-upstream-integrations.md | attested_completed |
| OBPI-0.0.19-05 | obpis/OBPI-0.0.19-05-docs-bdd-closeout.md | attested at closeout |

### Closeout artifacts (OBPI-0.0.19-05)

- Manpage: `docs/user/manpages/gz-justify.md`
- Command doc: `docs/user/commands/justify.md`
- Operator runbook entry: `docs/user/runbook.md` § Loop A Step 1b
- Governance runbook entry: `docs/governance/governance_runbook.md` § Workflow: Create or Promote ADR step 5b
- BDD coverage: `features/justify.feature` (8 scenarios, all passing)
- Manpage contract test: `tests/cli/test_justify_manpage.py` (25 tests, all passing)
- REQ → @covers parity: 12/12 covered (`uv run gz covers OBPI-0.0.19-05`)

### ARB receipts (canonical invocations per `.claude/rules/attestation-enrichment.md`)

| Claim | Receipt ID |
|-------|-----------|
| Lint clean (`uv run gz arb ruff`) | `arb-ruff-92a111f577994a6cb309275263073be1` |
| Type check clean (`uv run gz arb typecheck`) | `arb-step-typecheck-588634d7ca0146319026a6ff0f62066e` |
| Tests pass (`uv run gz arb step --name unittest -- uv run -m unittest -q`) | `arb-step-unittest-5731d9923b0449248263f81019e33daf` |
| Coverage floor (`uv run gz arb coverage run -m unittest discover -s tests -t .`) | `arb-step-coverage-dbe59d5c4ae64b9d9f3bfc911643c61d` |
| Docs build clean (`uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`) | `arb-step-mkdocs-f3f2b71a15de4e8c97a14831c0d1f95d` |

## Alternatives Considered

1. **Pure skill prompt, no CLI (Approach B)** — a single `.gzkit/skills/gz-justify/SKILL.md` file with a prompt body that walks the agent through 8 sections. No Python command handler, no Pydantic models, no file artifact. Rejected: operator cannot invoke from terminal (breaks "curious operator investigating" and "doubtful auditor" use cases); walkthroughs live only in conversation transcripts and cannot be cited in commit bodies, GHIs, or later sessions; no validation path; loses the tool/agent split that makes this skill architecturally clean. Selected only if walkthroughs are never re-read after the session that produced them.

1. **Full governance gate with ARB receipts (Approach C)** — new Pydantic schema for justify receipts stored in `artifacts/receipts/justify/`; `gz arb validate` recognizes them; Claude hook `justify-gate.py` enforces presence for every Heavy-lane OBPI Stage 2 start. Rejected by operator (explicit correction): "ARB serves QA evidence, justify serves reasoning — reuse is convenient but doesn't make sense"; conflates categories; universal Heavy-lane gate imposes friction the `defect-fix-routing.md` thresholds exist to prevent. Revisit only if advisory shape fails in operation.

1. **Universal gate on every anchor-scoped code change** — every `fix(...)` commit and OBPI Stage 2 start requires a fresh justify receipt. Rejected: crushes direct-fix routing; the 5-line fixes tracked by GHI #186-#192 would each require a justify ceremony producing no governance benefit the commit body doesn't already produce. Architecturally backwards.

1. **Extend `gz-adr-evaluate` instead of new skill** — make `gz adr evaluate` produce an 8-section walkthrough as a new output mode. Rejected: scope mismatch — evaluate judges document quality via rubric scoring (8 weighted dimensions), justify judges change soundness via reasoning scaffold. Different invocation moments (post-authoring ADR vs pre-execution any-anchor), different inputs (ADR document vs GHI/OBPI/draft), different outputs (numeric scorecard vs filled markdown walkthrough). Conflation would harm both skills.

1. **Conversational dialogue instead of static scaffold (like `gz-design`)** — skill runs a multi-turn Q&A through the 8 sections, one question at a time. Rejected: synchronous dialogue has 90% overlap with `gz-design`'s territory and adds no terminal-invocation path; the forcing-function value of justify is the static structured artifact that can be re-read, greppable, and cited, not a conversational pass-through.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.19 | Completed | Jeffry | 2026-04-22 | completed |
