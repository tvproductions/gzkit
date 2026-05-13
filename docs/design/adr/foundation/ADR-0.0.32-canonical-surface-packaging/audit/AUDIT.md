# AUDIT — ADR-0.0.32 (canonical-surface-packaging)

**Date:** 2026-05-13
**Auditor:** main-session agent (subagent invocation)
**Operator of record:** g0
**Lane / Kind / Sensitivity:** heavy / foundation / (none)
**Audit verdict:** BLOCKED — T0 enforcement surface itself fails closed against current repo state (21 errors); shortfalls are real and not in-scope for a single audit pass.

## Layer-2 ledger verdict

```
$ uv run gz adr audit-check ADR-0.0.32
ADR audit-check: ADR-0.0.32-canonical-surface-packaging
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.32-01 .. OBPI-0.0.32-14 (all 14 attested_completed)
Advisory 8 REQ(s) without @covers traceability (non-blocking):
  - REQ-0.0.32-01-07, 02-03, 03-04, 03-05, 09-03, 09-04, 11-06, 11-08
Coverage: 120/128 REQs covered (93.8%)
```

Layer 2 PASS — every linked OBPI has a recorded Gate-5 attestation receipt in the ledger. Per skill § Layer 2 Trust Model, this skips re-verification of OBPI-level evidence. Advisory REQ-coverage gaps recorded for future per-OBPI remediation; per skill § Step 2 diagnosis rule no cosmetic `@covers` backfill applied.

## Feature Demonstration (Step 3 — MANDATORY)

The ADR delivered five operator-visible capabilities. Each is exercised below with the live `gz` CLI command and representative output captured under `proofs/`.

### Capability 1 — Module-to-package API preservation

**Claim (C7):** `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` and `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserve all public-symbol re-exports.

```
$ uv run python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills; \
                    from gzkit.rules import CORE_RULES, scaffold_core_rules; \
                    print('skills:', len(CORE_SKILLS), 'rules:', len(CORE_RULES))"
skills: 11 rules: 19
```

(Proof: `proofs/module-package-imports.txt`.)

**Value:** Existing call sites (`from gzkit.skills import X`, `from gzkit.rules import X`) continue resolving after the module-to-package conversion. The dual-surface refactor did not break the public Python API; ~25 internal call sites and any adopter-side imports keep working.

### Capability 2 — `gz init --update` three-state refresh

**Claim (C3):** `gz init --update` provides version-aware refresh with IDENTICAL/STALE/EDITED three-state detection.

```
$ uv run gz init --update --dry-run
Refreshing canonical surfaces from installed wheel...
Dry run: no files will be written.
  IDENTICAL: 218 STALE: 3 EDITED: 0

Would refresh (STALE):
  - .gzkit/chores/README.md
  - .gzkit/chores/AGENTS.md
  - .gzkit/templates/skills/git-sync/SKILL.md
```

(Proof: `proofs/init-update-dry-run.txt`.)

**Value:** Adopters can refresh their canonical surfaces from a newer gzkit wheel without losing local edits. The three-state report makes the diff between wheel content and project content visible before any write; `--dry-run` gates the actual mutation.

### Capability 3 — `gz upgrade` adopter-side surface-only refresh

**Claim (C4):** `gz upgrade` is the adopter-side surface-only refresh subcommand, distinct from `gz init --update`.

```
$ uv run gz upgrade --help
usage: gz upgrade [-h] [--surface SURFACES] [--force] [--dry-run] ...

Surface-only refresh of .gzkit/<surface>/ from the installed wheel's package data.
Simpler than gz init --update: no manifest mutation, no scaffolder hooks, no agent sync.
Use --surface to refresh a subset of surfaces; use --force to overwrite operator-edited files.

  --surface SURFACES   Surfaces to refresh: skills,rules,templates,personas,hooks. Default: all.
  --force              Override safety checks
  --dry-run            Show planned actions without executing
```

(Proof: `proofs/upgrade-help.txt`.)

**Value:** Adopters who only want to pull, say, the latest skill catalogue without re-running the whole `gz init --update` ceremony can scope the refresh with `--surface skills`. Distinct from the project-refresh ceremony, which mutates the manifest and runs scaffolders.

### Capability 4 — Unified `gz agent sync control-surfaces`

**Claim (C2):** A single `gz agent sync control-surfaces` invocation propagates `.gzkit/<surface>/` to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy) AND `.[vendor]/<surface>/` (vendor mirrors).

```
$ uv run gz agent sync control-surfaces
... (full transcript in proofs/agent-sync.txt) ...
  Updated AGENTS.md
  Updated CLAUDE.md
  Updated docs/AGENTS.md
  Updated src/gzkit/AGENTS.md
  ... (instruction mirrors, persona mirrors, rule mirrors, skill mirrors, chore mirrors)
