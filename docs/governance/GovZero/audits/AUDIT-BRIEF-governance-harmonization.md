# Audit Brief: Governance Document Harmonization

Status: Pending
Created: 2026-01-11
Assigned: [Fresh Agent]
Output: `docs/governance/GovZero/audits/governance-harmonization-2026-01-11.md`

---

## Objective

Audit all documents in `docs/governance/` for drift against the canonical GovZero documents.
Produce a harmonization report with consolidation recommendations.

---

## Source of Truth

The following documents in `docs/governance/GovZero/` are **canonical**:

| Document | Authority |
|----------|-----------|
| `charter.md` | Gate definitions, lane doctrine, closeout attestation terms |
| `adr-lifecycle.md` | ADR lifecycle states, closeout-to-status mapping |
| `adr-status.md` | Authoritative ADR status table (uses lifecycle states from adr-lifecycle.md) |
| `audit-protocol.md` | Closeout ceremony behavior, agent MUST/MUST NOT rules |
| `adr-obpi-ghi-audit-linkage.md` | Relationship between ADR, OBPI, GHI, and audit artifacts |

All other governance documents MUST align with these or be marked superseded.

---

## Audit Scope

Examine every `.md` file in:

- `docs/governance/*.md` (root level)
- `docs/governance/db28/`
- `docs/governance/gzkit/`
- Any other subdirectories except `GovZero/` itself

Also examine:
- `docs/design/adr/_TEMPLATES/ADR_TEMPLATE_SEMVER.md` — Does the Status field align with adr-lifecycle.md?
- Any remaining references to the old `docs/design/adr/adr_status.md` path (now moved to GovZero)

---

## Audit Questions Per Document

For each document, answer:

1. **Relevance**: Is this document still relevant, or has its content been absorbed into GovZero?
2. **Conflict**: Does it define terms, statuses, or processes that conflict with GovZero canon?
3. **Redundancy**: Does it duplicate content that exists in GovZero?
4. **Reference**: Does it properly reference GovZero for canonical definitions, or does it redefine them?
5. **Disposition**: Should this document be:
   - **Kept**: Still relevant, no conflict
   - **Updated**: Relevant but needs alignment edits
   - **Superseded**: Move to `_archive/` with supersession header
   - **Consolidated**: Merge useful content into GovZero, then archive

---

## Consolidation Strategy (Moderate)

1. **Centralize**: If a document has useful content not in GovZero, propose where to add it
1. **Archive**: Move superseded documents to `docs/governance/_archive/` with header:

   ```markdown
   > **SUPERSEDED**: This document is superseded by [GovZero/{doc}.md](GovZero/{doc}.md).
   > Retained for historical reference only. Do not use for current guidance.
   ```

1. **Update references**: Any document referencing an archived doc should be updated to point to GovZero

---

## Output Format

Produce a report at `docs/governance/GovZero/audits/governance-harmonization-2026-01-11.md` with:

### Section 1: Executive Summary

- Total documents audited
- Counts by disposition (Kept / Updated / Superseded / Consolidated)
- Critical conflicts found

### Section 2: Document-by-Document Analysis

For each document:

```markdown
### {filename}
- **Path**: `docs/governance/{path}`
- **Disposition**: {Kept | Updated | Superseded | Consolidated}
- **Conflicts**: {None | List of conflicts}
- **Action Required**: {None | Specific edits | Archive | Merge into X}
- **Notes**: {Any additional context}
```

### Section 3: Recommended Actions

Prioritized list of changes to make, grouped by:
- Immediate (conflicts with GovZero canon)
- Near-term (redundancy cleanup)
- Deferred (nice-to-have consolidation)

### Section 4: Open Questions

Any unresolved questions for human decision (e.g., "where should ADR templates live?")

---

## Agent Instructions

1. **Read GovZero canon first**: Before auditing other docs, read all four canonical GovZero documents to internalize the source of truth.

2. **Do not modify files during audit**: This is a read-only audit. Produce the report only.

3. **Flag ambiguity**: If a document's disposition is unclear, mark it as "Needs Human Decision" with rationale.

4. **Note template drift**: The ADR template defines valid statuses. These MUST match adr-lifecycle.md.

5. **Find stale references**: Search for any docs still pointing to `docs/design/adr/adr_status.md` (old path).

6. **Preserve useful content**: If a document has unique, useful content not in GovZero, recommend consolidation rather than deletion.

---

## Success Criteria

- [ ] All documents in `docs/governance/` (except GovZero/) have been audited
- [ ] `adr_status.md` and ADR template have been checked for alignment
- [ ] Report is written to specified output path
- [ ] Each document has a clear disposition
- [ ] Conflicts are explicitly listed
- [ ] Recommended actions are prioritized
