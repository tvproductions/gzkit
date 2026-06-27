# Plan — OBPI-0.0.74-14-mx-hardening (the MX lean-kernel hardening guards)

## Context

This is the **campaign's topmost item** (Build-to-1.0 Movement I): the last of 19 OBPIs
under ADR-0.0.74 (currently **18/19**, closeout **BLOCKED** only on this one). Landing it
closes the ADR and releases **`0.29.0`** — MX as the first feature, per the campaign
versioning doctrine (§4).

The MX hangar exists (marker, leveled checkpoint, enter/exit, exit hard-gate, proxy-reality
detector) but has **no bound**: a session can stay open forever (every non-floor guard
demoted to advisory the whole time), a release can ship mid-repair, accrued advisory debt
sits silent, and a hand-deleted marker leaves a dangling open session undetected. This OBPI
lands the four hardening guards that bound the hangar — each resolving severity through the
**one leveled checkpoint** (no per-guard hand-set bool), satisfying parent-ADR Boundary
Invariant #2.

Floor is green (`uv run gz check` passes). Adjacent campaign sub-items already done:
GHI #640 (drifted Q&A transcript) CLOSED; OBPI-10 doc-type taxonomy WITHDRAWN.

## Design decisions (settled)

- **Debt-aging signal = open-MX-session age** (operator-chosen). The open hangar *is* the
  advisory-debt state; the guard ages the oldest open `mx_session_opened` (no matching close)
  and raises its emitted level by age-bucket. No ledger-writer change (brief Denied Paths
  forbid it — guards READ the ledger only).
