---
name: gz-deps-upgrade
persona: main-session
description: Refresh global uv tools, Python 3.13.x runtime, pyproject.toml pins/floors, and uv.lock to current PyPI latest in one disciplined pass. Use this skill whenever the operator asks to "update deps", "upgrade dependencies", "refresh uv.lock", "bump python", "update python 3.13", "deps to latest", "update pyproject", or any phrasing that asks for the project's dependency surface to move forward to current upstream — even if they don't name uv or pyproject explicitly. Default tool when "update" / "upgrade" lands on Python tooling for this repo.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-02
model: haiku
metadata:
  skill-version: "1.0.0"
---

# gz deps-upgrade

## Overview

A disciplined upgrade pass for the project's Python dependency surface:
global uv tools, Python 3.13.x runtime, `pyproject.toml` pins (`==`), `>=`
floors, and `uv.lock`. Verifies with `gz check` and emits a canonical ARB
unittest receipt as evidence.

The procedure is mechanical — its value is doing the *full* sequence in
order, not skipping the floor-bump or the verification step.

## Workflow

1. **Refresh global uv tools** (`mkdocs`, `ruff`, `ty`, `py-gzkit`).

   ```bash
   uv tool upgrade --all
   ```

2. **Refresh Python 3.13.x runtime.** uv installs the latest patch release
   of 3.13 — idempotent. Leave any `.python-version` file at `3.13`.

   ```bash
   uv python install 3.13
   uv python list --only-installed | grep '^cpython-3.13'
   ```

3. **Bump pinned (`==`) deps in `pyproject.toml` to current PyPI latest.**
   Inspect the pinned entries under `[project.optional-dependencies]` and
   `[dependency-groups]`. For each pinned package, query PyPI:

   ```bash
   curl -s "https://pypi.org/pypi/<pkg>/json" \
     | python3 -c 'import sys,json;print(json.load(sys.stdin)["info"]["version"])'
   ```

   Edit `pyproject.toml` to replace each `<pkg>==X.Y.Z` with the latest
   version. Skip if the pin already matches latest.

4. **Refresh the lock to latest within `>=` constraints.**

   ```bash
   uv lock --upgrade
   ```

5. **Sync the environment to the new lock.**

   ```bash
   uv sync
   ```

6. **Raise `>=` floors in `pyproject.toml` to match what got locked.**
   Read each locked version with:

   ```bash
   grep -E '^name = "(<pkg1>|<pkg2>|...)"$' -A 1 uv.lock
   ```

   Edit each `>=` entry to match the locked version. Skip patch-only bumps
   that are trivial (e.g., 7.13.4 → 7.13.5 within the same minor); bump
   on minor/major changes (e.g., 13.0 → 15.0, 24.0 → 25.5).

7. **Re-run lock + sync** to confirm the new floors don't force
   re-resolution.

   ```bash
   uv lock
   uv sync
   ```

8. **Verify with full quality gate.**

   ```bash
   uv run gz check
   ```

   Must end with `✓ All checks passed.` Anything else is a failure — stop
   and diagnose. Do **not** weaken floors to make the gate pass; pin the
   offender at the previous-known-good version and file a GHI for the
   migration.

9. **Emit canonical ARB unittest receipt** (per AGENTS.md § Attestation).

   ```bash
   uv run gz arb step --name unittest -- uv run -m unittest -q
   ```

   Capture the receipt path (`artifacts/receipts/arb-step-unittest-*.json`)
   for the commit message.

10. **Mirror skill changes** if you also touched skills/rules in the same
    pass:

    ```bash
    uv run gz agent sync control-surfaces
    ```

11. **Summarize the diff** for the operator: tool versions before/after,
    pyproject pin/floor deltas, count of locked-package upgrades, and the
    ARB receipt ID.

## Suggested commit message

```
chore(deps): upgrade pyproject + uv.lock to latest

<Notable upgrades — major bumps, pin moves, floor lifts.>

Verified via uv run gz check (✓ All checks passed) and ARB-receipted
unittest run: <N> tests, OK, exit_status=0
(receipt arb-step-unittest-<id>).
```

Pass the user's verbatim phrasing through the attestation per
AGENTS.md § Attestation. Do not include the operator's personal email.

## Risk notes

Major-version bumps that have historically required manual review (track
release notes if `gz check` fails after the upgrade):

- `rich` major bumps (Console / Table API surface)
- `pydantic` minor bumps (model serialization edge cases)
- `structlog` major bumps
- `behave` minor bumps after long quiet periods
- `pyinstaller` minor bumps (binary build path)

Recovery posture: pin the offender, file a GHI for the migration, do not
skip the upgrade for the rest of the surface.

## Validation

- `uv run gz check` exits 0
- `uv.lock` resolves cleanly with no churn on the second `uv lock` run
- ARB unittest receipt at `exit_status=0` exists in
  `artifacts/receipts/`

## Common Rationalizations

These thoughts mean STOP — you are about to ship a half-upgrade:

| Thought | Reality |
|---------|---------|
| "Lock-only bump is enough; floors don't matter" | Floors document tested baseline. Operators on fresh installs can resolve to versions you never tested if the floor lags. Bump them. |
| "I'll skip the ARB receipt — `gz check` already passed" | `gz check` runs tests but does not emit the canonical receipt AGENTS.md § Attestation requires for the commit message. Run the ARB step. |
| "The pin bump is just a patch — leave it" | If the pin is `==` the operator has stated intent to pin. Move the pin to current latest; do not let pinned packages silently lag. |
| "I'll bump the floor to whatever — `>=4.0` covers 4.26 anyway" | The floor is a tested baseline, not a wish. Set it to what `uv lock` actually resolved, so future installs match the tested resolution. |
| "Python is fine, no need to refresh 3.13" | Patch releases ship CPython security fixes. `uv python install 3.13` is idempotent and cheap; running it costs nothing. |
| "If `gz check` fails, I'll just lower the floor" | Lowering a floor to mask a failure ships a known-broken upgrade. Pin the offender at last-known-good and file a GHI. |

## Red Flags

- `uv.lock` and `pyproject.toml` floors disagree by more than a patch level after the upgrade
- Pinned (`==`) deps left at versions older than current PyPI latest
- `gz check` skipped, downgraded, or run only on a subset
- ARB unittest receipt not emitted (commit message has no receipt ID)
- Committing the upgrade without the attestation enrichment
- Touching `[project] version` as part of a deps upgrade (deps changes are not a release; AGENTS.md local rules)

## References

- AGENTS.md § Attestation — canonical ARB receipt requirement
- AGENTS.md § STDLIB-FIRST DOCTRINE — dependency-add discipline
- `pyproject.toml` — single source of truth for pins/floors
- `uv.lock` — resolution snapshot
- `.gzkit/skills/gz-check/SKILL.md` — quality gate invocation
