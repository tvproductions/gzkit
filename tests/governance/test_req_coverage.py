"""Tests for the OBPI-0.0.25-01 REQ-coverage discovery module.

Covers ``parse_brief_reqs(Path) -> list[str]`` and
``discover_covers(req_id, Path) -> list[TestRef]`` — the two pure functions
the OBPI completion gate composes to verify each REQ has at least one
``@covers``-decorated test.

Brief: ``OBPI-0.0.25-01-implement-coverage-gate``
Parent ADR: ``ADR-0.0.25-obpi-completion-req-coverage-gate`` (foundation, heavy)

Coverage map (REQ → test class). Mechanism tests for the discovery
primitives the wire tests in ``test_obpi_complete_coverage_gate.py``
depend on; REQ-IDs are the brief's acceptance-criteria identifiers
(REQ-0.0.25-01-01..06) — the auxiliary FAIL-CLOSED REQUIREMENTs (#5 AST,
#6 brief-shape tolerance, #7 multi-cover, #8/#9/#10 test discipline) are
mechanism-level expectations underwriting REQs 01 and 06, so they are
tagged against those identifiers per the precedent set by
``tests/commands/test_obpi_complete.py`` (OBPI-0.0.24-02 wire tests).

| REQ              | Mechanism asserted          | Test class                  |
|------------------|-----------------------------|-----------------------------|
| REQ-0.0.25-01-01 | parse_brief_reqs extracts   | TestParseBriefReqs          |
| REQ-0.0.25-01-01 | discover_covers returns ref | TestDiscoverCoversFinds     |
| REQ-0.0.25-01-01 | AST-based, broken-tolerant  | TestDiscoverCoversAstSafety |
| REQ-0.0.25-01-06 | duplicate @covers handled   | TestDiscoverCoversMultiple  |
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.req_coverage import TestRef, discover_covers, parse_brief_reqs
from gzkit.traceability import covers

_BRIEF_TEMPLATE = """\
---
id: OBPI-9.9.9-99-fixture
parent: ADR-9.9.9-fixture
item: 99
lane: Heavy
status: Draft
---

# OBPI-9.9.9-99-fixture: tempfile fixture brief

## Objective

Synthetic brief for parse_brief_reqs unit tests.

## Acceptance Criteria

{criteria}

## Evidence

### Implementation Summary

- nothing
"""


class TestParseBriefReqs(unittest.TestCase):
    """REQ-0.0.25-01-06 — parse_brief_reqs extracts canonical REQ rows only."""

    @covers("REQ-0.0.25-01-01")
    def test_extracts_canonical_req_rows(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: First criterion.",
                "- [x] REQ-9.9.9-99-02: Second criterion (checked).",
                "- Some non-REQ checklist note.",
                "  - Indented sub-bullet without REQ prefix.",
                "- [ ] REQ-9.9.9-99-03: Third criterion.",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(_BRIEF_TEMPLATE.format(criteria=criteria), encoding="utf-8")
            reqs = parse_brief_reqs(brief)
        self.assertEqual(
            reqs,
            ["REQ-9.9.9-99-01", "REQ-9.9.9-99-02", "REQ-9.9.9-99-03"],
        )

    @covers("REQ-0.0.25-01-01")
    def test_returns_empty_when_no_acceptance_criteria_section(self) -> None:
        body = "---\nid: x\n---\n\n# x\n\n## Objective\n\nNo criteria.\n"
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(body, encoding="utf-8")
            reqs = parse_brief_reqs(brief)
        self.assertEqual(reqs, [])

    @covers("REQ-0.0.25-01-01")
    def test_skips_malformed_req_lines(self) -> None:
        criteria = "\n".join(
            [
                "- [ ] REQ-9.9.9-99-01: Valid.",
                "- [ ] REQ-X-Y-Z: Malformed (non-numeric).",
                "- [ ] REQ-: Empty body.",
                "- [ ] REQ-9.9.9-99-04: Valid second.",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(_BRIEF_TEMPLATE.format(criteria=criteria), encoding="utf-8")
            with self.assertLogs("gzkit.triangle", level="WARNING") as cm:
                reqs = parse_brief_reqs(brief)
        self.assertEqual(reqs, ["REQ-9.9.9-99-01", "REQ-9.9.9-99-04"])
        self.assertEqual(len(cm.output), 2)
        self.assertTrue(all("Malformed REQ line" in message for message in cm.output))

    @covers("REQ-0.0.25-01-01")
    def test_returns_empty_when_brief_path_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "absent.md"
            self.assertEqual(parse_brief_reqs(missing), [])

    @covers("REQ-0.0.25-01-01")
    def test_stops_at_next_h2_section(self) -> None:
        criteria = (
            "- [ ] REQ-9.9.9-99-01: in-section.\n"
            "\n"
            "## Other Section\n"
            "\n"
            "- [ ] REQ-9.9.9-99-99: out-of-section."
        )
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(_BRIEF_TEMPLATE.format(criteria=criteria), encoding="utf-8")
            reqs = parse_brief_reqs(brief)
        self.assertEqual(reqs, ["REQ-9.9.9-99-01"])


_TEST_FILE_TEMPLATE = """\
import unittest

# Decorator import is only for pattern visibility — these fixture files
# are AST-parsed, never imported at runtime.
def covers(req_id):
    def deco(fn):
        return fn
    return deco


