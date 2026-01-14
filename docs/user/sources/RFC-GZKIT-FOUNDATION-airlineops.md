# RFC — gzkit (GovZero Kit) Foundation & Spec-Kit Alignment

## 0. Purpose

Establish **gzkit** ("GovZero Kit") as the formalization of our internal governance
methodology. gzkit will serve as the Spec-Kit-inspired, Python-native framework that
codifies our **Five Gates** (ADR, TDD, Docs, BDD, Human Attestation) with **tight Gate 3-5
linkage** and **north-star constitutions** for both AirlineOps and future projects.

**Critical Governance Evolution (v0.1.9+):** Gates 3 (Docs) and 5 (Human
Attestation) are no longer separate concerns. User documentation IS the Gate 5
proof. See `operator_runbook.md` (external) for exemplar
demonstrating determinism, auditability, recoverability, completeness, and
trustworthiness.

---

## 1. Lineage and Reference

**Reference Framework:** [GitHub Spec-Kit](https://github.com/github/spec-kit)

- Spec-Kit’s philosophy of *Constitute → Specify → Plan → Implement → Analyze* is adopted wholesale as gzkit’s phase model.
- We explicitly acknowledge Spec-Kit as the conceptual reference and will document deviations or extensions rather than obscure them.

### Our North Stars = Constitutions

1. **Five Gates Mandatory** — All work must pass: ADR (intent), TDD (tests), Docs (user
   guidance), BDD (contracts), Human Attestation (operator workflows).
2. **Gate 3-5 Linkage** — Documentation (Gate 3) and Human Attestation (Gate 5) are
   inseparable. User docs must demonstrate operational robustness end-to-end.
3. Human-only final attestation (Gate 5).
4. Markdown-only governance artifacts (no JSON/CSV receipts; use structured data only where necessary).
5. Mandatory chain — Brief → ADR → Audit.
6. Immutable audits once signed; new issues → new ADR.
7. Technical sufficiency = observable CLI behavior + exit-codes.
8. Governance is verification, not celebration.
9. Editor-first (VS Code + Copilot) interaction.

---

## 2. Naming and Placement

- **Name:** `gzkit` → short for *GovZero Kit*.
- **CLI alias:** `gz`.
- **Initial placement:** within the main AirlineOps monorepo (`tools/gzkit/` or `docs/governance/gzkit/`).
- **Future:** detachable standalone package once governance and tooling stabilize.

---

## 3. Philosophy

gzkit treats governance as executable documentation: all state lives in Markdown, validated and scaffolded by a Python CLI.
The framework should remain human-centric, auditable, and version-controlled.

### Modes

| Mode | Description |
|------|--------------|
| **lite** | MD-only, human-attested, minimal overhead. |
| **heavy** | Adds BDD artifacts (`.feature` files), optional structured outputs, and richer automation. |

Configuration key:

```json
{
  "mode": "lite"
}
```

### Prompt Lifecycle (GZKit Canonical Summary)

**Source:** Nate B. Jones, "AI News & Strategy Daily" (YouTube)

Prompts are code. Treat them like first-class artifacts with the same rigor
you apply to production software.

#### 1. Intent Formation & Discovery

**Start with clarity, not keyboards.** Define what success looks like. Convert\nvague goals into concrete, testable specs with constraints, assumptions, outputs.

**Key discipline:** No drafting until the intent spec exists. Period.

#### 2. Authoring & Drafting

**Write → Test → Refine.** Treat drafting as iterative.\nGenerate variants, evaluate, converge.

**Key discipline:** Every draft must map back to the intent spec. If it doesn't, you're guessing.

#### 3. Storage & Versioning

**Prompts are versioned artifacts, not throwaway scripts.** Use semantic versioning (`v1.2.3`). Store prompts in predictable, discoverable locations with rich metadata: purpose, model assumptions, dependencies, and change history. Git is your friend—track diffs like you track code.

**Key discipline:** If you can't reproduce a prompt's behavior from its version tag, your versioning is broken.

#### 4. Evaluation & Testing

**Measure everything.** Use canonical fixtures to systematically test prompts.
Track correctness, consistency, hallucination rate, cost per token, and latency.
Compare performance across model versions (GPT-4 vs. Claude) and prompt variants.
Record evaluation results as metadata.

**Key discipline:** Untested prompts are untrustworthy prompts. Build a test harness.

#### 5. Workflow Construction & Automation

**Compose, don't monolith.** Build multi-step workflows where prompts collaborate via
tools, memory, and conditional logic. Define clear roles: system prompts set behavior, task
prompts drive execution, tool schemas enforce structure. Use deterministic schemas for I/O
between steps—no loose strings, no "figure it out" handwaving.

**Key discipline:** Format discipline is workflow discipline. Lock down your interfaces.

#### 6. Deployment & Production Integration

**Ship with observability.** Integrate prompts via configuration-driven hot-swapping (never hard-code them). Log every production use, track version lineage, and monitor for quality drift over time. Implement fallback logic for failures and preserve full traceability across deployments.

**Key discipline:** If you can't trace a production output back to a specific prompt version, you're flying blind.

---

#### Ultra-Concise Embeddable Version (GZKit)

Adapted from Nate B. Jones (AI News & Strategy Daily).

**Prompt Lifecycle:**

1. **Intent** → explicit, testable spec before drafting
2. **Drafting** → iterative write/test/refine loops
3. **Versioning** → semver, metadata, reproducibility
4. **Evaluation** → canonical tests, metrics, drift tracking
5. **Workflow** → compose via tools/memory/schemas
6. **Deployment** → monitoring, fallback, traceability

---

## 4. CLI Phases & Verb Parity (Five Gates Integrated)

| Phase | Verb | Purpose | Spec-Kit Parity | Gates Covered | Notes |
|--------|------|----------|-----------------|---------------|-------|
| 1 | `constitute` | Define north-stars & charters | ✅ Constitute | ADR (Gate 1) | gzkit constitutions live under `docs/governance/gzkit/constitutions/`. |
| 2 | `specify` | Create briefs/specs | ✅ Specify | ADR (Gate 1) | Links to ADRs and acceptance criteria. |
| 3 | `plan` | Manage ADRs and linkage | ✅ Plan | ADR (Gate 1) | Inserts Gate 3-5 pointers automatically. |
| 4 | `implement` | Verify code + docs + BDD | ✅ Implement | TDD (Gate 2), Docs (Gate 3), BDD (Gate 4) | Runs tests, mkdocs build, Behave scenarios; ensures Gate 3-5 docs link. |
| 5 | `analyze` / `attest` | Human audit + operator workflows | ✅ Analyze / Attest | Human (Gate 5) + Docs (Gate 3) | Gate-5 layer; Gate 3 docs ARE the attestation proof (tight linkage). |

**Five Gates Enforcement:** Phases 1-4 are automated; Phase 5 (Human Attestation) is human-reviewed but relies on Gate 3 docs as proof vehicles.

Aliasing (configurable):

```json
{
  "aliases": {
    "specify": ["spec"],
    "analyze": ["audit", "attest"]
  }
}
```

---

## 5. Config Schema (draft)

`.gzkit.json`

```json
{
  "mode": "lite",
  "paths": {
    "specs": "docs/briefs",
    "adrs": "docs/adr",
    "audits": "docs/audit"
  },
  "aliases": {
    "specify": ["spec"],
    "analyze": ["audit"]
  },
  "license": "internal",
  "tag_style": "vX.Y.Z"
}
```

---

## 6. Gate-5 Pointer Rule (Gate 3-5 Linkage)

**Critical:** Gate 5 (Human Attestation) is proven via Gate 3 (Docs) — they are inseparable.

Each ADR `## Evidence` block must contain BOTH:

```markdown
Verified under Gate-3 (Docs): operator_runbook.md § [relevant section]
Verified under Gate-5 (Human): docs/design/audit/ADR-x.y.z/AUDIT.md
```

**Why linked:** User documentation (Gate 3) demonstrates operational workflows end-to-end. Running those workflows is the Gate 5 attestation. Documentation IS proof.

gzkit will check and insert these lines automatically if missing.

**Example (AirlineOps OBPI-13, OBPI-52, OBPI-53):**

```markdown
## Evidence

### Gate 1: ADR
- Parent: ADR-0.1.9-aviation-core-cemented

### Gate 2: TDD
- Coverage: 42.60% (exceeds ≥40% floor)
- Tests: 1223/1223 passing

### Gate 3: Docs
- User guide: operator_runbook.md § "Gate 5: Human Attestation — Complete Workflows"
- Markdown lint: PASS
- mkdocs build: PASS

### Gate 4: BDD
- Policy storage scenarios: 10/10 passing (behave)
- Warehouse orchestrate scenarios: 15/15 passing

### Gate 5: Human Attestation
- Operator attestation: docs/user/operator_runbook.md demonstrates end-to-end discovery→planning→execution→validation→reporting
- Error recovery proofs: Scenario A (transient), B (permanent), C (operator override)
- Cross-dataset coordination: FAA/BTS AIRAC alignment proven
```

---

## 7. Modes & Tool Behavior (Five Gates)

| Element | Lite Lane | Heavy Lane |
|----------|------------|-------------|
| **Gate 1: ADR** | Intent only | Intent + detailed rationale |
| **Gate 2: TDD** | ≥40% coverage | ≥40% coverage |
| **Gate 3: Docs** | User guide present | Markdown lint + mkdocs build + docs proof |
| **Gate 4: BDD** | Off (internal only) | `.feature` files + Behave runner |
| **Gate 5: Human** | Implicit (via code) | Explicit operator workflows (runbook/walkthrough) |
| **Governance files** | Markdown only | Markdown + optional JSON/CSV summaries |
| **CI/Lint** | Ruff + Type check | + BDD smoke tests + markdown lint + docs proof |

**Key Difference:** Heavy lane makes Gate 5 explicit — operator documentation is mandatory proof of robustness.

---

## 8. Interop with AirlineOps and OpsDev

- **Short term:** gzkit is a governance companion for AirlineOps; no runtime coupling.
- **Long term:** becomes a shared toolkit for any project using the GovZero method.
- **OpsDev bridge:** gzkit commands will surface within OpsDev CLI wrappers (`uv run gz …`).

---

## 9. Implementation Roadmap (Pre 1.0)

1. **RFC (you are here)** — capture all prior design discussions.
2. **Prototype CLI** — no-op commands + template scaffolding.
3. **Lite mode integration** — Gate-5 audits for ADR-0.1.8+ pipeline.
4. **Heavy mode expansion** — introduce BDD and structured outputs.
5. **Extraction & publish** — convert to standalone repo post AirlineOps 1.0.0.

---

## 10. Acknowledged Differences from Spec-Kit

| Area | Spec-Kit | gzkit |
|-------|-----------|-------|
| Artifact type | JSON + YAML + MD | Markdown (default) + opt JSON in heavy |
| Attestation | Tool driven | Human-only final (Gate 5 explicit) |
| Gates | Implicit via process | Explicit Five Gates with Gate 3-5 linkage |
| BDD support | None explicit | Native (Behave or similar) |
| Language bias | Polyglot (JS, Ruby, etc.) | Python-first (3.11+) |
| Modes | Single workflow | Lite/Heavy config switch |
| Integration | GitHub Actions | Local CLI + VS Code/Copilot |
| Docs role | Documentation separate | **Docs ARE the Gate 5 proof** (tight linkage) |

---

## 11. Structured vs. Prose Governance (Design Insight)

### The Markdown Lint Problem

**Observation from AirlineOps CI simplification (2024-11-09):**

Mixing **structured data** (audit tables, SQL snippets, bold labels) with **prose formatting rules** (MD013 line-length, MD036 emphasis-as-heading) creates constant friction:

- ❌ Audit files need long lines for SQL/technical content (>200 chars)
- ❌ Markdown lint wants prose flow (short lines, heading hierarchy)
- ❌ Result: Blocked commits, token waste fixing formatting, not content

**Root cause:** Trying to make Markdown be **both human-readable AND machine-structured**.

### Ledgers > Receipts

**Traditional receipt (prose attestation):**

```markdown
# Receipt: DB1B Q3 2024 Load

On 2024-11-09, Jeff verified that DB1B market data for Q3 2024 loaded correctly.

- Dataset: bts_db1b_market
- Period: 2024-Q3
- Row count: 1,234,567
- SHA256: abc123...

Signature: [human]
```

**Problems:**

- Hard to validate (requires parsing markdown, checking signatures)
- Becomes stale (what if code changes? Receipt is historical, not current)
- Token-intensive to maintain (formatting, linking, dating)
- Not queryable (can't ask "show all Q3 2024 loads")

**Structured ledger (append-only JSONL):**

```jsonl
{"event":"warehouse_load","dataset":"bts_db1b_market","period":"2024-Q3","sha256":"abc123...","row_count":1234567,"admitted":true,"run_id":"uuid","started_at_utc":"2024-11-09T14:32:00Z"}
```

**Benefits:**

- ✅ Machine-readable: `jq`, `grep`, Python scripts can query
- ✅ Append-only: Audit trail without mutating history
- ✅ Deterministic: No formatting ambiguity, no markdown lint
- ✅ Queryable: "Show all Q3 2024 loads" = `jq 'select(.period=="2024-Q3")'`
- ✅ Reproducible: Ledger + test script = current proof (re-run if needed)

### GovZero Principle: Ephemeral Proof

**GovZero formula:**

```text
ADR (intent) + Ledger (events) + Test (validator) = Proof
```

**NOT:**

```text
ADR (intent) + Receipt (human attestation) + Signatures = Proof
```

**Why ledgers work:**

- 🤖 Automated: Tests run in CI, no human paperwork
- 📊 Queryable: Ledgers are data, receipts are prose
- 🔄 Reproducible: Re-run test to prove current state, not historical claim
- 💰 Token-efficient: No markdown formatting fights
- ⚡ Fast: No heavyweight docs to maintain

**Evidence = `uv run -m opsdev gates` (green output) + ledger entries + test report**

### Implications for gzkit

**Markdown should be for:**

- ✅ ADR intent/rationale (immutable after acceptance)
- ✅ Briefs (work scoping, acceptance criteria)
- ✅ Human-readable audit summaries (pointers to structured proof)
- ❌ NOT structured data tables (use YAML/JSON/CSV/JSONL)
- ❌ NOT machine-parsed contracts (use Behave `.feature` or YAML specs)

**Structured formats for:**

- ✅ Ledgers: JSONL (append-only audit trail)
- ✅ Configs: JSON (validated schemas)
- ✅ Test data: CSV, JSON (deterministic fixtures)
- ✅ Specs: YAML (machine-readable contracts, if Spec-Kit-aligned)

**gzkit should:**

1. Keep ADRs as prose (intent/rationale only, not duplicate checklists)
2. Move acceptance criteria → YAML specs (machine-readable)
3. Audit summaries → markdown pointers to structured evidence (ledgers, test reports)
4. Evidence validation → test scripts that query ledgers (`@covers` decorators link tests to specs)
5. Avoid heavyweight markdown receipts (ephemeral proof via reproducible commands)

### CI/Pre-commit Alignment

**AirlineOps learned (2024-11-09):**

- Pre-commit: Standard tools only (ruff, ty, unittest) - no markdown lint
- CI: Transparent UV commands (coverage, build) - no opsdev wrappers
- Developer rituals: `opsdev lite/heavy` (opt-in thoroughness checks)
- Markdown/YAML lint: Only in `opsdev heavy` (non-blocking, for PR prep)

**gzkit should adopt:**

- Structured validation in automation (AST checks, schema validation, test assertions)
- Prose formatting as opt-in quality gate (not blocking)
- Clear separation: automated gates vs. developer rituals
- **Gate 3-5 linkage enforcement:** Docs build passes → Gate 3 proof exists → can attest Gate 5

---

## 12. Open Questions

- Config placement: root `.gzkit.json` or under `governance/`?
- Default mode: `lite` for students or `heavy` for internal use?
- How to display gate status visually (`gz status` command vs table in docs)?
- Should gzkit auto-generate Spec-Kit-compatible metadata for future interop?
- Should acceptance criteria move from ADR prose → YAML specs? (Spec-Kit alignment)
- What's the minimal ledger schema for evidence? (event type, timestamp, artifact refs)

---

## 13. References

- GitHub Spec-Kit docs & examples
- GovZero v4/v5 Charters with Five Gates
- ADR-0.1.9-aviation-core-cemented (external) — Canonical example of Five Gates in practice (OBPI-13, OBPI-52, OBPI-53)
- operator_runbook.md (external) — Gate 3-5 Linkage exemplar (comprehensive human attestation)
- Gate-5 Charter (2025-10 edition, updated for Gate 3-5 linkage 2025-12)

---

**Status:** Draft (Five Gates evolution incorporated 2025-12-04)
**Owner:** JB
**Intended Readiness:** Align with AirlineOps 1.0.0 (Zero-to-One use case); Gate 3-5 linkage foundational
**Next Step:** Confirm structure → author `CPB-GZKIT-INITIATE.md` to scaffold CLI skeleton once approved.
