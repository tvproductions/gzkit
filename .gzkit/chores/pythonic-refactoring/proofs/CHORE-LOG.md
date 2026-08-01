# CHORE-LOG: pythonic-refactoring

## 2026-05-10T15:30:21-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.08s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.40s) -- exit 0 == 0
  - [FAIL] `uv run -m unittest -q` => rc=1 (97.80s) -- exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stdout:
Validated: evaluation-justify-binding

✓ No evaluation-justify-binding violations.
Validated: evaluation-justify-binding

❌ 1 violation(s):

   → ADR-0.0.fixture: missing gz-justify artifact for low score
Error: Attestation receipt-binding gate failed (heavy/foundation policy).
  - missing: no receipt file at
arb-step-unittest-dddddddddddddddddddddddddddddddd.json
Recovery: re-run the cited ARB commands and re-cite the resolved receipt IDs.
Error: ADR closeout blocked — unwaived REQ coverage gaps in ADR-9.9.9-fixture:
  OBPI-9.9.9-99-fixture: REQ-9.9.9-99-01
Waive each gap with `gz obpi complete --accept-uncovered <REQ-ID>
--accept-uncovered-reason <REASON>` before closing the ADR.
ADR closeout receipt emitted.
  ADR: ADR-9.9.9-fixture
  Event: closed
ADR closeout receipt emitted.
  ADR: ADR-9.9.9-fixture
  Event: closed
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- NO GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0

Advisory proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Advisory: would file GHI for dim:clarity:low
No proofs directory for eval-feedback-cluster
No unfiled proposals for eval-feedback-cluster.

Proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/101

Proposal: dim:clarity:low
  Recurrence: 5
  Summary: Dimension 'clarity' scored in the 'low' band across 3 artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/100

Proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/99
usage: gz complexity advise [-h] [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path RULE_PATH]
                            [--attest-intrinsic] [--reason REASON]
                            [--attestor ATTESTOR] [--debug]
                            path

Runs the OBPI-0.0.29-02 diagnosis engine against the file or directory at PATH. Loads the canonical threshold table from .gzkit/rules/complexity-thresholds.json (ADR-0.0.28), measures per-function radon_cc via radon's Python API, and emits an AdvisorDiagnosis for every band crossing. Default output is structured prose; --json emits the canonical Pydantic serialization. Exit codes: 0 success or warn-band crossings, 1 user/config error, 2 system/IO error, 3 block-band crossing.

positional arguments:
  path                  File or directory to analyze (recursive on
                        directories)

options:
  -h, --help            show this help message and exit
  --json                Emit AdvisorDiagnosis list as a JSON array
                        (machine-readable)
  --quiet               Errors only (no progress output)
  --verbose             Debug output (per-file analysis trace)
  --dry-run             Show planned actions without executing
  --auto-chain          Reserved for OBPI-05 (xenon-as-gate auto-fire); no-op
                        here
  --rule-path RULE_PATH
                        Override threshold data path (default:
                        .gzkit/rules/complexity-thresholds.json)
  --attest-intrinsic    Commit-time intrinsic attestation; requires
                        <file>:<qualname> as path
  --reason REASON       Rationale for intrinsic attestation (required with
                        --attest-intrinsic)
  --attestor ATTESTOR   Full name of the attesting human (required with
                        --attest-intrinsic)
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity advise src/gzkit/commands/validate.py
    gz complexity advise src/gzkit/ --json
    gz complexity advise tests/ --quiet

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
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
  + eval-feedback-cluster
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
  + eval-feedback-cluster
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
  + eval-feedback-cluster
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
ADR audit-check: ADR-0.0.23
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
Backfill 1 covers-backfill warning(s):
  tests/x.py:1 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa (0c / 0d before receipt
r1); see .claude/rules/tests.md § Invariant 6f for remediation
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
Unresolvable 1 covers-backfill location(s) not resolvable in git:
  tests/x.py:1 unresolvable
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
FAIL 1 covers-backfill finding(s):
  tests/x.py:1 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa (0c / 0d before receipt
r1); see .claude/rules/tests.md § Invariant 6f for remediation
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmp90drxe8g/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
usage: gz complexity advise [-h] [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path RULE_PATH]
                            [--attest-intrinsic] [--reason REASON]
                            [--attestor ATTESTOR] [--debug]
                            path

