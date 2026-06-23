---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-23T23:32:47Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: 9edaf99e
session_id:
continues_from: .gzkit/handoffs/20260623T120423Z-meta-validator-rehomed-substrate.md
---

<!-- Handoff document for ADR-0.0.74 — created by claude-code at 2026-06-23T23:32:47Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

**Extra caution this chain:** the grandparent handoff
(`20260623T084256Z-sizing-...`) advised "open a new **foundation** ADR," and
following it uncritically caused a §3a violation (foundation kind is abolished).
Test every advised step below against the active campaign BEFORE acting — the
campaign RULES the sequencing; this handoff only advises.

## Current State Summary

No implementation occurred this session — it was an orientation + state-refresh
session. Working tree is **clean**; `main` is at `9edaf99e`, ahead=0. The
substrate state described by the predecessor handoff
(`20260623T120423Z-meta-validator-rehomed-substrate.md`) holds unchanged, with
two reconciliation commits now landed on top of it:

- **`de051cd2`** `docs(campaign): living-state update` — recorded the
  gates-as-sensors *partial* (GHI #637 done / GHI #638 residual) and the
  meta-validator seating under ADR-0.0.74 into the active campaign's living state.
- **`9edaf99e`** `docs(handoff): reconcile advised steps to operator ruling` —
  aligned the advised next steps so the **foundation-abolition fail-close stays
  in Movement III** (operator ruling 2026-06-23, "as is in movement iii"); it is
  NOT pulled forward into Movement I.

Net effect: the prior handoff's substance is intact and now reconciled with the
operator's sequencing ruling and reflected in the campaign living-state. Nothing
new is implemented or attested.

Standing substrate facts (carried forward, verified this session):

- **GHI #637 (CLOSED, `b7f2f58c`)** — leveled MX checkpoint now has live
  production consumers (`validate_cmd._run_scope_checks` + both rendition gates
  route through `disposition.grounds(checkpoint.resolve(...))`). Facade cured.
- **GHI #638 (OPEN, verified OPEN this session)** — gates-as-sensors residual:
  the `gz check` step layer (~30 steps in `quality.py`) + ~5 solo `validate_cmd`
  paths still self-decide fatality (`returncode=3` / `SystemExit(3)`) outside the
  checkpoint. Needs an OBPI under ADR-0.0.74. Campaign line 220 box stays
  UNCHECKED until migrated.
- **GHI #639 (CLOSED, `cb752202`)** — ADR-0.0.75 (mis-booked `kind: foundation`)
  demoted to pool; meta-validator re-homed VERBATIM as **OBPI-0.0.74-15..19**.

The enforcement-claim meta-validator is seated as **OBPI-0.0.74-15..19
(Draft/authored, NOT implemented)** — verified present on disk this session
(all five briefs + the demoted `ADR-pool.enforcement-claim-meta-validator.md`).

## Important Context

- **ADR-0.0.74 is the single locus of substrate work**: the MX kernel
  (campaign line 221) + the gates-as-sensors residual (GHI #638) + the
  meta-validator (OBPI-15..19), all converging on release **0.29.0**.
- **Two axes, do not conflate them** (this cost a refuted claim two sessions ago):
  *MX-demotability* (does a guard route severity through the checkpoint so it
  demotes under the hangar marker — campaign line 220) is ORTHOGONAL to
  *NC-falsifiability* (does an enforcement claim have a live negative control —
  the meta-validator). GHI #637 advanced the first for the `gz validate`
  dispatcher; GHI #638 is its residual; the meta-validator is the second.
- **`resolve_fence_proof` is in `src/gzkit/req_kind.py` (~line 91), NOT
  `closeout_proof.py`** — OBPI-18 depends on the correct module.
- **Honest negative (OBPI-17):** `secrets` and `operator-pii` have **no bound
  gate5 production entrypoint today**; the brief forbids binding a narrower proxy
  to fake a live NC — the real production path may need to be built first.
- **The existing 33 qc_binding NCs force `fail_closed=True`** — the forbidden
  forced-mode pattern §5 names. OBPI-16 re-authors them un-forced.
- **"max vibes" finding (carried):** heavy ADR ceremony blessed a decision
  (ADR-0.0.75 foundation) that contradicted the campaign at its root. Gates check
  SHAPE, not TRUTH. The recourse is the floor (§5), not more ceremony — but per
  the operator ruling that fail-close cure stays **Movement III**, not now.

## Decisions Made

- **Decision:** Create a state-refresh handoff chained from the 12:04Z predecessor
  rather than amending it, reflecting HEAD `9edaf99e` and the two reconciliation
  commits.
  **Rationale:** the operator asked for a fresh handoff; handoffs are append-only
  register entries (continues_from preserves lineage), never edited in place.
  **Alternatives rejected:** editing the prior handoff (loses the audit chain);
  skipping the handoff because "nothing changed" (the reconciliation commits and
  the operator's Movement-III ruling are exactly the context worth preserving).
- **Carried (unchanged):** all meta-validator design decisions (D1 un-forced NCs
  through the real path; D2 runner-driven `@enforces`; D3 strict no-debt) and the
  re-home-under-0.0.74 decision remain as booked in the predecessor handoff.

## Immediate Next Steps

ADVISORY ONLY — present to the operator and obtain authorization before acting.
All are **Movement I** work converging on ADR-0.0.74 / release 0.29.0. NONE is a
new foundation ADR.

1. **Scope an OBPI under ADR-0.0.74 for the GHI #638 gates-as-sensors residual**
   (migrate the `gz check` step layer + ~5 solo `validate_cmd` paths through the
   checkpoint) — completes campaign line 220 (Movement I item 2). This is the
   predecessor's advised first step and remains topmost.
2. **Implement the meta-validator** OBPI-0.0.74-15..19 in land-order
   15 → 16 → 17 + 18 → 19 (start with OBPI-15 `@enforces` declaration + registry)
   — campaign line 222 (Movement I item 3).
3. **MX kernel hardening** (campaign line 221): TTL/max-open, no-force exit,
   ledger debt-aging, dangling-state detector.

> **Sequencing precondition (campaign §7):** confirm `uv run gz check` is green
> before opening any of these — "no movement opens while `gz check` is red."
> **NOT a near-term step:** the `foundation`-abolition fail-close stays in
> **Movement III** (operator ruling 2026-06-23) — deferred behind Movement I; do
> not pull it forward. See Pending Work.

## Pending Work / Open Loops

- **GHI #638 (open)** — gates-as-sensors residual; needs an OBPI under ADR-0.0.74.
- **GHI #620 (open)** — turn-end claim-grounding gate; would catch ungrounded
  "complete" prose claims.
- **Campaign line 220 box stays UNCHECKED** — gates-as-sensors is incomplete
  until the `gz check` step layer also routes through the checkpoint (ideally a
  live NC proves it).
- **OBPI-17 blocker risk** — `secrets`/`operator-pii` may need their real gate5
  production entrypoints built before their live NCs can bind.
- **`_NEGATIVE_CONTROL_DEBT`** in qc_binding should be removed when OBPI-16 lands
  (strict-no-debt, per D3).
- **Foundation-abolition fail-close — Movement III (operator ruling 2026-06-23).**
  `gz validate --taxonomy` rejecting `kind: foundation` + a live NC is the
  structural cure for the root failure, but it is deferred behind Movement I and
  NOT pulled forward. Do not advise it as a near-term step.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; `git rev-parse --short HEAD` is `9edaf99e` (or later)
- [ ] `uv run gz check` is green before opening any Movement I item (campaign §7 precondition)
- [ ] `uv run -m unittest -q` passes (last observed prior session: 6398 tests, exit 0)
- [ ] `rg -n "checkpoint\.resolve\(" src/gzkit/commands/validate_cmd.py src/gzkit/governance/trust_audits/rendition_freshness.py src/gzkit/governance/trust_audits/rendition_floor_coherence.py` shows 3 production callers (GHI #637 cure intact)
- [ ] `ls docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/ | rg "OBPI-0.0.74-1[5-9]"` shows 5 briefs
- [ ] `gh issue view 638 --json state` is OPEN (gates-as-sensors residual still tracked)
- [ ] Before any new-ADR action: confirm `kind` against campaign §3a (foundation abolished)

## Evidence / Artifacts

- `.gzkit/handoffs/20260623T120423Z-meta-validator-rehomed-substrate.md` — predecessor handoff (full substrate detail; this handoff carries it forward)
- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — the active campaign (Movement I lines 218-222; §3a; §5; §7; §8); living-state updated by `de051cd2`
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — substrate ADR (MX kernel + meta-validator checklist items)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-15-enforces-declaration-and-registry.md` — meta-validator OBPI A
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-16-meta-validator-runner.md` — OBPI B (runner; un-forced NCs)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-17-gate5-invariants-floor-migration.md` — OBPI C (gate5 NCs; honest negative)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-18-structural-fence-proof-upgrade.md` — OBPI D (upgrades resolve_fence_proof in `src/gzkit/req_kind.py`)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-19-floor-wiring.md` — OBPI E (floor wiring; lands last)
- `docs/design/adr/pool/ADR-pool.enforcement-claim-meta-validator.md` — demoted ADR-0.0.75 (inert intake history)
- `src/gzkit/mx/disposition.py` — `grounds(route)` predicate (GHI #637)
- `src/gzkit/mx/checkpoint.py` — `is_advisory` delegates to `resolve()` (GHI #637)

## Environment State

Python 3.13, uv-managed. `main` at `9edaf99e`, ahead=0, clean. No active OBPI
locks. No version bump (nothing released — this session is orientation +
state-refresh only).
