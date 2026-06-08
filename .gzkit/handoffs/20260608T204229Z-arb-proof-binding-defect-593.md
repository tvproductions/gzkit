---
mode: CREATE
adr_id: ADR-0.0.67
branch: main
timestamp: "2026-06-08T20:42:29Z"
agent: claude-code
obpi_id:
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.67 — created by claude-code at 2026-06-08T20:42:29Z -->

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

A `/gz-adr-closeout-ceremony ADR-0.0.67` run uncovered a foundation-level
governance defect and was halted before attestation. The session pivoted from
closeout into defect-surfacing and a (deliberately abandoned) design dialogue.

**Committed (ground truth):**

- `814099fe` — `fix(closeout)`: scoped the EXECUTE→ATTESTATION proof-binding gate
  to `state.adr_id` (GHI #592). Was repo-global, so a parked/blocked sibling
  ADR's ceremony blocked unrelated closeouts. RED→GREEN regression added in
  `tests/governance/test_ceremony_ln_consumption.py::TestGateScopedToCeremonyAdr`;
  coupled gate-wiring assertions updated. Pre-commit gates passed.
- `bb108622` (current HEAD) — added `ln:` proof-bindings to ADR-0.0.67's three
  briefs. **This commit is itself an instance of defect #593** (it binds REQs to
  ephemeral ARB receipt-IDs that are not in the committed ledger). It should
  most likely be **reverted**, not built upon.

**Paused, not attested:**

- ADR-0.0.67's closeout ceremony is **paused at Step 6 (ATTESTATION)**. State
  persists in `.gzkit/ceremonies/ADR-0.0.67-tool-skill-invariant1-enforcement.ceremony.json`.
  Demos 1–4 ran and were acknowledged; the ARB evidence quartet + behave suite
  (335 scenarios, 0 fail) were green; spec-reviewer and quality-reviewer
  subagents returned SOUND-with-caveats. The ceremony stopped when the
  proof-binding gate exposed defect #593. **Do not attest** until #593 is fixed.

## Important Context

