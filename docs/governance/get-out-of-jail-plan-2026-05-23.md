# Get Out of Jail — Recovery Plan, 2026-05-23

> **Read this if you opened it cold.** This is the recovery plan written
> the day GHI #517 (5-alarm structural emergency), GHI #519 (Codex 258K
> window collapse), and `docs/governance/model-regression-deep-dive-2026-05-23.md`
> all landed in the same session. The diagnosis is done. This document
> is the action plan. **Sobriety. No new doctrine. No new foundation ADRs.
> No three-model review. Move what's already authored from pool to
> shipped.**

## Why this plan exists

GSD (`gsd-build/get-shit-done`, now `open-gsd/get-shit-done-redux`) is
beating gzkit on the territory between SuperPowers' archipelago and
gzkit's empire — not because GSD is lighter, but because:

1. **GSD's surface is task-routed, not always-loaded.** Their 49 KB
   `planner.md` loads only when planner fires. gzkit's 30 KB `AGENTS.md`
   sits in every turn.
2. **GSD's spine is typed code with mechanical discovery.** Module
   Interfaces, Adapters, Builders, a Command Routing Hub with a closed
   `errorKind` enum. gzkit's spine is prose with validators bolted on.
3. **GSD's tests are boring gates.** 70% line coverage, fail the build.
   gzkit's REQ-coverage gate passed an ADR where the AND-clause REQ was
   half-missing (GHI #517 Failure 4).
4. **GSD has no Layer 1/2/3, no lifecycle ceremony, no 1:1 sync mandate.**
   `Completed` is not a state to harvest. Their lifecycle has no terminal
   ceremony that can jam.

gzkit's prior art already designs the answer to every one of those.
**The bottleneck is promotion velocity, not insight.** This plan
unlocks promotion velocity on a 14-day timeline.

## Definition of "out of jail"

You are out of jail when **all** of these hold:

- [ ] Root `AGENTS.md` is ≤ 5 KB and is a router, not an encyclopedia.
- [ ] `gz context <ADR-ID>` exists as a CLI verb and produces a focused
      Markdown payload (ADR + OBPI briefs + related tests + applicable
      rules) suitable for piping to any agent harness.
- [ ] A namespace-router skill layer exists (`/gz-workflow`,
      `/gz-governance`, `/gz-quality`, `/gz-project`, `/gz-context`,
      `/gz-manage`) — small intent tables, no duplicated ceremony.
- [ ] At least four canonical skills declare `inputs:` / `outputs:`
      frontmatter, validated by `gz validate --skill-contracts`.
- [ ] Closeout ceremony reads structured `REQ → Evidence` data from a
      `CeremonyStore` port (ADR-0.0.3 spine), not extracted shell.
- [ ] `lifecycle_status: Completed` is harvested for ≥ 50 of the 61
      currently-Validated ADRs as a side effect of closeout being fixed.
- [ ] A normal Codex/Claude session can carry an ADR through plan →
      implement → verify → closeout within a 200K token budget without
      orientation rereads.

If those seven hold, gzkit is shipping on GSD's architectural footing
using its own foundation. Stop the plan there.

## What you must NOT do during these 14 days

| Anti-temptation | Why it stays banned |
|---|---|
| Author a new `0.0.59+` foundation ADR | Foundation churn is the bug. The five-failure ceremony of #517 happened on a fresh 0.0.x. Pause until the spine ships. |
| Run a three-model review of #517 | The deep-dive packet is already 17 KB. More diagnosis ≠ more action. |
| Promote more than the four pool ADRs named in this plan | Pool overhang is a context-load problem. Don't worsen it. |
| Write a new doctrine page in `docs/governance/` | Same reason. This file is the only new doctrine permitted. |
| Fix in-flight defects discovered during these 14 days | File to GHI with `recovery-deferred` label. Triage after. |
| "Improve" `gz-adr-closeout-ceremony` SKILL.md in place | Replace via Move 5. Patching the prose is the wrong layer. |
| Add a new `gz validate --…` scope outside the ones this plan names | Validator proliferation is part of the current load problem. |
| Touch the 5:1 governance-to-output mantra | The mantra is true *iff* the 5x is mechanical. Earn it back by shipping the spine; don't restate it. |

## Prequel (Day 0) — Universal queue collapse

Before Move 1 can promote a pool ADR into a coherent product-semver position,
the existing feature-ADR queue must be honest. As of 2026-05-23, `pyproject.toml`
is at `0.26.6` and the last Validated feature ADR is `0.26.0` — but `0.27.0`–
`0.51.0` sit as `Pending` feature ADRs, effectively all `0/N` OBPI completion.
That's a 25-deep queue of unkept release promises blocking the next-shippable
minor. The kind-table doctrine reads feature = *"Active/committed (or queued)
release-carrying capability"*; "queued" was supposed to mean "next up," not
"claimed slot 24 deep."

### Mechanical rule (binding, no per-ADR judgment)

> Every feature ADR in `Pending` lifecycle is demoted to pool. ID becomes
> `ADR-pool.<slug>`. Frontmatter `kind` and `semver` are stripped. Any
> declared OBPI brief files under the demoted ADR are deleted — pool ADRs
> are uncommitted by doctrine and do not carry OBPIs; briefs are
> re-authored if the ADR is later re-promoted.

**Scope:** `0.27.0`–`0.51.0`, all 25 ADRs. The two with token (1/5) OBPI
progress (`0.40.0-reporter-render`, `0.47.0-owasp-top10`) are included — the
operator's call 2026-05-23 is that those partial OBPIs were model hiccups,
not in-flight work, so they demote with the rest. Seven of the 25 carry a
pre-existing pool-slug counterpart (a promote-bug or fork artifact) and demote
via `--on-collision keep-pool`, deleting the feature package and leaving the
existing pool ADR untouched; the ledger event records `collision_resolution`.

**Tracking:** Single GHI [#520](https://github.com/tvproductions/gzkit/issues/520)
(`adr-taxonomy: 24-deep Pending feature queue blocks recovery semver`; the
GHI title undercounts by one — actual queue depth is 25, captured here and
in the sweep ledger events), labeled `defect`, `runtime`, `tech-debt`,
`recovery-prerequisite`. Authored via `/ghi-author` 2026-05-23 (per Behavior
Rule — Always #13). Every `artifact_renamed` event in the sweep carries
`"reason": "pool_demotion"` and `"ghi": 520` in its payload for narrative
anchor and re-litigation context. GHI closes `fixed` against the sweep commit
SHA when the 25 demotions land.

**Tooling prerequisite:** `gz adr demote` does not exist as of 2026-05-23.
Build it as a single Day-0 housekeeping deliverable (single GHI, no new
ADR), mirroring `gz adr promote`'s schema-edit + file-move + ledger-event
pattern. Demotion emits an `artifact_renamed` ledger event with
`reason="pool_demotion"` and `extra={prior_kind, prior_semver, demoted_at,
ghi, operator?, note?}` — reusing the existing event factory (per Q5=a
2026-05-23) rather than introducing a new event type. The `new_id` lives
on the rename event itself, not in extras. Pool file stays clean (no
`previously:` frontmatter); history is queryable via `gz state <pool-id>`
per state doctrine (Layer 2 ledger = source of truth for state transitions).

**After the prequel:**
- Highest active feature ADR = `0.26.0`
- Next promotion lands at `0.27.0`, restoring coherence with `pyproject.toml = 0.26.6`
- Recovery promotions slot into `0.27.0`–`0.30.0` for Moves 1, 2, 4, 5

### Footnote 1 — Deferred taxonomy review (recorded 2026-05-23)

The prequel enforces *existing* doctrine. It does **not** address a deeper
structural question surfaced by the operator 2026-05-23: the
foundation/feature/pool taxonomy inherited from airlineops has soft edges
that allowed this sprawl to accumulate unnoticed. Specifically:

1. **Pool intent-tagging is missing.** Pool ADRs have no `kind:` frontmatter,
   so "feature-shaped or foundation-shaped?" must be rediscovered at every
   triage.
2. **"Queued feature" is functionally indistinguishable from pool.** A
   feature ADR at `Pending` / `0/N` is identical to a pool ADR except for
   load-bearing a semver slot it has no plan to deliver.
3. **Kind classification may have drifted.** Some pool ADRs may be better
   suited as foundations; some Pending features (before this prequel) may
   have been foundations all along.
4. **No commitment-state axis separate from kind.** Currently `kind`
   conflates "what the ADR is about" with "what stage of commitment it's in."

**Operator position:** The taxonomy is not abandoned — it carries genuine
signal from airlineops — but the edges need sharpening. The right venue
for that sharpening is a post-recovery foundation ADR, not patches during
the 14 days.

**This footnote is the trace.** When recovery is closed, file the
taxonomy-sharpening work as a foundation ADR candidate (or a pool ADR
that promotes to foundation when committed). Captured questions to seed
that work:

- Should pool items carry an optional `kind:` frontmatter for intent-tagging?
- Should "commitment state" be a third axis orthogonal to `kind` and `lane`?
- What additional fields belong on the `adr_demoted` ledger event for
  re-promotion ergonomics (e.g., should `prior_obpi_briefs` be archived
  references rather than fully deleted)?
- What are the migration semantics when a pool ADR is re-promoted to a
  *different* `kind` than its prior life?

## The plan — five moves, 14 days, every move cites prior art

### Move 1 (Days 1–2) — Promote the namespace router

**Cite:** `docs/design/adr/pool/ADR-pool.namespace-router-product-surface.md`
(`inspired_by: gsd`, lists six routers).

**Why first:** Highest leverage. Single ADR that lets every later move
discover its skill instead of inlining doctrine into AGENTS.md.

**Actions:**

- [ ] `uv run gz adr promote --kind feature ADR-pool.namespace-router-product-surface`
- [ ] Author exactly three OBPIs under the promoted ADR:
  - OBPI-A: build the six router skill files (`gz-workflow`,
    `gz-governance`, `gz-quality`, `gz-project`, `gz-context`,
    `gz-manage`) — each ≤ 500 bytes, intent table only, no procedure.
  - OBPI-B: register the routers in the canonical skill list +
    refresh control surfaces (`uv run gz agent sync control-surfaces`).
  - OBPI-C: add `gz validate --router-tables` (mechanical check that
    every routed skill exists and every concrete skill is reachable
    from at least one router).
- [ ] Lane: **lite** for OBPI-A/B; **lite** for OBPI-C if it stays under
      ~150 LoC, otherwise **heavy**. Do not let it grow.

**Done when:** Six router skill files exist; `gz validate --router-tables`
passes; the router skills appear in `uv run gz skill list`.

---

### Move 2 (Days 3–5) — Ship `gz context <ADR-ID>`

**Cite:** `docs/design/adr/pool/ADR-pool.focused-context-loader.md`
(`inspired_by: openspec`, scope is one new verb).

**Why second:** The router from Move 1 needs a payload to point at.
`gz context` is that payload. Together they replace "load 30 KB
AGENTS.md every turn" with "load 3–5 KB router + invoke `gz context`
once per ADR session."

**Actions:**

- [ ] `uv run gz adr promote --kind feature ADR-pool.focused-context-loader`
- [ ] Author two OBPIs:
  - OBPI-A: implement `gz context <ADR-ID>` — outputs target ADR file
    + OBPI brief contents + related test file paths (via `@covers`
    decorators or naming convention) + applicable rules (lane, current
    gate, next required action). Output: single Markdown document.
  - OBPI-B: implement `gz context --slim <ADR-ID>` (omit governance
    rules; for non-governance agents).
- [ ] Lane: **lite**. Single new verb, no schema change.
- [ ] Update `.gz-context/` router from Move 1 to reference this verb
      as its primary entry.

**Done when:** `uv run gz context ADR-0.0.3` produces a single Markdown
payload < 30 KB suitable for piping to Codex / Claude / any harness.
Note token budget: a single ADR + its briefs should land under 20 KB
for any non-pathological foundation; flag tracking ADRs over 30 KB as
candidates for decomposition.

---

### Move 3 (Days 6–8) — Shrink AGENTS.md to ≤ 5 KB router boot manifest

**Cite:** `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/`
(Validated foundation, 4 OBPIs already authored but never delivered as
a context-collapse outcome).

**Why third:** The router and context loader exist now. AGENTS.md can
finally become what ADR-0.0.54 always said it should be: a map, not an
encyclopedia.

**Actions:**

- [ ] Re-open the four OBPIs under ADR-0.0.54. Do NOT re-author. Audit
      against current AGENTS.md state.
- [ ] Lift the prose sections currently in AGENTS.md to skill-routed
      docs under `docs/governance/` (per existing `gz-context-diet`
      skill, which already does this). Each lifted section gets a
      ≤ 1-line pointer back in AGENTS.md.
- [ ] Target shape for the new AGENTS.md (illustrative):
  ```
  # AGENTS.md
  - Project: gzkit
  - Stack: Python 3.13+ / uv / ruff / ty
  - Boot: read this file, then `gz state` and `gz status`
  - Routers: see .claude/skills/gz-workflow/, gz-governance/, ...
  - First load on every ADR session: `gz context <ADR-ID>`
  - Invariants (hard binding):
    1. Do not bypass Gate 5 attestation
    2. Do not edit `.gzkit/ledger.jsonl` directly
    3. Operator PII never in repo-bound artifacts
    4. `uv run` for every Python command
  - Failure-mode taxonomy: .claude/rules/agent-failure-modes.md
  - Routing details: see specific router skills
  ```
- [ ] Update the `instructions-files-budget` validator default for
      `AGENTS.md` from 40 KB to 5 KB.
- [ ] Run `uv run gz validate --invariant-coherence` — adjust the
      composed registry until it accepts the lean shape.

**Done when:** Root `AGENTS.md` ≤ 5 KB; `gz validate --invariant-coherence`
passes; `gz check` is green; a fresh session reads AGENTS.md +
optionally a router + `gz context` and has everything needed.

---

### Move 4 (Days 9–11) — Typed skill contracts (the mechanical glue between islands)

**Cite:** `docs/design/adr/pool/ADR-pool.intent-stage-skill-composition.md`
(four-skill Intent stage, GHI #429 evidence of stub-level skills with
no documented Inputs/Outputs/handoff).

**Why fourth:** This is gzkit's answer to GSD's CONTEXT.md predicate
database / Module Interfaces. Without it, skills remain prose islands.
With it, the seams are data, validated at runtime.

**Actions:**

- [ ] `uv run gz adr promote --kind feature ADR-pool.intent-stage-skill-composition`
- [ ] Author one OBPI per cluster, starting with Intent stage:
  - OBPI-A: extend skill frontmatter schema to permit `inputs:` and
    `outputs:` blocks (Pydantic model addition; one schema file).
  - OBPI-B: populate `inputs:` / `outputs:` on the four Intent-stage
    skills (`gz-prd`, `gz-constitute`, `gz-design`, `gz-adr-create`).
    Outputs MUST cite the produced artifact path/glob. Inputs MUST
    cite upstream artifact path/glob.
  - OBPI-C: implement `gz validate --skill-contracts` — at skill
    invocation, the declared `inputs:` MUST exist on disk; the
    declared `outputs:` MUST exist or be produced. Fail-closed.
- [ ] Lane: **heavy** (schema change). All three OBPIs ride one ADR.

**Done when:** Four Intent-stage skills declare typed contracts; `gz
validate --skill-contracts` passes; running `gz-design` without a
present PRD/Constitution fails with a clear error pointing at the
missing input.

---

### Move 5 (Days 12–14) — Redirect GHI #516 to ride the hexagonal spine, NOT a new ceremony

**Cite:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/`
(Validated foundation; FileStore/ProcessRunner/LedgerStore/ConfigStore
protocols + AST policy tests already define the pattern).

**Why fifth:** Closeout ceremony is the broken pillar (GHI #516, five
failures in one walkthrough). The fix is not a new validator and not a
rewritten ceremony. The fix is a `CeremonyStore` port + a structured
`ReqEvidence` model, consumed by a re-shaped closeout that no longer
extracts shell from prose.

**Actions:**

- [ ] Re-label GHI #516 with `recovery-move-5`. Add a comment redirecting
      the remediation route from "design a new ceremony" to "consume
      ADR-0.0.3's ports."
- [ ] Author one focused feature ADR (NOT a foundation):
  `ADR-pool.closeout-ceremony-on-hexagonal-spine` (promote immediately
  to feature on author) — Decision: closeout walks structured
  `ReqEvidence` produced by a `CeremonyStore` adapter; brief schema
  gains `req_evidence:` frontmatter; AND-clause REQs rejected at brief
  authoring time; `--next` blocked at Gate 5 boundary in the ceremony
  state machine.
- [ ] Three OBPIs:
  - OBPI-A: brief schema add `req_evidence: [{req: REQ-X.Y.Z-NN-MM,
    file: path, anchor: "…", assertion: "…"}]` field; reject AND-clause
    REQ text at authoring.
  - OBPI-B: `CeremonyStore` port in `gzkit/core/ports/`;
    `LocalCeremonyStore` adapter in `gzkit/adapters/`. AST policy test
    enforces the import boundary (already in ADR-0.0.3 enforcement).
  - OBPI-C: closeout walkthrough renders `req_evidence` data; refuses
    to advance past Gate 5 step without explicit `--attest`.
- [ ] Lane: **heavy** (schema + runtime contract).

**Done when:** Running closeout on an ADR with stale anchors fails at
preflight (not at operator visual inspection); `--next` cannot bypass
Gate 5; the 61 currently-Validated ADRs become eligible for closeout
without ceremony-as-verification-layer.

---

## Harvest (Days 15–21, after exit)

This is **after** out-of-jail, not part of the 14-day plan. Listed for
continuity so you don't lose the thread.

- Re-run closeout on the 61 Validated ADRs. Expect most to harvest
  cleanly to `Completed` now that closeout has teeth and reads
  structured data. Bookkeeping should match reality.
- Promote `ADR-pool.canonical-vs-runtime-separation` once closeout
  ships — receipts move out of canonical surfaces.
- Triage the remaining pool ADRs against the post-recovery shape. Many
  pool ADRs that look important today will be redundant once the
  router + context loader + typed contracts ship.

## Anti-temptation tripwires

If any of these surface during the 14 days, stop and re-read this file:

1. You catch yourself drafting a new foundation ADR. → Stop. File to
   GHI with `recovery-deferred`.
2. A subagent suggests "let's also fix X while we're here." → No. File
   to GHI.
3. You consider running a multi-model diagnosis. → No. The diagnosis
   exists. Execution is the bottleneck.
4. You start "improving" SKILL.md prose on a broken ceremony. → No.
   Replace via Move 5.
5. You feel the urge to write more doctrine to explain the recovery. →
   This file is the only new doctrine. Refer to it; do not add to it.

## The single sentence to remember when context fragments

> **gzkit's best ideas are already in `docs/design/adr/pool/`. Move
> five of them to shipped (router, context-loader, skill-contracts,
> closeout-on-spine) and you have GSD's footing on your own foundation.
> Stop authoring new ones until those five ship.**

## Files this plan touches (no surprises)

- New: this file (`docs/governance/get-out-of-jail-plan-2026-05-23.md`)
- Promotes from pool: `ADR-pool.namespace-router-product-surface`,
  `ADR-pool.focused-context-loader`,
  `ADR-pool.intent-stage-skill-composition`
- Authors new feature ADR: `closeout-ceremony-on-hexagonal-spine` (Move 5)
- Re-harvests existing OBPIs under: `ADR-0.0.54` (Move 3),
  `ADR-0.0.3` (Move 5 leans on it; no new OBPI there)
- Validator additions (capped at three): `--router-tables`,
  `--skill-contracts`, and the brief-schema REQ-evidence check (folded
  into existing `--documents` / `--brief-reconcile` rather than a new
  scope where possible)

## When this plan is closed

Close this file by appending a final dated section:

```
## Recovery closeout — <YYYY-MM-DD>
- AGENTS.md size: <bytes>
- gz context: shipped <date>
- routers: <list>
- typed-contract skills: <list>
- closeout-on-spine: shipped <date>
- harvested Validated → Completed: <count>
- jail status: out
```

Do not delete the file. It is the durable proof gzkit climbed out, and
the template if anything like this happens again.
