---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "6.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-28
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony as a **defense presentation** where the completing agent makes its case and the human judges it.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## Trust Model

**Layer 2 — Ledger Consumption:** This tool orchestrates human attestation using ledger proof.

- **Reads:** Ledger entries, audit reports, ADR/OBPI files, REVIEW-*.md artifacts
- **Writes:** Attestation records, status updates
- **Does NOT re-verify:** Evidence (trusts Layer 1 proof)
- **Requires:** Human attestation before finalizing

---

## When to Use

- Human invokes "ADR closeout ceremony" (or equivalent: "begin closeout", "closeout ADR-X.Y.Z")
- Human is ready to witness and attest to ADR completion
- All OBPIs are believed to be complete

---

## Quality Control Context

Pre-commit enforcement exists, but closeout **requires direct human observation** of evidence.
Do not claim results; present paths and commands only.

---

## Procedure

### Step 1: Recognize Trigger

When the human says "ADR closeout ceremony" (or equivalent), begin the ceremony protocol.

### Step 2: Pre-Flight — Ceremony Readiness Check

Before presenting the ceremony, verify that all evidence prerequisites are met. **Block the ceremony** (do not proceed to attestation) if ANY of the following are true:

| Condition | Check Method | Block? |
|-----------|-------------|--------|
| Any OBPI missing Closing Argument | Read each brief, check for `## Closing Argument` section with substantive content | **YES** |
| Any OBPI missing product proof | Run `uv run gz closeout ADR-X.Y.Z --dry-run` and check for MISSING entries | **YES** |
| No reviewer assessment available | Check for `REVIEW-*.md` files in the ADR package's briefs/ or obpis/ directory | Heavy: **YES**, Lite: **WARN** |

If blocked, report which OBPIs have missing evidence and stop. Do not proceed to the defense presentation.

```text
CEREMONY BLOCKED — Missing Evidence

The following OBPIs cannot proceed to attestation:

| OBPI | Issue |
|------|-------|
| OBPI-X.Y.Z-01 | Missing closing argument |
| OBPI-X.Y.Z-03 | No reviewer assessment |

Resolve these before re-invoking the ceremony.
```

### Step 3: Present Defense Brief

Once readiness is confirmed, present the **Defense Brief** — the agent's case for closure. This replaces the old checklist-only ceremony. The defense brief has three parts:

#### Part 1: Closing Arguments (per OBPI)

Present each OBPI's Closing Argument section in sequence. Each closing argument should articulate:
- **What was built** (artifact paths)
- **What it enables** (operator capability)
- **Why it matters** (proof command or documentation link)

```text
DEFENSE BRIEF — ADR-X.Y.Z

═══════════════════════════════════════════════════════
CLOSING ARGUMENTS
═══════════════════════════════════════════════════════

OBPI-X.Y.Z-01 — [Title]
────────────────────────
[Closing argument text from the brief]

OBPI-X.Y.Z-02 — [Title]
────────────────────────
[Closing argument text from the brief]
```

#### Part 2: Product Proof Status

Display the product proof table from `uv run gz closeout ADR-X.Y.Z --dry-run`:

```text
═══════════════════════════════════════════════════════
PRODUCT PROOF
═══════════════════════════════════════════════════════

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-X.Y.Z-01 | docstring | FOUND |
| OBPI-X.Y.Z-02 | command_doc | FOUND |
| OBPI-X.Y.Z-03 | runbook | FOUND |
```

#### Part 3: Reviewer Assessment

Present the reviewer agent's independent assessment for each OBPI:

```text
═══════════════════════════════════════════════════════
REVIEWER ASSESSMENT
═══════════════════════════════════════════════════════

| OBPI | Verdict | Promises Met | Docs Quality | Closing Arg |
|------|---------|-------------|-------------|-------------|
| OBPI-X.Y.Z-01 | PASS | 4/4 | substantive | earned |
| OBPI-X.Y.Z-02 | CONCERNS | 3/4 | substantive | earned |

[For any CONCERNS or FAIL verdict, present the reviewer's summary]
```

Read the full assessment from the `REVIEW-*.md` artifacts in the ADR package.

