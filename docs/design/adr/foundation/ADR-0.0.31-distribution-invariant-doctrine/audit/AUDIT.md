# AUDIT (Gate-5) — ADR-0.0.31 Distribution Invariant Doctrine

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.0.31-distribution-invariant-doctrine |
| ADR Title | Distribution Invariant (T0 Doctrine) |
| Kind / Lane | foundation / lite |
| ADR Dir | `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/` |
| Audit Date | 2026-05-10 |
| Auditor(s) | Claude Opus 4.7 (agent) + g0 (operator) |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?** A foundation-kind doctrine surface that names the **T0 distribution invariant** — the contract between the wheel's package data and the canonical surfaces an operator receives from `pip install py-gzkit && gz init`. The ADR authors three citable artifacts and the cross-link graph that ties them together. It deliberately ships **no mechanical enforcement** (that is ADR-0.0.32's scope), preserving the proven ADR-0.0.18 (taxonomy doctrine) ↔ ADR-0.0.17 (taxonomy mechanical) split.

The five capabilities below correspond to the five doctrine surfaces named in the ADR's Decision section.

### Capability 1: T0 layer is citable in the trust-doctrine layer table

```bash
$ grep -n "T0" docs/governance/trust-doctrine.md | head -5
63:The doctrine names four trust layers. ... T0 sits upstream of T1: distribution must happen before any layer's canonical claims are valid for external consumers.
67:| **T0** | Distribution | Does the wheel reproducibly deliver every canonical surface to a fresh `gz init`? |
72:T0 is upstream of T1: if a canonical surface only exists in this repo's `.gzkit/` and never ships, then T1 (canon-as-truth) is silently project-specific instead of project-portable. ...
74:### T0 — Distribution Invariant
81:> "a wheel that ships without a canonical surface is a T0 breach, regardless of whether downstream `gz init` reports success" — GHI #318
```

**Why it matters:** Downstream ADRs (notably ADR-0.0.32) and any future canonical-surface promotion now have a single, stable referent for the question *"does this ship?"*. The verbatim failure-mode quote anchored to GHI #318 prevents re-litigation of the premise.

### Capability 2: T0 paragraph names the mechanical-enforcement contract ADR-0.0.32 must satisfy

```bash
$ sed -n '85,93p' docs/governance/trust-doctrine.md
**Mechanical enforcement contract.** The mechanical surface that satisfies T0 — wheel package-data extension, canonical-content-shipping scaffolders, `gz init --update`, and the build-then-install smoke test — is owned by [ADR-0.0.32 (canonical surface packaging)](../design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md). T0 prescribes the contract any enforcement layer MUST satisfy:

1. A T0 audit MUST detect missing package data without depending on downstream installation evidence.
2. A T0 audit MUST distinguish "canonical surface authored but not shipped" (the GHI #318 class) from "canonical surface authored and shipped" (correct state) and from "no canonical surface authored" (out of scope — T0 governs *delivery* of authored canon, not authorship volume).
3. A T0-passing build MUST produce a wheel that, when installed into a fresh venv and run through `gz init`, yields a project whose canonical surfaces are byte-equivalent (modulo project-name substitution) to a frozen baseline manifest.

**See also:** [T0 Failure-Mode Catalog](distribution_invariant_catalog.md) — worked examples (GHI #318 self-hosting blindness; ADR-0.0.21 chores promotion gap) and an "Is this a T0 breach?" decision tree for applying T0 to new canonical surfaces.
```

**Why it matters:** ADR-0.0.32 (mechanical) cites this paragraph as its contract floor. Without these three numbered constraints, the mechanical ADR would have no doctrine to test against — the doctrine/mechanics decoupling would collapse.

### Capability 3: Advisory scorecard registers T0 as Promotable with explicit promotion target

```bash
$ uv run gz validate --advisory-scorecard
Validated: advisory_scorecard
✓ All validations passed (1 scopes).

$ grep -n "T0" docs/governance/advisory-rules-audit.md | head -3
237:### Distribution Invariant Doctrine (T0) (`docs/governance/trust-doctrine.md` T0 layer + `ADR-0.0.31`)
241:| 57 | Every canonical surface ... MUST be reproducibly delivered by `pip install py-gzkit && gz init` ... | **Promotable** | T0 doctrine authored in `docs/governance/trust-doctrine.md` § T0 (OBPI-0.0.31-01) and ADR-0.0.31; mechanical enforcement tracked under ADR-0.0.32-canonical-surface-packaging, pending OBPI-0.0.32-07 (`gz validate --distribution`, ...). When OBPI-0.0.32-07 lands this row flips to **Mechanical**. Receipt-id prefix: `arb-distribution-`. |
```