class FixtureTests(unittest.TestCase):
{body}
"""


def _write_test_file(root: Path, name: str, body: str) -> Path:
    path = root / name
    path.write_text(_TEST_FILE_TEMPLATE.format(body=body), encoding="utf-8")
    return path


class TestDiscoverCoversFinds(unittest.TestCase):
    """REQ-0.0.25-01-01 — discover_covers returns refs for matching @covers."""

    @covers("REQ-0.0.25-01-01")
    def test_returns_ref_for_matching_decorator(self) -> None:
        body = "\n".join(
            [
                '    @covers("REQ-9.9.9-99-01")',
                "    def test_one(self):",
                "        self.assertTrue(True)",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp)
            _write_test_file(tests_root, "test_fixture.py", body)
            refs = discover_covers("REQ-9.9.9-99-01", tests_root)
        self.assertEqual(len(refs), 1)
        ref = refs[0]
        self.assertIsInstance(ref, TestRef)
        self.assertEqual(ref.qualified_name, "FixtureTests.test_one")
        self.assertTrue(ref.file_path.endswith("test_fixture.py"))
        self.assertGreater(ref.line, 0)

    @covers("REQ-0.0.25-01-01")
    def test_returns_empty_when_no_match(self) -> None:
        body = "\n".join(
            [
                '    @covers("REQ-9.9.9-99-01")',
                "    def test_one(self):",
                "        pass",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp)
            _write_test_file(tests_root, "test_fixture.py", body)
            refs = discover_covers("REQ-9.9.9-99-99", tests_root)
        self.assertEqual(refs, [])

    @covers("REQ-0.0.25-01-01")
    def test_returns_empty_when_tests_root_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no-such-dir"
            self.assertEqual(discover_covers("REQ-9.9.9-99-01", missing), [])


class TestDiscoverCoversMultiple(unittest.TestCase):
    """Mechanism for REQ-0.0.25-01-06 — duplicate @covers across multiple tests."""

    @covers("REQ-0.0.25-01-06")
    def test_two_tests_decorated_for_same_req(self) -> None:
        body = "\n".join(
            [
                '    @covers("REQ-9.9.9-99-01")',
                "    def test_alpha(self):",
                "        pass",
                "",
                '    @covers("REQ-9.9.9-99-01")',
                "    def test_beta(self):",
                "        pass",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp)
            _write_test_file(tests_root, "test_fixture.py", body)
            refs = discover_covers("REQ-9.9.9-99-01", tests_root)
        names = sorted(r.qualified_name for r in refs)
        self.assertEqual(names, ["FixtureTests.test_alpha", "FixtureTests.test_beta"])


class TestDiscoverCoversAstSafety(unittest.TestCase):
    """Mechanism for REQ-0.0.25-01-01 — broken .py files skipped; valid match found."""

    @covers("REQ-0.0.25-01-01")
    def test_skips_unparseable_file_keeps_valid_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp)
            broken = tests_root / "test_broken.py"
            broken.write_text("def malformed( :\n    pass\n", encoding="utf-8")
            _write_test_file(
                tests_root,
                "test_valid.py",
                "\n".join(
                    [
                        '    @covers("REQ-9.9.9-99-02")',
                        "    def test_x(self):",
                        "        pass",
                    ]
                ),
            )
            with self.assertLogs("gzkit.traceability", level="WARNING") as cm:
                refs = discover_covers("REQ-9.9.9-99-02", tests_root)
        self.assertEqual(len(refs), 1)
        self.assertTrue(refs[0].file_path.endswith("test_valid.py"))
        self.assertTrue(any("Skipping unparseable file" in message for message in cm.output))


_FEATURE_TEMPLATE = """\
Feature: Fixture feature for BDD coverage

  @{req_id}
  Scenario: Fixture scenario for {req_id}
    Given a synthetic step
    Then the requirement is satisfied
"""


class TestDiscoverCoversBddFeatureTree(unittest.TestCase):
    """REQ-0.0.25-01-01 — discover_covers unions features_root BDD scenario tags."""

    @covers("REQ-0.0.25-01-01")
    def test_returns_ref_for_bdd_scenario_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp) / "tests"
            tests_root.mkdir()
            features_root = Path(tmp) / "features"
            features_root.mkdir()
            (features_root / "fixture.feature").write_text(
                _FEATURE_TEMPLATE.format(req_id="REQ-9.9.9-99-01"), encoding="utf-8"
            )
            refs = discover_covers("REQ-9.9.9-99-01", tests_root, features_root=features_root)
        self.assertGreater(len(refs), 0)
        self.assertTrue(any("fixture" in r.file_path for r in refs))

    @covers("REQ-0.0.25-01-01")
    def test_bdd_ref_not_returned_without_features_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp) / "tests"
            tests_root.mkdir()
            features_root = Path(tmp) / "features"
            features_root.mkdir()
            (features_root / "fixture.feature").write_text(
                _FEATURE_TEMPLATE.format(req_id="REQ-9.9.9-99-01"), encoding="utf-8"
            )
            refs = discover_covers("REQ-9.9.9-99-01", tests_root)
        self.assertEqual(refs, [])

    @covers("REQ-0.0.25-01-01")
    def test_missing_features_root_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tests_root = Path(tmp) / "tests"
            tests_root.mkdir()
            missing = Path(tmp) / "no-such-features"
            refs = discover_covers("REQ-9.9.9-99-01", tests_root, features_root=missing)
        self.assertEqual(refs, [])


if __name__ == "__main__":
    unittest.main()
