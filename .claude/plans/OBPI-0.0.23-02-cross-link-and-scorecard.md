# Plan: OBPI-0.0.23-02-cross-link-and-scorecard

## Context

- **OBPI:** `OBPI-0.0.23-02-cross-link-and-scorecard`
- **Parent ADR:** `ADR-0.0.23-agent-failure-mode-taxonomy` (foundation, lite)
- **Objective:** Wire `.gzkit/rules/agent-failure-modes.md` (landed under
  OBPI-01) into the always-loaded contract surface (`AGENTS.md` § DO IT
  RIGHT) with a one-line pointer, and register it in the advisory-rules
  audit scorecard so `gz validate --advisory-scorecard` surfaces it.
- **Lane / kind / attestation:** Lite lane × foundation kind ⇒ brief-level
  Gate 5 (TTY + `ATTEST`) is required at completion per AGENTS.md § Lane &
  Kind & Sensitivity Attestation Matrix.
- **STOP-on-BLOCKERS check:** OBPI-01 deliverable
  `.gzkit/rules/agent-failure-modes.md` exists (229 lines, version 0.1.0).
  Cross-link target resolves; safe to proceed.

### Destination-in-mind disclosure

Before writing this plan I had already concluded the cleanest cross-link
seat in `AGENTS.md` is a one-line pointer appended to § DO IT RIGHT
"Extracted pedagogy" subsection (line ~80), parallel in shape to the
existing `agent-contract-rationale.md` pointer at line 76. The scorecard
entry follows the shape of the most-recently-added foundation rule
(Security Sensitivity, lines 188–192), with classification **Judgment**
since the rule is a vocabulary, not a mechanical check (the brief
explicitly names the starting classification in REQ-3).

### Rejected alternatives

1. **Inline pointer inside one of the numbered DO IT RIGHT invariants
   (6a / 6c / 6g / 6h)** — rejected: the rule is the *catalogue* the
   invariants point at, not a sub-clause of any one of them. Inlining
   inside e.g. 6g implies 6g owns the taxonomy, which it does not.
2. **Add the pointer at the end of the "Extracted pedagogy" paragraph
   as a continuation of that sentence** — rejected: pedagogy points at
   `agent-contract-rationale.md` (per-turn pedagogy lift); the failure-
   mode taxonomy is canonical reviewer vocabulary, not pedagogy.
   Distinct seat needed.
3. **Score the rule as Promotable up front** (anticipating GHIs
   #308–#312) — rejected: the brief explicitly says "start at
   **Judgment**". Promotion lands when the validator lands; pre-scoring
   would conflate doctrine state with implementation state.
4. **Append a fresh top-level § (e.g. § Agent Failure-Mode Taxonomy) to
   AGENTS.md** — rejected: brief REQ-5 is "NEVER inline the failure-
   mode taxonomy into AGENTS.md — the pointer is one line". A new
   section would be in the spirit of inlining; the discipline is one
   line, one pointer.

## Files

- `AGENTS.md` (modify) — one-line pointer in § DO IT RIGHT.
- `docs/governance/advisory-rules-audit.md` (modify) — new
  `### Agent Failure-Mode Taxonomy (`.gzkit/rules/agent-failure-modes.md`)`
  section before the `---` / `## Summary` boundary; update Summary
  Judgment counts.
- `docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/obpis/OBPI-0.0.23-02-cross-link-and-scorecard.md`
  (modify at completion) — Implementation Summary, Key Proof, Evidence,
  Human Attestation populated by `gz obpi complete` in Stage 5.

All paths are inside the brief's Allowed Paths (AGENTS.md, advisory-
rules-audit.md, parent ADR package scope). No paths from the Denied list
are touched.

## Steps

