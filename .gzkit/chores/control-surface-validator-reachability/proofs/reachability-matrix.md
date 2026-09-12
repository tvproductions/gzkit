# Reachability matrix

Observed 2026-09-12T17:15:06.103568+00:00 against working tree at HEAD 464dd4ff8fa2ee12d98afe99a867280e1b82b431.

Instrument: `check_reachability.py --report`; full rows from its `build_matrix` function.

```text
runnable scopes: 98
  A gated       47
  B test-only   27
  C doc-only    23
  D orphan       1
ungated (B+C+D): 51
orphans (delete candidates): --doc-surface-parity
EXIT=0
```

| Scope | Instrument tier |
|---|---|
| `--absorption-duplicates` | C |
| `--adr-status-fresh` | A |
| `--adversarial-validation` | A |
| `--advisor-proof-binding` | C |
| `--advisory-scorecard` | A |
| `--agents-md-map-conformance` | A |
| `--allowlist-only` | C |
| `--audits` | B |
| `--authorship` | A |
| `--behave-req-tags` | B |
| `--brief-command-shape` | B |
| `--brief-cross-references` | C |
| `--brief-demo-section` | C |
| `--brief-headings` | C |
| `--brief-reconcile` | B |
| `--brief-structure` | A |
| `--briefs` | C |
| `--bullet-retention` | A |
| `--changelog` | C |
| `--chores-layout` | B |
| `--class-size` | C |
| `--cli-alignment` | B |
| `--closeout-proof` | A |
| `--commit-trailers` | B |
| `--complexity-doctrine-links` | A |
| `--complexity-thresholds` | A |
| `--config-registry` | A |
| `--corpus-retirement-witness` | A |
| `--decomposition` | C |
| `--deprecated-verb-prescription` | B |
| `--distribution` | B |
| `--doc-surface-parity` | D |
| `--documents` | B |
| `--evaluation-justify-binding` | B |
| `--event-handlers` | B |
| `--event-schemas` | B |
| `--exemption-controls` | A |
| `--fidelity-presence` | A |
| `--frontmatter` | B |
| `--gate-callers` | A |
| `--insights-shape` | A |
| `--instructions` | C |
| `--instructions-files-budget` | A |
| `--interviews` | A |
| `--intrinsic-attestation` | C |
| `--invariant-coherence` | A |
| `--invariant-witness` | B |
| `--kind-invariance` | A |
| `--ledger` | B |
| `--line-endings` | A |
| `--lock-exchange-coupling` | A |
| `--manifest` | C |
| `--obpi-lifecycle-coherence` | A |
| `--okf-conformance` | B |
| `--ontology-purity` | C |
| `--orientation-freshness` | A |
| `--orphaned-implementation` | C |
| `--persona-witness` | A |
| `--personas` | C |
| `--pointer-anchors` | A |
| `--pool-adr-isolation` | C |
| `--pool-interview` | A |
| `--producer-fields` | A |
| `--pydantic-models` | C |
| `--python-version-pins` | A |
| `--qc-binding` | A |
| `--receipt-shape` | A |
| `--reconcile-freshness` | C |
| `--red-parity` | A |
| `--rendition-floor-coherence` | A |
| `--rendition-freshness` | A |
| `--rendition-lineage` | A |
| `--req-kind-discipline` | A |
| `--requirements` | C |
| `--router-tables` | B |
| `--rule-version-markers` | B |
| `--sensitivity` | B |
| `--session-green-gate` | A |
| `--setpoint-coherence` | B |
| `--skill-alignment` | C |
| `--status-writer-coverage` | A |
| `--surface-fidelity` | A |
| `--surface-weight` | A |
| `--surfaces` | B |
| `--task-envelope-coherence` | A |
| `--tautological-test-audit` | A |
| `--taxonomy` | A |
| `--test-tiers` | B |
| `--transcribed-adr-counts` | A |
| `--type-ignores` | B |
| `--unscoped-rules` | A |
| `--utf8-prefix` | B |
| `--validator-fields` | B |
| `--vendor-manifest` | B |
| `--version` | C |
| `--version-release` | C |
| `--waiver-ratchet` | A |
| `--wheel-path-literals` | A |

## Interpretation and disposition

Retain the disclosure baseline; no upward re-baseline was performed. These are static caller classifications, not dispatch receipts. Tier A does not itself prove a hook was installed or invoked in this session.

The sole D classification, `--doc-surface-parity`, is a false orphan inference: `tests/governance/test_doc_surface_parity.py` imports and calls the audit function directly, including `test_real_project_has_no_commands_dir`. All five tests passed in this run, and the standalone scope passed. `src/gzkit/commands/validate_audits.py:38` also includes it in `AUDITS_AGGREGATE_MEMBERS`, dispatched by `run_audits_umbrella`; the umbrella passed in the sweep. The scanner only detects literal CLI invocations and misses those function calls. Retain the validator; route scanner semantics as a correction. B/C findings require individual caller inspection, not automatic retirement.
