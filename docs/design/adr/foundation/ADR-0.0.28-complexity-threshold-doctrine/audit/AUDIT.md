# Audit: ADR-0.0.28-complexity-threshold-doctrine

- ADR: `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md`
- Generated: 2026-05-05
- Feature-Demonstration augmentation: 2026-05-06 (post-validation; closes Step 3 gap of `gz-adr-audit` skill)

## Attestation Record
- Attestor: Jeffry Babb (verbatim ack `attest completed` on 2026-05-06T01:18:01+00:00)
- Status: validated (lifecycle Completed → Validated)
- Receipt: `audit_receipt_emitted` event=`validated`, anchor commit `fbc9d22`
- Bound ARB receipts (meta-receipt-bind):
  - `arb-ruff-1ffb15a1eb614d078b345518c423f0ed`
  - `arb-step-typecheck-184d9e60c7be49d9ba88260f5f2026ee`
  - `arb-step-unittest-a7295197d4bd43249402cd2da1e47b09`
  - `arb-step-mkdocs-c8297a10696b4df1a219acf13248b96c`
  - `arb-step-behave-fe27f62b3524481cab166270a7492ee4`

## Feature Demonstration

The ADR delivers a three-surface mirror of ADR-0.0.27's exemplar shape
(rule + loader + validator), seating the canonical complexity threshold
table as foundation doctrine. Three capabilities, each demonstrated below
against the live product surface — what the operator and downstream ADRs
(0.0.29 advisor, 0.0.30 authoring-guidance) can do that they could not
before this ADR landed.

### Capability 1 — Canonical threshold rule file at `.gzkit/rules/`

**What it delivers:** twelve canonical metrics × three bands (`advise` /
`warn` / `block`) = 36 rows, each carrying the percentile + absolute-number
pairing per OBPI-0.0.27-05's citation contract, anchored to
`docs/governance/complexity/distilled-characteristics-2026-05-04.md` at
`corpus_revision: 1`. Doctrine, not data — mirrored by
`gz agent sync control-surfaces` so agents pattern-match against the
canonical surface, not training memory.

```bash
ls -la .gzkit/rules/complexity-thresholds.md \
       .claude/rules/complexity-thresholds.md \
       .github/instructions/complexity_thresholds.instructions.md
```

Representative output (full proof: `audit/proofs/feature-demo-rule-file.txt`):

```
-rw-r--r-- .gzkit/rules/complexity-thresholds.md  (17 763 B, rule-version 0.1.0)
-rw-r--r-- .claude/rules/complexity-thresholds.md (17 603 B, mirror)
-rw-r--r-- .github/instructions/complexity_thresholds.instructions.md (17 586 B, mirror)
```

**Why this matters:** before ADR-0.0.28, threshold values would have
proliferated across xenon flags, advisor rule tables, authoring-guidance
prose, and the existing complexity-reduction-xenon chore — each drifting
independently every refresh. The single canonical home + vendor-mirror
surface is the structural defense against that drift class. Bootstrap
carve-outs for `radon_mi`, `lizard_nesting_depth`, `cohesion_lcom4` are
declared on-surface (with GHI #404 / GHI #405 follow-up references) — a
transparent doctrine waiver, not a silent skip.

### Capability 2 — Frozen `ThresholdTable` Pydantic runtime contract

**What it delivers:** `src/gzkit/complexity/thresholds.py` exposes a
`ThresholdTable` (frozen, `extra='forbid'`) populated by
`load_threshold_table(rule_path)`, with `band_for(metric, value)` returning
the highest-severity band the value crosses and `bands_for_metric(metric)`
enumerating the per-metric ladder. ADR-0.0.29 and ADR-0.0.30 bind against
this Pydantic surface, not the rule file directly.

```bash
uv run python -c "
from pathlib import Path
from gzkit.complexity.thresholds import load_threshold_table
table = load_threshold_table(Path('.gzkit/rules/complexity-thresholds.md'))
print(f'{len(table.bands)} bands across {len({b.metric for b in table.bands})} metrics')
for b in table.bands_for_metric('radon_cc'):
    print(f'  p{b.corpus_percentile} -> CC={b.absolute_number} -> {b.trigger_semantic}')
print(table.band_for('radon_cc', 20.0))
"
```

Representative output (full proof: `audit/proofs/feature-demo-loader.txt`):

```
36 bands across 12 metrics
  p75 -> CC=4.0  -> advise
  p90 -> CC=7.0  -> warn
  p95 -> CC=11.0 -> block
band_for(radon_cc, 20) -> trigger=block, percentile=p95, absolute=11.0
band_for(radon_cc,  4) -> trigger=advise
ThresholdTable.frozen=True, extra='forbid'
Mandatory block band confirmed for all 12 canonical metrics.
```

**Why this matters:** downstream ADRs receive a frozen typed contract,
not a JSON blob each re-parses. Single parser closes the
parser-divergence drift class named in ADR § Positive #7. The
`extra='forbid'` posture means a stray YAML key in the rule file
fail-closes at load time rather than silently widening the contract.

### Capability 3 — `gz validate --complexity-thresholds` gate

**What it delivers:** a fail-closed validator wired into `gz validate
--all` and `gz check`. Closes on missing `block` band per metric, missing
percentile + absolute pairing, trigger-semantic outside the
`{block,warn,advise}` enum, or an unparseable citation tuple.

```bash
uv run gz validate --complexity-thresholds
```

Representative output (full proof: `audit/proofs/feature-demo-validator.txt`):

```
Bootstrap-mode: .gzkit/rules/complexity-thresholds.md declares a Bootstrap
absolutes carve-out section; portability checks against bootstrap rows are
skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is
informational, not a policy breach — review tracked GHIs (#404 parser
zeros, #405 polarity-aware model) for resolution.
Validated: complexity_thresholds
✓ All validations passed (1 scopes).
```

**Why this matters:** threshold drift now surfaces at `gz check` time —
pre-commit and pre-merge — not at midnight when the operator is debugging
an advisor diagnosis. The validator is the gate that closes the
"validator drift" failure class (rule lives in the codebase but never
fires); integration into the `gz check` pipeline is the structural
guarantee. Bootstrap-mode notices reference open GHIs by number, so
the doctrine waiver is itself witness-able and trackable.

### Capability summary

| # | Capability | Surface | Failure class closed |
|---|------------|---------|----------------------|
| 1 | Canonical threshold rule file | `.gzkit/rules/complexity-thresholds.md` (+ mirrors) | Threshold drift across xenon / advisor / authoring-guidance / chore |
| 2 | Frozen `ThresholdTable` runtime contract | `src/gzkit/complexity/thresholds.py` | Parser divergence between downstream consumers |
| 3 | `gz validate --complexity-thresholds` gate | `gz validate --all` + `gz check` integration | Validator-drift (rule exists but never fires) |

Capabilities 2 and 3 unblock ADR-0.0.29 (complexity advisor) and ADR-0.0.30
(authoring-time guidance); without ADR-0.0.28's frozen contract those ADRs
would each carry their own threshold values and re-introduce the drift
class this cluster exists to close.

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `eval-delta` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 3 | pass | `skill-audit` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `eval-delta` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 3 | pass | `skill-audit` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.0.28-01-threshold-rule-file | completed | Yes |
| OBPI-0.0.28-02-threshold-loader | completed | Yes |
| OBPI-0.0.28-03-threshold-validator | completed | Yes |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/audit/proofs/docs.txt`

## Evidence Links
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-01-threshold-rule-file.md`
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-02-threshold-loader.md`
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-03-threshold-validator.md`