Runs the OBPI-0.0.29-02 diagnosis engine against the file or directory at PATH. Loads the canonical threshold table from .gzkit/rules/complexity-thresholds.json (ADR-0.0.28), measures per-function radon_cc via radon's Python API, and emits an AdvisorDiagnosis for every band crossing. Default output is structured prose; --json emits the canonical Pydantic serialization. Exit codes: 0 success or warn-band crossings, 1 user/config error, 2 system/IO error, 3 block-band crossing.

positional arguments:
  path                  File or directory to analyze (recursive on
                        directories)

options:
  -h, --help            show this help message and exit
  --json                Emit AdvisorDiagnosis list as a JSON array
                        (machine-readable)
  --quiet               Errors only (no progress output)
  --verbose             Debug output (per-file analysis trace)
  --dry-run             Show planned actions without executing
  --auto-chain          Reserved for OBPI-05 (xenon-as-gate auto-fire); no-op
                        here
  --rule-path RULE_PATH
                        Override threshold data path (default:
                        .gzkit/rules/complexity-thresholds.json)
  --attest-intrinsic    Commit-time intrinsic attestation; requires
                        <file>:<qualname> as path
  --reason REASON       Rationale for intrinsic attestation (required with
                        --attest-intrinsic)
  --attestor ATTESTOR   Full name of the attesting human (required with
                        --attest-intrinsic)
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity advise src/gzkit/commands/validate.py
    gz complexity advise src/gzkit/ --json
    gz complexity advise tests/ --quiet

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz complexity guide [-h] [--json] [--quiet] [--verbose] [--server]
                           [--debug]
                           [path]

Reads the advise band from the canonical threshold table (.gzkit/rules/complexity-thresholds.json, ADR-0.0.28), measures the target file or directory, and emits AuthoringHint blocks for functions approaching the warn threshold. Exit 3 is NOT used — this surface never blocks; that is gz complexity advise's role.

positional arguments:
  path        File or directory to analyze

options:
  -h, --help  show this help message and exit
  --json      Emit canonical AuthoringHint JSON array to stdout
  --quiet     Suppress output; rely on exit code only
  --verbose   Emit debug output to stderr
  --server    Start JSON-over-stdio LSP-style protocol server for editor/IDE
              integration.
  --debug     Enable debug mode with full tracebacks

Examples
    gz complexity guide src/gzkit/commands/validate.py
    gz complexity guide src/gzkit/ --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz complexity distill [-h] [--corpus CORPUS]
                             [--baseline-json BASELINE_JSON]
                             [--output-dir OUTPUT_DIR]
                             [--baseline-dir BASELINE_DIR] [--prior PRIOR]
                             [--no-prior] [--allow-dated-sibling]
                             [--today TODAY_OVERRIDE] [--quiet | --verbose]
                             [--debug]

Compose the OBPI-0.0.27-03 measurement pipeline with the OBPI-0.0.27-04 distillation render. Loads the corpus from --corpus, runs measurement to --baseline-dir, and writes a dated distilled-characteristics-{YYYY-MM-DD}.md under --output-dir. Use --baseline-json to inject a pre-built baseline and skip measurement (test path; agent-runs use --corpus).

