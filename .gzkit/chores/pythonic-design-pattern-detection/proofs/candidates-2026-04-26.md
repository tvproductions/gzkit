# Pythonic Design Pattern Candidates — 2026-04-26

- **Scanned root:** `src`
- **Files scanned:** 191
- **Candidates flagged:** 54

## Summary

| Pattern | Count | Pythonic target |
|---------|-------|-----------------|
| Context manager (class) | 1 | `@contextlib.contextmanager` generator (Python idiom — not GoF) |
| Strategy | 4 | First-class function or `Callable[..., R]` |
| isinstance dispatch chain | 49 | `match` statement or `@functools.singledispatch` |

## Candidates

### Context manager (class)

- **src/gzkit/cli/formatters.py:330** — `ProgressContext`
  - Signal: Class defines __enter__ + __exit__ with at most one other method
  - Pythonic target: `@contextlib.contextmanager` generator (Python idiom — not GoF)
  - Absorption ref: https://refactoring.guru/design-patterns/decorator/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

### Strategy

- **src/gzkit/cli/formatters.py:330** — `ProgressContext`
  - Signal: Class with __init__ + exactly one public method ('advance')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Absorption ref: https://refactoring.guru/design-patterns/strategy/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/cli/parser.py:33** — `StableArgumentParser`
  - Signal: Class with __init__ + exactly one public method ('error')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Absorption ref: https://refactoring.guru/design-patterns/strategy/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:107** — `_ParserState`
  - Signal: Class with __init__ + exactly one public method ('get_prefix')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Absorption ref: https://refactoring.guru/design-patterns/strategy/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/flags/decisions.py:16** — `FeatureDecisions`
  - Signal: Class with __init__ + exactly one public method ('product_proof_enforced')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Absorption ref: https://refactoring.guru/design-patterns/strategy/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

### isinstance dispatch chain

- **src/gzkit/adr_eval_redteam.py:99** — `parse_redteam_result`
  - Signal: Function `parse_redteam_result` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/arb/advisor.py:99** — `collect_arb_advice`
  - Signal: Function `collect_arb_advice` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/arb/patterns.py:123** — `collect_patterns`
  - Signal: Function `collect_patterns` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:92** — `_detect_singleton`
  - Signal: Function `_detect_singleton` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:222** — `_detect_composite`
  - Signal: Function `_detect_composite` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:280** — `_detect_template_method`
  - Signal: Function `_detect_template_method` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:303** — `_detect_state`
  - Signal: Function `_detect_state` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:340** — `_detect_adapter_or_proxy`
  - Signal: Function `_detect_adapter_or_proxy` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/adr_audit.py:552** — `adr_emit_receipt_cmd`
  - Signal: Function `adr_emit_receipt_cmd` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/adr_coverage.py:199** — `_collect_covers_annotations`
  - Signal: Function `_collect_covers_annotations` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/chores.py:218** — `_load_chores_registry`
  - Signal: Function `_load_chores_registry` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/chores_exec.py:51** — `_parse_criterion`
  - Signal: Function `_parse_criterion` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/chores_exec.py:167** — `_parse_chore_pointer`
  - Signal: Function `_parse_chore_pointer` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/config_paths.py:152** — `_flatten_manifest_paths`
  - Signal: Function `_flatten_manifest_paths` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/obpi_cmd.py:125** — `obpi_emit_receipt_cmd`
  - Signal: Function `obpi_emit_receipt_cmd` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:38** — `_extract_handler_name`
  - Signal: Function `_extract_handler_name` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:88** — `_find_root_parser_name`
  - Signal: Function `_find_root_parser_name` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:122** — `_handle_assignment`
  - Signal: Function `_handle_assignment` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:154** — `_handle_set_defaults`
  - Signal: Function `_handle_set_defaults` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:169** — `_handle_chained_add_parser`
  - Signal: Function `_handle_chained_add_parser` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:193** — `discover_commands`
  - Signal: Function `discover_commands` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:233** — `_build_import_map`
  - Signal: Function `_build_import_map` contains 9 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/eval/datasets.py:70** — `validate_dataset_json`
  - Signal: Function `validate_dataset_json` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/eval/scorer.py:81** — `score_instruction_eval`
  - Signal: Function `score_instruction_eval` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:306** — `_collect_emitted_event_types`
  - Signal: Function `_collect_emitted_event_types` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:321** — `_collect_claimed_event_types`
  - Signal: Function `_collect_claimed_event_types` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:378** — `_collect_info_get_fields`
  - Signal: Function `_collect_info_get_fields` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:402** — `_collect_ledger_written_fields`
  - Signal: Function `_collect_ledger_written_fields` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:551** — `_is_entry_point_script`
  - Signal: Function `_is_entry_point_script` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:689** — `_has_dataclass_decorator`
  - Signal: Function `_has_dataclass_decorator` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:713** — `_has_model_config`
  - Signal: Function `_has_model_config` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:970** — `_load_behave_coverage_waivers`
  - Signal: Function `_load_behave_coverage_waivers` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:1340** — `audit_adr_taxonomy`
  - Signal: Function `audit_adr_taxonomy` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:1569** — `_settings_session_start_command_strings`
  - Signal: Function `_settings_session_start_command_strings` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:1594** — `_codex_session_start_command_strings`
  - Signal: Function `_codex_session_start_command_strings` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:1616** — `_script_section_headings`
  - Signal: Function `_script_section_headings` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits.py:1645** — `_collect_state_references_collector`
  - Signal: Function `_collect_state_references_collector` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/hooks/obpi.py:210** — `normalize_scope_audit`
  - Signal: Function `normalize_scope_audit` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/hooks/obpi.py:234** — `normalize_git_sync_state`
  - Signal: Function `normalize_git_sync_state` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/justify/evidence.py:271** — `_gather_ledger_events`
  - Signal: Function `_gather_ledger_events` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger.py:348** — `get_latest_gate_statuses`
  - Signal: Function `get_latest_gate_statuses` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger_proof.py:13** — `_normalize_req_proof_input_item`
  - Signal: Function `_normalize_req_proof_input_item` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger_semantics.py:59** — `_normalize_scope_audit`
  - Signal: Function `_normalize_scope_audit` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/personas.py:350** — `_evidence_quality_proxy`
  - Signal: Function `_evidence_quality_proxy` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/quality.py:78** — `_find_parents_subscript_lines`
  - Signal: Function `_find_parents_subscript_lines` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/traceability.py:194** — `_iter_test_functions`
  - Signal: Function `_iter_test_functions` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/traceability.py:434** — `_extract_covers_arg`
  - Signal: Function `_extract_covers_arg` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:33** — `_validate_ledger_field`
  - Signal: Function `_validate_ledger_field` contains 9 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:185** — `_validate_ledger_metadata`
  - Signal: Function `_validate_ledger_metadata` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Absorption ref: https://refactoring.guru/design-patterns/visitor/python/example
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

