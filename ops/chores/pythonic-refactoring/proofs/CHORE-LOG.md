# CHORE-LOG: pythonic-refactoring

## 2026-03-19T15:59:23-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.08s) — exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.22s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (21.16s) — exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 685 tests in 20.782s

OK
```
## 2026-03-21T14:18:45-05:00
- Status: FAIL
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.08s) — exit 0 == 0
  - [FAIL] `uvx ty check . --exclude features` => rc=1 (0.27s) — exit 1 != 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `int`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: Union elements `str` and `list[str]` are not assignable to `int`
info: rule `invalid-argument-type` is enabled by default

error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `str`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: Union elements `int` and `list[str]` are not assignable to `str`
info: rule `invalid-argument-type` is enabled by default

error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `list[str]`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: Union elements `int` and `str` are not assignable to `list[str]`
info: rule `invalid-argument-type` is enabled by default

error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `list[str]`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: Union elements `int` and `str` are not assignable to `list[str]`
info: rule `invalid-argument-type` is enabled by default

error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `TaskComplexity`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: rule `invalid-argument-type` is enabled by default

error[invalid-argument-type]: Argument is incorrect
   --> tests\test_pipeline_dispatch.py:140:29
    |
138 |         }
139 |         defaults.update(overrides)
140 |         return DispatchTask(**defaults)
    |                             ^^^^^^^^^^ Expected `str`, found `int | str | list[str]`
141 |
142 |     def test_contains_task_heading(self):
    |
info: Union elements `int` and `list[str]` are not assignable to `str`
info: rule `invalid-argument-type` is enabled by default

error[unresolved-attribute]: Attribute `status` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:206:26
    |
204 |         result = parse_handoff_result(output)
205 |         self.assertIsNotNone(result)
206 |         self.assertEqual(result.status, HandoffStatus.DONE)
    |                          ^^^^^^^^^^^^^
207 |         self.assertEqual(result.files_changed, ["a.py"])
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `files_changed` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:207:26
    |
205 |         self.assertIsNotNone(result)
206 |         self.assertEqual(result.status, HandoffStatus.DONE)
207 |         self.assertEqual(result.files_changed, ["a.py"])
    |                          ^^^^^^^^^^^^^^^^^^^^
208 |
209 |     def test_done_with_concerns(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `status` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:213:26
    |
211 |         result = parse_handoff_result(output)
212 |         self.assertIsNotNone(result)
213 |         self.assertEqual(result.status, HandoffStatus.DONE_WITH_CONCERNS)
    |                          ^^^^^^^^^^^^^
214 |         self.assertEqual(result.concerns, ["might break X"])
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `concerns` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:214:26
    |
212 |         self.assertIsNotNone(result)
213 |         self.assertEqual(result.status, HandoffStatus.DONE_WITH_CONCERNS)
214 |         self.assertEqual(result.concerns, ["might break X"])
    |                          ^^^^^^^^^^^^^^^
215 |
216 |     def test_blocked_result(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `status` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:220:26
    |
218 |         result = parse_handoff_result(output)
219 |         self.assertIsNotNone(result)
220 |         self.assertEqual(result.status, HandoffStatus.BLOCKED)
    |                          ^^^^^^^^^^^^^
221 |
222 |     def test_needs_context_result(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `status` is not defined on `None` in union `HandoffResult | None`
   --> tests\test_pipeline_dispatch.py:226:26
    |
224 |         result = parse_handoff_result(output)
225 |         self.assertIsNotNone(result)
226 |         self.assertEqual(result.status, HandoffStatus.NEEDS_CONTEXT)
    |                          ^^^^^^^^^^^^^
227 |
228 |     def test_no_json_block_returns_none(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[not-subscriptable]: Cannot subscript object of type `None` with no `__getitem__` method
   --> tests\test_pipeline_integration.py:217:30
    |
215 |             loaded = load_dispatch_summary(plans_dir, obpi_id)
216 |             self.assertIsNotNone(loaded)
217 |             self.assertEqual(loaded["obpi_id"], obpi_id)
    |                              ^^^^^^^^^^^^^^^^^
218 |             self.assertEqual(loaded["aggregation"]["total_tasks"], 1)
    |
info: rule `not-subscriptable` is enabled by default

error[not-subscriptable]: Cannot subscript object of type `None` with no `__getitem__` method
   --> tests\test_pipeline_integration.py:218:30
    |
216 |             self.assertIsNotNone(loaded)
217 |             self.assertEqual(loaded["obpi_id"], obpi_id)
218 |             self.assertEqual(loaded["aggregation"]["total_tasks"], 1)
    |                              ^^^^^^^^^^^^^^^^^^^^^
219 |
220 |     def test_load_missing_returns_none(self) -> None:
    |
info: rule `not-subscriptable` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:330:26
    |
328 |         result = parse_review_result(output)
329 |         self.assertIsNotNone(result)
330 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
    |                          ^^^^^^^^^^^^^^
331 |         self.assertEqual(result.findings, [])
332 |         self.assertEqual(result.summary, "Everything looks good")
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:331:26
    |
329 |         self.assertIsNotNone(result)
330 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
331 |         self.assertEqual(result.findings, [])
    |                          ^^^^^^^^^^^^^^^
332 |         self.assertEqual(result.summary, "Everything looks good")
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `summary` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:332:26
    |
330 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
331 |         self.assertEqual(result.findings, [])
332 |         self.assertEqual(result.summary, "Everything looks good")
    |                          ^^^^^^^^^^^^^^
333 |
334 |     def test_valid_fail_verdict_with_findings(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:341:26
    |
339 |         result = parse_review_result(output)
340 |         self.assertIsNotNone(result)
341 |         self.assertEqual(result.verdict, ReviewVerdict.FAIL)
    |                          ^^^^^^^^^^^^^^
342 |         self.assertEqual(len(result.findings), 1)
343 |         self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:342:30
    |
340 |         self.assertIsNotNone(result)
341 |         self.assertEqual(result.verdict, ReviewVerdict.FAIL)
342 |         self.assertEqual(len(result.findings), 1)
    |                              ^^^^^^^^^^^^^^^
343 |         self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
344 |         self.assertEqual(result.findings[0].file, "src/a.py")
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:343:26
    |
341 |         self.assertEqual(result.verdict, ReviewVerdict.FAIL)
342 |         self.assertEqual(len(result.findings), 1)
343 |         self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
    |                          ^^^^^^^^^^^^^^^
344 |         self.assertEqual(result.findings[0].file, "src/a.py")
345 |         self.assertEqual(result.findings[0].line, 42)
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:344:26
    |
342 |         self.assertEqual(len(result.findings), 1)
343 |         self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
344 |         self.assertEqual(result.findings[0].file, "src/a.py")
    |                          ^^^^^^^^^^^^^^^
345 |         self.assertEqual(result.findings[0].line, 42)
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:345:26
    |
343 |         self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.CRITICAL)
344 |         self.assertEqual(result.findings[0].file, "src/a.py")
345 |         self.assertEqual(result.findings[0].line, 42)
    |                          ^^^^^^^^^^^^^^^
346 |
347 |     def test_valid_concerns_verdict(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:355:26
    |
353 |         result = parse_review_result(output)
354 |         self.assertIsNotNone(result)
355 |         self.assertEqual(result.verdict, ReviewVerdict.CONCERNS)
    |                          ^^^^^^^^^^^^^^
356 |         self.assertEqual(len(result.findings), 2)
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:356:30
    |
354 |         self.assertIsNotNone(result)
355 |         self.assertEqual(result.verdict, ReviewVerdict.CONCERNS)
356 |         self.assertEqual(len(result.findings), 2)
    |                              ^^^^^^^^^^^^^^^
357 |
358 |     def test_all_severity_levels_parsed(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:368:43
    |
366 |         result = parse_review_result(output)
367 |         self.assertIsNotNone(result)
368 |         severities = {f.severity for f in result.findings}
    |                                           ^^^^^^^^^^^^^^^
369 |         self.assertEqual(
370 |             severities,
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:396:26
    |
394 |         result = parse_review_result(output)
395 |         self.assertIsNotNone(result)
396 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
    |                          ^^^^^^^^^^^^^^
397 |         self.assertEqual(result.summary, "first block")
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `summary` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:397:26
    |
395 |         self.assertIsNotNone(result)
396 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
397 |         self.assertEqual(result.summary, "first block")
    |                          ^^^^^^^^^^^^^^
398 |
399 |     def test_pass_with_no_findings_succeeds(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:403:26
    |
401 |         result = parse_review_result(output)
402 |         self.assertIsNotNone(result)
403 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
    |                          ^^^^^^^^^^^^^^
404 |         self.assertEqual(result.findings, [])
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `findings` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:404:26
    |
402 |         self.assertIsNotNone(result)
403 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
404 |         self.assertEqual(result.findings, [])
    |                          ^^^^^^^^^^^^^^^
405 |
406 |     def test_result_embedded_in_prose(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unresolved-attribute]: Attribute `verdict` is not defined on `None` in union `ReviewResult | None`
   --> tests\test_review_protocol.py:415:26
    |
413 |         result = parse_review_result(prose)
414 |         self.assertIsNotNone(result)
415 |         self.assertEqual(result.verdict, ReviewVerdict.PASS)
    |                          ^^^^^^^^^^^^^^
416 |
417 |     def test_empty_string_returns_none(self):
    |
info: rule `unresolved-attribute` is enabled by default

error[unknown-argument]: Argument `extra_field` does not match any known parameter
   --> tests\test_roles.py:155:17
    |
153 |             HandoffResult(
154 |                 status=HandoffStatus.DONE,
155 |                 extra_field="not allowed",
    |                 ^^^^^^^^^^^^^^^^^^^^^^^^^
156 |             )
    |
info: rule `unknown-argument` is enabled by default

warning[unused-type-ignore-comment]: Unused blanket `type: ignore` directive
   --> tests\test_roles.py:273:52
    |
271 |         result = HandoffResult(status=HandoffStatus.DONE)
272 |         with self.assertRaises(ValidationError):
273 |             result.status = HandoffStatus.BLOCKED  # type: ignore[misc]
    |                                                    ^^^^^^^^^^^^^^^^^^^^
274 |
275 |     def test_review_result_is_frozen(self) -> None:
    |
help: Remove the unused suppression comment
270 |     def test_handoff_result_is_frozen(self) -> None:
271 |         result = HandoffResult(status=HandoffStatus.DONE)
272 |         with self.assertRaises(ValidationError):
    -             result.status = HandoffStatus.BLOCKED  # type: ignore[misc]
273 +             result.status = HandoffStatus.BLOCKED
274 |
275 |     def test_review_result_is_frozen(self) -> None:
276 |         result = ReviewResult(verdict=ReviewVerdict.PASS)

warning[unused-type-ignore-comment]: Unused blanket `type: ignore` directive
   --> tests\test_roles.py:278:50
    |
276 |         result = ReviewResult(verdict=ReviewVerdict.PASS)
277 |         with self.assertRaises(ValidationError):
278 |             result.verdict = ReviewVerdict.FAIL  # type: ignore[misc]
    |                                                  ^^^^^^^^^^^^^^^^^^^^
    |
help: Remove the unused suppression comment
275 |     def test_review_result_is_frozen(self) -> None:
276 |         result = ReviewResult(verdict=ReviewVerdict.PASS)
277 |         with self.assertRaises(ValidationError):
    -             result.verdict = ReviewVerdict.FAIL  # type: ignore[misc]
278 +             result.verdict = ReviewVerdict.FAIL
279 |
280 |
281 | if __name__ == "__main__":

warning[unused-type-ignore-comment]: Unused blanket `type: ignore` directive
   --> tests\test_verification_dispatch.py:550:34
    |
548 |         scope = _make_scope(req_index=1)
549 |         with self.assertRaises(ValidationError):
550 |             scope.req_index = 2  # type: ignore[misc]
    |                                  ^^^^^^^^^^^^^^^^^^^^
551 |
552 |     def test_scope_forbids_extra(self) -> None:
    |
help: Remove the unused suppression comment
547 |
548 |         scope = _make_scope(req_index=1)
549 |         with self.assertRaises(ValidationError):
    -             scope.req_index = 2  # type: ignore[misc]
550 +             scope.req_index = 2
551 |
552 |     def test_scope_forbids_extra(self) -> None:
553 |         from pydantic import ValidationError

warning[unused-type-ignore-comment]: Unused blanket `type: ignore` directive
   --> tests\test_verification_dispatch.py:567:56
    |
565 |         result = _make_result(req_index=1)
566 |         with self.assertRaises(ValidationError):
567 |             result.outcome = VerificationOutcome.FAIL  # type: ignore[misc]
    |                                                        ^^^^^^^^^^^^^^^^^^^^
568 |
569 |     def test_plan_is_frozen(self) -> None:
    |
help: Remove the unused suppression comment
564 |
565 |         result = _make_result(req_index=1)
566 |         with self.assertRaises(ValidationError):
    -             result.outcome = VerificationOutcome.FAIL  # type: ignore[misc]
567 +             result.outcome = VerificationOutcome.FAIL
568 |
569 |     def test_plan_is_frozen(self) -> None:
570 |         from pydantic import ValidationError

warning[unused-type-ignore-comment]: Unused blanket `type: ignore` directive
   --> tests\test_verification_dispatch.py:574:41
    |
572 |         plan = VerificationPlan()
573 |         with self.assertRaises(ValidationError):
574 |             plan.strategy = "parallel"  # type: ignore[misc]
    |                                         ^^^^^^^^^^^^^^^^^^^^
575 |
576 |     def test_verification_outcome_values(self) -> None:
    |
help: Remove the unused suppression comment
571 |
572 |         plan = VerificationPlan()
573 |         with self.assertRaises(ValidationError):
    -             plan.strategy = "parallel"  # type: ignore[misc]
574 +             plan.strategy = "parallel"
575 |
576 |     def test_verification_outcome_values(self) -> None:
577 |         self.assertEqual(VerificationOutcome.PASS, "PASS")

Found 36 diagnostics
```
## 2026-03-21T14:29:57-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.08s) — exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.23s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (21.78s) — exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.402s

