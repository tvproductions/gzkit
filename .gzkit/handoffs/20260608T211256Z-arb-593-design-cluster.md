---
mode: CREATE
adr_id: ADR-0.0.67
branch: main
timestamp: "2026-06-08T21:12:56Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260608T204229Z-arb-proof-binding-defect-593.md
---

<!-- Handoff document for ADR-0.0.67 — created by claude-code at 2026-06-08T21:12:56Z -->

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

Continues from `20260608T204229Z-arb-proof-binding-defect-593.md`. That handoff's
five advised steps were resumed under explicit operator authorization ("do next
steps"). Two mechanical/reversible steps executed; two decisions ruled by the
operator; the design cluster deliberately deferred to a fresh session.

**Executed this session (ground truth):**

- **Revert landed — `aec872f4`** (`revert(obpi): drop ADR-0.0.67 ln: bindings —
  defect #593 in miniature`). Reverts `bb108622`. Removed 81 lines of `ln:`
  proof-binding frontmatter (13 REQs × ARB receipt-IDs) across the three
  ADR-0.0.67 briefs. Discriminating fact resolved from the **ledger** (not
  frontmatter): all three OBPIs were `attested_completed` (attestor g0;
  receipts 2026-06-07T21:47, 2026-06-08T00:33, 2026-06-08T07:44) **before**
  `bb108622` (13:50). So `bb108622` mutated attested-brief frontmatter post-
  attestation, and the revert **restores** the attested state — GHI #549's
  attested-edit gate does not block a corrective revert. Pre-commit gates passed.
- **GHI #594 filed** — `arb: no archive/purge half — 1875 receipts accumulate
  unbounded` (`enhancement` + `runtime` + `tech-debt`). Cross-linked to sibling
  #585 (handoff archive — same root shape, different surface); blocker comment
  records that no same-session destination was authored (needs an operator design
  conversation on retention policy).

**Operator rulings this session:**

- **ADR-0.0.67 → keep held.** Ceremony stays paused at closeout Step 6
  (unattested); attest only after the #593 substrate fix lands. Nothing unwound;
  the three OBPIs remain `attested_completed`.
- **Design cluster (#549 + #593 + rename) → stop, resume in fresh session.** Do
  not vibe a foundation ADR at the tail of a resume; enter the constrained design
  deliberately (this handoff is that boundary).

## Important Context

- **ARB = Agent Reported Bugs / Agent Self-Reporting.** Defect telemetry —
  ephemeral, gitignored (`artifacts/` swept into `.gitignore` by chore `9a543890`,
  2026-05-08), NOT ledger-backed, NOT attestation proof. `gz arb --help` and
  `AGENTS.md` § Attestation still mislabel ARB receipts as "canonical attestation
  evidence" — that identity drift is part of defect #593, to be corrected in its
  ADR, not honored.
- **#593 is the substrate defect.** `_receipt_exists`
  (`src/gzkit/governance/trust_audits/closeout_proof_binding.py:134-136`) checks
  for `artifacts/receipts/<id>.json` file existence — a gitignored, machine-local,
  ledger-absent substrate. OBPI-0.0.63-03's own brief (REQ-0.0.63-03-03/-04)
  specified a **ledger-existence** floor; the implementation regressed to file
  existence. The fix re-roots proof-binding at **committed** proof, per-REQ and
  kind-aware (ADR-0.0.59 matrix): BEHAVIOR→`@covers` test; SUPPORT→ledger
  `artifact_edited` event; STRUCTURAL-FENCE→parent-ADR `## Boundary Invariants`.
- **`ln:`→`req_evidence:` rename** is folded into #593's fix. `req_evidence` is the
  self-documenting original (the Pydantic class is `ReqEvidence`); `ln` is drift
  with no documented expansion. **17 attested briefs repo-wide still carry `ln:`
  blocks** (`grep -rl '^ln:' docs/design/adr --include='*.md'` → 17; 0 use
  `req_evidence:`). The rename touches all 17 → squarely #549 territory.
- **#549 logically precedes the rename.** It is the doctrine gate: *may attested
  briefs be textually corrected for zero-semantic-change drift (e.g. a pure
  key-rename) without re-attestation?* No canonical answer exists (Never #7 covers
  *reading* Layer-1 vs Layer-2; the *write*-side is ungoverned). #549's own
  routing hint: pool ADR `ADR-pool.attested-record-edit-doctrine`.
- **META (carried forward, still binding):** in-flight design at this repo's scale
  is itself a vibing surface. The prior session demonstrably vibed (a wrong
  "retire `ln:`, use `@covers`" call — `@covers` is BEHAVIOR-only). #593's fix
  MUST be designed in constrained mode (tight scope, ground truth per step,
  adversarial check per move), not reactive dialogue. This is why the cluster was
  deferred rather than attempted now.

## Decisions Made

- **Decision:** Revert `bb108622` rather than build on it or rewrite history.
  **Rationale:** The `ln:` bindings pointed at ephemeral ARB receipts (#593 in
  miniature); a forward revert keeps the defect-and-removal visible per
  ledger-of-truth doctrine. The three commits are unpushed but a reset would erase
  the audit trail.
  **Alternatives rejected:** `git reset`/rebase (erases the defect record);
  amending the bindings to point elsewhere (no committed substrate exists yet —
  that *is* #593's design work).

- **Decision:** The revert is corrective, so GHI #549 does not gate it.
  **Rationale:** Ledger shows the briefs were attested *before* `bb108622`; the
  revert restores the attested-time frontmatter rather than making a new
  post-attestation edit. #549 governs the *forward* rename, not the restoration.
  **Alternatives rejected:** Block the revert pending #549 (would freeze a
  corrective action behind an unrelated open doctrine question).

- **Decision (operator):** Keep ADR-0.0.67 held at Step 6; do not unwind.
  **Rationale:** The OBPIs are sound and attested; only the ADR-level closeout is
  blocked by #593's substrate. Holding preserves all completed work.
  **Alternatives rejected:** Formally unwind the closeout (no governed `--abort`
  path exists; would be manual teardown for no benefit).

- **Decision (operator):** Defer the #549 + #593 + rename cluster to a fresh,
  focused session.
  **Rationale:** Constrained-mode design mandate; avoid vibing a foundation ADR at
  the tail of a resume.
  **Alternatives rejected:** Draft the #549 pool ADR now; begin #593 design now.

- **Decision:** ARB lifecycle (#594) is a separate concern from #593, left
  open-with-blocker (not routed to a destination).
  **Rationale:** Retention policy (window, archive format, purge authorization,
  harvest-before-purge ordering) is a genuine operator design conversation, not a
  mechanical fix; possibly unified with #585 (handoff archive) under one pool ADR.
  **Alternatives rejected:** Auto-authoring a pool ADR now (would vibe a policy the
  operator must decide).

## Immediate Next Steps

<!-- ADVISORY ONLY — present and await operator authorization before acting. -->

1. **Open the constrained design for the #549 + #593 + rename cluster** (likely via
   `gz-design`). Tight scope, ground-truth-per-step, adversarial check per move.
   Resolve **#549 first** — it gates the rename.
2. **#549 doctrine ruling (drafted, operator to rule):** admit a CLOSED enumeration
   of semantics-preserving corrections to attested briefs without re-attestation —
   (a) renamed-target pointer updates, (b) pure key-renames of evidence frontmatter
   (`ln:`→`req_evidence:`), (c) schema-conformance heading rewrites. REQUIRE
   re-attestation for any change to REQ text / acceptance criteria / evidence
   *content* (which receipts a REQ binds). FORBID silently re-pointing a REQ's
   proof. Mechanize as a validator scope; route to pool ADR
   `ADR-pool.attested-record-edit-doctrine`.
3. **Design #593's fix:** foundation ADR amending ADR-0.0.63 (proof-binding) +
   `AGENTS.md` § Attestation + ARB's stated identity. Re-root `_receipt_exists`
   from file-existence to per-REQ kind-aware committed-proof resolution. Fold in
   the `ln:`→`req_evidence:` rename across the 17 briefs (gated by #549's ruling).
   Not a direct-fix.
4. **Route #594** (ARB lifecycle) — decide with the operator whether ARB-receipt
   retention and handoff retention (#585) share one pool ADR or get separate homes;
   author the destination, then close #594 `superseded`.
5. **After #593's substrate fix lands,** resume ADR-0.0.67's closeout ceremony from
   Step 6 and attest.

## Pending Work / Open Loops

- **GHI #593** (open) — the foundation substrate defect. Needs the constrained
  design + ADR. Blocks ADR-0.0.67 attestation.
- **GHI #549** (open) — attested-brief-edit doctrine gate. Gates the rename in
  step 3. Routing hint: pool ADR `ADR-pool.attested-record-edit-doctrine`.
- **GHI #594** (open, blocker comment) — ARB archive/purge lifecycle; sibling of
  #585. Needs operator retention-policy conversation.
- **GHI #591** (open) — `gz obpi audit` coverage uses whole-`src` denominator;
  ≥40% floor structurally unreachable for scoped OBPIs. Direct-fix candidate,
  deferred.
- **GHI #592** (open) — gate-scope fix landed (`814099fe`); two named sub-defects
  remain (`--pause`d ceremonies counted in-scope; BLOCKED ADR-0.0.41 reached
  step 6). Close or split.
- **ADR-0.0.41** — stale parked ceremony at Step 6 for a BLOCKED ADR; no governed
  `--abort` path exists. Disposition unresolved.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; `git rev-parse --short HEAD` is `aec872f4`
- [ ] `git log --oneline -2` shows `aec872f4` (revert) atop `e87bbe75` (prior handoff)
- [ ] `git show --stat aec872f4` shows 81 deletions across the three OBPI-0.0.67 briefs
- [ ] `grep -rl '^ln:' docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/` returns nothing (bindings reverted)
- [ ] `grep -rl '^ln:' docs/design/adr --include='*.md' | wc -l` is 17 (the rename scope, unchanged elsewhere)
- [ ] `uv run gz adr status ADR-0.0.67` shows 3/3 `attested_completed`, closeout READY, QC PENDING (human attestation)
- [ ] `.gzkit/ceremonies/ADR-0.0.67-tool-skill-invariant1-enforcement.ceremony.json` shows `current_step: 6`, `attestation: null`, `paused_at` set — ceremony genuinely held
- [ ] `gh issue view 594` is open with the blocker comment; `gh issue view 585` carries the sibling cross-link
- [ ] Working tree: `obpi-audit.jsonl` (M) and the ceremony JSON (??) are uncommitted ceremony artifacts (expected)

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — proof-binding validator; `_receipt_exists` (file-existence floor, the #593 locus) and the `adr_id`-scoped `validate_closeout_proof_binding` (the #592 fix)
- `src/gzkit/commands/closeout_ceremony.py` — `_gate_proof_binding` passes the ceremony's own adr_id into the validator (the #592 fix)
- `src/gzkit/governance/brief_structure.py` — the `ReqEvidence` model plus the `ln` frontmatter field (the rename target)
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-01-recursive-verb-path-enumeration.md` — restored to attested frontmatter by the revert (no `ln:`)
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-02-wire-orphan-verbs-into-skills.md` — same
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-03-delete-deprecated-lock-aliases.md` — same
- `.gzkit/ceremonies/ADR-0.0.67-tool-skill-invariant1-enforcement.ceremony.json` — paused ceremony state (Step 6, unattested)
- `docs/design/adr/pool/ADR-pool.tdd-receipt-stream.md` — the separate-but-related governance-event receipt stream concept
- `.gzkit/handoffs/20260608T204229Z-arb-proof-binding-defect-593.md` — predecessor handoff (the five-step plan this session executed/deferred)

## Environment State

Python 3.13 / uv. Branch `main`, 4 commits ahead of `origin/main` (unpushed:
`814099fe`, `bb108622`, `e87bbe75`, `aec872f4`). Pre-commit gates green on the
revert commit. No environment-specific blockers.
