---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-20T00:33:29Z"
agent: claude-code
obpi_id: OBPI-0.0.37-22
session_id:
continues_from: .gzkit/handoffs/20260619T231600Z-b1-increment-2-corpus-enrichment.md
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-20T00:33:29Z -->

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

**Register-entry facts (token-block discipline):** last commit SHA `26e09987`;
branch `main`, up to date with `origin/main`; no OBPI lock was claimed this
session (orientation reported no active locks, none claimed). Working tree is
**dirty** with two uncommitted files from this session's corpus capture:
`.gzkit/corpus/AGENTS.md.jsonl` and `.gzkit/ledger.jsonl` (the
`corpus_entry_appended` event). These are intentional and uncommitted — the next
session should decide whether to commit them (a `docs(corpus)` commit) before
other work.

This session began as a `/git-sync` and accomplished four things:

1. **git-sync**: clone was 16 commits behind `origin/main`; ran
   `gz git-sync --apply` (ff-only pull). Now at `26e09987`, clean-synced.
2. **Reviewed the prior handoff** (`continues_from`) and investigated a
   discrepancy it surfaced.
3. **Filed GHI #634** (a status-display defect — verified, see below).
4. **Captured one operator-doctrine corpus entry** (verified verbatim).

No implementation work was done on the B.1 composition itself. The session
ended with the operator directing a fresh handoff for a new session.

**OBPI-0.0.37-22 ledger truth: REPUDIATED.** The last lifecycle event for the
OBPI is `obpi_completion_repudiated` (2026-06-16T01:01:55Z, cause
`model-induced-fabrication`, attestor `g0`), which reversed the completion
receipt of 2026-06-14T14:07:50Z. B.1 Increment 2 (genuine recomposition +
re-attestation) is the pending work that would clear the repudiation.

## Important Context

**The new operator doctrine captured this session (binding, now in corpus):**
> "read all docs and all code if you are not more than 90% convinced/confident of
> a recommendation or prioritization for any design/development action. If you are
> still not sure, admit it and consult the human operator."

This entry was captured because, during this session, the agent repeatedly
presented confident design framings for the B.1 work that collapsed on the next
file read (three successive framings: "unsatisfiable fork", "expected, no
conflict", "reformatting is forced"). The doctrine is the corrective: do the
complete read-through BEFORE recommending a direction; admit uncertainty and
consult rather than vibing a plan. The resuming agent should honor this for the
B.1 thread specifically — it is not yet at the 90% bar.

**Verified facts about the CMS / AGENTS.md render path (each read from source
this session):**
- `render_agents_md` (`src/gzkit/governance/compose.py:48-69`) returns
  `load_rendition(project_root, "AGENTS.md", "claude")` bytes verbatim — it does
  NOT use any registry or template; the `invariants`/`template_root` params are
  unused. `sync_agents_md` (`src/gzkit/sync_surfaces.py:369`) writes those bytes
  to AGENTS.md. So the committed rendition IS the full AGENTS.md, 1:1.
- The committed `claude` rendition is byte-identical to AGENTS.md (29953 B) and
  is STALE: of the 44 `tier: invariant` corpus entries, only 16 appear verbatim;
  28 are absent. `codex` rendition is 9292 B (hand-compressed), 15/44 present.
- Reason for the 28 absences: the enriched corpus entries were captured as
  NORMALIZED / stripped text (markdown removed, trailing periods added, `NEVER:`
  prepended, some reworded) — they are not byte-for-byte substrings of the
  formatted AGENTS.md. The invariant-floor (`assert_invariant_verbatim` in
  `src/gzkit/content/tier_policy.py`) is a strict substring check, so a candidate
  equal to today's AGENTS.md fails on all 28 (this is what "failed twice" in the
  prior handoff actually was).
- A real Jinja2 render pipeline EXISTS and is capable of nuanced formatting:
  `src/gzkit/content/render/pipeline.py` `render(model, vendor)` renders an
  `AgentContract` model (`src/gzkit/content/models/agent_contract.py`) through
  `src/gzkit/content/templates/agentcontract/{claude,codex}.md.j2`. The
  `Pillar` model's verbatim-`lines` field is documented as "Verbatim section-body
  lines for full-fidelity capture and structural round-trip (ADR-0.0.37-13)". The AGENTS.md
  playback path does NOT currently use this pipeline — that gap is the #623 facade.