**Why it matters:** The scorecard self-tests via `gz validate --advisory-scorecard` — every rule under `.gzkit/rules/` and every governance invariant must have a row classifying it Mechanical/Promotable/Judgment/Ambiguous. Row 57 makes T0 visible to the audit and names OBPI-0.0.32-07 as the single tripwire that flips the row to Mechanical when `gz validate --distribution` lands.

### Capability 4: Failure-mode catalog supplies worked examples and a decision tree

```bash
$ grep -n "^## " docs/governance/distribution_invariant_catalog.md
15:## Worked Example #1: GHI #318 — Self-Hosting Blindness
60:## Worked Example #2: The Chores Promotion Gap (ADR-0.0.21)
92:## Is This a T0 Breach?
188:## Related

$ wc -l docs/governance/distribution_invariant_catalog.md
194 docs/governance/distribution_invariant_catalog.md
```

**Why it matters:** Doctrine without worked examples drifts into abstraction. The catalog gives future canonical-surface promotions (a new skill kind, a new rule family, a new hook surface) a concrete decision tree to apply: *"Does it ship in the wheel? Does the scaffolder install it? Is it byte-equivalent? Is the baseline updated?"* — branching to the named recovery action when the answer is No.

### Capability 5: Cross-link graph is closed (ADR ↔ doctrine ↔ catalog ↔ scorecard ↔ ADR-0.0.32)

```bash
$ grep -n "Doctrine source\|ADR-0.0.31" docs/governance/distribution_invariant_catalog.md
91:**Doctrine source:** [ADR-0.0.31 (distribution invariant doctrine)](../design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/ADR-0.0.31-distribution-invariant-doctrine.md).
```

The cross-link graph is closed in both directions:

- ADR-0.0.31 Evidence → `trust-doctrine.md` (forward)
- `trust-doctrine.md` § T0 → ADR-0.0.31 (back) + ADR-0.0.32 (forward, mechanical)
- `trust-doctrine.md` § T0 → `distribution_invariant_catalog.md` (See also)
- `distribution_invariant_catalog.md` → ADR-0.0.31 (Doctrine source)
- `advisory-rules-audit.md` row 57 → ADR-0.0.31 + ADR-0.0.32 + OBPI-0.0.32-07

**Why it matters:** A doctrine surface with one-way links breaks under refactoring. A future agent following any one of {ADR text, doctrine paragraph, scorecard row, catalog file} reaches the others without guessing — that is what makes T0 *citable*, not just *present*.

### Value Summary

