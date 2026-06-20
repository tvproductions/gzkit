---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-19T23:16:00Z"
agent: claude-code
obpi_id: OBPI-0.0.37-22
session_id:
continues_from: .gzkit/handoffs/20260619T224207Z-b1-increment-1-rendition-commit-freshness.md
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-19T23:16:00Z -->

## 🛑 SUPERSEDED 2026-06-20 — the next pull is NOT B.1

**This handoff's advised next step (B.1 Increment 2 rendition rebuild) is no
longer the topmost pull.** Per the Magna Carta amendment dated 2026-06-20
(`docs/governance/build-to-1.0-campaign-2026-06-10.md`, operator-verbatim:
*"handoff and magna carta are stale, 0.0.74 should be a P0 issue, look"*),
**ADR-0.0.74-mx-mode-maintenance-hangar (MX Mode) is now the topmost P0 pull**
and **B.1 (ADR-0.0.37) is PAUSED behind it.** B.1 Increment 2's
`_FRESHNESS_FAIL_CLOSED=True` flag-flip is the exact staging flag
OBPI-0.0.74-09 retires; B.1 resumes against the MX marker mechanism only after
0.0.74 lands. Orient to the campaign's `Topmost (sequenced)` marker — not to the
"Advised next step" below.

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

**B.1 Increment 2 — corpus enrichment phase landed; composition phase NOT yet
complete.** OBPI-0.0.37-22 remains `repudiated` by design (not re-attested).

This session began as a `/git-sync` invocation (synced the
`dynamic-singing-locket.md` plan file, commit prior to this work) and then
pulled B.1 Increment 2 per the Magna Carta sequencing. Increment 1
(commit `c070f28a`) had already landed the `gz content commit` seam + content
fingerprint freshness gate in **warn mode** (`_FRESHNESS_FAIL_CLOSED=False`).

**What landed this session (commit `880fa9fa`, pushed to origin/main):**
Corpus `.gzkit/corpus/AGENTS.md.jsonl` enriched from 9 → 44 entries. 35 new
`--tier invariant` entries captured via `gz content remember`:
- 7 operator-doctrine-verbatim-canon entries (the canon-owner attestation set)
- 6 prime-directive-ownership entries
- 10 do-it-right-craftsmanship-maxim entries
- 12 behavior-rules entries (Always + Never constraints)

**What is NOT done (the composition phase that completes the increment):**
The committed renditions still omit the 35 new invariant-tier entries. `gz check`
(run this session, exit 0 overall — warn-staged gate) reports the corpus→rendition
seam is NOT satisfied: *"Committed rendition 'AGENTS.md/codex' omits 29
invariant-tier corpus entries [list elided] Recompose with a candidate that includes every
invariant-tier entry verbatim."* The same applies to the `claude` consumer.

A candidate compose attempt (`gz content compose AGENTS.md --consumer claude
--candidate /tmp/AGENTS_candidate.md`) **FAILED** twice with an invariant-floor
violation: the candidate did not contain every invariant-tier entry **verbatim**.
Root cause: the candidate hand-summarized several bullets that are `tier:
invariant` in the corpus and therefore must appear byte-for-byte. `/tmp` candidate
is ephemeral and is NOT committed — it must be rebuilt.

## Important Context

- **Invariant-tier entries must appear VERBATIM in the candidate rendition.** The
  compose validator (`gz content compose`) fail-closes (exit 1, invariant-floor
  violation) if any `tier: invariant` corpus entry is not present byte-for-byte in
  the candidate. Summarizing/shortening an invariant entry is the failure mode hit
  twice this session. Only `tier: compressible` entries may be condensed.
- **The corpus is the source of truth; renditions are played back from it.** The
  pipeline is `corpus → compress → rendition → playback`. `gz content remember`
  appends to corpus (done); `gz content compose` validates+stages a candidate;
  `gz content commit` promotes candidate→committed with a frozen fingerprint +
  Gate-5 attestation.
- **`gz content remember` section IDs are kebab-case normalized.** Valid sections
  for AGENTS.md are the kebab-case pillar ids (e.g. `operator-doctrine-verbatim-canon`,
  `prime-directive-ownership`, `do-it-right-craftsmanship-maxim`, `behavior-rules`).
  Passing a title like "Operator Doctrine" fails — the error lists valid sections.
- **Two consumers need committing:** `claude` and `codex` (the `gz check` output
  flagged `AGENTS.md/codex`; both consumers have committed renditions that omit
  the new entries).
- **The staging flag** `_FRESHNESS_FAIL_CLOSED` lives in
  `src/gzkit/governance/trust_audits/rendition_freshness.py`. Increment 2's
  terminal step flips it `False → True` (warn → fail-closed) per the
  OBPI-0.0.41-02→-03 warn-then-fail precedent — only AFTER the renditions are
  recommitted to include all entries, else `gz check` goes red.
- **OBPI-22 is Heavy/foundation + `sensitivity: security`** — completion requires
  Gate-5 human attestation; there is no self-close path. The operator's verbatim
  `--attestation-text` IS Gate 5.
- **Bash tool `cd` to a Windows backslash path fails** (backslashes eaten by
  bash). Working dir is already the repo root — do not prefix commands with `cd`.
  PowerShell tool handles Windows paths; Bash tool uses a POSIX `/c/Users/Jeff`
  style path.

## Decisions Made

- **Decision:** Capture all 35 new corpus entries at `--tier invariant`.
  **Rationale:** They are binding governance rules (operator doctrine, PRIME
  DIRECTIVE, DO IT RIGHT, Behavior Rules) that the `--rendition-floor-coherence`
  floor requires verbatim at every setpoint.
  **Alternatives rejected:** `--tier compressible` for the craftsmanship/behavior
  rules — rejected because they are load-bearing constraints, not condensable prose.
