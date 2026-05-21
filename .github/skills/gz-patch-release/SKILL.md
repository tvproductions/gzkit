---
name: gz-patch-release
persona: main-session
description: "Orchestrate the GHI-driven patch release ceremony: draft narrative release notes, operator approval, RELEASE_NOTES update, git-sync, and GitHub release."
category: adr-audit
compatibility: GovZero v6 framework; provides ceremony walkthrough for GHI-driven patch releases
metadata:
  skill-version: "1.5.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/releases/patch-release.md, docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-21
model: sonnet
---

# gz-patch-release

Orchestrate the GHI-driven patch release ceremony by drafting narrative release
notes, presenting them to the operator for approval, and executing the release
pipeline.

**Authority:** `docs/governance/GovZero/releases/patch-release.md`

---

## Trust Model

**Layer 2 — Ledger Consumption:** This skill orchestrates operator attestation
using GHI evidence and CLI outputs.

- **Reads:** GHI discovery output, cross-validation results, RELEASE_NOTES.md
- **Writes:** Narrative release notes, RELEASE_NOTES.md entry, GitHub release
- **Does NOT re-verify:** GHI qualification (trusts `gz patch release` CLI)
- **Requires:** Operator approval before any publish action

---

## When to Use

- Operator says "patch release", "do a patch release", or equivalent
- **Either qualifier holds:**
  - **Behavior-level GHIs** closed since last tag with runtime label + src diff
    (auto-discovered by `gz patch release --dry-run`)
  - **Foundation-ADR closeouts** — a foundation ADR (`0.0.x`) reached
    `Validated` status with all OBPIs `Validated` and a Gate-5 `validated`
    receipt in the ledger since the last tag (auto-discovered by
    `gz patch release --dry-run`)
- The operator wants to cut a patch version bump driven by either qualifier

## When NOT to Use

- For minor or major releases — use `gz closeout` ceremony instead
- When neither qualifier holds — no closed GHIs **and no foundation
  closeouts** surface in `gz patch release --dry-run` since the last tag
- When the operator wants to manually edit version files — this ceremony owns
  version sync via `sync_project_version`

## Qualifier Doctrine

Foundation ADRs codify app/system invariants and identity-shaping semantics.
Per the hexagonal port/adapter doctrine (`docs/governance/hexagonal-architecture.md`),
ports (foundation ADRs) and adapters (feature ADRs) are equal code surfaces —
both ship validators, runtime engines, and schemas, and both participate in
the patch-release cadence on the same footing. A foundation closeout
(Validated, all OBPIs Validated, Gate-5 `validated` receipt in the ledger) is a
release-worthy event in its own right — the operator does not need to bundle it
into an unrelated behavior-level GHI to ship it, and the CLI enumerates it
mechanically rather than leaving it to operator memory.

