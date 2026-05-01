# Plan — OBPI-0.26.0-05: Ledger Schema comparison and decision

- **OBPI:** OBPI-0.26.0-05-ledger-schema
- **Parent ADR:** ADR-0.26.0-governance-library-module-absorption (Heavy)
- **Brief:** `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md`
- **Sibling precedent:** OBPI-0.26.0-04-adr-governance (Decision: Confirm
  by reference to OBPI-0.25.0-20), OBPI-0.26.0-03-adr-recon (Completed),
  OBPI-0.26.0-02-references (Decision: Exclude), OBPI-0.26.0-01-adr-management
  (Completed)
- **Canonical precedent for this source module:** OBPI-0.25.0-29-ledger-schema-pattern
  (`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md`),
  attested 2026-04-13, **Decision: Exclude** with five-point rationale
  anchored on architectural-scope mismatch, superset functionality,
  storage-doctrine conflict, no-narrow-idiom, and tooling-vs-consumer
  distinction.
- **ADR execution warning:** OBPI-0.26.0-01..05 are decision units first.
  If comparison shows Absorb requires substantial implementation, split the
  Absorb path into a follow-on execution unit (OBPI or GHI) rather than
  bundling it here. For an Exclude outcome (the structurally indicated
  landing), no implementation follows.

## Context

The opsdev module `../airlineops/src/opsdev/lib/ledger_schema.py` (501
lines) is an audit-only Pydantic schema for per-ADR
`docs/design/adr/.../logs/obpi-audit.jsonl` files. It defines four entry
types — `obpi-audit`, `covers-map`, `coverage-run`, `reconciliation` —
under schema version `govzero.ledger.v1`, plus a flat `EvidencePayload`
(`extra="allow"`), ID pattern validators (`OBPI_ID_PATTERN`,
`ADR_ID_PATTERN`), legacy entry handling (`_infer_entry_type`), and a
small set of validator helpers (`validate_ledger_entry`,
`is_valid_ledger_entry`, `parse_ledger_entry`, `create_timestamp`). It is
schema-only — no persistence class, no derivation pipeline.

The brief frames gzkit's equivalent as "Partial in `src/gzkit/ledger.py`,"
but `ledger.py` is only one of three artifacts in gzkit's ledger surface.
The actual gzkit comparison target is the triad:

- `src/gzkit/events.py` (556 lines) — typed ledger event models with
  Pydantic discriminated unions. 17+ lifecycle event classes
  (`project_init`, `prd_created`, `constitution_created`, `obpi_created`,
  `adr_created`, `artifact_edited`, `attested`, `gate_checked`,
  `closeout_initiated`, `audit_receipt_emitted`, `obpi_receipt_emitted`,
  `artifact_renamed`, `adr_annotated`, `lifecycle_transition`,
  `task_started`, `task_completed`, `task_blocked`, `task_escalated`),
  resolved via `TypeAdapter` over `TypedLedgerEvent`. Nested evidence
  models (`ReqProofInput`, `ScopeAudit`, `GitSyncState`,
  `ObpiReceiptEvidence`) carry cross-field validation.
- `src/gzkit/ledger.py` (728 lines) — `Ledger` persistence class with
  `append`, `read_all`, `query`, `latest_event`, `canonicalize_id`,
  `get_latest_gate_statuses`, `get_artifact_graph`,
  `get_pending_attestations`, rename-chain resolution, and cache
  invalidation. Schema version `gzkit.ledger.v1`.
- `src/gzkit/schemas/ledger.json` (318 lines) — per-event JSON Schema
  consumed by CLI-side validation.

Total gzkit surface: ~1602 lines vs opsdev's 501 lines. The gzkit surface
is a functional superset for the gzkit problem (lifecycle event stream,
central `.gzkit/ledger.jsonl`), and opsdev's per-ADR `obpi-audit.jsonl`
storage layout collides with gzkit's Architectural Boundary 6 ("derived
views never silently become source-of-truth").

