# AUDIT (Gate-5) — ADR-0.0.12 Agent Role Persona Profiles

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.12 |
| ADR Title | Agent Role Persona Profiles |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles |
| Audit Date | 2026-04-04 |
| Auditor(s) | Claude Opus 4.6 (agent), jeff (human attestor) |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?**

- All 6 agent roles have virtue-ethics-based persona frames stored in `.gzkit/personas/`
- Pipeline dispatch loads the relevant persona and prepends it to subagent prompts
- AGENTS.md references the persona control surface with role mapping and grounding
- `gz personas list` discovers and displays all persona files with traits/anti-traits
- Persona frames use orthogonal trait composition — no expertise claims, only behavioral identity

### Capability 1: Persona Discovery

```bash
$ uv run gz personas list
                                 Agent Personas
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Traits            ┃ Anti-Traits       ┃ Grounding        ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ implementer       │ methodical,       │ minimum-viable-e… │ I plan before I  │
│                   │ test-first,       │ token-efficiency… │ write...         │
│                   │ atomic-edits,...  │ split-imports,... │                  │
│ main-session      │ craftsperson,     │ generic-assistan… │ I write Python   │
│                   │ governance-aware, │ token-efficiency… │ the way it was   │
│                   │ whole-file-reaso… │ incremental-patc… │ meant to be...   │
│ narrator          │ clarity,          │ verbosity,        │ I translate      │
│                   │ precision,...     │ jargon-accumulat… │ evidence into    │
│                   │                   │                   │ decisions...     │
│ pipeline-orchest… │ ceremony-complet… │ premature-summar… │ I see each       │
│                   │ stage-discipline, │ stage-skipping,   │ pipeline stage   │
│                   │ governance-fidel… │ good-enough-comp… │ as a promise...  │
│ quality-reviewer  │ architectural-ri… │ rubber-stamping,  │ I evaluate       │
│                   │ solid-principles, │ cosmetic-focus,   │ structure, not   │
│                   │ maintainability-… │ over-engineering… │ surface...       │
│ spec-reviewer     │ independent-judg… │ rubber-stamping,  │ I read every     │
│                   │ skepticism,       │ optimistic-bias,  │ changed file     │
│                   │ evidence-based-a… │ deference-to-imp… │ myself...        │
└───────────────────┴───────────────────┴───────────────────┴──────────────────┘
```

**Why it matters:** Operators can inspect all active persona identities at a
glance. Each persona shows the specific trait cluster designed to prevent the
production failures that motivated the ADR (import splitting, rubber-stamp
reviews, premature summarization).

### Capability 2: Dispatch Integration

```bash
$ uv run -m unittest tests.test_pipeline_runtime.TestPersonaPipelineIntegration -v
test_load_persona_for_dispatch_implementer ... ok
test_prepend_persona_to_prompt_with_compose ... ok
test_role_persona_map_covers_agent_file_map ... ok
test_dispatch_record_persona_field ... ok
...
Ran 11 tests in 0.003s — OK
```

**Why it matters:** `load_persona_for_dispatch()` maps role names to persona
files and `prepend_persona_to_prompt()` injects the frame into every subagent
prompt. Every dispatched agent (implementer, reviewer, narrator, orchestrator)
now starts with an intentionally designed behavioral identity instead of
defaulting to "helpful AI assistant."

### Capability 3: AGENTS.md Persona Contract

```bash
$ uv run -m unittest tests.test_sync_surfaces.TestAgentsPersonaSection -v
test_agents_template_has_persona_section ... ok
test_agents_persona_references_control_surface ... ok
test_agents_persona_frames_behavioral_identity ... ok
test_agents_persona_forbids_expertise_claims ... ok
test_persona_discovery_command ... ok
Ran 5 tests in 0.001s — OK
```

**Why it matters:** AGENTS.md is the operator contract. It now includes a
Persona section with role mappings, grounding for the main-session persona,
and explicit anti-patterns (no expertise claims). The main session persona
("I write Python the way it was meant to be written") frames the entire
operator experience.