### Step 4: Present Evidence Commands

After the defense brief, present the verification commands:

```text
═══════════════════════════════════════════════════════
VERIFICATION EVIDENCE
═══════════════════════════════════════════════════════

Artifacts for your direct observation:
- Tests: Run `uv run -m unittest -v`
- Coverage: Run `uv run coverage report` or view `artifacts/reports/coverage.html`
- Docs build: Run `uv run mkdocs build -q`
- BDD (if Heavy): Run `uv run behave features/{feature}.feature`

Docs alignment check (human-confirmed):
- [ ] Manpage exists and reflects current CLI behavior
- [ ] Runbook includes relevant commands
- [ ] CLI --help matches manpage SYNOPSIS
```

### Step 5: Runbook Walkthrough

The ceremony is a **runbook walkthrough** demonstrating the ADR's achieved value. Outside of
foundation/0.0.x ADRs, observable behavior is required.

**Rules:**

- Run ONLY gzkit CLI commands from the runbook/manpage
- NO ad-hoc Python, NO raw SQL, NO heredoc scripts
- One command at a time
- Wait for human acknowledgment before proceeding to next command

**If human is in CLI mode (e.g., Claude Code):**

- Offer to run the commands and show output
- Run ONE command, show output, STOP and WAIT for acknowledgment
- Only proceed to next command after acknowledgment

Present the walkthrough:

```text
Runbook Walkthrough — Demonstrating ADR Value

The following commands from the runbook demonstrate the ADR's achieved value.
These are product surface commands (gzkit CLI), not ad-hoc scripts.

Commands to execute:
1. [command 1 from runbook]
2. [command 2 from runbook]
...

Would you like me to run these one at a time, or will you run them yourself?
```

### Step 6: Request Attestation

After the defense brief is presented and commands have been witnessed:

```text
═══════════════════════════════════════════════════════
ATTESTATION REQUEST
═══════════════════════════════════════════════════════

The defense brief has been presented. All closing arguments, product proof,
and reviewer assessments are above.

When you are ready, provide your attestation:
- "Completed" — ADR work is finished; all claims verified; ready to finalize
- "Completed — Partial: [reason]" — Subset accepted, remainder deferred
- "Dropped — [reason]" — ADR rejected; does not advance

I await your attestation.
```

### Step 7: Record Attestation via Closeout Pipeline

After the human provides their attestation decision in Step 6, run the closeout command:

```bash
uv run gz closeout ADR-X.Y.Z
```

This command handles the full closeout pipeline:

1. Re-validates quality gates (fast final check)
2. Prompts for formal attestation (enter the same decision from Step 6)
3. **Bumps project version** in pyproject.toml, `__init__.py`, and README badge
4. Writes the ADR closeout form with attestation details and Defense Brief
5. Transitions ADR status to Completed/Dropped

**CRITICAL:** Do not skip `gz closeout` or manually record attestation — the closeout
command is the only code path that syncs the project version. Skipping it causes version
drift between pyproject.toml and the release tag, which breaks PyPI publishing.

### Step 8: Close Related GitHub Issues

After attestation is recorded:

1. Search for GitHub Issues related to the ADR (use `gh issue list`)
2. Review each related issue to confirm it is addressed by the ADR work
3. Close issues that are resolved, with a comment linking to the ADR closeout

```bash
# Search for related issues
gh issue list --search "ADR-X.Y.Z" --state open

# Close resolved issues
gh issue close <issue-number> --comment "Resolved by ADR-X.Y.Z closeout."
```

### Step 9: Update RELEASE_NOTES.md

Append the release entry to `RELEASE_NOTES.md`:

```markdown
## vX.Y.Z (YYYY-MM-DD)

**ADR:** ADR-X.Y.Z - [Title]

[Brief description of capability added]

### Delivered
- [Key deliverables]

### Gate Evidence
All 5 GovZero gates satisfied.
```

### Step 10: Create GitHub Release

Create a GitHub release for the ADR version:

