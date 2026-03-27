# CHORE-LOG: doc-coverage

## 2026-03-26T20:38:26-05:00
- Status: FAIL
- Chore: doc-coverage
- Title: Documentation Cross-Coverage Enforcement
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run -m gzkit.doc_coverage.runner` => rc=1 (0.32s) — exit 1 != 0

```text
[uv run -m gzkit.doc_coverage.runner] stdout:
Documentation Coverage Gap Report
========================================

  Command: adr covers-check
    MISSING: governance_runbook -- 'gz adr covers-check' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz adr covers-check' not found in runbook.md
  Command: adr promote
    MISSING: operator_runbook -- 'gz adr promote' not found in runbook.md
  Command: adr report
    MISSING: command_docs_mapping -- 'adr report' not in COMMAND_DOCS
    MISSING: governance_runbook -- 'gz adr report' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz adr report' not found in runbook.md
  Command: agent sync control-surfaces
    MISSING: operator_runbook -- 'gz agent sync control-surfaces' not found in runbook.md
  Command: check
    MISSING: command_docs_mapping -- 'check' not in COMMAND_DOCS
    MISSING: manpage -- Missing check.md
  Command: chores advise
    MISSING: command_docs_mapping -- 'chores advise' not in COMMAND_DOCS
    MISSING: index_entry -- 'chores-advise.md' not in index
    MISSING: manpage -- Missing chores-advise.md
    MISSING: operator_runbook -- 'gz chores advise' not found in runbook.md
  Command: chores audit
    MISSING: operator_runbook -- 'gz chores audit' not found in runbook.md
  Command: chores list
    MISSING: operator_runbook -- 'gz chores list' not found in runbook.md
  Command: chores plan
    MISSING: operator_runbook -- 'gz chores plan' not found in runbook.md
  Command: chores run
    MISSING: operator_runbook -- 'gz chores run' not found in runbook.md
  Command: chores show
    MISSING: command_docs_mapping -- 'chores show' not in COMMAND_DOCS
    MISSING: index_entry -- 'chores-show.md' not in index
    MISSING: manpage -- Missing chores-show.md
    MISSING: operator_runbook -- 'gz chores show' not found in runbook.md
  Command: constitute
    MISSING: governance_runbook -- 'gz constitute' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz constitute' not found in runbook.md
  Command: format
    MISSING: command_docs_mapping -- 'format' not in COMMAND_DOCS
    MISSING: index_entry -- 'format.md' not in index
    MISSING: manpage -- Missing format.md
    MISSING: operator_runbook -- 'gz format' not found in runbook.md
  Command: init
    MISSING: governance_runbook -- 'gz init' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz init' not found in runbook.md
  Command: interview
    MISSING: command_docs_mapping -- 'interview' not in COMMAND_DOCS
    MISSING: index_entry -- 'interview.md' not in index
    MISSING: manpage -- Missing interview.md
    MISSING: operator_runbook -- 'gz interview' not found in runbook.md
  Command: lint
    MISSING: command_docs_mapping -- 'lint' not in COMMAND_DOCS
    MISSING: index_entry -- 'lint.md' not in index
    MISSING: manpage -- Missing lint.md
  Command: migrate-semver
    MISSING: governance_runbook -- 'gz migrate-semver' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz migrate-semver' not found in runbook.md
  Command: obpi emit-receipt
    MISSING: governance_runbook -- 'gz obpi emit-receipt' not found in governance_runbook.md
  Command: obpi pipeline
    MISSING: governance_runbook -- 'gz obpi pipeline' not found in governance_runbook.md
  Command: obpi reconcile
    MISSING: governance_runbook -- 'gz obpi reconcile' not found in governance_runbook.md
  Command: obpi status
    MISSING: governance_runbook -- 'gz obpi status' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz obpi status' not found in runbook.md
  Command: parity check
    MISSING: governance_runbook -- 'gz parity check' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz parity check' not found in runbook.md
  Command: plan
    MISSING: governance_runbook -- 'gz plan' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz plan' not found in runbook.md
  Command: prd
    MISSING: governance_runbook -- 'gz prd' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz prd' not found in runbook.md
  Command: readiness evaluate
    MISSING: governance_runbook -- 'gz readiness evaluate' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz readiness evaluate' not found in runbook.md
  Command: register-adrs
    MISSING: governance_runbook -- 'gz register-adrs' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz register-adrs' not found in runbook.md
  Command: roles
    MISSING: governance_runbook -- 'gz roles' not found in governance_runbook.md
  Command: skill audit
    MISSING: operator_runbook -- 'gz skill audit' not found in runbook.md
  Command: skill list
    MISSING: command_docs_mapping -- 'skill list' not in COMMAND_DOCS
    MISSING: index_entry -- 'skill-list.md' not in index
    MISSING: manpage -- Missing skill-list.md
    MISSING: operator_runbook -- 'gz skill list' not found in runbook.md
  Command: skill new
    MISSING: command_docs_mapping -- 'skill new' not in COMMAND_DOCS
    MISSING: index_entry -- 'skill-new.md' not in index
    MISSING: manpage -- Missing skill-new.md
    MISSING: operator_runbook -- 'gz skill new' not found in runbook.md
  Command: specify
    MISSING: governance_runbook -- 'gz specify' not found in governance_runbook.md
    MISSING: operator_runbook -- 'gz specify' not found in runbook.md
  Command: state
    MISSING: operator_runbook -- 'gz state' not found in runbook.md
  Command: test
    MISSING: command_docs_mapping -- 'test' not in COMMAND_DOCS
    MISSING: manpage -- Missing test.md
  Command: tidy
    MISSING: command_docs_mapping -- 'tidy' not in COMMAND_DOCS
    MISSING: index_entry -- 'tidy.md' not in index
    MISSING: manpage -- Missing tidy.md
    MISSING: operator_runbook -- 'gz tidy' not found in runbook.md
  Command: typecheck
    MISSING: command_docs_mapping -- 'typecheck' not in COMMAND_DOCS
    MISSING: index_entry -- 'typecheck.md' not in index
    MISSING: manpage -- Missing typecheck.md
  Command: validate
    MISSING: command_docs_mapping -- 'validate' not in COMMAND_DOCS
    MISSING: manpage -- Missing validate.md

  Orphaned documentation:
    - [manpage] docs/user/commands/adr-audit-check.md: Manpage 'adr-audit-check.md' has no matching command 'adr audit check'
    - [manpage] docs/user/commands/adr-covers-check.md: Manpage 'adr-covers-check.md' has no matching command 'adr covers check'
    - [manpage] docs/user/commands/adr-emit-receipt.md: Manpage 'adr-emit-receipt.md' has no matching command 'adr emit receipt'
    - [manpage] docs/user/commands/agent-sync-control-surfaces.md: Manpage 'agent-sync-control-surfaces.md' has no matching command 'agent sync control surfaces'
    - [manpage] docs/user/commands/check-config-paths.md: Manpage 'check-config-paths.md' has no matching command 'check config paths'
    - [manpage] docs/user/commands/git-sync.md: Manpage 'git-sync.md' has no matching command 'git sync'
    - [manpage] docs/user/commands/migrate-semver.md: Manpage 'migrate-semver.md' has no matching command 'migrate semver'
    - [manpage] docs/user/commands/obpi-emit-receipt.md: Manpage 'obpi-emit-receipt.md' has no matching command 'obpi emit receipt'
    - [manpage] docs/user/commands/register-adrs.md: Manpage 'register-adrs.md' has no matching command 'register adrs'

FAILED: 86 issues found across 36 commands.
[uv run -m gzkit.doc_coverage.runner] stderr:
<frozen runpy>:128: RuntimeWarning: 'gzkit.doc_coverage.runner' found in sys.modules after import of package 'gzkit.doc_coverage', but prior to execution of 'gzkit.doc_coverage.runner'; this may result in unpredictable behaviour
```
