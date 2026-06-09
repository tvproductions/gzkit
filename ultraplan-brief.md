# Planning Brief — gzkit restore-health convergence

> **Purpose:** Single planning input for ultraplan. Self-contained — no need to
> read the handoff chain. Captures (1) restore-health status, (2) one open
> decision that gates the rest, and (3) the candidate work-list with
> dependencies. **Authored 2026-06-09; HEAD `3c1695eb` on `main`, synced 0/0.**

---

## 1. Headline

**The restore-health treadmill's structural exit has landed.** For eight prior
sessions, `main` went silently RED *between* sessions — coupled-surface edits
(BDD scenarios, manpages, the insights schema, the `ln` proof-binding surface)
weren't caught at edit time and surfaced as archaeology at the next closeout. The
operator named this recurring pattern **V.I.B.E.S.** ("Velocity Increased, Bugs
Expected Software").

That root cause now has a mechanical gate: **ADR-0.0.68
`green-between-sessions-gate` is Completed + attested (2/2 OBPIs)** —
(01) a pre-push `gz check` hook, (02) a session-green-gate validator. Remaining
work is therefore closer to **additive / maintenance** than corrective. This is
the "done enough" inflection the recovery plan was driving toward.

---

## 2. Restore-health status

| Signal | State |
|---|---|
| `main` | Green; synced 0/0 to `origin/main`; HEAD `3c1695eb` |
| Foundation ADR set | 68 ADRs; ~38 Validated, ADR-0.0.68 now Completed (one step short of Validated) |
| **Root-cause gate** | ✅ **Landed** — green-between-sessions enforcement exists (ADR-0.0.68) |
| Open emergencies | **#519 only** — codex gzkit context surface exhausts 258K window (untouched) |
| Open GHIs | 38 (steady-state triage scale, not a restore-health queue) |
| ADR-0.0.41 | **Pending / pre_closeout / BLOCKED, 2/5 OBPIs** — the `ln`-coupled closeout |

**Recently cleared (post-last-handoff session):** #591 (obpi-audit coverage
denominator scoped to brief unit), #589 (pipeline Stage 3 exit-code integrity),
#600 (session-green-gate token match), #598 (OBPI-0.0.68-01 demo docs).

**"Done enough" definition** (from the recovery plan): (a) foundation set all
Validated or consciously parked; (b) the standing green-between-sessions
invariant holds (✅ now true); (c) the GHI backlog drops to steady-state triage +
patch-release cadence. With (b) achieved, the structural red-generator is gone.

---

## 3. ⚠️ OPEN DECISION — resolve before sequencing (operator's call)

> **✅ RESOLVED (operator ruling, 2026-06-09):** **Option A — Sunset `ln`.**
> Ratified during the ADR-0.0.68 audit session; #599's auto-populate direction
> loses. Next step when P1 is picked up: scope the `ln`-sunset foundation ADR
> (retire surface → derived view over req-kind + ledger; close #543; fold the
> `trust_audits/cli.py:222-225` fail-open seam fix). ADR-0.0.68 reached
> **Validated** the same session, so the gate's zero-rewiring fence
> (REQ-0.0.68-02-04) is locked before sunset work begins.

