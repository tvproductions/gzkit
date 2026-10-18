---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-18T15:47:34Z'
agent: claude-code
session_id: e6800367-eb28-4b68-9624-65d94f7cdf17
continues_from: .gzkit/handoffs/20261018T131458Z-session-close-ghi-1257-next.md
---

## Current State Summary

Session close, safe mode still open (contract docs/governance/harbor-pilotage-candidate-2026-10-15.md). Landed and pushed: d5fcd5c3f fixed GHI #1257 (closed with evidence): the MX hangar is bounded by one lease, the session lock's TTL; expiry is booked once as mx_session_lease_expired at session start and announced, never evicted; gz mx exit holds the marker (exiting) through its full-strength re-run; gz validate --mx-hardening runs the TTL, debt-aging and dangling-state guards in gz check; the orientation renders a conditional MX hangar section. Also fixed in flight: the orientation's SECTION_HEADINGS roster omitted the guard-canary section. 32d8c274c booked ADR-pool.operator-bulletin (ledger-derived operator bulletins; design closed, operator approved as booked). In progress, not landed: tightening the requirements and feature model to an adoptable state, one decision at a time. Decision 1 (grain) accepted; decision 2 (identity) put to the operator and answered with a question, not a selection.

## Important Context

The requirements-model detail is NOT in the canon files alone. It is in the 2026-10-17 drydock session transcript ~/.claude/projects/-Users-jeff-Documents-Code-gzkit/696ca9a4-7b6b-4d3a-8611-0da2766bf075.jsonl (10:00 to 11:20 UTC: the FDAU and Backplane prior-art report, the decisions report, the first-principles verification of the general arrangement) and the 2026-10-15/16 planning session 4fd13b45-724e-4433-ab23-fd6c5df2b932.jsonl. FDAU is tvproductions/xplane-fdau; read docs/project/backlog-method.md, docs/project/backlog-governance-model.md (its sections Candidate pattern for gzkit and airlineops, ADRs feature records and releases are different records, A safe migration test, A minimal transferable schema) and ROADMAP.md through gh api. The operator answered the identity question with: "why NOT the FDAU method? didn't we discuss WBS and other aspects? it was actually part of a much broader conversation." That broader conversation (WBS and related aspects) has not been found yet; search the transcripts above and docs/rnd/renewing-vows/ before proposing identity again. Tension to surface, not resolve: the 2026-10-17 ruling "REQ ids stay sequential so a move between areas keeps identity" (insight scope harbor-pilotage-wp4) versus FDAU's family-encoded C2.3 ids. Canon state of the model: docs/governance/ieee/design-candidates.md section The joined requirements model is recorded but unratified, still carries the retired engineering-order rung, and has five open points; the ratified general arrangement in the contract governs where they differ. Safe-mode purpose binds: structure, not population (operator 2026-10-17); design questions go to the operator one at a time, never written into canon without ratification. Token-block expiry: the operator ruled it book-and-notify like the hangar, but brief OBPI-0.35.0-19 owns lock occupancy, is at its frozen brief-size ceiling, and ADR-0.35.0 is frozen by RO-8, so the route is still the operator's call. The child session local_43a33688 (Amend OBPI-0.35.0-19) is idle and holding with no edits.

## Decisions Made

- [operator-ruled] Fix GHI #1257 in this session (verbatim: "proceed: fix GHI #1257 here, per the ruling and the surface list in the handoff"); booked with gz handoff decide.
- [operator-ruled] Lease expiry is never an eviction (verbatim: "what are we going to do? evict? at worst, we book a status at least expiry and notify. In fact, we lack a messaging/notification system, broadly, in gzkit.").
- [operator-ruled] Land the hangar fix, then design the bulletin (verbatim: "Land GHI #1257 now as book-and-announce on expiry for the hangar (no eviction, exit keeps state through its checks), then open the bulletin system design with gz-design as a pool ADR.").
- [operator-ruled] Bulletin design selections, verbatim labels: "Derived from ledger (Rec.)", "Board + agent context (Rec.)", "Clears with its condition (Rec.)", "Occupancy + lease (Rec.)", "Book it (Rec.)"; then "The pool ADR reads right as booked; close the design."
- [operator-ruled] The token block takes the same expiry rule as the hangar (verbatim: "yes, of course, didn't I draw their equivalence for our design consideration?"); route first ruled "Amend OBPI-0.35.0-19 (Rec.)", which is blocked (brief-size ceiling, RO-8 freeze) and awaits a new route ruling.
- [operator-ruled] Requirements-model decision 1, grain: a REQ is one acceptance statement under a feature outcome and a work package plans one outcome (verbatim: "you got it"); tighten the model to adoptable one decision at a time (verbatim: "Yes. Start with decision 2, identity: put it to me with a recommendation, then continue one decision at a time.").
- [agent-chose] gz mx exit holds the marker with an exiting field rather than an environment variable, keeping ADR-0.0.74 Boundary Invariant 1 (single MX truth-source).
- [agent-chose] Past-lease and aged-debt levels top out at WARNING so neither can ground exit; max-open stays CRITICAL, dangling stays ERROR.

## Immediate Next Steps

1. Resume requirements-model decision 2 (identity): first find the broader conversation the operator named (WBS and related aspects) in the transcripts and docs/rnd/renewing-vows/, then answer "why NOT the FDAU method?" directly, put the FDAU identity scheme to the operator with the 2026-10-17 sequential-REQ ruling surfaced beside it, and take decisions 3 to 9 one at a time.
2. Operator: rule the token-block expiry route (GHI direct fix in maintenance mode, recommended, or hold for civil rule), then tell the idle child session local_43a33688 to proceed or stop.
3. Operator: the proposed card for a session that specifies RO-2 (the id-resolution seam) is waiting to be started.
4. Once the model's decisions are ratified, draft the document that replaces design-candidates.md section The joined requirements model and run FDAU's paper migration test on four items.

## Pending Work / Open Loops

- Requirements-model decisions 2 to 9 open: identity; authority split (L1 structure file versus ledger state, a deliberate departure from FDAU's ROADMAP/BACKLOG); lifecycle states and transition evidence; dependencies and readiness; one work package per outcome; candidate_release and released_in; Q-19 open points (non-functional applicability, feature-file declaration, bounded contexts); ADR links many-to-many.
- Token-block book-and-notify is ruled but unlanded; OBPI-0.35.0-19 Requirement 8, its Denied Paths and REQ-0.35.0-19-15 still encode eviction.
- RO-2 to RO-8 not started; RO-2 is the keystone.
- ADR-pool.operator-bulletin first-kinds list may add obpi_lock_lease_expired once the token-block event exists.
- GHI #1246, #1250, #1252, #922 open from the prior handoff.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 after this handoff is synced.
- gh issue view 1257 reads CLOSED.
- uv run gz validate --mx-hardening exits 0 and prints the lease and debt advisories while safe mode is open.
- uv run gz adr report lists ADR-pool.operator-bulletin.
- uv run gz insights remember records exist under scopes drydock-ghi-1257-lease-expiry and requirements-model-tightening.

## Evidence / Artifacts

- `src/gzkit/mx/lease.py` — expiry booking.
- `src/gzkit/governance/trust_audits/mx_hardening.py` — the scope and the shared findings rendering.
- `src/gzkit/mx/hardening.py` — the lease read from the lock TTL.
- `docs/design/adr/pool/ADR-pool.operator-bulletin.md` — the bulletin design.
- `docs/governance/ieee/design-candidates.md` — the unratified joined requirements model.
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` — the drydock contract and its general arrangement.

## Settled Rulings

1597 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