1. **Add the cross-link in AGENTS.md § DO IT RIGHT.** Insert one line
   immediately after the existing `See docs/governance/agent-contract-
   rationale.md § Rationale for 6g/6h …` line (line 76), in the form:

   > See [`.gzkit/rules/agent-failure-modes.md`](.gzkit/rules/agent-failure-modes.md)
   > for the canonical six-pattern failure-mode taxonomy these invariants
   > backstop ([ADR-0.0.23](docs/design/adr/foundation/ADR-0.0.23-agent-failure-mode-taxonomy/ADR-0.0.23-agent-failure-mode-taxonomy.md)).

   The line satisfies REQ-1 (one new line in § DO IT RIGHT pointing at
   the rule) and REQ-2 (cites both relative path and ADR-0.0.23).

2. **Add the scorecard section in `docs/governance/advisory-rules-audit.md`.**
   Append a new third-level section
   `### Agent Failure-Mode Taxonomy (`.gzkit/rules/agent-failure-modes.md`)`
   immediately before the `---` divider on line 194 (i.e. right after
   the Security Sensitivity row). The section carries one row, ID `49`,
   classification **Judgment**, with a Why column naming the vocabulary
   role and pointing at the future `gz validate --failure-mode-coverage`
   promotion path under follow-up GHIs #308–#312:

   ```
   | 49 | Six-pattern agent failure-mode vocabulary (Safeguard
   circumvention / Reckless action / Fabrication / Skipped cheap
   verification / Correction fails / Dishonest when caught) — drawn from
   Opus 4.7 § 2.3.6 + GPT-5.5 § 9.2; cited by name when reviewing PRs,
   filing defects, and extending the scorecard | **Judgment** |
   Vocabulary, not mechanical check. The mechanical defenses already
   exist as separate rules / gates (TTY+`ATTEST` authenticity gate,
   ARB receipts, hook fail-closed behavior, `gz validate --commit-
   trailers`, layered-trust T1/T2/T3); this rule is the shared name
   they point at. Promotion candidate `gz validate --failure-mode-
   coverage` tracked under GHIs #308–#312 per ADR-0.0.23 § Decision. |
   ```

   Satisfies REQ-3 (scorecard row exists, classification recorded).

3. **Update the Summary counts.** The existing block (lines 200–205)
   shows Judgment = 18 (31%). Adding one Judgment row makes Judgment =
   19 (32%). Mechanical stays 35; Promotable stays 5; Ambiguous stays
   0. Total rises 58 → 59. Recompute the percentages:
   - Mechanical: 35 / 59 = 59%
   - Promotable: 5 / 59 = 8%
   - Judgment: 19 / 59 = 32%
   - Ambiguous: 0%

   Update the dated note above the table to add a brief
   "and OBPI-0.0.23-02 added the failure-mode-taxonomy vocabulary row."

4. **Verify scorecard parity.** Run
   `uv run gz validate --advisory-scorecard` and capture the exit
   status. The scorecard self-test enforces "every `.gzkit/rules/*.md`
   file has a row" — the new rule file already exists, so the row added
   in Step 2 is what makes the check pass (REQ-4 — exit 0). If the
   validator surfaces other drift, fix only what this OBPI's scope
   allows; surface anything outside scope as a follow-up GHI per the
   defect-fix-routing thresholds.

5. **Verify documents and lint.** Run
   `uv run gz validate --documents` and
   `uv run gz lint`. Both already canonical baseline checks; capture
   ARB receipts via `uv run gz arb ruff` for lint and `uv run gz arb
   step --name validate-documents -- uv run gz validate --documents`
   for the docs scope so the Stage 4 evidence table cites real
   receipt IDs (lite lane, so missing receipts are warning-only — but
   foundation kind elevates rigor at brief-level).

6. **Confirm cross-reference resolution.** Run the two `grep` commands
   from the brief's Verification block:

   ```
   grep -n "agent-failure-modes" AGENTS.md
   grep -n "agent-failure-modes" docs/governance/advisory-rules-audit.md
   ```

   Both must return at least one match, naming the inserted lines.

