---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-16T12:05:27Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260616T091837Z-adr-0.0.37-facade-qc-binding-meta-audit.md
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-16T12:05:27Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

Short maintenance session, all work landed on `main` and pushed. Tree is clean
and synced (`ahead=0 behind=0 diverged=False dirty=False`). Three things happened:

1. **Collapsed the feature branch to main.** The session opened on
   `fix/adr-0.0.37-real-coherence-gate` (6 commits ahead). The operator directed
   that no feature branch should have been created. The branch was squash-merged
   to `main` (commit `dbaa9b94`), and the branch was deleted locally and on
   `origin`. A blocking test (`test_gz_adr_create_version_bumped`) was fixed
   first — `_EXPECTED_VERSIONS["gz-adr-create"]` updated `6.5.0` → `6.6.0` to
   match the already-bumped skill frontmatter.

2. **Captured the no-feature-branch directive as verbatim operator canon.**
   Operator directive (verbatim): *"don't do that feature branch bullshit
   again."* Captured into the corpus source-of-truth at **invariant tier**
   (`gz content remember AGENTS.md --section operator-doctrine-verbatim-canon`,
   commit `cc80cdca`). That tripped the `rendition-freshness` and
   `rendition-floor-coherence` pre-push gates. Completed the full governed
   recompose: built claude + codex candidate renditions with the directive
   verbatim, `gz content compose` (invariant floor satisfied), recorded advisory
   QC verdicts (score 1.0, zero information loss), promoted candidates to
   committed renditions, and `gz agent sync control-surfaces` played the directive
   back into root `AGENTS.md` line 337 and mirrors (commit `f3d8f586`).

3. **git-sync clean.** Final `gz git-sync --apply` confirmed in sync.

All coherence gates green: `invariant-coherence`, `rendition-freshness`,
`rendition-floor-coherence`. The directive is now both binding canon in
`AGENTS.md` and mechanically enforced by the floor-coherence gate.

## Important Context

- **NO FEATURE BRANCHES.** Work directly on `main` and `git-sync`. This is now
  invariant-tier operator canon in `AGENTS.md` § Operator Doctrine (verbatim
  canon), line 337. Any future rendition that drops it fails the
  `rendition-floor-coherence` gate closed.
- **Rendition promotion is Gate-5 attested.** `gz content compose` only writes a
  `.candidate.md`; promoting a candidate to a committed rendition
  (`.gzkit/renditions/AGENTS.md/{claude,codex}.md`) is OBPI-22 scope and requires
  operator attestation. There is **no** CLI promote/playback verb — promotion is a
  `cp candidate → committed` then `gz agent sync control-surfaces` to play back
  into `AGENTS.md` + mirrors. The operator attested the promotion in flight by
  choosing "full verbatim canon (attested)".
- **Any corpus mutation trips `rendition-freshness`** regardless of tier — a
  `compressible` entry would have forced the same recompose. Tier choice does not
  let you skip recompose; it only governs whether the *floor-coherence* gate fires.