Sync complete.
```

(Proof: `proofs/agent-sync.txt`.)

**Value:** Before this ADR, the `.gzkit/ → src/gzkit/` arrow was manual (`cp` or `git mv`) and the `.gzkit/ → .[vendor]/` arrow ran separately. Now one invocation closes both arrows from the canonical source-of-truth. The byte-parity test fails closed on any forgotten sync run, so the sync invariant is mechanical — no agent goodwill required.

### Capability 5 — T0 distribution-invariant fail-closed enforcement

**Claim (C5):** `gz validate --distribution` enforces wheel-shipping discipline fail-closed (exit 3 on any drift).

```
$ uv run gz validate --distribution
Validated: manifest, surfaces, ledger, instructions, briefs, documents,
personas, version, taxonomy

❌ Validation failed with 21 error(s):
   →  src/gzkit/rules/_scaffolder.py
    ON_DISK_NOT_INCLUDED: ...not covered by any include glob in [tool.hatch.build.targets.wheel] include.
   →  src/gzkit/rules/complexity-thresholds.json
    ON_DISK_NOT_INCLUDED: ...not covered by any include glob in ...
   →  src/gzkit/skills/format/SKILL.md  (and 17 more SKILL.md cases)
    ON_DISK_NOT_BASELINE: ...exists on disk and is covered by a wheel include glob
                          but is NOT in the baseline manifest.
   →  src/gzkit/templates/skills/git-sync/SKILL.md
    ON_DISK_NOT_BASELINE: ...