Before ADR-0.0.31, "does the wheel ship the canonical content?" was an unnamed question — the gzkit dogfood loop concealed for the entire pre-1.0 cycle that `pip install py-gzkit && gz init` produced an empty greenfield project (GHI #318). After ADR-0.0.31, the question has a name (T0), a doctrine home (`trust-doctrine.md`), a worked-example catalog (`distribution_invariant_catalog.md`), a self-testing scorecard registration (row 57, Promotable), and a forward pointer to the mechanical ADR that will satisfy it (ADR-0.0.32). Every future canonical-surface promotion now has a single citable invariant to satisfy — *"is it T0-compliant?"* — and the failure-mode catalog tells the operator exactly which decision-tree branch they're on.

---

## Execution Log

| # | Check | Command | Result | Notes / Proof |
|---|-------|---------|--------|---------------|
| 1 | Ledger proof (Layer-2 trust) | `uv run gz adr audit-check ADR-0.0.31` | ✓ PASS | All 3 OBPIs completed with evidence. `proofs/audit-check.txt`. Advisory: 14 REQs without `@covers` (non-blocking; doctrine-only ADR has no mechanical surface to cover). |
| 2 | ADR lifecycle pre-state | `uv run gz adr report ADR-0.0.31` | ✓ PASS | Lane=lite, Lifecycle=Completed, Closeout=attested, OBPI 3/3, QC=READY. `proofs/adr-report-pre.txt`. |
| 3 | Trust-doctrine T0 paragraph present | `grep -n "T0" docs/governance/trust-doctrine.md` | ✓ PASS | T0 layer row, dedicated `### T0 — Distribution Invariant` section, verbatim GHI #318 quote, three numbered enforcement constraints. `proofs/t0-trust-doctrine-grep.txt`. |
| 4 | Advisory-scorecard T0 entry | `grep -n "T0" docs/governance/advisory-rules-audit.md` | ✓ PASS | Row 57 classified **Promotable**, cites ADR-0.0.31 + ADR-0.0.32 + OBPI-0.0.32-07; receipt-id prefix `arb-distribution-` reserved. `proofs/scorecard-t0-grep.txt`. |
| 5 | Catalog file authored | filesystem check + heading scan | ✓ PASS | 194 lines; two worked examples (GHI #318, ADR-0.0.21 chores gap); "Is This a T0 Breach?" decision tree at line 92; "Doctrine source" back-link to ADR-0.0.31 at line 91. `proofs/distribution-catalog-head.txt`, `proofs/decision-tree-excerpt.txt`. |
| 6 | Advisory-scorecard self-test | `uv run gz validate --advisory-scorecard` | ✓ PASS | "All validations passed (1 scopes)" — every rule has a scorecard row, T0 included. `proofs/advisory-scorecard-validate.txt`. |
| 7 | Document validity | `uv run gz validate --documents` | ✓ PASS | "All validations passed (1 scopes)" — frontmatter and schema valid for all governance docs. `proofs/validate-documents.txt`. |
| 8 | CLI surface coverage | `uv run gz cli audit` | ✓ PASS | "CLI audit passed. Cross-coverage: 94/94 commands fully covered." `proofs/cli-audit.txt`. |

## Dataset Spot Examples

```text
$ uv run gz adr audit-check ADR-0.0.31
ADR audit-check: ADR-0.0.31-distribution-invariant-doctrine
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.0.31-01-author-t0-doctrine
  - OBPI-0.0.31-02-register-t0-scorecard
  - OBPI-0.0.31-03-t0-failure-mode-catalog
Advisory 14 REQ(s) without @covers traceability (non-blocking): ...
Coverage: 8/22 REQs covered (36.4%)
```

The 8/22 covered REQs all live under `OBPI-0.0.31-03` (the catalog content). OBPI-01 and OBPI-02 author plain-prose doctrine surfaces (`trust-doctrine.md`, `advisory-rules-audit.md`) with no executable mechanical surface to cover with `@covers`-decorated tests. This is structurally identical to ADR-0.0.18 (taxonomy doctrine), the cited architectural precedent — doctrine-only ADRs surface coverage gaps that are out-of-scope by design, not defects.

## Summary Table

| Aspect | Status | Evidence |
|--------|--------|----------|
| Implementation Completeness | ✓ COMPLETE | All 3 OBPIs `attested_completed`; all five doctrine deliverables (layer table, T0 section, enforcement contract, scorecard row, catalog) present and citable. |
| Cross-link Integrity | ✓ COMPLETE | Bidirectional links closed across {ADR, trust-doctrine, catalog, scorecard, ADR-0.0.32}. |
| Doctrine Stability | ✓ STABLE | Verbatim GHI #318 quote in place; mechanical-enforcement contract phrased as three constraints any future enforcement layer must satisfy (ADR-0.0.18-style decoupling). |
| Documentation Alignment | ✓ ALIGNED | `gz validate --documents` and `--advisory-scorecard` both pass; `gz cli audit` 94/94. |
| Mechanical Scope Discipline | ✓ HELD | Zero mechanical changes proposed. Mechanics deferred to ADR-0.0.32 per the cited Decision-section split. |
| Risk Items Resolved | ✓ NONE OUTSTANDING | Coverage advisory understood and documented; no shortfalls. |

## Evidence Index

All proof logs co-located under `audit/proofs/`:

- `audit/proofs/audit-check.txt` — Layer-2 ledger proof (3 OBPIs PASS)
- `audit/proofs/adr-report-pre.txt` — pre-validation ADR report (Lifecycle=Completed)
- `audit/proofs/t0-trust-doctrine-grep.txt` — T0 references in `trust-doctrine.md`
- `audit/proofs/back-link-grep.txt` — ADR-0.0.31 back-link from catalog (line 91)
- `audit/proofs/distribution-catalog-head.txt` — catalog file head
- `audit/proofs/decision-tree-excerpt.txt` — "Is This a T0 Breach?" decision tree
- `audit/proofs/scorecard-t0-grep.txt` — scorecard row 57 (Promotable)
- `audit/proofs/advisory-scorecard-validate.txt` — `gz validate --advisory-scorecard` PASS
- `audit/proofs/validate-documents.txt` — `gz validate --documents` PASS
- `audit/proofs/cli-audit.txt` — `gz cli audit` 94/94
- `audit/proofs/adr-report-post.txt` — post-validation ADR report (Lifecycle=Validated, Closeout=READY, QC=READY)

## Recommendations

- **No blocking issues found.** All five doctrine deliverables are present, citable, and self-consistent. The cross-link graph is closed. Layer-3 self-tests (`gz validate --advisory-scorecard`, `--documents`) pass. CLI surface coverage is 94/94.
- **Coverage advisory is by-design, not a shortfall.** OBPI-01 and OBPI-02 author plain-prose doctrine surfaces; the absence of `@covers`-decorated tests for their REQs reflects that there is no mechanical surface to cover. This mirrors the ADR-0.0.18 (taxonomy doctrine) precedent the ADR explicitly cites. No action required; mechanical enforcement and its REQ→test coverage are owned by ADR-0.0.32 (OBPI-0.0.32-07, `gz validate --distribution`).
- **Forward-pointer hygiene confirmed.** Scorecard row 57 names OBPI-0.0.32-07 explicitly as the tripwire that flips the row from Promotable to Mechanical. When that OBPI lands, this audit's "no outstanding risk items" claim retroactively gains a mechanical backstop.

## Attestation

I/we attest that ADR-0.0.31-distribution-invariant-doctrine is implemented as intended, evidence is reproducible, and no blocking discrepancies remain. The five doctrine deliverables (layer table, T0 paragraph + enforcement-contract clauses, scorecard row 57, failure-mode catalog with worked examples and decision tree, closed cross-link graph) are present and citable. Mechanical enforcement is correctly deferred to ADR-0.0.32 per the ADR-0.0.18 ↔ ADR-0.0.17 architectural precedent.

Signed: g0 — 2026-05-10 (operator verbal `accept audit` / `verify audit` ack relayed via `gz adr emit-receipt --event validated --attestor-present`).
Agent witness: Claude Opus 4.7 (agent-relayed-operator-attestation branch, GHI #292).

## Agent Attestation Block (Step 8 ceremony close)

- **Operator verbatim ack:** `accept audit`
- **Agent enrichment (canon pattern):** `accept audit — ADR-0.0.31 distribution-invariant-doctrine validated; 3/3 OBPIs attested_completed; five doctrine deliverables verified (T0 layer in trust-doctrine.md, T0 paragraph with GHI #318 quote, scorecard row 57 Promotable, distribution_invariant_catalog.md 194 lines, closed cross-link graph); gz validate --advisory-scorecard PASS [arb-step-advisoryscorecard-9dfc77711fec4705a39876f16c1b52e6], gz validate --documents PASS [arb-step-documents-bee17fe8d665483da54b7e33d5eb493a], gz cli audit 94/94 [arb-step-cliaudit-c5b28fa378ec405fbae1c2b40ffdb73e]; no shortfalls; mechanical scope correctly deferred to ADR-0.0.32`
- **Receipt event:** `audit_receipt_emitted` for ADR-0.0.31-distribution-invariant-doctrine, event=`validated`, ts=`2026-05-10T14:54:44.784552+00:00`, anchor commit=`971db9a`, semver=`0.0.31` (last entry in `.gzkit/ledger.jsonl`).
- **Cited ARB receipts (canonical regex compliant):**
  - `arb-step-advisoryscorecard-9dfc77711fec4705a39876f16c1b52e6` (`gz validate --advisory-scorecard` PASS)
  - `arb-step-documents-bee17fe8d665483da54b7e33d5eb493a` (`gz validate --documents` PASS)
  - `arb-step-cliaudit-c5b28fa378ec405fbae1c2b40ffdb73e` (`gz cli audit` 94/94)
- **Lifecycle confirmation (Step 9):** `uv run gz adr report ADR-0.0.31` reports `Lifecycle=Validated`, `Closeout Phase=validated`, `Closeout=READY`, `QC=READY`, OBPI 3/3 `attested_completed`. Captured in `audit/proofs/adr-report-post.txt`.
- **Co-presence marker:** `.claude/plans/.pipeline-active-ADR-0.0.31-distribution-invariant-doctrine.json` removed by `gz adr audit-end ADR-0.0.31` at ceremony close.
- **Agent witness:** Claude Opus 4.7 (1M context), agent-relayed-operator-attestation branch (GHI #292), Step 8 ceremony close per `gz-adr-audit` skill.