- **Handoff storage split-brain (GHI #529) is live.** Doctrine names
  `.gzkit/handoffs/` canonical; the orientation script scans both that and
  ADR-package `handoffs/` dirs. The programmatic handoff API
  (`create_handoff`/`resume_handoff`) is **NOT IMPLEMENTED** — it is OBPI-02 of
  `ADR-pool.handoff-system-consolidation`. CREATE/RESUME are manual procedures
  gated by `gzkit.handoff_validation.validate_handoff_document`.

## Decisions Made

- **Decision:** Land the no-feature-branch directive as invariant-tier verbatim
  canon (not a lighter `agent-insights.jsonl` course-correction record).
  **Rationale:** Operator explicitly chose "full verbatim canon (attested)" when
  presented the two options; a standing behavioral directive belongs in the
  durable corpus + AGENTS.md, mechanically enforced.
  **Alternatives rejected:** (a) insights-only record (Behavior Rule 11 channel) —
  lighter, no recompose, but not surfaced in AGENTS.md at session start;
  (b) `git reset` the corpus commit — rejected because a `corpus_entry_appended`
  ledger event was already written, and reverting it via git is editing the
  ledger by the back door (AGENTS.md § Never #2).
- **Decision:** Squash-merge the branch to main rather than rebase/replay.
  **Rationale:** Operator wanted the branch gone and the work consolidated on main;
  squash gives one coherent commit. **Alternatives rejected:** fast-forward merge
  (would preserve the 6-commit branch history the operator did not want).
- **Decision:** Fix the failing `gz-adr-create` version test by updating the
  expected value to `6.6.0`. **Rationale:** The skill frontmatter was legitimately
  bumped to 6.6.0; the test's `_EXPECTED_VERSIONS` constant had simply not been
  updated in lockstep. **Alternatives rejected:** reverting the skill version
  (would undo a real, intended bump).

## Immediate Next Steps

<!-- ADVISORY ONLY — present for operator review; do not execute without authorization. -->

1. **Resume the Magna Carta campaign.** Per session orientation, the campaign
   (`docs/governance/build-to-1.0-campaign-2026-06-10.md`, 7/38 done) governs what
   is pulled next. Topmost unchecked items whose gate is met:
   `0.2 Source + Config-First AST guard` (`governance/vocabulary.py`),
   `0.3 Bind the models` (`core/models.py` + `brief_structure.py`),
   `0.4 Bind the schemas`. Confirm with operator which to pull.
2. **ADR-0.0.73 (verification-layer-binding-audit) is booked with 7 OBPIs** and
   seated in the campaign — design DONE + approved per the prior handoff. Confirm
   with operator whether to begin OBPI-0.0.73-01
   (`qc-step-registry-and-classifier`) or defer to the campaign sequencing.
3. Consider whether `ADR-pool.handoff-system-consolidation` (GHI #529) warrants
   promotion — the handoff programmatic API and storage split-brain remain
   unresolved and surfaced again this session.

## Pending Work / Open Loops

- **GHI #529 — handoff system consolidation:** programmatic CREATE/RESUME API
  not implemented; `.gzkit/handoffs/` vs ADR-package `handoffs/` storage
  split-brain unresolved. Pool ADR awaiting promotion decision.
- **Advisory drift (non-blocking):** `gz check` reports 1860 unlinked specs
  (REQs with no test) and 10 orphan tests. Advisory only; does not affect exit
  code. `gz drift` for the per-finding list.
- **Flag health:** `ops.product_proof` flag approaching deadline (within 14 days).
- **ADR-0.0.73 OBPIs (7) unimplemented** — booked but not started.

## Verification Checklist

- [ ] `git branch --show-current` → `main` (NOT a feature branch)
- [ ] `git status` clean; `uv run gz git-sync` shows `ahead=0 behind=0`
- [ ] `uv run gz validate --invariant-coherence --rendition-freshness --rendition-floor-coherence` → all pass
- [ ] `grep -n "Never create feature branches" AGENTS.md` → line 337 present verbatim
- [ ] `uv run -m unittest -q` passes (last full run: 6176 tests, 0 failures after the version-test fix)
- [ ] `uv run gz status` for current gate/lifecycle state before pulling new work

## Evidence / Artifacts

- `AGENTS.md` — no-feature-branch directive verbatim at line 337 (§ Operator Doctrine)
- `.gzkit/corpus/AGENTS.md.jsonl` — invariant-tier corpus entry (source of truth)
- `.gzkit/renditions/AGENTS.md/claude.md` — recomposed committed rendition with directive
- `.gzkit/renditions/AGENTS.md/codex.md` — recomposed committed rendition with directive
- `tests/governance/test_foundation_invariance_skill_enrichment.py` — `_EXPECTED_VERSIONS` fix (6.5.0 → 6.6.0)
- `.gzkit/handoffs/20260616T091837Z-adr-0.0.37-facade-qc-binding-meta-audit.md` — predecessor handoff (ADR-0.0.73 design lock)

## Environment State

- Branch: `main` (feature branch `fix/adr-0.0.37-real-coherence-gate` deleted local + remote)
- HEAD: `f3d8f586`; in sync with `origin/main`
- Python 3.13.14 (uv-managed); platform darwin
- Pre-push gate: full `gz check` (32 steps) green on the final push
