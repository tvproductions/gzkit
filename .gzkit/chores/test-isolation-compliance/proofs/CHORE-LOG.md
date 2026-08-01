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
