# GovZero ADR/OBPI/GHI/Audit Linkage

Status: Active
Last reviewed: 2026-01-22
Authority: Canon (linkage, artifact placement, and pre-release identifier conventions)

This document defines the canonical linkage between ADRs, OBPIs, GHIs, and audits.
Gate definitions and closeout behavior remain authoritative in `charter.md` and
`audit-protocol.md`.

## Scope

- Defines how ADR intent, OBPI briefs, GitHub issues, and audit artifacts connect.
- Standardizes where related artifacts live and how they reference each other.
- Does not redefine gate semantics or human attestation rules.

## Definitions

- **ADR**: The intent contract and top-level evidence ledger for a decision.
- **OBPI**: One Brief Per Item; the atomic implementation unit for a single ADR checklist item.
- **GHI**: GitHub Issue used for tracking work (optional but linkable).
- **Audit**: Post-attestation reconciliation artifact that references observed proofs.
- **ADR Closeout Form**: An optional collaboration workspace for the closeout ceremony (observation and attestation).

## Canonical linkage rules

1. Each ADR MUST include a Feature Checklist and an Evidence Ledger.
1. Each checklist item MUST map to exactly one OBPI brief.
1. Each OBPI brief MUST reference its parent ADR and the specific checklist item.
1. The ADR Evidence Ledger MUST include a "Related issues" field; use `none` or `TBD`
   when no GHI exists (no blank fields).
1. If a GHI exists for an OBPI, the OBPI MUST link it and the ADR Evidence Ledger
   SHOULD list it.
1. Audits occur only after human attestation and MUST NOT be treated as proof of
   attestation.
1. ADR Closeout Forms are optional workspaces; they are not proof artifacts and are not
   required for closeout.

---

## Timing of OBPI Creation (Binding)

**OBPIs are co-created with the ADR, not deferred.**

When an ADR is pulled from pool or authored fresh:

1. **At Draft time:** OBPI brief files are created alongside the ADR document
2. **Before Proposed:** All checklist items have corresponding brief files
3. **Before Accepted:** Brief count matches checklist item count (1:1 mapping verified)

**What this means:**

- An ADR cannot be marked Proposed with "TBD" or "Pending" entries in its OBPI table
- Brief files must exist in the `briefs/` directory — a table row is not sufficient
- The brief content may be minimal at Draft (stub acceptable), but the file must exist

**Enforcement:** The `gz-adr-manager` skill creates briefs during ADR creation.
See [adr-lifecycle.md](adr-lifecycle.md) § OBPI Completeness Requirement for the canonical rule.

## Artifact layout

### Pool layout (pre-prioritization)

ADRs in the planning pool live in a dedicated directory with pre-release identifiers.
Pool entries are lightweight — intent only, no OBPIs, no folder structure.

```text
docs/design/adr/pool/
  ADR-0.2.0-pool.exog-pipeline.md       # lightweight intent
  ADR-0.2.0-pool.forecaster-core.md     # target minor version + slug
  ADR-1.3.0-pool.scheduler-cadence.md   # post-1.0 planning
```

**Pool ADR template (minimal):**

```markdown
# ADR-{version}-pool.{slug}

## Intent

[2-3 sentences describing the problem and proposed solution]

## Target Scope

- [Bullet list of major deliverables]

## Dependencies

- [Prerequisites or related ADRs]

## Notes

[Optional: context, alternatives considered, rough effort estimate]
```

When an ADR is pulled from pool for implementation:

1. Assign the next available version number in the target series
2. Create full folder structure under `docs/design/adr/adr-X.Y.x/`
3. Expand intent into full ADR with Feature Checklist and Evidence Ledger
4. Write OBPI briefs for each checklist item
5. Delete or redirect the pool file

### Preferred layout (ADR-contained)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md
  ADR-CLOSEOUT-FORM.md            # optional closeout ceremony workspace
  briefs/
    OBPI-X.Y.Z-01-*.md
    OBPI-X.Y.Z-02-*.md
  audit/
    AUDIT_PLAN.md                 # pre-audit plan
    AUDIT.md                      # post-attestation audit log
    proofs/                       # optional, command outputs and receipts
  logs/
    design-outcomes.jsonl         # optional, agent-facing
