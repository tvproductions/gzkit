# AirlineOps GovZero Exploration — Verbatim

**Date:** 2026-01-22
**Context:** Raw output from exploring airlineops codebase to understand GovZero in practice

---

## Summary: Governance Concepts from AirlineOps That gzkit Should Document

Based on my thorough search of the airlineops codebase, here are the key governance concepts and practices that gzkit should document:

---

### 1. OBPIs (Observable Behavioral Progress Indicators)

**What they are:**
- OBPI = "One Brief Per Item"
- Atomic implementation units that map 1:1 to ADR checklist items
- Each OBPI is a single markdown brief document describing exactly one piece of work
- Located in `docs/design/adr/{adr-folder}/briefs/` or `docs/design/briefs/{adr-path}/`

**Numbering discipline (mandatory):**
- Sequential, zero-gap numbering: `OBPI-0.0.19-01`, `OBPI-0.0.19-02`, `OBPI-0.0.19-03`
- If an ADR has 19 checklist items → OBPIs 01 through 19 (no gaps, no categorical grouping)
- Pre-release identifier scheme: `0.1.15-obpi.03` (SemVer compliant)

**OBPI anatomy:**
- Parent ADR reference and checklist item mapping
- Objective statement
- Lane designation (Lite/Heavy)
- Allowed/Denied paths (scope boundaries)
- Requirements (fail-closed)
- Acceptance Criteria
- Gate evidence (what commands/artifacts prove completion)

**Example:** `/Users/jeff/Documents/Code/airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.19-AIRAC-orchestrated-warehouse-pipeline/briefs/OBPI-0.0.19-01-canonicalize-librarian.md`

---

### 2. Closeout Ceremonies (Hard-Mode Attestation Protocol)

**What it is:**
- A **mode transition** where the agent yields interpretive authority to the human
- Triggered by human invocation: "ADR closeout ceremony" (or equivalents: "begin closeout", "closeout ADR-X.Y.Z")
- Ensures human attestation is grounded in **direct observation**, not mediated through agent claims

**Why it matters (epistemic integrity):**
- Prevents "mediated observation" where humans see reality only through agent lens
- Agent presents **paths and commands**, not **conclusions and outcomes**
- Human executes and observes directly; agent is a "silent index"
- Eliminates corruption risk from agent errors/bias

**Attestation forms (canonical):**
The human MUST provide exactly one of these explicit forms:
- **"Completed"** — All work finished; claims verified
- **"Completed — Partial: [reason]"** — Subset accepted; remainder deferred with documented rationale
- **"Dropped — [reason]"** — ADR rejected; clear rationale provided

**Agent behavior during closeout (MUST):**
1. Recognize the trigger phrase as mode transition
2. Immediately yield interpretive authority
3. Present **raw artifact paths and commands** for human execution, NOT summaries
4. Wait for **explicit** human attestation before recording
5. Run audit checks **only after** attestation (post-closeout)
6. Reference gates by number only; defer to charter for definitions
7. Surface audit-protocol.md for human reference

**Agent behavior during closeout (MUST NOT):**
1. Summarize or interpret evidence outcomes
2. Infer attestation from silence/continuation
3. Auto-close based on passing checks
4. Run audit during closeout mode
5. Present ledger entries as proof of completion
6. Redefine gate semantics
7. Offer to "check if requirements are met" (human checks; agent presents paths)
8. Proceed to post-closeout tasks until attestation recorded

**Closeout Form template:**
- Located at `ADR-CLOSEOUT-FORM.md` in ADR folder
- Optional workspace for collaboration during ceremony
- Pre-attestation checklist, human attestation phase, post-attestation audit section
- Phase markers: Phase 1 (COMPLETED) → Phase 2 (VALIDATED)

**Example:** `/Users/jeff/Documents/Code/airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.19-AIRAC-orchestrated-warehouse-pipeline/ADR-CLOSEOUT-FORM.md`

---

### 3. Daily Workflow Patterns

**Git Sync Ritual:**
- Mentioned in CLAUDE.md as part of standard workflow
- Command: `uv run -m opsdev git-sync --apply --lint --test`
- Workflow element that integrates governance checks into development flow

**Gate Progression Pattern (Lite Lane):**
1. **Gate 1 (ADR):** Record intent; checklist items → OBPI briefs
2. **Gate 2 (TDD):** Passing tests; coverage ≥40%
3. Lite lane complete; code merged