The OBPI is therefore a comparison + decision unit per the ADR's stated
frame. Three outcomes are nominally available (Absorb / Confirm / Exclude),
and the canonical precedent OBPI-0.25.0-29-ledger-schema-pattern landed
**Exclude** on the same source artifact three weeks ago. Re-running the
comparison with a divergent rationale on identical source material would
itself be a doctrine-drift signal — Exclude-by-reference is the
structurally correct landing.

### Duplicate-OBPI surface (mirror of GHI #376)

This brief is the **second** OBPI evaluating `lib/ledger_schema.py`
across two parent ADRs. The defect is structurally identical to the one
already tracked under **GHI #376** ("Duplicate-OBPI evaluation:
`lib/adr_governance.py` absorbed twice across ADR-0.25.0 and ADR-0.26.0"),
where OBPI-0.26.0-04 mirrored OBPI-0.25.0-20 on the same source artifact.
The same root cause applies: the ADR-0.26.0 authoring did not check
whether ADR-0.25.0's Phase-2 absorption sweep had already covered each
module in scope. The same proposed mechanical guard (`gz validate
--absorption-duplicates`, enumerated in GHI #376's "Tracking impact"
section) would catch both instances.

Resolution: extend GHI #376 with this `lib/ledger_schema.py` second
instance via a `gh issue comment 376` rather than file a parallel GHI.
Root cause and mitigation are identical; tracking surface unification
keeps the closeout audit footprint single.

## Files

- **Read (audit, no edits):**
  - `../airlineops/src/opsdev/lib/ledger_schema.py` (501 lines) — opsdev
    source under review (re-confirm structure, do not re-read end-to-end
    if precedent is fresh).
  - `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md`
    — canonical precedent attested 2026-04-13.
  - `src/gzkit/events.py` (556 lines) — gzkit typed event models
    (verify line ranges still match precedent's anchors:
    `events.py:286-463` event classes, `events.py:443-465` TypeAdapter,
    `events.py:45-205` nested evidence models).
  - `src/gzkit/ledger.py` (728 lines) — gzkit `Ledger` persistence class
    (verify `ledger.py:165-180` append; precedent cited
    `ledger.py:133-565`, but file has grown).
  - `src/gzkit/schemas/ledger.json` (318 lines) — per-event JSON Schema.
  - `src/gzkit/core/models.py` — Pydantic `Field(..., pattern=...)` ID
    enforcement (precedent cited `core/models.py:37,140`).
  - `tests/` — confirm no canonical witness file exists for the Exclude
    decision (Exclude outcomes typically introduce no code or tests; the
    OBPI-0.25.0-29 brief itself stated Gate 2 N/A).
- **Edit (brief only on Exclude/Confirm path):**
  - `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md`
- **Edit (Absorb path only — ADR warning says split into follow-on unit):**
  - `src/gzkit/` — adapted module (deferred; not anticipated)
  - `tests/` — coverage (deferred; not anticipated)

All edits stay inside the brief's Allowed Paths
(`src/gzkit/`, `tests/`, this ADR directory). No `pyproject.toml` edits,
no CI files, no opsdev edits (one-way absorption only), no
cross-brief boundary crossings.

## Steps

1. **Stage 1 lock + markers.** Claim the OBPI lock; the per-OBPI pipeline
   marker is written by `gz obpi pipeline` itself when this skill enters
   Stage 2.

   ```bash
   uv run gz obpi lock claim OBPI-0.26.0-05-ledger-schema
   ```

2. **Stage 1→2 Confidence Gate.** Self-report confidence after reading
   the brief, the canonical precedent (OBPI-0.25.0-29), and confirming
   the gzkit surface lines still align. Initial confidence is **~92%**:
   - Procedure mirrors OBPI-0.26.0-04 (Confirm-by-reference) exactly,
     adjusted for Exclude verdict.
   - Source artifact unchanged (501 L `lib/ledger_schema.py`); gzkit
     triad unchanged in shape, slightly grown in size.
   - The canonical precedent is recent (three weeks) and explicitly
     attested under Heavy lane.
   - Only the source-material wording in the brief header (`Partial in
     src/gzkit/ledger.py`) is not perfectly aligned with the actual
     comparison surface — same observation pattern as OBPI-0.26.0-04.
   - At ≥90% confidence, the `gz justify` walkthrough is not required.
     If any read in Step 4 surfaces a material divergence from the
     precedent, drop confidence and run
     `uv run -m gzkit justify OBPI-0.26.0-05-ledger-schema --save`
     before composing the comparison.

