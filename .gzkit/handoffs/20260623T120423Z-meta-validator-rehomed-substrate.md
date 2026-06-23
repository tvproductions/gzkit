---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-23T12:04:23Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: cb752202
session_id:
continues_from: .gzkit/handoffs/20260623T084256Z-sizing-enforcement-claim-meta-validator.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-23T12:04:23Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

**Extra caution this chain:** the predecessor handoff
(`20260623T084256Z-sizing-...`) advised "open a new **foundation** ADR." Following
that uncritically caused a §3a violation this session (foundation kind is
abolished). Test every advised step below against the active campaign BEFORE
acting — see § Campaign Consistency Check.

## Current State Summary

Three repairs landed on `main` this session (all pushed; working tree clean):

- **GHI #637 (CLOSED, commit `b7f2f58c`)** — the leveled MX checkpoint pipeline
  (`checkpoint.resolve` / `disposition.route` / `levels` `GZ_<LEVEL>`) had **0
  production consumers** despite OBPI-0.0.74-12 being attested COMPLETED (a
  facade). Fixed: added `disposition.grounds(route)`; migrated
  `validate_cmd._run_scope_checks` (all scopes) + `rendition_freshness` +
  `rendition_floor_coherence` from the boolean `is_advisory` to
  `disposition.grounds(checkpoint.resolve(name, levels.ERROR, root))`;
  re-expressed `is_advisory` as a thin delegate over `resolve()`.
  Semantics-preserving (`TestLeveledConsumptionEquivalence`). `unittest` 6398
  exit 0.
- **GHI #638 (OPEN, routing note)** — gates-as-sensors residual: the `gz check`
  step layer (~30 steps in `quality.py` + ~5 solo `validate_cmd` paths:
  qc-binding, fidelity-presence, waiver-ratchet, unscoped-rules,
  handoff-document-audit, dispatch-attestation) still self-decide fatality
  (`returncode=3` / `SystemExit(3)`) outside the checkpoint. A Codex cross-model
  review REFUTED the in-session "gates-as-sensors complete" claim. Destination =
  a future OBPI under ADR-0.0.74; deferred per operator.
- **GHI #639 (CLOSED, commit `cb752202`)** — ADR-0.0.75 was booked with
  `kind: foundation`, contradicting campaign §3a. Corrected: demoted ADR-0.0.75
  to pool (`ADR-pool.enforcement-claim-meta-validator`), withdrew
  OBPI-0.0.75-01..05, and re-homed the meta-validator design VERBATIM as
  **OBPI-0.0.74-15..19** under the MX hangar / 0.29.0 feature.

The enforcement-claim meta-validator (campaign Movement I item 3, §5's "floor's
teeth") is now seated as **OBPI-0.0.74-15..19 (Draft/authored, NOT
implemented)**. Nothing is implemented or attested — all of the above is
authored governance plus the one `b7f2f58c` code repair.

## Important Context

- **ADR-0.0.74 is now the single locus of substrate work**: the MX kernel
  (campaign line 221) + the gates-as-sensors residual (GHI #638) + the
  meta-validator (OBPI-15..19), all converging on release **0.29.0**.
- **Two axes, do not conflate them** (this distinction cost a refuted claim this
  session): *MX-demotability* (does a guard route severity through the checkpoint
  so it demotes under the hangar marker — campaign line 220) is ORTHOGONAL to
  *NC-falsifiability* (does an enforcement claim have a live negative control —
  the meta-validator). GHI #637 advanced the first for the `gz validate`
  dispatcher; GHI #638 is its residual; the meta-validator is the second.
- **`resolve_fence_proof` is in `src/gzkit/req_kind.py` (~line 91), NOT
  `closeout_proof.py`** — the sizing handoff had this wrong; OBPI-18 depends on
  the correct module.
- **Honest negative (OBPI-17):** `secrets` and `operator-pii` have **no bound
  gate5 production entrypoint today**. The brief forbids binding a narrower proxy
  to fake a live NC — the real production path may need to be built first.
- **The existing 33 qc_binding NCs force `fail_closed=True`** — the forbidden
  forced-mode pattern §5 names. OBPI-16 re-authors them un-forced.
- **"max vibes" finding:** the heavy ADR ceremony (gz-design → gz-adr-create →
  gz-adr-evaluate 4.0/4.0 → green builds) blessed a decision that contradicted
  the campaign at its root. The gates check SHAPE, not TRUTH. The recourse is the
  floor (§5), not more ceremony (campaign §2a). See § Decisions Made.

## Decisions Made

- **Decision:** Fix GHI #637 as a direct fix; leave OBPI-0.0.74-12 as-is (GHI is
  the repair record), not repudiated.
  **Rationale:** GHI-tracked defect repair routes to direct fix (operator canon).
  **Alternatives rejected:** `gz obpi repudiate` OBPI-12 (operator chose leave-as-is).
- **Decision:** Re-home the meta-validator under ADR-0.0.74 as OBPI-15..19;
  demote ADR-0.0.75 to pool.
  **Rationale:** campaign §3a abolished `foundation`; §5 ties the meta-validator
  primitive to the floor + MX exit gate (both ADR-0.0.74); §2/§2a forbid ADR
  accretion. No new ADR.
  **Alternatives rejected:** keep ADR-0.0.75 as foundation (contradicts §3a);
  re-cast as a `feature` ADR (operator chose the fold into 0.0.74).
- **Decision (meta-validator design, booked):** D1 — NCs trigger through the real
  production path; forcing kwargs forbidden; the 33 qc_binding NCs re-authored
  un-forced. D2 — runner-driven `@enforces(claim, fixture, entrypoint)` contract
  (runner invokes the real path; forcing impossible by construction). D3 — strict,
  NO debt (no `_NEGATIVE_CONTROL_DEBT` escape; floor-wiring lands LAST).
  **Rationale:** genuineness must be absolute and structural, not heuristic; §5 is
  the purest reading.
  **Alternatives rejected:** second parallel NC system; NC-as-callable + static
  no-force guard; shrink-only debt ratchet; free-prose scanning in v1 (deferred
  extension F).