```bash
# MANDATORY: run full git sync immediately before release creation
uv run gz git-sync --apply --lint --test

# Create release (title = semver only)
gh release create vX.Y.Z --title "vX.Y.Z" --notes "$(cat <<'EOF'
## What's New

[Brief description of capability added]

## ADR Reference

- **ADR:** ADR-X.Y.Z - [Title]
- **Status:** Completed
- **Attestation:** [Date]

## Delivered

- [List key deliverables]

## Gate Evidence

All 5 GovZero gates satisfied. See ADR closeout form for details.
EOF
)"
```

**Policy constraint:** `uv run gz git-sync --apply --lint --test` MUST be the command immediately preceding `gh release create`.

### Step 11: Present Ceremony Summary

Display the ceremony completion table:

```text
ADR-X.Y.Z CLOSEOUT CEREMONY — COMPLETE

  Step 1:  Trigger recognized                            [done]
  Step 2:  Ceremony readiness verified                   [done]
  Step 3:  Defense Brief presented                       [done]
  Step 4:  Evidence commands presented                   [done]
  Step 5:  Runbook walkthrough executed                  [done]
  Step 6:  Attestation requested                         [done]
  Step 7:  Closeout pipeline (attest + version bump)     [done]
  Step 8:  GitHub Issues reviewed                        [done]
  Step 9:  RELEASE_NOTES.md updated                      [done]
  Step 10: GitHub Release vX.Y.Z created                 [done]
```

---

## MUST Rules

1. **MUST** verify ceremony readiness (Step 2) before presenting the defense brief
2. **MUST** block the ceremony if ANY OBPI is missing a closing argument
3. **MUST** block the ceremony if ANY OBPI is missing product proof
4. **MUST** block the ceremony for Heavy-lane ADRs if no reviewer assessment exists
5. **MUST** present closing arguments in sequence, not as a checklist
6. **MUST** display the product proof status table with per-OBPI proof type
7. **MUST** present the reviewer agent's structured assessment (promises-met, docs-quality, closing-argument-quality)
8. **MUST** use only runbook/manpage-documented gzkit commands for the walkthrough
9. **MUST** run one command at a time, wait for acknowledgment
10. **MUST** wait for explicit human attestation before closing
11. **MUST** run `uv run gz closeout ADR-X.Y.Z` to record attestation and bump project version
12. **MUST** run `uv run gz git-sync --apply --lint --test` immediately before any `gh release create`

---

## MUST NOT Rules

1. **MUST NOT** claim outcomes or interpret evidence
2. **MUST NOT** proceed to attestation when evidence is missing (blocking conditions in Step 2)
3. **MUST NOT** present a checklist without the closing arguments (the defense brief IS the ceremony)
4. **MUST NOT** use ad-hoc Python scripts, raw SQL, or heredoc code
5. **MUST NOT** flood multiple commands without waiting for acknowledgment
6. **MUST NOT** infer attestation from silence or implicit approval
7. **MUST NOT** auto-close an ADR based on passing checks

---

## Lite-Lane Applicability

For Lite-lane-only ADRs, the ceremony still requires closing arguments and product proof, but:

- Reviewer assessment is **advisory** (warning if absent, not blocking)
- Gate 5 human attestation may still be required if the parent ADR is Heavy

---

## ADR Folder Structure (Canonical)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md             # Intent document
  ADR-CLOSEOUT-FORM.md            # Closeout ceremony workspace (includes Defense Brief)
  obpis/
    OBPI-X.Y.Z-01-*.md            # Atomic implementation units
    OBPI-X.Y.Z-02-*.md
    REVIEW-OBPI-X.Y.Z-01-*.md     # Reviewer assessment artifacts
  audit/
    AUDIT-ADR-X.Y.Z-COMPLETED.md  # Post-attestation reconciliation
  logs/
    design-outcomes.jsonl         # Optional agent-facing working memory
```

---

## References

- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
- Gate definitions: `docs/governance/GovZero/charter.md`
- Artifact linkage: `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
- Runbook: `docs/user/runbook.md`
- Manpage directory: `docs/user/manpages/`
- Defense Brief rendering: `src/gzkit/commands/common.py` (ceremony enforcement helpers)
