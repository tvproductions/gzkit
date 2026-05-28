# The June 2026 gzkit Road to Salvation

**Date:** 2026-05-28
**Author:** ahuimanu (operator) — *"GzKit is sick and in poor health. I need HELP."*
**Drafted with:** Claude Opus 4.8 (the savior under test)
**Status:** **ACTIVE — this is the canonical recovery roadmap.**

> ## This document supersedes the priors
>
> The June 2026 Road to Salvation is the **single authoritative recovery plan**.
> It absorbs, updates, and supersedes:
>
> - `docs/governance/get-out-of-jail-plan-2026-05-23.md` (Prequel + Moves 1–6) —
>   **superseded**; its shipped moves are harvested here, its stalled moves are
>   re-sequenced below.
> - `docs/governance/get-out-of-jail-extensions-2026-05-23.md` (3 GSD deltas) —
>   **deferred**; still post-recovery, re-anchored to this plan's exit.
> - `.claude/plans/rescue-and-repair-roadmap-2026-05-27.md` (operator notebook) —
>   **folded in**; its workstream closures are the "what shipped" evidence here.
> - `docs/governance/opus-4.8-assessment.md` — **companion/cousin**. That document
>   is now the *capability profile* ("what Opus 4.8 can do"). **This document holds
>   the *applied plan* ("how Opus 4.8 digs gzkit out").** Read them together; when
>   they disagree on sequencing, this document wins.
>
> The 5-alarm fire (GHI [#517](https://github.com/tvproductions/gzkit/issues/517)),
> the Codex window collapse (GHI #519), and the model-regression deep-dive remain
> the binding diagnosis. This plan does not re-litigate them — it digs out of them.

---

## 0. The one paragraph that matters

gzkit is not sick because its ideas are wrong or because the model is weak. It is
sick because **its covenant is asserted in prose, not promoted to Mechanical** —
and because the 4.7-era defect velocity (557 GHIs in ~4.5 months, clusters of
8–11 in a day) proved that *a capable agent in front of missing gates fills the
tracker faster in both directions.* The get-out-of-jail plan correctly named the
five structural moves; **three shipped, three stalled, and the un-gated three are
exactly where the new June GHIs are still pouring in.** Opus 4.8 is the burndown
engine that finishes the stalled three — **after** which the same capability that
caused the flood becomes the force that drains it.

---

## 1. The 4.7 era — what "falling apart" actually looked like

Claude Opus 4.7 shipped **2026-04-16**. In the ~6 weeks since, the repo's distress
signal is unambiguous. This is the corpus this plan collates and answers.

### 1.1 The panic record (chronological)

| When | Artifact | What it says |
|---|---|---|
| 2026-04-16 | `GZK-GOV-007`, `model-regression-taxonomy.md` | 4.7 behavioral shift: cautious prompts *degrade* it; action-downgrade; "declaring sufficiency without acting." gzkit's governance shape resembles the cautious prompt Anthropic tested. |
| 2026-04-18 | GHI #224 (umbrella) + #229, `artifacts/audits/4.7-governance-hardening-ghi-drafts.md` | **"defect velocity ~5× baseline."** F4 over-ceremony coupling + F5 cross-surface contradictions *deadlock* 4.7. GHIs #186–#199, #217–#223 filed in 48 hours. |
| 2026-04-27 | GHI #349 | Governance surface is **choreographed, not state-machined** — silent state drift is *structurally tolerated*. "It's all vibey." |
| 2026-05-23 | **GHI #517** (`emergency`) | **5-ALARM FIRE.** Five structural failures in one ADR-0.0.57 closeout. *"THE DEGRADATION CANNOT BE OVERSTATED. Det her er et klovneshow!"* |
| 2026-05-23 | GHI #519 (`emergency`) | Codex context surface **exhausts the 258K window**. Still **open**. |
| 2026-05-23 | `get-out-of-jail-plan`, `-extensions`, `model-regression-deep-dive` | The recovery diagnosis + the five-move plan. |
| 2026-05-25 | ADR-0.0.59 (Move 6 inserted) | Categorical test-shape rot: **~3,404 filesystem-shaped test ops (32% of the tree)**. |
| 2026-05-27 | `rescue-and-repair-roadmap` | Operator notebook: workstreams A/B/B′/D closed; **GHI #553 — new 5-alarm** (TASK governance silently abandoned despite Validated ADR-0.22.0). |
| 2026-05-28 | `opus-4.8-assessment.md` | The capability verdict: adopt 4.8 *as the burndown engine, after the gates exist*. |

### 1.2 The five recurring failure classes (root-cause, not symptom)

1. **Unenforced doctrine** — invariants stated in ADRs/AGENTS.md with no
   `gz validate --<scope>` that fails CI (#537, #538, #551, #552, #556).
2. **Verification theater** — demos hand-authored not executed; tautological
   tests; extractor noise (#540, #539, #562, #541; the canonical case is the
   five #517 failures).
3. **Declared-but-never-wired** — schemas tested but never instantiated in the
   real path; "proof" is regex, not a query (#543, #544, #545).
4. **Runtime brittleness** — UTF-8 / shell-less / heredoc assumptions break in
   the agent subprocess runtime (#534, #550, #539, #519).
5. **Lifecycle / state drift** — demote/promote leave stale state; choreography
   decoheres; TASK envelopes silently abandoned (#349, #553, #558, #559, #536,
   #549, #480).

**The meta-finding (unchanged since #517):** ceremony correctness is enforced by
*prose in SKILL.md files* with **no Layer 2 runtime enforcement** and **the
operator as the verification layer.** That is the mud. We are digging out of it.

---

## 2. Recovery-state audit — where we actually are (validated 2026-05-28)

The get-out-of-jail plan's seven "out of jail" criteria, checked against the live
repo (`main` @ `25cf1c6`, `pyproject` = `0.28.0`) and open GHIs:

| # | Move / criterion | State | Evidence |
|---|---|---|---|
| Prequel | `gz adr demote` + collapse the 25-deep `0.27.0`–`0.51.0` queue | ✅ **SHIPPED** | `src/gzkit/commands/adr_demote.py` + manpage (GHI #521); ADRs 0.48/0.49/0.50 demoted (#559 confirms). |
| Move 1 | Namespace router skill layer | ✅ **SHIPPED** | All six skills exist: `gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage` (+ `gz-skill-router`). |
| Move 2 | `gz context <ADR-ID>` focused-context loader | ✅ **SHIPPED** | `src/gzkit/commands/context_cmd.py`, manpage, `gz-context` skill; landed as ADR-0.28.0 (repo at `0.28.0`). |
| Move 6 | ADR-0.0.59 test-shape doctrine | ⚠️ **SHIPPED, partial sweep** | ADR-0.0.59 **Validated** 2026-05-27. `gz validate --req-kind-discipline` / `--tautological-test-audit` exist. **But** only the top-5 first-wave sweep ran; the long tail of ~3,400 ops remains (the ADR's own tradeoff #1). |
| Move 3 | Root `AGENTS.md` ≤ 5 KB router | ❌ **STALLED** | Skills `AGENTS.md` still ~20 KB. **GHI #533**: 5K target blocked on ADR-0.0.37 + registry-projection migration. **GHI #519** (Codex 258K window) is the unpaid cost. |
| Move 4 | Typed skill contracts + `gz validate --skill-contracts` | ❌ **NOT SHIPPED** | No `--skill-contracts` scope in `src/gzkit/`. Skills remain prose islands. |
| Move 5 | Closeout on hexagonal spine (`CeremonyStore` + `ReqEvidence`) | ❌ **NOT SHIPPED** | No `CeremonyStore` in `src/`. **GHI #516 still OPEN.** All five #517 failure classes remain un-gated. |
| Harvest | ≥ 50 of 61 Validated ADRs → `Completed` | ❌ **NOT DONE** | Closeout still can't be trusted to harvest until Move 5 lands. |

**The verdict in one line:** *The cheap, mechanical moves shipped. The three that
actually close the 5-alarm failure classes (3, 4, 5) stalled — and the June GHI
flood (#537–#562) is concentrated precisely on those three un-gated surfaces.*

### 2.1 Proof the leak is still open

The newest GHIs are not new problems — they are the **predicted** consequence of
shipping Moves 1–2–6 while leaving 3–4–5 stalled:

- **#540** (demos not executed) and **#539** (heredoc demo split) = #517 Failures 1 & 3, **still un-gated** → Move 5 territory.
- **#537** (BEHAVIOR-kind cannot-be-uncovered-accepted not enforced) and **#538** (STRUCTURAL-FENCE parent shape unchecked) = #517 Failure 4 class → Move 5 + validator promotion.
- **#543/#544/#545** (declared-but-never-wired req-kind schemas) = the dead-schema class, born *inside the Move 6 machinery itself*.
- **#519** (Codex window) = the unpaid Move 3 bill.
- **#553** (TASK envelope abandoned) = a fresh state-drift 5-alarm of the #349 class.

---

## 3. How Opus 4.8 digs gzkit out — capability applied to the stalled moves

> The companion `opus-4.8-assessment.md` argues *what* 4.8 can do. This section is
> *how* we point it. The rule from the assessment holds: **4.8 is the burndown
> engine behind the gates, never a substitute for building them.** Below, each
> stalled move is matched to the specific 4.8 capability that clears it.

| Stalled move | The blocker | The 4.8 capability that clears it |
|---|---|---|
| **Move 3** (AGENTS.md ≤ 5 KB) | #533: needs ADR-0.0.37 + registry-projection migration; large always-loaded surface | **Long-context coherence.** 4.8 holds the AGENTS.md + ADR + rules chain reliably in one session, so the prose-lift to skill-routed docs can be done coherently in fewer passes — directly relieving the #519 window pressure. |
| **Move 4** (typed skill contracts) | No `inputs:`/`outputs:` schema; no `--skill-contracts` validator | **Spec-bound mechanical authoring.** Promoting Judgment-tier rules into fail-closed validators is exactly the fast, precise, spec-following work 4.8 excels at. This is the highest-leverage burndown class. |
| **Move 5** (closeout-on-spine) | #516 open; `CeremonyStore`/`ReqEvidence` span CLI + ledger + schema | **Multi-file lifecycle coherence.** The port + adapter + brief-schema + ceremony-renderer change is one coherent cross-file patch — 4.8's strongest shape. Closes all five #517 failure classes at once. |
| **Harvest** (61 → Completed) | Closeout untrustworthy until Move 5 | **Throughput behind a real gate.** Once closeout has teeth, 4.8 re-runs it across 61 ADRs fast — the *good* kind of velocity. |
| **Runtime hardening** (#534/#550/#539/#519) | UTF-8 / shell-less / heredoc recurring | **Runtime discipline.** 4.8 follows the cross-platform rules (no `PYTHONUTF8=1` prefix, shell-less invocation) more consistently, so the class stops recurring. |

**The honest boundary (carried from the assessment):** 4.8 changes nothing it is
pointed at *without* a gate. #517 Failure 2 — GHI #427's prose "fix" that never
landed — is the proof. So this plan builds the gate first in every phase, then
lets 4.8 sprint behind it. **Judgment calls (#547 gray zones, #549 re-attestation,
#553 doctrine) stay with the operator. The covenant reserves final judgment for the
human; 4.8 does not get to decide doctrine.**

---

## 4. The June plan — three phases, gate-first, every phase names its proof

> Posture (inherited and reaffirmed): **Sobriety. No new foundation ADRs beyond the
> ones named. No new doctrine pages — this file is the only new one. Build the gate
> before you point the model at the surface.** Finish the get-out-of-jail spine
> before chasing anything new.

### Phase I (Week 1) — Pay the runtime + window debt (unblock everything)

The Codex window emergency (#519) and the recurring runtime brittleness gate every
other move (a 4.8 session that can't hold the surface can't execute the plan).

- [ ] **Move 3 down payment.** Lift the heaviest prose sections out of `AGENTS.md`
      into skill-routed docs (the `gz-context-diet` path), each replaced by a
      ≤ 1-line pointer. Target the #519 window first; full ≤ 5 KB lands when
      ADR-0.0.37 + registry-projection close (#533).
- [ ] **Harden the runtime contract once.** Consolidate UTF-8 + shell-less +
      heredoc handling (#534, #550, #539) so the class stops recurring.
- [ ] **Gate:** extend `gz validate` runtime checks so a brief authored with a
      shell-only compound command or a multi-line heredoc demo **fails closed**.
- [ ] **4.8's job:** coherent multi-file prose-lift; consistent runtime-rule adherence.

**Done when:** a normal Codex/Claude session carries an ADR plan→closeout inside a
200K budget without orientation rereads; #519 closes; #534/#550/#539 closed.

### Phase II (Week 2) — Build the spine that closes the 5-alarm classes

This is the heart. Move 5 (closeout-on-spine) + Move 4 (typed contracts) are the
gates that make the #517/#537/#538/#540/#539 GHIs *impossible*, not just fixed.

- [ ] **Move 5 — closeout on the hexagonal spine.** Author/promote
      `ADR-pool.closeout-ceremony-on-hexagonal-spine`. Ship `CeremonyStore` port +
      `ReqEvidence` model; brief schema gains `req_evidence:`; **AND-clause REQs
      rejected at authoring** (kills #517 Failure 4 / #537); **`--next` blocked at
      the Gate 5 boundary** (kills #517 Failure 5); **demos executed not
      transcribed** (kills #517 Failures 1 & 3 / #540 / #539). Re-label #516
      `recovery-move-5`.
- [ ] **Move 4 — typed skill contracts.** `inputs:`/`outputs:` frontmatter on the
      four Intent-stage skills; `gz validate --skill-contracts` fail-closed.
- [ ] **Promote Judgment-tier rules to Mechanical.** For #537, #538, #551, #552,
      add a fail-closed `gz validate --<scope>` and catalogue it per the scorecard.
      Treat any doctrine without a failing test as *not yet real*.
- [ ] **Wire or delete the dead schemas.** Audit #543, #544, #545 — instantiate in
      the production path or remove. Dead schemas read as coverage and lie.
- [ ] **4.8's job:** the cross-file `CeremonyStore` patch held in one coherent pass;
      the validator backlog burned down fast and precisely.

**Done when:** closeout on an ADR with stale anchors fails at preflight; `--next`
cannot bypass attestation; #516/#537/#538/#539/#540/#543/#544/#545 closed.

### Phase III (Week 3) — Harvest, drain, and prove the model wasn't the bottleneck

- [ ] **Harvest.** Re-run closeout across the 61 Validated ADRs; harvest ≥ 50 to
      `Completed`. Bookkeeping matches reality.
- [ ] **Drain the lifecycle-drift cluster.** #553 (TASK envelope), #558/#559
      (demote stale state), #536 (invalid OBPI paths), #480 (3,536 validator
      errors) — route per the now-real gates.
- [ ] **Empirical proof.** Measure GHIs-opened-per-session-day before vs. after the
      gates land. If the rate **drops** with the *same or stronger* model, that
      confirms enforcement — not the model — was always the binding constraint.
- [ ] **Cap the discovery reflex.** WIP cap + "no new doctrine without a gate"
      before filing more. Same-day batches of 8–11 GHIs are the disease, not the cure.
- [ ] **Triage the deferred extensions.** Re-evaluate the three GSD deltas in
      `get-out-of-jail-extensions` against the post-recovery shape.

**Done when:** the GHI-open rate is measurably down, ≥ 50 ADRs are `Completed`, and
the `emergency`-labeled backlog is empty.

---

## 5. Definition of "out of the mud"

gzkit is out of the mud when **all** of these hold:

- [ ] No open `emergency`-labeled GHI (#519, #553 resolved).
- [ ] Every one of the five #517 failure classes has a **failing gate** that
      reproduces it, not prose guidance.
- [ ] `gz validate --skill-contracts` and the Move 5 closeout preflight are in the
      default `gz check` pipeline and fail closed.
- [ ] Root `AGENTS.md` ≤ 5 KB; a full ADR cycle fits a 200K budget.
- [ ] ≥ 50 of 61 Validated ADRs harvested to `Completed`.
- [ ] The dead-schema class (#543/#544/#545) is wired or deleted — zero "tested but
      never instantiated" records.
- [ ] GHIs-opened-per-session-day is **measurably lower** than the 4.7-era baseline.

If those hold, gzkit is shipping on its own foundation with the covenant **promoted
to Mechanical** — and Opus 4.8 is doing the *good* kind of fast.

---

## 6. Anti-temptation tripwires (binding for the whole of June)

1. Drafting a new foundation ADR outside Moves 3/4/5? → Stop. File `recovery-deferred`.
2. "Let's also fix X while we're here"? → No. File a GHI; honor the WIP cap.
3. Pointing 4.8 at an un-gated surface to "just clean it up"? → No. **Build the
   gate first.** A faster agent in front of a missing gate fills the tracker faster.
4. Writing more doctrine to explain the recovery? → This file is the only new
   doctrine. Refer to it; do not add to it.
5. Letting 4.8 make a doctrine/judgment call (#547, #549, #553)? → No. The covenant
   reserves final judgment for the human.

---

## 7. The single sentence to remember when context fragments

> **gzkit is in the mud because Moves 3, 4, and 5 stalled — the exact surfaces the
> June GHI flood is pouring onto. Build those three gates, then let Opus 4.8 sprint
> the harvest behind them. The model is the engine of the rescue, never a
> substitute for the gate. A smarter agent in front of missing gates just fills the
> tracker faster — so we build the gates first, in June, and dig out for good.**

---

## 8. When this plan is closed

Append a final dated section (do not delete the file — it is the durable proof gzkit
climbed out of the 4.7-era mud):

```
## Salvation closeout — <YYYY-MM-DD>
- emergency GHIs open: 0
- #517 failure classes gated: 5/5
- gz validate --skill-contracts: shipped <date>
- closeout-on-spine (Move 5): shipped <date>
- AGENTS.md size: <bytes>
- harvested Validated → Completed: <count> / 61
- GHIs/session-day vs 4.7 baseline: <before> → <after>
- mud status: out
```
