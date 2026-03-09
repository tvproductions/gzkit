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
| `obpi-completion-validator.py` | Imported (Adapted) | Adapted for gzkit: `/obpis/OBPI-` paths, `.gzkit/ledger.jsonl`, `resolve_adr_lane()` | Imported in OBPI-0.9.0-02 |
| `obpi-completion-recorder.py` | Already Covered | Recording chain exists via `ledger-writer.py` → `record_artifact_edit()` → `_record_obpi_completion_if_ready()` | No new file needed (OBPI-0.9.0-02) |
| `pipeline-gate.py` | Defer (Confirmed) | `.claude/plans/` infrastructure and pipeline markers absent in gzkit | Deferred — future plan-mode lifecycle ADR |
| `pipeline-router.py` | Defer (Confirmed) | Plan-mode lifecycle surfaces absent in gzkit | Deferred — future plan-mode lifecycle ADR |
| `plan-audit-gate.py` | Defer (Confirmed) | Plan audit receipt infrastructure absent in gzkit | Deferred — future plan-mode lifecycle ADR |
| `pipeline-completion-reminder.py` | Defer (Confirmed) | Pipeline lifecycle markers absent in gzkit | Deferred — future plan-mode lifecycle ADR |
| `session-staleness-check.py` | Defer (Confirmed) | Session policy / pipeline artifacts absent in gzkit | Deferred — future plan-mode lifecycle ADR |
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

## Tranche 1 Result (OBPI-0.9.0-01)

- Imported: `.claude/hooks/instruction-router.py`
- Imported: `.claude/hooks/post-edit-ruff.py`
- Created: `.claude/hooks/README.md` (gzkit-compatible content)
- Wired in `.claude/settings.json`:
  - `PreToolUse Write|Edit -> instruction-router.py`
  - `PostToolUse Edit|Write -> post-edit-ruff.py`
  - Existing `ledger-writer.py` retained

## Tranche 2 Result (OBPI-0.9.0-02)

- Imported (adapted): `.claude/hooks/obpi-completion-validator.py` — PreToolUse blocking gate
- Already covered: `obpi-completion-recorder.py` — existing `ledger-writer.py` chain handles recording
- Deferred (confirmed): 5 pipeline/plan hooks — all depend on plan-mode lifecycle infrastructure
- Updated `.claude/settings.json`:
  - `PreToolUse Write|Edit -> obpi-completion-validator.py (blocking), instruction-router.py`
  - PostToolUse unchanged
- Updated `.claude/hooks/README.md` with tranche history
