# Pythonic Design Pattern Candidates — 2026-10-10

- **Scanned root:** `src`
- **Files scanned:** 541
- **Candidates flagged:** 132

## Summary

| Pattern | Count | Pythonic target |
|---------|-------|-----------------|
| Context manager (class) | 1 | `@contextlib.contextmanager` generator (Python idiom — not GoF) |
| Strategy | 5 | First-class function or `Callable[..., R]` |
| isinstance dispatch chain | 126 | `match` statement or `@functools.singledispatch` |

## Candidates

### Context manager (class)

- **src/gzkit/cli/formatters.py:340** — `ProgressContext`
  - Signal: Class defines __enter__ + __exit__ with at most one other method
  - Pythonic target: `@contextlib.contextmanager` generator (Python idiom — not GoF)
  - Example: `Python/src/Decorator/Conceptual/main.py`
  - Output: `Python/src/Decorator/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

### Strategy

- **src/gzkit/cli/formatters.py:340** — `ProgressContext`
  - Signal: Class with __init__ + exactly one public method ('advance')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Example: `Python/src/Strategy/Conceptual/main.py`
  - Output: `Python/src/Strategy/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/cli/parser.py:33** — `StableArgumentParser`
  - Signal: Class with __init__ + exactly one public method ('error')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Example: `Python/src/Strategy/Conceptual/main.py`
  - Output: `Python/src/Strategy/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/complexity/advisor/engine.py:100** — `DiagnosisEngine`
  - Signal: Class with __init__ + exactly one public method ('diagnose')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Example: `Python/src/Strategy/Conceptual/main.py`
  - Output: `Python/src/Strategy/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:115** — `_ParserState`
  - Signal: Class with __init__ + exactly one public method ('get_prefix')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Example: `Python/src/Strategy/Conceptual/main.py`
  - Output: `Python/src/Strategy/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/flags/decisions.py:16** — `FeatureDecisions`
  - Signal: Class with __init__ + exactly one public method ('product_proof_enforced')
  - Pythonic target: First-class function or `Callable[..., R]`
  - Example: `Python/src/Strategy/Conceptual/main.py`
  - Output: `Python/src/Strategy/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

### isinstance dispatch chain

