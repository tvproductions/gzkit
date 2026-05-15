# Patch Release: v0.26.3

**Date:** 2026-05-15
**Previous Version:** 0.26.2
**Tag:** v0.26.2

## Qualifying GHIs

| # | Title | Status | Warning |
|---|-------|--------|---------|
| 428 | Operator runbook missing first-time-operator entry (empty repo → first attested release) | diff_only | GHI #428 has commits touching src/gzkit/ but no 'runtime' label |
| 429 | Verify PRD → Constitution → Design → ADR handoff cohesion (intent stage) | excluded |  |
| 430 | First-release ceremony (pre-release → v0.1.0/v1.0.0) is undocumented | excluded |  |
| 431 | obpi-specify: detect missing ## Demo section on heavy-lane CLI-shipping briefs | qualified |  |
| 432 | Brief command-shape check has no speculative-skip marker; OBPIs introducing new CLI verbs cannot pass authored validation | qualified |  |
| 433 | audit creates-declaration drops dotfile-rooted paths (.gzkit/, .claude/, .agents/, .github/) due to lstrip | qualified |  |
| 435 | gz obpi pipeline --from=sync --evidence-json silently ignores attestation_text / attestor_present fields | qualified |  |
| 436 | gz obpi pipeline verify gate doesn't catch brief sibling-OBPI/ADR cross-reference drift | qualified |  |
| 437 | Commit-message auto-rewriting silently replaces fix() messages with generic 'chore: update' (GHI #434 victim) | qualified |  |
| 438 | Reconciliation doesn't catch implementation-without-ceremony state (force-released lock + allowed-path changes + frontmatter still Draft) | qualified |  |
| 439 | gz git-sync produces generic 'chore: update X, Y, Z' commit messages that are useless for archaeology | qualified |  |
| 441 | arb: step writer accepts step names the receipt-binding regex rejects | qualified |  |
| 442 | Hook executable test fails on Windows (S_IXUSR not applicable) | excluded |  |
| 443 | Frontmatter runtime budget test flakes under concurrent load | excluded |  |
| 444 | coverage-40pct chore lane mismatch: coverage instrumentation exceeds 120s lite-lane budget | qualified |  |
| 445 | test-isolation-compliance chore: suite >60s + 4 slow tests + 344 lines stdout noise | qualified |  |
| 446 | Author rule-pair conflict matrix (chore: control-surface-rule-conflicts) | excluded |  |
| 448 | chore acceptance for control-surface-rule-conflicts doesn't enforce evidence-bar from ADR-pool.control-surface-rule-pair-conflict-audit | qualified |  |
| 449 | Add .gzkit/ → src/gzkit/ dev-time sync mechanism for canonical surfaces | qualified |  |
| 450 | Add gz upgrade subcommand for adopter-side canonical surface refresh | qualified |  |
| 453 | Residual scaffold_skill dependency on templates/skill.md + stale CORE_SKILLS lint entry (OBPI-0.0.32-02 follow-up) | qualified |  |
| 455 | Security registry staleness after canonical-surface migration (OBPI-0.0.32-03) | qualified |  |
| 456 | gz-plan-audit 'stop cleanly' contradicts gz-obpi-pipeline Iron Law when invoked as sub-step | qualified |  |
| 457 | Rule mirror drift: AGENTS.md + complexity-thresholds.json missing from src/gzkit/rules/ | qualified |  |
| 458 | skill-mandate 'agents MUST run gz obpi pipeline' is advisory in practice; freeform-stage execution produces malformed markers that re-trigger the Stage-5 TTY/PTY friction class | excluded |  |
| 462 | obpi complete: security auto-detect deadlocks completion when canonical slot unfilled | qualified |  |
| 466 | covers-backfill detector: same-commit block-creation flagged as backfill (blocks ADR-0.0.32 audit) | qualified |  |

## Operator Approval

Approved by gz patch release
