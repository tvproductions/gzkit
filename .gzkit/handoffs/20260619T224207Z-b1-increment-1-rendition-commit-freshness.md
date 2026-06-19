---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-19T22:42:07Z"
agent: claude-code
obpi_id: OBPI-0.0.37-22
session_id:
continues_from: .gzkit/handoffs/20260619T201319Z-adr-0.0.73-complete-reconciled-b1-next-boundary.md
last_commit_sha: c070f28a
---

<!-- Handoff document for ADR-0.0.37 / OBPI-0.0.37-22 — created by claude-code at 2026-06-19T22:42:07Z -->

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

This session pulled the Magna Carta topmost — **B.1 (ADR-0.0.37 real corpus
rebuild)** — and landed **Increment 1** under operator-approved plan. Branch is
`main`, synced to `origin/main` at commit `c070f28a` (ahead=0, behind=0). No OBPI
lock was claimed this session (this is a session-boundary handoff, not a
lock-release register entry).

**OBPI-0.0.37-22's mechanism was genuinely re-built** (it was repudiated
2026-06-16 for `model-induced-fabrication`). Two commits landed:

- `2427d78b` — the mechanism (staged warn→fail, OBPI-0.0.41 precedent):
  operator-attested `gz content commit` candidate→committed promotion (the missing
  REQ-22-01 caller for `save_rendition` — renditions had been hand-placed); corpus
  content-fingerprint (`sha256` of canonical `Corpus.dumps()`, cross-platform
  stable) + frozen `RenditionProvenance` sidecar; the content-based
  `--rendition-freshness` gate that kills the mtime tautology; the
  `rendition_committed` ledger event; REQ-0.0.37-22-07; docs + BDD; and the two
  coupled surfaces (ADR-0.0.73 QC-binding negative control + the content-surface
  lock test).
- `c070f28a` — operator-authorized `gz agent sync control-surfaces` clearing the
  pre-existing `--surfaces` drift (a benign Windows working-tree CRLF artifact —
  see Important Context).

**OBPI-0.0.37-22 remains `repudiated` BY DESIGN.** This increment built the
mechanism honestly; it did NOT re-attest. Floor is green: full suite **6350 tests
pass**; ruff + ty + xenon (C/C/C) + interrogate (100%); `gz cli audit` 109/109;
the CMS validators + `--commit-trailers` + `--surfaces` all exit 0.

## Important Context

- **The deeper truth that scopes Increment 2:** the corpus
  (`.gzkit/corpus/AGENTS.md.jsonl`) holds **9 entries / 6.3 KB** while `AGENTS.md`
  is ~30 KB. The floor gate checks invariant *presence*, not *derivation* — so **no
  committed rendition is yet genuinely "the corpus played back"** (~24 KB of
  AGENTS.md has no corpus provenance). Enriching the corpus is the heart of B.1 and
  is a separate lineage (OBPI-19 capture), deliberately NOT done in Increment 1.
- **The staging flag is the resumption pivot.** `_FRESHNESS_FAIL_CLOSED = False`
  in `src/gzkit/governance/trust_audits/rendition_freshness.py` keeps the gate in
  WARN mode (drift prints a stderr warning, exits 0, no ledger event — so
  `gz check` stays green). Increment 2 flips it to `True` (drift → exit 3 +
  `composition_drift_detected`). Both modes are unit-tested now via the
  `fail_closed=` keyword.
- **Handoff Next Step 4 (predecessor) is EXPLAINED, not just patched.** The
  `--surfaces` red was a Windows working-tree CRLF artifact: `--surfaces` reads
  working-tree bytes, Windows checks out CRLF, the renderer emits LF. The committed
  state was always LF-correct (the sync commit's only content change was the
  `agent_sync_completed` event). The `--surfaces` (1 file) vs `gz agent sync
  --dry-run` (105 paths) "disagreement" is just dry-run listing every renderable
  path vs `--surfaces` reporting genuine byte drift. Open question carried below:
  whether this recurs on a fresh Windows checkout (a `.gitattributes` concern, not
  root-caused).
- **The repudiated OBPIs are 02 / 03 / 21 / 22.** This session re-built 22's
  mechanism. 02/03 disposition is RE-POINT + re-attest (operator ruling, below); 21
  needs honest re-verification. All three remain `repudiated`.
- **`gz adr evaluate` gotcha (carried):** it rewrites `docs/design/adr/AGENTS.md`
  with CRLF-only churn; discard with `git checkout` after re-scoring.

## Decisions Made

- **Decision:** OBPIs 02/03 disposition is **re-point to the corpus mechanism +
  re-attest** (not withdraw, not rebuild-registry).
  **Rationale:** operator chose the reversible `repudiate` verb for them; the
  2026-06-03 Re-Alignment superseded the registry-projection mechanism with the
  corpus track, so their *function* (render + drift gate) is already delivered by
  OBPI-22 playback + GHI #623 floor-coherence — re-pointing makes the checklist
  honest without building a dead second mechanism.
  **Alternatives rejected:** withdraw+fold (permanent, contradicts the chosen
  `repudiate`); rebuild the `.gzkit/invariants` registry renderer (contradicts the
  Re-Alignment supersession).
- **Decision:** B.1 Increment 1 = the OBPI-22 **mechanism**, freshness gate
  **staged warn→fail** (OBPI-0.0.41 precedent).
  **Rationale:** keeps green-first while the corpus is enriched and renditions
  re-seeded; avoids both a red floor and a premature commit of un-provenanced
  renditions.
  **Alternatives rejected:** commit the current floor-valid renditions now (leaves
  ~24 KB un-provenanced — a partial facade); corpus-enrichment-first (the mechanism
  is the prerequisite to commit anything honestly).
