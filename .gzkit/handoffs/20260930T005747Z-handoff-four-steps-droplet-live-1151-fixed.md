---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-30T00:57:47Z'
agent: claude-code
session_id: 62e1d102-4c74-4092-b850-1e307cc00196
continues_from: .gzkit/handoffs/20260929T100124Z-worktrees-removed-ghi-1150-filed.md
---

## Current State Summary

Resumed the 20260929T100124Z handoff and the operator ruled 'do all four'. Closed this session: GHI #1150 fixed (92f64debc; scan-all skips Validated/Abandoned ADRs, folds ids through the rename map, and walkthrough subject matching now follows renames). GHI #802 fixed: gzkit.org is live again on the new droplet (Caddy + Let's Encrypt, release-triggered rsync deploy, daily freshness check; cf1444951). GHI #939 closed superseded after OBPI-0.35.0-10's brief was amended with REQ-08..10 (56ebcf907). ADR-pool.handoff-resume-assessment authored and registered (60131a309). GHI #1151 filed, narrowed, then fixed (0f0f69890, 0765d9bfb; fold_renames re-binds only a reused alias). main is 0/0 with origin before this handoff's sync.

## Important Context

gzkit.org hosting: droplet myvps2 at 209.97.149.89, Caddy serving /var/www/gzkit.org/site; the CI key is confined by rrsync (command=rrsync,restrict) and cannot open a shell; repo secrets VPS_SSH_KEY and VPS_KNOWN_HOSTS plus variable VPS_HOST=gzkit.org drive the deploy-vps job in docs.yml; docs-freshness.yml fails when the served tag lags the latest release. The operator's Mac has no personal SSH key, and pasting multi-line blocks after a sudo password prompt swallows the later lines (run sudo -v first). macOS rsync is openrsync and cannot talk to rrsync, so test deploys from CI, not the Mac. Freed feature semver slots are reused, never retired; 0.35.0-0.39.0 were reused after the 2026-05-23 demotion. gz arb red commit mode reports an annotation-only hunk as undriven; recorded as an insight, not fixed.

## Decisions Made

- [operator-ruled] Resume the handoff and work all four advised steps (verbatim: 'do all four').
- [operator-ruled] Keep gzkit.org on the droplet and automate its deploy, superseding the 2026-09-28 Pages ruling (verbatim: 'A, set up the droplet').
- [operator-ruled] Apply the OBPI-0.35.0-10 brief amendment and handle the ADR interview (verbatim: 'take care of these').
- [operator-ruled] The handoff_api correction is a pool ADR, not a feature slot (verbatim: 'this could ONLY be a pool adr at this point').
- [operator-ruled] Author the pool ADR and file the ledger GHI (verbatim: 'yes to both, author the pool ADR and file the GHI').
- [operator-ruled] Freed semver slots are reused, not retired (verbatim: 'no, these are semver sequences, we can't just 'retire' them').
- [operator-ruled] Fix GHI #1151 in this session (verbatim: 'fix #1151 now').
- [agent-chose] GHI #1150: dropped terminal ADRs from the scan-all rather than keeping them as advisory (the recommended option, applied under 'do all four').
- [agent-chose] OBPI-0.35.0-10 REQ-08 retention-checks skill- and ADR-sourced rows against their own source instead of exempting them, so no Mechanical row is left unwitnessed.
- [agent-chose] Left GHI #799 open: the brief owns its precondition, but no REQ scores ADR-0.0.33's six anti-pattern rows.

## Immediate Next Steps

1. Ask the operator whether to draw the next ADR-0.35.0 OBPI; OBPI-0.35.0-10 now also carries the retention-scope REQs 08-10.
2. When OBPI-0.35.0-10 lands, add ADR-0.0.33's six anti-pattern rows to the scorecard as a direct fix under GHI #799.
3. Ask the operator whether to pick up the gz arb red annotation false-positive insight (commit_witness keeps annotations in its behavior fingerprint).
4. Offer to give the operator's Mac a personal SSH key for the droplet so logins stop depending on the web console.

## Pending Work / Open Loops

GHI #799 open with an updated blocker comment. ADR-pool.handoff-resume-assessment awaits promotion when drawn; it takes a feature semver then. Insight on gzkit.commit_witness (annotation-only hunks reported undriven) not yet a GHI. Carried from the predecessor: #611 clause 4 and held item (a); #1149 and #1125 open; pool promotion-triage facility owed by ADR-pool.pool-management section 9; gz obpi precomplete has no manpage; GovZero docs cite AirlineOps-era ADR numbers.

## Verification Checklist

curl -sI https://gzkit.org/ (expect HTTP/2 200); curl -s https://gzkit.org/build-info.json (expect the latest release tag); gh issue view 1150 802 939 1151 (expect CLOSED); uv run gz validate --evaluation-justify-binding (expect exit 0); uv run -m unittest tests.governance.test_rename_fold tests.governance.test_justify_binding_gate (expect OK); git rev-list --left-right --count origin/main...HEAD (expect 0 0); uv run gz check (expect exit 0).

## Evidence / Artifacts

Predecessor: `.gzkit/handoffs/20260929T100124Z-worktrees-removed-ghi-1150-filed.md`. GHI #1150: `src/gzkit/commands/validate_cmd.py`, `src/gzkit/governance/trust_audits/evaluation_justify_binding.py`, `tests/governance/test_justify_binding_gate.py`. GHI #802: `.github/workflows/docs.yml`, `.github/workflows/docs-freshness.yml`, `docs/developer/deployment.md`. GHI #939: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`. Pool ADR: `docs/design/adr/pool/ADR-pool.handoff-resume-assessment.md`, `docs/design/adr/pool/handoff-resume-assessment-interview.json`, `docs/governance/build-to-1.0-campaign-2026-09-20.md`. GHI #1151: `src/gzkit/obpi_lifecycle.py`, `tests/governance/test_rename_fold.py`.

## Settled Rulings

1219 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