- `_FRESHNESS_FAIL_CLOSED = False` (warn mode) still, in
  `src/gzkit/governance/trust_audits/rendition_freshness.py`.

**Honest boundary of the above:** the per-file reads are verified, but the agent
did NOT complete a full end-to-end read of the CMS pipeline (corpus store →
model mapping → composer → all four gates → OBPI-22 REQs → ADR-0.0.37 body).
Per the new doctrine, the resuming agent must complete that read BEFORE
recommending a B.1 direction. Treat the "correct path" framings from this
session's conversation as UNVERIFIED hypotheses, not conclusions.

**Bash quirk (carry-over, still true):** this is a macOS (darwin) session;
working dir is the repo root; use `uv run` for all Python; never prefix
`uv run gz` with `PYTHONUTF8=1`.

## Decisions Made

- **Decision:** Captured the new operator doctrine into the corpus under section
  `operator-doctrine-verbatim-canon`, `--tier invariant`,
  `--classification Judgment`.
  **Rationale:** It is operator verbatim doctrine; that section is the home for
  operator-captured invariants emitted verbatim at every setpoint. Tier invariant
  matches the section. Judgment because the "90% / convinced" threshold is a
  judgment call, not mechanical.
  **Alternatives rejected:** `behavior-rules` section (plausible — it parallels
  Always #7 `<90% sure → ask`) was passed over but flagged to the operator as a
  recapture option if preferred; operator did not redirect.

- **Decision:** Filed GHI #634 as a NEW `defect`/`runtime` GHI rather than folding
  into #623 or #610.
  **Rationale:** It is a distinct cut — the `status` consumer of repudiation state,
  where #610 is the `complete` consumer and #623 is the root facade. Cross-linked
  a sibling comment on #610 and referenced #623/#610 in the body.
  **Alternatives rejected:** comment-only on #623 (would bury a separately-fixable
  display defect under the larger facade work).

- **Decision:** Did NOT build any B.1 candidate, did NOT compose, did NOT flip the
  freshness flag, did NOT touch OBPI-22.
  **Rationale:** The agent was not at the 90% confidence bar on the B.1 direction;
  per the just-captured doctrine, recommending or executing a direction without a
  complete read is the failure mode being corrected.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before executing. -->

1. **Decide whether to commit this session's uncommitted corpus capture.** Working
   tree carries `.gzkit/corpus/AGENTS.md.jsonl` + `.gzkit/ledger.jsonl` (the new
   operator-doctrine entry). A `docs(corpus): capture read-before-recommend
   operator doctrine` commit on `main` then `gz git-sync --apply` is the clean
   close. Confirm the section/classification choices first (see Decisions Made).

2. **Thread 1 — GHI #634 direct-fix (confident, bounded).** `status_obpi.py` and
   `ledger_semantics.py` have zero references to `obpi_completion_repudiated`, so a
   repudiated OBPI renders green "ATTESTED COMPLETED". Add a `repudiated`
   runtime-state derivation in the semantics layer and a `REPUDIATED` branch in
   `_render_obpi_runtime_state` (`src/gzkit/commands/status_obpi.py:435`). TDD:
   write a failing test that a repudiated OBPI does not render `attested_completed`.
   Routes to direct-fix per AGENTS.md § Defect-fix routing
   (`fix(status): … (GHI #634)`), close citing the SHA.

3. **Thread 2 — B.1 Increment 2 read-through (NOT yet at 90%; doctrine-gated).** Do
   the complete end-to-end read FIRST, produce a plain factual map with file:line
   citations and NO recommendation: corpus store + model mapping, `composer.py`,
   `tier_policy.py`, all four CMS gates (`rendition_freshness`,
   `rendition_floor_coherence`, `invariant_coherence`, `bullet_retention`), the
   `content/render` pipeline + `agentcontract` templates + `AgentContract` model,
   the OBPI-22 brief REQs, and the ADR-0.0.37 body. Only AFTER that map, propose a
   direction — and consult the operator on the fork (re-capture corpus at full
   fidelity + render through the existing Jinja pipeline, vs. the prior handoff's
   hand-seed-candidates plan, which this session's reads suggest is wrong but did
   NOT fully verify).