options:
  -h, --help            show this help message and exit
  --corpus CORPUS       Corpus JSON path (default: data/exemplar_corpus.json)
  --baseline-json BASELINE_JSON
                        Pre-built baseline JSON (skip measurement; mutually
                        exclusive with --corpus run)
  --output-dir OUTPUT_DIR
                        Distilled-document output directory (default:
                        docs/governance/complexity)
  --baseline-dir BASELINE_DIR
                        Baseline output directory (default:
                        <output-dir>/baselines/<today>/)
  --prior PRIOR         Prior distilled-characteristics document path
                        (default: latest in output-dir)
  --no-prior            Treat as cold start; skip prior auto-detection
  --allow-dated-sibling
                        On same-date collision, write a -1-suffixed sibling
                        instead of failing
  --today TODAY_OVERRIDE
                        Override today's date (YYYY-MM-DD; for testing)
  --quiet, -q           Suppress non-error output
  --verbose, -v         Enable verbose output
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity distill
    gz complexity distill --corpus data/exemplar_corpus.json
    gz complexity distill --baseline-json baseline.json --no-prior
    gz complexity distill --today 2026-05-05 --allow-dated-sibling

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
[uv run -m unittest -q] stderr:
Exception in thread Thread-537 (_readerthread):
Traceback (most recent call last):
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\threading.py", line 1044, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\threading.py", line 995, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\subprocess.py", line 1615, in _readerthread
    buffer.append(fh.read())
                  ~~~~~~~^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 29: character maps to <undefined>
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmphhek25b_\test_broken.py
Malformed REQ line (skipped): - [ ] REQ-X-Y-Z: Malformed (non-numeric).
Malformed REQ line (skipped): - [ ] REQ-: Empty body.
======================================================================
ERROR: tests.hooks.test_complexity_advisor_auto_chain (unittest.loader._FailedTest.tests.hooks.test_complexity_advisor_auto_chain)
----------------------------------------------------------------------
ImportError: Failed to import test module: tests.hooks.test_complexity_advisor_auto_chain
Traceback (most recent call last):
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\unittest\loader.py", line 396, in _find_test_path
    module = self._get_module_from_name(name)
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\unittest\loader.py", line 339, in _get_module_from_name
    __import__(name)
    ~~~~~~~~~~^^^^^^
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\hooks\test_complexity_advisor_auto_chain.py", line 246, in <module>
    class TestShellHookContract(unittest.TestCase):
    ...<50 lines>...
                        )
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\hooks\test_complexity_advisor_auto_chain.py", line 249, in TestShellHookContract
    @covers("REQ-0.0.29-05-10")
     ~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\traceability.py", line 219, in covers
    raise ValueError(msg)
ValueError: Unknown REQ identifier: 'REQ-0.0.29-05-10' not found in extracted briefs


----------------------------------------------------------------------
Ran 4657 tests in 96.671s