- **src/gzkit/acceptance_execution.py:74** — `proof_claim_digest`
  - Signal: Function `proof_claim_digest` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/acceptance_execution.py:82** — `stable`
  - Signal: Function `stable` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/acceptance_store.py:192** — `review_from_receipt`
  - Signal: Function `review_from_receipt` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/adr_eval_redteam.py:99** — `parse_redteam_result`
  - Signal: Function `parse_redteam_result` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/arb/advisor.py:109** — `collect_arb_advice`
  - Signal: Function `collect_arb_advice` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/arb/patterns.py:133** — `collect_patterns`
  - Signal: Function `collect_patterns` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/__init__.py:55** — `_project_local_slugs`
  - Signal: Function `_project_local_slugs` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:92** — `_detect_singleton`
  - Signal: Function `_detect_singleton` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:222** — `_detect_composite`
  - Signal: Function `_detect_composite` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:280** — `_detect_template_method`
  - Signal: Function `_detect_template_method` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:305** — `_detect_state`
  - Signal: Function `_detect_state` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/chores/pythonic-design-pattern-detection/scan.py:343** — `_detect_adapter_or_proxy`
  - Signal: Function `_detect_adapter_or_proxy` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/codex_roles.py:55** — `_role_output`
  - Signal: Function `_role_output` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/adr_audit.py:1103** — `_apply_human_attestation_gates`
  - Signal: Function `_apply_human_attestation_gates` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/adr_coverage.py:202** — `_collect_covers_annotations`
  - Signal: Function `_collect_covers_annotations` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/chores_exec.py:52** — `_parse_criterion`
  - Signal: Function `_parse_criterion` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/chores_exec.py:168** — `_parse_chore_pointer`
  - Signal: Function `_parse_chore_pointer` contains 9 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/config_paths.py:152** — `_flatten_manifest_paths`
  - Signal: Function `_flatten_manifest_paths` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/config_paths.py:255** — `_collect_declared_audit_subjects`
  - Signal: Function `_collect_declared_audit_subjects` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/obpi_cmd.py:405** — `_gate_completed_receipt_binding`
  - Signal: Function `_gate_completed_receipt_binding` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/obpi_cmd.py:524** — `obpi_emit_receipt_cmd`
  - Signal: Function `obpi_emit_receipt_cmd` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commands/obpi_stages.py:389** — `_evidence_json_to_complete_flags`
  - Signal: Function `_evidence_json_to_complete_flags` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commit_witness.py:144** — `_decorator_name`
  - Signal: Function `_decorator_name` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/commit_witness.py:187** — `_behavior`
  - Signal: Function `_behavior` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/complexity/baseline.py:154** — `_round_floats`
  - Signal: Function `_round_floats` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/ownership.py:1622** — `_refuse_wrong_direction_witness`
  - Signal: Function `_refuse_wrong_direction_witness` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/ownership.py:1974** — `journal_replay_defect`
  - Signal: Function `journal_replay_defect` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/vendors.py:87** — `_load_manifest`
  - Signal: Function `_load_manifest` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/vendors.py:98** — `_load_temperatures`
  - Signal: Function `_load_temperatures` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/vendors.py:176** — `delivery_cap_for`
  - Signal: Function `delivery_cap_for` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/content/vendors.py:200** — `binding_delivery_cap`
  - Signal: Function `binding_delivery_cap` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/flag_scanner.py:119** — `discover_command_flag_specs`
  - Signal: Function `discover_command_flag_specs` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:44** — `_extract_handler_name`
  - Signal: Function `_extract_handler_name` contains 9 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:96** — `_find_root_parser_name`
  - Signal: Function `_find_root_parser_name` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:130** — `_handle_assignment`
  - Signal: Function `_handle_assignment` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:162** — `_handle_set_defaults`
  - Signal: Function `_handle_set_defaults` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:177** — `_handle_chained_add_parser`
  - Signal: Function `_handle_chained_add_parser` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:201** — `discover_commands`
  - Signal: Function `discover_commands` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/doc_coverage/scanner.py:242** — `_build_import_map`
  - Signal: Function `_build_import_map` contains 9 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/eval/datasets.py:64** — `validate_dataset_json`
  - Signal: Function `validate_dataset_json` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/eval/scorer.py:81** — `score_instruction_eval`
  - Signal: Function `score_instruction_eval` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/git_spawn_boundary.py:148** — `_spawns_git`
  - Signal: Function `_spawns_git` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/git_spawn_boundary.py:168** — `_inside_boundary`
  - Signal: Function `_inside_boundary` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/_qc_nc_hooks.py:30** — `hook_type_population`
  - Signal: Function `hook_type_population` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/adversarial_validation.py:133** — `_load_grandfathered`
  - Signal: Function `_load_grandfathered` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/bullet_retention.py:346** — `_load_pinned_identities`
  - Signal: Function `_load_pinned_identities` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/closeout_proof.py:188** — `_waived_req_ids`
  - Signal: Function `_waived_req_ids` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/codex_delivery_witness.py:115** — `delivered_contract_bytes`
  - Signal: Function `delivered_contract_bytes` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/config_derivation.py:97** — `policy_constants`
  - Signal: Function `policy_constants` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/config_registry.py:63** — `_waiver_owned`
  - Signal: Function `_waiver_owned` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/config_registry.py:165** — `audit_config_registry`
  - Signal: Function `audit_config_registry` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/cross_platform.py:249** — `_is_main_guard`
  - Signal: Function `_is_main_guard` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/cross_platform.py:572** — `_writes_text_without_newline`
  - Signal: Function `_writes_text_without_newline` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/cross_platform.py:665** — `_asserts_read_bytes_against_literal`
  - Signal: Function `_asserts_read_bytes_against_literal` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:315** — `_collect_emitted_event_types`
  - Signal: Function `_collect_emitted_event_types` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:330** — `_collect_typed_model_event_types`
  - Signal: Function `_collect_typed_model_event_types` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:419** — `_claimed_from_event_compare`
  - Signal: Function `_claimed_from_event_compare` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:478** — `_info_get_field`
  - Signal: Function `_info_get_field` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:501** — `_collect_ledger_written_fields`
  - Signal: Function `_collect_ledger_written_fields` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:548** — `_returned_dict_keys`
  - Signal: Function `_returned_dict_keys` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:630** — `_assigned_dict`
  - Signal: Function `_assigned_dict` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:649** — `_update_argument`
  - Signal: Function `_update_argument` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:663** — `_mutation_keys`
  - Signal: Function `_mutation_keys` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/events.py:732** — `audit_producer_fields`
  - Signal: Function `audit_producer_fields` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/exemption_controls.py:64** — `_load_accepted`
  - Signal: Function `_load_accepted` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/gate_callers.py:202** — `_load_accepted`
  - Signal: Function `_load_accepted` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/gate_enrollment.py:118** — `_load_accepted`
  - Signal: Function `_load_accepted` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/gate_population.py:185** — `_load_accepted`
  - Signal: Function `_load_accepted` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/intrinsic_attestation.py:30** — `validate_intrinsic_attestation`
  - Signal: Function `validate_intrinsic_attestation` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/models.py:95** — `_has_dataclass_decorator`
  - Signal: Function `_has_dataclass_decorator` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/models.py:119** — `_has_model_config`
  - Signal: Function `_has_model_config` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/orientation.py:41** — `_read_session_start_blocks`
  - Signal: Function `_read_session_start_blocks` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/orientation.py:75** — `_codex_session_start_command_strings`
  - Signal: Function `_codex_session_start_command_strings` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/orientation.py:111** — `_string_literals`
  - Signal: Function `_string_literals` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/orphaned_implementation.py:110** — `_partition_events`
  - Signal: Function `_partition_events` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/release.py:545** — `_ruff_selection`
  - Signal: Function `_ruff_selection` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/status_writer_coverage.py:121** — `_touches_status_key`
  - Signal: Function `_touches_status_key` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/status_writer_coverage.py:156** — `_consults_monitor`
  - Signal: Function `_consults_monitor` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/surface_delivery_witness.py:180** — `_audit_surface`
  - Signal: Function `_audit_surface` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/taxonomy.py:429** — `_grandfathered_event_ids`
  - Signal: Function `_grandfathered_event_ids` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/theater_signature_scan.py:71** — `_detect_copy_vs_self`
  - Signal: Function `_detect_copy_vs_self` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/theater_signature_scan.py:123** — `_is_mtime_node`
  - Signal: Function `_is_mtime_node` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/theater_signature_scan.py:187** — `_is_clean_early_return`
  - Signal: Function `_is_clean_early_return` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/theater_signature_scan.py:202** — `_detect_skip_if_pass`
  - Signal: Function `_detect_skip_if_pass` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/vendor_manifest.py:87** — `_root_contract_errors`
  - Signal: Function `_root_contract_errors` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/waiver_ratchet.py:86** — `_iter_entries`
  - Signal: Function `_iter_entries` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/waiver_ratchet.py:209** — `_fields_of`
  - Signal: Function `_fields_of` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/waiver_ratchet.py:250** — `_check_identity`
  - Signal: Function `_check_identity` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/governance/trust_audits/waiver_ratchet.py:353** — `audit_waiver_ratchet`
  - Signal: Function `audit_waiver_ratchet` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/handoff_validation.py:142** — `continues_from_refs`
  - Signal: Function `continues_from_refs` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/hooks/codex.py:84** — `sync_codex_hooks`
  - Signal: Function `sync_codex_hooks` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/hooks/obpi.py:217** — `normalize_scope_audit`
  - Signal: Function `normalize_scope_audit` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/hooks/obpi.py:241** — `normalize_git_sync_state`
  - Signal: Function `normalize_git_sync_state` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/insights/correction_mining.py:94** — `_user_text`
  - Signal: Function `_user_text` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/justify/evidence.py:271** — `_gather_ledger_events`
  - Signal: Function `_gather_ledger_events` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger.py:892** — `get_latest_gate_statuses`
  - Signal: Function `get_latest_gate_statuses` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger.py:931** — `get_effective_gate_statuses`
  - Signal: Function `get_effective_gate_statuses` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger.py:1151** — `_apply_audit_receipt_metadata`
  - Signal: Function `_apply_audit_receipt_metadata` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger_corrections.py:85** — `_field`
  - Signal: Function `_field` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger_proof.py:13** — `_normalize_req_proof_input_item`
  - Signal: Function `_normalize_req_proof_input_item` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ledger_semantics.py:85** — `_normalize_scope_audit`
  - Signal: Function `_normalize_scope_audit` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ontology/source.py:311** — `_ast_anchor_from_decorator`
  - Signal: Function `_ast_anchor_from_decorator` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/ontology/source.py:328** — `_ast_imports_and_defs`
  - Signal: Function `_ast_imports_and_defs` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/personas/__init__.py:371** — `_evidence_quality_proxy`
  - Signal: Function `_evidence_quality_proxy` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/quality.py:83** — `_load_quality_command_timeout`
  - Signal: Function `_load_quality_command_timeout` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/quality.py:276** — `_find_parents_access_lines`
  - Signal: Function `_find_parents_access_lines` contains 6 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/quality.py:909** — `_raw_mkdocs_validation`
  - Signal: Function `_raw_mkdocs_validation` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:49** — `_has_filesystem_op`
  - Signal: Function `_has_filesystem_op` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:70** — `_has_assertion`
  - Signal: Function `_has_assertion` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:157** — `_exercises_production_symbol`
  - Signal: Function `_exercises_production_symbol` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:228** — `_called_local_name`
  - Signal: Function `_called_local_name` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:241** — `_asserts_only_raises`
  - Signal: Function `_asserts_only_raises` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:284** — `_class_setup_map`
  - Signal: Function `_class_setup_map` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:313** — `_reads_project_source`
  - Signal: Function `_reads_project_source` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:376** — `_module_backed_self_attrs`
  - Signal: Function `_module_backed_self_attrs` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/tautological_tests.py:413** — `_calls_self_module`
  - Signal: Function `_calls_self_module` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/test_shape.py:110** — `_output_source`
  - Signal: Function `_output_source` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/test_shape.py:124** — `_has_assertion`
  - Signal: Function `_has_assertion` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/traceability.py:81** — `_non_docstring_string_ranges`
  - Signal: Function `_non_docstring_string_ranges` contains 4 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/traceability.py:276** — `_iter_test_functions`
  - Signal: Function `_iter_test_functions` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/traceability.py:523** — `_extract_covers_arg`
  - Signal: Function `_extract_covers_arg` contains 5 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:136** — `_declared_types`
  - Signal: Function `_declared_types` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:193** — `_validate_ledger_field`
  - Signal: Function `_validate_ledger_field` contains 7 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:273** — `_conditional_predicate`
  - Signal: Function `_conditional_predicate` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:296** — `_validate_ledger_conditionals`
  - Signal: Function `_validate_ledger_conditionals` contains 8 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_

