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
## 2026-07-07T05:55:58-05:00
- Status: FAIL
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [FAIL] `uv run python tests/tools/test_health_profiler.py` => rc=1 (113.10s) -- exit 1 != 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 6808  Wall: 25.1s
Failures: 0  Errors: 0

Top 5 slowest tests:
   4.218s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   3.670s  test_no_inbound_references_to_legacy_paths_in_live_files (tests.governance.test_agent_contract_fold.TestAgentContractFold.test_no_inbound_references_to_legacy_paths_in_live_files)
   2.714s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   2.554s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)
   2.547s  test_cli_audit_covers_complexity_guide (tests.commands.test_complexity_guide.TestComplexityGuideCliAuditParity.test_cli_audit_covers_complexity_guide)

Top 5 modules by time:
    5.1s    2 tests  2535.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    4.1s   20 tests  205.0ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.7s    9 tests  407.8ms/test  tests.governance.test_agent_contract_fold.TestAgentContractFold
    3.4s   31 tests  109.7ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.7s    1 tests  2710.0ms/test  tests.commands.test_justify_validate.TestCliAuditCoverage

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.22s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

FAILED: 1 violation(s)
  - Slow test (3.67s): test_no_inbound_references_to_legacy_paths_in_live_files (tests.governance.test_agent_contract_fold.TestAgentContractFold.test_no_inbound_references_to_legacy_paths_in_live_files)
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
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
```
## 2026-07-07T06:37:20-05:00
- Status: FAIL
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [FAIL] `uv run python tests/tools/test_health_profiler.py` => rc=1 (111.77s) -- exit 1 != 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 6808  Wall: 24.5s
Failures: 1  Errors: 0

Top 5 slowest tests:
   4.339s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   2.799s  test_no_inbound_references_to_legacy_paths_in_live_files (tests.governance.test_attestation_fold.TestAttestationFold.test_no_inbound_references_to_legacy_paths_in_live_files)
   2.741s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   2.568s  test_plan_create_manpage_exists_and_covers_cli_audit (tests.test_foundation_triage_e2e.TestDocsFixturesCoverageE2E.test_plan_create_manpage_exists_and_covers_cli_audit)
   2.551s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)

Top 5 modules by time:
    5.2s    2 tests  2590.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    4.1s   20 tests  204.0ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.5s   31 tests  111.9ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.8s    8 tests  350.0ms/test  tests.governance.test_attestation_fold.TestAttestationFold
    2.7s    1 tests  2740.0ms/test  tests.commands.test_justify_validate.TestCliAuditCoverage

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.34s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

FAILED: 2 violation(s)
  - Suite did not pass under parallel runner (exit 1)
  - Suite did not pass serially (1 failures, 0 errors)
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
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
```
## 2026-07-07T06:45:31-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (100.83s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (79.69s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 6808  Wall: 21.7s
Failures: 0  Errors: 0

Top 5 slowest tests:
   4.180s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   2.708s  test_cli_audit_exits_zero_after_validate_subverb_lands (tests.commands.test_justify_validate.TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands)
   2.464s  test_check_surfaces_report_returns_valid_report (tests.test_doc_coverage.TestIntegration.test_check_surfaces_report_returns_valid_report)
   2.461s  test_plan_create_manpage_exists_and_covers_cli_audit (tests.test_foundation_triage_e2e.TestDocsFixturesCoverageE2E.test_plan_create_manpage_exists_and_covers_cli_audit)
   2.451s  test_cli_audit_covers_complexity_advise (tests.commands.test_complexity_advise.TestComplexityAdviseCliAuditParity.test_cli_audit_covers_complexity_advise)

Top 5 modules by time:
    5.0s    2 tests  2505.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    4.0s   20 tests  199.5ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.4s   31 tests  109.4ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.7s    1 tests  2710.0ms/test  tests.commands.test_justify_validate.TestCliAuditCoverage
    2.5s    2 tests  1240.0ms/test  tests.test_doc_coverage.TestIntegration

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.18s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

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
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
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
Ran 6808 tests in 79.130s