FAILED (errors=1, skipped=2)
```
## 2026-05-10T15:36:12-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.08s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.35s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (95.22s) -- exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stdout:
Validated: evaluation-justify-binding

✓ No evaluation-justify-binding violations.
Validated: evaluation-justify-binding

❌ 1 violation(s):

   → ADR-0.0.fixture: missing gz-justify artifact for low score
Error: Attestation receipt-binding gate failed (heavy/foundation policy).
  - missing: no receipt file at
arb-step-unittest-dddddddddddddddddddddddddddddddd.json
Recovery: re-run the cited ARB commands and re-cite the resolved receipt IDs.
Error: ADR closeout blocked — unwaived REQ coverage gaps in ADR-9.9.9-fixture:
  OBPI-9.9.9-99-fixture: REQ-9.9.9-99-01
Waive each gap with `gz obpi complete --accept-uncovered <REQ-ID>
--accept-uncovered-reason <REASON>` before closing the ADR.
ADR closeout receipt emitted.
  ADR: ADR-9.9.9-fixture
  Event: closed
ADR closeout receipt emitted.
  ADR: ADR-9.9.9-fixture
  Event: closed
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- NO GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0
ADR Eval: ADR-0.0.26 -- GO
  Weighted total: 0.75/4.0
  OBPIs scored: 0

Advisory proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Advisory: would file GHI for dim:clarity:low
No proofs directory for eval-feedback-cluster
No unfiled proposals for eval-feedback-cluster.

Proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/101

Proposal: dim:clarity:low
  Recurrence: 5
  Summary: Dimension 'clarity' scored in the 'low' band across 3 artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/100

Proposal: dim:clarity:low
  Recurrence: 3
  Summary: Dimension 'clarity' scored in the 'low' band across 3 distinct
artifacts
  Rule target: docs/governance/clarity-low-improvement.md
Filed: https://github.com/owner/repo/issues/99
usage: gz complexity advise [-h] [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path RULE_PATH]
                            [--attest-intrinsic] [--reason REASON]
                            [--attestor ATTESTOR] [--debug]
                            path

Runs the OBPI-0.0.29-02 diagnosis engine against the file or directory at PATH. Loads the canonical threshold table from .gzkit/rules/complexity-thresholds.json (ADR-0.0.28), measures per-function radon_cc via radon's Python API, and emits an AdvisorDiagnosis for every band crossing. Default output is structured prose; --json emits the canonical Pydantic serialization. Exit codes: 0 success or warn-band crossings, 1 user/config error, 2 system/IO error, 3 block-band crossing.

positional arguments:
  path                  File or directory to analyze (recursive on
                        directories)

options:
  -h, --help            show this help message and exit
  --json                Emit AdvisorDiagnosis list as a JSON array
                        (machine-readable)
  --quiet               Errors only (no progress output)
  --verbose             Debug output (per-file analysis trace)
  --dry-run             Show planned actions without executing
  --auto-chain          Reserved for OBPI-05 (xenon-as-gate auto-fire); no-op
                        here
  --rule-path RULE_PATH
                        Override threshold data path (default:
                        .gzkit/rules/complexity-thresholds.json)
  --attest-intrinsic    Commit-time intrinsic attestation; requires
                        <file>:<qualname> as path
  --reason REASON       Rationale for intrinsic attestation (required with
                        --attest-intrinsic)
  --attestor ATTESTOR   Full name of the attesting human (required with
                        --attest-intrinsic)
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity advise src/gzkit/commands/validate.py
    gz complexity advise src/gzkit/ --json
    gz complexity advise tests/ --quiet

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
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
  + eval-feedback-cluster
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
  + eval-feedback-cluster
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
  + eval-feedback-cluster
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
ADR audit-check: ADR-0.0.23
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
Backfill 1 covers-backfill warning(s):
  tests/x.py:1 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa (0c / 0d before receipt
r1); see .claude/rules/tests.md § Invariant 6f for remediation
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
Unresolvable 1 covers-backfill location(s) not resolvable in git:
  tests/x.py:1 unresolvable
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.

Coverage: No REQs found for this ADR.
FAIL 1 covers-backfill finding(s):
  tests/x.py:1 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa (0c / 0d before receipt
r1); see .claude/rules/tests.md § Invariant 6f for remediation
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmpw7jkq974/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
Hook 'complexity-advisor-auto-chain' already present in .pre-commit-config.yaml
Installed hook 'complexity-advisor-auto-chain' in .pre-commit-config.yaml
  Replaced: xenon-complexity -> complexity-advisor-auto-chain
  Skip:     SKIP=complexity-advisor-auto-chain git commit
usage: gz complexity advise [-h] [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path RULE_PATH]
                            [--attest-intrinsic] [--reason REASON]
                            [--attestor ATTESTOR] [--debug]
                            path

Runs the OBPI-0.0.29-02 diagnosis engine against the file or directory at PATH. Loads the canonical threshold table from .gzkit/rules/complexity-thresholds.json (ADR-0.0.28), measures per-function radon_cc via radon's Python API, and emits an AdvisorDiagnosis for every band crossing. Default output is structured prose; --json emits the canonical Pydantic serialization. Exit codes: 0 success or warn-band crossings, 1 user/config error, 2 system/IO error, 3 block-band crossing.

positional arguments:
  path                  File or directory to analyze (recursive on
                        directories)

options:
  -h, --help            show this help message and exit
  --json                Emit AdvisorDiagnosis list as a JSON array
                        (machine-readable)
  --quiet               Errors only (no progress output)
  --verbose             Debug output (per-file analysis trace)
  --dry-run             Show planned actions without executing
  --auto-chain          Reserved for OBPI-05 (xenon-as-gate auto-fire); no-op
                        here
  --rule-path RULE_PATH
                        Override threshold data path (default:
                        .gzkit/rules/complexity-thresholds.json)
  --attest-intrinsic    Commit-time intrinsic attestation; requires
                        <file>:<qualname> as path
  --reason REASON       Rationale for intrinsic attestation (required with
                        --attest-intrinsic)
  --attestor ATTESTOR   Full name of the attesting human (required with
                        --attest-intrinsic)
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity advise src/gzkit/commands/validate.py
    gz complexity advise src/gzkit/ --json
    gz complexity advise tests/ --quiet

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz complexity guide [-h] [--json] [--quiet] [--verbose] [--server]
                           [--debug]
                           [path]

Reads the advise band from the canonical threshold table (.gzkit/rules/complexity-thresholds.json, ADR-0.0.28), measures the target file or directory, and emits AuthoringHint blocks for functions approaching the warn threshold. Exit 3 is NOT used — this surface never blocks; that is gz complexity advise's role.

positional arguments:
  path        File or directory to analyze

options:
  -h, --help  show this help message and exit
  --json      Emit canonical AuthoringHint JSON array to stdout
  --quiet     Suppress output; rely on exit code only
  --verbose   Emit debug output to stderr
  --server    Start JSON-over-stdio LSP-style protocol server for editor/IDE
              integration.
  --debug     Enable debug mode with full tracebacks

Examples
    gz complexity guide src/gzkit/commands/validate.py
    gz complexity guide src/gzkit/ --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz complexity distill [-h] [--corpus CORPUS]
                             [--baseline-json BASELINE_JSON]
                             [--output-dir OUTPUT_DIR]
                             [--baseline-dir BASELINE_DIR] [--prior PRIOR]
                             [--no-prior] [--allow-dated-sibling]
                             [--today TODAY_OVERRIDE] [--quiet | --verbose]
                             [--debug]

Compose the OBPI-0.0.27-03 measurement pipeline with the OBPI-0.0.27-04 distillation render. Loads the corpus from --corpus, runs measurement to --baseline-dir, and writes a dated distilled-characteristics-{YYYY-MM-DD}.md under --output-dir. Use --baseline-json to inject a pre-built baseline and skip measurement (test path; agent-runs use --corpus).

options:
  -h, --help            show this help message and exit
  --corpus CORPUS       Corpus JSON path (default: data/exemplar_corpus.json)
  --baseline-json BASELINE_JSON
                        Pre-built baseline JSON (skip measurement; mutually
                        exclusive with --corpus run)
  --output-dir OUTPUT_DIR
                        Distilled-document output directory (default:
                        docs/governance/complexity)
  --baseline-dir BASELINE_DIR
                        Baseline output directory (default:
                        <output-dir>/baselines/<today>/)
  --prior PRIOR         Prior distilled-characteristics document path
                        (default: latest in output-dir)
  --no-prior            Treat as cold start; skip prior auto-detection
  --allow-dated-sibling
                        On same-date collision, write a -1-suffixed sibling
                        instead of failing
  --today TODAY_OVERRIDE
                        Override today's date (YYYY-MM-DD; for testing)
  --quiet, -q           Suppress non-error output
  --verbose, -v         Enable verbose output
  --debug               Enable debug mode with full tracebacks

Examples
    gz complexity distill
    gz complexity distill --corpus data/exemplar_corpus.json
    gz complexity distill --baseline-json baseline.json --no-prior
    gz complexity distill --today 2026-05-05 --allow-dated-sibling

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
[uv run -m unittest -q] stderr:
Exception in thread Thread-537 (_readerthread):
Traceback (most recent call last):
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\threading.py", line 1044, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\threading.py", line 995, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\subprocess.py", line 1615, in _readerthread
    buffer.append(fh.read())
                  ~~~~~~~^^
  File "C:\Users\Jeff\AppData\Roaming\uv\python\cpython-3.13-windows-x86_64-none\Lib\encodings\cp1252.py", line 23, in decode
    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in position 29: character maps to <undefined>
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmpina7mrj9\test_broken.py
Malformed REQ line (skipped): - [ ] REQ-X-Y-Z: Malformed (non-numeric).
Malformed REQ line (skipped): - [ ] REQ-: Empty body.
[1] metric=radon_cc value=12.0 band=block
  Archetype: long_parameter_list
  Authority: fowler (Fowler Refactoring 2e ch.3)
  Proof: src/foo.py:10-30
  Recommended move: Extract Parameter Object
[1] metric=radon_cc value=12.0 band=warn
  Archetype: long_parameter_list
  Authority: fowler (Fowler Refactoring 2e ch.3)
  Proof: src/foo.py:10-30
  Recommended move: Extract Parameter Object
----------------------------------------------------------------------
Ran 4671 tests in 94.141s

OK (skipped=2)
```
## 2026-06-29T22:06:16-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.05s) -- exit 0 == 0
  - [FAIL] `uvx ty check . --exclude features` => rc=1 (0.38s) -- exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