| Qualifier | Source of truth | Discovery |
|-----------|-----------------|-----------|
| Behavior-level GHIs | `gh issue list` + commit cross-validation | `gz patch release --dry-run` |
| Foundation-ADR closeout | Ledger Gate-5 `validated` receipt (`audit_receipt_emitted`), scoped to the release range by receipt timestamp | `gz patch release --dry-run` (mechanically enumerated — GHI #490) |

When the qualifier is a foundation-ADR closeout, the Step 2 narrative
references the ADR ID and its decision rather than listing GHIs. The release
flow (Steps 4a–4e) is identical regardless of which qualifier fired.

---

## The Iron Law

```
ONCE THE OPERATOR APPROVES, THE CEREMONY FLOWS TO COMPLETION.
```

After the operator approves the release notes in Step 3, the agent executes
Steps 4a through 4e without pauses, summaries, or requests for additional
confirmation. The operator made their decision. The agent carries it out.

### Rationalization Prevention

| Thought | Reality |
|---------|---------|
| "Let me confirm before creating the GitHub release" | The operator already approved. Execute. |
| "I'll summarize what was done so far" | Summary is for after Step 4e, not between sub-steps. |
| "The git-sync failed, let me ask what to do" | Diagnose and fix. Only escalate if truly blocked. |
| "Let me show the RELEASE_NOTES diff first" | The operator approved the narrative. Write it. |

---

## Procedure

### Step 1: Discovery

Run the dry-run discovery to show the operator what qualifies for this release:

```bash
uv run gz patch release --dry-run
```

Present the output to the operator. This shows:

- Latest tag and date
- Current version and proposed patch version
- Each discovered GHI with its cross-validation status (qualified, label_only,
  diff_only, excluded)
- Warnings for label/diff disagreements

If no GHIs qualify (all excluded), inform the operator and stop. There is no
release to make.

#### Step 1a: Labeling-recovery (binding when `diff_only` GHIs surface)

`diff_only` means a closed GHI's commits touched `src/gzkit/` but the GHI
itself lacks the `runtime` label — the strict qualifier (`runtime` ∩ src
diff) drops it, and substantive runtime fixes silently fall out of the
release narrative. This is an authoring-side labeling-discipline defect
canonized in `ghi-author` § Step 1 (secondary labels) — the GHI #402
mechanism. The recovery is binding before the ceremony proceeds:

1. Enumerate `diff_only` GHIs:

   ```bash
   uv run gz patch release --dry-run --json > /tmp/patch-release.json
   jq -r '.qualifications[] | select(.status == "diff_only") | .ghi.number' /tmp/patch-release.json
   ```

2. For each enumerated GHI, read the body to confirm the `runtime`
   predicate fires per `ghi-author` § Step 1 — body cites `src/gzkit/`,
   symptom is `gz <verb>` runtime, or remedy shape is `fix(...)`. Confirm
   case-by-case; do not blanket-apply.

3. Backfill the label with operator confirmation per GHI batch:

   ```bash
   gh issue edit <N> --add-label runtime
   ```

4. Re-run `uv run gz patch release --dry-run` and verify the previously
   `diff_only` GHIs now report `qualified`.

5. Proceed to Step 2.

If a `diff_only` GHI's body does NOT cite a runtime surface (e.g. the
commit happened to brush `src/gzkit/` cosmetically while the GHI was a
docs-only change), do not backfill — the `excluded` bucket is the right
home and the operator should re-classify with `--remove-label runtime`
on any erroneous prior label. The labeling-recovery is not a license to
silence warnings; it is a corrective for the authoring-discipline defect.

