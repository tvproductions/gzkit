---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. Use when the user says "ADR closeout ceremony", all OBPIs are complete and ready for human attestation, or performing the final ADR sign-off.
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "6.2.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 — Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-31
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

### Step 3: Present Value Justification

Present a concise value narrative demonstrating the ADR's achieved purpose. This step is
**required for all closeouts** — generic housekeeping commands (unittest, ruff) do not
demonstrate ADR value.

**Structure:**

1. **State the problem** — What gap or friction existed before this ADR? (2-3 sentences)
2. **Before/after summary** — For each OBPI, show what changed and why it matters. Use a
   table with OBPI, Before, and After columns.
3. **Name the concrete capability** — What can operators/agents do now that they couldn't
   before? (1-2 sentences)

**For foundation/governance ADRs** where Steps 5-6 (docs alignment, runbook walkthrough)
may not apply, this step carries the primary burden of demonstrating value to the attestor.

### Step 4: Confirm Docs Alignment (Human-Driven)

Use the checklist in the fixed script. Do not assert outcomes.

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

**If human is in IDE (e.g., VS Code with Copilot):**

- Present the commands for human to run themselves
- Wait for human to report results

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

### Step 6: Execute Walkthrough (One at a Time)

For each command:

1. Show the command
2. Run it (if human requested) or wait for human to run it
3. Show output
4. STOP and WAIT for acknowledgment
5. Only then proceed to next command

### Step 7: Config Drift Check

Before requesting attestation, run the config drift audit to ensure no schema/config
drift exists:

```bash
uv run gz check-config-paths
```

**Behavior:**

- **No drift detected:** Check passes silently — proceed to attestation
- **Drift detected:** Ceremony **BLOCKED**. Present the drift findings and instruct the
  human to resolve drift before attestation can continue. Do not proceed to attestation
  until the check passes clean

### Step 8: Request Attestation

After all commands have been executed and witnessed:

```text
Runbook walkthrough complete.

When you are ready, provide your attestation:
- "Completed" — ADR work is finished; all claims verified; ready to finalize
- "Completed — Partial: [reason]" — Subset accepted, remainder deferred
- "Dropped — [reason]" — ADR rejected; does not advance

I await your attestation.
```

### Step 9: Record Attestation via Closeout Pipeline

After the human provides their attestation decision in Step 8, run the closeout command:

```bash
uv run gz closeout ADR-X.Y.Z
```

This command handles the full closeout pipeline:

1. Re-validates quality gates (fast final check)
2. Prompts for formal attestation (enter the same decision from Step 8)
3. **Bumps project version** in pyproject.toml, `__init__.py`, and README badge
4. Writes the ADR closeout form with attestation details
5. Transitions ADR status to Completed/Dropped

**CRITICAL:** Do not skip `gz closeout` or manually record attestation — the closeout
command is the only code path that syncs the project version. Skipping it causes version
drift between pyproject.toml and the release tag, which breaks PyPI publishing.

### Step 10: Ledger Receipt & Registry Reconciliation

The validation ledger is the **single source of truth** for ADR audit state. All registries
are derived projections. This step writes the authoritative receipt and cascades the validated
status through all governance surfaces.

**1. Write validation receipt to ledger:**

Append a `validated` event to the ADR's `logs/adr-validation.jsonl`:

```json
{
  "adr_id": "X.Y.Z",
  "event": "validated",
  "timestamp": "<ISO 8601>",
  "attestor": "human:<name>",
  "anchor": {
    "commit": "<HEAD commit hash>",
    "tag": "vX.Y.Z",
    "semver": "X.Y.Z"
  },
  "evidence": {
    "briefs_completed": "<count>",
    "gate": "Gate 5",
    "attestation": "<verbatim from Step 9>"
  }
}
```

**2. Cascade status through derived registries (Layer 3):**

```bash
uv run gz adr status
```

Then verify ADR status surfaces show the ADR as Validated with the correct audit date.

**3. Verify consistency:**

All status surfaces MUST show the ADR as `Validated` or `Completed` with the correct date.
Any drift between surfaces is a ceremony defect — fix before proceeding.

**Why this matters:** Without this step, attestation exists only in the closeout form (a markdown
artifact). The ledger receipt makes it machine-readable, temporally anchored to a specific commit,
and queryable by governance tooling.

### Step 11: Close Related GitHub Issues

After attestation is recorded:

1. Search for GitHub Issues related to the ADR (use `gh issue list`)
2. Review each related issue to confirm it is addressed by the ADR work
3. Close issues that are resolved, with a comment linking to the ADR closeout

```bash
# Search for related issues
gh issue list --search "ADR-X.Y.Z" --state open
gh issue list --search "storage" --state open  # or relevant keywords

# Close resolved issues
gh issue close <issue-number> --comment "Resolved by ADR-X.Y.Z closeout."
```

### Step 12: Update Version Surfaces and RELEASE_NOTES.md

Bump all version surfaces to match the ADR's SemVer, then append the release entry.

**Version surfaces (both required):**

```bash
# 1. pyproject.toml — canonical package version
#    Update: version = "X.Y.Z"

# 2. README.md — version badge
#    Update: version-X.Y.Z in the badge URL
```

**RELEASE_NOTES.md — append release entry:**

```markdown
## vX.Y.Z (YYYY-MM-DD)

**ADR:** ADR-X.Y.Z - [Title]

[Brief description of capability added]

### Delivered
- [Key deliverables]

### Gate Evidence
All 5 GovZero gates satisfied.
```

### Step 13: Git Sync (Pre-Release)

Commit and push all closeout artifacts (version bump, release notes, closeout form, ADR status
updates) so the release tag lands on the correct, fully-finalized commit.

```bash
uv run gz git-sync --apply --lint --test
```

**Why this is required:** `gh release create` tags `HEAD` on the remote. If version bump and
release notes changes are uncommitted or unpushed, the release tag points to a commit that
doesn't include its own version number — a governance integrity violation. Git-sync also runs
the full pre-commit suite (lint, ty, tests), providing a final validation gate before the
release is cut.

**Behavior:**

- **Clean sync:** Proceed to release creation
- **Sync failure:** Ceremony **BLOCKED** until the sync issue is resolved (e.g., merge
  conflicts, failing tests). Do not create a release with dirty or unpushed state.

### Step 14: Create GitHub Release

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

### Step 15: Present Ceremony Summary

Display the ceremony completion table:

```text
╔══════════════════════════════════════════════════════════════════╗
║   ADR-X.Y.Z CLOSEOUT CEREMONY — COMPLETE                         ║
╠══════════════════════════════════════════════════════════════════╣
║   Step 1: Trigger recognized                              ✓      ║
║   Step 2: Paths/commands summary presented                ✓      ║
║   Step 3: Value justification presented                   ✓      ║
║   Step 4: Docs alignment verified                         ✓      ║
║   Step 5: Runbook walkthrough presented                   ✓      ║
║   Step 6: Commands executed (one at a time)               ✓      ║
║   Step 7: Config drift check passed                       ✓      ║
║   Step 8: Attestation requested                           ✓      ║
║   Step 9: Closeout pipeline (attest + version bump)       ✓      ║
║   Step 10: Ledger receipt written & registries synced     ✓      ║
║   Step 11: GitHub Issues reviewed                         ✓      ║
║   Step 12: Version surfaces + RELEASE_NOTES.md updated     ✓      ║
║   Step 13: Git sync (pre-release)                         ✓      ║
║   Step 14: GitHub Release vX.Y.Z created                  ✓      ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## MUST Rules

1. **MUST** use the fixed script from `docs/governance/GovZero/audit-protocol.md`
2. **MUST** lead with a paths/commands-only summary (no outcomes or conclusions)
3. **MUST** present a value justification (problem statement, before/after summary per OBPI, capability gained) before proceeding to walkthrough
4. **MUST** use only runbook/manpage-documented gzkit commands for the walkthrough
5. **MUST** run one command at a time, wait for acknowledgment
6. **MUST** offer to run commands if human is in CLI mode
7. **MUST** run config drift check before requesting attestation; drift blocks the ceremony
8. **MUST** wait for explicit human attestation before closing
9. **MUST** run `uv run gz closeout ADR-X.Y.Z` to record attestation and bump project version — never manually record attestation
10. **MUST** write validation receipt to ledger and cascade status through all derived registries; the ledger is authority — registries are projections
11. **MUST** review and close related GitHub Issues after attestation
12. **MUST** bump version in `pyproject.toml` and README.md badge, then update RELEASE_NOTES.md with release entry
13. **MUST** run `uv run gz git-sync --apply --lint --test` before creating a release; dirty/unpushed state blocks the ceremony
14. **MUST** create GitHub release with title = semver only (vX.Y.Z)
15. **MUST** display ceremony completion summary table

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