```

This layout co-locates intent, briefs, audit, and optional logs for a single ADR.

### Legacy layout (shared briefs tree)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}.md
docs/design/briefs/adr-X.Y.x/adr-X.Y.Z-{slug}/OBPI-X.Y.Z-*.md
docs/design/briefs/adr-X.Y.x/adr-X.Y.Z-{slug}/AUDIT-ADR-X.Y.Z-COMPLETED.md
```

Legacy layout remains valid for historical ADRs. New ADRs SHOULD use the preferred
layout unless a transition plan is explicitly deferred.

**Legacy audit archive:** `docs/design/audit/**` remains historical only; new ADR audits live under
the ADR-contained layout above.

## GHI linkage rules

### GHIs vs OBPIs: Planned vs Emergent Work

**OBPIs are planned work.** Each OBPI is an atomic implementation unit scoped in advance,
tied to an ADR checklist item. OBPIs define what we intend to build.

**GHIs capture emergent work.** GitHub issues are for surprises, bugs, asides, problems,
and anything that surfaces *while fulfilling an OBPI*. GHIs are NOT OBPI-level work
themselves — they are discovered needs that arise during execution.

### GHI Purpose

GHIs should be used for:

- **Bugs** discovered during implementation
- **Surprises** that weren't anticipated in the original brief
- **Asides** — related work noticed but out of scope for the current OBPI
- **Problems** that block or complicate the planned work
- **Discovered needs** — new capabilities revealed as necessary during execution

### GHI-ADR Association

A GHI may be **associated with an ADR** as its discovery context. This means:
"while working on ADR-X.Y.Z, we discovered this need." The association records
provenance, not ownership.

A GHI discovered during ADR work may eventually:

1. Become a new OBPI under the same ADR (if scope fits)
2. Spawn a new ADR (if scope warrants semver bump)
3. Remain tracked for future consideration
4. Be closed as won't-fix or duplicate

### Linkage Mechanics

- GHIs are OPTIONAL. Use them for multi-session work, cross-team coordination, or
  when emergent work needs tracking outside the brief.
- If a GHI exists and relates to an OBPI, link it in the OBPI and in the ADR Evidence Ledger.
- If no GHI exists, use `none` or `TBD` in the ADR Evidence Ledger.

### Pre-Release Identifier Convention

GHIs discovered during ADR work can be tracked using SemVer pre-release identifiers:

```text
{adr-version}-ghi.{issue-number}
```

**Example:** While working on ADR-0.1.15, you discover a bug and create GHI #67.
The identifier `0.1.15-ghi.67` captures:

- **Discovery context**: Found during 0.1.15 work
- **Issue reference**: GitHub Issue #67
- **Precedence**: Sorts before `0.1.15` completion (per SemVer)

This convention is optional but enables unified version-based tracking across ADRs, OBPIs, and GHIs.
See [adr-lifecycle.md](adr-lifecycle.md) for the full pre-release identifier scheme.

## Optional JSONL ledger (agent-facing)

JSONL logs are allowed as agent memory but are not proof and do not replace Markdown
attestation. If used, store under the ADR folder `logs/` and include only trace
metadata. Suggested minimal schema:

```jsonl
{"ts":"ISO8601","obpi":"0.1.12-03","gate":2,"event":"implemented","actor":"agent","commit":"abc123","issue":47,"docs_updated":["path/to/doc"],"learning":""}
```

## References

- Gate definitions: `docs/governance/GovZero/charter.md`
- Closeout ceremony: `docs/governance/GovZero/audit-protocol.md`
- Governance index: `docs/governance/GOVERNANCE_AND_AGENT_TOOLING_INDEX.md`
- Background (non-canonical):
  - `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE.md`
  - `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-CODEX-FEEDBACK.md`
  - `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-COPILOT-FEEDBACK.md`