- **Decision:** Commit the corpus enrichment as its own atomic commit (`880fa9fa`)
  before the composition phase.
  **Rationale:** The enrichment is independently valid and durable; isolating it
  keeps the composition/flag-flip/completion as a clean reviewable next step and
  preserves progress if the session is interrupted.
  **Alternatives rejected:** Bundling enrichment + composition + completion in one
  commit — rejected as too coarse for review and risks losing the enrichment if
  composition stalls.
- **Decision:** Did NOT flip the staging flag or attempt `gz obpi complete` this
  session.
  **Rationale:** Renditions are not yet recomposed; flipping fail-closed now would
  redden `gz check`. Completion is Gate-5 operator-attested and the renditions
  must carry the corpus first.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before executing. -->

1. **Rebuild the candidate rendition with every invariant-tier entry verbatim.**
   Read the corpus (`.gzkit/corpus/AGENTS.md.jsonl`, 44 entries) and assemble a
   candidate AGENTS.md whose body contains each `tier: invariant` entry's `text`
   byte-for-byte. Do NOT summarize invariant entries (the failure hit twice this
   session). Suggest scripting the assembly from corpus `text` fields to guarantee
   verbatim fidelity rather than hand-typing.
2. **Validate + stage the candidate:** `gz content compose AGENTS.md --consumer
   claude --candidate <file>` then again `--consumer codex`. Must exit 0 (no
   invariant-floor violation) before proceeding.
3. **Attestly commit both renditions (Gate 5):** `gz content commit AGENTS.md
   --consumer claude --attestor "g0" --attestation-text "<operator verbatim>"`
   and the same for `--consumer codex`. Operator must supply the verbatim
   attestation token. NOTE attestor field: per operator doctrine, repo-bound
   author/attestor is recorded as **`g0`** (not the personal name) — confirm with
   operator.
4. **Flip the staging flag fail-closed:** in
   `src/gzkit/governance/trust_audits/rendition_freshness.py` set
   `_FRESHNESS_FAIL_CLOSED = True`. Run `gz check` — must stay green now that
   renditions carry the corpus. Tests already exercise both modes (per Increment 1).
5. **Complete OBPI-22 with operator attestation:** `gz obpi complete
   OBPI-0.0.37-22 --attestor "g0" --attestation-text "<operator verbatim>"` —
   Heavy/foundation/security walkthrough fires; operator's verbatim
   `--attestation-text` IS Gate 5. This clears `repudiated`. Then update
   the campaign B.1 checkbox + reconcile ADR-0.0.37 (02/03 re-point, 21 re-verify
   are SEPARATE later increments, NOT this one).

## Pending Work / Open Loops

- **02/03 re-point + re-attest** to the corpus mechanism — a SEPARATE later B.1
  increment (operator ruling), not part of Increment 2.
- **OBPI-21 honest re-verification** — later B.1.
- **B.2** registry-projected <15k codex surface (#519); **B.3** play back queued
  corpus entries — both follow B.1 terminal.
- **Corpus coverage is partial.** Only 4 sections of AGENTS.md were enriched
  (operator-doctrine, prime-directive, do-it-right, behavior-rules). The full
  AGENTS.md has ~20 sections. Whether the rendition must be a COMPLETE AGENTS.md
  replacement or whether incremental corpus growth is acceptable for OBPI-22
  completion is an OPEN QUESTION for the operator — the freshness gate checks
  invariant-floor *presence*, not full-surface *derivation* (per the Increment 1
  plan note: "no committed rendition is yet genuinely 'the corpus played back'").
- **Advisory (non-blocking):** `gz check` reports 1835 unlinked specs / 10 orphan
  tests (spec-test-code drift) and 1 approaching flag deadline (`ops.product_proof`,
  within 14 days). Both advisory, do not affect exit code.

## Verification Checklist

- [ ] `git log --oneline -3` shows `880fa9fa` (corpus enrichment) on main
- [ ] `git branch --show-current` → `main`; `git status` clean (origin synced)
- [ ] `wc -l .gzkit/corpus/AGENTS.md.jsonl` → 44 entries
- [ ] `uv run gz content commit --help` and `gz content compose --help` resolve
- [ ] `uv run gz check` exit 0 but reports rendition omits invariant-tier entries
      (the work-remaining signal)
- [ ] `grep _FRESHNESS_FAIL_CLOSED src/gzkit/governance/trust_audits/rendition_freshness.py`
      still `= False` (warn mode — not yet flipped)
- [ ] `uv run gz obpi status OBPI-0.0.37-22` → still `repudiated` (not re-attested)

## Evidence / Artifacts

- `.gzkit/corpus/AGENTS.md.jsonl` — the enriched corpus (44 entries; commit `880fa9fa`)
- `.gzkit/ledger.jsonl` — 35 `corpus_entry_appended` events from this session
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta; B.1 item at
  line ~827 defines Increment 2 scope
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-22-committed-rendition-store-deterministic-playback.md` — OBPI-22 brief
- `.claude/plans/dynamic-singing-locket.md` — the Increment 1 design plan (context
  for the mechanism Increment 2 consumes)
- `.gzkit/handoffs/20260619T224207Z-b1-increment-1-rendition-commit-freshness.md` —
  predecessor handoff (Increment 1)

## Environment State

- Platform: win32; shell PowerShell primary, Bash (POSIX) available.
- Bash tool: use POSIX paths (`/c/Users/Jeff/source/repos/va/gzkit`); do NOT prefix
  with `cd` to a backslash path (backslashes are eaten). Working dir is already
  repo root.
- Python via `uv run`; never prefix `uv run gz` with `PYTHONUTF8=1`.
