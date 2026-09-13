---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T07:56:15Z'
agent: claude-code
session_id: 89fe194c-e710-4a42-a2c2-c4dd7c0bbc7d
continues_from: .gzkit/handoffs/20260913T033449Z-exit-code-labels-and-rulings-booking.md
---

## Current State Summary

Whole-session handoff for session 89fe194c (2026-09-12/13). It supersedes the two partial handoffs this session wrote (`20260913T024806Z-chore-class-schema-and-found-defects.md`, `20260913T033449Z-exit-code-labels-and-rulings-booking.md`) as the single carrier; both stay in the chain.

The session resumed `20260912T235557Z-rnd-alignment-chores-rnd-reconstructed.md`. Its advised step 1 had already been done by session 7bf35675 (`fd6ededf2`, `44b8f4a98`). The operator ruled step 2 via one GHI, so the chore class system work order was filed as GHI #999 and step 1 of its ratified order landed in `f1c9b0e59`: `ChoreDeclaration` (class, rung, idempotent, staleness, remediation, nonAuthority, governingRule). Partial or malformed declarations fail closed; an absent one is announced and still runs (40 of 40 undeclared today).

The operator then called the session report "very sloppy" for listing three found defects as notes. All three and everything they led to were closed in-session:
- Chore lists in the design record re-measured by reading all 40 CHORE.md and corrected (`1fc04aef2`); two stale chore instructions fixed there too.
- Rulings store lag filed as GHI #1000, ruled "Book at authoring", fixed and closed (`2909096e8`, `6d7aeca62`). Verified live: a handoff's own rulings are searchable the moment it is written.
- Exit code 2 conflict filed as GHI #1001; first ruling was made on a framing that omitted attested REQ-0.0.4-02-03, re-put, ruled "Keep 2; fix the labels", fixed and closed (`fa45e2504`) with a registered negative control.
- CLI error text rendered as Rich markup, deleting bracketed spans (`670e018cc`); the same class in 12 more sites via widening GHI #944's roster (`2081eab69`); handoff rulings, resume preview and create refusal printed through markup, and a search miss reported as an empty store (`a432a5877`).
- Chore metadata duplication (CHORE.md vs acceptance.json and registry.json) filed as GHI #1002.

State at authoring: HEAD `1459eb836`, `main` level with origin, clean tree, no OBPI locks. gz check passed with real exit 0 before every commit set; heavy-lane ARB receipts emitted and cited in the #1000 and #1001 close comments.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system** — changed this session: own operator rulings now booked at authoring (GHI #1000 closed), rulings and refusal output print verbatim, search miss names the corpus size. Observed: rulings store holds 831 lines at authoring. Not touched: GHI #870 (OPEN, ResumeResult.chain read by nobody).
- **ghi triage** — filed #999, #1000, #1001, #1002; closed #1000 and #1001. No `ghi-triage` pass was run, so queue totals are unverified.
- **adr/obpi campaign** — no OBPI work (IRON LAW; operator initiates). No locks. ADR-0.35.0 remains TOPMOST, untouched. The chore class system advances the Movement C `doctrine-declared-without-mechanism` box's agent-side arm only; scorecard gained row 91 (Mechanical, NC-witnessed) and row 92 (Judgment), Promotable count unchanged.
- **new R&D** — the resumed handoff's R&D skill design (step 4) and alignment Pass D (step 3) were not worked; `docs/governance/capability-control-review-2026-09-12.md` not touched.

### Gotchas learned
- Background-task notifications reported exit 0 on gz check runs whose real exit was 1. Only the verifier's own exit captured immediately (`echo "REAL EXIT: $?"`) is evidence (tests.md, GHI #969). The verifier-pipe-gate hook also refuses any sequence where a verifier is not the last statement.
- A Mechanical advisory-scorecard row needs a registered property-level negative control cited `NC:<claim-id>`, and its rule text must appear verbatim in the per-turn surface (`gz validate --surface-fidelity`). A rule version bump fails gz check until the Coverage Ledger row is re-scored.
- The private cross-package import ratchet is shrink-only. Claim sources should call `gzkit.enforcement.extend_known_claims`, never import `_KNOWN_QC_CLAIM_IDS`.
- Before putting a canon conflict to the operator, read every attested REQ on the surface; the #1001 misframing came from reading only the constants REQ.

### Chore class system facts (authoritative in `docs/governance/chore-class-system.md` § The measured state)
- Stop at data: firm cli-contract-governance, evidence-integrity-audit, skill-trigger-testing; borderline dependency-currency, control-surface-rule-vs-check-drift; ambiguous-excluded pool-triage, arb-pattern-extraction.
- Self-contradictory: firm repository-structure-normalization, skill-command-doc-parity; ambiguous ledger-vocabulary-inertness.
- Declaration keys are camelCase to match the registry; remediation categories use CSAF underscore spelling; `governingRule` is `.gzkit/rules/<file>.md` optionally with ` § clause`, or `none`.
- The absence-to-refusal flip belongs to #999 step 5, not earlier.

## Decisions Made

