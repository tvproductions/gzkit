<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->
<!--
TEMPLATE — copy into the TARGET repo (not gzkit) when opening a flight-test
engagement. Fill every <…>. Delete this comment block. The program doctrine
this instance steers lives in gzkit at docs/flighttest/ and is target-agnostic;
this file is the engagement-specific steering surface, worked top-down.
-->

# Flight-Test Campaign — <TARGET> — <YYYY-MM-DD>

Status: **ACTIVE** (operator-ratified <YYYY-MM-DD>).

> **Distinct work-stream.** This campaign governs the flight-test engagement
> against **<TARGET>** to prove gzkit's workflows. It does **not** contend with
> gzkit's Build-to-1.0 Magna Carta — that plan rules gzkit's own build sessions;
> this one rules flight-test sorties against this target. Different work, no
> rivalry.
>
> **It steers; the program propels.** The doctrine (gzkit `docs/flighttest/`)
> and the `gz-flighttest` skill do the work; this plan only sequences the
> sorties. The flight log (`flight-log.md`) is the append-only truth; this
> checklist is a Layer-3 view of it. Amendments are operator-ratified and
> **append to the log, never inline-accrete** here.

> **Topmost (sequenced):** <the topmost unflown sortie whose entry gate is met>.
> Work-start is operator-gated: each sortie opens only on a recorded Go.

## Substrate

- **Target repo:** <path / remote>
- **Qualifies (README §7):** boring & bounded ⟨why⟩ · real-buildable ⟨why⟩ ·
  greenfield/near-cold ⟨state⟩ · separate repo ⟨confirmed⟩
- **Build-order payload:** <the real slices each spine sortie delivers into the target>

## The Queue — the daily driver

> Work top-down. Check a sortie off **only** with its Chase PASS verdict + the
> flight-log evidence cited. Green floor: no sortie opens while the target's
> `uv run gz check` is red.

- [ ] **S1 — Cold Start & Spine** *(center)* — the full canonical chain, `gz init` → PRD → Constitution → ADR → OBPI → implement → Gate-5 attest → closeout → sync.
- [ ] **S2 — Promotion & Decomposition** *(center-out)* — pool→promote, decomposition matrix, contract-bearing OBPI pipeline, traceability.
- [ ] **S3 — Defect & Issue Loops** *(expansion)* — GHI author/close/triage, defect-fix routing, brief & OBPI reconcile, simplify.
- [ ] **S4 — Integrity & Adversarial** *(corner)* — repudiate, withdraw, hook fail-closed, Layer-3≠truth, invariant coherence, corpus round-trip, validator sweep.
- [ ] **S5 — Quality & Maintenance** *(expansion)* — `gz check`, ARB, complexity, pythonic patterns, tech-debt, evaluate, tidy, mx hangar.
- [ ] **S6 — Release & Continuity** *(center-out)* — release ceremony, `gh` release, session-handoff create/resume, context load.

> Sortie definitions, test-point chains, and the coverage matrix are in gzkit
> `docs/flighttest/manifest.md`. A checked box here must trace to a flight-log
> entry with a Chase verdict.

## Amendment protocol

- Amendments are **operator-ratified**. Record the ruling (verbatim) in the
  flight log, then reflect it here.
- New sorties (coverage growth) are added to gzkit `docs/flighttest/manifest.md`
  first, then queued here.
- This file dies only by a ratified successor edition (new dated file).