3. **Re-confirm opsdev source structure.** Spot-check
   `../airlineops/src/opsdev/lib/ledger_schema.py` for the four entry
   classes (`ObpiAuditEntry`, `CoversMapEntry`, `CoverageRunEntry`,
   `ReconciliationEntry`) and `EvidencePayload`/`govzero.ledger.v1`
   anchors named in the precedent. Confirmed at lines 98, 154, 235, 264,
   286 in initial Stage-1 verification — no further read required unless
   the spot-check surfaces a structural change.

4. **Re-confirm gzkit surface anchors.** For each line range cited in
   the OBPI-0.25.0-29 precedent, verify the anchor still resolves:
   - `events.py:286-463` event class definitions (file is now 556 L —
     re-anchor if needed)
   - `events.py:443-465` `TypeAdapter` over `TypedLedgerEvent`
   - `events.py:45-205` nested evidence models
   - `events.py:213-470` `parse_typed_event` and helpers
   - `ledger.py:133-565` `Ledger` class (file is now 728 L — re-anchor
     to current line range)
   - `ledger.py:165-180` `Ledger.append`
   - `core/models.py:37,140` Pydantic `Field(..., pattern=...)` ID
     enforcement
   Record any anchor drift in the brief's Comparison section as a
   "precedent anchor refresh" note — the underlying capability is
   unchanged, only line numbers shift.

5. **Confirm or correct the brief's "Partial in `src/gzkit/ledger.py`"
   header.** ledger.py (728 lines) is the persistence class only; the
   schema definitions live in events.py and schemas/ledger.json. Record
   this observation in the brief body (Comparison section), do **not**
   amend the parent-ADR-authored Source Material header — same
   observation pattern as OBPI-0.26.0-04 (mirror canonical surface).

6. **Build dimension-by-dimension comparison table** in the brief
   mirroring the OBPI-0.25.0-29 twelve-dimension table. Re-anchor cited
   line ranges to the current files; do not invent new dimensions or
   omit any from the precedent (verbatim re-use is the correct shape
   when source artifact and gzkit surface are unchanged in capability).
   Each cell must cite concrete line ranges or `tests/` paths — no vague
   adjectives. Add a one-line note pointing at OBPI-0.25.0-29 as the
   canonical anchor.

7. **Record final decision: Exclude (by reference to OBPI-0.25.0-29).**
   The five-point rationale from OBPI-0.25.0-29 is reproduced verbatim
   (with refreshed line anchors where they have shifted) because the
   architectural shape, capability gap, and doctrine collision are
   identical:
   1. Architectural scope mismatch (per-ADR audit-only schema vs
      lifecycle-wide event stream).
   2. Superset functionality (17+ event classes vs 4 audit types;
      richer nested evidence models; `Ledger` persistence class
      airlineops lacks entirely).
   3. Storage doctrine conflict (`CLAUDE.md` § Architectural Boundaries
      item 6 prohibits derived per-ADR storage from becoming
      source-of-truth).
   4. No narrow idiom warranting standalone absorption (`ConfigDict
      (frozen=True)` discipline is a minor convention difference;
      `extra="forbid"` plus append-only writes give gzkit equivalent
      practical immutability without migration cost; `create_timestamp`
      is one inlined helper).
   5. Tooling-layer vs consumer-layer distinction (gzkit is governance
      tooling; airlineops's per-ADR `obpi-audit.jsonl` storage layout
      is a consumer-layer architectural choice a toolkit should not
      mandate).

   Pre-mortem hypothesis (do not pre-decide): the structurally
   indicated landing is **Exclude** with the five-point rationale
   above plus a sixth point recording the duplicate-OBPI surface
   tracked under GHI #376. Step 6's dimension table must drive the
   decision, not this hypothesis — if any dimension surfaces a
   material capability gap that did not exist three weeks ago,
   re-evaluate.

