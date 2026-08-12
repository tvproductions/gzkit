---
name: gz-patch-release
persona: main-session
description: "Orchestrate the GHI-driven patch release ceremony: draft narrative release notes, operator approval, RELEASE_NOTES update, git-sync, and GitHub release."
category: adr-audit
compatibility: GovZero v6 framework; provides ceremony walkthrough for GHI-driven patch releases
metadata:
  skill-version: "1.10.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/releases/patch-release.md, docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-12
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
- **Writes:** Narrative release notes, RELEASE_NOTES.md entry, CHANGELOG.md entry, GitHub release
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
  diff_only, open_upstream, excluded)
- Warnings for label/diff disagreements and for still-open GHIs

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

#### Step 1b: Open-upstream adjudication (binding when `open_upstream` GHIs surface)

`open_upstream` means a GHI carries the `runtime` label AND has commits
touching `src/gzkit/` in the release range — it would otherwise qualify —
but is still **OPEN** on GitHub. Discovery cannot resolve this alone: the
project-canonical subject form `fix(<scope>): <summary> (GHI #N)` is what
`AGENTS.md` § Defect-fix routing prescribes for *any* GHI-tracked repair,
so it attributes work without declaring closure. A locally-committed fix
awaiting push and an incremental cut under a deliberately-open tracker
produce the identical commit (GHI #714).

The operator adjudicates, per GHI:

1. Enumerate them:

   ```bash
   uv run gz patch release --dry-run --json > /tmp/patch-release.json
   jq -r '.qualifications[] | select(.status == "open_upstream") | .ghi.number' /tmp/patch-release.json
   ```

2. For each, determine which case it is:

   | Case | Signal | Action |
   |------|--------|--------|
   | Fix landed; close pending push | The range contains the complete remedy; nothing is held back | Close the GHI (`gh issue close <N> --comment "…"` citing the commit SHA), re-run discovery, and it reports `qualified` |
   | Work under a still-open tracker | Part of the scope landed; the GHI intentionally remains open | Leave open. Describe **only what actually landed** in Step 2 — never the GHI's full scope — and do not count it in the `Stats` line |

3. Re-run `uv run gz patch release --dry-run` after any closures.

4. Proceed to Step 2.

**Do not close a GHI merely to clear the bucket.** The bucket exists so the
release narrative stops asserting closures that did not happen; closing an
open tracker to make the warning disappear reintroduces the exact defect
(canonical instances: GHI #533 and #615 during the v0.33.2 ceremony).

#### Step 1c: Unclassified-reference adjudication (binding when `unclassified_reference` GHIs surface)

`unclassified_reference` means a GHI is cited in the release range by a
commit whose Conventional-Commits type is **not** a closure type
(`fix`/`feat`/`perf`/`refactor`/`revert`), and no closure commit in the
range claims it. Discovery cannot decide this alone: `chore` and `docs`
are excluded from the closure types on the premise that such commits
ceremonialize work closed by a separate code-change commit, and when no
such commit exists the premise is false.

The bucket is **disclosure, not qualification** — it exists because the
prior state was silence. Every other bucket is computed from the closure
ref set, so a GHI absent from that set rendered as a shorter list rather
than a warning, and there was no "referenced but unclassifiable" state to
render (GHI #794).

1. Enumerate them:

   ```bash
   uv run gz patch release --dry-run --json > /tmp/patch-release.json
   jq -r '.qualifications[] | select(.status == "unclassified_reference") | .ghi.number' /tmp/patch-release.json
   ```

2. For each, determine which case it is:

   | Case | Signal | Action |
   |------|--------|--------|
   | The citing commit IS the remedy | A dependency or toolchain upgrade, a generated-surface regeneration — `chore(deps): … (GHI #N)` with no separate code commit. `has_runtime_label` and `has_src_diff` are usually both true | Treat as release content. Write it into the Step 2 narrative and the changelog by hand; the enumeration will not do it for you |
   | The GHI was routed, not shipped | `docs(adr): … (GHI #N)` authoring a pool ADR the finding was closed `superseded` against, per `ghi-author` § Doctrine | Not release content. Leave it out of the narrative |
   | The citing commit is context only | The GHI's real remedy shipped in a prior tag; this commit merely references it | Not release content |

3. Record the adjudication in the release notes' `### Gate Evidence`,
   naming which case fired. The bucket surfaces the question every
   release; a decision made and not written down gets re-made next
   release from scratch.

4. Proceed to Step 2.

**Do not suppress a report by re-typing the commit.** Rewriting
`chore(deps):` as `fix(deps):` to clear the bucket makes the symptom
vanish and leaves the next non-code-typed remedy exposed — the same shape
§ Step 1a refuses for `diff_only`. If the closure-type set itself should
change, that is an operator ruling against GHI #794, not a commit-message
edit.

### Step 2: Narrative Drafting

**Draft narrative release notes from GHI titles AND descriptions.** This is the
core value of the ceremony — the agent transforms raw issue data into
operator-facing release communication.

Rules for narrative drafting:

1. **NEVER use raw GHI titles as release notes.** GHI titles are triage
   shorthand, not user-facing communication.
2. **Read each qualifying GHI's description** to understand the actual change,
   not just the title.
3. **Group changes into the Good Docs sections** the adopted template
   (`.gzkit/templates/release_notes.md`, GHI #685) prescribes — Highlights /
   New features / Improvements / Bug fixes / Known issues / Deprecated — ordered
   by reader impact. Functional-area / subsystem grouping is CHANGELOG altitude;
   it does not belong in the curated release notes.
4. **Tense follows Good Docs:** present tense for features and improvements
   ("Adds X", "Improves Y"); past tense for bug fixes ("Fixed X"). **Do not
   describe HOW a bug was fixed** — mechanism and internals are CHANGELOG.md's
   job (`.gzkit/rules/changelog-release-notes.md`: the two artifacts never
   collapse into each other). Release notes headline reader-facing impact.
5. **Reference GHI numbers** as anchors: `- **#42** — Fixed version drift
   between pyproject.toml and __init__.py`.
6. **Include a one-line summary** at the top describing the release scope.

Draft format (Good Docs shape; omit any section with no content, but
`### Gate Evidence` is RETAINED per `.gzkit/templates/release_notes.md`):

```markdown
## vX.Y.Z (YYYY-MM-DD)

<One-to-two-sentence highlights summary of the release scope.>

### New features

- **#NN** — Reader-facing capability, present tense.

### Improvements

- **#NN** — Reader-facing enhancement, present tense.

### Bug fixes

- **#NN** — Reader-facing effect of the fix, past tense; no mechanism.

### Gate Evidence

<Qualifiers, version sync, operator approval, git-sync gates.>

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
below the document header and above the most recent existing entry. Conform to
`.gzkit/templates/release_notes.md` — the *curated, reader-facing* narrative,
retaining the `### Gate Evidence` provenance section
(`.gzkit/rules/changelog-release-notes.md`).

#### 4b-bis. Update CHANGELOG.md (distinct artifact — not the same as release notes)

Stamp the accumulated `## [Unreleased]` block in `CHANGELOG.md` with
`## vX.Y.Z (YYYY-MM-DD)` and open a fresh empty `## [Unreleased]`. The changelog
is the *exhaustive, developer-facing* projection of the closed-since-tag GHIs,
conforming to `.gzkit/templates/changelog.md`, one `GHI #N` per entry.

Run the hermetic structural check on the stamped file:

```bash
uv run gz validate --changelog
```

**Coverage cross-check (release-time teeth):** every closed-since-tag user-visible
GHI surfaced by `gz patch release --dry-run` MUST appear as a changelog entry
before publish. A discovered GHI with no changelog entry blocks the release — this
is the networked half of the enforcement the hermetic `gz validate --changelog`
structural check cannot perform.

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

For non-Foundation releases, publish ONLY the newest version block as the
release body — `RELEASE_NOTES.md` is cumulative, so `--notes-file` on the whole
file would dump every historical version into the release (GHI #710). Slice the
top block (a new release is always prepended, so the newest entry is the first
`## v…` block):

```bash
BODY="$(mktemp)"
awk '/^## v/{c++} c==2{exit} c==1' RELEASE_NOTES.md > "$BODY"
gh release create vX.Y.Z --target main --latest --title "vX.Y.Z" --notes-file "$BODY"
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
