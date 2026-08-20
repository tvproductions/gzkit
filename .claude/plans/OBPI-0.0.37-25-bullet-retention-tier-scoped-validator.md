# Plan: OBPI-0.0.37-25-bullet-retention-tier-scoped-validator — ADR-0.0.33 Bullet-Retention Tier-Scoped Validator

**OBPI:** OBPI-0.0.37-25-bullet-retention-tier-scoped-validator
**ADR:** ADR-0.0.37-constitutional-invariant-composition (Checklist item #25)
**Lane:** Heavy
**Status:** Ready for implementation (B.1, sequence 2 of 3 — reads OBPI-24's advisor-QC receipt)

## Booked decisions (operator, 2026-06-14)

- **Witness granularity: surface-level.** A `tier: compressible` entry passes iff the **surface's
  committed rendition** has a valid advisor-QC receipt (`arb-step-judge-*`, `exit_status == 0`) +
  operator attestation. The validator reads the latest `rendition_advisor_verdict` ledger event for
  the surface to find the receipt id, then validates that receipt. (NOT fragile per-bullet text
  correlation.)
- **No-match fallback: invariant.** When a scorecard bullet maps to no corpus entry (tier unknown),
  treat it as **invariant** (conservative — preserves the Era-1 verbatim contract).

## Context

Flip `gz validate --bullet-retention` from a **whole-surface verbatim grep** to **tier-aware**
enforcement, realizing ADR-0.0.33 § Amendment (2026-06-03):

- **Invariant tier:** verbatim-presence contract unchanged + fail-closed (exit 3 on absent/altered).
- **Compressible tier:** retention satisfied by a present, valid advisor-QC receipt + operator
  attestation for the committed rendition (surface-level witness). A reworded/combined compressible
  entry that carries the witness MUST NOT fail; one without the witness fails closed (exit 3).
  The invariant preserved is *no binding information is lost* (witnessed by receipt + attestation),
  not *every byte identical*.

The validator change lands **in the same commit-window** as the coupled ADR-0.0.33 Invariant-1
amendment, staying wired into `--surface-fidelity` / `gz check` throughout (Anti-Pattern #1).
Editing a Validated foundation invariant's enforcement is a **real attested amendment**, never a
silent validator edit (parent ADR Alternative #18).

## Discovery-grounded facts

- **Seam:** `governance/trust_audits/bullet_retention.py:59` — `normalized_rule not in _normalize(corpus)`
  inside the loop (lines 52–72) that today treats every `_ENFORCED_CLASSES` entry identically.
  `validate_bullet_retention(project_root) -> list[ValidationError]` (line 40). Helpers:
  `_parse_scorecard` (reads `docs/governance/advisory-rules-audit.md`), `_collect_surface_corpus`,
  `_normalize`, `_ENFORCED_CLASSES = frozenset({"mechanical","promotable"})`.
- **Tier source:** `content/models/corpus.py` `CorpusEntry.tier: Literal["invariant","compressible"]`
  (line 45); load via `corpus_store.load_corpus(root, surface)` (entries at `.gzkit/corpus/<surface>.jsonl`).
- **Receipt witness:** reuse `governance/trust_audits/attestation_receipts.py` receipt-loading
  (`_load_receipt` / `_classify_one`, `exit_status == 0`) to validate the surface's advisor-QC receipt.
- **No flag/CLI change:** `--bullet-retention` already registered (`parser_maintenance.py:641`,
  `validate_cmd.py:400`) and wired FIRST into `validate_surface_fidelity` (`trust_audits/__init__.py:142`)
  → stays in `gz check`. Behavior-only change.
- **ADR-0.0.33 mis-cite:** § Amendment lines 118–124 say the flip is *"realized by OBPI-0.0.37-18"* /
  *"attested at OBPI-0.0.37-18's Gate 5"* — both wrong (OBPI-18 was the corpus model; the validator on
  disk is still the Era-1 grep). Correct to **OBPI-0.0.37-25**. Attestation Block ~line 267 (add amendment row).
- **Preserve** existing REQ-0.0.33-01-0{1..5} coverage in `tests/governance/test_bullet_retention.py`
  (tempdir + `@covers` + one-facet-per-class convention).

## Files

### Edits (no files created)

- `src/gzkit/governance/trust_audits/bullet_retention.py` — flip to tier-aware (read corpus tier;
  invariant → verbatim grep unchanged; compressible → surface-level receipt+attestation witness;
  unknown-tier → invariant fallback)
- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
  — correct realizer cite (18 → 25) + record amendment's Gate-5 attestation in the Attestation Block
- `tests/governance/test_bullet_retention.py` — add tier-scoped BEHAVIOR tests; PRESERVE ADR-0.0.33-01 coverage
- `docs/user/manpages/validate.md` — document the tier-scoped `--bullet-retention`
- `data/behave_coverage_waivers.json` — OBPI-level behave waiver (validator-internal; no new verb)
- (brief + parent ADR evidence/checklist as usual)

## Steps (TDD-ordered)

### Step 0 — Brief reconcile + 24-seam check
`uv run gz validate --brief-reconcile`. Confirm OBPI-24 landed (the advisor-QC receipt + the
`rendition_advisor_verdict` event exist); if not, the compressible-branch tests use receipt fixtures.

### Step 1 — Tier-aware validator (REQ-01, REQ-02, REQ-03) — RED→GREEN
Refactor the lines 52–72 loop: for each enforced bullet, resolve its tier via the surface corpus
(unknown → invariant).
- **invariant:** keep `normalized_rule not in _normalize(corpus)` → ValidationError (exit 3).
- **compressible:** look up the surface's latest `rendition_advisor_verdict` event → load + validate
  that receipt (`exit_status == 0`) + confirm operator attestation present. Witnessed → pass; not
  witnessed → ValidationError (exit 3).
Tests (`@covers`, preserve existing classes):
- `test_invariant_absent_fails_closed` (REQ-01).
- `test_compressible_reworded_with_receipt_passes` (REQ-02) — reworded entry + valid receipt+attestation fixture → no error.
- `test_compressible_without_receipt_fails_closed` (REQ-03) — compressible + no valid witness → exit 3.

### Step 2 — Coupled ADR-0.0.33 amendment (REQ-04)
Correct § Amendment realizer cite (OBPI-18 → OBPI-25, two lines: 118 + 122) and add the amendment
attestation row to the Attestation Block (filled at Gate 5 with the receipt ids).

### Step 3 — Stay-wired proof (REQ-05)
Confirm `--bullet-retention` remains first in `validate_surface_fidelity` → `gz validate --surface-fidelity`
exit 0 on coherent canon; participates in `gz check`. (No wiring edit needed; assertion-only.)

### Step 4 — Docs (REQ-06)
`docs/user/manpages/validate.md` tier-scoped `--bullet-retention`; `gz validate --cli-alignment` resolves.

## Verification (canonical, arb-wrapped)

```bash
uv run gz validate --brief-reconcile
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_bullet_retention -v
uv run gz covers OBPI-0.0.37-25-bullet-retention-tier-scoped-validator --json
uv run gz validate --bullet-retention
uv run gz validate --surface-fidelity
uv run gz validate --documents --cli-alignment
uv run mkdocs build --strict
```

## Notes / risks

- **Surface-level witness (booked):** avoids brittle scorecard↔corpus text correlation. The
  validator's new data dependency is `load_corpus(surface)` + the latest `rendition_advisor_verdict`
  ledger event + receipt validation. Confirm the operator-attestation read path at implementation.
- **24 → 25 dependency:** the compressible branch reads OBPI-24's receipt. If 24 attested first
  (sequence intends this), the real wiring is live; else fixtures + brief-reconcile note.
- **Doctrine-drift guard:** the validator edit MUST land with the attested ADR-0.0.33 amendment in the
  same commit-window — never a silent validator change. Preserve the invariant-tier verbatim contract;
  never treat compressible as an unconditional retention escape.
- **Gate 5** is dual-purpose: OBPI-25 completion AND the ADR-0.0.33 amendment attestation point.
