---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "7.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-05
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony by driving the CLI state machine.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## Trust Model

**Layer 2 — Ledger Consumption:** This tool orchestrates human attestation using ledger proof.

- **Reads:** Ledger entries, audit reports, ADR/OBPI files
- **Writes:** Attestation records, status updates via CLI commands
- **Does NOT re-verify:** Evidence (trusts Layer 1 proof)
- **Requires:** Human attestation before finalizing

---

## When to Use

- Human invokes "ADR closeout ceremony" (or equivalent: "begin closeout", "closeout ADR-X.Y.Z")
- Human is ready to witness and attest to ADR completion
- All OBPIs are believed to be complete

---

## Architecture

The ceremony is driven by `src/gzkit/commands/closeout_ceremony.py`, which provides:

- **Step sequencing** — deterministic step ordering via `CeremonyStep` enum
- **Foundation skip** — `FOUNDATION_SKIP_STEPS` automatically skips RELEASE_NOTES and RELEASE steps for 0.0.x ADRs
- **State persistence** — ceremony state saved in `.gzkit/ceremonies/`
- **Walkthrough discovery** — commands extracted from OBPI briefs and command docs
- **Turn locks** — prevents step skipping

**The agent MUST drive the ceremony through CLI commands, not by reimplementing
step logic in prose.** The CLI handles all conditional logic (Foundation skips,
lane-specific steps, step ordering). The agent's role is to:

1. Run the CLI command for each step
2. Present the output to the human
3. Wait for human acknowledgment
4. Advance via CLI

---

## Procedure

### Step 1: Recognize Trigger and Initialize

When the human says "ADR closeout ceremony" (or equivalent), start the ceremony:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony
```

This initializes the ceremony state machine and outputs the Step 2 summary.
Present the output to the human. Do not interpret or claim outcomes.

### Step 2: Advance Through Steps

After the human acknowledges each step, advance:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --next
```

The CLI outputs the content for the next step. Present it and wait for acknowledgment.

**Repeat this cycle for each step.** The CLI handles:

- Which step comes next
- Skipping Foundation-excluded steps (RELEASE_NOTES, RELEASE for 0.0.x)
- What content to present at each step

### Step 3: Walkthrough Execution

When the CLI presents walkthrough commands (Steps 3-4), run them one at a time:

- Run ONE command, show output, STOP and WAIT for acknowledgment
- Only proceed to next command after acknowledgment
- After all walkthrough commands are done, advance via `--next`

### Step 4: Attestation

When the CLI presents the attestation prompt (Step 5), wait for the human's decision.
Record it:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --attest "Completed"
```

Valid attestations:
- `"Completed"` — ADR work is finished; all claims verified
- `"Completed - Partial: [reason]"` — Subset accepted, remainder deferred
- `"Dropped - [reason]"` — ADR rejected; does not advance

### Step 5: Closeout Pipeline

When the CLI presents Step 6, run the closeout pipeline:

```bash
uv run gz closeout ADR-X.Y.Z
```

This handles quality gates, attestation recording, version bump, and closeout form.
After it completes, advance the ceremony:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --next
```

### Step 6: GitHub Issues

When the CLI presents Step 7, close related issues:

```bash
gh issue list --search "ADR-X.Y.Z" --state open
gh issue close <number> --comment "Resolved by ADR-X.Y.Z closeout."
```

Then advance via `--next`.

### Step 7: Release Steps (CLI-Driven)

The CLI automatically handles Foundation vs non-Foundation:

- **Foundation (0.0.x):** Steps 8-9 are skipped automatically by `FOUNDATION_SKIP_STEPS`
- **Non-Foundation:** The CLI presents RELEASE_NOTES and GitHub Release steps

For non-Foundation releases:

```bash
# Step 8: Update RELEASE_NOTES.md (agent edits the file)
# Step 9: Create GitHub release
uv run gz git-sync --apply --lint --test
gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."
```

After each step, advance via `--next`.

### Step 8: Completion

When the CLI outputs the ceremony completion summary, present it to the human.
The ceremony is done.

---

## CLI Reference

| Command | Purpose |
|---------|---------|
| `gz closeout ADR-X.Y.Z --ceremony` | Initialize or resume ceremony |
| `gz closeout ADR-X.Y.Z --ceremony --next` | Advance to next step |
| `gz closeout ADR-X.Y.Z --ceremony --attest "..."` | Record attestation at Step 5 |
| `gz closeout ADR-X.Y.Z --ceremony --ceremony-status` | Show current step |
| `gz closeout ADR-X.Y.Z` | Run closeout pipeline (Step 6) |

---

## MUST Rules

1. **MUST** drive the ceremony through CLI commands (`--ceremony`, `--next`, `--attest`) — never reimplement step logic in prose
2. **MUST** present CLI output to the human without interpreting or claiming outcomes
3. **MUST** use only runbook/manpage-documented gzkit commands for the walkthrough
4. **MUST** run walkthrough commands one at a time, wait for acknowledgment
5. **MUST** offer to run commands if human is in CLI mode
6. **MUST** wait for explicit human attestation before closing
7. **MUST** run `uv run gz closeout ADR-X.Y.Z` for the closeout pipeline — never manually record attestation
8. **MUST** review and close related GitHub Issues after attestation
9. **MUST** run `uv run gz git-sync --apply --lint --test` immediately before `gh release create` (non-Foundation only)

---

## MUST NOT Rules

1. **MUST NOT** manually reimplement ceremony step logic — the CLI state machine is authoritative
2. **MUST NOT** manually skip or add steps — the CLI handles Foundation skips and step ordering
3. **MUST NOT** claim outcomes or interpret evidence
4. **MUST NOT** use ad-hoc Python scripts, raw SQL, or heredoc code
5. **MUST NOT** flood multiple commands without waiting for acknowledgment
6. **MUST NOT** infer attestation from silence or implicit approval
7. **MUST NOT** auto-close an ADR based on passing checks

---

## ADR Folder Structure (Canonical)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md             # Intent document
  ADR-CLOSEOUT-FORM.md            # Closeout ceremony workspace
  briefs/
    OBPI-X.Y.Z-01-*.md            # Atomic implementation units
  audit/
    AUDIT-ADR-X.Y.Z-COMPLETED.md  # Post-attestation reconciliation
```

---

## References

- Ceremony code: `src/gzkit/commands/closeout_ceremony.py`
- Step renderers: `src/gzkit/commands/ceremony_steps.py`
- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
- Gate definitions: `docs/governance/GovZero/charter.md`
- Release tag rule: `docs/governance/GovZero/adr-lifecycle.md`
- Runbook: `docs/user/operator_runbook.md`