**Gate Progression Pattern (Heavy Lane):**
1. **Gate 1 (ADR):** Record intent; detailed Feature Checklist
2. **Gate 2 (TDD):** Passing tests; coverage ≥40%
3. **Gate 3 (Docs):** Documentation build passes; markdown lint clean; links valid
4. **Gate 4 (BDD):** Passing Behave scenarios for external contracts
5. **Gate 5 (Human Attestation):** Closeout ceremony; explicit human attestation
6. **Post-Attestation:** Audit run; ADR status → Validated

**Documentation = Gate 5 Artifact (critical insight):**
- Gate 5 is NOT a separate deliverable; it's the **result of comprehensive documentation updates**
- When code changes → operator documentation must reflect those changes
- When workflows change → runbooks/walkthroughs must be updated
- When contracts change → help text, CLI docs, user guides must be revised
- Agents treat documentation updates as **required, first-class delivery** alongside code
- No hand-holding; same rigor as Gates 1-4

**Heavy Lane Documentation Obligation (no discretion):**
- Scan relevant docs BEFORE starting work
- Update all affected documentation surfaces in the same PR/branch
- Ensure docstrings match actual behavior
- Ensure CLI help text is current
- Ensure runbooks/walkthroughs have concrete, working examples
- Ensure links/anchors are valid
- Run markdown lint + mkdocs build to validate

---

### 4. ADR/OBPI/GHI/Audit Linkage and Topology

**ADR structure (preferred modern layout):**
```
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md           # Intent document
  ADR-CLOSEOUT-FORM.md          # Optional ceremony workspace
  briefs/
    OBPI-X.Y.Z-01-*.md          # Brief for checklist item 1
    OBPI-X.Y.Z-02-*.md          # Brief for checklist item 2
    ...                         # Sequential, no gaps
  audit/
    AUDIT_PLAN.md               # Pre-audit plan
    AUDIT.md                    # Post-attestation audit log
    proofs/                     # Optional command outputs, receipts
  logs/
    design-outcomes.jsonl       # Optional agent-facing metadata
```

**ADR Lifecycle States (canonical, mutually exclusive):**
1. **Pool** — Planned, lightweight intent only (pre-prioritization)
2. **Draft** — Being authored; not ready for review
3. **Proposed** — Submitted for review; awaiting acceptance
4. **Accepted** — Approved; implementation may begin
5. **Completed** — Implementation finished; Gate 5 attestation received
6. **Validated** — Post-attestation audit completed (Phase 2)
7. **Superseded** — Replaced by newer ADR
8. **Abandoned** — Work stopped; clear rationale

**Pre-release identifier scheme (SemVer compliant):**
- Format: `{major}.{minor}.{patch}[-{type}.{identifier}]`
- Types:
  - `pool.{slug}` — Planned ADR in pool (`0.2.0-pool.forecaster-core`)
  - `obpi.{nn}` — OBPI in progress (`0.1.15-obpi.03`)
  - `ghi.{nn}` — GitHub issue discovered during work (`0.1.15-ghi.67`)

**OBPIs vs GHIs distinction:**
- **OBPIs = planned work** — scoped in advance, tied to ADR checklist items
- **GHIs = emergent work** — bugs, surprises, asides discovered while fulfilling OBPI
- GHIs are NOT OBPI-level work themselves; they're discovered needs surfaced during execution

---

### 5. Tooling and Commands for Managing ADRs/OBPIs

**Core Skills (workflow automation):**

Available as reusable procedures in `.github/skills/`:

1. **gz-adr-manager** (`SKILL.md`)
   - Create/update ADR documents
   - Structure ADR folder, initialize briefs, update registries

2. **gz-obpi-brief** (`SKILL.md`)
   - Generate compliant OBPI markdown brief
   - Enforce One Brief Per Item discipline
   - Template-driven with Heavy Lane mandatory planning template

3. **gz-adr-closeout-ceremony** (`SKILL.md`)
   - Execute closeout ceremony protocol
   - Present artifact paths/commands-only summary
   - Guide human through direct observation (no interpretation)

4. **gz-adr-audit** (`SKILL.md`)
   - Gate-5 audit templates and procedure
   - Post-attestation reconciliation

5. **gz-adr-sync** (`SKILL.md`)
   - Sync ADR index and status tables from source files
   - Detect and reconcile drift

6. **gz-obpi-sync** (`SKILL.md`)
   - Sync OBPI status in ADR table from brief sources
   - Detect and reconcile drift

7. **gz-adr-verification** (`SKILL.md`)
   - Generate ADR→tests verification report
   - Use @covers mappings to link ADR to test coverage