- **Decision:** the governed commit seam is a **new `gz content commit` verb**.
  **Rationale:** operator-attested promotion (Gate 5; fail-closed on empty
  attestor/text), single-responsibility, symmetric with `compose`.
  **Alternatives rejected:** fold into `sync_agents_md` (unattested) or
  `gz governance render --commit` (re-conflates playback with commit — the exact
  facade that was repudiated).
- **Decision:** the `config/doc-coverage.json` entry for `content commit` was
  reasoned from the schema + `.claude/rules/cli.md` + the verified group-manpage
  structure, NOT by imitating `content compose`.
  **Rationale:** operator course-correction in flight (imitation is not authority);
  recorded as an `improvement` insight in `.gzkit/insights/agent-insights.jsonl`.

## Immediate Next Steps

ADVISORY ONLY — present these and await operator authorization before acting.

1. **Pull B.1 Increment 2 — corpus enrichment + attested re-seed.** Capture
   `AGENTS.md`'s real content into the corpus (OBPI-19 lineage,
   `gz content remember` per section, invariant vs compressible tiers); then run the
   genuine `gz content compose` → operator-attested `gz content commit` for the
   `claude` and `codex` renditions; then flip `_FRESHNESS_FAIL_CLOSED = True` in
   `rendition_freshness.py`; then `gz obpi complete OBPI-0.0.37-22` to clear the
   repudiation. This is the governing next pull and is LARGE — orient and plan
   before mutating.
2. **Re-point + re-attest OBPI-02 and OBPI-03** to the corpus mechanism (renderer =
   playback; drift = `--invariant-coherence` + `--rendition-floor-coherence`),
   reconciling their briefs, then re-attest to clear their repudiation.
3. **Honestly re-verify OBPI-0.0.37-21** (composer now runs + emits
   `composition_candidate_emitted`; confirm all its REQs genuinely pass) and clear
   its repudiation.
4. **Then B.2** (registry-projected <15k codex surface, closes GHI #519) and **B.3**
   (play back queued corpus entries into rendered AGENTS.md).

## Pending Work / Open Loops

- **OBPI-0.0.37-22 `repudiated`** — mechanism built this session; re-attestation is
  Increment 2 (after corpus enrichment + the fail-closed flip).
- **OBPI-0.0.37-02 / -03 / -21 still `repudiated`** — disposition decided (02/03
  re-point; 21 re-verify) but not executed.
- **Windows CRLF / `.gitattributes` question** — the `--surfaces` drift was a
  working-tree CRLF artifact; whether it recurs on a fresh Windows checkout is
  observed-but-not-root-caused (benign; no committed-state impact).
- **GHI #618 OPEN** (residual `validate()` 78-param signature) and **GHI #632 OPEN**
  (tautological-test-audit brittleness) — carried from the predecessor handoff,
  untouched this session.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; `git rev-list --left-right --count
  origin/main...HEAD` returns `0 0`; HEAD at `c070f28a`.
- [ ] OBPI-0.0.37-22 is still `repudiated` (NOT re-attested): `uv run gz obpi status
  OBPI-0.0.37-22` and the ledger `obpi_completion_repudiated` (2026-06-16) with no
  later clearing re-attestation.
- [ ] `_FRESHNESS_FAIL_CLOSED` is still `False` in
  `src/gzkit/governance/trust_audits/rendition_freshness.py` (warn-staged).
- [ ] `uv run gz validate --rendition-freshness` exits 0 (warn mode) with stderr
  recompose warnings for the two un-sidecared renditions.
- [ ] Full suite green: `uv run --with unittest-parallel unittest-parallel -t . -s
  tests`.
- [ ] Confirm GHI #618 and #632 still OPEN.

## Evidence / Artifacts

- `src/gzkit/commands/content/commit.py` — the new operator-attested `gz content commit` verb
- `src/gzkit/content/rendition_store.py` — `corpus_fingerprint`, `RenditionProvenance`, fingerprint sidecar helpers
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — content-fingerprint gate + `_FRESHNESS_FAIL_CLOSED` staging flag
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — ADR-0.0.73 QC-binding negative control updated to the fingerprint mechanism (missing-sidecar fixture, fail-closed)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-22-committed-rendition-store-deterministic-playback.md` — brief with REQ-0.0.37-22-07 + corrected freshness-mechanism annotation
- `features/rendition_playback.feature` — BDD rewritten to content semantics + a commit scenario
- `.gzkit/insights/agent-insights.jsonl` — the doc-coverage course-correction `improvement` insight
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta; B.1 line carries the repudiation/disposition prose this increment advances
- `.gzkit/handoffs/20260619T201319Z-adr-0.0.73-complete-reconciled-b1-next-boundary.md` — predecessor handoff (ADR-0.0.73 closed; B.1 next)

## Environment State

- Python 3.13 with uv; Windows primary. Full suite runs ~50s parallel
  (`unittest-parallel`, 6350 tests) / ~265s serial. The pre-commit hook runs the
  cheap gates (ruff/ty/xenon/interrogate/surface-fidelity-cheap/gitleaks); the
  full `gz check` (unittest + behave + all validators) runs at pre-push. `gz adr
  evaluate` touches `docs/design/adr/AGENTS.md` with CRLF-only churn — discard
  after re-scoring.
