---
id: skill-surface-sync
paths:
  - ".claude/**"
  - ".agents/**"
  - ".gzkit/skills/**"
  - ".gzkit/rules/**"
description: Version-disciplined editing and sync for skill and rule surfaces
---

<!-- rule-version: 0.15.0 -->

# Skill & Surface Sync (gzkit)

> **Rule version:** `0.15.0` — § Surface layout lists `.gzkit/agents/`: each registered role's Codex and Claude copies are generated from its canonical body, their vendor metadata kept (GHI #1328; operator, 2026-11-14: *"A: Generate from canon"*); prior narrative in [Rule Version History](../../docs/governance/rule-version-history.md#skill-surface-syncmd).

## Non-negotiable rules

1. **Edit `.gzkit/` first.** `.gzkit/skills/` and `.gzkit/rules/` are canonical; every other copy is generated.
2. **Bump the version on every edit.** Do not edit a skill without bumping its `skill-version` frontmatter, nor a rule without its body-level marker; do not skip sync because two files look the same (it also updates manifests and registrations). Skills: `metadata.skill-version`, a quoted `X.Y.Z` string nested under `metadata:` (a top-level `skill-version:` is invisible to `skills_audit.py`; presence is enforced, `SKA-METADATA-SKILL-VERSION-MISSING`). Rules: the body-level `<!-- rule-version: X.Y.Z -->` comment right after the frontmatter plus the visible `> **Rule version:** \`X.Y.Z\`` block quote with a one-sentence rationale; `RuleFrontmatter` is `extra="forbid"` and rejects `skill-version:` on a rule. Minor for a governance or procedure change, patch for wording or tooling.
3. **Run sync after every edit.** `uv run gz agent sync control-surfaces` writes the wheel copy at `src/gzkit/<surface>/` and every enabled vendor's mirror in one invocation.
4. **Never edit vendor mirrors directly.** Read the roster from `.gzkit.json` § `vendors`, never from a list here — a transcribed roster went stale when Copilot was dropped (GHI #921).
5. **Never edit `src/gzkit/<surface>/` directly.** `src/gzkit/{skills,rules,personas,templates}/` are derived; only `sync_pkg_surfaces` writes them.
6. **`skill-version` bumps require `last_reviewed` bumps in the same edit (skills only).** Set `last_reviewed:` to today's date whenever `skill-version` moves — the 90-day staleness audit (`DEFAULT_MAX_REVIEW_AGE_DAYS`, `src/gzkit/skills_audit.py`) reads it, and a version bump without it silently disarms that signal. Rules carry no `last_reviewed:`.

## Surface layout

| Canonical (edit here) | Pkg copy (generated) | Vendor mirrors (generated) | Version marker |
|---|---|---|---|
| `.gzkit/skills/` | `src/gzkit/skills/` | `<surface_root>/skills/` per enabled vendor | `metadata.skill-version` |
| `.gzkit/rules/` | `src/gzkit/rules/` | `<surface_root>/rules/` or the vendor's `instruction_format` path | `<!-- rule-version -->` + block quote |
| `.gzkit/personas/` | `src/gzkit/personas/` | `<surface_root>/personas/` | none |
| `.gzkit/templates/` | `src/gzkit/templates/` | none (scaffold-time only) | none |
| `.gzkit/chores/<slug>/` | `src/gzkit/chores/<slug>/` (canonical class only) | none | none |
| `.gzkit/agents/` (roles registered in `roles.json`) | none | `.codex/agents/<name>.toml`, `.claude/agents/<name>.md`: body from canon, vendor metadata and frontmatter kept | none |

Sync compares no versions: it rewrites every mirror from canon, so a hand edit to a mirror is lost at the next sync. The drift report is `gz validate --surfaces`: *"Generated surface is out of sync with canonical state. Run `uv run gz agent sync control-surfaces` to repair."* (`validate_pkg/sync_parity.py`). Before running that sync, carry any mirror edit worth keeping into `.gzkit/` and bump its version; flag one whose origin is unclear for human review. Full resolution design: [Skill-Surface-Sync Rationale](../../docs/governance/skill-surface-sync-rationale.md).

## Bootstrap semantics (`gz init`)

After `gz init`, the adopter's `.gzkit/<surface>/` is the canonical source and rule 1 binds from then on; the wheel's package surface is the one-time bootstrap source. Repair-mode `gz init` is idempotent (`skip_existing=True`); `--force` wipes and re-copies. Retired-slug filtering, scaffolding order and the `gz init --update` roadmap: [Rationale § Bootstrap semantics](../../docs/governance/skill-surface-sync-rationale.md#bootstrap-semantics-gz-init).

## Retirement policy (delete-on-retire, binding)

A superseded or consolidated skill's directory is deleted from every surface root — `.gzkit/skills/`, `src/gzkit/skills/`, each enabled vendor's `<surface_root>/skills/` — in the same commit or OBPI that introduces its successor. No `lifecycle_state: retired` stub survives. Rationale (GHI #464): [Rationale § Retirement policy](../../docs/governance/skill-surface-sync-rationale.md#retirement-policy-delete-on-retire).

A retired rule leaves the same way. Its doctrine moves first, to a named home: a skill that runs when the rule binds, a doc under `docs/governance/`, an `AGENTS.md` entry, or the failure message of the witness that enforces it. Retiring never deletes doctrine. In the commit that retires the rule:

- delete `.gzkit/rules/<name>.md`, then sync, which removes the vendor mirrors. Sync never removes the package copy, so delete `src/gzkit/rules/<name>.md` by hand. That is the one exception to rule 5, and it lasts until GHI #1316 lands;
- remove its entry from `data/distribution_baseline_manifest.json` and its row from the Coverage Ledger of `docs/governance/advisory-rules-audit.md`, and re-point or retire the scorecard rows that cite it;
- re-point every test, validator message, doc link and `.gzkit/chores/registry.json` target that names the rule's path.

A test behind an attested REQ that reads the rule is repaired at the surface (`AGENTS.md` § OBPI Acceptance Protocol, attested REQ whose subject a later ruling retired); one whose REQ asserts the file exists goes to the operator first. **Advisory in part:** `gz validate --distribution` refuses a baseline entry left behind, but sync never removes the package copy (GHI #1316) or an adopter's copy, and no witness flags an orphaned ledger row (GHI #1317).

## Canonical surface class-classifier

Every file under a canonical surface (`src/gzkit/{chores,rules,skills,personas,templates}/`) is exactly one class (OBPI-0.0.32-13/-15):

| Class | Definition | Byte-parity | Sync |
|---|---|---|---|
| **canonical** | operator-authored content present at `.gzkit/<surface>/` | required | `.gzkit/ → src/gzkit/`; in the wheel and the baseline manifest |
| **package_only** | Python modules and support files with no `.gzkit/` counterpart (`__init__.py`, `_scaffolder.py`), and a retired skill the wheel still carries | exempt | never propagated to `.gzkit/` |
| **runtime_state** | per-run logs, receipts, proofs | exempt | never synced either way |
| **project_local** *(chores and skills)* | a chore whose `registry.json` entry declares `"projectLocal": true`, or a skill whose `SKILL.md` frontmatter declares `project_local: true` (GHI #915) | exempt | never shipped in the wheel or scaffolded by `gz init` |

Declare a project-local chore with `"projectLocal": true` in `.gzkit/chores/registry.json`, and a project-local skill with `project_local: true` in its `SKILL.md` frontmatter — the property is declared, never inferred, and the shipped `registry.json` is filtered so the wheel never advertises a chore it does not carry (GHI #728). `gz validate --distribution` and `sync_pkg_surfaces` both read the per-surface `_classify_<surface>_file` helpers. Per-surface default classes and the classifier matrix: [Rationale § Class-classifier reference](../../docs/governance/skill-surface-sync-rationale.md#class-classifier-reference).