There is a **live inconsistency** in the `ln` (closeout-proof-binding) surface
strategy. The handoff chain records an operator decision to **sunset `ln`** (let
it wither; don't feed it), on the rationale that `gz validate
--req-kind-discipline` is the real proof channel and `ln` masks the deferred
SUPPORT/FENCE req-kind gap rather than closing it. But the most recent commit —
**#599, `3c1695eb`** — does the opposite: it **auto-populates brief `ln:` from
resolved receipts** (feeds the surface).

These are opposite strategies for the same surface, and **ADR-0.0.41's closeout
depends on which one wins.** Per gzkit's "name confusion, don't resolve
unilaterally" rule, ultraplan must surface this for an operator ruling rather
than pick silently.

| Option | What it means | Tradeoff |
|---|---|---|
| **A — Sunset `ln`** | Retire the surface; replace its "green-at-closeout" purpose with a derived view over (req-kind channels + ledger); complete the deferred SUPPORT/FENCE req-kind channels (#543). | Honest closure of the proof gap; one foundation ADR collapses several loops; **unblocks 0.0.41**. Larger, contract-bearing (touches CLI validator, schema field, ceremony gate, 17 briefs). |
| **B — Keep + auto-populate** | Accept #599's direction; `ln:` is auto-filled from resolved receipts, so closeout stops generating red. | Smaller; already partly landed. But retains a redundant drift surface and leaves the SUPPORT/FENCE req-kind gap (#543) masked rather than closed. |

**Recommendation:** A (sunset) is the convergence move — it's subtraction of the
red-generator and structurally closes #543 — but #599 has already moved toward B,
so the operator should explicitly ratify a direction before 0.0.41 closeout.

---

## 4. Candidate work-list (for ultraplan to sequence)

### P0 — #519 (the only open emergency)
- **What:** codex gzkit context surface exhausts the 258K window.
- **Cure path:** the durable fix needs the **<15k registry-projected surface
  (GHI #533)** + **ADR-0.0.37 build-out** + **Gate 5 human attestation**.
- **Status:** interim byte relief already landed (root AGENTS.md under Codex's
  32,768 B cap); full-window closure still open.
- **Gate:** requires the operator for Gate 5; cannot be fully autonomous.

### P1 — `ln` strategy decision + ADR-0.0.41 closeout
- **Blocked on:** §3 decision (sunset vs. keep-and-auto-populate).
- **Then:** ADR-0.0.41 is Pending/BLOCKED at pre_closeout, 2/5 OBPIs. Drive its
  closeout ceremony — or decide it attests as-is (its cited receipts resolve via
  the ledger), exactly as 0.0.67 did.
- **If sunset chosen:** scope the `ln`-sunset foundation ADR (retire surface →
  derived view over req-kind + ledger; complete deferred SUPPORT/FENCE channels,
  closing #543; fold the fail-open seam fix at `trust_audits/cli.py:222-225` →
  surfaced `ValidationError` + covering test). This ADR unblocks 0.0.41.

### P2 — ADR-0.0.68 → Validated
- ADR-0.0.68 is Completed + attested; run its audit ceremony
  (COMPLETED → VALIDATED) to lock the green-between-sessions gate as a permanent
  validated floor. Low-energy, high-symbolic-value (it's the treadmill exit).

### P3 — Foundation backlog (additive, felt-need-paced)
- ~19 Draft + ~8 Proposed foundation ADRs remain short of Validated. With the
  red-generator gone these are additive — pace by felt need, not momentum. Do
  **not** restart the retired OBPI-17 density-classification route.

### P4 — GHI steady-state triage
- 38 open GHIs. Now maintenance-cadence, not restore-health. Run `ghi-triage` for
  a rank-ordered pull list.

---

## 5. Dependency / sequencing notes

```
§3 ln-decision ──► P1 (0.0.41 closeout)
                     └─(if sunset)─► ln-sunset foundation ADR ──► closes #543
P0 (#519) ── independent, but operator-gated (Gate 5) ── topmost priority
P2 (0.0.68 → Validated) ── independent, low-energy
P3 (foundation backlog) ── gated on "done enough" appetite, not blocking
P4 (GHI triage) ── continuous
```

- **#519 is the topmost priority** (sole emergency) but needs operator Gate 5 —
  it cannot close in a fully autonomous run.
- **The `ln` decision is the highest-leverage unblock** for in-flight ceremony
  (frees 0.0.41 and, if sunset, structurally closes #543).
- **Everything else is additive** now that ADR-0.0.68 holds the green floor.

---

## 6. Verification anchors

```bash
uv run gz adr report ADR-0.0.68          # Completed, attested, 2/2 OBPIs
uv run gz adr report ADR-0.0.41          # Pending, pre_closeout, BLOCKED, 2/5
uv run gz adr report ADR-0.0.67          # Validated (last fully-closed foundation ADR)
git log -1 --oneline                     # 3c1695eb (GHI #599 ln auto-populate)
git status -sb                           # clean, synced 0/0
gh issue list --state open --label emergency   # only #519
```
