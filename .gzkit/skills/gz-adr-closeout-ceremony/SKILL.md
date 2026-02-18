---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 — Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony, guiding the human through a runbook walkthrough to demonstrate ADR value.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## Trust Model

**Layer 2 — Ledger Consumption:** This tool orchestrates human attestation using ledger proof.

- **Reads:** Ledger entries, audit reports, ADR/OBPI files
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

### Step 2: Present Paths/Commands-Only Summary

Lead with a summary derived **only** from the paths and commands you present. Do not interpret or
claim outcomes. Use the fixed script from `docs/governance/GovZero/audit-protocol.md`:

```text
ADR CLOSEOUT CEREMONY — MODE TRANSITION

I am now in PASSIVE PRESENTER mode. I will not interpret evidence.

Summary (paths/commands only; no outcomes):
- ADR under review: [ADR path]
- Related briefs: [OBPI paths]
- Runbook/manpage paths (for walkthrough commands): [paths]
- Evidence commands listed below

Artifacts for your direct observation:
- Tests: Run `uv run -m unittest -v`
- Coverage: Run `uv run coverage report` or view `artifacts/reports/coverage.html`
- Docs build: Run `uv run mkdocs build -q`
- BDD (if Heavy): Run `uv run behave features/{feature}.feature`
- Runbook walkthrough (product commands from runbook/manpages): [commands]

Docs alignment check (human-confirmed):
- [ ] Manpage exists and reflects current CLI behavior
- [ ] Runbook includes relevant commands
- [ ] Dataset documentation updated if applicable
- [ ] CLI --help matches manpage SYNOPSIS

When you have observed the artifacts, provide your attestation:
- "Completed"
- "Completed — Partial: [reason]"
- "Dropped — [reason]"

I await your attestation.
```

### Step 3: Confirm Docs Alignment (Human-Driven)

Use the checklist in the fixed script. Do not assert outcomes.

### Step 4: Runbook Walkthrough

The ceremony is a **runbook walkthrough** demonstrating the ADR's achieved value. Outside of
foundation/0.0.x ADRs, observable behavior is required.

**Rules:**

- Run ONLY airlineops CLI commands from the runbook/manpage
- NO ad-hoc Python, NO raw SQL, NO heredoc scripts
- One command at a time
- Wait for human acknowledgment before proceeding to next command

**If human is in CLI mode (e.g., Claude Code):**

- Offer to run the commands and show output
- Run ONE command, show output, STOP and WAIT for acknowledgment
- Only proceed to next command after acknowledgment

**If human is in IDE (e.g., VS Code with Copilot):**

- Present the commands for human to run themselves
- Wait for human to report results

Present the walkthrough:

```text
Runbook Walkthrough — Demonstrating ADR Value

The following commands from the runbook demonstrate the ADR's achieved value.
These are product surface commands (airlineops CLI), not ad-hoc scripts.

Commands to execute:
1. [command 1 from runbook]
2. [command 2 from runbook]
...

Would you like me to run these one at a time, or will you run them yourself?
```

### Step 5: Execute Walkthrough (One at a Time)

For each command:

1. Show the command
2. Run it (if human requested) or wait for human to run it
3. Show output
4. STOP and WAIT for acknowledgment
5. Only then proceed to next command

### Step 6: Request Attestation

After all commands have been executed and witnessed:

```text
Runbook walkthrough complete.

When you are ready, provide your attestation:
- "Completed" — ADR work is finished; all claims verified; ready to finalize
- "Completed — Partial: [reason]" — Subset accepted, remainder deferred
- "Dropped — [reason]" — ADR rejected; does not advance

I await your attestation.
```

### Step 7: Record Attestation

After receiving attestation:

1. Record the attestation verbatim with timestamp in the closeout form
2. Update ADR status if "Completed"
3. Commit the closeout form

### Step 8: Close Related GitHub Issues

After attestation is recorded:

1. Search for GitHub Issues related to the ADR (use `gh issue list`)
2. Review each related issue to confirm it is addressed by the ADR work
3. Close issues that are resolved, with a comment linking to the ADR closeout