error[unsupported-operator]: Unsupported `/` operation
   --> tests/governance/test_obpi_complete_lock_release.py:169:30
    |
169 |             self.assertTrue((root / hp).is_file())  # cited register entry exists
    |                              ----^^^--
    |                              |      |
    |                              |      Has type `str | None`
    |                              Has type `Path`
    |

Found 1 diagnostic
```
## 2026-06-30T02:46:24-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.04s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.41s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (82.66s) -- exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stderr:
[1/1] Test
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:131: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
WARNING [rendition-floor-coherence, staged warn]: Committed rendition 'AGENTS.md/claude' omits 1 invariant-tier corpus entry (corpus-tty); the rendition does not satisfy canon's invariant floor (the canon->rendition seam ADR-0.0.37 requires). Recompose with a candidate that includes every invariant-tier entry verbatim: `gz content compose AGENTS.md`, attest the candidate, then recommit the rendition.
WARNING [rendition-freshness, staged warn]: No provenance sidecar (claude.corpus.json) for 'AGENTS.md'/'claude': the committed rendition can no longer be proven to derive from the current corpus (ADR-0.0.37 § Re-Alignment; rendition-freshness gate, OBPI-0.0.37-22 REQ-03). Recompose and re-attest: `gz content compose AGENTS.md --consumer claude` then `gz content commit AGENTS.md --consumer claude --attestor <you> --attestation-text <verbatim>`.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'OBPI-0.0.37-07-test.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
----------------------------------------------------------------------
Ran 6660 tests in 81.954s

OK
```
## 2026-07-07T05:47:41-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.07s) -- exit 0 == 0
  - [FAIL] `uvx ty check . --exclude features` => rc=1 (0.43s) -- exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