### Capability 4: BDD Persona Scenarios

```bash
$ uv run -m behave features/persona.feature
1 feature passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
30 steps passed, 0 failed, 0 skipped — Took 0.077s
```

**Why it matters:** End-to-end scenarios prove that persona files survive
workspace initialization, appear in CLI output with correct traits, and are
referenced in AGENTS.md with the designed grounding text.

### Value Summary

Before this ADR, agents operated with the default Assistant persona — token-efficient,
incremental, shallow-compliant — which caused production failures (import splitting,
partial edits, rubber-stamp reviews). Now every agent role starts from an intentionally
designed identity with specific trait clusters that directly counter those failure
modes. The persona loading is automatic via dispatch, not opt-in.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| All 6 personas exist | `uv run gz personas list` | ✓ | 6 personas in table |
| JSON mode | `uv run gz personas list --json` | ✓ | Valid JSON, 6 entries |
| Schema validation | `uv run -m unittest tests.test_persona_schema -v` | ✓ | 42 tests OK; `proofs/unittest_persona.txt` |
| Model validation | `uv run -m unittest tests.test_persona_model -v` | ✓ | 20 tests OK; `proofs/unittest_persona.txt` |
| Dispatch integration | `uv run -m unittest tests.test_pipeline_runtime.TestPersonaPipelineIntegration -v` | ✓ | 11 tests OK; `proofs/unittest_dispatch.txt` |
| AGENTS.md persona | `uv run -m unittest tests.test_sync_surfaces -v` | ✓ | 12 tests OK; `proofs/unittest_agents_persona.txt` |
| BDD scenarios | `uv run -m behave features/persona.feature` | ✓ | 6 scenarios, 30 steps; `proofs/behave_persona.txt` |
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.12` | ✓ | PASS, 21/22 REQs (95.5%) |

## Shortfalls

### Shortfall 1: REQ-0.0.12-07-03 uncovered in `@covers` traceability

- **Severity:** Non-blocking
- **Description:** REQ-0.0.12-07-03 ("Given behave features/persona.feature, when persona integration scenarios run, then all pass") is checked `[x]` in the brief and verified by the BDD pass above, but has no `@covers("REQ-0.0.12-07-03")` decorator in Python test files. This is because BDD steps use Gherkin, not Python decorators.
- **Remedy:** Tooling gap — the coverage scanner only checks `@covers` in `tests/`. A future enhancement could scan feature files for REQ references. Not a defect in ADR-0.0.12's implementation.

### Shortfall 2: ADR Evidence section references nonexistent test file

- **Severity:** Non-blocking
- **Description:** ADR document line 273 references `tests/test_persona_profiles.py` but the actual files are `tests/test_persona_schema.py` and `tests/test_persona_model.py`.
- **Remedy:** Documentation drift. The tests exist under different names. Non-blocking because the evidence path is not machine-consumed.

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 7 OBPIs attested, 21/22 REQs covered |
| Data Integrity | ✓ All 6 persona files parse and validate |
| Dispatch Integration | ✓ All roles map to personas, prepend works |
| Documentation Alignment | ✓ AGENTS.md persona section present and tested |
| BDD Coverage | ✓ 6 scenarios, 30 steps pass |
| Risk Items | ⚠ 2 non-blocking shortfalls documented |

## Evidence Index

- `audit/proofs/unittest_persona.txt` — 62 persona schema + model tests
- `audit/proofs/unittest_dispatch.txt` — 11 dispatch integration tests
- `audit/proofs/unittest_agents_persona.txt` — 12 AGENTS.md persona tests
- `audit/proofs/behave_persona.txt` — 6 BDD scenarios, 30 steps

## Attestation

I attest that ADR-0.0.12 is implemented as intended, evidence is reproducible,
and no blocking discrepancies remain. Two non-blocking shortfalls are documented
(BDD coverage tooling gap, test file naming drift).

Signed: agent:claude-opus-4-6 Date: 2026-04-04
