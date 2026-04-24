# CHORE-LOG: sync-manpage-docstrings

## 2026-03-21T14:36:04-05:00
- Status: PASS
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.30s) — exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
```
## 2026-04-02T19:52:53-05:00
- Status: PASS
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.72s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 68/68 commands fully covered.
```
## 2026-04-19T20:02:33-05:00
- Status: FAIL
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run gz cli audit` => rc=1 (1.84s) -- exit 1 != 0

```text
[uv run gz cli audit] stdout:
CLI audit failed.
  - docs\user\commands\arb-ruff.md: missing doc for `arb ruff`
  - docs\user\commands\arb-step.md: missing doc for `arb step`
  - docs\user\commands\arb-ty.md: missing doc for `arb ty`
  - docs\user\commands\arb-typecheck.md: missing doc for `arb typecheck`
  - docs\user\commands\arb-coverage.md: missing doc for `arb coverage`
  - docs\user\commands\arb-validate.md: missing doc for `arb validate`
  - docs\user\commands\arb-advise.md: missing doc for `arb advise`
  - docs\user\commands\arb-patterns.md: missing doc for `arb patterns`
  - cross-coverage:arb ruff: missing manpage: Missing arb-ruff.md
  - cross-coverage:arb ruff: missing index_entry: 'arb-ruff.md' not in index
  - cross-coverage:arb ruff: missing docstring: No handler name resolved
  - cross-coverage:arb step: missing manpage: Missing arb-step.md
  - cross-coverage:arb step: missing index_entry: 'arb-step.md' not in index
  - cross-coverage:arb step: missing docstring: No handler name resolved
  - cross-coverage:arb ty: missing manpage: Missing arb-ty.md
  - cross-coverage:arb ty: missing index_entry: 'arb-ty.md' not in index
  - cross-coverage:arb ty: missing docstring: No handler name resolved
  - cross-coverage:arb typecheck: missing manpage: Missing arb-typecheck.md
  - cross-coverage:arb typecheck: missing index_entry: 'arb-typecheck.md' not
in index
  - cross-coverage:arb typecheck: missing docstring: No handler name resolved
  - cross-coverage:arb coverage: missing manpage: Missing arb-coverage.md
  - cross-coverage:arb coverage: missing index_entry: 'arb-coverage.md' not in
index
  - cross-coverage:arb coverage: missing operator_runbook: 'gz arb coverage'
not found in runbook.md
  - cross-coverage:arb coverage: missing docstring: No handler name resolved
  - cross-coverage:arb validate: missing manpage: Missing arb-validate.md
  - cross-coverage:arb validate: missing index_entry: 'arb-validate.md' not in
index
  - cross-coverage:arb validate: missing docstring: No handler name resolved
  - cross-coverage:arb advise: missing manpage: Missing arb-advise.md
  - cross-coverage:arb advise: missing index_entry: 'arb-advise.md' not in
index
  - cross-coverage:arb advise: missing operator_runbook: 'gz arb advise' not
found in runbook.md
  - cross-coverage:arb advise: missing docstring: No handler name resolved
  - cross-coverage:arb patterns: missing manpage: Missing arb-patterns.md
  - cross-coverage:arb patterns: missing index_entry: 'arb-patterns.md' not in
index
  - cross-coverage:arb patterns: missing operator_runbook: 'gz arb patterns'
not found in runbook.md
  - cross-coverage:arb patterns: missing docstring: No handler name resolved
  - cross-coverage:orphan: orphaned manpage: docs\user\commands\arb.md (Manpage
'arb.md' has no matching discovered command)
  - cross-coverage:orphan: orphaned manpage: docs\user\commands\plan.md
(Manpage 'plan.md' has no matching discovered command)

Cross-coverage: 8/85 commands have gaps.
  - arb ruff: missing manpage, index_entry, docstring
  - arb step: missing manpage, index_entry, docstring
  - arb ty: missing manpage, index_entry, docstring
  - arb typecheck: missing manpage, index_entry, docstring
  - arb coverage: missing manpage, index_entry, operator_runbook, docstring
  - arb validate: missing manpage, index_entry, docstring
  - arb advise: missing manpage, index_entry, operator_runbook, docstring
  - arb patterns: missing manpage, index_entry, operator_runbook, docstring

Orphaned documentation:
  - docs\user\commands\arb.md: Manpage 'arb.md' has no matching discovered
command
  - docs\user\commands\plan.md: Manpage 'plan.md' has no matching discovered
command
```
## 2026-04-19T20:48:32-05:00
- Status: PASS
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (2.01s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 85/85 commands fully covered.
```
## 2026-04-19T21:15:29-05:00
- Status: PASS
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (1.97s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 85/85 commands fully covered.
```
## 2026-04-24T02:24:47-05:00
- Status: PASS
- Chore: sync-manpage-docstrings
- Title: Sync Manpage Docstrings (One-Liner Alignment)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (1.36s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 86/86 commands fully covered.
```
