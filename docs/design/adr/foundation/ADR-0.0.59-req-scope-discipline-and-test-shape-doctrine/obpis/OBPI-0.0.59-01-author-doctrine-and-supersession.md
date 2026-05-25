---
id: OBPI-0.0.59-01-author-doctrine-and-supersession
parent: ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.59-01-author-doctrine-and-supersession: Author REQ Scope Discipline Doctrine + Supersede Pool ADR + Close Superseded GHIs

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md`
- **Checklist Item:** #1 — "OBPI-0.0.59-01: Author REQ scope discipline doctrine (.gzkit/rules/tests.md § REQ Scope Discipline + docs/governance/req-scope-discipline.md canonical expansion) + reconcile GHI #270 tests.md § 6f vs tool-skill-runbook-alignment.md § Invariant 3 contradiction (output-form fixture tests are BEHAVIOR proofs) + supersede ADR-pool.obpi-req-taxonomy-scope-fence (its Path A/B/C/D rolls into Alternatives Considered with credit) + close GHI #165 and GHI #531 superseded against this ADR + add advisory-rules-audit.md scorecard entry classifying --req-kind-discipline Mechanical (lite lane: doctrine + scorecard only, no code/schema)"

**Status:** Draft

## Objective

Land the doctrine port for ADR-0.0.59: ship the three-kind REQ taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL-FENCE) with its proof-channel matrix as canonical rule + canonical doctrine doc, classify the rule as Mechanical-for-shape in the advisory scorecard, reconcile the long-standing GHI #270 doctrine contradiction (output-form fixture tests are BEHAVIOR proofs), supersede `ADR-pool.obpi-req-taxonomy-scope-fence` with its Path A/B/C/D analysis preserved as credit in the parent ADR's Alternatives, and close GHIs #165 and #531 superseded against ADR-0.0.59. This OBPI ships the contract OBPIs 02-05 consume; it ships zero code, zero schema, zero new CLI.

## Lane

**Lite** — doctrine + scorecard + rule update + supersession bookkeeping. No new CLI verb, no schema change, no runtime contract change. The behavior-bearing surfaces (validator in OBPI-02, parity gate in OBPI-03, chore in OBPI-04/05) are downstream consumers; this OBPI does not ship them. Per `.gzkit/rules/skill-surface-sync.md`, the rule-file edit is a rule-version bump (`tests.md` will rev 0.4.0 → 0.5.0); the new doctrine doc and scorecard row are content surfaces. Foundation-kind parent ADR-0.0.59 still triggers universal brief-level Gate 5 attestation per ADR-0.0.36, even though the lane is Lite.

## Allowed Paths

- `.gzkit/rules/tests.md` — append `## REQ Scope Discipline` subsection naming three-kind taxonomy, proof-channel matrix, brief-authoring tag syntax, and GHI #270 reconciliation note. Bump `<!-- rule-version: 0.5.0 -->` + visible block-quote per `.gzkit/rules/skill-surface-sync.md` non-negotiable rule #2.
- `docs/governance/req-scope-discipline.md` — NEW canonical doctrine expansion. Mirrors the ADR-0.0.54 / `docs/governance/agents-md-doctrine.md` shape: rule-file pointer, problem framing (the categorical category error + quantification: 32% project-wide / 42% governance fs-shaped ratio), three-kind taxonomy with proof-channel detail, port-vs-adapter framing, lift targets matrix, consequences (positive / negative / reversibility), related artifacts.
- `docs/governance/advisory-rules-audit.md` — new section "REQ Scope Discipline" with one scorecard row (row 59) classifying the rule Mechanical for shape; Summary count Mechanical 42→43; narrative paragraph updated.
- `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` — append `## Disposition` section noting supersession by ADR-0.0.59; Path A/B/C/D credit preserved (the pool ADR's body is unchanged; only the disposition is appended).
- `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/**` — parent ADR package scope (for brief edits, evidence updates, etc.)

## Creates these files

- **CREATE** `docs/governance/req-scope-discipline.md` — new canonical doctrine expansion (the encyclopedia entry the AGENTS.md / rule-file links resolve to)

## Denied Paths

- `src/gzkit/**` — no code shipped in this OBPI (validators in OBPI-02/03, chore in OBPI-04)
- `tests/**` — no tests written (Gate 2 is the structural-validator pass per the new taxonomy; this OBPI's REQs are [support] kind, witnessed by ledger + structural validator, not by @covers tests per ADR-0.0.59 § Decision)
- `src/gzkit/schemas/**` — no schema change (the brief-format inline tag is doctrine-only at this OBPI; mechanical enforcement is OBPI-02 scope)
- `data/**` — no data file changes (no waiver entries, no baseline files; those are OBPI-04 scope)
- `.gzkit/skills/gz-obpi-specify/**`, `.gzkit/skills/gz-obpi-pipeline/**` — skill updates downstream of validator land in OBPI-02
- `AGENTS.md`, `CLAUDE.md` — unchanged at this OBPI; doctrine pointer lift (if needed) lands per a subsequent ADR-0.0.54 OBPI-02 or later
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

This OBPI's REQs are authored under the new three-kind taxonomy as eat-your-own-dogfood. Mechanical validation of the `[kind]` tags lands in OBPI-02; this OBPI declares the kinds prose-explicitly for doctrinal coherence.

1. REQ-0.0.59-01-01 [support]: `.gzkit/rules/tests.md` carries a new `## REQ Scope Discipline` subsection (rule-version bumped 0.4.0 → 0.5.0 with visible block-quote + body HTML comment per `.gzkit/rules/skill-surface-sync.md` non-negotiable rule #2). The subsection MUST state the canonical three-kind taxonomy verbatim from parent ADR § Decision (BEHAVIOR / SUPPORT / STRUCTURAL-FENCE), the proof-channel matrix (covers_test / ledger_event / parent_adr_invariant), and the brief-authoring tag syntax `REQ-X.Y.Z-NN-NN [kind]: claim text`. Proof: ledger `artifact_edited` event citing `.gzkit/rules/tests.md`; structural validator `gz validate --documents` accepts the file.
2. REQ-0.0.59-01-02 [support]: `docs/governance/req-scope-discipline.md` exists as canonical doctrine expansion (fresh authoring; no compression-by-summarization). MUST cite the parent ADR, the rule file, the OpenAI/Karpathy harness-engineering framing, the three-kind taxonomy with per-kind proof-channel detail, the quantification (32% project-wide / 42% governance fs-shaped ratio with airlineops parity context), and the canonical reconciliation of GHI #270 (output-form fixture tests are BEHAVIOR proofs). Proof: ledger `artifact_edited` event for the new file; `gz validate --documents` accepts the file; `mkdocs build --strict` clean.
3. REQ-0.0.59-01-03 [support]: `docs/governance/advisory-rules-audit.md` gains a new section "REQ Scope Discipline" with one row (next-free integer, expected row 59) classifying the rule **Mechanical** for shape. Summary count: Mechanical 42 → 43, narrative updated naming ADR-0.0.59 OBPI-01 as the addition source. Proof: ledger `artifact_edited` event for the file; `gz validate --advisory-scorecard` exit 0.
4. REQ-0.0.59-01-04 [support]: GHI #270 reconciliation is captured in the new `## REQ Scope Discipline` subsection of `tests.md` as a footnote / inline note: output-form fixture tests (per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3) are **BEHAVIOR** REQ proofs — they test CLI render-code behavior, not file content. The apparent contradiction between tests.md § 6f and tool-skill-runbook-alignment.md § Invariant 3 dissolves once REQ kind is named. Proof: grep for "GHI #270" in `.gzkit/rules/tests.md` returns the reconciliation note; the note text references both rule files by name.
5. REQ-0.0.59-01-05 [support]: `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` gains an appended `## Disposition` section stating the ADR is **superseded** by `ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine`. The pool ADR's body content (Intent, Decision, Alternatives Considered Paths A-D, Notes) is preserved unchanged; only the Disposition section is added. The Disposition section names Path D specifically as the framing inherited by ADR-0.0.59's STRUCTURAL-FENCE proof channel. Proof: ledger `artifact_edited` event citing the pool ADR; `gz validate --documents` accepts the file; `gz adr report` still shows the pool ADR (supersession is a disposition note, not removal).
6. REQ-0.0.59-01-06 [support]: GHI #165 closed via `gh issue close 165 --comment` with disposition `superseded` against ADR-0.0.59, citing the ledger_event + parent_adr_invariant proof channels as the non-code REQ evidence GHI #165 named missing. Per `ghi-close` skill, the close comment cites a registered destination (ADR-0.0.59 visible in `gz adr report`). Proof: `gh issue view 165 --json state` returns `"state": "CLOSED"`; close-comment cites ADR-0.0.59.
7. REQ-0.0.59-01-07 [support]: GHI #531 closed via `gh issue close 531 --comment` with disposition `superseded` against ADR-0.0.59, citing the doctrinal correction and the open-with-blocker → closed-with-destination transition per `ghi-close` doctrine. Proof: `gh issue view 531 --json state` returns `"state": "CLOSED"`; close-comment cites ADR-0.0.59 and acknowledges the doctrinal reversal from GHI #530's superseded 5th-defense (which was the wrong shape).
8. REQ-0.0.59-01-08 [support]: No operator PII in any authored content (rule file, doctrine doc, scorecard entry, pool-ADR disposition note, GHI close comments). Per AGENTS.md § Local Agent Rules — operator-PII rule. Proof: explicit absence check before commit; grep for personal-email pattern returns empty.

> STOP-on-BLOCKERS: if `.gzkit/rules/tests.md`, `docs/governance/advisory-rules-audit.md`, or `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` is absent, print BLOCKERS and halt. (All present as of OBPI authoring 2026-05-25.)

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision** — quote the canonical statement verbatim (the three-kind taxonomy + proof-channel matrix + brief-authoring tag syntax + 4 decision items 1:1 with OBPIs) into this brief's Implementation Summary. Decision is the contract.
- [ ] Parent ADR § Intent — the OpenAI/Karpathy harness-engineering framing + quantification + operator's verbatim "staggering find" characterization.
- [ ] Parent ADR § Consequences — the positive consequences list informs the doctrine doc structure; the negative consequences list informs the 2am-operator bypass surface notes.
- [ ] Parent ADR § Alternatives Considered — the pool ADR's Path A/B/C/D framing must be preserved in the supersession note.
- [ ] Parent ADR § Q&A Transcript / 7 forcing functions answers — the pre-mortem (process-evidence as fourth kind), assumption surfacing (multi-channel REQs), 2am-operator (bypass mechanism), and reversibility (one-way doors) all inform the doctrine doc's caveats sections.

**Existing artifacts (read once, cache):**

- [ ] `.gzkit/rules/tests.md` — current state (version 0.4.0; the file to amend)
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3 — the doctrine the reconciliation note must name (the contradiction's other side)
- [ ] `docs/governance/advisory-rules-audit.md` — existing scorecard shape (row format, Summary table, narrative pattern). Most recent row is row 58 (Map-Not-Encyclopedia, added by OBPI-0.0.54-01 this session).
- [ ] `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` — pool ADR being superseded; preserve all existing content, append Disposition section only
- [ ] `docs/governance/agents-md-doctrine.md` — pattern reference for the new doctrine doc shape (canonical expansion authored fresh, structural mirrors)
- [ ] GHI #165 body — what non-code REQ proof channels were named missing (ledger + parent-ADR-invariant cover those)
- [ ] GHI #531 body — categorical defect framing; the doctrinal reversal of the GHI #530 5th-defense proposal

**Context — the existing mechanisms this doctrine composes with:**

- [ ] `gz covers OBPI --json` — current shape (will extend in OBPI-03)
- [ ] `gz validate --instructions-files-budget` + `--documents` + `--advisory-scorecard` — existing structural validators that prove SUPPORT-kind REQ artifacts; this OBPI's REQs are covered by them
- [ ] `.gzkit/ledger.jsonl` — `artifact_edited` is the most-frequent event type (3,117+ instances); the SUPPORT proof channel queries this event class

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/rules/tests.md` present (yes)
- [ ] `docs/governance/advisory-rules-audit.md` present (yes)
- [ ] `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` present (yes)
- [ ] `docs/governance/` directory writable (yes)
- [ ] `gh` CLI authenticated for GHI #165 and #531 close operations

**Existing Code (understand current state):**

- [ ] `.gzkit/rules/tests.md` — current state: 4,500 chars, rule-version `0.4.0`, contains Red-Green-Refactor + Tests-assert-semantics invariant 6f + Output-form fixture carve-out + TASK-Driven Workflow. The new `## REQ Scope Discipline` subsection appends after the existing § Two runners, one test surface section; the GHI #270 reconciliation note slots into the Output-form fixture carve-out as an inline annotation (output-form fixtures are BEHAVIOR REQ proofs, not contradiction with § 6f).
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3 — the "other side" of the GHI #270 contradiction: every skill output contract MUST have a test asserting render-form markers (box-drawing for table, JSON-parseable for JSON, etc.). Under the new taxonomy this is BEHAVIOR-kind testing of CLI render code; not in conflict with § 6f's prose-content-assertion prohibition.
- [ ] `docs/governance/advisory-rules-audit.md` — current state: 28k chars, last row is 58 (Map-Not-Encyclopedia under ADR-0.0.54, added 2026-05-25 earlier this session). Summary table shows Mechanical=42 / Promotable=6 / Judgment=19. New row 59 will be REQ Scope Discipline (Mechanical); Summary updates to 43/6/19.
- [ ] `docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md` — current state: 138 lines, contains Intent (8 scope-fence REQ instances on ADR-0.0.32 with table) + Decision (open surface questions) + 4 Alternatives Paths A/B/C/D with strengths/weaknesses + Notes + Promotion guidance. Body content preserved unchanged; only `## Disposition` section appended.
- [ ] `docs/governance/agents-md-doctrine.md` — pattern reference for the new doctrine doc shape. Authored 2026-05-25 under OBPI-0.0.54-01; structure: source ADR / rule-file pointer / authoring-context line, failure-pattern framing, invariant statement, port-vs-adapter framing, budget table, lift targets table, consequences (what changes / what does not change / reversibility), related artifacts. The new `docs/governance/req-scope-discipline.md` mirrors this shape with REQ-taxonomy specifics.
- [ ] `data/behave_coverage_waivers.json` — current state: schema_version + default_rationale + waivers map. The new `adr-0.0.59-content-only` rationale entry slots into default_rationale (mirrors `adr-0.0.54-content-only` added under OBPI-0.0.54-01). The OBPI's own waiver entry slots into waivers map (parallel to OBPI-0.0.54-01's entry). This is a downstream side effect of OBPI-01's completion ceremony, not an OBPI-01 deliverable.

## Quality Gates

### Gate 1: ADR
- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR § Decision quoted in Implementation Summary

### Gate 2: TDD
- [ ] This OBPI ships content; per ADR-0.0.59 § Decision, SUPPORT-kind REQs are witnessed by ledger event + structural validator, NOT by @covers tests. Gate 2 is satisfied by structural-validator clean run: `uv run gz validate --documents --advisory-scorecard` exit 0
- [ ] Tests pass (no regression): `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No new test files authored (would be anti-pattern under the very doctrine this OBPI ships)

### Code Quality
- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy-lane parent ADR; OBPI is Lite — still applicable to content-shipping OBPI)
- [ ] `docs/governance/req-scope-discipline.md` renders cleanly under `mkdocs build --strict`
- [ ] Scorecard entry renders correctly
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD
- [ ] No BDD scenario applies — content-only OBPI per the new doctrine being shipped. Waiver entry to land in `data/behave_coverage_waivers.json` citing `adr-0.0.59-content-only` rationale (consistent with ADR-0.0.54-01's `adr-0.0.54-content-only` precedent).

### Gate 5: Human (universal per ADR-0.0.36)
- [ ] Foundation-kind brief: explicit human attestation required at completion via `gz obpi complete --attestation-text "<operator verbatim>"`

## Verification

```bash
# REQ-01: rule file updated with new subsection and version bump
test -f .gzkit/rules/tests.md
grep -q "## REQ Scope Discipline" .gzkit/rules/tests.md
grep -q "rule-version: 0.5.0" .gzkit/rules/tests.md
grep -q "BEHAVIOR" .gzkit/rules/tests.md
grep -q "SUPPORT" .gzkit/rules/tests.md
grep -q "STRUCTURAL-FENCE" .gzkit/rules/tests.md

# REQ-02: doctrine doc exists
test -f docs/governance/req-scope-discipline.md

# REQ-03: scorecard entry present
grep -q "REQ Scope Discipline" docs/governance/advisory-rules-audit.md
grep -q "req-scope-discipline" docs/governance/advisory-rules-audit.md

# REQ-04: GHI #270 reconciliation note in rule file
grep -q "GHI #270" .gzkit/rules/tests.md

# REQ-05: pool ADR disposition appended
grep -q "Disposition" docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md
grep -q "ADR-0.0.59" docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md

# REQ-06/07: GHI states (run after gh issue close)
gh issue view 165 --json state | grep -q "CLOSED"
gh issue view 531 --json state | grep -q "CLOSED"

# Structural validator passes (Gate 2 + Gate 3 floor)
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Demo

```bash
# The new doctrine subsection in tests.md:
grep -A 20 "## REQ Scope Discipline" .gzkit/rules/tests.md | head -25

# The canonical doctrine expansion:
head -30 docs/governance/req-scope-discipline.md

# The scorecard row:
grep -B1 -A3 "REQ Scope Discipline" docs/governance/advisory-rules-audit.md

# The supersession note:
grep -A 10 "## Disposition" docs/design/adr/pool/ADR-pool.obpi-req-taxonomy-scope-fence.md

# The closed GHIs:
gh issue view 165 --json state,closedAt
gh issue view 531 --json state,closedAt
```

## Acceptance Criteria

(REQ-derived; per ADR-0.0.59 § Decision SUPPORT-kind REQs are witnessed by ledger event + structural validator; @covers-decorated tests are NOT required — that would be the categorical anti-pattern this OBPI's doctrine names. The OBPI-02 validator will mechanically enforce this exemption.)

- [ ] REQ-0.0.59-01-01 [support]: `.gzkit/rules/tests.md` § REQ Scope Discipline added with three-kind taxonomy + proof-channel matrix + tag syntax. Witness: ledger `artifact_edited` event; `gz validate --documents` exit 0.
- [ ] REQ-0.0.59-01-02 [support]: `docs/governance/req-scope-discipline.md` authored as canonical expansion. Witness: ledger `artifact_edited` event; `gz validate --documents` exit 0; `mkdocs build --strict` clean.
- [ ] REQ-0.0.59-01-03 [support]: Scorecard row 59 added; Mechanical count 42→43. Witness: ledger `artifact_edited` event; `gz validate --advisory-scorecard` exit 0.
- [ ] REQ-0.0.59-01-04 [support]: GHI #270 reconciliation note present in tests.md naming output-form fixture tests as BEHAVIOR proofs. Witness: grep confirms text presence; doctrine doc cross-references the reconciliation.
- [ ] REQ-0.0.59-01-05 [support]: Pool ADR carries Disposition section pointing to ADR-0.0.59. Witness: ledger `artifact_edited` event; pool-ADR body preserved unchanged (no Path A/B/C/D edits).
- [ ] REQ-0.0.59-01-06 [support]: GHI #165 closed superseded against ADR-0.0.59. Witness: `gh issue view 165 --json state` returns CLOSED.
- [ ] REQ-0.0.59-01-07 [support]: GHI #531 closed superseded against ADR-0.0.59. Witness: `gh issue view 531 --json state` returns CLOSED.
- [ ] REQ-0.0.59-01-08 [support]: Zero operator PII in authored content. Witness: explicit grep absence check before commit.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR § Decision quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** Structural validator clean; suite regression-free; no new test files (per the doctrine being shipped)
- [ ] **Code Quality:** Lint + typecheck + docs build + unittest sweep clean with ARB receipts
- [ ] **Value Narrative:** Problem-before (REQ→@covers parity machinery applied uniformly to content REQs; tautological filesystem-grep tests accumulate at 32% project-wide / 42% governance ratio) vs capability-now (three-kind taxonomy named in tests.md; canonical doctrine doc lands as encyclopedia entry; pool ADR superseded; GHIs closed; the categorical category error is doctrinally addressed)
- [ ] **Key Proof:** The new `## REQ Scope Discipline` subsection in tests.md + the canonical doctrine doc + the scorecard row + the closed GHIs
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded above

### Gate 2 (TDD)
```text
# Paste validate --documents --advisory-scorecard + arb-step-unittest receipt ID here at completion
```

### Code Quality
```text
# Paste lint + typecheck + mkdocs ARB receipt IDs here at completion
```

### Gate 5 (Human)
```text
# Record operator-verbatim attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added: none (doctrine prohibits @covers tests for SUPPORT-kind REQs)
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked. Will populate during implementation if surfaced._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