error[missing-argument]: No argument provided for required parameter `provenance`
  --> tests/test_ontology_model.py:60:13
   |
60 | /             OntologyEdge(
61 | |                 source_id="a",
62 | |                 target_id="b",
63 | |                 link_type=LinkType.PARENT,
64 | |                 bogus=1,  # type: ignore[call-arg]
65 | |             )
   | |_____________^
   |

error[missing-argument]: No argument provided for required parameter `provenance`
  --> tests/test_ontology_model.py:90:13
   |
90 |             OntologyEdge(source_id="a", target_id="b", link_type=LinkType.CHILD)
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |

error[missing-argument]: No argument provided for required parameter `ownership`
   --> tests/test_ontology_model.py:128:13
    |
128 |             OntologyNode(node_id="n1", object_type=ObjectType.ADR, plane=Plane.PRODUCT)  # type: ignore[call-arg]
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |

error[missing-argument]: No argument provided for required parameter `plane`
   --> tests/test_ontology_model.py:133:13
    |
133 |             OntologyNode(node_id="n1", object_type=ObjectType.ADR, ownership=Ownership.HARNESS)  # type: ignore[call-arg]
    |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |

Found 4 diagnostics
```
## 2026-07-07T06:35:27-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.04s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.35s) -- exit 0 == 0
  - [FAIL] `uv run -m unittest -q` => rc=1 (83.18s) -- exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stderr:
[1/1] Test
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:131: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
WARNING [rendition-floor-coherence, staged warn]: Committed rendition 'AGENTS.md/claude' omits 1 invariant-tier corpus entry (corpus-tty); the rendition does not satisfy canon's invariant floor (the canon->rendition seam ADR-0.0.37 requires). Recompose with a candidate that includes every invariant-tier entry verbatim: `gz content compose AGENTS.md`, attest the candidate, then recommit the rendition.
WARNING [rendition-freshness, staged warn]: No provenance sidecar (claude.corpus.json) for 'AGENTS.md'/'claude': the committed rendition can no longer be proven to derive from the current corpus (ADR-0.0.37 § Re-Alignment; rendition-freshness gate, OBPI-0.0.37-22 REQ-03). Recompose and re-attest: `gz content compose AGENTS.md --consumer claude` then `gz content commit AGENTS.md --consumer claude --attestor <you> --attestation-text <verbatim>`.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'OBPI-0.0.37-07-test.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
======================================================================
FAIL: test_no_new_deps_shell_true_or_dataclass (tests.governance.test_agent_contract_fold.TestAgentContractFold.test_no_new_deps_shell_true_or_dataclass)
REQ 13: OBPI-02 introduces no stdlib ``dataclass``, no ``shell=True``,
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py", line 356, in test_no_new_deps_shell_true_or_dataclass
    self.assertFalse(
    ~~~~~~~~~~~~~~~~^
        non_conforming,
        ^^^^^^^^^^^^^^^
        f"OBPI-02 may not introduce new imports: {non_conforming!r}",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: ['import subprocess'] is not false : OBPI-02 may not introduce new imports: ['import subprocess']

----------------------------------------------------------------------
Ran 6808 tests in 82.610s

FAILED (failures=1)
```
## 2026-07-07T06:42:29-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.04s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.37s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (78.16s) -- exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stderr:
[1/1] Test
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:131: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
WARNING [rendition-floor-coherence, staged warn]: Committed rendition 'AGENTS.md/claude' omits 1 invariant-tier corpus entry (corpus-tty); the rendition does not satisfy canon's invariant floor (the canon->rendition seam ADR-0.0.37 requires). Recompose with a candidate that includes every invariant-tier entry verbatim: `gz content compose AGENTS.md`, attest the candidate, then recommit the rendition.
WARNING [rendition-freshness, staged warn]: No provenance sidecar (claude.corpus.json) for 'AGENTS.md'/'claude': the committed rendition can no longer be proven to derive from the current corpus (ADR-0.0.37 § Re-Alignment; rendition-freshness gate, OBPI-0.0.37-22 REQ-03). Recompose and re-attest: `gz content compose AGENTS.md --consumer claude` then `gz content commit AGENTS.md --consumer claude --attestor <you> --attestation-text <verbatim>`.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:376: DeprecationWarning: Brief 'OBPI-0.0.37-07-test.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
----------------------------------------------------------------------
Ran 6808 tests in 77.613s