8. **Update brief with REQ-01..REQ-05 evidence.** Each acceptance
   criterion gets a concrete observation:
   - REQ-01: brief frontmatter records `decision: Exclude`; brief body
     records the decision in `## Decision`
   - REQ-02: rationale cites concrete capability/robustness/ergonomics
     differences with line anchors (the dimension table from Step 6)
   - REQ-03: Absorb path only — N/A (Exclude outcome, vacuous pass)
   - REQ-04: Exclude path — five-point rationale plus duplicate-OBPI
     observation explains why no upstream absorption is warranted
   - REQ-05: Gate 4 N/A rationale (no operator-visible behavior change
     for an Exclude decision-only brief)

9. **Heading sweep.** Verify brief evidence sections will use H3
   (`### Implementation Summary`, `### Key Proof`, `### Closing
   Argument`) per `.claude/rules/brief-heading-conventions.md`. The
   current brief has only `### Closing Argument` placeholder; the H3
   `### Implementation Summary` and `### Key Proof` will be added at
   Stage 5 via `gz obpi complete --implementation-summary` and
   `--key-proof`.

10. **Stage 3 verification (Phase 1 baseline + Phase 1b parity gate).**

    ```bash
    uv run gz arb ruff
    uv run gz arb typecheck
    uv run gz arb step --name unittest -- uv run gz test --obpi OBPI-0.26.0-05-ledger-schema
    uv run gz covers OBPI-0.26.0-05-ledger-schema --json
    uv run gz validate --documents --surfaces --brief-headings
    ```

    Heavy lane addition (only meaningful if brief edits affect mkdocs
    build):

    ```bash
    uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
    ```

    Phase 1b: REQs are `[doc]`-tagged in the brief, so `gz covers`
    parity routes through `_synthesize_doc_proof_linkage` for vacuous
    pass (`uncovered_reqs: 0`). No `@covers` decorator additions
    needed — same pattern as OBPI-0.26.0-04 closure.

11. **Stage 4 ceremony.** Render the canonical Stage 4 template — Value
    Narrative (before/after), Key Proof (one concrete command + output),
    Evidence table with ARB receipt IDs, REQ coverage table with
    `@covers` location showing `[doc]` route via brief content, files
    modified (the brief itself only). Wait for human attestation
    (Heavy lane).

12. **Stage 5 sync.**

    ```bash
    # Pre-flight checklist (mandatory)
    uv run gz obpi precomplete OBPI-0.26.0-05-ledger-schema

    # Closure narrative preview to operator (this skill's Step 1
    # gate — present Implementation Summary + Key Proof prose inline
    # before invoking gz obpi complete).

    # Atomic completion (with --attestor-present per GHI #292; the
    # pipeline marker written by Stage 1 satisfies the co-presence
    # proxy)
    uv run gz obpi complete OBPI-0.26.0-05-ledger-schema \
      --attestor 'g0' \
      --attestation-text "$(cat /tmp/obpi-attestation.txt)" \
      --implementation-summary "$(cat /tmp/obpi-summary.md)" \
      --key-proof "$(cat /tmp/obpi-keyproof.md)" \
      --attestor-present

    uv run gz obpi lock release OBPI-0.26.0-05-ledger-schema
    rm -f .claude/plans/.pipeline-active-OBPI-0.26.0-05.json
    rm -f .claude/plans/.pipeline-active.json   # only if it points to this OBPI

    # Git-sync #1 — commits brief edits + lock release + marker cleanup
    uv run gz git-sync --apply

    # Reconcile + ADR status refresh
    uv run gz obpi reconcile OBPI-0.26.0-05-ledger-schema
    uv run gz adr status ADR-0.26.0 --json > /dev/null

    # Git-sync #2 — commits reconcile output + ADR status refresh
    uv run gz git-sync --apply
    ```

