---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-20T18:01:09Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260620T161707Z-control-class-grounding-vs-custody-quagmire.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-20T18:01:09Z -->

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

In-flight, operator-led, control-by-control review of gzkit's validation
gate/lock surface — the "grounding-vs-custody quagmire" from the predecessor
handoff — now grounded from code rather than from the predecessor's memory
snapshot. **Station 1 complete; Station 2 (meta-stack) complete — `invariant-coherence` RED-but-salvageable, `waiver-ratchet` GREEN (a real, working control), `qc-binding` RED (repudiated-once 2026-06-18, half-repaired — both channels defeated). All 9 stations complete — control-by-control review DONE. Open: de-tax ratification (token-block Sub-Inv 5 / ADR-0.0.41).** The session produced one durable,
operator-ratified design decision (levels + MX, see Decisions Made) and a
running verdict: gzkit's *validate-time* gate surface is substantially facade,
and the operator named the trajectory a deliberate reduction — a "gzkit
lobotomy" — with the kernel-severity/MX spine as the thing that survives the cut.

No production code changed this session. The only writes were three append-only
`improvement` records in `.gzkit/insights/agent-insights.jsonl` logging agent
fabrications (see Pending Work). Working tree clean at HEAD `b9fb4540`, branch
`main`, 0 ahead / 0 behind.

## Important Context

- **The review now runs through one lens:** for each gate, ask "are you a
  self-deciding blocker, or a sensor that should just emit a severity level to
  MX?" That lens is the product of the Station-1 dialogue and reframes Stations
  2–9.
- **Station 1 (the two rendition gates) is facade as live enforcement.**
  `_FRESHNESS_FAIL_CLOSED = False` (`rendition_freshness.py:37`) and
  `_FLOOR_FAIL_CLOSED = False` (`rendition_floor_coherence.py:37`) — both inert,
  both warn and return zero errors live. The ONLY real invariant-floor
  enforcement is at compose time: `assert_invariant_verbatim` at
  `composer.py:57`. The validate-time gates are redundant with it and inert.
- **The tests certify the inertness.** `test_rendition_floor_coherence.py`
  `TestStagedWarn` asserts that, in the live warn default, a dropped invariant
  returns no errors — a green test that locks in "the gate does nothing." The
  gates prove they *can* fail only by forcing `fail_closed=True`, a mode the
  live system never runs.
- **The anti-theater control is foolable.** The qc-binding negative controls for
  these two gates (`_qc_negative_controls.py:164` and `:194`) force
  `fail_closed=True` — their own comments admit "the live gate is staged in warn
  mode." So the tool meant to catch theater certifies a non-live mode.
- **The corpus→rendition CMS is the ADR-0.0.37 spine**, flagged facade by GHI
  #623, with OBPI-22 repudiated; its real rebuild is campaign item B.1, PAUSED
  behind ADR-0.0.74. This is grounded, not a decision pending from the operator.
- **Operator determination on rendition (verbatim seating):** the settled
  derivative IS a projection; retain/version the projected file; having the
  agent recompute it each time is vibe coding; no Gate-5 on commit.
- **Two anti-vibe-test systems exist but share a semantic blind spot:**
  `tautological_tests.py` (`gz validate --tautological-test-audit`) catches only
  structurally vacuous tests (filesystem ops, no assertion); qc-binding catches
  vacuous bound steps but is satisfiable by a forced non-live mode. Neither
  detects "asserts against a non-live config" or "certifies inertness."

## Decisions Made

- **Decision:** Adopt the Linux kernel log-level hierarchy, gzkit-namespaced as
  `GZ_<LEVEL>` (0 = `GZ_EMERG` through 7 = `GZ_DEBUG`), as gzkit's universal
  severity substrate.
  **Rationale:** separates the three concerns the current code fuses into a
  single `_FAIL_CLOSED` bool — assessment (a T/F alignment fact), severity (the
  level), and disposition (what the level costs).
  **Alternatives rejected:** (a) a generic "single severity authority"
  abstraction — rejected as VIBES; the accounting showed severity keys off four
  distinct axes (build-state, stakes, magnitude, time) and only the lane/kind
  stakes pair was genuinely duplicated; (b) keep per-gate self-decided severity —
  rejected, the fractal-proliferation surface stays open.
