# CHORE-LOG: pythonic-design-pattern-detection

## 2026-04-26T18:50:25-05:00
- Status: FAIL
- Chore: pythonic-design-pattern-detection
- Title: Pythonic Design Pattern Detection (AST Scanner + refactoring.guru Catalogue)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run -m unittest -q` => rc=1 (76.59s) -- exit 1 != 0

```text
[uv run -m unittest -q] stdout:
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local (local-only, preserved)
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local-slug (local-only, preserved)
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local (local-only, preserved)
[uv run -m unittest -q] stderr:
======================================================================
FAIL: test_no_bracketed_type_ignore_under_src (tests.governance.test_type_ignore_syntax.TypeIgnoreSyntaxPolicy.test_no_bracketed_type_ignore_under_src)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\governance\test_type_ignore_syntax.py", line 23, in test_no_bracketed_type_ignore_under_src
    self.assertFalse(
    ~~~~~~~~~~~~~~~~^
        errors,
        ^^^^^^^
    ...<4 lines>...
        ),
        ^^
    )
    ^
AssertionError: [ValidationError(type='type_ignores', artifact='src\\gzkit\\chores\\pythonic-design-pattern-detection\\scan.py:422', message='`# type: ignore[<code>]` is not honored by ty. Use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.', field=None, ledger_value=None, frontmatter_value=None)] is not false : Found `# type: ignore[<code>]` comments — ty does not honor bracketed mypy-style codes. Use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.
  src\gzkit\chores\pythonic-design-pattern-detection\scan.py:422: `# type: ignore[<code>]` is not honored by ty. Use bare `# type: ignore` or `# ty: ignore[<ty-code>]`.

======================================================================
FAIL: test_every_active_skill_has_a_manpage (tests.test_skill_manpage_coverage.ActiveSkillManpageCoverageTest.test_every_active_skill_has_a_manpage)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\test_skill_manpage_coverage.py", line 46, in test_every_active_skill_has_a_manpage
    self.assertEqual([], missing, f"active skills missing manpages: {missing}")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [] != ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect']

Second list contains 2 additional elements.
First extra element 0:
'gz-pythonic-pattern-apply'

- []
+ ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect'] : active skills missing manpages: ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect']

======================================================================
FAIL: test_every_active_skill_is_linked_from_index (tests.test_skill_manpage_coverage.ActiveSkillManpageCoverageTest.test_every_active_skill_is_linked_from_index)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\test_skill_manpage_coverage.py", line 72, in test_every_active_skill_is_linked_from_index
    self.assertEqual([], unlinked, f"active skills not linked from index: {unlinked}")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [] != ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect']

Second list contains 2 additional elements.
First extra element 0:
'gz-pythonic-pattern-apply'

- []
+ ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect'] : active skills not linked from index: ['gz-pythonic-pattern-apply', 'gz-pythonic-pattern-detect']

----------------------------------------------------------------------
Ran 3660 tests in 75.589s

FAILED (failures=3, skipped=1)
```
## 2026-04-26T18:53:39-05:00
- Status: PASS
- Chore: pythonic-design-pattern-detection
- Title: Pythonic Design Pattern Detection (AST Scanner + refactoring.guru Catalogue)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (77.60s) -- exit 0 == 0
  - [PASS] `uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py --self-test` => rc=0 (0.10s) -- exit 0 == 0

```text
[uv run -m unittest -q] stdout:
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local (local-only, preserved)
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local-slug (local-only, preserved)
Chores registry diff:
  + agents-md-architectural-boundaries
  + arb-pattern-extraction
  + cli-contract-governance
  + complexity-reduction-xenon
  + config-paths-remediation
  + control-surface-rule-conflicts
  + control-surface-rule-vs-check-drift
  + control-surface-skill-rule-reachability
  + coverage-40pct
  + cross-platform-test-cleanup
  + dependency-currency
  + doc-coverage
  + evidence-integrity-audit
  + exceptions-and-logging-rationalization
  + frontmatter-ledger-coherence
  + hardcoded-root-eradication
  + instructions-files-diet
  + memory-hygiene
  + module-sloc-cap-radon
  + pep257-docstring-compliance
  + pool-triage
  + pythonic-design-pattern-application
  + pythonic-design-pattern-detection
  + pythonic-refactoring
  + quality-check
  + repository-structure-normalization
  + schema-and-config-drift-audit
  + skill-authoring-quality
  + skill-command-doc-parity
  + skill-manifest-sync
  + skill-trigger-testing
  + sync-manpage-docstrings
  + test-isolation-compliance
  + test-manpage-examples
  + validate-manpages
  = only-local (local-only, preserved)
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3660 tests in 76.600s

OK (skipped=1)
[uv run python src/gzkit/chores/pythonic-design-pattern-detection/scan.py --self-test] stdout:
OK (21 positive, 4 negative)
```