- **REQ-14-05 is a *state-property* fence** ("none hand-sets its own severity"), not an
  *enforcement* claim — so per parent-ADR BI#10 it resolves via the `## Boundary Invariants`
  anchor (BI#2), **not** a live `@enforces` NC. (Verification checkpoint below confirms.)
- **Guards that must bite while the marker is up emit CRITICAL** so the checkpoint *pins*
  them (checkpoint.py:31 demotes non-floor `!= CRITICAL` to ADVISORY under the marker;
  CRITICAL is never demoted). This is the honest mechanism, not a bool bypass.

## New module: `src/gzkit/mx/hardening.py`

Four guards + frozen Pydantic result models (`ConfigDict(frozen=True, extra="forbid")`),
mirroring `proxy_reality.py` conventions. Shared private reader `_open_sessions(root)` →
list of `(session_id, opened_at_ts)` for `mx_session_opened` events with no matching
`mx_session_closed` (via `gzkit.ledger.Ledger.query`). Each guard resolves severity through
`checkpoint.resolve(guard_name, emitted_level, root)` and reports `disposition.grounds(route)`.
`now` injectable (default `datetime.now(UTC)`) for deterministic tests.

| Guard | fn | emitted level | grounds? |
|---|---|---|---|
| TTL / max-open (REQ-14-01) | `ttl_max_open_status(root, *, now, ttl_hours=24, max_open=1)` | CRITICAL if `>max_open` open sessions (hard invariant, pins); ERROR if any past TTL; else INFO | over-max always; past-TTL outside marker |
| No-release-while-open (REQ-14-02) | `normal_release_blocked(root)` | CRITICAL while marker active (pins → AOG); else INFO | yes, while marker up |
| Debt-aging (REQ-14-03) | `debt_aging_status(root, *, now)` | by oldest-open age: INFO `<6h` → NOTICE `<12h` → WARNING `<24h` → ERROR `>=24h` | only `>=24h` outside marker |
| Dangling-state (REQ-14-04) | `dangling_state_status(root)` | ERROR if ledger-open AND marker absent on disk; else INFO | yes (marker absent ⇒ no demotion) |

Guard names: `mx-ttl-max-open`, `mx-normal-release`, `mx-debt-aging`, `mx-dangling-state`.
**No module-level `_*_FAIL_CLOSED` bool** anywhere (REQ-14-05 / Denied Paths).

## Wiring the no-release guard at the real release sites (REQ-14-02)

The block must be exercised "at the real release site, not merely a standalone predicate",
and must short-circuit **before** any gh/network call (keeps tests hermetic):

- `src/gzkit/commands/patch_release.py` — in `patch_release_cmd` (line ~726), right after
  `project_root = get_project_root()` and **before** `_ensure_gh_available`:
  `if not full and dry_run` paths unaffected; on the executing path, if
  `hardening.normal_release_blocked(project_root).blocked` → print error + `raise SystemExit(3)`.
- `src/gzkit/commands/closeout.py` — in `closeout_cmd` (line ~615), right after
  `project_root = get_project_root()`: `if not dry_run and hardening.normal_release_blocked(project_root).blocked` → abort with SystemExit(3).

Dry-run preview stays usable while the hangar is open; only actual release is refused
(exit 3 = policy breach per CLI exit-code map).

## Tests: `tests/mx/test_hardening.py` (unittest, `@covers`)

Mirror `tests/mx/test_proxy_reality.py` / `test_marker.py` (tmp roots, planted
`.gzkit/ledger.jsonl` + optional `.gzkit/mx.json` marker):

- **REQ-14-01**: old open session → flagged + `route == checkpoint.resolve(...)`; two open
  sessions → over-max CRITICAL/grounds.
- **REQ-14-02**: `normal_release_blocked` True under marker, False without; **plus** the
  block exercised at the real site — build a project via the closeout test's `_quick_init()`
  pattern with an active marker, call `closeout_cmd(dry_run=False)` and `patch_release_cmd`
  and assert `SystemExit(3)`.
- **REQ-14-03**: emitted level rises monotonically (INFO→NOTICE→WARNING→ERROR) across
  increasing `now` — the "grows louder" semantic.
- **REQ-14-04**: ledger-open + marker-missing → dangling; ledger-open + marker-present →
  not dangling; ledger-closed + marker-missing → not dangling.
- **REQ-14-05**: assert no `_*_FAIL_CLOSED` module attr and each guard's route derives from
  `checkpoint.resolve` (structural pin, mirroring `test_check_step_checkpoint_seam.py`).

## Docs (Gate 3, Heavy) — requires a small allowlist amendment

The lockout changes the observable behavior of two documented commands, so per DO IT RIGHT
1a (coupled-surface coherence) the same change updates:
- `docs/user/manpages/patch-release.md` and `docs/user/manpages/closeout.md` — note the
  "refused while an MX hangar is open; exit the hangar first (exit 3)" behavior.
- `docs/governance/governance_runbook.md` — one line on the release lockout.

These three paths are **outside the brief's current Allowed Paths** → I will request an
**operator-ratified allowlist amendment** (same precedent as OBPI-13's enforcement.py
amendment) as part of plan approval. No new CLI verb is added, so `gz cli audit` needs no
new manpages.

## Execution route

Contract-bearing Heavy OBPI ⇒ the **OBPI pipeline mandate** applies.
1. Implement via TDD (RED `test_hardening.py` → GREEN `hardening.py` + wiring), so I control
   the checkpoint-demotion nuance directly.
2. `uv run gz obpi pipeline OBPI-0.0.74-14-mx-hardening --from=verify` — runs brief-reconcile,
   Gate-2 verify, `uv run gz check`, guarded `uv run gz git-sync --apply --lint --test`,
   then `gz obpi complete` (Heavy ⇒ **operator Gate-5 attestation**, never bypassed).
3. After the ADR shows 19/19, the **`0.29.0` release ceremony** is the next campaign step
   (separate operator-gated action — not part of this OBPI).

## Verification

```bash
uv run -m unittest tests.mx.test_hardening -v          # all guard tests green
uv run gz covers OBPI-0.0.74-14-mx-hardening --json    # REQ-14-01..05 proof_status pass
uv run gz lint && uv run gz typecheck
uv run gz check                                        # floor stays green
uv run python -c "from gzkit.mx import hardening; print(hardening.normal_release_blocked())"
```

**Checkpoint to confirm during impl:** that `resolve_fence_proof` resolves REQ-14-05 (a
state-property fence) via the BI#2 anchor without demanding a live `@enforces` NC. If it
demands one (i.e. it reads REQ-14-05 as an enforcement assertion), flag and route — do not
silently backfill a forced NC.
