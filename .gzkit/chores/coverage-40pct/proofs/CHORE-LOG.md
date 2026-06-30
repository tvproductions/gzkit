# CHORE-LOG: coverage-40pct

## 2026-05-10T14:02:00-05:00
- Status: FAIL
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (102.80s) -- exit 0 == 0
  - [FAIL] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=124 (128.22s) -- Timed out after 120s

```text
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
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmp7v_fk0dr/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmp0kiggv8z\test_broken.py
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
Ran 4671 tests in 101.633s

OK (skipped=2)
[uv run coverage run -m unittest discover -s tests -t . -q] stdout:
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
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmpl1u2m1eq/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
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
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmp4m1fmqyx\test_broken.py
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
Ran 4671 tests in 126.309s

OK (skipped=3)
```
## 2026-05-10T18:29:06-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: medium
- Version: 1.1.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (39.45s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (39.96s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.68s) -- exit 0 == 0

```text
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
Bootstrap-mode: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpmuxlniwd/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpccktwjza/test_broken.py
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
Ran 4727 tests in 38.842s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stdout:
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
Bootstrap-mode: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpgf4mkbwu/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpc728vmdv/test_broken.py
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
Ran 4727 tests in 39.342s

OK (skipped=1)
[uv run coverage report --fail-under=40] stdout:
Name                                                              Stmts   Miss  Cover
-------------------------------------------------------------------------------------
src/gzkit/__init__.py                                                 1      0   100%
src/gzkit/__main__.py                                                 3      3     0%
src/gzkit/adapters/__init__.py                                        0      0   100%
src/gzkit/adapters/config.py                                         12      0   100%
src/gzkit/adr_eval.py                                               142     16    89%
src/gzkit/adr_eval_redteam.py                                        43      4    91%
src/gzkit/adr_eval_scoring.py                                       276     26    91%
src/gzkit/arb/__init__.py                                             7      0   100%
src/gzkit/arb/advisor.py                                            118     26    78%
src/gzkit/arb/paths.py                                               15      0   100%
src/gzkit/arb/patterns.py                                           103     10    90%
src/gzkit/arb/ruff_reporter.py                                      114     17    85%
src/gzkit/arb/step_reporter.py                                       57      9    84%
src/gzkit/arb/validator.py                                          115     16    86%
src/gzkit/chores/__init__.py                                        101      7    93%
src/gzkit/chores/eval_feedback_cluster_lib.py                       177     63    64%
src/gzkit/cli/__init__.py                                            15      1    93%
src/gzkit/cli/formatters.py                                         173     14    92%
src/gzkit/cli/helpers/__init__.py                                     4      0   100%
src/gzkit/cli/helpers/common_flags.py                                15      0   100%
src/gzkit/cli/helpers/epilog.py                                      13      0   100%
src/gzkit/cli/helpers/exit_codes.py                                  16      0   100%
src/gzkit/cli/helpers/standard_options.py                            23      0   100%
src/gzkit/cli/logging.py                                             45      1    98%
src/gzkit/cli/main.py                                                92      8    91%
src/gzkit/cli/parser.py                                              19      0   100%
src/gzkit/cli/parser_arb.py                                          60      3    95%
src/gzkit/cli/parser_artifacts.py                                   265      1    99%
src/gzkit/cli/parser_governance.py                                  157      2    99%
src/gzkit/cli/parser_maintenance.py                                 238      0   100%
src/gzkit/cli/progress.py                                            43      2    95%
src/gzkit/commands/__init__.py                                        0      0   100%
src/gzkit/commands/adr_audit.py                                     579    121    79%
src/gzkit/commands/adr_audit_covers_backfill.py                     270     37    86%
src/gzkit/commands/adr_coverage.py                                  221     44    80%
src/gzkit/commands/adr_promote.py                                   195     26    87%
src/gzkit/commands/adr_promote_utils.py                             248     51    79%
src/gzkit/commands/arb.py                                            64     20    69%
src/gzkit/commands/attest.py                                        104      8    92%
src/gzkit/commands/audit_cmd.py                                     163      7    96%
src/gzkit/commands/ceremony_data.py                                 230     19    92%
src/gzkit/commands/ceremony_intent.py                                65      1    98%
src/gzkit/commands/ceremony_steps.py                                110     27    75%
src/gzkit/commands/chores.py                                        347     71    80%
src/gzkit/commands/chores_exec.py                                   192     45    77%
src/gzkit/commands/chores_propose_ghi_cmd.py                         60      6    90%
src/gzkit/commands/cli_audit.py                                     139     33    76%
src/gzkit/commands/closeout.py                                      291     32    89%
src/gzkit/commands/closeout_ceremony.py                             257     15    94%
src/gzkit/commands/closeout_form.py                                 155     26    83%
src/gzkit/commands/common.py                                        339     46    86%
src/gzkit/commands/complexity_advise.py                             186     36    81%
src/gzkit/commands/complexity_distill_cmd.py                         70     13    81%
src/gzkit/commands/complexity_guide.py                               55     15    73%
src/gzkit/commands/config_paths.py                                  148     16    89%
src/gzkit/commands/covers.py                                         84      3    96%
src/gzkit/commands/drift.py                                          80     10    88%
src/gzkit/commands/flags.py                                          96     11    89%
src/gzkit/commands/frontmatter_reconcile.py                          49     25    49%
src/gzkit/commands/gates.py                                         199     96    52%
src/gzkit/commands/init_cmd.py                                      329     78    76%
src/gzkit/commands/interview_cmd.py                                 134    123     8%
src/gzkit/commands/issue_cmd.py                                      69      6    91%
src/gzkit/commands/justify_cmd.py                                    10      0   100%
src/gzkit/commands/obpi_audit_cmd.py                                240    197    18%
src/gzkit/commands/obpi_cmd.py                                      255     57    78%
src/gzkit/commands/obpi_complete.py                                 441     56    87%
src/gzkit/commands/obpi_lock.py                                      80     11    86%
src/gzkit/commands/obpi_lock_cmd.py                                   2      2     0%
src/gzkit/commands/obpi_precomplete.py                              149     10    93%
src/gzkit/commands/obpi_stages.py                                   215     15    93%
src/gzkit/commands/parity.py                                         54     11    80%
src/gzkit/commands/patch_release.py                                 354    133    62%
src/gzkit/commands/personas.py                                       74      7    91%
src/gzkit/commands/pipeline.py                                       93      0   100%
src/gzkit/commands/plan.py                                          121     32    74%
src/gzkit/commands/plan_audit_cmd.py                                208     15    93%
src/gzkit/commands/preflight.py                                      87     11    87%
src/gzkit/commands/quality.py                                       240    147    39%
src/gzkit/commands/readiness.py                                     152     33    78%
src/gzkit/commands/register.py                                      242     15    94%
src/gzkit/commands/roles.py                                          70     30    57%
src/gzkit/commands/skills_cmd.py                                     88      6    93%
src/gzkit/commands/specify_cmd.py                                   364     66    82%
src/gzkit/commands/state.py                                         155      6    96%
src/gzkit/commands/status.py                                        272     28    90%
src/gzkit/commands/status_obpi.py                                   218     38    83%
src/gzkit/commands/status_obpi_inspect.py                           169     19    89%
src/gzkit/commands/status_render.py                                 214     19    91%
src/gzkit/commands/sync.py                                          293    101    66%
src/gzkit/commands/task.py                                          132      7    95%
src/gzkit/commands/tidy.py                                           89     38    57%
src/gzkit/commands/validate_cmd.py                                  476    169    64%
src/gzkit/commands/validate_frontmatter.py                          151     14    91%
src/gzkit/commands/version_sync.py                                  103      2    98%
src/gzkit/complexity/__init__.py                                      5      0   100%
src/gzkit/complexity/advisor/__init__.py                              2      0   100%
src/gzkit/complexity/advisor/archetype_rules.py                     104     16    85%
src/gzkit/complexity/advisor/config.py                               13      2    85%
src/gzkit/complexity/advisor/diagnosis.py                            52      2    96%
src/gzkit/complexity/advisor/engine.py                              112      7    94%
src/gzkit/complexity/advisor/intrinsic.py                            18      0   100%
src/gzkit/complexity/advisor/presentation.py                         54      4    93%
src/gzkit/complexity/advisor/timeout.py                              73     20    73%
src/gzkit/complexity/aggregator.py                                   38      2    95%
src/gzkit/complexity/authoring/__init__.py                            0      0   100%
src/gzkit/complexity/authoring/engine.py                             69      3    96%
src/gzkit/complexity/authoring/hint.py                               28      0   100%
src/gzkit/complexity/authoring/protocol.py                          110     15    86%
src/gzkit/complexity/baseline.py                                     79      1    99%
src/gzkit/complexity/citation.py                                     19      0   100%
src/gzkit/complexity/distillation.py                                120      5    96%
src/gzkit/complexity/measurement.py                                 199     24    88%
src/gzkit/complexity/thresholds.py                                   65      7    89%
src/gzkit/config.py                                                  89      0   100%
src/gzkit/core/__init__.py                                            0      0   100%
src/gzkit/core/exceptions.py                                         30      0   100%
src/gzkit/core/lifecycle.py                                          36      0   100%
src/gzkit/core/models.py                                            133      3    98%
src/gzkit/core/scoring.py                                           195     25    87%
src/gzkit/core/validation_rules.py                                   41      0   100%
src/gzkit/decomposition.py                                            2      0   100%
src/gzkit/doc_coverage/__init__.py                                    5      0   100%
src/gzkit/doc_coverage/flag_scanner.py                               81      6    93%
src/gzkit/doc_coverage/manifest.py                                   36      1    97%
src/gzkit/doc_coverage/models.py                                     43      0   100%
src/gzkit/doc_coverage/runner.py                                     61     21    66%
src/gzkit/doc_coverage/scanner.py                                   273     29    89%
src/gzkit/eval/__init__.py                                            0      0   100%
src/gzkit/eval/datasets.py                                           87     26    70%
src/gzkit/eval/delta.py                                              76      1    99%
src/gzkit/eval/regression.py                                         97      3    97%
src/gzkit/eval/runner.py                                             47      0   100%
src/gzkit/eval/scorer.py                                            153      1    99%
src/gzkit/events.py                                                 233     23    90%
src/gzkit/flags/__init__.py                                           6      0   100%
src/gzkit/flags/decisions.py                                         17      0   100%
src/gzkit/flags/diagnostics.py                                       75      1    99%
src/gzkit/flags/models.py                                            52      0   100%
src/gzkit/flags/registry.py                                          47      2    96%
src/gzkit/flags/service.py                                           62      0   100%
src/gzkit/git_sync.py                                                93     11    88%
src/gzkit/governance/__init__.py                                      0      0   100%
src/gzkit/governance/adr_status_index.py                            137     11    92%
src/gzkit/governance/brief_path_validity.py                          90      1    99%
src/gzkit/governance/frontmatter_coherence.py                       218     36    83%
src/gzkit/governance/req_coverage.py                                 37      0   100%
src/gzkit/governance/status_vocab.py                                 14      0   100%
src/gzkit/governance/trust_audits/__init__.py                        25      0   100%
src/gzkit/governance/trust_audits/absorption_duplicates.py           55      5    91%
src/gzkit/governance/trust_audits/advisor_proof_binding.py          113     13    88%
src/gzkit/governance/trust_audits/attestation_receipts.py            85      3    96%
src/gzkit/governance/trust_audits/briefs.py                         211     20    91%
src/gzkit/governance/trust_audits/chores.py                          41      3    93%
src/gzkit/governance/trust_audits/cli.py                             84      8    90%
src/gzkit/governance/trust_audits/code_quality.py                    74     13    82%
src/gzkit/governance/trust_audits/complexity_doctrine_links.py      115     14    88%
src/gzkit/governance/trust_audits/complexity_thresholds.py           47      4    91%
src/gzkit/governance/trust_audits/cross_platform.py                  99      4    96%
src/gzkit/governance/trust_audits/doc_surface_parity.py              15      0   100%
src/gzkit/governance/trust_audits/evaluation_justify_binding.py      58      5    91%
src/gzkit/governance/trust_audits/events.py                         135      9    93%
src/gzkit/governance/trust_audits/insights.py                        37      1    97%
src/gzkit/governance/trust_audits/instructions_files_budget.py       37      0   100%
src/gzkit/governance/trust_audits/intrinsic_attestation.py           33      3    91%
src/gzkit/governance/trust_audits/models.py                          71     13    82%
src/gzkit/governance/trust_audits/orientation.py                    125     15    88%
src/gzkit/governance/trust_audits/orphaned_implementation.py        146     10    93%
src/gzkit/governance/trust_audits/reconcile.py                       49     17    65%
src/gzkit/governance/trust_audits/release.py                         46      8    83%
src/gzkit/governance/trust_audits/sensitivity.py                    115     14    88%
src/gzkit/governance/trust_audits/taxonomy.py                       118     17    86%
src/gzkit/handoff_validation.py                                     135      2    99%
src/gzkit/hooks/__init__.py                                           3      0   100%
src/gzkit/hooks/claude.py                                           124      6    95%
src/gzkit/hooks/copilot.py                                           19      1    95%
src/gzkit/hooks/core.py                                             173     42    76%
src/gzkit/hooks/guards.py                                           119      5    96%
src/gzkit/hooks/install_complexity_advisor.py                       145     44    70%
src/gzkit/hooks/obpi.py                                             392     26    93%
src/gzkit/hooks/scripts/__init__.py                                   0      0   100%
src/gzkit/hooks/scripts/ghi.py                                        2      0   100%
src/gzkit/hooks/scripts/pipeline.py                                   4      0   100%
src/gzkit/hooks/scripts/quality.py                                    2      0   100%
src/gzkit/hooks/scripts/routing.py                                    4      0   100%
src/gzkit/hooks/scripts/validation.py                                 4      0   100%
src/gzkit/insights/__init__.py                                        2      0   100%
src/gzkit/insights/model.py                                          19      0   100%
src/gzkit/instruction_audit.py                                      125      7    94%
src/gzkit/instruction_eval.py                                       141     17    88%
src/gzkit/interview.py                                              111     29    74%
src/gzkit/justify/__init__.py                                         6      0   100%
src/gzkit/justify/anchors.py                                         53      4    92%
src/gzkit/justify/cli.py                                            105     10    90%
src/gzkit/justify/complexity_hints.py                                71     56    21%
src/gzkit/justify/evidence.py                                       204     39    81%
src/gzkit/justify/models.py                                          48      0   100%
src/gzkit/justify/parser.py                                         166     13    92%
src/gzkit/justify/templates/__init__.py                               0      0   100%
src/gzkit/justify/walkthrough.py                                     96      0   100%
src/gzkit/ledger.py                                                 407     21    95%
src/gzkit/ledger_events.py                                           86      1    99%
src/gzkit/ledger_proof.py                                            50      8    84%
src/gzkit/ledger_semantics.py                                       208     19    91%
src/gzkit/lifecycle.py                                               29      2    93%
src/gzkit/lock_manager.py                                            97      2    98%
src/gzkit/models/__init__.py                                          3      0   100%
src/gzkit/models/exemplar.py                                         41      0   100%
src/gzkit/models/frontmatter.py                                       2      0   100%
src/gzkit/models/persona.py                                          76      2    97%
src/gzkit/models/security_surfaces.py                                47      2    96%
src/gzkit/personas.py                                               233     26    89%
src/gzkit/pipeline_dispatch.py                                      222      2    99%
src/gzkit/pipeline_markers.py                                       366     47    87%
src/gzkit/pipeline_runtime.py                                       138      5    96%
src/gzkit/pipeline_verification.py                                  145      1    99%
src/gzkit/ports/__init__.py                                           2      0   100%
src/gzkit/ports/interfaces.py                                        24      9    62%
src/gzkit/quality.py                                                428     51    88%
src/gzkit/registry.py                                                57      0   100%
src/gzkit/reporter/__init__.py                                        3      0   100%
src/gzkit/reporter/panels.py                                         14      0   100%
src/gzkit/reporter/presets.py                                        63      2    97%
src/gzkit/roles.py                                                   79      1    99%
src/gzkit/rules.py                                                  271     21    92%
src/gzkit/scan/__init__.py                                            0      0   100%
src/gzkit/scan/mapping.py                                            17      3    82%
src/gzkit/scan/models.py                                             80      8    90%
src/gzkit/schemas/__init__.py                                        12      0   100%
src/gzkit/skill_contract.py                                           2      0   100%
src/gzkit/skills.py                                                 136     23    83%
src/gzkit/skills_audit.py                                           224     46    79%
src/gzkit/skills_mirror.py                                           95      6    94%
src/gzkit/sync.py                                                   152      6    96%
src/gzkit/sync_skill_validation.py                                  159     29    82%
src/gzkit/sync_skills.py                                            277     36    87%
src/gzkit/sync_skills_validation.py                                 130    130     0%
src/gzkit/sync_surfaces.py                                          212     14    93%
src/gzkit/tasks.py                                                   92      2    98%
src/gzkit/templates/__init__.py                                      28      2    93%
src/gzkit/temporal_drift.py                                         132      9    93%
src/gzkit/traceability.py                                           321     29    91%
src/gzkit/triangle.py                                               164      5    97%
src/gzkit/utils.py                                                   59     10    83%
src/gzkit/validate.py                                                40     22    45%
src/gzkit/validate_pkg/__init__.py                                    0      0   100%
src/gzkit/validate_pkg/document.py                                   78     25    68%
src/gzkit/validate_pkg/ledger_check.py                              132     29    78%
src/gzkit/validate_pkg/manifest.py                                   36      8    78%
src/gzkit/validate_pkg/surface.py                                   106     19    82%
src/gzkit/validate_pkg/sync_parity.py                               136     32    76%
src/gzkit/validators/__init__.py                                      0      0   100%
src/gzkit/validators/unscoped_rules.py                              136      8    94%
-------------------------------------------------------------------------------------
TOTAL                                                             27781   4123    85%
```
## 2026-05-10T18:47:11-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (39.40s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (39.43s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.66s) -- exit 0 == 0

```text
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
Bootstrap-mode: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmps1_m3xd3/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpsmuwc8cn/test_broken.py
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
Ran 4728 tests in 38.875s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stdout:
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
Bootstrap-mode: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpc8nzdxbh/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpwh91xff3/test_broken.py
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
Ran 4728 tests in 38.865s

OK (skipped=1)
[uv run coverage report --fail-under=40] stdout:
Name                                                              Stmts   Miss  Cover
-------------------------------------------------------------------------------------
src/gzkit/__init__.py                                                 1      0   100%
src/gzkit/__main__.py                                                 3      3     0%
src/gzkit/adapters/__init__.py                                        0      0   100%
src/gzkit/adapters/config.py                                         12      0   100%
src/gzkit/adr_eval.py                                               142     16    89%
src/gzkit/adr_eval_redteam.py                                        43      4    91%
src/gzkit/adr_eval_scoring.py                                       276     26    91%
src/gzkit/arb/__init__.py                                             7      0   100%
src/gzkit/arb/advisor.py                                            118     26    78%
src/gzkit/arb/paths.py                                               15      0   100%
src/gzkit/arb/patterns.py                                           103     10    90%
src/gzkit/arb/ruff_reporter.py                                      114     17    85%
src/gzkit/arb/step_reporter.py                                       57      9    84%
src/gzkit/arb/validator.py                                          115     16    86%
src/gzkit/chores/__init__.py                                        101      7    93%
src/gzkit/chores/eval_feedback_cluster_lib.py                       177     63    64%
src/gzkit/cli/__init__.py                                            15      1    93%
src/gzkit/cli/formatters.py                                         173     14    92%
src/gzkit/cli/helpers/__init__.py                                     4      0   100%
src/gzkit/cli/helpers/common_flags.py                                15      0   100%
src/gzkit/cli/helpers/epilog.py                                      13      0   100%
src/gzkit/cli/helpers/exit_codes.py                                  16      0   100%
src/gzkit/cli/helpers/standard_options.py                            23      0   100%
src/gzkit/cli/logging.py                                             45      1    98%
src/gzkit/cli/main.py                                                92      8    91%
src/gzkit/cli/parser.py                                              19      0   100%
src/gzkit/cli/parser_arb.py                                          60      3    95%
src/gzkit/cli/parser_artifacts.py                                   265      1    99%
src/gzkit/cli/parser_governance.py                                  157      2    99%
src/gzkit/cli/parser_maintenance.py                                 238      0   100%
src/gzkit/cli/progress.py                                            43      2    95%
src/gzkit/commands/__init__.py                                        0      0   100%
src/gzkit/commands/adr_audit.py                                     579    121    79%
src/gzkit/commands/adr_audit_covers_backfill.py                     270     37    86%
src/gzkit/commands/adr_coverage.py                                  221     44    80%
src/gzkit/commands/adr_promote.py                                   195     26    87%
src/gzkit/commands/adr_promote_utils.py                             248     51    79%
src/gzkit/commands/arb.py                                            64     20    69%
src/gzkit/commands/attest.py                                        104      8    92%
src/gzkit/commands/audit_cmd.py                                     163      7    96%
src/gzkit/commands/ceremony_data.py                                 230     19    92%
src/gzkit/commands/ceremony_intent.py                                65      1    98%
src/gzkit/commands/ceremony_steps.py                                110     27    75%
src/gzkit/commands/chores.py                                        338     71    79%
src/gzkit/commands/chores_exec.py                                   196     43    78%
src/gzkit/commands/chores_propose_ghi_cmd.py                         60      6    90%
src/gzkit/commands/cli_audit.py                                     139     33    76%
src/gzkit/commands/closeout.py                                      291     32    89%
src/gzkit/commands/closeout_ceremony.py                             257     15    94%
src/gzkit/commands/closeout_form.py                                 155     26    83%
src/gzkit/commands/common.py                                        339     46    86%
src/gzkit/commands/complexity_advise.py                             186     36    81%
src/gzkit/commands/complexity_distill_cmd.py                         70     13    81%
src/gzkit/commands/complexity_guide.py                               55     15    73%
src/gzkit/commands/config_paths.py                                  148     16    89%
src/gzkit/commands/covers.py                                         84      3    96%
src/gzkit/commands/drift.py                                          80     10    88%
src/gzkit/commands/flags.py                                          96     11    89%
src/gzkit/commands/frontmatter_reconcile.py                          49     25    49%
src/gzkit/commands/gates.py                                         199     96    52%
src/gzkit/commands/init_cmd.py                                      329     78    76%
src/gzkit/commands/interview_cmd.py                                 134    123     8%
src/gzkit/commands/issue_cmd.py                                      69      6    91%
src/gzkit/commands/justify_cmd.py                                    10      0   100%
src/gzkit/commands/obpi_audit_cmd.py                                240    197    18%
src/gzkit/commands/obpi_cmd.py                                      255     57    78%
src/gzkit/commands/obpi_complete.py                                 441     56    87%
src/gzkit/commands/obpi_lock.py                                      80     11    86%
src/gzkit/commands/obpi_lock_cmd.py                                   2      2     0%
src/gzkit/commands/obpi_precomplete.py                              149     10    93%
src/gzkit/commands/obpi_stages.py                                   215     15    93%
src/gzkit/commands/parity.py                                         54     11    80%
src/gzkit/commands/patch_release.py                                 354    133    62%
src/gzkit/commands/personas.py                                       74      7    91%
src/gzkit/commands/pipeline.py                                       93      0   100%
src/gzkit/commands/plan.py                                          121     32    74%
src/gzkit/commands/plan_audit_cmd.py                                208     15    93%
src/gzkit/commands/preflight.py                                      87     11    87%
src/gzkit/commands/quality.py                                       240    147    39%
src/gzkit/commands/readiness.py                                     152     33    78%
src/gzkit/commands/register.py                                      242     15    94%
src/gzkit/commands/roles.py                                          70     30    57%
src/gzkit/commands/skills_cmd.py                                     88      6    93%
src/gzkit/commands/specify_cmd.py                                   364     66    82%
src/gzkit/commands/state.py                                         155      6    96%
src/gzkit/commands/status.py                                        272     28    90%
src/gzkit/commands/status_obpi.py                                   218     38    83%
src/gzkit/commands/status_obpi_inspect.py                           169     19    89%
src/gzkit/commands/status_render.py                                 214     19    91%
src/gzkit/commands/sync.py                                          293    101    66%
src/gzkit/commands/task.py                                          132      7    95%
src/gzkit/commands/tidy.py                                           89     38    57%
src/gzkit/commands/validate_cmd.py                                  476    169    64%
src/gzkit/commands/validate_frontmatter.py                          151     14    91%
src/gzkit/commands/version_sync.py                                  103      2    98%
src/gzkit/complexity/__init__.py                                      5      0   100%
src/gzkit/complexity/advisor/__init__.py                              2      0   100%
src/gzkit/complexity/advisor/archetype_rules.py                     104     16    85%
src/gzkit/complexity/advisor/config.py                               13      2    85%
src/gzkit/complexity/advisor/diagnosis.py                            52      2    96%
src/gzkit/complexity/advisor/engine.py                              112      7    94%
src/gzkit/complexity/advisor/intrinsic.py                            18      0   100%
src/gzkit/complexity/advisor/presentation.py                         54      4    93%
src/gzkit/complexity/advisor/timeout.py                              73     20    73%
src/gzkit/complexity/aggregator.py                                   38      2    95%
src/gzkit/complexity/authoring/__init__.py                            0      0   100%
src/gzkit/complexity/authoring/engine.py                             69      3    96%
src/gzkit/complexity/authoring/hint.py                               28      0   100%
src/gzkit/complexity/authoring/protocol.py                          110     15    86%
src/gzkit/complexity/baseline.py                                     79      1    99%
src/gzkit/complexity/citation.py                                     19      0   100%
src/gzkit/complexity/distillation.py                                120      5    96%
src/gzkit/complexity/measurement.py                                 199     24    88%
src/gzkit/complexity/thresholds.py                                   65      7    89%
src/gzkit/config.py                                                  89      0   100%
src/gzkit/core/__init__.py                                            0      0   100%
src/gzkit/core/exceptions.py                                         30      0   100%
src/gzkit/core/lifecycle.py                                          36      0   100%
src/gzkit/core/models.py                                            133      3    98%
src/gzkit/core/scoring.py                                           195     25    87%
src/gzkit/core/validation_rules.py                                   41      0   100%
src/gzkit/decomposition.py                                            2      0   100%
src/gzkit/doc_coverage/__init__.py                                    5      0   100%
src/gzkit/doc_coverage/flag_scanner.py                               81      6    93%
src/gzkit/doc_coverage/manifest.py                                   36      1    97%
src/gzkit/doc_coverage/models.py                                     43      0   100%
src/gzkit/doc_coverage/runner.py                                     61     21    66%
src/gzkit/doc_coverage/scanner.py                                   273     29    89%
src/gzkit/eval/__init__.py                                            0      0   100%
src/gzkit/eval/datasets.py                                           87     26    70%
src/gzkit/eval/delta.py                                              76      1    99%
src/gzkit/eval/regression.py                                         97      3    97%
src/gzkit/eval/runner.py                                             47      0   100%
src/gzkit/eval/scorer.py                                            153      1    99%
src/gzkit/events.py                                                 233     23    90%
src/gzkit/flags/__init__.py                                           6      0   100%
src/gzkit/flags/decisions.py                                         17      0   100%
src/gzkit/flags/diagnostics.py                                       75      1    99%
src/gzkit/flags/models.py                                            52      0   100%
src/gzkit/flags/registry.py                                          47      2    96%
src/gzkit/flags/service.py                                           62      0   100%
src/gzkit/git_sync.py                                                93     11    88%
src/gzkit/governance/__init__.py                                      0      0   100%
src/gzkit/governance/adr_status_index.py                            137     11    92%
src/gzkit/governance/brief_path_validity.py                          90      1    99%
src/gzkit/governance/frontmatter_coherence.py                       218     36    83%
src/gzkit/governance/req_coverage.py                                 37      0   100%
src/gzkit/governance/status_vocab.py                                 14      0   100%
src/gzkit/governance/trust_audits/__init__.py                        25      0   100%
src/gzkit/governance/trust_audits/absorption_duplicates.py           55      5    91%
src/gzkit/governance/trust_audits/advisor_proof_binding.py          113     13    88%
src/gzkit/governance/trust_audits/attestation_receipts.py            85      3    96%
src/gzkit/governance/trust_audits/briefs.py                         211     20    91%
src/gzkit/governance/trust_audits/chores.py                          41      3    93%
src/gzkit/governance/trust_audits/cli.py                             84      8    90%
src/gzkit/governance/trust_audits/code_quality.py                    74     13    82%
src/gzkit/governance/trust_audits/complexity_doctrine_links.py      115     14    88%
src/gzkit/governance/trust_audits/complexity_thresholds.py           47      4    91%
src/gzkit/governance/trust_audits/cross_platform.py                  99      4    96%
src/gzkit/governance/trust_audits/doc_surface_parity.py              15      0   100%
src/gzkit/governance/trust_audits/evaluation_justify_binding.py      58      5    91%
src/gzkit/governance/trust_audits/events.py                         135      9    93%
src/gzkit/governance/trust_audits/insights.py                        37      1    97%
src/gzkit/governance/trust_audits/instructions_files_budget.py       37      0   100%
src/gzkit/governance/trust_audits/intrinsic_attestation.py           33      3    91%
src/gzkit/governance/trust_audits/models.py                          71     13    82%
src/gzkit/governance/trust_audits/orientation.py                    125     15    88%
src/gzkit/governance/trust_audits/orphaned_implementation.py        146     10    93%
src/gzkit/governance/trust_audits/reconcile.py                       49     17    65%
src/gzkit/governance/trust_audits/release.py                         46      8    83%
src/gzkit/governance/trust_audits/sensitivity.py                    115     14    88%
src/gzkit/governance/trust_audits/taxonomy.py                       118     17    86%
src/gzkit/handoff_validation.py                                     135      2    99%
src/gzkit/hooks/__init__.py                                           3      0   100%
src/gzkit/hooks/claude.py                                           124      6    95%
src/gzkit/hooks/copilot.py                                           19      1    95%
src/gzkit/hooks/core.py                                             173     42    76%
src/gzkit/hooks/guards.py                                           119      5    96%
src/gzkit/hooks/install_complexity_advisor.py                       145     44    70%
src/gzkit/hooks/obpi.py                                             392     26    93%
src/gzkit/hooks/scripts/__init__.py                                   0      0   100%
src/gzkit/hooks/scripts/ghi.py                                        2      0   100%
src/gzkit/hooks/scripts/pipeline.py                                   4      0   100%
src/gzkit/hooks/scripts/quality.py                                    2      0   100%
src/gzkit/hooks/scripts/routing.py                                    4      0   100%
src/gzkit/hooks/scripts/validation.py                                 4      0   100%
src/gzkit/insights/__init__.py                                        2      0   100%
src/gzkit/insights/model.py                                          19      0   100%
src/gzkit/instruction_audit.py                                      125      7    94%
src/gzkit/instruction_eval.py                                       141     17    88%
src/gzkit/interview.py                                              111     29    74%
src/gzkit/justify/__init__.py                                         6      0   100%
src/gzkit/justify/anchors.py                                         53      4    92%
src/gzkit/justify/cli.py                                            105     10    90%
src/gzkit/justify/complexity_hints.py                                71     56    21%
src/gzkit/justify/evidence.py                                       204     39    81%
src/gzkit/justify/models.py                                          48      0   100%
src/gzkit/justify/parser.py                                         166     13    92%
src/gzkit/justify/templates/__init__.py                               0      0   100%
src/gzkit/justify/walkthrough.py                                     96      0   100%
src/gzkit/ledger.py                                                 407     21    95%
src/gzkit/ledger_events.py                                           86      1    99%
src/gzkit/ledger_proof.py                                            50      8    84%
src/gzkit/ledger_semantics.py                                       208     19    91%
src/gzkit/lifecycle.py                                               29      2    93%
src/gzkit/lock_manager.py                                            97      2    98%
src/gzkit/models/__init__.py                                          3      0   100%
src/gzkit/models/exemplar.py                                         41      0   100%
src/gzkit/models/frontmatter.py                                       2      0   100%
src/gzkit/models/persona.py                                          76      2    97%
src/gzkit/models/security_surfaces.py                                47      2    96%
src/gzkit/personas.py                                               233     26    89%
src/gzkit/pipeline_dispatch.py                                      222      2    99%
src/gzkit/pipeline_markers.py                                       366     47    87%
src/gzkit/pipeline_runtime.py                                       138      5    96%
src/gzkit/pipeline_verification.py                                  145      1    99%
src/gzkit/ports/__init__.py                                           2      0   100%
src/gzkit/ports/interfaces.py                                        24      9    62%
src/gzkit/quality.py                                                428     51    88%
src/gzkit/registry.py                                                57      0   100%
src/gzkit/reporter/__init__.py                                        3      0   100%
src/gzkit/reporter/panels.py                                         14      0   100%
src/gzkit/reporter/presets.py                                        63      2    97%
src/gzkit/roles.py                                                   79      1    99%
src/gzkit/rules.py                                                  271     21    92%
src/gzkit/scan/__init__.py                                            0      0   100%
src/gzkit/scan/mapping.py                                            17      3    82%
src/gzkit/scan/models.py                                             80      8    90%
src/gzkit/schemas/__init__.py                                        12      0   100%
src/gzkit/skill_contract.py                                           2      0   100%
src/gzkit/skills.py                                                 136     23    83%
src/gzkit/skills_audit.py                                           224     46    79%
src/gzkit/skills_mirror.py                                           95      6    94%
src/gzkit/sync.py                                                   152      6    96%
src/gzkit/sync_skill_validation.py                                  159     29    82%
src/gzkit/sync_skills.py                                            277     36    87%
src/gzkit/sync_skills_validation.py                                 130    130     0%
src/gzkit/sync_surfaces.py                                          212     14    93%
src/gzkit/tasks.py                                                   92      2    98%
src/gzkit/templates/__init__.py                                      28      2    93%
src/gzkit/temporal_drift.py                                         132      9    93%
src/gzkit/traceability.py                                           321     29    91%
src/gzkit/triangle.py                                               164      5    97%
src/gzkit/utils.py                                                   59     10    83%
src/gzkit/validate.py                                                40     22    45%
src/gzkit/validate_pkg/__init__.py                                    0      0   100%
src/gzkit/validate_pkg/document.py                                   78     25    68%
src/gzkit/validate_pkg/ledger_check.py                              132     29    78%
src/gzkit/validate_pkg/manifest.py                                   36      8    78%
src/gzkit/validate_pkg/surface.py                                   106     19    82%
src/gzkit/validate_pkg/sync_parity.py                               136     32    76%
src/gzkit/validators/__init__.py                                      0      0   100%
src/gzkit/validators/unscoped_rules.py                              136      8    94%
-------------------------------------------------------------------------------------
TOTAL                                                             27776   4121    85%
```
## 2026-06-29T21:52:15-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (81.47s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (112.69s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.86s) -- exit 0 == 0

```text
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
Ran 6660 tests in 80.956s

OK
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
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
Ran 6660 tests in 111.902s

OK
[uv run coverage report --fail-under=40] stdout:
Name                                                                Stmts   Miss  Cover
---------------------------------------------------------------------------------------
src/gzkit/__init__.py                                                   1      0   100%
src/gzkit/__main__.py                                                   3      3     0%
src/gzkit/adapters/__init__.py                                          0      0   100%
src/gzkit/adapters/config.py                                           12      0   100%
src/gzkit/adr_eval.py                                                 163     16    90%
src/gzkit/adr_eval_redteam.py                                          43      4    91%
src/gzkit/adr_eval_scoring.py                                         294     25    91%
src/gzkit/adr_eval_substance.py                                        57      5    91%
src/gzkit/arb/__init__.py                                               7      0   100%
src/gzkit/arb/advisor.py                                              118     26    78%
src/gzkit/arb/paths.py                                                 15      0   100%
src/gzkit/arb/patterns.py                                             103     10    90%
src/gzkit/arb/ruff_reporter.py                                        114     17    85%
src/gzkit/arb/step_reporter.py                                         57      9    84%
src/gzkit/arb/validator.py                                            115     16    86%
src/gzkit/brief_commands.py                                            71      5    93%
src/gzkit/chores/__init__.py                                          122     14    89%
src/gzkit/chores/control-surface-rule-conflicts/check_evidence.py     213     59    72%
src/gzkit/chores/eval_feedback_cluster_lib.py                         177     63    64%
src/gzkit/cli/__init__.py                                              15      1    93%
src/gzkit/cli/formatters.py                                           173     14    92%
src/gzkit/cli/helpers/__init__.py                                       4      0   100%
src/gzkit/cli/helpers/common_flags.py                                  15      0   100%
src/gzkit/cli/helpers/epilog.py                                        13      0   100%
src/gzkit/cli/helpers/exit_codes.py                                    16      0   100%
src/gzkit/cli/helpers/standard_options.py                              23      0   100%
src/gzkit/cli/logging.py                                               45      1    98%
src/gzkit/cli/main.py                                                  94      8    91%
src/gzkit/cli/parser.py                                                19      0   100%
src/gzkit/cli/parser_arb.py                                            60      3    95%
src/gzkit/cli/parser_artifacts.py                                     329      3    99%
src/gzkit/cli/parser_governance.py                                    170      8    95%
src/gzkit/cli/parser_handler_manifest.py                               14      0   100%
src/gzkit/cli/parser_maintenance.py                                   258      0   100%
src/gzkit/cli/progress.py                                              43      2    95%
src/gzkit/commands/__init__.py                                          0      0   100%
src/gzkit/commands/adr_audit.py                                       588    120    80%
src/gzkit/commands/adr_audit_covers_backfill.py                       325     41    87%
src/gzkit/commands/adr_coverage.py                                    221     44    80%
src/gzkit/commands/adr_demote.py                                      201     23    89%
src/gzkit/commands/adr_fidelity.py                                     38     33    13%
src/gzkit/commands/adr_promote.py                                     198     26    87%
src/gzkit/commands/adr_promote_utils.py                               248     51    79%
src/gzkit/commands/arb.py                                              64     20    69%
src/gzkit/commands/attest.py                                          104      8    92%
src/gzkit/commands/audit_cmd.py                                       165      7    96%
src/gzkit/commands/brief_reconcile.py                                  59      6    90%
src/gzkit/commands/ceremony_data.py                                   224     60    73%
src/gzkit/commands/ceremony_intent.py                                  65      1    98%
src/gzkit/commands/ceremony_state.py                                   92      2    98%
src/gzkit/commands/ceremony_steps.py                                  112     27    76%
src/gzkit/commands/chores.py                                          338     71    79%
src/gzkit/commands/chores_exec.py                                     196     43    78%
src/gzkit/commands/chores_propose_ghi_cmd.py                           60      6    90%
src/gzkit/commands/cli_audit.py                                       139     33    76%
src/gzkit/commands/closeout.py                                        300     32    89%
src/gzkit/commands/closeout_ceremony.py                               209     14    93%
src/gzkit/commands/closeout_form.py                                   155     26    83%
src/gzkit/commands/common.py                                          339     46    86%
src/gzkit/commands/complexity_advise.py                               186     36    81%
src/gzkit/commands/complexity_distill_cmd.py                           70     13    81%
src/gzkit/commands/complexity_guide.py                                 55     15    73%
src/gzkit/commands/config_paths.py                                    151     16    89%
src/gzkit/commands/content/__init__.py                                 83      0   100%
src/gzkit/commands/content/advise_rendition.py                         20      3    85%
src/gzkit/commands/content/commit.py                                   38     10    74%
src/gzkit/commands/content/compose.py                                  34      7    79%
src/gzkit/commands/content/edit.py                                     85     31    64%
src/gzkit/commands/content/import_.py                                  34      6    82%
src/gzkit/commands/content/list.py                                     27      5    81%
src/gzkit/commands/content/remember.py                                 52     13    75%
src/gzkit/commands/content/render.py                                   33     16    52%
src/gzkit/commands/content/show.py                                     72     28    61%
src/gzkit/commands/context_cmd.py                                     102      5    95%
src/gzkit/commands/covers.py                                          107      4    96%
src/gzkit/commands/drift.py                                            80     10    88%
src/gzkit/commands/flags.py                                            96     11    89%
src/gzkit/commands/frontmatter_reconcile.py                            49     25    49%
src/gzkit/commands/gates.py                                           199     81    59%
src/gzkit/commands/governance_render.py                                34      1    97%
src/gzkit/commands/init_cmd.py                                        456    139    70%
src/gzkit/commands/interview_cmd.py                                   135     73    46%
src/gzkit/commands/issue_cmd.py                                        69      6    91%
src/gzkit/commands/justify_cmd.py                                      10      0   100%
src/gzkit/commands/knowledge.py                                        11      2    82%
src/gzkit/commands/mx_cmd.py                                           76     12    84%
src/gzkit/commands/obpi_audit_cmd.py                                  258    101    61%
src/gzkit/commands/obpi_cmd.py                                        315     54    83%
src/gzkit/commands/obpi_complete.py                                   539     66    88%
src/gzkit/commands/obpi_lock.py                                       138     21    85%
src/gzkit/commands/obpi_lock_cmd.py                                     2      2     0%
src/gzkit/commands/obpi_precomplete.py                                163      9    94%
src/gzkit/commands/obpi_present_evidence.py                            39     32    18%
src/gzkit/commands/obpi_stages.py                                     215     25    88%
src/gzkit/commands/parity.py                                           54     11    80%
src/gzkit/commands/patch_release.py                                   417    143    66%
src/gzkit/commands/personas.py                                         74      7    91%
src/gzkit/commands/pipeline.py                                         93      0   100%
src/gzkit/commands/plan.py                                            137     28    80%
src/gzkit/commands/plan_audit_cmd.py                                  211     15    93%
src/gzkit/commands/preflight.py                                        90     11    88%
src/gzkit/commands/quality.py                                         253    132    48%
src/gzkit/commands/readiness.py                                       152     33    78%
src/gzkit/commands/register.py                                        242     15    94%
src/gzkit/commands/roles.py                                            70     30    57%
src/gzkit/commands/skills_cmd.py                                       88      6    93%
src/gzkit/commands/specify_cmd.py                                     361     66    82%
src/gzkit/commands/state.py                                           155      6    96%
src/gzkit/commands/status.py                                          290     28    90%
src/gzkit/commands/status_obpi.py                                     227     16    93%
src/gzkit/commands/status_obpi_inspect.py                             169     19    89%
src/gzkit/commands/status_render.py                                   229     19    92%
src/gzkit/commands/sync.py                                            293    101    66%
src/gzkit/commands/task.py                                            351     90    74%
src/gzkit/commands/tidy.py                                             89     19    79%
src/gzkit/commands/upgrade.py                                          93      6    94%
src/gzkit/commands/validate_briefs.py                                  83     11    87%
src/gzkit/commands/validate_cmd.py                                    481    195    59%
src/gzkit/commands/validate_commit_trailers.py                         58      8    86%
src/gzkit/commands/validate_frontmatter.py                            150     12    92%
src/gzkit/commands/validate_req_kind.py                                88      6    93%
src/gzkit/commands/validate_task_envelope.py                          392     58    85%
src/gzkit/commands/version_sync.py                                    103      2    98%
src/gzkit/complexity/__init__.py                                        5      0   100%
src/gzkit/complexity/advisor/__init__.py                                2      0   100%
src/gzkit/complexity/advisor/archetype_rules.py                       104     16    85%
src/gzkit/complexity/advisor/config.py                                 13      2    85%
src/gzkit/complexity/advisor/diagnosis.py                              52      2    96%
src/gzkit/complexity/advisor/engine.py                                112      7    94%
src/gzkit/complexity/advisor/intrinsic.py                              19      0   100%
src/gzkit/complexity/advisor/presentation.py                           54      4    93%
src/gzkit/complexity/advisor/timeout.py                                73     20    73%
src/gzkit/complexity/aggregator.py                                     38      2    95%
src/gzkit/complexity/authoring/__init__.py                              0      0   100%
src/gzkit/complexity/authoring/engine.py                               69      3    96%
src/gzkit/complexity/authoring/hint.py                                 28      0   100%
src/gzkit/complexity/authoring/protocol.py                            110     15    86%
src/gzkit/complexity/baseline.py                                       79      1    99%
src/gzkit/complexity/citation.py                                       19      0   100%
src/gzkit/complexity/distillation.py                                  120      5    96%
src/gzkit/complexity/measurement.py                                   199     24    88%
src/gzkit/complexity/thresholds.py                                     65      7    89%
src/gzkit/config.py                                                    89      0   100%
src/gzkit/content/__init__.py                                           0      0   100%
src/gzkit/content/advisor_qc.py                                        22      0   100%
src/gzkit/content/composer.py                                          21      0   100%
src/gzkit/content/corpus_store.py                                      16      0   100%
src/gzkit/content/migration/__init__.py                                 2      0   100%
src/gzkit/content/migration/registry.py                                19      1    95%
src/gzkit/content/models/__init__.py                                   12      0   100%
src/gzkit/content/models/agent_contract.py                             19      0   100%
src/gzkit/content/models/base.py                                        4      0   100%
src/gzkit/content/models/bullet.py                                     10      0   100%
src/gzkit/content/models/chore.py                                      16      0   100%
src/gzkit/content/models/corpus.py                                     34      0   100%
src/gzkit/content/models/handoff.py                                    16      0   100%
src/gzkit/content/models/persona.py                                    14      0   100%
src/gzkit/content/models/rule.py                                       28      0   100%
src/gzkit/content/models/scenario.py                                    8      0   100%
src/gzkit/content/models/skill.py                                      16      0   100%
src/gzkit/content/parse/__init__.py                                     2      0   100%
src/gzkit/content/parse/markdown_parser.py                            276     17    94%
src/gzkit/content/render/__init__.py                                    2      0   100%
src/gzkit/content/render/pipeline.py                                   41      4    90%
src/gzkit/content/rendition.py                                         19      0   100%
src/gzkit/content/rendition_store.py                                   39      0   100%
src/gzkit/content/templates/bullet/claude.md.j2                         1      0   100%
src/gzkit/content/tier_policy.py                                        8      0   100%
src/gzkit/content/tui/__init__.py                                       5      0   100%
src/gzkit/content/tui/panels.py                                         6      0   100%
src/gzkit/content/tui/status.py                                        15      3    80%
src/gzkit/content/tui/tables.py                                        11      0   100%
src/gzkit/content/validation/__init__.py                                3      0   100%
src/gzkit/content/validation/hooks.py                                  19      0   100%
src/gzkit/content/vendors.py                                           56      6    89%
src/gzkit/core/__init__.py                                              0      0   100%
src/gzkit/core/exceptions.py                                           30      0   100%
src/gzkit/core/lifecycle.py                                            36      0   100%
src/gzkit/core/models.py                                              133      3    98%
src/gzkit/core/scoring.py                                             200     25    88%
src/gzkit/core/validation_rules.py                                     46      0   100%
src/gzkit/decomposition.py                                              2      0   100%
src/gzkit/doc_coverage/__init__.py                                      5      0   100%
src/gzkit/doc_coverage/flag_scanner.py                                 81      5    94%
src/gzkit/doc_coverage/manifest.py                                     36      1    97%
src/gzkit/doc_coverage/models.py                                       43      0   100%
src/gzkit/doc_coverage/runner.py                                       61     21    66%
src/gzkit/doc_coverage/scanner.py                                     283     27    90%
src/gzkit/enforcement.py                                              116      7    94%
src/gzkit/eval/__init__.py                                              0      0   100%
src/gzkit/eval/datasets.py                                             87     26    70%
src/gzkit/eval/delta.py                                                76      1    99%
src/gzkit/eval/regression.py                                           97      3    97%
src/gzkit/eval/runner.py                                               47      0   100%
src/gzkit/eval/scorer.py                                              153      1    99%
src/gzkit/event_evidence.py                                           146     23    84%
src/gzkit/events.py                                                   303      0   100%
src/gzkit/fidelity.py                                                  84      5    94%
src/gzkit/flags/__init__.py                                             6      0   100%
src/gzkit/flags/decisions.py                                           17      0   100%
src/gzkit/flags/diagnostics.py                                         75      1    99%
src/gzkit/flags/models.py                                              52      0   100%
src/gzkit/flags/registry.py                                            47      2    96%
src/gzkit/flags/service.py                                             62      0   100%
src/gzkit/foundation/__init__.py                                        2      0   100%
src/gzkit/foundation/rubric.py                                        157     35    78%
src/gzkit/foundation/triage.py                                         82     33    60%
src/gzkit/git_sync.py                                                  93     11    88%
src/gzkit/governance/__init__.py                                        2      0   100%
src/gzkit/governance/adr_status_index.py                              137     11    92%
src/gzkit/governance/brief_path_validity.py                            90      1    99%
src/gzkit/governance/brief_reconcile.py                               187      7    96%
src/gzkit/governance/brief_structure.py                                67      2    97%
src/gzkit/governance/compose.py                                        30     14    53%
src/gzkit/governance/events.py                                         20      2    90%
src/gzkit/governance/frontmatter_coherence.py                         218     36    83%
src/gzkit/governance/invariants.py                                     32      1    97%
src/gzkit/governance/reconcile_freshness.py                            21      0   100%
src/gzkit/governance/req_coverage.py                                   44      1    98%
src/gzkit/governance/stage4_evidence.py                               134     16    88%
src/gzkit/governance/status_vocab.py                                   31      2    94%
src/gzkit/governance/trust_audits/__init__.py                          54      0   100%
src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py               112      0   100%
src/gzkit/governance/trust_audits/_qc_negative_controls.py            166      0   100%
src/gzkit/governance/trust_audits/absorption_duplicates.py             55      5    91%
src/gzkit/governance/trust_audits/advisor_proof_binding.py            113     13    88%
src/gzkit/governance/trust_audits/agents_md_map_conformance.py        208     12    94%
src/gzkit/governance/trust_audits/attestation_receipts.py              85      3    96%
src/gzkit/governance/trust_audits/brief_reconcile.py                   47     11    77%
src/gzkit/governance/trust_audits/briefs.py                           315     27    91%
src/gzkit/governance/trust_audits/bullet_retention.py                 129      9    93%
src/gzkit/governance/trust_audits/chores.py                            52      6    88%
src/gzkit/governance/trust_audits/cli.py                              102      5    95%
src/gzkit/governance/trust_audits/closeout_proof.py                   191     26    86%
src/gzkit/governance/trust_audits/code_quality.py                      74     13    82%
src/gzkit/governance/trust_audits/complexity_doctrine_links.py        115     12    90%
src/gzkit/governance/trust_audits/complexity_thresholds.py             47      2    96%
src/gzkit/governance/trust_audits/cross_platform.py                   153      9    94%
src/gzkit/governance/trust_audits/distribution.py                     165     25    85%
src/gzkit/governance/trust_audits/doc_surface_parity.py                15      0   100%
src/gzkit/governance/trust_audits/evaluation_justify_binding.py        58      5    91%
src/gzkit/governance/trust_audits/events.py                           135      9    93%
src/gzkit/governance/trust_audits/fidelity_presence.py                 46      3    93%
src/gzkit/governance/trust_audits/insights.py                          37      1    97%
src/gzkit/governance/trust_audits/instructions_files_budget.py         37      0   100%
src/gzkit/governance/trust_audits/intrinsic_attestation.py             33      3    91%
src/gzkit/governance/trust_audits/invariant_coherence.py               25      0   100%
src/gzkit/governance/trust_audits/kind_invariance.py                   65      4    94%
src/gzkit/governance/trust_audits/lock_handoff_coupling.py            117     14    88%
src/gzkit/governance/trust_audits/models.py                            71     14    80%
src/gzkit/governance/trust_audits/okf_conformance.py                   63      5    92%
src/gzkit/governance/trust_audits/orientation.py                      139     17    88%
src/gzkit/governance/trust_audits/orphaned_implementation.py          146     11    92%
src/gzkit/governance/trust_audits/pointer_integrity.py                 66      3    95%
src/gzkit/governance/trust_audits/qc_binding.py                        59      2    97%
src/gzkit/governance/trust_audits/receipt_shape.py                    135     23    83%
src/gzkit/governance/trust_audits/reconcile.py                         49     17    65%
src/gzkit/governance/trust_audits/release.py                           46      8    83%
src/gzkit/governance/trust_audits/rendition_floor_coherence.py         40      1    98%
src/gzkit/governance/trust_audits/rendition_freshness.py               44      1    98%
src/gzkit/governance/trust_audits/router_tables.py                     40      4    90%
src/gzkit/governance/trust_audits/scenario_reachability.py            102     14    86%
src/gzkit/governance/trust_audits/sensitivity.py                      129     16    88%
src/gzkit/governance/trust_audits/session_green_gate.py                23      1    96%
src/gzkit/governance/trust_audits/setpoint_coherence.py                32      3    91%
src/gzkit/governance/trust_audits/surface_weight.py                   117     19    84%
src/gzkit/governance/trust_audits/taxonomy.py                         118     11    91%
src/gzkit/governance/trust_audits/theater_signature_scan.py            98      9    91%
src/gzkit/governance/trust_audits/vendor_manifest.py                   27      3    89%
src/gzkit/governance/trust_audits/waiver_ratchet.py                   114     14    88%
src/gzkit/handoff_validation.py                                       244     11    95%
src/gzkit/hooks/__init__.py                                             3      0   100%
src/gzkit/hooks/claude.py                                             133      5    96%
src/gzkit/hooks/copilot.py                                             19      1    95%
src/gzkit/hooks/core.py                                               173     42    76%
src/gzkit/hooks/guards.py                                             151      7    95%
src/gzkit/hooks/install_complexity_advisor.py                         145     44    70%
src/gzkit/hooks/obpi.py                                               395     26    93%
src/gzkit/hooks/scripts/__init__.py                                     0      0   100%
src/gzkit/hooks/scripts/ghi.py                                          2      0   100%
src/gzkit/hooks/scripts/mx.py                                           3      0   100%
src/gzkit/hooks/scripts/pipeline.py                                     4      0   100%
src/gzkit/hooks/scripts/quality.py                                      3      0   100%
src/gzkit/hooks/scripts/routing.py                                      4      0   100%
src/gzkit/hooks/scripts/validation.py                                   4      0   100%
src/gzkit/insights/__init__.py                                          2      0   100%
src/gzkit/insights/correction_mining.py                               121     12    90%
src/gzkit/insights/model.py                                            19      0   100%
src/gzkit/instruction_audit.py                                        125      7    94%
src/gzkit/instruction_eval.py                                         141     17    88%
src/gzkit/interview.py                                                119     20    83%
src/gzkit/justify/__init__.py                                           6      0   100%
src/gzkit/justify/anchors.py                                           53      4    92%
src/gzkit/justify/cli.py                                              105     10    90%
src/gzkit/justify/complexity_hints.py                                  71     56    21%
src/gzkit/justify/evidence.py                                         204     39    81%
src/gzkit/justify/models.py                                            48      0   100%
src/gzkit/justify/parser.py                                           166     13    92%
src/gzkit/justify/templates/__init__.py                                 0      0   100%
src/gzkit/justify/walkthrough.py                                       96      0   100%
src/gzkit/knowledge/__init__.py                                         3      0   100%
src/gzkit/knowledge/__main__.py                                         4      4     0%
src/gzkit/knowledge/concept_frontmatter.py                             11      0   100%
src/gzkit/knowledge/generate.py                                        40      1    98%
src/gzkit/ledger.py                                                   431     21    95%
src/gzkit/ledger_events.py                                            125      3    98%
src/gzkit/ledger_proof.py                                              50      8    84%
src/gzkit/ledger_semantics.py                                         208     19    91%
src/gzkit/lifecycle.py                                                 29      2    93%
src/gzkit/lock_manager.py                                             135      5    96%
src/gzkit/models/__init__.py                                            3      0   100%
src/gzkit/models/exemplar.py                                           41      0   100%
src/gzkit/models/frontmatter.py                                         2      0   100%
src/gzkit/models/historical_waiver.py                                  13      0   100%
src/gzkit/models/persona.py                                            76      2    97%
src/gzkit/models/security_surfaces.py                                  47      2    96%
src/gzkit/models/tautological_tests.py                                 25      0   100%
src/gzkit/models/theater_signatures.py                                  9      0   100%
src/gzkit/mx/__init__.py                                                3      0   100%
src/gzkit/mx/awareness.py                                              47      7    85%
src/gzkit/mx/checkpoint.py                                             14      0   100%
src/gzkit/mx/disposition.py                                            17      0   100%
src/gzkit/mx/hardening.py                                             102      3    97%
src/gzkit/mx/invariants.py                                             40      1    98%
src/gzkit/mx/levels.py                                                 11      0   100%
src/gzkit/mx/log.py                                                   117     13    89%
src/gzkit/mx/marker.py                                                 78     11    86%
src/gzkit/mx/proxy_reality.py                                          47      1    98%
src/gzkit/personas/__init__.py                                        266     27    90%
src/gzkit/pipeline_dispatch.py                                        222      2    99%
src/gzkit/pipeline_markers.py                                         366     47    87%
src/gzkit/pipeline_runtime.py                                         228     23    90%
src/gzkit/pipeline_verification.py                                    145      1    99%
src/gzkit/ports/__init__.py                                             2      0   100%
src/gzkit/ports/interfaces.py                                          24      9    62%
src/gzkit/qc_binding.py                                                33      2    94%
src/gzkit/quality.py                                                  558     76    86%
src/gzkit/registry.py                                                  57      0   100%
src/gzkit/reporter/__init__.py                                          3      0   100%
src/gzkit/reporter/panels.py                                           14      0   100%
src/gzkit/reporter/presets.py                                          63      2    97%
src/gzkit/req_kind.py                                                 283     33    88%
src/gzkit/roles.py                                                     79      1    99%
src/gzkit/rules/__init__.py                                           312     24    92%
src/gzkit/rules/_scaffolder.py                                         39      3    92%
src/gzkit/schemas/__init__.py                                          12      0   100%
src/gzkit/skill_contract.py                                             2      0   100%
src/gzkit/skills/__init__.py                                          189     25    87%
src/gzkit/skills_audit.py                                             224     46    79%
src/gzkit/skills_mirror.py                                             95      6    94%
src/gzkit/sync.py                                                     152      7    95%
src/gzkit/sync_skill_validation.py                                    159     29    82%
src/gzkit/sync_skills.py                                              277     32    88%
src/gzkit/sync_surfaces.py                                            294     19    94%
src/gzkit/tasks.py                                                    192     21    89%
src/gzkit/tautological_tests.py                                       158     16    90%
src/gzkit/templates/__init__.py                                        87      4    95%
src/gzkit/temporal_drift.py                                           132      9    93%
src/gzkit/traceability.py                                             328     29    91%
src/gzkit/triangle.py                                                 167      5    97%
src/gzkit/trust_audits.py                                               2      2     0%
src/gzkit/utils.py                                                     59     10    83%
src/gzkit/validate.py                                                  43     25    42%
src/gzkit/validate_pkg/__init__.py                                      0      0   100%
src/gzkit/validate_pkg/document.py                                     92     25    73%
src/gzkit/validate_pkg/ledger_check.py                                132     26    80%
src/gzkit/validate_pkg/manifest.py                                     36      8    78%
src/gzkit/validate_pkg/surface.py                                     106     19    82%
src/gzkit/validate_pkg/sync_parity.py                                 136     32    76%
src/gzkit/validators/__init__.py                                        0      0   100%
src/gzkit/validators/unscoped_rules.py                                136      8    94%
---------------------------------------------------------------------------------------
TOTAL                                                               37223   4968    87%
```