- **src/gzkit/validate_pkg/ledger_check.py:478** — `_validate_ledger_metadata`
  - Signal: Function `_validate_ledger_metadata` contains 3 isinstance() calls
  - Pythonic target: `match` statement or `@functools.singledispatch`
  - Example: `Python/src/Visitor/Conceptual/main.py`
  - Output: `Python/src/Visitor/Conceptual/Output.txt`
  - Role map: _[fill in after reading example]_
  - Pythonic collapse: _[fill in]_
  - Disposition: _[applied | deferred | not-pythonic-rewrite]_
  - Notes: _[fill in]_


## Dispositions — 2026-10-10 (maintenance visit D), PROVISIONAL

`DESIGN_PATTERNS_ARCHIVE` is unset on this machine, so the example corpus was not read and every
disposition below is **provisional** per CHORE.md § Python example corpus. They are recorded by
candidate class with the concrete reason, not per row; the per-row judgment the chore requires is
operator time this visit did not have, and the 2026-04-26 report (54 candidates) still carries its
template placeholders, so the backlog is two runs deep.

| Class | Count | Provisional disposition | Reason |
|---|---|---|---|
| isinstance dispatch chain | 126 | `not-pythonic-rewrite` (provisional) | The chains sit in AST walkers (`tautological_tests.py`, `doc_coverage/scanner.py`, `scan.py` itself), JSON/ledger shape readers (`trust_audits/events.py`, `validate_pkg/ledger_check.py`, `waiver_ratchet.py`) and frontmatter parsers — type-narrowing over untyped input, where `isinstance` is the idiom `match` would only restate. A `singledispatch` rewrite moves the chain into registration order and loses the local reading. Re-review any chain that gains a fourth arm. |
| Strategy (`__init__` + one public method) | 5 | `deferred` (provisional) | Candidates include `StableArgumentParser.error` (an `argparse` subclass; the one method is an override, not a strategy) and `ProgressContext.advance`; the detector's signal is shape, and these shapes are framework hooks. Deferred to a run with the archive mounted. |
| Context manager (class) | 1 | `deferred` (provisional) | `cli/formatters.py` `ProgressContext`: `@contextlib.contextmanager` fits if `advance` can become a yielded callable; needs the Rich progress API read beside the example. |

xenon `--max-absolute B` (`proofs/xenon-hotspots-2026-10-10.txt`): 375 lines, every block ranked C
(the gate's ceiling is C, so none breaches); no candidate above coincides with a C-ranked block that
the chore's step 2 would promote to the top of the apply queue.

Run log row: 2026-10-10 | AST 132 | reference 0 (archive unset) | applied 0 | deferred 6 | not-pythonic 126 (all provisional).
