<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# T0 Failure-Mode Catalog

**Doctrine source:** [trust-doctrine.md § T0 — Distribution Invariant](trust-doctrine.md#t0-distribution-invariant)

This catalog is the operator-facing companion to the T0 doctrine paragraph in `trust-doctrine.md`. Where the doctrine page names the invariant in one paragraph, this catalog gives it teeth: worked examples of past T0-class failures and a canonical "Is this a T0 breach?" decision tree that future canonical-surface promotions check against during authoring.

The catalog references and applies the T0 doctrine. It does not redefine it. Any framing difference between this file and `trust-doctrine.md` § T0 is a defect in this file — the doctrine page is authoritative.

**Mechanical enforcement:** [ADR-0.0.32 (canonical surface packaging)](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md) is the mechanical counterpart to this doctrine. The decision tree below points into ADR-0.0.32's OBPI work items for each class of T0 breach.

---

## Worked Example #1: GHI #318 — Self-Hosting Blindness

**Summary:** `pip install py-gzkit && gz init` in a greenfield project produces zero rule files and one-line skill stubs — not the canonical surfaces gzkit uses to govern itself. The failure was concealed for the entire pre-1.0 cycle because gzkit develops against its own repo's `.gzkit/` content; no "fresh-project install" smoke test existed. The dogfood loop closed in a way that made the packaging gap structurally invisible.

**Surfaced:** 2026-04-25 by the first external greenfield consumer.

**Why this is a T0 breach:** Every failure class below is a case where a canonical surface existed in the repo but was not reproducibly delivered to a fresh `gz init`. The downstream consumer received a degraded surface (stub or nothing) while `gz init` reported success — the exact shape the T0 invariant names.

### Failure Class A — Rules Entirely Unscaffolded

No `scaffold_core_rules` function existed. No `CORE_RULES` registry symmetric to `CORE_SKILLS` or `CORE_CHORES`. `init_cmd.py` never referenced rules. A greenfield `gz init` produced zero rule files; contextual rule loading silently no-oped.

**Closed by:**
- [OBPI-0.0.32-03](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-03-rules-physical-migration.md) — physical migration (`git mv .gzkit/rules/<slug>.md src/gzkit/rules/<slug>.md` for all 14 canonical rules)
- [OBPI-0.0.32-04](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-04-rules-scaffolder-authoring.md) — `CORE_RULES` registry + `scaffold_core_rules` + `init_cmd` wiring

### Failure Class B — Skills Scaffold as One-Line Stubs

`scaffold_core_skills` iterated `CORE_SKILLS` and rendered each through the generic `templates/skill.md` template with one-line metadata. The stub for `gz-status` was `behavior_description: "Run \`gz status\` and present a structured overview."` — unrelated to the canonical SKILL.md that exists in this repo. `gz init` reported "Scaffolded N core skills"; the count was true but content depth was far below the canonical surface.

**Closed by:**
- [OBPI-0.0.32-01](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-01-skills-physical-migration.md) — physical migration of all 61 canonical skills into `src/gzkit/skills/<slug>/SKILL.md`
- [OBPI-0.0.32-02](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-02-skills-scaffolder-refactor.md) — scaffolder refactor to copy canonical SKILL.md content from `importlib.resources.files("gzkit.skills")` instead of rendering stubs

### Failure Class C — Wheel Package-Data Includes Chores Only

`pyproject.toml` `[tool.hatch.build.targets.wheel]` declared chores under `src/gzkit/chores/**` but nothing else. No skill SKILL.md content was shipped (no `src/gzkit/skills/<slug>/SKILL.md` tree existed at all — see B). No rule files were shipped. Templates and hook-auxiliary files were likely absent from the wheel. The inclusion was a point-in-time artifact of ADR-0.0.21 (chores promotion) extending the include list without recognizing that skills and rules faced the same gap.

**Closed by:**
- [OBPI-0.0.32-06](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-06-t0-smoke-test.md) — build-then-install T0 smoke test + `pyproject.toml` include extension to ship the new surface trees
- [OBPI-0.0.32-07](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-07-validate-distribution.md) — `gz validate --distribution` T0 enforcement scope (fail-closed exit 3 on any unshipped canonical surface)

### Failure Class D — Re-Run Upgrade Only Adds Missing Artifacts

`init_cmd.py` routed re-runs through `_repair_missing_artifacts` when `--force` was not passed. Repair called `scaffold_core_skills(..., skip_existing=True)` — an existing stub skill was never refreshed even when the package shipped an improved canonical version. Cross-version upgrades silently left stale artifacts in place. The only escape was `--force`, a full wipe.

**Closed by:**
- [OBPI-0.0.32-05](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-05-init-update-flag.md) — `gz init --update` flag with three-state detection (IDENTICAL / STALE / EDITED) and version-aware refresh

### Root Cause

Self-hosting blindness is the meta-failure: gzkit ran every test against its own repo's `.gzkit/` content, never against a wheel-installed surface in a fresh project. The trust chain accepted `gz init` exit-0 without independent verification of content depth. T0 names this class so future surface promotions cannot accumulate silently again.

---

## Worked Example #2: The Chores Promotion Gap (ADR-0.0.21)

**Summary:** Chores got the right T0-compliant packaging treatment. Skills and rules did not. The difference was not doctrine — it was timing.

**Doctrine:** [ADR-0.0.21 (chores-as-gzkit-surface)](../design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md)

### What ADR-0.0.21 Got Right

ADR-0.0.21 promoted chores from `ops/chores/` (gzkit-repo-only scratch directory) to a first-class `.gzkit/` surface with:

- **Two-surface layout:** canonical source ships in `src/gzkit/chores/` inside the wheel; consumer project overlay lives in `.gzkit/chores/`.
- **Project-first → package-fallback resolution:** resolvers consult `importlib.resources` as fallback rather than relying on `Path.cwd()` alone.
- **Wheel include extended:** `pyproject.toml` `[tool.hatch.build.targets.wheel]` gained `src/gzkit/chores/**/*.md`, `*.json`, `README.md`, `registry.json` entries.
- **Doctor repair surface:** `gz chores doctor` detects and repairs missing or stale project-overlay artifacts.
- **Layout validator:** `gz validate --chores-layout` prevents regression to `ops/chores/` placement.

This is exactly the T0-compliant pattern: `pip install py-gzkit && gz init && gz chores list` returns the canonical chore set with zero manual intervention.

### Why Skills and Rules Missed It

Chores were promoted *after* the self-hosting blindness was already entrenched and the ADR's author recognized that chores would have downstream consumers. Skills and rules were promoted *earlier*, when there were no external consumers to expose the packaging gap. The `scaffold_core_skills` stub-rendering path was already there; the ADR that promoted skills did not add wheel include entries because there were no external consumers asking for them yet.

The result: chores and skills/rules landed in the same repo, governed by the same CLI, but with different packaging contracts — one T0-compliant, two not. No doctrine existed to catch the gap because T0 had not been named yet.

### Why This Is the "T0 Was Operationally True Before It Was Named" Example

ADR-0.0.21's author applied T0 reasoning without the T0 label. The ADR's intent ("a downstream `pip install py-gzkit` yields a working CLI with zero chores" is a distribution bug) and anti-patterns ("ship-only-with-the-repo" and "cwd-bound resolution") are exact applications of T0. The pattern was proven at the chores surface before the invariant was written down.

Future canonical-surface promotions can read ADR-0.0.21 as a concrete template for what T0-compliant promotion looks like. The four elements — two-surface layout, project-first/package-fallback, wheel include extension, doctor repair surface — are the pattern any new surface must apply to satisfy T0.

---

## Is This a T0 Breach?

Apply this decision tree when promoting a new canonical surface or extending an existing one. A "No" at any branch is a T0 breach requiring the named recovery action before the surface can ship.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  Canonical surface being promoted or extended                           │
│  (skill kind, rule family, hook surface, persona, template, chore, …)  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 1. Does it ship in the wheel? │
              │    (check pyproject.toml      │
              │     [tool.hatch.build]        │
              │     include entries)          │
              └───────────┬──────────────────┘
                          │
           ┌──────────────┴──────────────┐
          YES                            NO
           │                             │
           │                    Recovery: extend
           │                    [tool.hatch.build.targets.wheel]
           │                    include: to cover the new surface
           │                    directory (follow ADR-0.0.21 pattern)
           │
           ▼
┌──────────────────────────────────────────┐
│ 2. Does `pip install py-gzkit &&        │
│    gz init` reproduce it?               │
│    (check scaffolder: does init_cmd.py  │
│     call scaffold_core_<surface>()?    │
│     does it copy canonical content,    │
│     not render stubs?)                 │
└───────────┬──────────────────────────────┘
            │
 ┌──────────┴──────────┐
YES                    NO
 │                     │
 │            Recovery: add scaffold_core_<surface>()
 │            to init_cmd._scaffold_project_skeleton
 │            (fresh init) and _repair_missing_artifacts
 │            (re-run repair). Implement project-first →
 │            package-fallback resolution via importlib.resources
 │            (ADR-0.0.21 OBPI-0.0.21-04 pattern).
 │
 ▼
┌──────────────────────────────────────────┐
│ 3. Does the baseline manifest list it?  │
│    (check data/distribution_baseline_   │
│     manifest.json — the frozen          │
│     byte-equivalence reference)         │
└───────────┬──────────────────────────────┘
            │
 ┌──────────┴──────────┐
YES                    NO
 │                     │
 │            Recovery: extend the baseline manifest
 │            to include the new surface entries;
 │            re-run `gz validate --distribution`
 │            to confirm the wheel-installed output
 │            matches the updated baseline.
 │
 ▼
┌──────────────────────────────────────────┐
│ 4. Does `gz validate --distribution`    │
│    cover it?                            │
│    (check that the T0 validator scope   │
│     enumerates this surface and exits 3 │
│     when the surface is unshipped)      │
└───────────┬──────────────────────────────┘
            │
 ┌──────────┴──────────┐
YES                    NO
 │                     │
 │            Recovery: extend T0 validator scope
 │            (follow OBPI-0.0.32-07 pattern);
 │            if ADR-0.0.32 is already closed,
 │            file a follow-up GHI labeled `defect`
 │            with surface name + missing scope.
 │
 ▼
T0 PASS — surface promotion is distribution-compliant.
```

### Decision Tree Quick Reference

| Branch | Check | Recovery if No |
|--------|-------|----------------|
| 1 | Surface ships in wheel | Extend `pyproject.toml` include entries |
| 2 | `gz init` reproduces the surface (canonical content, not stubs) | Add/fix `scaffold_core_<surface>()` with importlib.resources |
| 3 | Baseline manifest lists it | Extend `data/distribution_baseline_manifest.json` |
| 4 | `gz validate --distribution` covers it | Extend validator scope; file GHI if ADR-0.0.32 closed |

---

## Related

- [trust-doctrine.md § T0 — Distribution Invariant](trust-doctrine.md#t0-distribution-invariant) — the authoritative doctrine this catalog applies
- [ADR-0.0.31 (distribution invariant doctrine)](../design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md) — the foundation ADR that authored the T0 invariant
- [ADR-0.0.32 (canonical surface packaging)](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md) — the mechanical enforcement surface; each recovery action above traces to an OBPI in ADR-0.0.32
- [ADR-0.0.21 (chores-as-gzkit-surface)](../design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md) — the canonical T0-compliant promotion precedent
- [GHI #318](https://github.com/tvproductions/gzkit/issues/318) — the origin defect that surfaced the self-hosting blindness and triggered T0 doctrine
