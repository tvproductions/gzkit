---
mode: CREATE
adr_id: ADR-0.0.73
branch: main
timestamp: "2026-06-19T19:09:09Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260619T153352Z-sanity-reduction-618-boundary.md
last_commit_sha: dec9497d
---

<!-- Handoff document for ADR-0.0.73 / Build-to-1.0 Magna Carta — created by claude-code at 2026-06-19T19:09:09Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** clearance to unilaterally execute that plan. On resume — at
**every** freshness level, Fresh included — you MUST: (1) present the advised next
steps and current state to the operator; (2) obtain explicit operator
authorization before any file mutation or `gz` ceremony; (3) treat the
human-as-final-witness doctrine as binding from the first step. You advise; the
operator rules; you note variance and stop.

## Current State Summary

Floor is green (`uv run gz check` passing) and `main` is synced at commit
`dec9497d`. This session advanced the Magna Carta Sanity-Reduction track,
landing two named cuts end-to-end (guard-test-first, parity-proven, green-gated):

- **#617 (CLI handler-manifest collapse) — LANDED + CLOSED** (commit `664417ca`).
  The three byte-identical `_lazy` resolvers + `_HANDLER_CACHE` and their
  per-group `_LAZY_HANDLERS` slices across `parser_governance` / `parser_maintenance`
  / `parser_artifacts` collapsed into one shared
  `src/gzkit/cli/parser_handler_manifest.py` (93 entries; verified zero
  cross-manifest key collisions). Fenced by a new resolution guard
  `tests/cli/test_handler_manifest_resolves.py` (both directions: every manifest
  entry resolves to a callable, every `_lazy`/`_arb` call-site names a known key),
  proven non-tautological against planted defects.
- **#631 (eval-scorer false-RED lexicon) — LANDED + CLOSED** (commits `756786a6`
  fix + `dec9497d` cleanup). `_score_architectural_alignment` widened to the
  canonical foundation-ADR shape; then re-scored four ADRs and retired four
  justify band-aids the fix made unnecessary.

`#618 step 2` (the `VALIDATOR_REGISTRY` collapse, commit `ae82f9ac`) was already
landed before this session, but GHI #618 stays OPEN with residual scope (below).

## Important Context

- The Magna Carta `docs/governance/build-to-1.0-campaign-2026-06-10.md` GOVERNS;
  its Progress note (updated this session, synced at `dec9497d`) is the
  authoritative resume record — read it first. The Sanity-Reduction track runs
  alongside the topmost spine (ADR-0.0.73), never preempting it.
- **#631 scope correction (key discovery):** the eight false-RED justify
  band-aids had THREE root causes, not one. The `_score_architectural_alignment`
  lexicon fix cleared only the arch-alignment family (ADR-0.0.26 / 0.0.51 / 0.0.56)
  plus one stale eval (ADR-0.0.64). The other two causes are routed, not fixed —
  see Pending Work.
- **#618 is NOT fully discharged** despite step-2's `VALIDATOR_REGISTRY` landing:
  the collapse folded the internal enumerations only. The 78-param `validate()`
  signature, the `p_validate` forwarding lambda, and the ~80 `add_argument` parser
  flags + `_build_check_steps` are still hand-synced (not registry-derived). The
  GHI's "Expected" (all surfaces derived from the registry) is unmet; the GHI
  scope hint calls the remainder its own ADR/OBPI.
