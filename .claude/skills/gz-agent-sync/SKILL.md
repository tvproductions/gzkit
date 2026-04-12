---
name: gz-agent-sync
description: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.1.0"
---

# gz agent sync control-surfaces

## Overview

Operate the gz agent sync control-surfaces command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz agent sync control-surfaces` (or `--dry-run` first when staging changes).
3. If sync preflight fails, repair canonical `.gzkit/skills` state before retrying.
4. If sync reports stale mirror-only paths, follow manual recovery:
   - `uv run gz skill audit --json`
   - remove stale mirror-only paths listed by sync
   - `uv run gz agent sync control-surfaces`
   - `uv run gz skill audit`
5. Summarize deterministic output, recovery actions, and follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Common Rationalizations

These thoughts mean STOP — you are about to create canon/derived drift:

| Thought | Reality |
|---------|---------|
| "I edited `.claude/skills/foo/SKILL.md` directly — it's the runtime path anyway" | `.claude/` is a vendor mirror. The next sync overwrites it. Edit `.gzkit/skills/foo/SKILL.md` (canonical) and run sync. The instinct to edit the mirror is the bug. |
| "The mirrors look identical to canon — skip sync" | Sync is idempotent on a clean tree. Running it costs nothing; not running it after a skill edit guarantees drift. |
| "I bumped `last_reviewed` instead of `skill-version`" | Version mismatch is the conflict-resolution signal. Without a `skill-version` bump, sync cannot detect intentional edits vs. mirror drift. Bump the version. |
| "Sync reported stale mirror-only paths — I'll deal with them next time" | Stale mirror paths mean the canonical source was deleted or renamed. Leaving them means the old skill keeps loading. Run the recovery sequence now. |
| "Two skills have the same content — sync isn't needed" | Same content can have different `skill-version` values. The version is the primary signal; ignoring it loses the audit trail. |
| "I can skip `--dry-run`, this edit was small" | The dry-run shows you exactly which mirrors will change. Five seconds of preview prevents the "what just happened to my .github/instructions/" recovery session. |
| "Manual copy from canonical to mirror is faster than sync" | Sync also updates manifests, registrations, and vendor-specific rendering. A manual copy gets the file but breaks the index. |

## Red Flags

- Direct edits to `.claude/skills/`, `.claude/rules/`, `.github/skills/`, or `.github/instructions/`
- Skill edits without a `skill-version` bump
- Sync run produces no output diff but the canonical files just changed (something is broken)
- Stale mirror-only paths reported and not cleaned up
- Mirror version higher than canonical version (someone edited the wrong surface)
- Skill manifests out of sync with on-disk skill files
- Skipping sync because "the mirrors are fine"

## Example

Use $gz-agent-sync to sync control surfaces and mirrors..