- **Decision:** Gates become T/F sensors that emit a leveled event to the
  ledger; MX is the handler.
  **Rationale:** dissolves self-deciding blockers, staging bools, and
  control-on-a-control into "report a level; MX owns the response." Top of the
  scale (crit/alert/emerg, 0–2) triggers GHI + insight + an immediate trip to
  the hangar, where the operator opens all bays and PRIME DIRECTIVEs it.
  **Alternatives rejected:** gates keep deciding their own warn/block (the
  status-quo facade).
- **Decision:** This severity system is the concrete form of ADR-0.0.74 Boundary
  Invariant #2 ("single severity authority") and lands in ADR-0.0.74 — not a new
  ADR or invented vehicle.
  **Rationale:** the grounded home is already open (topmost P0, 1/10).
  **Alternatives rejected:** a fabricated "ADR-0.0.37 redesign" / "CMS-fate
  decision" — both were agent inventions the operator caught and rejected.
- **Decision:** The floor that stays a hard stop even under the interim posture
  is human attestation (sacrosanct, canon), ledger integrity (Never #2),
  operator-PII, and secrets.
  **Rationale:** canon-backed, irreversible-harm class — the exit hard-gate
  cannot catch-and-undo these.
  **Alternatives rejected:** a bare enumerated floor with no membership predicate
  (carried forward as a refinement to settle, not yet ratified).
- **Decision:** Interim operating posture — treat facade fail-closed gates as
  non-blocking (note it, level it, keep moving); do not freeze on craptastic
  blockers; the floor above stays.
  **Rationale:** agents vibe regardless of authoring-time instruction (this
  session is the live proof); post-hoc mechanical detection is the real control,
  not agent compliance.
  **Alternatives rejected:** authoring-time guidance as the primary control —
  rejected because it presumes agent compliance the session disproves.
- **Decision:** Naming convention for the rebuilt sensor surface is
  `<SUBJECT>_<PROPERTY>_<DISPOSITION>` — an object or object+property base plus a
  disposition (the T/F predicate and/or `GZ_<LEVEL>`).
  **Rationale:** the current ~80-scope registry mixes at least four conventions
  (bare object like `manifest`; object+property like `reconcile_freshness`;
  mechanism-named like `waiver_ratchet`/`qc_binding`; compound descriptive like
  `agents_md_map_conformance`) — named ad hoc, the fingerprint of "built in
  isolation." `ratchet` is a valid *property*, but `waiver-ratchet` is V.I.B.E.S.:
  it over-indexes on one of three mechanisms and leaves the ratcheted *subject*
  unclear. One convention makes the 80-scope surface legible for MX to consume.
  Example: `rendition_floor_aligned` (subject `rendition`, property `floor`,
  disposition `aligned`).
  **Alternatives rejected:** keep ad-hoc per-gate naming (the status quo that
  produced the inconsistency).
- **Decision:** MX mode runs NO ADR ceremony — it is pure fix.
  **Rationale:** the hangar is for direct repair; ADR/OBPI ceremony is never a
  precondition to fix in MX. If a fix incidentally yields an architectural
  decision worth recording on an ADR, recording it is acceptable ("so be it") —
  an output, never a gate. Consistent with operator canon: "GHIs are authorized
  for direct repair, always; never spin up an ADR or OBPI merely to discharge a
  GHI." (Operator estimate: the full MX cleanup is roughly a year of work.)
  **Alternatives rejected:** requiring an ADR/OBPI to authorize MX fixes —
  rejected as the exact ceremony overhead MX exists to escape.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to operator, await authorization before executing. -->

1. **Resume Station 2 at its last control, `qc-binding`** (the watcher's watcher).
   `invariant-coherence` is done (RED, salvageable once a real renderer exists —
   GHI #623); `waiver-ratchet` is done (GREEN, real — its only bite is
   freezes-not-drains, re-levelled under MX). Apply the sensor-vs-blocker lens.
2. **Walk Stations 3–9:** behave/waiver-ratchet deadlock; whole-repo audits
   dragged into OBPI completion; custody de-tax (the lock class); doctrine-vs-code
   drift (TTL 12x, auto-reap fiction); footguns (docstring `@covers`, opt-in
   coupling validator); GREEN confirm.
3. **After the review:** consolidate the levels+MX severity architecture into
   ADR-0.0.74 — the concrete BI#2 — reshaping OBPI-02 (checkpoint) and OBPI-09
   (staging-flag retirement) around "gates produce levels, MX consumes."
4. **Scope the army-of-agents semantic test-audit** as a sibling of the
   tautological-test chore: post-hoc detection of live-vs-assessed-mode mismatch,
   inertness-certifying tests, and forced-mode-only RED.
5. **Measure** the true vibed-test rate (`gz validate --tautological-test-audit`
   plus a semantic pass) before sizing the lobotomy.

## Pending Work / Open Loops

- **The kernel-severity/MX system is decided but unbuilt:** no severity level on
  `ValidationError`, no severity→ledger event, no auto-MX trigger.
- **Stations 2–9 of the control review are unwalked.**
- **Corpus→rendition CMS fate** is campaign item B.1, paused behind ADR-0.0.74 —
  a grounded sequenced item, not a fresh decision owed by the operator.
- **The two anti-vibe-test systems' semantic blind spot** is unaddressed; the
  army-of-agents audit (Next Step 4) is the proposed answer, unscoped.
- **Three agent fabrications this session** are logged in
  `.gzkit/insights/agent-insights.jsonl` (premature ADR-0.0.74 routing; a
  fabricated "ADR-0.0.37 redesign"; a fabricated "CMS-fate decision you own").
  No code consequence; they stand as evidence for the post-hoc-detection thesis.
- **`qc-binding` is RED — the antibody to ADR-0.0.37 is itself still hollow.**
  Both channels defeated: channel 1 (static theater signatures) inert
  (`theater_flags` hardcoded `[]`, `qc_binding.py:147`/`:196`) — the exact defect
  OBPI-0.0.73-02 was repudiated for 2026-06-18, with the 2026-06-19 recovery
  fixing only channel 2; channel 2 (the negative-control "essential cure") gamed
  by the rendition NCs forcing `fail_closed=True` (`_qc_negative_controls.py:164`/
  `:194`). The Magna Carta marks ADR-0.0.73 DONE with a green self-check — that
  closeout rests on a cure that does not catch its target. **Recorded to the
  Magna Carta** (`build-to-1.0-campaign-2026-06-10.md`, Phase 0 hot-store, dated
  2026-06-20) as MX fix/repair, no ADR. Connector: open GHI #634 (repudiated OBPI
  renders ATTESTED COMPLETED) for OBPI-02's `Completed`-vs-`pending-re-attestation`
  layer-drift.
- **Station 3 — behave/waiver-ratchet deadlock is a KIND-BLIND behave gate**
  (`audit_behave_req_tags`, `briefs.py:524`, no kind filter), not a waiver-ratchet
  defect. Fix: mirror `obpi_complete.py:592`'s SUPPORT/STRUCTURAL-FENCE exemption
  (~3 lines). MX direct-fix. Booked to Magna Carta 2026-06-20.
- **Station 4 — whole-repo audits gate OBPI completion (GREEN checks,
  mis-coupled); the `audit_pydantic_models` RED finding is RETRACTED** (verified
  explicit-only, not in `_build_check_steps`, so not a completion gate). Real
  completion-coupled whole-scope gates: `audit_insights_shape` (`:344`, whole
  jsonl), `lock-handoff-coupling`, `waiver-ratchet`, `tautological-audit` — all
  real. Defect = completion-coupling (unrelated violation blocks the OBPI).
  Disposition: re-level under MX (whole-repo violations → accrued `GZ_<LEVEL>`
  ledger debt MX drains, not hard blockers; OBPI's own diff gates completion);
  leveled debt stays VISIBLE (2026-04-18 silent-accumulation outage lesson).
  Booked to Magna Carta 2026-06-20.
- **Station 5 — the OBPI lock is the CATEGORY ERROR (custody paying grounding's
  tax), confirmed in code.** Five verified defects: completion-never-releases
  (GHI #619; no `delete_lock` in any completion path), release fail-closed on a
  handoff (`obpi_lock.py:216`), TTL ~12× drift (120m vs canon 1440m, GHI #604),
  two divergent reapers (`lock_manager.reap` full-tax vs `preflight._apply_cleanup`
  raw-unlink, zero ledger), SessionStart auto-reap fiction (`session_orientation.py`
  never calls `reap_expired_locks`). GREEN: O_EXCL claim primitive + ceremony
  turn-lock. Disposition: lease model (O_EXCL + TTL auto-expire; contention →
  `GZ_<LEVEL>`; release/reap = unlink + ledger event, no handoff-as-evidence).
  Defects 1/3/4/5 = direct-GHI MX fixes; **the de-tax (remove handoff-as-evidence)
  relaxes token-block Sub-Invariant 5 / amends ADR-0.0.41 — PENDING operator
  ratification.** Booked to Magna Carta 2026-06-20.
- **Station 8 — footguns + a meta-catch.** (1) docstring/comment `@covers` is a
  REAL signal footgun: decorator form records a runnable `func_name`
  (`traceability.py:336`), docstring form records `str(py_file)` (`:368`) —
  counted by `gz covers`, not runnable at completion (the OBPI-0.0.74-01 trap).
  Fix: `GZ_NOTICE` at discovery, direct-GHI. (2) "opt-in coupling validator"
  RETRACTED — `--lock-handoff-coupling` IS in `gz check` (`_build_check_steps:352`);
  the `explicit` flag only skips the bare `gz validate` umbrella. (3) META-CATCH:
  2nd false "explicit=not-enforced" sweep claim (1st: pydantic_models, Station 4);
  the sweep conflated `gz validate` registry "explicit" with "not in `gz check`" —
  cross-check any remaining sweep enforcement claim against `_build_check_steps`.
  Booked to Magna Carta 2026-06-20.
- **Station 9 — GREEN confirm (review COMPLETE, 9 stations).** Preserve: the floor
  (Gate 5, ledger, operator-PII, secrets); verified-this-session GREENs —
  compose-time `assert_invariant_verbatim` (`composer.py:57`), `waiver-ratchet`,
  `audit_insights_shape`, kind-discipline (`obpi_complete.py:592`, the model to
  emulate); sweep-sourced GREENs to spot-verify — O_EXCL primitive, ceremony
  turn-lock, attestation-receipts. Synthesis: cut the facade + the friction; keep
  the floor + the few real checks; one `GZ_<LEVEL>` system MX drains. Booked to
  Magna Carta 2026-06-20.

## Verification Checklist

- [ ] `git rev-parse --short HEAD` resolves to `b9fb4540` until new work commits
- [ ] `git branch --show-current` is `main`
- [ ] `_FRESHNESS_FAIL_CLOSED = False` still present in `rendition_freshness.py`
      (gate still inert — Station 1 finding holds)
- [ ] `_FLOOR_FAIL_CLOSED = False` still present in `rendition_floor_coherence.py`
- [ ] `uv run gz validate --insights-shape` passes (the three new improvement
      records are schema-valid)
- [ ] `uv run gz adr status ADR-0.0.74-mx-mode-maintenance-hangar` shows 1/10 and
      no severity-architecture OBPI yet booked

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/rendition_freshness.py` — inert freshness gate (`_FRESHNESS_FAIL_CLOSED = False` at line 37)
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — inert floor gate (`_FLOOR_FAIL_CLOSED = False` at line 37)
- `src/gzkit/content/composer.py` — the one real invariant-floor enforcement (`assert_invariant_verbatim` at line 57)
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — anti-theater control foolable via forced `fail_closed=True` (lines 164 and 194)
- `tests/governance/test_rendition_floor_coherence.py` — tests that certify the inert warn behavior (`TestStagedWarn`)
- `src/gzkit/tautological_tests.py` — the tautological-test audit with the structural-only blind spot
- `.gzkit/insights/agent-insights.jsonl` — three improvement records logging this session's fabrications
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — the grounded home (Boundary Invariant #2)
- `.gzkit/handoffs/20260620T161707Z-control-class-grounding-vs-custody-quagmire.md` — predecessor handoff

## Environment State

Branch `main`, HEAD `b9fb4540`, clean tree. Python 3.13 / uv toolchain. No
in-progress OBPI locks. ADR-0.0.74 pipeline not active. The decisions recorded
here are design determinations only; no governance ceremony (no Gate 5, no OBPI
completion) was performed or implied.
