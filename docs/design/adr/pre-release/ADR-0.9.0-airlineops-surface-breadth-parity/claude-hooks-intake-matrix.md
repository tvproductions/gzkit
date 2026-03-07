# ADR-0.9.0 `.claude/hooks` Intake Matrix

## Metadata

- Date: 2026-03-06
- Canonical source: `../airlineops/.claude/hooks/`
- Extraction target: `.claude/hooks/`
- Rule: `GovZero = AirlineOps - product capabilities`

## Decisions

| Canonical Hook | Decision | Rationale | Action |
| --- | --- | --- | --- |
| `instruction-router.py` | Import Now | Governance-only, informational, non-blocking | Imported in OBPI-0.9.0-01 |
| `post-edit-ruff.py` | Import Now | Governance-safe quality automation, non-blocking | Imported in OBPI-0.9.0-01 |
| `obpi-completion-validator.py` | Import with Compatibility | Canonical script assumes `/briefs/` and local audit ledger layout not used in gzkit | Create OBPI-0.9.0-02 adaptation |
| `obpi-completion-recorder.py` | Import with Compatibility | Canonical script targets airlineops anchor/runtime layout | Create OBPI-0.9.0-02 adaptation |
| `pipeline-gate.py` | Defer (Tracked) | Depends on plan-audit pipeline markers not yet in gzkit runtime | Track for OBPI-0.9.0-02 |
| `pipeline-router.py` | Defer (Tracked) | Depends on plan-mode lifecycle surfaces not yet imported | Track for OBPI-0.9.0-02 |
| `plan-audit-gate.py` | Defer (Tracked) | Requires plan-mode audit assets absent in gzkit | Track for OBPI-0.9.0-02 |
| `pipeline-completion-reminder.py` | Defer (Tracked) | Depends on pipeline lifecycle markers | Track for OBPI-0.9.0-02 |
| `session-staleness-check.py` | Defer (Tracked) | Session policy import should be bundled with plan lifecycle controls | Track for OBPI-0.9.0-02 |
| `insight-harvester.py` | Defer (Tracked) | Requires transcript-path/session-end contract integration | Track for OBPI-0.9.0-03 |
| `insight-reminder.py` | Defer (Tracked) | Companion to insight harvester/session controls | Track for OBPI-0.9.0-03 |
| `hook-diag.py` | Defer (Tracked) | Operational debug utility; import after primary hook runtime parity | Track for OBPI-0.9.0-03 |
| `dataset-guard.py` | Exclude | Product capability guard from AirlineOps dataset domain, not GovZero-core | Keep excluded unless gzkit product scope changes |
| `README.md` | Import with Compatibility | Canonical README references hooks not yet present; gzkit needs a truthful local variant | Created gzkit-specific `.claude/hooks/README.md` in OBPI-0.9.0-01 |

## Evidence Commands

```bash
cd ../airlineops && rg --files .claude/hooks | sort
rg --files .claude/hooks | sort
```

## Immediate Tranche Result

- Imported: `.claude/hooks/instruction-router.py`
- Imported: `.claude/hooks/post-edit-ruff.py`
- Created: `.claude/hooks/README.md` (gzkit-compatible content)
- Wired in `.claude/settings.json`:
  - `PreToolUse Write|Edit -> instruction-router.py`
  - `PostToolUse Edit|Write -> post-edit-ruff.py`
  - Existing `ledger-writer.py` retained