OK
```
## 2026-07-31T18:50:41-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (108.00s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (79.59s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 7704  Wall: 24.4s
Failures: 0  Errors: 0

Top 5 slowest tests:
   4.826s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   1.338s  test_exit_0_when_all_bound_steps_have_negative_controls (tests.governance.test_qc_binding_scope.TestExitCodeBehavior.test_exit_0_when_all_bound_steps_have_negative_controls)
   1.238s  test_missing_on_disk_reported (tests.governance.test_brief_reconcile.TestAllowlistDimension.test_missing_on_disk_reported)
   1.114s  test_validator_runs_to_completion_under_real_repo_load (tests.commands.test_validate_frontmatter.TestFrontmatterGuard.test_validator_runs_to_completion_under_real_repo_load)
   1.047s  test_main_returns_zero_on_clean_cwd (tests.test_hooks_guards.TestMain.test_main_returns_zero_on_clean_cwd)

Top 5 modules by time:
    5.8s    2 tests  2925.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    4.5s    9 tests  495.6ms/test  tests.test_validate_sync_parity.CodexConfigSyncParityTest
    4.5s   20 tests  222.5ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    3.9s   31 tests  125.8ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.7s   17 tests  159.4ms/test  tests.commands.test_skills.TestSkillCommands

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.83s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

PASSED: All thresholds met.
[uv run python tests/tools/test_health_profiler.py] stderr:
[1/1] Test
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: argument --repair: not allowed with argument --recon
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
Ran 2 tests in 0.007s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 0.008s

OK
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
  BLOCKER: ADR-0.0.37 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.54 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.64 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.65 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.72 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
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
Ran 2 tests in 0.008s

OK
..
----------------------------------------------------------------------
Ran 2 tests in 0.007s

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
Ran 7704 tests in 78.921s

OK
```
## 2026-08-01T01:32:14-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (112.27s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (81.84s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 7704  Wall: 27.5s
Failures: 0  Errors: 0

Top 5 slowest tests:
   4.892s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   1.245s  test_missing_on_disk_reported (tests.governance.test_brief_reconcile.TestAllowlistDimension.test_missing_on_disk_reported)
   1.221s  test_exit_0_when_all_bound_steps_have_negative_controls (tests.governance.test_qc_binding_scope.TestExitCodeBehavior.test_exit_0_when_all_bound_steps_have_negative_controls)
   1.188s  test_validator_runs_to_completion_under_real_repo_load (tests.commands.test_validate_frontmatter.TestFrontmatterGuard.test_validator_runs_to_completion_under_real_repo_load)
   1.048s  test_audit_qc_binding_passes_with_no_negative_control_debt (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_audit_qc_binding_passes_with_no_negative_control_debt)

Top 5 modules by time:
    5.9s    2 tests  2970.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
    4.7s   20 tests  236.5ms/test  tests.commands.test_sync_cmds.TestSyncCommand
    4.3s    9 tests  478.9ms/test  tests.test_validate_sync_parity.CodexConfigSyncParityTest
    3.9s   31 tests  125.8ms/test  tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits
    2.7s   17 tests  156.5ms/test  tests.commands.test_skills.TestSkillCommands

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
    4.89s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