- [operator-ruled] Resume ruling on the prior handoff: "Step 2 via one GHI (Recommended)" — one work-order GHI for the chore class system (#999), GHI #936 stays the order for the status verb.
- [operator-ruled] Licenses at the schema step: "rung + idempotent (Recommended)" — rung carries the writing license; a required boolean idempotent carries the scheduling license.
- [operator-ruled] Authorization expiry: "Not now (Recommended)" — no expiry field; recorded, not adopted.
- [operator-ruled] Rollout: "Warn, flip at step 5 (Recommended)" — an undeclared chore is announced and still runs until per-chore declarations land.
- [operator-ruled] Session correction, verbatim "this seems very sloppy": defects found in flight are fixed or routed to a work order in-session, never listed back to the operator as notes.
- [operator-ruled] GHI #1000: "Book at authoring (Recommended)" — gz handoff create books the document's own operator rulings when it writes the handoff, accepting that a later linked handoff in another lineage inherits them.
- [operator-ruled] GHI #1001 re-put with REQ-0.0.4-02-03 disclosed: "Keep 2; fix the labels (Recommended)" — parse errors keep exiting 2 and code 2 is labelled Usage or System/IO; the earlier "Usage error → 1" selection is withdrawn as made on an incomplete framing.
- [agent-chose] Built a registered negative control for scorecard row 91 rather than scoring it Promotable, because the Movement C box drives Promotable rows to zero and the row carried observed drift evidence.
- [agent-chose] Split chore metadata duplication into its own GHI (#1002) instead of attaching it to #999, since it is a different failure class.
- [agent-chose] Left per-command manpage exit-code tables unchanged under #1001: each describes that command's own code-2 cause and stays true.

## Immediate Next Steps

1. GHI #999 step 3: the class-conformance validator — a CHORE.md whose workflow contradicts its declared rung fails — reading criteria and version from the authority GHI #1002 settles; take #1002 first or together.
2. GHI #1002: reconcile the 17 CHORE.md acceptance tables and 7 versions with `acceptance.json` and `registry.json`, citing the JSON as authority per `.claude/rules/governance-core.md`, with a witness that fails on today's tree.
3. GHI #936 (step 2 of the chore order): `gz chores status` rendering current / due / overdue / paused from the staleness declaration, announced in `scripts/session_orientation.py`, never gating.
4. Resumed-handoff step 4, in a fresh session: R&D skill design — confirm or overturn the orchestrator-over-disciplines resolution, one skill versus orchestrator plus namespace, rule on `.out-of-scope/`, draft the campaign R&D-front amendment text for ratification.

## Pending Work / Open Loops

- GHI #999 steps 4-6: README class, rung and admission semantics; per-chore declarations (apply the conversion directive, fix the self-contradictory chores, remedy the stop-at-data ones, calibrate the control-surface five individually) with the absence-to-refusal flip; the suppression rule with its witness.
- Read GHI #997 and GHI #808 before declaring eval-feedback-cluster and decommission-tautological-tests.
- Resumed-handoff step 3: rule-chore Pass D alignment audit and the two middle-scale rule clauses (package API declaration, catch-all module prohibition) — each lands only with its witness.
- GHI #870 (handoff chain consumption) open on the handoff front, untouched.
- GHI #810 (CLI-shape Promotable rows) open, adjacent to #1001 [settled], untouched.
- No ghi-triage pass this session; queue state beyond the issues named here is unverified.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run gz handoff rulings --search "Keep 2"
uv run gz chores list
gh issue view 999 --json state,title
gh issue view 1000 --json state,title
gh issue view 1001 --json state,title
gh issue view 1002 --json state,title
gh issue view 936 --json state,title
uv run -m unittest tests.commands.test_chores_declaration tests.cli.test_exit_code_claims tests.governance.test_handoff_ruling_store tests.policy.test_rich_markup_escaping
```

Expected at authoring: 0 0; no active locks; the Keep 2 search returns the #1001 ruling; chores list ends "40 of 40 chores carry no class declaration (GHI #999)."; #999, #1002 and #936 OPEN, #1000 and #1001 CLOSED; tests green. Re-run rather than trust these.

## Evidence / Artifacts

- `src/gzkit/commands/chores_declaration.py` and `tests/commands/test_chores_declaration.py` — chore declaration schema (GHI #999).
- `docs/governance/chore-class-system.md` — licenses reconciled, field table as landed, measured state corrected.
- `src/gzkit/chores/README.md` — Class Declaration section.
- `src/gzkit/cli/helpers/exit_code_claims.py` and `tests/cli/test_exit_code_claims.py` — NC:cli-usage-error-exit-two (GHI #1001).
- `.gzkit/rules/cli.md` — rule 0.7.0; `docs/governance/advisory-rules-audit.md` — rows 91 and 92.
- `src/gzkit/handoff_api.py` and `tests/governance/test_handoff_ruling_store.py` — rulings booked at authoring (GHI #1000).
- `tests/policy/test_rich_markup_escaping.py` — widened free-text roster (GHI #944).
- `tests/cli/test_error_boundary_markup.py` and `tests/test_handoff_cli.py` — verbatim rendering tests.
- `.gzkit/handoffs/20260913T024806Z-chore-class-schema-and-found-defects.md` and `.gzkit/handoffs/20260913T033449Z-exit-code-labels-and-rulings-booking.md` — this session's partial handoffs.
- Commits `f1c9b0e59`, `670e018cc`, `2081eab69`, `a432a5877`, `1fc04aef2`, `fa45e2504`, `2909096e8`, `6d7aeca62`.
- ARB receipts `arb-ruff-4ad63df49a1443caaeef2bd1b41f0c14`, `arb-step-typecheck-80e979e5eb7b4a6a8ead42f1ce06a44c`, `arb-step-unittest-0967bf57f9d745e7b378da2b53d0e2d8`.
- GitHub issues #999, #1000, #1001, #1002.

## Settled Rulings

830 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