When `diff_only` is a chronic pattern across consecutive releases, file
a `defect`-labeled GHI against `ghi-author` discipline rather than
absorbing the recovery cost every cycle (canonical home: GHI #402).

### Step 2: Narrative Drafting

**Draft narrative release notes from GHI titles AND descriptions.** This is the
core value of the ceremony — the agent transforms raw issue data into
operator-facing release communication.

Rules for narrative drafting:

1. **NEVER use raw GHI titles as release notes.** GHI titles are triage
   shorthand, not user-facing communication.
2. **Read each qualifying GHI's description** to understand the actual change,
   not just the title.
3. **Group changes by functional area** (e.g., "CLI Fixes", "Governance
   Improvements", "Infrastructure") following the pattern in RELEASE_NOTES.md.
4. **Write in past tense** — "Fixed X", "Added Y", "Improved Z".
5. **Reference GHI numbers** as anchors: `- **#42** — Fixed version drift
   between pyproject.toml and __init__.py`.
6. **Include a one-line summary** at the top describing the release scope.

Draft format:

```markdown
## vX.Y.Z (YYYY-MM-DD)

<One-line summary of the release scope.>

### <Functional Area>

- **#NN** — Description of change
- **#NN** — Description of change

### Stats

- N GHIs closed
```

### Step 3: Operator Approval

Present the drafted release notes to the operator and wait for explicit approval.

**This is the human gate.** Do not proceed until the operator says "approved",
"looks good", "go ahead", or equivalent affirmative.

The operator may:

- **Approve as-is** — proceed to Step 4
- **Request edits** — revise the narrative and present again
- **Cancel** — stop the ceremony, no release produced

### Step 4: Execute Release

**Iron Law applies.** Once the operator approves, execute all sub-steps without
pauses.

#### 4a. Run `gz patch release`

```bash
uv run gz patch release
```

This atomically:

- Bumps the patch version via `sync_project_version` (pyproject.toml,
  `__init__.py`, README badge)
- Writes the markdown manifest to `docs/releases/PATCH-vX.Y.Z.md`
- Appends the JSONL ledger entry

#### 4b. Update RELEASE_NOTES.md

Insert the approved narrative release notes at the top of `RELEASE_NOTES.md`,
below the document header and above the most recent existing entry.

#### 4c. Git-sync

```bash
uv run gz git-sync --apply
```

This MUST run immediately before `gh release create`. Same policy as the
closeout ceremony.

#### 4d. GitHub Release (non-Foundation only)

**Foundation ADRs (0.0.x) skip this step.** The Foundation skip policy applies
to patch releases the same way it applies to minor releases in the closeout
ceremony.

For non-Foundation releases:

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

For Foundation releases, log:

```
Skipping GitHub release: Foundation ADR (0.0.x) — release artifacts are
RELEASE_NOTES.md entry and git tag only.
```

#### 4e. Confirm Completion

Present the final status to the operator:

```
Patch release vX.Y.Z complete.
  Version synced: pyproject.toml, __init__.py, README badge
  Manifest: docs/releases/PATCH-vX.Y.Z.md
  RELEASE_NOTES.md: updated
  Git-sync: committed and pushed
  GitHub release: created / skipped (Foundation)
```

---

## Foundation Policy

Foundation ADRs (version 0.0.x) follow a restricted release path:

- Version sync: **yes** (pyproject.toml, `__init__.py`, README badge)
- Manifest: **yes** (markdown + JSONL)
- RELEASE_NOTES.md: **yes**
- Git-sync: **yes**
- GitHub release: **no** — skipped per existing Foundation policy

This mirrors the `FOUNDATION_SKIP_STEPS` behavior in the closeout ceremony.

---

## MUST Rules

1. **MUST** draft narrative release notes from GHI content — never use raw titles
2. **MUST** wait for explicit operator approval before any publish action
3. **MUST** run `uv run gz git-sync --apply` immediately before
   `gh release create`
4. **MUST** skip GitHub release creation for Foundation (0.0.x) ADRs
5. **MUST** use `sync_project_version` via `gz patch release` — never manually
   edit version files
6. **MUST** execute Steps 4a-4e without pauses after operator approval

## MUST NOT Rules

1. **MUST NOT** use raw GHI titles as release notes
2. **MUST NOT** proceed past Step 3 without explicit operator approval
3. **MUST NOT** create a GitHub release for Foundation (0.0.x) versions
4. **MUST NOT** pause between Step 4 sub-steps for confirmation or summaries
5. **MUST NOT** manually edit pyproject.toml, `__init__.py`, or README badge —
   version sync is `gz patch release`'s responsibility
6. **MUST NOT** skip the git-sync step or reorder it after `gh release create`

---

## CLI Reference

| Command | Purpose |
|---------|---------|
| `gz patch release --dry-run` | Discovery: show qualifying GHIs and proposed version |
| `gz patch release --dry-run --json` | Discovery: machine-readable output |
| `gz patch release` | Execute: version sync + manifest generation |
| `gz patch release --json` | Execute: machine-readable output |
| `gz git-sync --apply` | Pre-release sync with quality gates |
| `gh release create vX.Y.Z ...` | GitHub release (non-Foundation only) |

---

## References

- CLI command: `src/gzkit/commands/patch_release.py`
- Version sync: `src/gzkit/commands/version_sync.py` (`sync_project_version`)
- Closeout ceremony: `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- Command docs: `docs/user/manpages/patch-release.md`
- Governance release policy: `docs/governance/GovZero/releases/patch-release.md`