- **Decision:** Highest-leverage recourse to the "max vibes" failure is to make
  the §3a `foundation`-abolition a real fail-close, not a sentence.
  **Rationale:** the schema enum still permits `kind: foundation`, so nothing
  blocked ADR-0.0.75 at creation — a facade enforcement claim. A live NC
  (`--kind foundation` → assert exit != 0) would have blocked the entire detour
  at the first command.
  **Alternatives rejected:** rely on agent diligence (exhortation, not structural).
  **Sequencing (operator ruling 2026-06-23, "as is in movement iii"):** stays in
  Movement III — NOT pulled forward into Movement I; deferred behind the Movement I
  substrate per the campaign's top-down sequence.

## Immediate Next Steps

ADVISORY ONLY — present to the operator and obtain authorization before acting.
All are **Movement I** work converging on ADR-0.0.74 / release 0.29.0. NONE is a
new foundation ADR.

1. **Scope an OBPI under ADR-0.0.74 for the GHI #638 gates-as-sensors residual**
   (migrate the `gz check` step layer + ~5 solo `validate_cmd` paths through the
   checkpoint) — completes campaign line 220 (Movement I item 2).
2. **Implement the meta-validator** OBPI-0.0.74-15..19 in land-order
   15 → 16 → 17 + 18 → 19 (start with OBPI-15 `@enforces` declaration + registry)
   — campaign line 222 (Movement I item 3).
3. **MX kernel hardening** (campaign line 221): TTL/max-open, no-force exit,
   ledger debt-aging, dangling-state detector.

> **Sequencing precondition (campaign §7):** confirm `uv run gz check` is green
> before opening any of these — "no movement opens while `gz check` is red."
> **NOT a near-term step:** the `foundation`-abolition fail-close stays in
> **Movement III** (operator ruling 2026-06-23, "as is in movement iii") —
> deferred behind Movement I; do not pull it forward. See Pending Work.

## Pending Work / Open Loops

- **GHI #638 (open)** — gates-as-sensors residual; needs an OBPI under ADR-0.0.74.
- **GHI #620 (open)** — turn-end claim-grounding gate; would catch ungrounded
  "complete" prose claims like the one Codex refuted this session.
- **Campaign line 220 box stays UNCHECKED** — gates-as-sensors is incomplete;
  do not check it until the `gz check` step layer also routes through the
  checkpoint (and ideally a live NC proves it).
- **OBPI-17 blocker risk** — `secrets`/`operator-pii` may need their real gate5
  production entrypoints built before their live NCs can bind.
- **`_NEGATIVE_CONTROL_DEBT`** in qc_binding should be removed when OBPI-16 lands
  (strict-no-debt, per D3).
- **Foundation-abolition fail-close — Movement III (operator ruling 2026-06-23,
  "as is in movement iii").** `gz validate --taxonomy` rejecting `kind: foundation`
  + a live NC is the structural cure for this session's root failure, but it is
  deferred behind Movement I and NOT pulled forward. Do not advise it as a
  near-term step.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; `git rev-parse --short HEAD` is `cb752202` (or later)
- [ ] `uv run -m unittest -q` passes (last observed: 6398 tests, exit 0)
- [ ] `rg -n "checkpoint\.resolve\(" src/gzkit/commands/validate_cmd.py src/gzkit/governance/trust_audits/rendition_freshness.py src/gzkit/governance/trust_audits/rendition_floor_coherence.py` shows 3 production callers (GHI #637 cure intact)
- [ ] `ls docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/ | rg "OBPI-0.0.74-1[5-9]"` shows 5 briefs
- [ ] `uv run gz obpi validate --adr ADR-0.0.74 --authored` — OBPI-15..19 PASS
- [ ] `rg -c "0\.0\.75" docs/design/adr/pool/ADR-pool.enforcement-claim-meta-validator.md` > 0 (demoted stub present)
- [ ] Before any new-ADR action: confirm `kind` against campaign §3a (foundation abolished)

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — amended ADR (Decision subsection, +5 checklist items, Boundary Invariants #6-10, rejected alternatives, negatives)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-15-enforces-declaration-and-registry.md` — meta-validator OBPI A
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-16-meta-validator-runner.md` — OBPI B (runner; engine-lift; un-forced NCs)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-17-gate5-invariants-floor-migration.md` — OBPI C (gate5 NCs; honest negative)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-18-structural-fence-proof-upgrade.md` — OBPI D (upgrades resolve_fence_proof in `src/gzkit/req_kind.py`)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-19-floor-wiring.md` — OBPI E (floor wiring; lands last)
- `docs/design/adr/pool/ADR-pool.enforcement-claim-meta-validator.md` — demoted ADR-0.0.75 (inert intake history)
- `src/gzkit/mx/disposition.py` — new `grounds(route)` predicate (GHI #637)
- `src/gzkit/mx/checkpoint.py` — `is_advisory` now delegates to `resolve()`
- `tests/mx/test_disposition.py` — `TestRouteGrounds` + `TestLeveledConsumptionEquivalence`
- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — the active campaign (Movement I lines 218-222; §3a; §5; §8)
- `.gzkit/insights/agent-insights.jsonl` — course-correction insight (kind=foundation pre-fill, 2026-06-23)

## Environment State

Python 3.13, uv-managed. `main` at `cb752202`, ahead=0 behind=0, clean. No active
OBPI locks. No version bump (nothing released this session — repairs are
governance + one code fix already on main).