```bash
# Search for related issues
gh issue list --search "ADR-X.Y.Z" --state open
gh issue list --search "mirror" --state open  # or relevant keywords

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

**Why this matters:** The release tags the commit as a governance milestone. The human attestation (Gate 5) is the authority that allows this release to exist.

### Step 11: Present Ceremony Summary

Display the ceremony completion table:

```text
╔══════════════════════════════════════════════════════════════════╗
║   ADR-X.Y.Z CLOSEOUT CEREMONY — COMPLETE                         ║
╠══════════════════════════════════════════════════════════════════╣
║   Step 1: Trigger recognized                              ✓      ║
║   Step 2: Paths/commands summary presented                ✓      ║
║   Step 3: Docs alignment verified                         ✓      ║
║   Step 4: Runbook walkthrough presented                   ✓      ║
║   Step 5: Commands executed (one at a time)               ✓      ║
║   Step 6: Attestation requested                           ✓      ║
║   Step 7: Attestation recorded                            ✓      ║
║   Step 8: GitHub Issues reviewed                          ✓      ║
║   Step 9: RELEASE_NOTES.md updated                        ✓      ║
║   Step 10: GitHub Release vX.Y.Z created                  ✓      ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## MUST Rules

1. **MUST** use the fixed script from `docs/governance/GovZero/audit-protocol.md`
2. **MUST** lead with a paths/commands-only summary (no outcomes or conclusions)
3. **MUST** use only runbook/manpage-documented airlineops commands for the walkthrough
4. **MUST** run one command at a time, wait for acknowledgment
5. **MUST** offer to run commands if human is in CLI mode
6. **MUST** wait for explicit human attestation before closing
7. **MUST** record attestation verbatim with timestamp
8. **MUST** review and close related GitHub Issues after attestation
9. **MUST** update RELEASE_NOTES.md with release entry
10. **MUST** create GitHub release with title = semver only (vX.Y.Z)
11. **MUST** display ceremony completion summary table

---

## MUST NOT Rules

1. **MUST NOT** claim outcomes or interpret evidence
2. **MUST NOT** use ad-hoc Python scripts, raw SQL, or heredoc code
3. **MUST NOT** flood multiple commands without waiting for acknowledgment
4. **MUST NOT** infer attestation from silence or implicit approval
5. **MUST NOT** auto-close an ADR based on passing checks
6. **MUST NOT** skip the evidence commands or docs alignment checklist

---

## ADR Folder Structure (Canonical)

New ADRs should use the ADR-contained layout:

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md             # Intent document
  ADR-CLOSEOUT-FORM.md            # Closeout ceremony workspace
  briefs/
    OBPI-X.Y.Z-01-*.md            # Atomic implementation units
    OBPI-X.Y.Z-02-*.md
  audit/
    AUDIT-ADR-X.Y.Z-COMPLETED.md  # Post-attestation reconciliation
  logs/
    design-outcomes.jsonl         # Optional agent-facing working memory
```

---

## Example: ADR-0.1.13 Closeout

```text
ADR CLOSEOUT CEREMONY — MODE TRANSITION

I am now in PASSIVE PRESENTER mode. I will not interpret evidence.

Summary (paths/commands only; no outcomes):
- ADR under review: docs/design/adr/adr-0.1.x/ADR-0.1.13-mirror-parquet-lake-analytical-reads/ADR-0.1.13-mirror-parquet-lake-analytical-reads.md
- Related briefs: docs/design/adr/adr-0.1.x/ADR-0.1.13-mirror-parquet-lake-analytical-reads/briefs/OBPI-0.1.13-*.md
- Runbook/manpage paths (for walkthrough commands): docs/user/manpages/warehouse-mirror.md
- Evidence commands listed below

Artifacts for your direct observation:
- Tests: Run `uv run -m unittest -v`
- Coverage: Run `uv run coverage report` or view `artifacts/reports/coverage.html`
- Docs build: Run `uv run mkdocs build -q`
- BDD (if Heavy): Run `uv run behave features/mirror.feature`
- Runbook walkthrough (product commands from runbook/manpages): `uv run -m airlineops warehouse mirror sync --all`, `uv run -m airlineops warehouse mirror status`

Docs alignment check (human-confirmed):
- [ ] Manpage exists and reflects current CLI behavior
- [ ] Runbook includes relevant commands
- [ ] Dataset documentation updated if applicable
- [ ] CLI --help matches manpage SYNOPSIS

When you have observed the artifacts, provide your attestation:
- "Completed"
- "Completed — Partial: [reason]"
- "Dropped — [reason]"

I await your attestation.
```

---

## References

- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
- Gate definitions: `docs/governance/GovZero/charter.md`
- Artifact linkage: `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
- Runbook: `docs/user/operator_runbook.md`
- Manpage directory: `docs/user/manpages/`