13. **Extend GHI #376 with the second instance.** After git-sync #2 is
    clean, append a comment to GHI #376 enumerating
    `lib/ledger_schema.py` as a second occurrence of the same defect
    (OBPI-0.25.0-29 attested 2026-04-13 vs OBPI-0.26.0-05 in-flight,
    same source artifact, structurally identical resolution
    Exclude-by-reference). Do **not** file a parallel GHI; the root
    cause and proposed mechanical guard are identical, and tracking
    unification keeps the ADR-0.26.0 closeout-audit footprint single.

    ```bash
    gh issue comment 376 --body "$(cat /tmp/ghi-376-second-instance.md)"
    ```

## Verification

Brief-specific verification commands (also embedded in the brief
itself):

```bash
test -f ../airlineops/src/opsdev/lib/ledger_schema.py
# Expected: opsdev source under review exists

test -f src/gzkit/ledger.py
# Expected: gzkit comparison target exists (brief-stated; actual
# comparison is the events.py + ledger.py + schemas/ledger.json triad,
# captured in the brief body).

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-05-ledger-schema
# Expected: comparison or absorbed implementation remains green
# (vacuous pass when no @covers tests target this OBPI — the [doc]
# REQ pattern routes to brief-content proof via
# _synthesize_doc_proof_linkage; covered by gz covers parity gate)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

Lane-required heavy commands:

```bash
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
# Heavy lane: docs build clean (only meaningful if brief edits affect mkdocs build)

# uv run -m behave features/heavy_lane_gate4.feature
# Only required when operator-visible behavior changes; record N/A otherwise.
```

## Notes

- **Decision-unit framing.** Per the ADR execution warning, this brief
  is a decision unit. Exclude-by-reference outcome means the scope of
  THIS brief is the decision artifact only; no follow-on absorption is
  warranted.
- **Brief comparison-target correction (Step 5).** The brief names
  `src/gzkit/ledger.py` as the comparison target, but ledger.py is the
  persistence-class surface. Schema definitions live in events.py
  (typed event classes, nested evidence models) and schemas/ledger.json
  (per-event JSON Schema). Record this observation in the brief body
  (Comparison section); do not edit the brief's Source Material header
  — that is parent-ADR-authored framing, same as OBPI-0.26.0-04.
- **Exclude-by-reference (not Confirm).** Unlike OBPI-0.26.0-04 which
  landed Confirm by reference to OBPI-0.25.0-20 (gzkit functional
  superset across all subcommands), this brief lands **Exclude** by
  reference to OBPI-0.25.0-29 because the storage-doctrine conflict and
  tooling-vs-consumer distinction are decisive — gzkit is a functional
  superset *and* the airlineops storage layout would actively collide
  with gzkit's Architectural Boundary 6.
- **No new dependencies, no new code.** opsdev `ledger_schema.py`
  imports only stdlib + Pydantic — gzkit already has Pydantic. But the
  Exclude decision means no absorption of the module itself, so no
  dependency surface changes.
- **Duplicate-OBPI surface (GHI #376).** This brief is the second
  instance of the same defect already tracked under GHI #376 (which
  named `lib/adr_governance.py` as the first instance). Resolution:
  extend GHI #376 with this `lib/ledger_schema.py` instance via
  `gh issue comment`; do not file a parallel GHI. The proposed
  mechanical guard `gz validate --absorption-duplicates` already
  enumerated in GHI #376 would catch both instances — same root cause,
  same mitigation.
- **PII rule.** Operator name only in attestor field (`g0`);
  no personal email anywhere in brief, ledger, attestation text, or
  commits.
- **Pre-mortem (operator-economy framing).** The most likely failure
  mode is reading the precedent OBPI-0.25.0-29 brief once and copying
  its dimension table verbatim without re-anchoring the gzkit line
  ranges (events.py was 470 L → now 556 L; ledger.py was 598 L → now
  728 L). Mitigation: Step 4 explicitly walks the cited anchors and
  records refresh deltas in the brief Comparison section. Capability
  is unchanged; only line numbers shift.
- **Skill-sync hygiene check.** No skill or rule edits anticipated for
  this brief. If any are made, bump the version marker per
  `.claude/rules/skill-surface-sync.md` and run
  `uv run gz agent sync control-surfaces`. For an Exclude brief, this
  is unlikely to fire.
