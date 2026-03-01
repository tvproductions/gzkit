# Agent Readiness Audit

## Applying the four-discipline taxonomy to gzkit

This audit applies Nate B. Jones' prompting taxonomy (prompt craft, context engineering, intent engineering, specification engineering) and the five specification primitives to `gzkit`.

Scoring scale (0-3):

- 0: Not present
- 1: Informal
- 2: Partial
- 3: Agent-ready

---

## Discipline 1: Prompt Craft

### gzkit

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Standard prompts for common tasks (adding skills, updating governance docs, parity sweeps) | 2 | Canonical skills exist for these workflows (`.gzkit/skills/gz-*`, `airlineops-parity-scan`) and are mirrored/synced. | No single "prompt cookbook" consolidating best prompt patterns per task family. |
| Examples of good and bad output for recurring work | 1 | Some runbook examples and command output excerpts exist (`docs/user/runbook.md`). | Few explicit WRONG vs RIGHT examples for governance artifacts and parity reports. |
| Explicit output format expectations | 2 | Strong contract language exists in AGENTS (evidence, attestation, gate expectations) and command docs. | Output formatting standards are distributed; no central style contract for audit/report artifacts. |
| Guardrails for known failure modes | 3 | Strong MUST/NEVER constraints in `AGENTS.md`; fail-closed governance conventions and receipt/audit commands. | Remaining guardrails are not consistently codified in `.github/instructions` beyond governance subset. |
| Ambiguity resolution rules | 2 | Defect-first and tracking rules are explicit (`AGENTS.md`), parity rubric adds import classification behavior. | Ambiguity rules are not yet normalized into a compact decision tree for all recurring workflows. |

---

## Discipline 2: Context Engineering

### gzkit

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| CLAUDE.md or equivalent project-level agent instructions | 3 | `CLAUDE.md` present and generated from governance canon. | Minor: architecture section is terse ("See project documentation"). |
| `.github/copilot-instructions.md` with project-specific guidance | 3 | Present and synced via `gz agent sync control-surfaces`; includes skills and governance behavior. | Could include tighter task-specific examples. |
| GovZero framework documented in agent-readable form | 3 | Rich GovZero docs under `docs/governance/GovZero/**` plus governance runbook and parity rubric. | None blocking. |
| Skills registry (`discovery-index.json`) current and accurate | 1 | Skills inventory exists in generated control surfaces (`AGENTS.md`, `CLAUDE.md`) and skill audit tooling. | `.github/discovery-index.json` is referenced in templates/OBPIs but missing in repo. |
| Agent parity documentation (Claude vs. GHCP conventions) | 2 | Mirror contract and sync behavior documented in AGENTS/skills/ADR history (`ADR-0.4.0-*`). | No single operator-facing parity guide that compares agent-specific expectations side-by-side. |
| README that orients a new agent session | 1 | README has strong conceptual framing and lineage context. | Quickstart commands drift from runtime (`gz plan new`, `gz verify` invalid today). |
| Known conventions documented (naming, file placement, test patterns) | 3 | Conventions are explicit across AGENTS, runbooks, command docs, skills, and tests. | None blocking. |
| Context rot mitigation: stale docs cleaned/flagged | 2 | Sync command + parity scan/report cadence exist; lint/validate/build checks run clean. | Drift still present (README command drift, missing discovery-index references). |

---

## Discipline 3: Intent Engineering

### gzkit

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Project purpose statement an agent can read | 3 | Strong purpose narrative in README/lineage/genesis; AGENTS states project identity. | None blocking. |
| Trade-off hierarchy: governance rigor vs shipping velocity | 2 | Lite/Heavy lanes and gate doctrine define rigor levels; attestation boundaries are explicit. | No concise "trade-off ladder" artifact that ranks speed vs rigor decisions in one place. |
| Quality bar definition | 3 | Gates, quality commands, and acceptance protocol are explicit and testable. | None blocking. |
| Scope boundaries | 3 | OBPI allowed/denied paths + parity intake rubric import/exclude logic define scope discipline. | None blocking. |
| Relationship to AirlineOps and course materials defined | 2 | AirlineOps lineage and extraction context documented (`docs/user/reference/lineage.md`, parity docs). | Course-material relationship is narrative, not an explicit policy surface with constraints. |
| Decision escalation rules | 3 | Human attestation boundary and Gate 5 rules are explicit; agents blocked from unilateral completion. | None blocking. |
| GovZero self-application: does gzkit eat its own dog food? | 2 | gzkit uses its own commands for sync/audit/validation and maintains governance artifacts in-repo. | Some self-application drift remains (README runtime mismatch, discovery-index contract gap). |

---

## Discipline 4: Specification Engineering

### Primitive 1: Self-Contained Problem Statements

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| gzkit: Are issues/tasks written with full context? | 2 | OBPI briefs include objective, lane, allowed/denied paths, requirements, and verification sections. | Many briefs remain Draft with placeholder checkboxes/comments; not all are execution-ready. |
| gzkit: Do task descriptions specify which governance framework version, which agent target? | 2 | Skills encode GovZero version metadata and mirror targets. | Task artifacts are inconsistent about agent-target specificity and discovery-index dependencies. |