- **Coupled-surface lesson (#617):** the doc-coverage scanner
  (`gzkit.doc_coverage.scanner`) AST-globs `src/gzkit/cli/parser_*.py` for
  `_LAZY_HANDLERS` to resolve handler docstrings. Naming the shared module
  `parser_handler_manifest.py` kept that glob working with zero scanner edits;
  the sensitivity test's `_HANDLER_CACHE` injection was repointed to the shared
  module. `parser_arb` was deliberately excluded (its `_arb` hardcodes the module
  and ignores its manifest — different shape).
- **Gotcha:** `gz adr evaluate` rewrites `docs/design/adr/AGENTS.md` with
  CRLF-only churn (no content change). Discard it after re-scoring with
  `git checkout docs/design/adr/AGENTS.md`.

## Decisions Made

- **Decision:** #617 landed the full reductive collapse now, waiving the GHI's
  Phase-I deferral.
  **Rationale:** operator explicitly directed full collapse; additive guard +
  reductive collapse done together, guard-test-first so the collapse is provably
  equivalence-preserving (the guard stayed green across it).
  **Alternatives rejected:** additive-guard-only (leaves the duplication);
  deferring the collapse to post-1.0 (operator overrode the deferral).
- **Decision:** the shared module is named `parser_handler_manifest.py`.
  **Rationale:** matches the scanner's `parser_*.py` glob, preserving docstring
  resolution with no scanner change.
  **Alternatives rejected:** a non-`parser_*` name (breaks doc-coverage silently).
- **Decision:** #631 scoped to `_score_architectural_alignment` only.
  **Rationale:** the GHI pinpoints lines 356/361; the Feature Checklist false-RED
  is a different dimension owned by ADR-0.0.73 item 7 (evaluator truth-binding).
  **Alternatives rejected:** also rewriting `_score_feature_checklist` (overlaps
  ADR-0.0.73 forward work, scope creep).
- **Decision:** pre-existing control-surface drift FLAGGED, not auto-synced.
  **Rationale:** `gz validate --surfaces` and `gz agent sync --dry-run` disagree
  on which surfaces drifted; a directly-edited mirror needs the version-marker
  conflict-resolution per `.claude/rules/skill-surface-sync.md`, not a clobbering
  re-sync.
  **Alternatives rejected:** blind `gz agent sync control-surfaces` (could clobber
  an intentional mirror edit and mask the real cause).

## Immediate Next Steps

ADVISORY ONLY — present these and await operator authorization before acting.

1. Pull Sanity-Reduction cut **(d): the waiver/grandfather/baseline stack
   review** — inventory the registered waiver/grandfather/baseline surfaces (e.g.
   `data/behave_coverage_waivers.json`, `data/waiver_ratchet_registry.json`,
   `data/fidelity_presence_grandfather.json`, the tautological and sensitivity
   baselines), collapse what proves redundant, keep what each mechanism uniquely
   earns. Last named cut; feeds Phase-I.
2. Triage the **phantom-ADR orphaned evals**: ADR-0.47.0 / 0.49.0 / 0.50.0 carry
   stale low-score `adr-evaluation` ledger events and justify band-aids but no
   resolvable on-disk package. Decide repudiate-the-evals vs resolve-the-package-
   lifecycle (demoted or renamed?); file a GHI via `/ghi-author` if it warrants
   tracking.
3. Investigate the **pre-existing control-surface drift** before any
   `gz agent sync`: `gz validate --surfaces` flags `security-sensitivity.md` plus
   the obpi-completion hook; `gz agent sync --dry-run` flags `skill-surface-sync.md`
   plus the control-surface and staleness hooks. Determine whether a mirror was
   edited directly (version-marker check) before syncing.
4. (Campaign spine) The sequenced topmost remains **ADR-0.0.73 QC-binding
   meta-audit (0/7)** — the Sanity-Reduction cuts are the parallel track, not a
   substitute for it.

## Pending Work / Open Loops

- **GHI #618 OPEN** — `VALIDATOR_REGISTRY` landed the internal enumerations
  (commit `ae82f9ac`); residual is the 78-param signature, the forwarding lambda,
  and the ~80 parser flags + `_build_check_steps` (not registry-derived). The
  GHI's "Expected" is unmet; its own ADR/OBPI per the scope hint.
- **GHI #632 OPEN** — tautological-test-audit brittleness (E.5 drainage),
  unchanged this session.
- **ADR-0.0.73 item 7 (evaluator truth-binding)** owns the
  `_score_feature_checklist` false-RED (ADR-0.0.73's own Feature Checklist scores
  1.0 because the scorer demands a literal `OBPI-` prefix + uniform granularity);
  not yet built. The ADR-0.0.73 justify band-aid is retained meanwhile.
- **Phantom-ADR orphaned evals** (0.47.0 / 0.49.0 / 0.50.0) — three justify
  band-aids stuck (cannot re-score a non-existent package); untracked, needs
  triage (step 2).
- **Pre-existing control-surface drift** — untracked; needs cause investigation
  before sync (step 3).

## Verification Checklist

- [ ] `git branch --show-current` is `main`; HEAD at or ahead of `dec9497d`, synced.
- [ ] `uv run gz check` green before opening the next cut (green-first).
- [ ] `uv run -m unittest tests.cli.test_handler_manifest_resolves` passes (#617 guard).
- [ ] `uv run -m unittest tests.test_adr_eval` passes (#631 guard + scorer fixtures).
- [ ] `uv run gz validate --evaluation-justify-binding` exits 0 (4 band-aids retired; 4 remain valid).
- [ ] Confirm GHI #618 and #632 still OPEN; #617 and #631 CLOSED.
- [ ] Re-read the campaign Progress note (synced at `dec9497d`) before pulling the next cut.

## Evidence / Artifacts

- `src/gzkit/cli/parser_handler_manifest.py` — the single shared `_lazy` resolver + merged 93-entry manifest (#617)
- `tests/cli/test_handler_manifest_resolves.py` — the #617 resolution guard (both directions, non-tautological)
- `src/gzkit/doc_coverage/scanner.py` — the coupled doc-coverage scanner kept coherent by the `parser_*` naming (#617)
- `src/gzkit/adr_eval_scoring.py` — `_score_architectural_alignment` widened to the foundation-ADR shape (#631)
- `tests/test_adr_eval.py` — `TestArchitecturalAlignmentFalseRed` guard + strong/weak fixtures (#631)
- `src/gzkit/governance/trust_audits/evaluation_justify_binding.py` — the gate the #631 band-aids fed
- `src/gzkit/commands/validate_cmd.py` — the #618 `VALIDATOR_REGISTRY` (residual scope noted in Pending Work)
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta; Progress note updated this session
- `.gzkit/handoffs/20260619T153352Z-sanity-reduction-618-boundary.md` — predecessor handoff

## Environment State

- Python 3.13 with uv; Windows primary. `uv run -m unittest -q` runs ~265s (6329
  tests). `gz adr evaluate` touches `docs/design/adr/AGENTS.md` with CRLF-only
  churn — discard after re-scoring.
