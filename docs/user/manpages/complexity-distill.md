# gz complexity distill

Distillation pass for the exemplar-corpus doctrine cluster.

## NAME

gz complexity distill — run a complexity distillation pass against the
exemplar corpus and emit a dated distilled-characteristics document.

## SYNOPSIS

```text
gz complexity distill [--corpus PATH] [--output-dir PATH] [--baseline-dir PATH]
                      [--baseline-json PATH]
                      [--prior PATH | --no-prior]
                      [--allow-dated-sibling]
                      [--today YYYY-MM-DD]
```

## DESCRIPTION

`gz complexity distill` is the destination CLI verb for the
[`gz-complexity-distill`](../skills/gz-complexity-distill.md) skill
(parent ADR-0.0.27, OBPI-0.0.27-06). It composes the OBPI-0.0.27-03
measurement pipeline (`gzkit.complexity.measurement.measure_corpus`)
with the OBPI-0.0.27-04 distillation render
(`gzkit.complexity.distillation.render_document`) for ad-hoc operator
invocation.

Default flow:

1. Load the corpus from `--corpus` (default `data/exemplar_corpus.json`).
2. Run the measurement pipeline and write `baseline.json` +
   `baseline.summary.md` under
   `--baseline-dir` (default `<output-dir>/baselines/<today>/`).
3. Auto-detect the most recent prior `distilled-characteristics-*.md`
   under `--output-dir` (excluded if `--no-prior` or if `--prior` is
   supplied explicitly).
4. Render a dated `distilled-characteristics-{YYYY-MM-DD}.md` under
   `--output-dir` (default `docs/governance/complexity/`).
5. Print a human-readable progress summary on stdout.

`--baseline-json PATH` short-circuits steps 1–2: the file is parsed as
a `BaselineArtifact` and used directly. This is the test-injection path
that lets the Output Contract conformance tests run without invoking
radon/lizard/cohesion against real Git checkouts.

The verb does **not** author the practitioner-eye observation block per
metric — every per-metric section emits an operator-attested placeholder
that the operator fills at Gate 5 (REQ-0.0.27-04-10, the OEE seam).

## OPTIONS

- `--corpus PATH` — Corpus JSON path (default `data/exemplar_corpus.json`).
- `--baseline-json PATH` — Pre-built baseline JSON; skip the measurement
  pipeline. The file's content must validate as
  `gzkit.complexity.baseline.BaselineArtifact`.
- `--output-dir PATH` — Where to write the distilled-characteristics
  document (default `docs/governance/complexity`).
- `--baseline-dir PATH` — Where to write the baseline artifacts
  (default `<output-dir>/baselines/<today>/`). Ignored when
  `--baseline-json` is set.
- `--prior PATH` — Prior distilled-characteristics document used by the
  diff-narration section. Defaults to the latest dated sibling under
  `--output-dir` (today's date excluded).
- `--no-prior` — Treat the run as cold-start; skip prior auto-detection
  and emit the cold-start sentinel diff section.
- `--allow-dated-sibling` — On a same-date collision write a
  `-1`-suffixed sibling instead of failing with exit 3.
- `--today YYYY-MM-DD` — Override today's date. Used by tests for
  determinism; not for production runs.
- `--quiet`, `-q` — Suppress non-error output.
- `--verbose`, `-v` — Enable verbose output.
- `--debug` — Enable debug mode with full tracebacks.

## EXIT STATUS

- `0` — Distilled document written; summary printed.
- `1` — User/config error: bad `--today`, missing corpus path, baseline
  JSON failed to parse or validate.
- `2` — System/IO error: required measurement tool binary missing,
  whole-project measurement rejected, write failure.
- `3` — Policy breach: distilled-characteristics document for `--today`
  already exists and `--allow-dated-sibling` was not supplied
  (REQ-0.0.27-04-05 no-overwrite guard).

## EXAMPLES

```bash
# Default run against the canonical corpus
gz complexity distill

# Pin the date and write under a scratch directory (testing)
gz complexity distill --baseline-json fixtures/baseline.json \
                      --output-dir /tmp/distill --no-prior --today 2026-05-05

# Cold-start invocation (skip prior auto-detection)
gz complexity distill --no-prior

# Allow a same-date sibling on collision
gz complexity distill --allow-dated-sibling
```

## OUTPUT CONTRACT (REQ-0.0.27-06-04)

stdout (human-readable summary, four lines plus header):

```text
Distillation pass complete.
  Corpus revision: <int>
  Baseline artifact: <posix path>
  Distilled document: <posix path>
  Per-metric sections rendered: <int>
```

The destination document conforms to OBPI-0.0.27-04: frontmatter
(`corpus_revision`, `baseline_artifact_path`, `distillation_date`,
`prior_distillation_path`), one section per canonical metric, a "Diff
against prior distillation" section (cold-start sentinel on first run),
and a "Citation form" section quoting the citation contract.

## SEE ALSO

- `gz-complexity-distill` skill at `.gzkit/skills/gz-complexity-distill/` —
  the routing skill; this verb is its declared `gz_command:` target.
- ADR-0.0.27 — Exemplar Corpus Doctrine.
- OBPI-0.0.27-04 — distillation pass authoring brief (the produced
  document's structural contract).
- OBPI-0.0.27-06 — distill skill brief (the deferral source closed by
  GHI #400).
- `.gzkit/rules/complexity-doctrine.md` — selection methodology,
  cadence triggers, citation contract.
- [`gz validate`](validate.md) `--complexity-doctrine-links` —
  link-integrity validator that fails closed when downstream ADRs cite
  a missing or out-of-date document.