4. **Sequencing check:** confirm with the operator whether B.1 is still the active
   Magna Carta pull (orientation listed B.1 behind ADR-0.0.73; operator stated
   0.0.73 is completed this session). The campaign plan
   `docs/governance/build-to-1.0-campaign-2026-06-10.md` governs.

## Pending Work / Open Loops

- **B.1 Increment 2 is unbuilt.** Genuine recomposition of the `claude` + `codex`
  renditions to satisfy the invariant-floor, under Gate-5 attestation, then flip
  `_FRESHNESS_FAIL_CLOSED = True`, then `gz obpi complete OBPI-0.0.37-22` to clear
  the repudiation. Direction is the OPEN fork in Step 3 — do not assume the prior
  handoff's "hand-seed candidates" plan is correct.
- **GHI #634** open (status renders repudiated as ATTESTED COMPLETED) — Thread 1.
- **GHI #623** open (root: ADR-0.0.37 derivation spine is facade; 02/03/21/22
  repudiated). The B.1 work is the cure; #623 is its tracking home.
- **GHI #610** open (repudiated OBPI cannot be re-completed: brief status not
  reset). This will likely block `gz obpi complete OBPI-0.0.37-22` at the end of
  B.1 — verify before relying on the completion step.
- **Section/classification ratification** for the new corpus entry (operator may
  prefer `behavior-rules` / `Promotable`).
- **02/03 re-point + OBPI-21 re-verify** remain separate later B.1 increments
  (operator ruling, prior handoff) — NOT part of Increment 2.

## Verification Checklist

- [ ] `git rev-parse HEAD` → `26e09987…` (or later if Step 1 committed)
- [ ] `git branch --show-current` → `main`
- [ ] `git status --short` → shows the two corpus/ledger files until Step 1 commits them
- [ ] `wc -l .gzkit/corpus/AGENTS.md.jsonl` → `46`
- [ ] `tail -1 .gzkit/corpus/AGENTS.md.jsonl` → the read-before-recommend doctrine, `tier: invariant`, `section: operator-doctrine-verbatim-canon`
- [ ] `uv run gz obpi status OBPI-0.0.37-22` → note it currently MISREPRESENTS state as `ATTESTED COMPLETED` (this is GHI #634); ledger truth is repudiated
- [ ] `grep "obpi_completion_repudiated" .gzkit/ledger.jsonl | grep OBPI-0.0.37-22` → repudiation event present (2026-06-16)
- [ ] `grep _FRESHNESS_FAIL_CLOSED src/gzkit/governance/trust_audits/rendition_freshness.py` → still `= False`
- [ ] `gh issue view 634` → open, `defect`/`runtime`

## Evidence / Artifacts

- `.gzkit/corpus/AGENTS.md.jsonl` — corpus (46 entries; new operator-doctrine entry is the last line; uncommitted)
- `.gzkit/ledger.jsonl` — carries this session's `corpus_entry_appended` event (uncommitted)
- `src/gzkit/commands/status_obpi.py` — Thread 1 fix surface (`_render_obpi_runtime_state` at line 435)
- `src/gzkit/ledger_semantics.py` — Thread 1 fix surface (runtime/attestation-state derivation; no repudiation awareness)
- `src/gzkit/governance/compose.py` — `render_agents_md` (read_bytes playback, lines 48-69)
- `src/gzkit/sync_surfaces.py` — `sync_agents_md` (writes rendition to AGENTS.md)
- `src/gzkit/content/render/pipeline.py` — the real Jinja2 render pipeline (unused by AGENTS.md playback)
- `src/gzkit/content/templates/agentcontract/claude.md.j2` — the formatting-bearing template
- `src/gzkit/content/models/agent_contract.py` — the `AgentContract` model and its `Pillar` verbatim-lines field
- `src/gzkit/content/tier_policy.py` — `assert_invariant_verbatim` (the substring floor)
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — `_FRESHNESS_FAIL_CLOSED` flag
- `.claude/plans/dynamic-singing-locket.md` — B.1 Increment 1 design plan (operator ruling on staged warn→fail)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-22-committed-rendition-store-deterministic-playback.md` — OBPI-22 brief
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta campaign plan
- `.gzkit/handoffs/20260619T231600Z-b1-increment-2-corpus-enrichment.md` — predecessor handoff
- GHI #634 (status renders repudiated as ATTESTED COMPLETED); GHI #623 (root facade); GHI #610 (repudiate cannot re-complete)