OK
```
## 2026-07-31T18:41:45-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.06s) -- exit 0 == 0
  - [FAIL] `uvx ty check . --exclude features` => rc=1 (0.50s) -- exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
error[invalid-argument-type]: Argument is incorrect
   --> scripts/migrate_brief_frontmatter.py:136:24
    |
136 |         BriefStructure(**{k: v for k, v in candidate.items() if k in BriefStructure.model_fields})
    |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Expected `Literal["Lite", "Heavy"]`, found `Unknown | list[Unknown]`
    |
info: element `list[Unknown]` of union `Unknown | list[Unknown]` is not assignable to `Literal["Lite", "Heavy"]`

error[invalid-argument-type]: Argument is incorrect
   --> scripts/migrate_brief_frontmatter.py:136:24
    |
136 |         BriefStructure(**{k: v for k, v in candidate.items() if k in BriefStructure.model_fields})
    |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Expected `str`, found `Unknown | list[Unknown]`
    |
info: element `list[Unknown]` of union `Unknown | list[Unknown]` is not assignable to `str`

error[invalid-argument-type]: Argument is incorrect
   --> scripts/migrate_brief_frontmatter.py:136:24
    |
136 |         BriefStructure(**{k: v for k, v in candidate.items() if k in BriefStructure.model_fields})
    |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Expected `str`, found `Unknown | list[Unknown]`
    |
info: element `list[Unknown]` of union `Unknown | list[Unknown]` is not assignable to `str`

error[invalid-argument-type]: Argument is incorrect
   --> scripts/migrate_brief_frontmatter.py:136:24
    |
136 |         BriefStructure(**{k: v for k, v in candidate.items() if k in BriefStructure.model_fields})
    |                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Expected `str`, found `Unknown | list[Unknown]`
    |
info: element `list[Unknown]` of union `Unknown | list[Unknown]` is not assignable to `str`

warning[unused-ignore-comment]: Unused blanket `ty: ignore` directive
  --> tests/test_adversarial_validation_event.py:49:60
   |
49 |                 self.assertEqual(parsed.verdict, verdict)  # ty: ignore
   |                                                            ^^^^^^^^^^^^
   |
help: Remove the unused suppression comment
   |
48 |                 parsed = parse_typed_event(_event(verdict=verdict))
   -                 self.assertEqual(parsed.verdict, verdict)  # ty: ignore
49 +                 self.assertEqual(parsed.verdict, verdict)
50 |
   |

warning[unused-ignore-comment]: Unused blanket `ty: ignore` directive
  --> tests/test_adversarial_validation_gate.py:39:48
   |
39 |     _enforce_adversarial_validation(**kwargs)  # ty: ignore
   |                                                ^^^^^^^^^^^^
   |
help: Remove the unused suppression comment
   |
38 |     kwargs.update(overrides)
   -     _enforce_adversarial_validation(**kwargs)  # ty: ignore
39 +     _enforce_adversarial_validation(**kwargs)
40 |
   |

error[invalid-assignment]: Object of type `((unaccounted, override) -> Unknown) | ((_u, _o) -> Decision)` is not assignable to attribute `_decide` of type `def _decide(unaccounted: tuple[SeamEdge, ...], override: CaptainOverride | None) -> Decision`
   --> tests/test_airlock_enter.py:427:17
    |
427 |                 airlock_mod._decide = mutation
    |                 ^^^^^^^^^^^^^^^^^^^
    |
info: element `(unaccounted, override) -> Unknown` of union `((unaccounted, override) -> Unknown) | ((_u, _o) -> Decision)` is not assignable to `def _decide(unaccounted: tuple[SeamEdge, ...], override: CaptainOverride | None) -> Decision`

error[not-iterable]: Object of type `object` is not iterable
   --> tests/test_handoff_cli.py:101:42
    |
101 |             [row["timestamp"] for row in payload],
    |                                          ^^^^^^^
    |
info: It doesn't have an `__iter__` method or a `__getitem__` method

error[not-iterable]: Object of type `object` is not iterable
   --> tests/test_handoff_cli.py:106:58
    |
106 |             all(row["adr_id"] == "ADR-0.0.65" for row in payload),
    |                                                          ^^^^^^^
    |
info: It doesn't have an `__iter__` method or a `__getitem__` method

error[invalid-assignment]: Invalid subscript assignment with key of type `Literal["Decisions Made"]` and value of type `str` on object of type `dict[str, LiteralString]`
   --> tests/test_handoff_cli.py:270:9
    |
270 |         sections["Decisions Made"] = decisions
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^---------
    |                                      |
    |                                      Expected value of type `LiteralString`, got `str`
    |

error[invalid-assignment]: Object of type `list[tuple[TestCase, str] | tuple[None, str]]` is not assignable to attribute `failures` of type `list[tuple[TestCase, str]]`
   --> tests/test_smoke_gate.py:123:9
    |
123 |         failing.failures = [(None, "boom")]  # type: ignore[list-item]
    |         ^^^^^^^^^^^^^^^^
    |
info: element `tuple[None, str]` of union `tuple[TestCase, str] | tuple[None, str]` is not assignable to `tuple[TestCase, str]`
info: └── the first tuple element is not compatible: `None` is not assignable to `TestCase`

warning[unused-ignore-comment]: Unused blanket `ty: ignore` directive
  --> tests/test_uncovered_accept_kind_gate.py:44:48
   |
44 |     return _apply_uncovered_waivers(**kwargs)  # ty: ignore
   |                                                ^^^^^^^^^^^^
   |
help: Remove the unused suppression comment
   |
43 |     kwargs.update(overrides)
   -     return _apply_uncovered_waivers(**kwargs)  # ty: ignore
44 +     return _apply_uncovered_waivers(**kwargs)
45 |
   |

Found 12 diagnostics
```
## 2026-08-01T01:28:59-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.04s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.50s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (84.28s) -- exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stderr:
[1/1] Test
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:393: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:393: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'brief.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-01-demo.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-02-consumer.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-01-demo.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-01-selfmade.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-02-consumer.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/brief_reconcile.py:212: DeprecationWarning: Brief 'OBPI-0.9.9-02-consumer.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: argument --repair: not allowed with argument --recon
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:393: DeprecationWarning: Brief 'OBPI-0.0.65-04-x.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
/Users/jeff/Documents/Code/gzkit/src/gzkit/pipeline_runtime.py:393: DeprecationWarning: Brief 'OBPI-0.0.37-07-test.md' lacks structured frontmatter fields (allowlist, reqs, verification); loading as LegacyBriefShape. Migrate to structured frontmatter per OBPI-0.0.37-04.
  parsed = parse_brief(brief_path)
..
----------------------------------------------------------------------
Ran 2 tests in 0.008s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 0.008s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
  BLOCKER: ADR-0.0.37 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.54 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.64 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.65 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.72 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
----------------------------------------------------------------------
Ran 7704 tests in 83.387s

OK
```
