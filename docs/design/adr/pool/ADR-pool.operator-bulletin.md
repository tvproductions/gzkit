---
id: ADR-pool.operator-bulletin
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.operator-bulletin: Operator bulletin: ledger-derived notices of occupancy, lease and severity

## Status

Pool

## Intent

**Origin.** Operator, 2026-10-18, while ruling GHI #1257 (verbatim): "we lack a
messaging/notification system, broadly, in gzkit. Capture certain events and ensure that a
bulletin, with priority/severity, is available and presented. This would be a very useful
system. So, when a token block for a work package and the mx hangar/drydock is occupied, the
operator is aware." A pool ADR is a change proposal: it books nothing and initiates nothing;
promotion is the operator's.

**The gap.** gzkit records occupancy and expiry in the ledger (`obpi_lock_claimed`,
`obpi_lock_ttl_warning`, `mx_session_opened`, `mx_session_lease_expired`, landed in
`d5fcd5c3f` for GHI #1257) but presents them through scattered, unpersisted channels: the
session orientation's conditional sections (chores due, guard canaries, the MX hangar), the
per-turn MX banner, `[advisory]` lines inside `gz check`, and GHIs. Nothing turns a captured
event into a notice that carries a severity, stays available, is presented and can be
acknowledged; and each new announcement is new ad hoc code, which is how the orientation's
heading roster came to omit one of its own sections (fixed in `d5fcd5c3f`).

## Target Scope

- One pure projection, `project_bulletins(ledger, now) -> list[Bulletin]`, a Layer-3 view of
  Layer-2 events; the board, the session orientation and the per-turn hook all read it, so
  there is one rendering.
- A declared kinds registry, `data/bulletin_kinds.json` (registered in
  `data/config_registry.json`): per kind, the raising event type, the severity (the existing
  MX level ladder, `gzkit.mx.levels`, DEBUG to CRITICAL), the clearing event types and the
  agent-context presentation threshold.
- `Bulletin` (Pydantic, frozen): `id` (derived from kind and subject), `kind`, `subject`
  (OBPI id or MX session), `severity`, `raised_by` (event id and ts), `quieted`, `message`
  (three-part prose per `guardrail-feedback-prose.md`).
- `gz bulletin list [--json] [--min-severity LEVEL] [--all]` and
  `gz bulletin ack <id> --operator-text "<words>"`, the latter writing one
  `bulletin_acknowledged` ledger event; one noun, no new root leaf (`cli.md`).
- First kinds: token block occupied (`obpi_lock_claimed` until `obpi_lock_released`); hangar
  or drydock occupied, with mode and contract (`mx_session_opened` until `mx_session_closed`);
  lease half spent (`obpi_lock_ttl_warning`); lease expired (`mx_session_lease_expired`);
  dangling MX session.

## Non-Goals

- No eviction and no gating: a bulletin informs, it blocks nothing (operator ruling
  2026-10-18 on lease expiry: "at worst, we book a status at least expiry and notify").
- No bulletin store outside the ledger, and no hand-clearing.
- No external or SaaS channel in the first cut.

## Decision

Proposed, not decided. Four design questions were put to the operator on 2026-10-18 and
answered by selection (the selected option labels, verbatim):

1. Where a bulletin lives: **"Derived from ledger (Rec.)"** — a Layer-3 view computed from
   Layer-2 events, with acknowledgement itself a ledger event; no second source of truth
   (`docs/governance/state-doctrine.md`, Architectural Boundary 6).
2. How it is presented: **"Board + agent context (Rec.)"** — `gz bulletin list` as the board,
   and the session orientation and per-turn hook rendering open bulletins at or above a
   threshold, so the agent relays them unprompted; today's chore, canary and MX-hangar
   sections fold into it. No external channel in the first cut; the model keeps a port.
3. When it stops being presented: **"Clears with its condition (Rec.)"** — open while the
   ledger shows its condition holding; acknowledgement quiets it in agent context until its
   severity rises, and the board still lists it.
4. What the first cut carries: **"Occupancy + lease (Rec.)"** — the kinds the operator named,
   with later kinds (chores due, guard canaries, behind-origin) migrating in through the
   registry once they are ledger-backed.

Lane: heavy, because it adds a CLI noun and a ledger event type.

Relationships: `ADR-pool.channel-agnostic-human-triggers` is the inverse direction (the
operator reaching the system) and `bulletin_acknowledged` is its first concrete trigger;
`ADR-pool.maintenance-record-entry` ("its coming due is announced from the events, and gates
nothing") becomes a bulletin kind; `ADR-pool.progressive-context-disclosure`'s L3
"time-bridging alerts" would read this projection rather than build another.

## Alternatives Considered

- **Emitter-posted bulletin store.** Rejected by the operator's first answer: a bulletin file
  or registry that emitters post into is a second state surface that drifts from the ledger
  it summarizes.
- **Hybrid: derived plus a posting verb** for notices with no ledger event behind them.
  Not selected: two code paths, and a notice worth presenting is worth a ledger event.
- **Grow the orientation's conditional sections** (the status quo). Rejected: no board, no
  acknowledgement, no shared severity, and each announcement is new ad hoc code; the
  roster drift fixed in `d5fcd5c3f` is that shape's measured cost.
- **The harness's own notification or push surfaces.** Rejected for the first cut:
  vendor-specific and not ledger-backed; a push adapter stays a port behind the projection.
- **Board only.** Not selected (operator's second answer): the operator must remember to
  look, which is the gap the system exists to close.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
