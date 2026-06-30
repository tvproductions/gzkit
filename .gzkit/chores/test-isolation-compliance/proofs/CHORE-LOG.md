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
## 2026-05-10T19:10:42-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (39.60s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (39.48s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 4728  Wall: 39.2s
Failures: 0  Errors: 0

Top 5 slowest tests:
   1.834s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   1.555s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)
   1.551s  test_cli_audit_covers_complexity_guide (tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity.test_cli_audit_covers_complexity_guide)
   1.452s  test_check_surfaces_report_returns_valid_report (tests.test_doc_coverage.TestIntegration.test_check_surfaces_report_returns_valid_report)
   1.012s  test_chores_run_timeout_returns_nonzero (tests.commands.test_chores.TestChoresCommands.test_chores_run_timeout_returns_nonzero)

Top 5 modules by time:
    1.9s   28 tests   67.5ms/test  tests.test_obpi_validator.TestObpiValidator
    1.8s    1 tests  1830.0ms/test  tests.commands.test_justify_validate.TestCliAuditCoverage
    1.6s   27 tests   57.8ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    1.6s    1 tests  1550.0ms/test  tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity
    1.6s    1 tests  1550.0ms/test  tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity

PASSED: All thresholds met.
[uv run python tests/tools/test_health_profiler.py] stderr:
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmp6kdk12hn/test_broken.py
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
[uv run -m unittest -q] stderr:
Skipping unparseable file: /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpmzcvm7z7/test_broken.py
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
Ran 4728 tests in 39.020s

OK (skipped=1)
```
## 2026-06-29T22:15:54-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (108.14s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (81.04s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 6660  Wall: 25.5s
Failures: 0  Errors: 0

Top 5 slowest tests:
   4.227s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   2.487s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   2.317s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)
   2.308s  test_plan_create_manpage_exists_and_covers_cli_audit (tests.test_foundation_triage_e2e.TestDocsFixturesCoverageE2E.test_plan_create_manpage_exists_and_covers_cli_audit)
   2.265s  test_cli_audit_covers_complexity_guide (tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity.test_cli_audit_covers_complexity_guide)

Top 5 modules by time:
    5.1s    2 tests  2535.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    3.9s   20 tests  194.0ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.3s   31 tests  105.2ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.5s    1 tests  2490.0ms/test  tests.commands.test_justify_validate.TestCliAuditCoverage
    2.3s    1 tests  2320.0ms/test  tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.23s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

PASSED: All thresholds met.
[uv run python tests/tools/test_health_profiler.py] stderr:
[1/1] Test
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
WARNING [rendition-floor-coherence, staged warn]: Committed rendition 'AGENTS.md/claude' omits 1 invariant-tier corpus entry (corpus-tty); the rendition does not satisfy canon's invariant floor (the canon->rendition seam ADR-0.0.37 requires). Recompose with a candidate that includes every invariant-tier entry verbatim: `gz content compose AGENTS.md`, attest the candidate, then recommit the rendition.
WARNING [rendition-freshness, staged warn]: No provenance sidecar (claude.corpus.json) for 'AGENTS.md'/'claude': the committed rendition can no longer be proven to derive from the current corpus (ADR-0.0.37 § Re-Alignment; rendition-freshness gate, OBPI-0.0.37-22 REQ-03). Recompose and re-attest: `gz content compose AGENTS.md --consumer claude` then `gz content commit AGENTS.md --consumer claude --attestor <you> --attestation-text <verbatim>`.
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check
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
Ran 6660 tests in 80.521s

OK
```
