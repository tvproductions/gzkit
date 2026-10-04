---
name: gz-deps-upgrade
persona: main-session
description: Move the toolchain and dependencies to current upstream in one pass: uv itself, global uv tools, the Python 3.13.x runtime, `pyproject.toml` pins and `uv.lock`. Use when the operator asks to update or upgrade deps, Python, uv, pyproject or the lockfile.
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-10-04
model: haiku
metadata:
  skill-version: "1.3.0"
---

# gz deps-upgrade

## Overview

A disciplined upgrade pass for the project's Python toolchain and dependency
surface: the `uv` binary itself, global uv tools, Python 3.13.x runtime,
`pyproject.toml` pins (`==`), `>=` floors, and `uv.lock`. Verifies with
`gz check` and emits a canonical ARB unittest receipt as evidence.

The procedure is mechanical — its value is doing the *full* sequence in
order, not skipping the floor-bump or the verification step.

## Workflow

1. **Refresh the `uv` binary itself first.** uv is the foundation of every
   later step — its resolver and lockfile behavior can change between
   releases, so upgrade it before resolving anything. When uv was installed
   via the standalone installer (`~/.local/bin/uv`), `uv self update` works
   directly. When uv is managed by an external package manager (Homebrew,
   pipx, system), `uv self update` is disabled — upgrade through that manager
   instead (`brew upgrade uv`, `pipx upgrade uv`, etc.) and note which path
   was used.

   ```bash
   uv --version                      # before
   uv self update                    # standalone-installer path
   # OR, if self-update is disabled: brew upgrade uv  /  pipx upgrade uv
   uv --version                      # after — confirm it moved (or already latest)
   ```

   **Move the pin with the binary.** `pyproject.toml` `[tool.uv]
   required-version` pins the exact uv version for this repository, and it is
   the one authority: uv refuses to run here on any other version, and
   `astral-sh/setup-uv` installs exactly that version in every workflow. Once
   the binary has moved, every `uv` command in the repository fails until the
   pin names the new version, so set `required-version = "==<new version>"`
   before the next step. CI follows in the same commit; no workflow carries a
   uv version of its own.

   Skipping uv itself is a half-upgrade: the rest of the pass runs on a stale
   resolver. Never skip this step.

2. **Refresh global uv tools** (`mkdocs`, `ruff`, `ty`, `py-gzkit`).

   ```bash
   uv tool upgrade --all
   ```

3. **Refresh Python 3.13.x runtime and move the pin with it.** uv installs
   the latest patch release of 3.13 — idempotent. `.python-version` pins the
   full patch (e.g. `3.13.15`), not `3.13`: it is the authority
   `gz validate --python-version-pins` holds every CI declaration to
   (`python-version:` and `uv python install` in `.github/workflows/`).

   ```bash
   uv python install 3.13
   uv python list --only-installed | grep '^cpython-3.13'
   cat .python-version
   ```

   When the newest installed patch is above the pin, run
   `uv python pin 3.13.<N>` and change every workflow declaration to the same
   patch in this pass; the pin and the workflows move together or not at all.
   Confirm with `uv run gz validate --python-version-pins`.

4. **Bump pinned (`==`) deps in `pyproject.toml` to current PyPI latest.**
   Inspect the pinned entries under `[project.optional-dependencies]` and
   `[dependency-groups]`. For each pinned package, query PyPI:

   ```bash
   curl -s "https://pypi.org/pypi/<pkg>/json" \
     | python3 -c 'import sys,json;print(json.load(sys.stdin)["info"]["version"])'
   ```

   Edit `pyproject.toml` to replace each `<pkg>==X.Y.Z` with the latest
   version. Skip if the pin already matches latest.

5. **Refresh the lock to latest within `>=` constraints.**

   ```bash
   uv lock --upgrade
   ```

6. **Sync the environment to the new lock.**

   ```bash
   uv sync
   ```

7. **Raise `>=` floors in `pyproject.toml` to match what got locked.**
   Read each locked version with:

   ```bash
   grep -E '^name = "(<pkg1>|<pkg2>|...)"$' -A 1 uv.lock
   ```

   Edit each `>=` entry to match the locked version. Skip patch-only bumps
   that are trivial (e.g., 7.13.4 → 7.13.5 within the same minor); bump
   on minor/major changes (e.g., 13.0 → 15.0, 24.0 → 25.5).

8. **Re-run lock + sync** to confirm the new floors don't force
   re-resolution.

   ```bash
   uv lock
   uv sync
   ```

9. **Verify with full quality gate.**

   ```bash
   uv run gz check
   ```

   Must end with `✓ All checks passed.` Anything else is a failure — stop
   and diagnose. Do **not** weaken floors to make the gate pass; pin the
   offender at the previous-known-good version and file a GHI for the
   migration.

10. **Emit canonical ARB unittest receipt** (per AGENTS.md § Attestation).

    ```bash
    uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
    ```

    Capture the receipt path (`artifacts/receipts/arb-step-unittest-*.json`)
    for the commit message.

11. **Mirror skill changes** if you also touched skills/rules in the same
    pass:

    ```bash
    uv run gz agent sync control-surfaces
    ```

12. **Summarize the diff** for the operator: uv binary + tool versions
    before/after, pyproject pin/floor deltas, count of locked-package
    upgrades, and the ARB receipt ID.

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
- `.python-version` names the newest installed 3.13 patch, and
  `uv run gz validate --python-version-pins` exits 0
- `uv --version` equals the `[tool.uv] required-version` pin in `pyproject.toml`
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
| "The skill is about deps, not uv itself" | uv IS the toolchain that resolves every dep. A pass that upgrades tools/lock on a stale uv is a half-upgrade running on an old resolver. `uv self update` is Step 1; skipping it is the bug this row exists to prevent. |
| "If `gz check` fails, I'll just lower the floor" | Lowering a floor to mask a failure ships a known-broken upgrade. Pin the offender at last-known-good and file a GHI. |

## Red Flags

- `uv` binary left un-upgraded (Step 1 skipped) — the rest of the pass ran on a stale resolver
- `uv` binary upgraded and the `required-version` pin left behind — every `uv` command now fails, and CI still installs the old version
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