OK
```
## 2026-04-02T19:37:27-05:00
- Status: PASS
- Chore: pythonic-refactoring
- Title: Pythonic Refactoring (ruff + ty)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx ruff check .` => rc=0 (0.04s) -- exit 0 == 0
  - [PASS] `uvx ty check . --exclude features` => rc=0 (0.19s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (33.95s) -- exit 0 == 0

```text
[uvx ruff check .] stdout:
All checks passed!
[uvx ty check . --exclude features] stdout:
All checks passed!
[uv run -m unittest -q] stdout:
All frontmatter is aligned with ledger state. No changes.
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Completed  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Abandoned  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
{
  "passed": true,
  "commands_discovered": 68,
  "commands_checked": 68,
  "commands_with_gaps": 0,
  "gaps": [],
  "undeclared_commands": [],
  "orphaned_docs": []
}
Documentation Coverage Gap Report
========================================

PASSED: 68 commands discovered, 68 checked, all required surfaces present.
usage: gz flag [-h] [--quiet | --verbose] [--debug] {explain} ...

Single-flag inspection commands (explain).

positional arguments:
  {explain}
    explain      Show full metadata and resolved state for one flag

options:
  -h, --help     show this help message and exit
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flag explain ops.product_proof
    gz flag explain ops.product_proof --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz flags [-h] [--stale] [--json] [--quiet | --verbose] [--debug]

Display all registered feature flags with current values and sources.

options:
  -h, --help     show this help message and exit
  --stale        Show only stale flags (past review_by or remove_by dates)
  --json         Output as JSON
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flags
    gz flags --stale
    gz flags --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Unknown flag: 'bogus.key'

ops.product_proof
  Category:      ops
  Description:   Test flag.
  Owner:         test
  Default:       True
  Current value: True
  Source:        registry
  Review by:     2026-06-29 (88d)
  Linked ADR:    ADR-0.23.0
  Linked issue:  GHI-49

Unknown flag: 'nonexistent.key'
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
No stale flags.
                           Feature Flags (stale only)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key           ┃ Category ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ ops.stale_fl… │ ops      │ True    │ True  │ registry │ test  │ review:      │
│               │          │         │       │          │       │ -456d        │
└───────────────┴──────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Claimed: OBPI-0.1.0-01 (agent=unknown-93077, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-93077, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-93077, ttl=240m)
No lock found: OBPI-0.1.0-01
Released: OBPI-0.1.0-01
No active locks.
{
  "unlinked_specs": [],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 0,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 0
  },
  "scan_timestamp": "2026-04-03T00:37:27.604821+00:00"
}
{
  "unlinked_specs": [
    "REQ-0.1.0-01-01"
  ],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 1,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 1
  },
  "scan_timestamp": "2026-04-03T00:37:27.605318+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 33.707s

OK
```