EXIT=3
```

(Proof: `proofs/validate-distribution.txt`.)

**Value (mechanism works as designed):** the validator IS fail-closed against real drift. Exit 3, 21 categorized errors, named resolution paths. This is the T0 enforcement surface this ADR shipped doing its job — catching drift between on-disk canonical content, wheel include globs, and the frozen baseline manifest.

**Value (shortfall surfaced):** the very fact that the validator returns 21 errors against the current repo head means the *repo state* has drifted past the baseline OBPI-06 froze. Two distinct drift classes are present (see Shortfalls below), and the validator caught both — exactly the behaviour the ADR promised.

## Execution log

| Check | Result | Notes |
|---|---|---|
| `gz adr audit-check ADR-0.0.32` | ✓ PASS | 14/14 OBPIs attested_completed; 8 advisory REQ-coverage gaps non-blocking |
| `gz validate --distribution` | ✗ FAIL (exit 3, 21 errors) | Mechanism enforces fail-closed correctly; current repo state has drifted past baseline |
| `gz init --update --dry-run` | ✓ PASS | Three-state report works; 218 IDENTICAL / 3 STALE / 0 EDITED |
| `gz upgrade --help` | ✓ PASS | Manpage surface present with `--surface`, `--force`, `--dry-run` |
| `gz agent sync control-surfaces` | ✓ PASS | Single invocation propagates to all derived surfaces; idempotent on re-run |
| `gz lint` | ✓ PASS | All checks passed |
| `uv run -m unittest` | ✓ PASS | 4967 tests, 1 skipped, 0 failed |
| Module-to-package imports | ✓ PASS | `from gzkit.skills import …` and `from gzkit.rules import …` both resolve |
| T0 smoke test exists | ✓ PASS | `features/distribution_invariant.feature` + `features/steps/distribution_invariant_steps.py` present |
| 1:1 checklist↔OBPI sync | ✓ FIXED in this audit | 13 OBPI checklist items flipped from `[ ]` to `[x]` to match ledger truth |
| Frontmatter status | ✓ FIXED in this audit | `status: Draft` → `status: Completed` to match ledger truth |

## Evidence index

| Artifact | Path |
|---|---|
| Audit plan | `audit/AUDIT_PLAN.md` |
| Distribution validation transcript | `audit/proofs/validate-distribution.txt` |
| Init-update dry-run transcript | `audit/proofs/init-update-dry-run.txt` |
| Upgrade help surface | `audit/proofs/upgrade-help.txt` |
| Agent sync transcript | `audit/proofs/agent-sync.txt` |
| Module-package imports proof | `audit/proofs/module-package-imports.txt` |
| ADR prose | `ADR-0.0.32-canonical-surface-packaging.md` |
| OBPI briefs | `obpis/OBPI-0.0.32-01-..-14.md` |
| Ledger | `.gzkit/ledger.jsonl` |

## Shortfalls identified

### S1 — Distribution baseline manifest is stale (BLOCKING)

`data/distribution_baseline_manifest.json` carries 52 skills + 19 rules + 6 personas + 11 templates + 0 chores; on-disk under `src/gzkit/<surface>/` there are 70 skills + 20 rules (incl. `*.json`) + 6 personas + 12 templates + 158 chore files. 19 `ON_DISK_NOT_BASELINE` errors flag the drift.

- **Severity:** Blocking — `gz validate --distribution` is part of the ADR's delivered enforcement surface; its current fail-closed return prevents marking the ADR VALIDATED.
- **Root cause:** OBPI-06 froze the baseline at one moment in time; subsequent skill/rule/template additions did not regenerate it. No `gz` regenerator subcommand exists for the baseline.
- **Proposed fix scope:** (a) author a baseline regenerator (`gz validate --distribution --regenerate-baseline` or similar) so the manifest stays current; (b) regenerate the manifest against current on-disk state; (c) re-run `gz validate --distribution` to confirm exit 0.
- **Routing:** OBPI ceremony, not direct fix — touches data semantics, may require a new CLI flag and tests, crosses validator + data + manpage boundaries.

### S2 — Package-only files inside canonical surface roots (BLOCKING)

`src/gzkit/rules/_scaffolder.py` (private Python helper) and `src/gzkit/rules/complexity-thresholds.json` (runtime data) live under the rules surface root but are not covered by the wheel `include:` globs (which target `*.md` only). 2 `ON_DISK_NOT_INCLUDED` errors flag this.

- **Severity:** Blocking — same fail-closed prevention as S1.
- **Root cause:** The `src/gzkit/rules/` surface mixes canonical authored content (`*.md`) with package-only Python/data. The chores class-classifier doctrine (`.gzkit/rules/skill-surface-sync.md` § Chores class-classifier; helper at `src/gzkit/chores/__init__.py::_classify_chore_file`) handles this for chores but has not been extended to rules.
- **Proposed fix scope:** (a) extend `pyproject.toml [tool.hatch.build.targets.wheel] include:` to ship `src/gzkit/rules/**/*.json` (since `complexity-thresholds.json` is runtime data per `src/gzkit/complexity/thresholds.py`); (b) either extend the include block for `_scaffolder.py` OR extend the distribution validator to honor the class-classifier doctrine across non-chore surfaces; (c) regenerate baseline (folded into S1's fix).
- **Routing:** OBPI ceremony — same boundary-crossing as S1.

### S3 — Advisory REQ-coverage gaps (NON-BLOCKING, documented)

`audit-check` flagged 8 REQs without `@covers` traceability across OBPI-01/02/03/09/11:
`REQ-0.0.32-01-07`, `REQ-0.0.32-02-03`, `REQ-0.0.32-03-04`, `REQ-0.0.32-03-05`, `REQ-0.0.32-09-03`, `REQ-0.0.32-09-04`, `REQ-0.0.32-11-06`, `REQ-0.0.32-11-08`.

- **Severity:** Non-blocking (CLI explicitly labels as advisory).
- **Routing per skill § Step 2 diagnosis rule:** No cosmetic `@covers` backfill applied. Each REQ should be re-derived from its OBPI brief and either backed by a semantically-grounded test (case a) or removed if the assertion drifted from REQ semantics (case b). Diagnosis deferred to a follow-on OBPI/GHI under each REQ's parent.

### S4 — Doc-drift fixed in flight (non-blocking)

- ADR frontmatter `status: Draft` did not match the ledger truth (all 14 OBPIs attested_completed). Updated to `Completed` in this audit pass.
- 13 of 14 OBPI checklist items were left `[ ]` despite the ledger marking them `attested_completed`. Per AGENTS.md § OBPI Decomposition Mandate "1:1 Synchronization Mandate", flipped to `[x]` in this audit pass.

## Remediation

S1 and S2 are blocking. Together they describe one coherent gap: the T0 enforcement mechanism shipped under OBPI-07 lacks a regenerator companion (S1) and a class-classifier extension for non-chore surfaces (S2). Both require code changes, manpage changes, and test coverage; both cross the validator-vs-data-vs-CLI boundary. Per AGENTS.md § Defect-fix routing, this exceeds the direct-fix thresholds — file a GHI and pause the audit ceremony.

**Recommended action (parent agent):** file a GHI titled "ADR-0.0.32 T0 baseline regenerator + class-classifier extension to rules surface" against `tvproductions/gzkit`. Body should describe both shortfalls together with the audit transcript path. Resume `/gz-adr-audit ADR-0.0.32` after the GHI's fix lands.

## Attestation status

**No `audit-begin` invocation.** No validated receipt emitted. Audit is BLOCKED per skill § Step 8 "Audit fails → no receipt." Lifecycle remains `Pending` (will move to `Validated` only after S1/S2 remediation + a future audit pass).

**Agent signature (audit work performed):** main-session subagent (Opus 4.7), 2026-05-13. Audit work itself is complete and reproducible; the blocking shortfalls prevent moving to VALIDATED, not from a failed audit *procedure*.
