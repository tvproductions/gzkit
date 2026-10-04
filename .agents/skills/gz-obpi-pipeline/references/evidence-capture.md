# Evidence Capture

Each stage records evidence to the OBPI audit ledger:

| Stage | Evidence Written |
|-------|-----------------|
| Stage 1 | Brief parsed, plan file loaded, lock claimed |
| Stage 2 | Files changed, tests added |
| Stage 3 | Verification outputs (pass/fail) |
| Stage 4 | Attestation text + timestamp |
| Stage 5 | `gz obpi complete` (Step 1: attestation + brief + receipt), lock released (Step 2), markers cleaned (Steps 3-4), git-sync #1 (Step 5), reconcile (Step 6), git-sync #2 (Step 8) |
