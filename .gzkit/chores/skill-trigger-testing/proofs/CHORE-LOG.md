# CHORE-LOG: skill-trigger-testing

## 2026-05-10T13:28:55-05:00
- Status: PASS
- Chore: skill-trigger-testing
- Title: Skill Trigger & Output Testing
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (104.87s) -- exit 0 == 0

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
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmpn_5zi7kj/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmp02boz8o6\test_broken.py
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
Ran 4671 tests in 103.645s

OK (skipped=2)
```
## 2026-05-10T14:15:46-05:00
- Status: PASS
- Chore: skill-trigger-testing
- Title: Skill Trigger & Output Testing
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (112.03s) -- exit 0 == 0

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
Bootstrap-mode: C:/Users/Jeff/AppData/Local/Temp/tmplm7kr2jh/.gzkit/rules/complexity-thresholds.md declares a Bootstrap absolutes carve-out section; portability checks against bootstrap rows are skipped per ADR-0.0.28 § Bootstrap absolutes (REQ-11). This is informational, not a policy breach — review tracked GHIs (#404 parser zeros, #405 polarity-aware model) for resolution.
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
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmp8d_xhpf7\test_broken.py
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
Ran 4671 tests in 110.767s

OK (skipped=2)
```
