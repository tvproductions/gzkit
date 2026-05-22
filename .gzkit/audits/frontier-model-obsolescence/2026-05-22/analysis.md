# Frontier Model Obsolescence Audit

Date: 2026-05-22

## Executive Verdict

gzkit is not obsolete if it is understood as a deterministic governance harness: ledger, receipts, validators, schemas, reconciliation, content rendering, and completion gates.

gzkit is becoming obsolete where it behaves like a large caution prompt. Frontier models now need less step-by-step behavioral prose, and in some cases layered caution makes them worse: more literal, more likely to ask instead of act, and more likely to burn context proving compliance rather than finishing the job.

The remediation path is therefore not "more doctrine." It is:

1. Repair the executable control-surface substrate.
2. Make live-surface round-trips fail closed.
3. Compress AGENTS.md/CLAUDE.md into a map with pointers.
4. Replace Claude-specific model selection with harness-neutral capability routing.
5. Move remaining guidance into sensors, validators, receipts, and health reports.

The audit found one critical defect that should dominate the roadmap: ADR-0.0.34, the agent-control-surface rendering substrate, is marked Validated and audit-check passes, but the live `gz content import AGENTS.md --as AgentContract --write ...` path loses almost all AGENTS.md and CLAUDE.md content.

## Current Frontier Baseline

Primary-source model baseline used for this audit:

