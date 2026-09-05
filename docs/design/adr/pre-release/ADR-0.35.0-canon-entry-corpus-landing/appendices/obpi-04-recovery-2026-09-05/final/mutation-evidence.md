# OBPI-0.35.0-04 final-source mutation evidence — 2026-09-05

`summary-v4.json` records **43 passing, unskipped baselines and 43 assertion-killed
mutations**, zero survivors, zero invalid cases, verified before/after module
provenance, exact restoration after every mutation, and unchanged baseline
inventory. Final selected live input hashes still match after execution.

The source commit is `40fd9994e5b0347acc19fcd35e40b7fb8c6a2a0f` plus the
explicitly hashed R16 test-fixture correction. The four selected file hashes in
`summary-v4.json` are the binding identity; this is not a claim that every tested
byte equals that commit.

## Roster and limits

- G1–G18 are reconstructed current edits under historical labels. The original
  historical runner is lost; these are not a replay of its exact patches.
- Historical G19–G22 remain missing. None have been invented or renumbered.
- R01–R18 are explicitly named current recovery/diagnostic witnesses.
- W01–W07 are seven controls of the production Windows route, status handling,
  handle closure, ABI, unknown platform, and synchronization flags. They use
  **mocked native boundaries on this local host**. Actual Windows integration
  execution is separate CI evidence, not proved by this sweep.
- These are sensitivity witnesses for named edits, not exhaustive fault or
  power-loss proof. Ledger #952/#953 and coherent `.gzkit/` tampering retain
  their already accepted boundaries.

The runner's `obpi_sweep_complete` stays false by design: it does not certify
native Windows integration, final review, or OBPI completion. The finite local
manifest is fully selected and every case is witnessed.

## Preserved failed attempts and corrections

`v2-refusal.txt` records refusal before output creation when the initial manifest
caught a concurrent ownership-test addition. The original36 builder preceded the
addition while the Windows extension followed it. The v3 rebuild preserves every
exact edit and test selector, with explicit comparison records.

`full-run-v3/results.json` remains unchanged: **41 killed, one invalid RED (R06),
one survivor (R16)**. R06 had eight real preservation assertion failures inside
helper subtests, but the old runner required a selected-method traceback frame
that unittest had already truncated at the subtest boundary. Runner v2 observes
explicit test-method execution phase as an additional witness. It does not
accept setup or teardown failures. Eight retained harness controls show two valid
method/helper assertions accepted and six setup/teardown/import/origin cases
rejected.

R16 survived because its fixture seeded only an old extraction, not the old
snapshot whose exemption the mutation changed. The corrected fixture seeds an
old snapshot and verifies that retained current material equals current source
bytes. Production code did not change. `case-rebinding-review-v4.json` records
unchanged exact mutation edits and selectors against the corrected test bytes.
The v4 run kills both R06 and R16 and all other cases.

## Reproduction and retention

Run from the gzkit checkout with its declared dependencies:

```bash
UV_CACHE_DIR=/tmp/gzkit-health-uv-cache \
UV_TOOL_DIR=/tmp/gzkit-health-uv-tools \
uv run --no-sync python run_sweep-v2.py \
  --manifest manifest43-v4.json \
  --root /Users/jeff/Documents/Code/gzkit \
  --output /private/tmp/gzkit-obpi04-another-mutation-run --timeout 120
```

Choose a new output directory. The runner refuses hash drift, ambiguous edits,
setup/import failures, skips, timeouts, and module origins outside its isolated
worktree. It mutates only that isolated worktree and restores exact bytes after
each case. `provenance_controls.py` exercises the eight harness controls.

`final-mutation-evidence.zip` retains runner versions, builders, every manifest
and review record, summaries, full per-case stdout/stderr/commands/provenance,
exact before/after mutated source, and all actually loaded project module bytes
from each baseline. It omits duplicate complete baseline/worktree copies and
bytecode caches; full baseline inventories remain. The complete original trees
also remain in the temporary working directory. `archive-members.json` lists
retained member SHA-256 values and `archive-verification.json` verifies the ZIP
against those bytes. No prior result has been overwritten.
