---
name: gz-complexity-advisor
description: Preview complexity advisor diagnosis, understand auto-chain context, or check intrinsic complexity attestation guidance. Use when the operator says "preview complexity advisor", "complexity diagnosis", "advisor recommendation", "what does the advisor say", or "intrinsic complexity attestation".
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.2.1"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 - File Sync"
gz_command: complexity advise
model: opus
---

# gz-complexity-advisor

Run `gz complexity advise`, the trigger-time surface of the complexity-doctrine
cluster (ADR-0.0.27 corpus, 0.0.28 thresholds, 0.0.29 advisor, 0.0.30
authoring guidance). It measures per-function `radon_cc` in a file or
directory, and for every function that crosses an `advise`, `warn` or `block`
band of `.gzkit/rules/complexity-thresholds.json` it emits a diagnosis:
archetype, doctrinal frame, proof ranges and recommended move. It exits 3 when
any crossing is in the `block` band and 0 otherwise.

The table's `radon_cc` bands are stricter than the xenon ceiling the
pre-commit hook enforces (`.gzkit/rules/pythonic.md` § Size Limits & Refactoring), so a tree
that commits cleanly can still exit 3 here.

This skill ends at the diagnosis. It does not refactor, and it does not
attest on the operator's behalf.

## When to Use

1. **Ad-hoc preview-before-fail** — see the diagnosis for a file before xenon
   refuses a commit.
2. **After a xenon failure** — the auto-chain hook is not installed in this
   repository, so run the advisor by hand on the files xenon named.
3. **Irreducible complexity** — the operator wants to record that a
   function's complexity is intrinsic.

## Ad-hoc preview

```bash
uv run gz complexity advise src/gzkit/commands/validate_cmd.py
uv run gz complexity advise src/gzkit/ --json
```

## Output Contract

**Declared form:** structured prose (default human-readable). Each diagnosis
prints `Metric | Band | Value | Archetype`, then `Authority`, `Citation`,
`Excerpt`, `Recommended`, and `File` with the line range and node kind,
followed by the function's source. `--auto-chain` selects the condensed
commit-time presentation instead.

**Machine-readable mode:** `--json` emits an array of `AdvisorDiagnosis`
objects with `metric`, `crossing_band`, `crossing_value`, `archetype`,
`doctrinal_frame`, `proof`, `recommended_move` and `intrinsic_attestation`.

When no archetype rule in `data/advisor_archetype_rules.json` matches a
crossing, the archetype falls back to `long_parameter_list`, and no rule covers
the `advise` band. Read the function's code before trusting that label.

## Auto-chain hook

`.pre-commit-config.yaml` runs plain xenon. The composite hook
`complexity-advisor-auto-chain` (OBPI-0.0.29-05) is installed only by
`uv run python -m gzkit.hooks.install_complexity_advisor`. Once installed, it
runs xenon and, on failure, diagnoses the staged Python files in its own
process, printing to stderr and failing the commit on a `block` crossing. It
wraps the advisor in a timeout, `.gzkit.json` § `advisor_timeout_seconds`
(30 seconds when unset) unless the hook is run with `--timeout`; on timeout
it lets the commit through and appends a record to
`.gzkit/insights/advisor-failures.jsonl`. Skip it for one commit with
`SKIP=complexity-advisor-auto-chain git commit`.

## Intrinsic-complexity attestation

Two paths exist. Neither currently stops `gz complexity advise` from
diagnosing the function.

- **`@intrinsic_complexity(reason=..., attestor=...)`** registers the function
  in an in-memory registry when its module is imported. `gz complexity advise`
  reads source files as text and never imports them, so the decorator has no
  effect on a CLI run.
- **`--attest-intrinsic`** takes `<file_path>:<qualname>` as the path, plus
  `--reason` and `--attestor` (a handle, never a real name; an omitted
  `--attestor` takes `.gzkit.json` § `authorship.attestor_handle`). It refuses
  a function that crosses no band and refuses without an interactive terminal.
  The operator types `ATTEST` to confirm, and it appends an
  `intrinsic-complexity-attestation` event to the ledger, whose shape
  `gz validate --intrinsic-attestation` checks. The advisor does not read that
  event back.

The operator runs `--attest-intrinsic` themselves; the agent drafts the reason.

```bash
uv run gz complexity advise src/gzkit/commands/adr_audit.py:_collect_obpi_findings --attest-intrinsic \
  --reason "<why this complexity is intrinsic>" --attestor g0
```

## Related

- Manpage: `docs/user/manpages/complexity-advise.md`
- Runbook: `docs/user/runbook.md` § Governance Doctrine Surfaces
- Sister skill: `gz-complexity-guide` (authoring-time hints)
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/`
- Threshold table: `.gzkit/rules/complexity-thresholds.json` (ADR-0.0.28)
- Distillation: `gz-complexity-distill`