- OpenAI says GPT-5.5 in Codex and ChatGPT is aimed at "real work" across coding, research, documents, spreadsheets, software operation, ambiguity, and tool use. OpenAI also reports GPT-5.5 in Codex improving document/spreadsheet/slide work and computer-use workflows. Source: [Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/).
- Anthropic says Claude Opus 4.7 improves on Opus 4.6 for advanced software engineering, complex long-running tasks, instruction following, verification, and tool-error recovery. Anthropic also explicitly says prompts/harnesses may need retuning because Opus 4.7 follows older prompts more literally. Source: [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7).
- Google DeepMind says Gemini 3.1 Pro is its advanced complex-task model, natively multimodal, with up to a 1M-token context window and ability to process entire code repositories. Source: [Gemini 3.1 Pro model card](https://deepmind.google/models/model-cards/gemini-3-1-pro/).
- OpenAI's GPT-5.5 system card reports strong agentic and cyber-task performance but still frames external evaluation, safeguards, and capability margins as live concerns. Source: [GPT-5.5 system card](https://deploymentsafety.openai.com/gpt-5-5/gpt-5-5.pdf).

Implication: the model layer has improved enough that "tell the agent to be careful" has diminishing returns. But the model layer has not made auditability, evidence binding, replayable state, or organizational proof obsolete.

## Repo Shape

Observed local scale:

- `src/gzkit`: 304 Python files.
- `tests`: 358 Python test files.
- `.gzkit/skills`: 52 skill files.
- `.gzkit/rules`: 20 rule markdown files.
- `docs/design/adr`: 314 ADR markdown files and 719 OBPI markdown files.

This is not a small prompt pack. It is a governance runtime with a large doctrine surface attached.

## What Remains Load-Bearing

### Ledger State

[src/gzkit/ledger.py](../../../../src/gzkit/ledger.py) defines the ledger as append-only JSONL and says state is derived from the ledger, not separately stored. `LedgerEvent` is a Pydantic model with `extra="forbid"` and deterministic serialization. The append path writes JSON lines and invalidates caches.

This is robust against stronger models. Better models make more claims; the ledger is how claims become replayable state.

### Receipt Binding

[src/gzkit/governance/trust_audits/attestation_receipts.py](../../../../src/gzkit/governance/trust_audits/attestation_receipts.py) parses ARB receipt IDs, resolves receipt JSON, requires `exit_status == 0`, and fails closed for heavy/foundation zero-receipt cases.

Observed command:

```text
$ uv run gz validate --attestation-receipts 'tests: receipt arb-step-unittest-00000000000000000000000000000000' --lane heavy --kind foundation
❌ Attestation receipt validation failed (1 entry):
  →  arb-step-unittest-00000000000000000000000000000000
      no receipt file at arb-step-unittest-00000000000000000000000000000000.json
```

This survives frontier-model improvement. Stronger models can still make ungrounded claims; receipt validation blocks the claim from becoming proof.

### Instruction Surface Budget

[src/gzkit/governance/trust_audits/instructions_files_budget.py](../../../../src/gzkit/governance/trust_audits/instructions_files_budget.py) enforces per-file budgets for AGENTS.md, CLAUDE.md, and `.claude/rules/*.md`, with remediation pointing to `gz-context-diet`.

Observed command:

```text
$ uv run gz validate --instructions-files-budget
Validated: instructions_files_budget

✓ All validations passed (1 scopes).
```

This is directionally correct but insufficient: passing a 40k budget still permits a 31k AGENTS.md wall. The next bar should be scenario-aware loading and content-model compression, not only byte-count ceiling.

### Vendor Manifest Validation

[data/vendor-manifest.json](../../../../data/vendor-manifest.json) declares render routes for eight content types, and `uv run gz validate --vendor-manifest` passes.

Observed command:

```text
$ uv run gz validate --vendor-manifest
Validated: vendor_manifest

✓ All validations passed (1 scopes).
```

This is a good primitive. The weakness is that it currently routes only to `claude`.

## Critical Finding

### F1: ADR-0.0.34 is Validated, but live AgentContract round-trip loses AGENTS.md/CLAUDE.md content

Severity: Critical.

Why it matters: gzkit's strongest answer to frontier-model obsolescence is "move prompt prose into deterministic content models and renderers." The live implementation currently proves the opposite for the most important surface.

Repo evidence:

- [docs/governance/agent-control-surface-rendering-substrate.md](../../../../docs/governance/agent-control-surface-rendering-substrate.md) declares the binding claim that every per-turn surface is rendered from canonical Pydantic content models via deterministic vendor-aware templates.
- The same doctrine says today's Era 1 still has hand-authored static files, but Era 2 should be Pydantic + Jinja2 deterministic rendering for all content types.
- [src/gzkit/content/models/agent_contract.py](../../../../src/gzkit/content/models/agent_contract.py) defines `AgentContract` with only `name`, `purpose`, `tech_stack`, and `rules`.
- [src/gzkit/content/parse/markdown_parser.py](../../../../src/gzkit/content/parse/markdown_parser.py) parses only H1, preamble, `## Tech Stack`, and `## Rules` for `AgentContract`.
- [src/gzkit/content/templates/agentcontract/claude.md.j2](../../../../src/gzkit/content/templates/agentcontract/claude.md.j2) renders only those fields.
- [docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-03-reverse-parse-migration.md](../../../../docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-03-reverse-parse-migration.md) requires lossless migration of AGENTS.md and CLAUDE.md: import, write, then `diff -q` exits 0.
- `uv run gz adr audit-check ADR-0.0.34 --json` reports `passed: true`, 8/8 OBPIs complete, 39/39 REQs covered, and no findings.

Observed live commands:

```text
$ uv run gz content show AGENTS.md --as AgentContract
Type: AgentContract
Source: AGENTS.md

Fields:
  - name: AGENTS.md
  - purpose: Universal agent contract for gzkit.
  - rules: <list, 0 item(s)>
  - schema_version: 1
  - tech_stack: <list, 0 item(s)>
```

```text
$ uv run gz content render AGENTS.md --as AgentContract --vendor claude
# AGENTS.md

Universal agent contract for gzkit.
```

```text
$ wc -c AGENTS.md /tmp/gzkit-agents-roundtrip.md CLAUDE.md /tmp/gzkit-claude-roundtrip.md
   31483 AGENTS.md
      51 /tmp/gzkit-agents-roundtrip.md
    1378 CLAUDE.md
      26 /tmp/gzkit-claude-roundtrip.md
   32938 total
```

```text
$ diff -q AGENTS.md /tmp/gzkit-agents-roundtrip.md
Files AGENTS.md and /tmp/gzkit-agents-roundtrip.md differ
```

Interpretation: the ledger and REQ coverage say the substrate is validated; live behavior says the most important round-trip acceptance criterion fails. This is not a model obsolescence problem. It is an evidence-chain defect.

Route: GHI tracker via `ghi-author`, then OBPI ceremony. This changes CLI/runtime/schema/validator behavior, so it is not a direct fix under AGENTS.md defect-routing rules.

## Other Findings

### F2: Model Selection Is Claude-Tiered, Not Harness-Neutral

Severity: High.

Evidence:

- [CLAUDE.md](../../../../CLAUDE.md) has an "Opus 4.7 tuning" section and sets `xhigh` as default effort for gzkit agentic work.
- [.gzkit/rules/model-selection.md](../../../../.gzkit/rules/model-selection.md) maps `haiku`, `sonnet`, and `opus` to specific Claude model IDs, including `claude-opus-4-7`.
- The same rule says skill frontmatter `model:` values are `haiku`, `sonnet`, `opus`.

This was reasonable for Claude Code as the dominant harness, but it does not survive a world with GPT-5.5 Codex, Claude Opus 4.7, Gemini 3.1 Pro, Copilot, and future model churn. The stable abstraction should be capability/decision class, not vendor family name.

Remediation: introduce a harness capability matrix:

- `decision_class`: lookup, mechanical_validation, routine_review, architecture, refactor, closeout_narrative.
- `effort`: light, standard, deep, max.
- `required_capabilities`: long_context, repo_read, shell_exec, browser, computer_use, subagent, hook_interception, receipt_write, human_attestation.
- `vendor_projection`: Claude/Codex/Gemini/Copilot mapping kept in data, not skill prose.

Route: foundation ADR or pending vendor capability ADR. This touches schemas, skills, generated control surfaces, and docs; it is heavy-lane work.

### F3: AGENTS.md Is Within Budget but Still Too Heavy for Frontier Models

Severity: High.

Evidence:

- `AGENTS.md` is 31,483 bytes.
- `CLAUDE.md` is 1,378 bytes.
- `uv run gz validate --instructions-files-budget` passes because the budget is 40,000 bytes for AGENTS.md.
- [docs/governance/model-regression-taxonomy.md](../../../../docs/governance/model-regression-taxonomy.md) already states that over-cautious governance prompts can degrade modern model performance and that text-level remediation cannot close model-level tendencies.

The budget check prevents unbounded growth; it does not ensure the loaded prompt is the right prompt. Modern models need fewer global reminders and more task-scoped constraints, live checks, and durable artifacts.

Route: execute ADR-0.0.54 (`agents-md-map-not-encyclopedia-doctrine`) after the content round-trip defect is fixed. Dieting before round-trip fidelity is repaired risks deleting intent with no reliable renderer/parser safety net.

### F4: Vendor-Aware Rendering Is Currently Claude-Only

Severity: Medium to High.

Evidence:

- [src/gzkit/content/vendors.py](../../../../src/gzkit/content/vendors.py) fallback routes list only `claude` for every content type.
- [data/vendor-manifest.json](../../../../data/vendor-manifest.json) lists only `claude`.
- The repo has pool ADRs for vendor alignment: `vendor-alignment-codex`, `vendor-alignment-copilot`, `vendor-alignment-gemini-cli`, `vendor-capability-matrix`, and related harness pools in `gz status`.

This does not make gzkit obsolete, but it means gzkit's rendered-control-surface story is still Claude-shaped while the frontier landscape is multi-harness.

Route: promote/execute `ADR-pool.vendor-capability-matrix` before individual vendor alignment ADRs. Do not start by adding Codex/Gemini templates ad hoc; first define the capability schema that decides what each vendor surface can actually carry.

### F5: Audit-Check Can Pass Without Replaying Live Acceptance Commands

Severity: High.

Evidence:

- `uv run gz adr audit-check ADR-0.0.34 --json` returns pass with 39/39 covered REQs.
- The live command required by REQ-0.0.34-03-03 fails behaviorally.
- [tests/content/test_round_trip_agent_contract.py](../../../../tests/content/test_round_trip_agent_contract.py) tests synthetic minimal/full model instances, not the live AGENTS.md file.

The problem is not that tests are absent. The problem is that tests pin generated fixture round-trip, while the brief required current live surface round-trip.

Remediation: add `gz validate --content-roundtrip-live` and include it in `gz validate --surface-fidelity` or `gz check`. The validator should enumerate live canonical surfaces from the vendor/content manifest, run parse->render, and assert byte equality where the content type claims losslessness.

## Remediation Pathway

### Phase 0: Track the Critical Defect

Create one GHI through `ghi-author`:

Title: `ADR-0.0.34 live AgentContract round-trip loses AGENTS.md and CLAUDE.md content`

Body evidence:

- `uv run gz adr audit-check ADR-0.0.34 --json` passes.
- `uv run gz content show AGENTS.md --as AgentContract` returns only name/purpose and empty lists.
- AGENTS.md 31,483 bytes round-trips to 51 bytes.
- CLAUDE.md 1,378 bytes round-trips to 26 bytes.
- REQ-0.0.34-03-03 explicitly required zero-byte diff for AGENTS.md.

Route in the GHI: observation tracker only. Implementation is OBPI ceremony because the fix changes content model/schema/parser/renderer/validator behavior.

### Phase 1: Repair the Content Substrate Before Dieting Prompts

Goal: make the control-surface substrate trustworthy before compressing AGENTS.md.

Required implementation shape:

- Add failing tests that execute live-surface round-trip for AGENTS.md and CLAUDE.md.
- Replace skeletal `AgentContract` with a lossless markdown-block model, or split it into `AgentContract` metadata plus ordered `SectionBlock` / `RawBlock` content.
- Make parser preserve every section and unknown block, not only `Tech Stack` and `Rules`.
- Make renderer byte-stable for current surfaces.
- Add a live validator: `gz validate --content-roundtrip-live`.
- Include that validator in the surface-fidelity/check path.
- Update ADR-0.0.34 audit notes after the repair, because the current audit overclaims.

Do not make this a "semantic model everything perfectly" project. The first invariant is losslessness. Semantic extraction can come after no-content-loss is mechanically true.

### Phase 2: Execute AGENTS.md Map-Not-Encyclopedia

Goal: reduce prompt drag now that the renderer can preserve intent.

Route: ADR-0.0.54 is already pending:

- `ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine`
- OBPIs include authoring the map doctrine, lifting sections, adding a conformance validator, and enforcing sync.

Target shape:

- AGENTS.md contains only project identity, hard triggers, command map, active invariants, and pointers.
- Long rationale moves to docs/governance.
- Vendor-specific guidance stays in vendor surfaces.
- Task-scoped rules load by path/scenario, not globally.

Success criterion: not merely lower byte count. Success is fewer global caution instructions and more mechanical references to commands/validators.

### Phase 3: Replace Claude-Tier Model Selection

Goal: stop encoding current Claude family names as the core routing abstraction.

Implementation shape:

- Introduce a `harness_capabilities` data model.
- Convert skill `model:` to `decision_class:` plus optional `required_capabilities:`.
- Keep vendor-specific model IDs in data projections, not skill bodies.
- Render Claude, Codex, Gemini, and Copilot guidance from the same canonical capability facts.
- Add validator that fails when a skill uses vendor-specific model IDs outside vendor-specific surfaces.

This directly answers the "use current models" concern: current models become data, not doctrine.

### Phase 4: Add Harness Health and Live Replay

Goal: make long-agent work recoverable and auditable regardless of app autocompact behavior.

Implementation shape:

- `gz health`: aggregate cheap validators first, then expensive gates; show stale surfaces, failed round-trips, unresolved high-severity defects.
- Session checkpoint rule: deep audits create `.gzkit/audits/<topic>/<date>/analysis.md` at start and append evidence as work proceeds.
- Add a validator for audit artifacts that checks each finding has evidence, route, and next action.
- Add replay commands for claimed completion evidence, not just ledger REQ coverage.

This is the direct answer to the Codex failure mode in this session: the work must survive the chat transport.

## Priority Order

1. **Fix ADR-0.0.34 live round-trip defect.** This is the foundation for every future prompt-diet and vendor-rendering move.
2. **Run ADR-0.0.54 AGENTS.md map-not-encyclopedia.** Compress prose after lossless rendering is real.
3. **Promote vendor capability matrix.** Convert current model names into data projections.
4. **Add live replay health checks.** Make `gz health` expose whether validated doctrine still matches live commands.
5. **Then pursue Codex/Gemini/Copilot render templates.** Do this after the capability model exists, not as one-off mirrors.

## Bottom Line

Frontier models weaken the case for giant global instruction walls. They strengthen the case for gzkit's deterministic core.

The fair critique is sharper: gzkit is only future-proof if it finishes becoming executable governance. Right now, the repo already knows that direction, but the most important implementation of that direction has a live fidelity hole. Repair that first. Then diet the prose. Then make model/harness routing data-driven.