- **ARB = Agent Reported Bugs** (operator's binding clarification). It envelops
  common QA activities (ruff/ty/unittest/coverage) to **capture defect
  patterns** — it is *defect telemetry*, not attestation proof. Its receipts are
  *correctly* ephemeral and gitignored. `gz arb --help` and `AGENTS.md` §
  Attestation currently mislabel ARB receipts as "canonical attestation
  evidence" — that identity drift is part of defect #593, not a thing to honor.
- **The `ln:` proof-binding floor checks the wrong layer.** `_receipt_exists`
  (`src/gzkit/governance/trust_audits/closeout_proof_binding.py:134-136`) checks
  `artifacts/receipts/<id>.json` file existence. `artifacts/` was swept into
  `.gitignore` by chore `9a543890` (2026-05-08, grouped with caches/locks). So
  the proof substrate is gitignored, machine-local, non-portable; and ARB emits
  no ledger event, so receipt-IDs reach the committed ledger only as free-text
  inside `obpi_receipt_emitted` attestation strings.
- **The original design was already ledger-backed.** OBPI-0.0.63-03's own brief
  (REQ-0.0.63-03-03 / -04) specifies a **ledger-existence** floor ("cited
  receipt-ID resolves to a ledger event"). The implementation regressed to file
  existence, and `test_typo_receipt_id_fails_closed` is vacuous on the
  file-vs-ledger distinction (a typo'd ID is absent from both). So #593 is partly
  "the code never did what its own brief specified."
- **`@covers` is BEHAVIOR-only.** Per ADR-0.0.59's proof-channel matrix, only
  BEHAVIOR REQs use `@covers`; SUPPORT REQs prove via a ledger `artifact_edited`
  event + structural validator, and STRUCTURAL-FENCE REQs via a parent-ADR
  `## Boundary Invariants` entry. `ln:` exists to be the *kind-agnostic* per-REQ
  floor — so it cannot simply be retired in favor of `@covers`.
- **`ln` is a bad field name.** The Pydantic class is `ReqEvidence`, the field is
  `ln`, the extracted key is `ln_entries`. OBPI-0.0.63-03's changelog booked a
  `req_evidence`→`ln` rename as "resolving drift"; no source documents what `ln`
  expands to. The self-documenting original (`req_evidence`) is still the class
  name.
- **META: in-flight design at this repo's scale is itself a vibing surface.** The
  agent demonstrably vibed during this session (a confident "retire `ln:`, use
  `@covers`" recommendation that was wrong because `@covers` is BEHAVIOR-only;
  caught by the operator). Defect #593 is what vibing-at-scale produces — locally
  plausible layers stacked until they drift from the ledger-of-truth. #593's fix
  must be designed in a **constrained mode** (tight scope, ground truth per step,
  adversarial check per move), not reactive in-flight dialogue.

## Decisions Made

- **Decision:** Keep the closeout proof-binding mechanism; it has real
  anti-vibing value (machine-checkable REQ→evidence replacing narrative claims).
  **Rationale:** It is the structural floor that converts "agent says proven"
  into "validator checks proven."
  **Alternatives rejected:** Retire it in favor of `@covers` — rejected because
  `@covers` is BEHAVIOR-only and would orphan SUPPORT / STRUCTURAL-FENCE REQs.

- **Decision:** ARB stays defect telemetry — ephemeral, gitignored, NOT
  ledger-backed.
  **Rationale:** Operator: ledger-backing ARB would be "using ARB for other
  things" — itself a drift. ARB's job is defect-pattern capture, not proof.
  **Alternatives rejected:** Emit an `arb_receipt_emitted` ledger event (the
  original, retracted #593 proposal) — deepens the category error.

- **Decision:** Re-root proof-binding to resolve against **committed** proof, ARB
  out of the proof path; fix direction is per-REQ, kind-aware resolution
  (BEHAVIOR→`@covers` test; SUPPORT→ledger `artifact_edited` event;
  STRUCTURAL-FENCE→parent-ADR `## Boundary Invariants`).
  **Rationale:** Each REQ kind already has a committed proof channel (ADR-0.0.59);
  honors `ln:`'s original ledger-backed intent.
  **Status:** Direction only — NOT rigorously designed. Vibe-liable. Must be
  designed in a constrained mode and booked as a foundation ADR.

- **Decision:** Rename `ln:` → `req_evidence:` (revert the drift; restore the
  class-matching self-documenting name), folded into the #593 fix.
  **Rationale:** Substrate-agnostic and correct regardless of #593's outcome, but
  it shares the exact surface as #593 (schema, validator, `ln_entries` key, 17+
  briefs, SKILL.md, manpage, tests) — doing both together avoids touching every
  brief twice.
  **Alternatives rejected:** Standalone rename now — defensible but churns the
  briefs twice; invent a new name — rejected, the original `req_evidence` exists.

- **Decision:** `tdd-receipt-stream` (governance-event receipt stream) and #593
  are SEPARATE concerns sharing one doctrinal root.
  **Rationale:** `tdd-receipt-stream` *creates* a committed home for proof that
  doesn't exist yet (ARB-unsafe events); #593 *re-points* at proof already
  committed (`obpi_receipt_emitted`). Neither blocks the other.

## Immediate Next Steps

<!-- ADVISORY ONLY — present and await operator authorization before acting. -->

1. **Revert `bb108622`** (ADR-0.0.67 `ln:` bindings) — they are defect #593 in
   miniature (bound to ephemeral ARB receipts). Confirm disposition with operator
   first.
2. **Decide ADR-0.0.67's disposition** with the operator: keep paused/held until
   #593's substrate fix lands, or formally unwind the in-flight closeout.
3. **Resolve GHI #549** (may attested-brief frontmatter be edited for a
   non-semantic correction, e.g. a pure key-rename, without re-attestation?) —
   it gates both the `ln:`→`req_evidence:` rename and the #593 brief edits.
4. **File the ARB-lifecycle GHI** (separate concern): ARB has harvest
   (`arb patterns` / `arb advise`) but no `archive`/`purge` half; ~1875 receipts
   accumulated unbounded under gitignored `artifacts/`. Operator wants: harvest
   intelligence periodically, then archive and/or purge.
5. **Design #593's fix in a constrained mode** and book a foundation ADR amending
   ADR-0.0.63 (proof-binding) + `AGENTS.md` § Attestation + ARB's stated
   identity, folding in the `ln:`→`req_evidence:` rename. Not a direct-fix.

## Pending Work / Open Loops

- **GHI #591** (open, with blocker comment): `gz obpi audit` coverage criterion
  uses a whole-`src` denominator (`coverage report --format=total` over a single
  OBPI's narrow test file), so the ≥40% floor is structurally unreachable for any
  scoped OBPI. Design-resolved (denominator = brief Allowed Paths); a direct-fix
  candidate deferred past this ceremony.
- **GHI #592** (open): the gate-scope fix landed (`814099fe`); the issue body
  also names two sub-defects not yet addressed — `_iter_in_closeout_adrs` counts
  `--pause`d ceremonies as in-scope, and a BLOCKED ADR (ADR-0.0.41) was allowed
  to reach ceremony step 6. Close or split as appropriate.
- **GHI #593** (open, reframed): the foundation defect. Needs the constrained
  design pass + ADR.
- **ADR-0.0.41** has a stale parked ceremony at step 6 for a BLOCKED ADR (2/5
  OBPIs) — it triggered the #592 discovery. Disposition unresolved (no governed
  `--abort` path exists).
- **ARB identity drift** in `gz arb --help` and `AGENTS.md` § Attestation
  ("canonical attestation evidence") — to be corrected as part of #593's ADR.

## Verification Checklist

- [ ] `git branch --show-current` is `main`; `git rev-parse --short HEAD` is `bb108622`
- [ ] `git log --oneline -3` shows `bb108622` (ln bindings) and `814099fe` (gate fix)
- [ ] `uv run python -m unittest tests.governance.test_ceremony_ln_consumption tests.governance.test_closeout_proof_binding -q` passes (gate-scope regression)
- [ ] `.gzkit/ceremonies/ADR-0.0.67-tool-skill-invariant1-enforcement.ceremony.json` shows step 6, `attestation: null`, `paused_at` set — ceremony genuinely held
- [ ] `gh issue view 591`, `592`, `593` reflect the states above; `gh issue view 549` is the attested-brief-edit gate
- [ ] Working tree: `.gzkit/ceremonies/...67....json` and the demo-run `obpi-audit.jsonl` are uncommitted ceremony artifacts (expected)

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/closeout_proof_binding.py` — proof-binding validator; `_receipt_exists` (file-existence floor, the #593 locus) and the `adr_id`-scoped `validate_closeout_proof_binding` (the #592 fix)
- `src/gzkit/commands/closeout_ceremony.py` — `_gate_proof_binding` now passes the ceremony's own adr_id into the validator (the #592 fix)
- `tests/governance/test_ceremony_ln_consumption.py` — TestGateScopedToCeremonyAdr RED→GREEN regression for #592; updated gate-wiring assertions
- `src/gzkit/governance/brief_structure.py` — the ReqEvidence model plus the ln frontmatter field (the rename target)
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-01-recursive-verb-path-enumeration.md` — carries the `ln:` bindings added by `bb108622` (revert candidate)
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-02-wire-orphan-verbs-into-skills.md` — same
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-03-delete-deprecated-lock-aliases.md` — same
- `.gzkit/ceremonies/ADR-0.0.67-tool-skill-invariant1-enforcement.ceremony.json` — paused ceremony state (step 6, unattested)
- `docs/design/adr/pool/ADR-pool.tdd-receipt-stream.md` — the separate-but-related governance-event receipt stream concept

## Environment State

Python 3.13 / uv. Behave suite: 53 features, 335 scenarios passed, 0 failed,
1 skipped (run this session). Full unittest suite green via the closeout ARB
evidence pass (exit 0). No environment-specific blockers.