7. **REQ → @covers parity check.** Run
   `uv run gz covers OBPI-0.0.23-02-cross-link-and-scorecard --json`.
   This OBPI is a docs-only change with three REQs whose verification
   is mechanical (`gz validate --advisory-scorecard` exit 0,
   `gz validate --documents` clean, `grep` matches). If the parity
   gate flags `uncovered_reqs > 0`, the existing scorecard self-test
   in `tests/governance/test_advisory_scorecard.py` (or wherever it
   lives) is the natural anchor — add `@covers` decorators or
   docstring references to the three REQs there. If no anchor test
   exists, author a thin sentinel under `tests/governance/` whose
   single purpose is to assert the two grep matches and the validator
   exit 0, decorated with the three REQ IDs. Do not author logic-bearing
   tests; the validator is the mechanism, the sentinel is the
   `@covers` graph anchor.

8. **Stage 4 evidence preview** (per OBPI pipeline Stage 4 template).
   Compose Value Narrative, Key Proof (one runnable command + observed
   output), Evidence table (with receipt IDs from Step 5), and the
   REQ coverage table mapping REQ-0.0.23-02-{01,02,03} to the
   `@covers` anchors confirmed in Step 7. Foundation-kind ⇒ brief-
   level Gate 5; await `attest completed` (or equivalent) from
   operator before Stage 5.

9. **Stage 5 closure** (driven by `gz-obpi-pipeline`). Compose
   Implementation Summary and Key Proof prose for `gz obpi complete`,
   present them to operator inline (closure-narrative gate), then
   invoke `gz obpi complete OBPI-0.0.23-02-cross-link-and-scorecard
   --attestor 'Jeffry Babb' --attestation-text "<verbatim+enrichment>"
   --implementation-summary "..." --key-proof "..."
   --attestor-present`. The pipeline marker written at Stage 1
   satisfies the `--attestor-present` co-presence proxy; PTY fallback
   only if the marker check is refused.

## Verification

```bash
uv run gz arb ruff
uv run gz arb step --name validate-documents -- uv run gz validate --documents
uv run gz arb step --name validate-advisory-scorecard -- uv run gz validate --advisory-scorecard
uv run gz arb step --name validate-brief-headings -- uv run gz validate --brief-headings
uv run gz validate --advisory-scorecard
uv run gz validate --documents
uv run gz lint
grep -n "agent-failure-modes" AGENTS.md
grep -n "agent-failure-modes" docs/governance/advisory-rules-audit.md
uv run gz covers OBPI-0.0.23-02-cross-link-and-scorecard --json
```

All commands must exit 0; grep results must show at least one
`agent-failure-modes` reference in each file; the `covers` JSON must
report `summary.uncovered_reqs == 0`.

## Notes

- **Foundation-kind brief.** `Lite` lane does not relax the brief-level
  Gate 5 requirement. `gz obpi complete` will refuse a non-TTY parent
  unless `--attestor-present` is supplied with the active pipeline
  marker present at `.claude/plans/.pipeline-active-OBPI-0.0.23-02-
  cross-link-and-scorecard.json` (Stage 1 of the pipeline writes it).
- **No scope expansion.** The brief explicitly forbids inlining the
  taxonomy (REQ-5) and bars edits to `.gzkit/rules/agent-failure-
  modes.md` (Denied — that file is OBPI-01's deliverable). Vendor
  mirrors `.claude/rules/agent-failure-modes.md` and
  `.github/instructions/agent-failure-modes.md` are also Denied here;
  they regenerate under OBPI-03.
- **Operator PII discipline.** Attestor identity is "Jeffry Babb" only;
  no email in any commit message, brief body, attestation text, or
  ledger entry per the AGENTS.md Local Agent Rules.
- **Sibling-ADR overlap (advisory).** `gz plan audit` flagged 18
  sibling OBPIs that also touch `docs/governance/advisory-rules-
  audit.md` and the parent ADR-0.0.23 directory. All overlaps are
  inert: the file is *the* scorecard catalogue, so every rule-shipping
  OBPI legitimately appends to it; collisions are append-time, not
  edit-time. No coordination needed beyond this OBPI's append site.