**Governance Manifest:**
- Machine-readable governance config at `config/governance_manifest.json`
- Canonical reference for verification commands, gate definitions, doctrine

**Registries (must stay in sync):**
- `docs/design/adr/adr_index.md`
- `docs/design/adr/adr_status.md`
- `docs/governance/GovZero/adr-status.md` (canonical location)

---

### 6. Five Gates Framework

**Gate definitions (sole authority: `charter.md`):**

| Gate | Purpose | Lane | Artifact | Authority |
|------|---------|------|----------|-----------|
| **Gate 1** | Record intent & tradeoffs | Lite, Heavy | ADR document with problem/decision/consequences | ADR author |
| **Gate 2** | Verify implementation correctness | Lite, Heavy | Passing unit tests; coverage ≥40% | CI/test results |
| **Gate 3** | Ensure docs describe behavior accurately | Heavy only | Clean markdown lint, mkdocs build passes, links/anchors valid | Markdown validator + manual review |
| **Gate 4** | Verify external contract behavior | Heavy only | Passing Behave scenarios for CLI/API/schema contracts | Behave test results |
| **Gate 5** | Human directly observes & attests | Heavy only | Explicit human attestation recorded with timestamp | **Human attestation only** |

**Lane Selection:**
- **Lite:** Internal changes only (no external contract changes)
- **Heavy:** External contract changes (CLI, API, schema, error messages)

---

### 7. Key Invariants and Governance Philosophy

**Alignment Chain Covenant:**
```
Intent (ADR/OBPI) ↔ Code (behavior) ↔ Docs (claims)
```
All three links must hold. If any breaks, work isn't done.

**Scope expansion is not scope creep:**
- Agents own work completely
- Never defer or say "out of scope"
- Fix everything broken/misaligned immediately

**Documentation is not optional for Heavy lane:**
- Operator runbooks, walkthroughs, docstrings, mkdocs docs
- All surfaces must form coherent public contract
- No hand-holding; treat as first-class delivery

**Human authority is singular:**
- Only humans can attest to ADR completion (Gate 5)
- Agents present artifacts; humans observe and attest
- Audit runs **post-attestation** for reconciliation only
- Ledgers/logs are agent-facing, not proof

---

### 8. Referenced Key Documents

**GovZero Canon (in `docs/governance/GovZero/`):**
- `charter.md` — Sole authority for gate definitions
- `adr-lifecycle.md` — Lifecycle states, pre-release identifiers, status mapping
- `adr-obpi-ghi-audit-linkage.md` — Canonical linkage rules, artifact placement
- `audit-protocol.md` — Closeout ceremony behavior, agent scripts

**Key Governance Files:**
- `/AGENTS.md` — AI agent contract; GovZero v6 multi-agent edition
- `docs/design/adr/CLAUDE.md` — ADR governance rules for Claude Code
- `docs/governance/gate5_documentation_obligation.md` — Gate 5 definitive rules
- `docs/governance/AGENTS_MD_BEHAVIORAL_INVENTORY.md` — Behavioral checklist

---

### Key Takeaways for gzkit Documentation

1. **OBPIs are the atomic unit of work** — each maps to one checklist item; numbering must be sequential
2. **Closeout ceremony is a mode transition** — agent yields authority; human observes directly (never through agent interpretation)
3. **Documentation IS the Gate 5 artifact** — not a separate deliverable; comprehensive doc updates are required for Heavy lane
4. **Five Gates form an integrity chain** — all must pass; ADR intent must align with code behavior and documentation claims
5. **Governance is executable** — lives in markdown, validated by Python CLI (gzkit)
6. **Human attestation is the closure gate** — agents present; humans attest; audit reconciles post-attestation
7. **Skills provide reusable procedures** — ADR creation, OBPI generation, closeout ceremony, audit, sync/verification

---

### Files for Reference

**Absolute paths to key documents:**
- `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/charter.md`
- `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/adr-lifecycle.md`
- `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
- `/Users/jeff/Documents/Code/airlineops/docs/governance/GovZero/audit-protocol.md`
- `/Users/jeff/Documents/Code/airlineops/AGENTS.md`
- `/Users/jeff/Documents/Code/airlineops/docs/design/adr/CLAUDE.md`
- `/Users/jeff/Documents/Code/airlineops/docs/governance/gate5_documentation_obligation.md`
- `/Users/jeff/Documents/Code/airlineops/.github/skills/gz-adr-*` (suite of skills)