PASSED: All thresholds met.
[uv run python tests/tools/test_health_profiler.py] stderr:
[1/1] Test
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing transition); will not silently write it to 'Completed' (GHI #348 clobber class). Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: argument --repair: not allowed with argument --recon
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
Ran 2 tests in 0.008s

OK
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
  BLOCKER: ADR-0.0.37 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.54 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.64 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.65 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.72 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
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
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
  BLOCKER: ADR-0.0.37 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.54 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.64 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.65 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.72 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
----------------------------------------------------------------------
Ran 7704 tests in 81.208s

OK
```
## 2026-10-10T07:41:53-05:00
- Status: FAIL
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.2.0
- Criteria Results:
  - [FAIL] `uv run python tests/tools/test_health_profiler.py` => rc=1 (486.18s) -- exit 1 != 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 11542  Wall: 100.5s
Failures: 0  Errors: 0

Top 5 slowest tests:
  48.107s  test_every_canary_mutant_is_killed_by_its_designated_test (tests.governance.test_guard_canaries.TestTheLiveRegistry.test_every_canary_mutant_is_killed_by_its_designated_test)
  27.386s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)
   8.745s  test_timeout_kills_grandchild_not_just_child (tests.test_quality_command_timeout.TestQualityCommandTimeout.test_timeout_kills_grandchild_not_just_child)
   6.629s  test_main_returns_zero_on_clean_cwd (tests.test_hooks_guards.TestMain.test_main_returns_zero_on_clean_cwd)
   6.394s  test_grader_gaming_nc_passes_under_meta_validator (tests.mx.test_proxy_reality.TestProductionDiscoveryWiring.test_grader_gaming_nc_passes_under_meta_validator)

Top 5 modules by time:
   50.0s    3 tests  16680.0ms/test  tests.governance.test_guard_canaries.TestTheLiveRegistry
   29.9s    2 tests  14925.0ms/test  tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck
   14.8s    8 tests  1855.0ms/test  tests.test_quality_command_timeout.TestQualityCommandTimeout
   12.6s    2 tests  6290.0ms/test  tests.governance.test_enforcement_meta_validator.TestProductionRegistryDiscovery
    9.1s    8 tests  1131.2ms/test  tests.commands.test_obpi_acceptance_cli.TestAcceptanceProcessExit

Exempt E2E tests (>3s, allowlisted — not gated, see KNOWN_E2E_TESTS):
   27.39s  test_fidelity_gate_passes_now_recovery_is_complete (tests.governance.test_qc_binding_self_check.TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete)

Stdout noise (88 lines):
  | Owned section 'alpha-section' of 'Doc.md'. Unowned-byte floor fell from 83 to 26 (-57 B). Coverage:
  | Un-owned section 'doc-title' of 'Doc.md'. Unowned-byte floor rose from 26 to 65 (+39 B). Attested by
  | Un-owned section 'doc-title' of 'Doc.md'. Unowned-byte floor rose from 26 to 65 (+39 B). Attested by
  | Un-owned section 'alpha-section' of 'Doc.md'. Unowned-byte floor rose from 65 to 122 (+57 B). Attest
  | Refreshing canonical surfaces from installed wheel...
  | IDENTICAL: 0 STALE: 0 EDITED: 0
  | Chores registry diff:
  | + arb-pattern-extraction
  | = my-local-chore (local-only, preserved)
  | Chores registry diff:

FAILED: 12 violation(s)
  - Slow test (6.31s): test_no_arg_run_discovers_and_verifies_production_claims (tests.governance.test_enforcement_meta_validator.TestProductionRegistryDiscovery.test_no_arg_run_discovers_and_verifies_production_claims)
  - Slow test (6.27s): test_production_discovery_includes_qc_binding_and_lifted_ncs (tests.governance.test_enforcement_meta_validator.TestProductionRegistryDiscovery.test_production_discovery_includes_qc_binding_and_lifted_ncs)
  - Slow test (6.27s): test_default_run_registers_production_claims (tests.governance.test_enforcement_nc_discrimination.TestFloorDiscoversProductionClaims.test_default_run_registers_production_claims)
  - Slow test (3.50s): test_an_audit_that_ignores_disclosures_fails_the_admit_control (tests.governance.test_gate_population_claims.TestControlsFailWhenTheAuditIsWeakened.test_an_audit_that_ignores_disclosures_fails_the_admit_control)
  - Slow test (3.59s): test_both_claims_name_the_audit_and_pass (tests.governance.test_gate_population_claims.TestGatePopulationClaims.test_both_claims_name_the_audit_and_pass)
  - Slow test (48.11s): test_every_canary_mutant_is_killed_by_its_designated_test (tests.governance.test_guard_canaries.TestTheLiveRegistry.test_every_canary_mutant_is_killed_by_its_designated_test)
  - Slow test (3.52s): test_an_or_else_branch_cannot_present_a_failed_verifier_as_success (tests.governance.test_stage4_packet.TestOrElseConcealment.test_an_or_else_branch_cannot_present_a_failed_verifier_as_success)
  - Slow test (6.39s): test_meta_validator_fails_closed_on_an_unenrolled_member (tests.mx.test_gate5_enrollment.TestGate5EnrollmentCompleteness.test_meta_validator_fails_closed_on_an_unenrolled_member)
  - Slow test (6.39s): test_grader_gaming_nc_passes_under_meta_validator (tests.mx.test_proxy_reality.TestProductionDiscoveryWiring.test_grader_gaming_nc_passes_under_meta_validator)
  - Slow test (6.63s): test_main_returns_zero_on_clean_cwd (tests.test_hooks_guards.TestMain.test_main_returns_zero_on_clean_cwd)
  - Slow test (8.74s): test_timeout_kills_grandchild_not_just_child (tests.test_quality_command_timeout.TestQualityCommandTimeout.test_timeout_kills_grandchild_not_just_child)
  - Stdout noise: 88 line(s)
[uv run python tests/tools/test_health_profiler.py] stderr:
Refusing to re-baseline: the never-fired set grew. Disclose the new type deliberately rather than letting a re-run absorb it.
POLICY BREACH: 1 declared event type(s) have no live occurrence, disclosure, or verified isolated producer: c
  Why: a declared type with no producer is vocabulary that records nothing while reading as a modelled fact. Growth is allowed but must be visible — an undisclosed one is indistinguishable from a wired producer.
  Next step: WIRE THE PRODUCER and verify actual production use or register a fresh isolated execution, or retire the declaration. ADR-0.0.73 BI #8 registers this surface as a shrink-ratchet -- 'a committed baseline the list can only decrease against' -- so raising 'baseline_count' is not a recovery step and is never an agent's move to make: it is the laundering the ratchet exists to refuse. Draining a type that now fires updates data/ledger_vocabulary_grandfather.json and 'baseline_count' in data/waiver_ratchet_registry.json DOWNWARD together; run this script with --report --write to compute the drained set, which refuses to write when the never-fired set has grown. If a newly declared type genuinely cannot be wired yet, that is an operator ruling on the ratchet, not a line an agent edits to clear its own gate (GHI #611 review, 2026-09-06).
POLICY BREACH: 1 declared event type(s) have no live occurrence, disclosure, or verified isolated producer: acceptance_recorded
  Why: a declared type with no producer is vocabulary that records nothing while reading as a modelled fact. Growth is allowed but must be visible — an undisclosed one is indistinguishable from a wired producer.
  Next step: WIRE THE PRODUCER and verify actual production use or register a fresh isolated execution, or retire the declaration. ADR-0.0.73 BI #8 registers this surface as a shrink-ratchet -- 'a committed baseline the list can only decrease against' -- so raising 'baseline_count' is not a recovery step and is never an agent's move to make: it is the laundering the ratchet exists to refuse. Draining a type that now fires updates data/ledger_vocabulary_grandfather.json and 'baseline_count' in data/waiver_ratchet_registry.json DOWNWARD together; run this script with --report --write to compute the drained set, which refuses to write when the never-fired set has grown. If a newly declared type genuinely cannot be wired yet, that is an operator ruling on the ratchet, not a line an agent edits to clear its own gate (GHI #611 review, 2026-09-06).
Refusing to re-baseline: the never-fired set grew. Disclose the new type deliberately rather than letting a re-run absorb it.
POLICY BREACH: 1 declared event type(s) have no live occurrence, disclosure, or verified isolated producer: unregistered_event
  Why: a declared type with no producer is vocabulary that records nothing while reading as a modelled fact. Growth is allowed but must be visible — an undisclosed one is indistinguishable from a wired producer.
  Next step: WIRE THE PRODUCER and verify actual production use or register a fresh isolated execution, or retire the declaration. ADR-0.0.73 BI #8 registers this surface as a shrink-ratchet -- 'a committed baseline the list can only decrease against' -- so raising 'baseline_count' is not a recovery step and is never an agent's move to make: it is the laundering the ratchet exists to refuse. Draining a type that now fires updates data/ledger_vocabulary_grandfather.json and 'baseline_count' in data/waiver_ratchet_registry.json DOWNWARD together; run this script with --report --write to compute the drained set, which refuses to write when the never-fired set has grown. If a newly declared type genuinely cannot be wired yet, that is an operator ruling on the ratchet, not a line an agent edits to clear its own gate (GHI #611 review, 2026-09-06).
BLOCKERS: gz obpi withdraw: error: the following arguments are required: --attestor
BLOCKERS: gz obpi complete: error: the following arguments are required: --attestor
[1/1] Test
Error: the pending-transition journal '.gzkit/ownership/Doc.md.json.journal' is unreadable or malformed: the declaration at '.gzkit/ownership/Doc.md.json' is not the transition this witness would describe (unowned_byte_floor 125 != 26) -- a witness is derived from the state that landed, never from one that was hoped for.
Why forbidden: an un-owning is completed from its journal, so a journal that cannot be proven to continue the live on-disk predecessor makes an interrupted raise unrecoverable and no further un-owning of this surface may proceed on top of it (REQ-0.35.0-04-02). No ledger witness was written by this run, and the journal is RETAINED.
  Do NOT delete the journal and do NOT hand-edit the ownership declaration. Identify the interruption state from BOTH signals together -- the `floor_event_id` in '.gzkit/ownership/Doc.md.json' and whether `.gzkit/ledger.jsonl` carries the journal's `event_id` (`gz validate --ledger`):
    - state A, floor_event_id equals the journal's `parent_event_id` and the ledger has no such row: nothing landed. Move the journal aside for the record, then re-run to start a fresh transition from the declaration on disk.
    - state B or state C -- INDISTINGUISHABLE from disk, and the retry handles both the same way -- floor_event_id equals the journal's `event_id` and the ledger has no such row: the declaration ALREADY carries this transition, and what is outstanding is its durability barrier, its witness, or both. Re-run the same command; it re-establishes the barrier and appends the missing witness. This is the pair the retired advice treated as proof that nothing landed.
    - state D, the ledger carries the journal's `event_id`: the transition completed and is witnessed. Re-run the same command. If the surface still carries the bytes the floor was measured against it clears the recovery material; if an editor has since changed them, it refuses naming state D AND state E and hands you the measured bytes -- the SOURCE axis is orthogonal to states A-D, so a witness settles the transition and says nothing about the source.
  If the journal cannot be parsed at all its `event_id` is unreadable, so `floor_event_id` alone cannot separate state A from state B or state C: capture both files and ask the operator to rule.
Error: the witness source declaration declares identity 'Other.md', but this transaction's target is 'Doc.md' ('.gzkit/ownership/Doc.md.json').
Why forbidden: the target fixes ONE identity and its surface, declaration and journal paths for the whole transaction, and every snapshot consumed under its lock must agree with it. Adopting a second identity here would write and witness through paths chosen from different values, and `load_declaration` fails closed when a floor's witness names a surface its declaration does not (REQ-0.35.0-04-02). The journal is RETAINED at '.gzkit/ownership/Doc.md.json.journal', so the transition stays completable.
  Re-run the same command. The identity is resolved at entry, so a retry either proceeds against the declaration as it now stands or refuses naming the conflict.
Fidelity validation failed [surface-weight]: Surface weight limit exceeded
File not written.
[advisory] WARNING agents-md-map-conformance: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline rationale to docs/governance/ behind one-line pointers.
[advisory] WARNING instructions-files-budget: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline pedagogy to docs/governance/ behind one-line pointers.
[advisory] WARNING agents-md-map-conformance: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline rationale to docs/governance/ behind one-line pointers.
[advisory] WARNING instructions-files-budget: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline pedagogy to docs/governance/ behind one-line pointers.
[advisory] WARNING agents-md-map-conformance: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline rationale to docs/governance/ behind one-line pointers.
[advisory] WARNING agents-md-map-conformance: AGENTS.md is 25473 chars, exceeds 20000-char budget by 5473. Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) to lift inline rationale to docs/governance/ behind one-line pointers.
BLOCKERS: gz check: error: argument --full: not allowed with argument --fast
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
refused: synthetic monitor verdict
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
usage: check_proof_freshness.py <slug of a chore declaring staleness.signal elapsed-time, or content-delta with surfaces>

POLICY BREACH:
  .gzkit/chores/demo-coherence/proofs/report.md was last committed 1970-01-01, before its audited surface last moved (1970-01-01).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the demo-coherence audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
distribution-audit: cannot parse pyproject.toml: Expected '=' after a key in a key/value pair (at line 1, column 6)
Warning: ruff format did not run on /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-hooks-stroqtzk: exited 1
warning: `VIRTUAL_ENV=/Users/jeff/Documents/Code/gzkit/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Using CPython 3.14.6
Creating virtual environment at: .venv
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.14`.
   Building probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-xn5gx27h
error: Failed to build `probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-xn5gx27h`
  cause: The build backend returned an error
  cause: Call to `gzkit_no_such_backend.get_requires_for_build_editable` failed (exit status: 1)

         [stderr]
         Traceback (most recent call last):
           File "<string>", line 8, in <module>
             import gzkit_no_such_backend as backend
         ModuleNotFoundError: No module named 'gzkit_no_such_backend'

hint: This error likely indicates that `probe-tree@0.1.0` depends on `gzkit_no_such_backend`, but doesn't declare it as a build dependency. If `probe-tree` is a first-party package, consider adding `gzkit_no_such_backend` to its `build-system.requires`. Otherwise, either add it to your `pyproject.toml` under:

[tool.uv.extra-build-dependencies]
probe-tree = ["gzkit_no_such_backend"]

or `uv pip install gzkit_no_such_backend` into the environment and re-run with `--no-build-isolation`.
Warning: ruff format did not run on /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-hooks-cgaxj_jx: exited 1
warning: `VIRTUAL_ENV=/Users/jeff/Documents/Code/gzkit/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.14`.
   Building probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-xn5gx27h
error: Failed to build `probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-xn5gx27h`
  cause: The build backend returned an error
  cause: Call to `gzkit_no_such_backend.get_requires_for_build_editable` failed (exit status: 1)

         [stderr]
         Traceback (most recent call last):
           File "<string>", line 8, in <module>
             import gzkit_no_such_backend as backend
         ModuleNotFoundError: No module named 'gzkit_no_such_backend'

hint: This error likely indicates that `probe-tree@0.1.0` depends on `gzkit_no_such_backend`, but doesn't declare it as a build dependency. If `probe-tree` is a first-party package, consider adding `gzkit_no_such_backend` to its `build-system.requires`. Otherwise, either add it to your `pyproject.toml` under:

[tool.uv.extra-build-dependencies]
probe-tree = ["gzkit_no_such_backend"]

or `uv pip install gzkit_no_such_backend` into the environment and re-run with `--no-build-isolation`.
Warning: ruff format did not run on /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-hooks-5o76xm1b: exited 1
warning: `VIRTUAL_ENV=/Users/jeff/Documents/Code/gzkit/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Using CPython 3.14.6
Creating virtual environment at: .venv
warning: No `requires-python` value found in the workspace. Defaulting to `>=3.14`.
   Building probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-89x3hfwe
error: Failed to build `probe-tree @ file:///private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-root-binding-89x3hfwe`
  cause: The build backend returned an error
  cause: Call to `gzkit_no_such_backend.get_requires_for_build_editable` failed (exit status: 1)

         [stderr]
         Traceback (most recent call last):
           File "<string>", line 8, in <module>
             import gzkit_no_such_backend as backend
         ModuleNotFoundError: No module named 'gzkit_no_such_backend'

hint: This error likely indicates that `probe-tree@0.1.0` depends on `gzkit_no_such_backend`, but doesn't declare it as a build dependency. If `probe-tree` is a first-party package, consider adding `gzkit_no_such_backend` to its `build-system.requires`. Otherwise, either add it to your `pyproject.toml` under:

[tool.uv.extra-build-dependencies]
probe-tree = ["gzkit_no_such_backend"]

or `uv pip install gzkit_no_such_backend` into the environment and re-run with `--no-build-isolation`.
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
[advisory] rendition-lineage: What failed: committed rendition 'NCSurface.md/root' declares section 'owned-section' corpus-owned, but its committed bytes differ from what the effective corpus materializes for that section.
Why forbidden: ADR-0.35.0 § Decision item 4 — a corpus-owned section's bytes are DERIVED from canon, never hand-authored into the rendition, so prose written straight into an owned section is canon drift that no other gate observes. Lowering a section's declared ownership is never the repair for this finding: the declaration's scope changes only through OBPI-0.35.0-04's attested raise-path, as a deliberate governed move, never to clear a gate.
Next step: land the wording in canon (`gz content remember NCSurface.md ...`), then regenerate and recommit — `gz content compose NCSurface.md --consumer root`, then `gz content commit NCSurface.md --consumer root`.
[advisory] rendition-lineage: 1 committed rendition(s) graded; 1/2 sections owned, 61/115 bytes owned (53.0%); 0 section(s) / 0 byte(s) UNGRADED (declared corpus-owned with no committed lineage). Unowned and ungraded bytes are measured debt and never change this scope's exit code (ADR-0.35.0 § Decision item 4).
gzkit: recovered /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpdhgd8bky/ledger.jsonl — supplied the missing final newline for a complete 119-byte record; no row was discarded
gzkit: recovered /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpv3lazmr1/ledger.jsonl — supplied the missing final newline for a complete 119-byte record; no row was discarded
gzkit: recovered /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpxny12uk1/ledger.jsonl — supplied the missing final newline for a complete 119-byte record; no row was discarded
gzkit: recovered /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpxnfafpr4/ledger.jsonl — discarded 32 byte(s) of an interrupted append before the record boundary
gzkit: recovered /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpkt8fb_cu/ledger.jsonl — discarded 44 byte(s) of an interrupted append before the record boundary
refused: OBPI-test.md carries terminal OBPI status 'abandoned' (no outgoing canonical transition); will not silently write it to 'Completed' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing canonical transition); will not silently write it to 'Completed' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing canonical transition); will not silently write it to 'Completed' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'superseded' (no outgoing canonical transition); will not silently write it to 'Completed' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
refused: OBPI-test.md carries terminal OBPI status 'withdrawn' (no outgoing canonical transition); will not silently write it to 'Completed' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: --repair may be given at most once
BLOCKERS: gz permitted-entry: error: argument --repair: not allowed with argument --recon
refused: OBPI-test-brief.md carries terminal OBPI status 'abandoned' (no outgoing canonical transition); will not silently write it to 'Active' — that is the GHI #348 clobber class. Recover with an explicit transition (`gz obpi repudiate` / `gz obpi supersede`) or correct the ledger event, then re-run.
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
BLOCKERS: --apply requires both --attestor and --attestation. The Gate-5 human attestation IS the terminality witness for pre-ledger foundations; without it the backfill has no legitimate witness.
  BLOCKER: ADR-0.0.37 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.54 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.64 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.65 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
  BLOCKER: ADR-0.0.72 is a declared Sunset prerequisite but no such foundation package is on disk — cannot confirm it is terminal.
Warning: ruff format did not run on /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-fmt-tbg6vbi2/hooks: exited <MagicMock name='run().returncode' id='4497708368'>
<MagicMock name='run().stderr.strip()' id='4497706688'>
Warning: ruff format did not run on /var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/gzkit-fmt-no_uipzb/hooks: exited <MagicMock name='run().returncode' id='4496034848'>
<MagicMock name='run().stderr.strip()' id='4496031824'>
```
