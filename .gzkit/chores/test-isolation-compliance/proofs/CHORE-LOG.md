# CHORE-LOG: test-isolation-compliance

## 2026-05-10T14:03:56-05:00
- Status: FAIL
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [FAIL] `uv run python tests/tools/test_health_profiler.py` => rc=1 (112.75s) -- exit 1 != 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 4671  Wall: 111.5s
Failures: 0  Errors: 0

Top 5 slowest tests:
   3.279s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)
   3.167s  test_cli_audit_covers_complexity_guide (tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity.test_cli_audit_covers_complexity_guide)
   3.046s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   2.676s  test_check_surfaces_report_returns_valid_report (tests.test_doc_coverage.TestIntegration.test_check_surfaces_report_returns_valid_report)
   2.334s  test_no_inbound_references_to_legacy_paths_in_live_files (tests.governance.test_attestation_fold.TestAttestationFold.test_no_inbound_references_to_legacy_paths_in_live_files)

Top 5 modules by time:
    4.6s   25 tests  184.4ms/test  tests.test_obpi_validator.TestObpiValidator
    3.8s   16 tests  238.8ms/test  tests.commands.test_skills.TestSkillCommands
    3.8s   12 tests  316.7ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.7s   25 tests  147.2ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    3.3s    1 tests  3280.0ms/test  tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity

Stdout noise (344 lines):
  | Validated: evaluation-justify-binding
  | ✓ No evaluation-justify-binding violations.
  | Validated: evaluation-justify-binding
  | ❌ 1 violation(s):
  | → ADR-0.0.fixture: missing gz-justify artifact for low score
  | Error: Attestation receipt-binding gate failed (heavy/foundation policy).
  | - missing: no receipt file at
  | arb-step-unittest-dddddddddddddddddddddddddddddddd.json
  | Recovery: re-run the cited ARB commands and re-cite the resolved receipt IDs.
  | Error: ADR closeout blocked — unwaived REQ coverage gaps in ADR-9.9.9-fixture:

FAILED: 5 violation(s)
  - Suite took 111.5s (threshold: 60s)
  - Slow test (3.28s): test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)
  - Slow test (3.17s): test_cli_audit_covers_complexity_guide (tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity.test_cli_audit_covers_complexity_guide)
  - Slow test (3.05s): test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
  - Stdout noise: 344 line(s)
[uv run python tests/tools/test_health_profiler.py] stderr:
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
Skipping unparseable file: C:\Users\Jeff\AppData\Local\Temp\tmp60tdg5yu\test_broken.py
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
```
