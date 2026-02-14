# Governance Document Harmonization Report

**Date:** 2026-01-11
**Auditor:** Claude Code (Opus 4.5)
**Brief:** `AUDIT-BRIEF-governance-harmonization.md`

---

## Section 1: Executive Summary

| Metric | Count |
|--------|-------|
| **Total documents audited** | 21 |
| **Kept** | 14 |
| **Updated** | 5 |
| **Superseded** | 0 |
| **Consolidated** | 0 |
| **Needs Human Decision** | 2 |

### Critical Conflicts Found

1. **ADR Template Status Field** — Includes "Deprecated" (a deprecated term per `adr-lifecycle.md`) and omits "Draft" and "Proposed" as valid states.

2. **Stale Path References** — 35 files reference the old `docs/design/adr/adr_status.md` path; canonical location is now `docs/governance/GovZero/adr-status.md`.

3. **GovZero Version Drift** — Several documents reference "GovZero v4" or "GovZero v5" without acknowledging the current v6 (effective 2026-01-05).

---

## Section 2: Document-by-Document Analysis

### index.md

- **Path:** `docs/governance/index.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Well-organized governance index. Properly references GovZero as canonical source.

---

### GOVERNANCE_AND_AGENT_TOOLING_INDEX.md

- **Path:** `docs/governance/GOVERNANCE_AND_AGENT_TOOLING_INDEX.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Comprehensive index of governance surfaces. Already notes GovZero version drift as a known gap. Valuable reference document.

---

### ADR_DISPOSITION_RUBRIC.md

- **Path:** `docs/governance/ADR_DISPOSITION_RUBRIC.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Properly references `GovZero/charter.md` for gate definitions. Useful rubric for ADR evaluation.

---

### REPO_LAYOUT.md

- **Path:** `docs/governance/REPO_LAYOUT.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Describes repository folder structure. Complements `THREE_TIER_STRUCTURE.md`.

---

### ROADMAP.md

- **Path:** `docs/governance/ROADMAP.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Living planning document. Not governance doctrine.

---

### THREE_TIER_STRUCTURE.md

- **Path:** `docs/governance/THREE_TIER_STRUCTURE.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Defines config/artifacts/tmp tier separation. Well-maintained with verification commands.

---

### agent_skills.md

- **Path:** `docs/governance/agent_skills.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Defines skill discovery and precedence. Referenced by `AGENTS.md`.

---

### gate5_documentation_obligation.md

- **Path:** `docs/governance/gate5_documentation_obligation.md`
- **Disposition:** Updated
- **Conflicts:** References "v4" and "v5" evolution without mentioning current v6
- **Action Required:** Add note clarifying relationship to GovZero v6, or update version references
- **Notes:** Core Gate 5 doctrine. Content is aligned with GovZero canon but version numbering is stale.

---

### markdown_hygiene.md

- **Path:** `docs/governance/markdown_hygiene.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** References `.github/copilot-instructions.md` as authoritative source. Proper delegation.

---

### operator-documentation-philosophy.md

- **Path:** `docs/governance/operator-documentation-philosophy.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Anchored to ADR-0.0.8. Philosophy document, not normative.

---

### pep257_manpage_adoption.md

- **Path:** `docs/governance/pep257_manpage_adoption.md`
- **Disposition:** Updated
- **Conflicts:** References section says "GovZero v5" but current is v6
- **Action Required:** Update reference to GovZero v6 or add clarifying note
- **Notes:** Defines 3-layer documentation architecture (runbook → manpages → docstrings). Content aligns with GovZero canon.

---

### adr_audit_tools_reference.md

- **Path:** `docs/governance/adr_audit_tools_reference.md`
- **Disposition:** Updated
- **Conflicts:** Example output path `adr-status.txt` may confuse with old `adr_status.md` location
- **Action Required:** Clarify that `adr-status.txt` is command output, not the canonical status table
- **Notes:** Useful command reference for audit workflows.

---

### airlineops_north_star_1.0.0.md

- **Path:** `docs/governance/airlineops_north_star_1.0.0.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Program direction document. Not governance doctrine.

---

### github_labels.md

- **Path:** `docs/governance/github_labels.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Simple reference for GitHub label conventions.

---

### bts_package_management_policy.md

- **Path:** `docs/governance/bts_package_management_policy.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Comprehensive BTS dataset policy. Domain-specific, not governance doctrine.

---

### CLAUDE-CODE-EVALUATION-BRIEF.md

- **Path:** `docs/governance/CLAUDE-CODE-EVALUATION-BRIEF.md`
- **Disposition:** Needs Human Decision
- **Conflicts:** None
- **Action Required:** Decide: keep as historical record or archive
- **Notes:** Draft evaluation document from a specific session. Not normative. Could be archived to `_archive/` or kept as historical reference.

---

### GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE.md

- **Path:** `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Already marked as "Background (non-canonical)" in `adr-obpi-ghi-audit-linkage.md`. Design discussion document.

---

### GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-COPILOT-FEEDBACK.md

- **Path:** `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-COPILOT-FEEDBACK.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Feedback document. Non-canonical background material.

---

### GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-CODEX-FEEDBACK.md

- **Path:** `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-CODEX-FEEDBACK.md`
- **Disposition:** Needs Human Decision
- **Conflicts:** None
- **Action Required:** Decide: keep as historical record or archive
- **Notes:** Feedback document. Non-canonical background material. Similar to Copilot feedback doc.

---

### db28/stabilization.md

- **Path:** `docs/governance/db28/stabilization.md`
- **Disposition:** Kept
- **Conflicts:** None
- **Action Required:** None
- **Notes:** Domain-specific DB28 stabilization policy. Not general governance.

---

### gzkit/RFC-GZKIT-FOUNDATION.md

- **Path:** `docs/governance/gzkit/RFC-GZKIT-FOUNDATION.md`
- **Disposition:** Updated
- **Conflicts:** References "GovZero v4/v5" throughout; status says "Five Gates evolution incorporated 2025-12-04" but current GovZero is v6 (2026-01-05)
- **Action Required:** Update to reference GovZero v6 or add note that RFC predates v6 and will be aligned when activated
- **Notes:** Draft RFC for future gzkit framework. Conceptually aligned but version references are stale.

---

### ADR Template (docs/design/adr/_TEMPLATES/ADR_TEMPLATE_SEMVER.md)

- **Path:** `docs/design/adr/_TEMPLATES/ADR_TEMPLATE_SEMVER.md`
- **Disposition:** Updated
- **Conflicts:**
  - Status field includes "Deprecated" which is a deprecated term per `adr-lifecycle.md`
  - Status field omits "Draft" and "Proposed" as valid states
- **Action Required:** Update Status field to match `adr-lifecycle.md`: `**Status:** {Draft | Proposed | Accepted | Completed | Superseded | Abandoned}`
- **Notes:** Critical alignment issue. Template defines what agents and humans use for new ADRs.

---

## Section 3: Recommended Actions

### Immediate (Conflicts with GovZero Canon)

1. Fix ADR Template Status Field — File: `docs/design/adr/_TEMPLATES/ADR_TEMPLATE_SEMVER.md`
   - Change: Replace `{Accepted | Completed | Superseded | Deprecated | Abandoned}` with `{Draft | Proposed | Accepted | Completed | Superseded | Abandoned}`
   - Rationale: "Deprecated" is explicitly deprecated in `adr-lifecycle.md`; "Draft" and "Proposed" are valid lifecycle states

2. Update Stale Path References — Scope: 35 files reference `docs/design/adr/adr_status.md`
   - Change: Update to `docs/governance/GovZero/adr-status.md`
   - Priority files (governance/skills):
     - `.github/skills/adr-docs/SKILL.md`
     - `.github/skills/adr-manager/SKILL.md`
     - `src/opsdev/lib/adr.py`
     - `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE.md`

### Near-term (Version Alignment)

1. Update GovZero Version References
   - Files:
     - `docs/governance/gate5_documentation_obligation.md` — add v6 note
     - `docs/governance/pep257_manpage_adoption.md` — update references section
     - `docs/governance/gzkit/RFC-GZKIT-FOUNDATION.md` — add v6 alignment note
   - Change: Acknowledge GovZero v6 (effective 2026-01-05) or add clarifying notes

### Deferred (Nice-to-Have)

1. Archive Historical Documents (requires human decision)
   - `docs/governance/CLAUDE-CODE-EVALUATION-BRIEF.md` — consider moving to `_archive/`
   - `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE-CODEX-FEEDBACK.md` — consider moving to `_archive/`

2. Create `_archive/` Directory
   - If archiving is approved, create `docs/governance/_archive/` with README explaining archive policy

---

## Section 4: Open Questions

1. Should historical evaluation/feedback documents be archived?
   - `CLAUDE-CODE-EVALUATION-BRIEF.md` and agent feedback docs are non-normative
   - Options: keep in place (low maintenance), archive (cleaner tree), delete (loses history)

2. How should stale path references in proof/log files be handled?
   - Many stale references are in audit proof files (historical artifacts)
   - Options: update all (consistent), update only active files (pragmatic), leave proofs as historical snapshots

3. Should the gzkit RFC be updated now or when gzkit is activated?
   - RFC is currently dormant (draft status)
   - Options: update now (proactive), defer until RFC is activated (just-in-time)

---

## Appendix: Stale Reference Locations

Files referencing old `docs/design/adr/adr_status.md` path (35 total):

**Active/Normative (priority update):**
- `.github/skills/adr-docs/SKILL.md`
- `.github/skills/adr-manager/SKILL.md`
- `src/opsdev/lib/adr.py`
- `src/opsdev/commands/tasks.py`
- `docs/governance/GOVZERO-GATE-3-5-AUDIT-FORM-ISSUE.md`
- `ARCHITECTURE.md`
- `docs/user/index.md`

**Historical/Proof Files (lower priority):**
- `docs/design/audit/` subdirectories (various proof files)
- `docs/design/adr/adr-0.1.x/*/audit/proofs/` files
- `docs/design/briefs/` subdirectories (historical logs)

---

**Audit Status:** Complete
**Next Step:** Human review and approval of recommended actions