### Primitive 2: Acceptance Criteria

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| gzkit: Do tasks have explicit "done looks like" statements? | 3 | OBPI acceptance criteria and gate checklists are explicit in brief templates and many briefs. | None blocking. |
| gzkit: Are there verifiable outputs? | 3 | Runtime verification commands are concrete (`gz lint/test/typecheck/validate/...`) and frequently used in reports. | None blocking. |

### Primitive 3: Constraint Architecture

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| gzkit: Musts | 3 | Strong MUST language in AGENTS, gate covenant, runbooks, and parity rubric. | None blocking. |
| gzkit: Must-nots | 3 | Explicit NEVER rules (Gate 5 bypass, direct ledger edits, etc.). | None blocking. |
| gzkit: Preferences | 2 | Preferences exist (use skills, mirror sync workflow, selective parity intake). | Preferences are distributed; no compact preference hierarchy artifact. |
| gzkit: Escalation triggers | 2 | Defect tracking and attestation escalation are explicit. | Threshold-style triggers (e.g., "if change touches N surfaces then escalate") are not standardized. |

### Primitive 4: Decomposition

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| gzkit: Is the agent parity work decomposed into independent milestones? | 3 | Parity work decomposed into ADR/OBPI tranches (`ADR-0.3.0`, `ADR-0.4.0`, etc.). | None blocking. |
| gzkit: Are governance framework updates decomposed into sub-2-hour tasks? | 2 | OBPI granularity exists and is generally incremental. | Time-boxing discipline is not explicitly enforced in artifact contracts. |
| gzkit: Do decomposed tasks have clear input/output boundaries? | 3 | Allowed/denied paths + acceptance criteria + verification bundles provide clear boundaries. | None blocking. |

### Primitive 5: Evaluation Design

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| gzkit: Are there eval cases for governance document generation? | 2 | Tests exist for sync/control-surface generation (`tests/test_sync.py`, `tests/test_cli.py`, `tests/test_skills_audit.py`). | No dedicated eval harness with golden-output baselines for docs/governance generation artifacts. |
| gzkit: Are there eval cases for agent parity sweeps? | 1 | Parity sweeps are documented via dated reports and manual command bundles. | No automated parity regression suite with pass/fail thresholds over canonical deltas. |
| gzkit: Do evals run after model updates? | 1 | Quality checks are routine, but model/eval coupling is not formalized in CI workflows. | Missing long-horizon agent-harness/eval loop tied to model or instruction-surface changes. |

---

## Summary and Next Actions

Initial snapshot below reflects pre-remediation scoring; see Post-Remediation Addendum for current state.

### gzkit: Top 3 gaps

1. **Context contract drift (high impact, low effort):**
   - Gap: README quickstart uses invalid command patterns (`gz plan new`, `gz verify`).
   - Fix: update README quickstart to match current CLI surface and add a CLI-doc contract check in `gz cli audit` scope.

2. **Discovery index contract gap (high impact, low effort):**
   - Gap: `.github/discovery-index.json` is referenced by templates/OBPIs but missing.
   - Fix: either create and maintain `.github/discovery-index.json` or remove/replace all hard references with current control surfaces.

3. **Parity/eval automation gap (high impact, moderate effort):**
   - Gap: parity sweeps rely on manual reports; no automated regression harness.
   - Fix: add a deterministic parity check command/test suite with thresholded PASS/FAIL criteria and CI integration.

### Cross-project observations

- Governance/specification surfaces are stronger than evaluation harnesses.
- Context curation exists, but context rot appears where command surfaces evolve faster than onboarding docs.
- Constraint architecture is mature; ambiguity handling is still distributed across many files.

---

## Audit Metadata

- Date: 2026-03-01
- Auditor: Codex (GPT-5)
- Taxonomy source: Nate B. Jones, "If You're Prompting Like It's Last Month, You're Already Late" (February 2026)
- Corroborating sources: Anthropic (context engineering, harnesses), OpenAI (agent-building and long-horizon tasks)
- Framework version: Sprint and Drift / GovZero v6

## Evidence Notes (Initial, Now Resolved)

Tracked defects discovered during this audit:

1. README command drift
   - Evidence: `README.md` references `gz plan new` and `gz verify`; `uv run gz --help` shows no `verify` command.
2. Missing discovery index
   - Evidence: `.github/discovery-index.json` absent while referenced by OBPI templates and ADR artifacts.

## Post-Remediation Addendum (2026-03-01)

Follow-up hardening was completed after the initial scoring pass:

- `gz readiness audit` command added and wired into `gz check`.
- Readiness eval design now treats Gate 2 (TDD) and Gate 4 (BDD) as first-class signals.
- `.github/discovery-index.json` restored to required control surfaces.
- Readiness audit template added under `docs/governance/GovZero/audits/`.
- Nate transcript summary added under `docs/governance/GovZero/`.
- Governance runbook updated with a readiness-driven design workflow.

Current command state:

```bash
uv run gz readiness audit --json
```

Latest result: `success=true`, `overall_score=3.0`, `required_failures=[]`.
