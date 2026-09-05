# Retained OBPI-0.35.0-04 mutation evidence

This directory contains a manifest, an isolated mutation runner, and retained
proof artifacts. It does not certify OBPI completion or replace an independent
adversary round.

## Current roster

`manifest.json` contains **36 named mutations**: 26 behavior mutations,
9 diagnostic mutations, and 1 fixture-sensitivity mutation.

- **G1–G18** reconstruct current witnesses from the historical 18 guard labels.
  The original runner was lost, so these are not a replay of its exact edits.
- **G19–G22 are not present.** The four additional historical targets were not
  recovered. No target, result, or equivalent witness has been invented for them.
- **R01–R18** are newly named current mutations. They are not substitutes for
  the missing historical four.

The manifest records exact function-scoped replacements, source and test hashes,
selected unittest names, and the distinction between behavior, diagnostic, and
fixture-sensitivity evidence. Consult each case rather than treating the count
as 36 independent durability properties.

## Runner guarantees

The runner copies tracked files into retained `baseline/` and `work/` directories
outside the source checkout. It rejects existing output directories, source/test
hash drift, symlinked snapshot files, missing or ambiguous mutation targets, and
inputs that change during snapshot copying. Tracked dirty input is allowed only
when it matches the manifest; results separately record the source commit and
whether selected input bytes match that commit.

Every baseline and mutant test interpreter uses `-B`, an isolated `PYTHONPATH`,
and a fresh bytecode-cache prefix. The bootstrap additionally records **actual
loaded `__file__` paths before and after execution** in a
`<phase>.provenance.json` file. It checks the exact production/test targets and
their hashes, and rejects every loaded `gzkit` or `tests` module whose resolved
file or namespace path escapes `work/`. Environment settings alone earn no
provenance credit. Third-party and standard-library modules may use the selected
interpreter's installed dependencies.

Unittest result objects supply the counts and failure evidence. A killed mutation
requires a passing, unskipped baseline and a mutant assertion whose traceback
reaches the selected test method. Setup-only assertions, import/helper crashes,
test errors, skipped tests, empty runs, timeouts, and failed provenance are invalid
evidence. Bootstrap failures exit 86; their error record cannot count as a kill.

The runner restores the mutated file's exact original bytes in `finally`, checks
them against the retained baseline, and rechecks the complete baseline inventory.
Subprocess captures explicitly decode UTF-8 with replacement for invalid output;
source and manifest text use explicit UTF-8 without silent replacement.

## Latest representative proof

`representative-run-04/results.json` was produced by runner SHA-256
`f86b87e86616600c39e5de6d387fe6594baecbb870d030245f7636978189f32c` against
commit `18454c9066d54c8d14f61c5e43ff3241a45ee757` in the retained
`committed-reference-18454c90/` checkout. All selected source/test bytes match that
commit. A first attempt against the concurrently edited live checkout correctly
refused test-hash drift before creating output.

| Case | Baseline | Mutant | Provenance | Restoration |
| --- | --- | --- | --- | --- |
| R09: actual destination parent barrier | 1 test passes | 1 assertion failure | Valid before/after; 42 project modules | Exact bytes restored |
| R14: unreadable pending-source recovery diagnosis | 1 test passes | 4 subtest assertion failures | Valid before/after; 109 project modules | Exact bytes restored |

Both cases are `KILLED`; the complete baseline inventory is unchanged.
`full_manifest_selected` and `obpi_sweep_complete` are **false**.

`provenance-controls-01/results.json` records five harness controls: a test-method
assertion is accepted; a setup assertion, setup error, import crash, and import
from outside isolated work are rejected. The fixtures and subprocess evidence
are retained beside that result.

`representative-run-02/` preserves nine earlier representative kills. It predates
the explicit loaded-module provenance checks and must not be described as having
those newer witnesses. Earlier output directories remain unchanged.

## Command

Run from the gzkit project so `uv run` selects its declared interpreter and
dependencies. This is the command used for the latest representative proof:

```bash
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache \
UV_TOOL_DIR=/tmp/gzkit-health-uv-tools \
uv run python /private/tmp/gzkit-obpi04-assessment-4dt92ti0/mutation-sweep/run_sweep.py \
  --manifest /private/tmp/gzkit-obpi04-assessment-4dt92ti0/mutation-sweep/manifest.json \
  --root /private/tmp/gzkit-obpi04-assessment-4dt92ti0/mutation-sweep/committed-reference-18454c90 \
  --output /private/tmp/gzkit-obpi04-assessment-4dt92ti0/mutation-sweep/representative-run-04 \
  --cases R09,R14
```

For another run, choose a **new** output directory. Omitting `--cases` selects all
36 current manifest entries; that full run has not been performed with this
runner. Source or test changes require a reviewed manifest rebuild, never silent
retargeting of an existing case. Keep the previous manifest and results.

## Limits

The proof concerns sensitivity to the exact named edits. It does not establish
exhaustive fault coverage, power-loss behavior, or the identities of lost
historical cases. The manifest retains the declared boundaries for ledger
durability/atomicity (GHI #952/#953) and arbitrary coherent `.gzkit` tampering.

**Native Windows evidence remains pending.** Workflow run `33972482837` was
dispatched separately; this harness does not infer its outcome or credit local
POSIX tests as Windows proof. The representative evidence is bound to the named
commit and hashes, not to later Windows-related source or test changes.
