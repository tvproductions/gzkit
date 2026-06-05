---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-05T13:07:42Z"
agent: claude-code
obpi_id:
session_id: phase4-drain-2026-06-05-pm
continues_from: .gzkit/handoffs/20260605T094704Z-every-move-breaks-systemic-diagnosis.md
---

<!-- Handoff for ADR-0.0.37 — created by claude-code at 2026-06-05T13:07:42Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

Present the advised steps to the operator and obtain explicit authorization
before executing any of them — no push, no `gz` ceremony, no file mutation until
the operator says go. You advise; the operator rules; you note variance and stop.

## Current State Summary

Return-to-health **Phase-4 drain** session (the goal is
`docs/governance/return-to-health-plan-2026-05-30.md`). `uv run gz check` was
**GREEN throughout** (true exit 0, 26/26 gates). Tier 0 holds; recovery stays
**OPEN** (#519 is still the sole open `emergency`).

**🚨 FIRST ORIENTATION FACT / BLOCKER — unpushed commits vs. closed remote GHIs.**
Three commits are **local-only on `main`; they are NOT on `origin`**:

- `abba7e9b` — `fix(hexagonal-architecture)` (GHI #559)
- `44ceedd8` — `fix(obpi-complete)` decode with errors=replace (GHI #534)
- `7e44c731` — `docs(recovery)` Phase-4 drain plan update

A direct `git push origin main` was **blocked by the Claude Code auto-mode
classifier** ("no explicit user authorization for a direct main push"). I did
**not** work around it (Never #6). Meanwhile GHIs **#525, #534, #559, #560,
#562 are CLOSED on GitHub** with comments citing these SHAs. So `origin` lacks
the commits the closed issues reference — a fresh session reading `origin` sees
neither the fixes nor the plan update and could redo #559/#534. **Operator must
push to reconcile** (see Immediate Next Steps #1). `origin/main` was `dcea388b`
at session start and is unchanged; no concurrent agent was detected.

## Important Context

- **Gate-5 / heavy-lane ceiling (why this was a debt-drain, not a #519 push):**
  every remaining ADR-0.0.37 OBPI is heavy-lane, contract-bearing, and
  terminates at Gate 5 (operator attestation). A solo agent can build + verify
  but cannot attested-complete. #519's durable cure additionally needs the full
  registry-projection build. So #519 **cannot close in a solo session**; the
  lowest-regret solo work is draining completable Phase-4/3 debt.
- **`gz check` does NOT run `validate --documents`** (verified: 0 matches in the
  gate output). So #480/#524/#527 are non-gating recovery debt, not gate blockers.
- **`Validated` is gzkit's real ADR lifecycle status** (on dozens of ADRs and in
  `gz adr report`), but it is absent from the `--documents` validator status enum
  `[Draft, Proposed, Accepted, Superseded, Deprecated]`. #480/#524/#527 are one
  schema-enum-class decision (reconcile the validator enum to the real lifecycle),
  NOT per-file status edits — a schema/runtime-contract call for the operator.
- **#532 is bigger than its title** — the stale `docs/user/manpages/gz-validate.md`
  reference sprawls across dozens of ADR/OBPI briefs, many **attested**. Editing
  attested briefs collides with open doctrine question **#549**. The canonical
  doc actually lives at `docs/user/manpages/validate.md` (verified on disk;
  `docs/user/commands/validate.md` does NOT exist — some briefs assert the wrong
  path). Not a clean direct-fix.
- **Push convention:** this repo bundles work through `gz git-sync` chore commits,
  so clean `(GHI #N)`-trailer commits are usually squashed into sync carriers;
  the AI commits and the **operator pushes** (consistent with Snapshot I/J).

## Decisions Made

- **Decision:** Drain direct-fixable Phase-4 debt one at a time rather than
  attempt #519/ADR-0.0.37 build-out.
  **Rationale:** goal-hook autonomous mode + Gate-5 ceiling ⇒ #519 uncloseable
  solo; debt-drain is lowest-regret, completable-solo, advances Definition-of-
  Healthy item 5 + Phase-4 "issue count decreasing."
  **Alternatives rejected:** driving OBPI-0.0.37-21/22 to Gate 5 (stalls at
  attestation, risks the Snapshot-H half-built-on-main hazard).
- **Decision:** Fix #534's named site (obpi_complete.py) + file class-GHI #582
  for the 41-site class, rather than sweep all 41 now.
  **Rationale:** the full sweep adds a recurrence-defense validator = ceremony
  per Defect-fix routing; the instance fix is a clean ≤1-file direct-fix.
  **Alternatives rejected:** 41-site sweep solo (exceeds direct-fix thresholds;
  each site needs per-call verification).
- **Decision:** Close #525/#560/#562 as verify-only already-resolved.
  **Rationale:** all three verified resolved by current observed state (doctrine
  line present; behave scenario green; tautological audit exit 0) with carrying
  commits cited.
  **Alternatives rejected:** leaving them open (Phase-4 wants the count down).
- **Decision:** Defer #480/#524/#527 (schema class), #532 (attested-brief sprawl),
  #551 (loosening overlap + budget-touch), #571 (large routed).
  **Rationale:** each is operator-gated or exceeds clean-solo scope.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator; do not execute without authorization. -->

1. **[REQUIRED — audit-trail reconcile]** Push the three local commits so
   `origin` carries the fixes the already-closed GHIs cite:
   `git push origin main` (or `uv run gz git-sync --apply --lint --test`). The AI
   could not push (auto-mode classifier). Verify `git rev-list --left-right
   --count origin/main...HEAD` reads `0  0` afterward.
2. **#519 (the actual recovery blocker)** needs the operator: the ADR-0.0.37
   build-out (8/19 attested; remaining OBPIs 06/07/08/09/12/13/14/15/16/19) toward
   the <15k registry-projected surface (GHI #533) + Gate-5 attestation. No solo
   path closes it.
3. **Remaining Phase-4 is largely operator-gated:** decide the #480/#524/#527
   schema-enum-class question (add `Validated` to the `--documents` enum vs.
   another reconciliation) as a schema/runtime-contract call; #532 awaits the
   #549 attested-brief-correctability doctrine; #551 overlaps landed loosening
   `ac0816ff`.
4. **Optional clean solo Phase-3 candidates (NOT sized this session):** #569
   (DRY the verify-stage extractor onto `extract_fenced_commands`), #544 (add a
   Pydantic schema to the `covers` grandfathering cache load). Plausibly clean
   one-pass direct-fixes; size against thresholds before committing.
5. **#582** (subprocess decode robustness, ~41 sites + validator) is
   ceremony-sized — route deliberately, not as a quick sweep.

## Pending Work / Open Loops

- **#519** — sole open emergency; durable cure unbuilt (registry-projection to
  <15k, GHI #533) — operator-gated (build + Gate 5).
- **#582** — filed this session; 41 text-mode subprocess reads lack `errors=`;
  recurrence-defense validator proposed. Untouched beyond the #534 instance.
- **Schema-enum class (#480/#524/#527)** — `validate --documents` 3536 errors;
  `Validated`-status enum mismatch is the dominant sub-class; needs a schema
  decision, not per-file edits.
- **#532/#549** — manpage-path drift across attested briefs blocked on the
  attested-brief-correctability doctrine.
- **Minor awareness (not a defect):** the #559 port claim (ADR-0.13.0 →
  ADR-0.0.14 deterministic-OBPI-command port) was verified on 0.13.0's side
  (Intent + `promoted_from`); 0.0.14's body was not read to confirm it is the
  port. Hedged wording; mkdocs-green; acceptable.

## Verification Checklist

- [ ] `git rev-list --left-right --count origin/main...HEAD` → reconcile the
      `0  3` (unpushed) state to `0  0` via operator push.
- [ ] `uv run gz check` → "✓ All checks passed" (26/26, exit 0).
- [ ] `git branch --show-current` → `main`.
- [ ] `gh issue list --state open --label emergency` → only #519.
- [ ] `uv run -m unittest tests.commands.test_obpi_complete_subprocess_decode`
      → 2 pass (the #534 RED→GREEN guard).
- [ ] `uv run mkdocs build --strict` → exit 0 (the #559 doc fix link check).

## Evidence / Artifacts

- `docs/governance/return-to-health-plan-2026-05-30.md` — recovery plan; GHI
  register + tier counts updated this session (38→34 open; commit `7e44c731`).
- `src/gzkit/commands/obpi_complete.py` — `#534` fix: new `_run_captured` helper
  with `errors="replace"`; both covering-test call sites rewired (`44ceedd8`).
- `tests/commands/test_obpi_complete_subprocess_decode.py` — `#534` RED→GREEN
  decode-robustness test (non-UTF-8 `0xa7` tolerance + non-zero-exit preservation).
- `docs/governance/hexagonal-architecture.md` — `#559` fix: demoted-ADR adapter
  examples replaced with live feature adapters 0.13.0/0.18.0/0.12.0 (`abba7e9b`).

## Environment State

Python 3.13, macOS (darwin). Note: the #534 crash is Windows-surfaced
(reader-thread variant) but reproduces cross-platform on macOS (POSIX raises in
the calling thread); the fix (`errors="replace"`) covers both. Direct push to
`main` is gated by the Claude Code auto-mode classifier — operator push required.
