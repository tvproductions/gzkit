# Agent Prompt: gzkit Companion ADR for opsdev Retirement

## Ownership

**gzkit owns this work.** The gzkit agent is responsible for:

1. Reading the airlineops codebase (`../airlineops/`) to extract all non-domain value
2. Evaluating what airlineops/opsdev does better than gzkit's current implementation
3. Absorbing the best implementations into gzkit
4. Reaching full parity so airlineops can drop in gzkit and delete opsdev

airlineops ADR-0.0.36 is parked until gzkit is fully ready. The airlineops agent does
nothing until this work is complete. All extraction, evaluation, and absorption happens
here in the gzkit repo.

## The Subtraction Test

The governing principle:

```text
airlineops - gzkit = pure airline domain
```

gzkit is the whole works: rules, governance, structure, tools, templates, model harness
materials, Python code patterns, CLI framework, test infrastructure. Everything about
"how you build software" belongs in gzkit. Everything about "airlines" stays in airlineops.

If something in airlineops or opsdev is NOT airline-specific, it's either already in gzkit,
needs to be absorbed into gzkit, or is a gzkit blind spot that this ADR must address.

## Context

airlineops has a developer tooling package called `opsdev` (~90 commands, ~5,000 lines)
that is being retired. gzkit (v0.18.1) already covers ~80% of what opsdev does for
governance. But the audit scope is broader than opsdev CLI commands — it includes ALL
non-domain infrastructure in airlineops:

- **CLI commands** — the ~90 opsdev subcommands
- **Infrastructure code** — CLI framework, config loading, test harness (`TempDBMixin`),
  model patterns (Pydantic base classes, adapter contracts, port protocols), pre-commit
  hook implementations, agent hook scripts
- **Governance and methodology docs** — GovZero charter, gate definitions, audit protocol,
  session handoff, ADR lifecycle, OBPI templates
- **Templates and scaffolds** — ADR templates, brief templates, closeout forms, evaluation
  frameworks, discovery index, instruction files

Some of these gzkit already does better. Some airlineops/opsdev does better. The goal is
MAX gzkit — the best implementation from either side.

## Task

Draft a gzkit ADR that governs the absorption of all non-domain value from airlineops.

**Critical: READ the airlineops codebase first.** The source material is at:

- `../airlineops/src/opsdev/` — developer tooling package (90 commands, the primary target)
- `../airlineops/src/airlineops/` — infrastructure patterns that may be reusable
- `../airlineops/AGENTS.md` — the agent contract (governance methodology embedded here)
- `../airlineops/.github/instructions/` — instruction files
- `../airlineops/.github/copilot-instructions.md` — canonical doctrine set
- `../airlineops/.claude/hooks/` — agent hook implementations
- `../airlineops/.pre-commit-config.yaml` — pre-commit integration
- `../airlineops/config/opsdev/` — opsdev configuration files
- `../airlineops/docs/governance/GovZero/` — methodology documentation
- `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.36-opsdev-retirement/` — the airlineops
  ADR and its 12 OBPI briefs (especially OBPI-01 which defines the facility audit)

The ADR should cover:

### 1. Capability Absorption

Evaluate and onboard opsdev/airlineops capabilities into gzkit. Apply the subtraction test
to each: "Is this about airlines or about building software?"

**Quality tooling (gzkit doesn't have yet):**

- `validate-manpages` — manpage structure validation, call-stack alignment
- `sync-manpage-docstrings` — sync manpage one-liners with source docstrings
- `sloc-scan` — SLOC threshold violations (radon-based)
- `complexity-check` — xenon complexity analysis with configurable thresholds
- `mutate` — mutation testing (Cosmic Ray)
- `test-times` — slowest test reporting
- `test-quality` — test quality metrics
- `metrics scan/report` — code quality violation scanning

**Infrastructure that may need to flow upstream:**

- `TempDBMixin` — SQLite test isolation (not airline-specific — any project needs this)
- Config loading patterns — `load_settings()`, schema validation via Pydantic
- Cross-platform guards — Windows file locking, safe_rmtree, path handling
- Pre-commit hook Python scripts — the implementations, not just the config entries
- Agent hook implementations (PostToolUse, PreToolUse scripts)

**Potentially better in opsdev (compare honestly):**

- `git-sync` — opsdev's is comprehensive (skip-fetch, lint/test integration, trunk-only
  guard). Compare with gzkit's `git_sync.py`
- `arb` (Agent Self-Reporting) — structured receipts, schema drift validation. gzkit has
  `gz-arb` skill but compare implementations
- Pre-commit hook orchestration — opsdev has deep `.pre-commit-config.yaml` integration
- Chore system — both have one; compare maturity and config models

### 2. Instruction Plugin Registry

Design a system where:

- gzkit ships canonical instruction templates (cross-platform rules, testing policy, model
  conventions, etc.)
- Projects can extend or specialize through a registered mechanism
- `gz validate instructions` checks local overrides against canonical set
- Local customizations can't be ad-hoc — they must be registered plugins
- Conformance checking prevents project-local instructions from contradicting canonical ones

### 3. Model Harness Parity

gzkit must provide the model harness materials that any project needs:

- Pydantic base patterns and conventions
- Adapter/port contract patterns
- Config-first architecture (registry access, schema validation)
- Test infrastructure patterns (DB isolation, fixtures, cross-platform)

Evaluate what airlineops currently provides in these areas. What's airline-specific stays.
What's reusable flows upstream.

### 4. Best-Implementation Evaluation

For each capability that exists in both opsdev and gzkit, establish evaluation criteria:

- Feature completeness
- Error handling maturity
- Cross-platform robustness
- Configuration model
- Test coverage

The goal is MAX gzkit — take the best implementation from either side. Not "gzkit wins
by default."

### 5. Acceptance Criterion

When this ADR's work is complete, a project should be able to:

1. `uv add py-gzkit` (or path dep)
2. `gz init` in their project
3. Get full governance + quality + model harness tooling with zero opsdev dependency
4. Continue development without missing a beat

The subtraction test must hold: after gzkit is installed, the only thing left in the
project that isn't from gzkit is pure domain code.

### Relationship to airlineops

This ADR is the upstream companion to airlineops ADR-0.0.36. airlineops will NOT begin
its cutover until this ADR is complete and gzkit is fully ready. The sequencing is:

1. **gzkit absorbs all non-domain value from airlineops (THIS ADR — do it all here)**
2. airlineops adopts gzkit and relocates domain commands (ADR-0.0.36, parked)
3. airlineops deletes opsdev (ADR-0.0.36, parked)

## Important Notes

- Do NOT assume gzkit is always better. opsdev has maturity in areas gzkit hasn't touched.
- READ the airlineops source before evaluating. Don't guess — compare implementations.
- The airlineops codebase is the source material. Extract every reusable pattern.
- This is about making gzkit the best it can be, not about airlineops migration mechanics.
- The instruction plugin registry is a significant design problem — it deserves careful
  thought, not a quick answer.
