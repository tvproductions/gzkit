"""Tests for the ADR-0.0.22 sensitivity-binding validator.

REQ coverage:

- REQ-0.0.22-03-01: Floor fires — intersecting paths force `detected: security`.
- REQ-0.0.22-03-02: Escalation allowed — declared `security` w/ no intersection ok.
- REQ-0.0.22-03-03: Escape blocked — declared lower than detected exits with finding.
- REQ-0.0.22-03-04: Registry missing/malformed fails closed.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


def _write_brief(
    project_root: Path,
    *,
    obpi_id: str,
    allowed_paths: list[str],
    declared_sensitivity: str | None = None,
    parent_adr: str = "ADR-test-fixture",
    status: str = "Draft",
) -> Path:
    obpi_dir = project_root / "docs" / "design" / "adr" / "foundation" / parent_adr / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    brief_path = obpi_dir / f"{obpi_id}.md"
    sensitivity_line = (
        f"sensitivity: {declared_sensitivity}\n" if declared_sensitivity is not None else ""
    )
    body = f"""---
id: {obpi_id}
parent: {parent_adr}
item: 1
lane: Heavy
status: {status}
{sensitivity_line}---

# {obpi_id}

## Allowed Paths

"""
    for path in allowed_paths:
        body += f"- `{path}` -- under test\n"
    body += "\n## Acceptance Criteria\n\n- [ ] REQ-test-01-01: trivial\n"
    brief_path.write_text(body, encoding="utf-8")
    return brief_path


def _write_registry(project_root: Path, content: object) -> Path:
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    registry_path = data_dir / "security_surfaces.json"
    if isinstance(content, str):
        registry_path.write_text(content, encoding="utf-8")
    else:
        registry_path.write_text(json.dumps(content), encoding="utf-8")
    return registry_path


def _write_grandfather(project_root: Path, brief_rel_paths: list[str]) -> Path:
    """Write the GHI #625 grandfather waiver file naming pre-cutover briefs."""
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    gf_path = data_dir / "sensitivity_floor_grandfather.json"
    gf_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "rationale": "test fixture",
                "grandfathered_briefs": brief_rel_paths,
            }
        ),
        encoding="utf-8",
    )
    return gf_path


_SAFE_REGISTRY: list[dict[str, object]] = [
    {
        "category": "ledger_integrity",
        "globs": ["src/gzkit/ledger.py", "src/gzkit/ledger_*.py"],
        "rationale": "Ledger writers — append-only invariant.",
    },
    {
        "category": "credential_handling",
        "globs": ["src/gzkit/**/*credential*.py"],
        "rationale": "Credential handlers.",
    },
]


class TestSensitivityFloor(unittest.TestCase):
    """Auto-detect floor fires when paths intersect the registry."""

    @covers("REQ-0.0.22-03-01")
    def test_intersecting_paths_force_security(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-test-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
            )

            findings = ta.audit_sensitivity_binding(root)

        # Rule (.gzkit/rules/security-sensitivity.md §§ 1-2, GHI #625): an
        # omitted declaration over a registered security overlap is FAIL-CLOSED,
        # not merely informational. With no grandfather file present, the
        # non-grandfathered omission must emit a `sensitivity-floor-violation`.
        violations = [
            f
            for f in findings
            if f.type == "sensitivity-floor-violation" and "OBPI-test-01" in f.artifact
        ]
        self.assertEqual(
            len(violations),
            1,
            f"Expected one fail-closed floor-violation for an undeclared overlap, got {findings}",
        )
        self.assertIn("security", violations[0].message.lower())

    @covers("REQ-0.0.22-03-02")
    def test_declared_security_no_intersection_accepted(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-test-02",
                allowed_paths=["docs/user/runbook.md"],
                declared_sensitivity="security",
            )

            findings = ta.audit_sensitivity_binding(root)

        escape_findings = [f for f in findings if f.type == "sensitivity-escape-attempt"]
        self.assertEqual(escape_findings, [], "Escalation MUST be accepted")

    @covers("REQ-0.0.22-03-03")
    def test_escape_attempt_emits_finding(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-test-03",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity="lite",
            )

            findings = ta.audit_sensitivity_binding(root)

        escape = [f for f in findings if f.type == "sensitivity-escape-attempt"]
        self.assertEqual(len(escape), 1, f"Expected exactly one escape finding, got {findings}")
        self.assertIn("OBPI-test-03", escape[0].artifact)
        self.assertIn("lite", escape[0].message)
        self.assertIn("security", escape[0].message)


class TestSensitivityFloorViolation(unittest.TestCase):
    """GHI #625: omission over a security overlap is fail-closed, with a grandfather cutover.

    The binding rule (.gzkit/rules/security-sensitivity.md §§ 1-2) makes an
    omitted declaration over a registered security overlap a fail-closed
    violation. Briefs authored before the cutover are grandfathered via
    data/sensitivity_floor_grandfather.json; new ones fail closed.
    """

    def test_omitted_declaration_over_overlap_fails_closed(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-new-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
            )
            # No grandfather file → the omission is a new escape, fail-closed.
            findings = ta.audit_sensitivity_binding(root)

        violations = [f for f in findings if f.type == "sensitivity-floor-violation"]
        self.assertEqual(len(violations), 1, f"Expected one floor-violation, got {findings}")
        self.assertIn("OBPI-new-01", violations[0].artifact)

    def test_grandfathered_brief_omission_is_waived(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            brief = _write_brief(
                root,
                obpi_id="OBPI-old-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
            )
            _write_grandfather(root, [brief.relative_to(root).as_posix()])
            findings = ta.audit_sensitivity_binding(root)

        violations = [f for f in findings if f.type == "sensitivity-floor-violation"]
        self.assertEqual(violations, [], "Grandfathered brief must NOT fail closed")

    def test_cli_path_omission_fails_closed(self):
        """Coupled-surface coherence: the gz validate --sensitivity path enforces too."""
        from gzkit.commands.validate_cmd import _sensitivity_records

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-cli-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
            )
            _records, findings = _sensitivity_records(root)

        violations = [f for f in findings if f.type == "sensitivity-floor-violation"]
        self.assertEqual(len(violations), 1, f"CLI path must fail closed too, got {findings}")

    def test_cli_path_grandfathered_omission_waived(self):
        from gzkit.commands.validate_cmd import _sensitivity_records

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            brief = _write_brief(
                root,
                obpi_id="OBPI-cli-02",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
            )
            _write_grandfather(root, [brief.relative_to(root).as_posix()])
            _records, findings = _sensitivity_records(root)

        violations = [f for f in findings if f.type == "sensitivity-floor-violation"]
        self.assertEqual(violations, [], "CLI path must waive grandfathered briefs")


class TestSensitivityTerminalBriefExemption(unittest.TestCase):
    """GHI #682: the auto-detect floor does not gate terminal-status briefs.

    A terminal brief (Completed/Validated/Abandoned/Withdrawn/...) is a sealed
    historical record whose Allowed Paths describe a tree that has moved on;
    re-gating it on the security floor asks a frozen brief a question about the
    present. Consistent with the same shared-predicate scoping applied to
    `--brief-command-shape` (GHI #550) and the reconcile engine (GHI #707).
    The exemption is status-scoped, not blanket: active briefs still fail closed.
    """

    def test_terminal_brief_over_overlap_is_not_gated(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-terminal-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
                status="Completed",
            )
            findings = ta.audit_sensitivity_binding(root)

        gated = [f for f in findings if "OBPI-terminal-01" in f.artifact]
        self.assertEqual(
            gated,
            [],
            f"A terminal (Completed) brief must not be gated by the floor, got {gated}",
        )

    def test_active_brief_over_same_overlap_still_gated(self):
        """Control: the exemption is status-scoped — Draft briefs still fail closed."""
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-active-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
                status="Draft",
            )
            findings = ta.audit_sensitivity_binding(root)

        violations = [
            f
            for f in findings
            if f.type == "sensitivity-floor-violation" and "OBPI-active-01" in f.artifact
        ]
        self.assertEqual(
            len(violations),
            1,
            f"An active (Draft) brief over the same overlap must still fail closed, got {findings}",
        )

    def test_cli_path_terminal_brief_not_gated(self):
        """Coupled-surface coherence: the gz validate --sensitivity path exempts terminal too."""
        from gzkit.commands.validate_cmd import _sensitivity_records

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)
            _write_brief(
                root,
                obpi_id="OBPI-cli-terminal-01",
                allowed_paths=["src/gzkit/ledger.py"],
                declared_sensitivity=None,
                status="Completed",
            )
            _records, findings = _sensitivity_records(root)

        gated = [f for f in findings if "OBPI-cli-terminal-01" in f.artifact]
        self.assertEqual(gated, [], f"CLI path must exempt terminal briefs too, got {gated}")


class TestSensitivityRegistry(unittest.TestCase):
    """Registry availability is fail-closed."""

    @covers("REQ-0.0.22-03-04")
    def test_missing_registry_fails_closed(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Brief exists but no registry file.
            _write_brief(
                root,
                obpi_id="OBPI-test-04",
                allowed_paths=["src/gzkit/ledger.py"],
            )

            findings = ta.audit_sensitivity_binding(root)

        registry_errors = [f for f in findings if f.type == "sensitivity-registry-missing"]
        self.assertEqual(
            len(registry_errors), 1, f"Expected fail-closed registry-missing, got {findings}"
        )
        self.assertIn("security_surfaces.json", registry_errors[0].artifact)

    @covers("REQ-0.0.22-03-04")
    def test_malformed_registry_fails_closed(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, "{ not json")
            _write_brief(
                root,
                obpi_id="OBPI-test-05",
                allowed_paths=["src/gzkit/ledger.py"],
            )

            findings = ta.audit_sensitivity_binding(root)

        malformed = [f for f in findings if f.type == "sensitivity-registry-malformed"]
        self.assertEqual(
            len(malformed), 1, f"Expected fail-closed registry-malformed, got {findings}"
        )

    @covers("REQ-0.0.22-03-04")
    def test_schema_invalid_registry_fails_closed(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, [{"category": "not_canonical", "globs": ["x"], "rationale": "x"}])
            _write_brief(
                root,
                obpi_id="OBPI-test-06",
                allowed_paths=["src/gzkit/ledger.py"],
            )

            findings = ta.audit_sensitivity_binding(root)

        malformed = [f for f in findings if f.type == "sensitivity-registry-malformed"]
        self.assertEqual(
            len(malformed),
            1,
            f"Expected fail-closed on Pydantic schema invalid registry, got {findings}",
        )


class TestSensitivityExplain(unittest.TestCase):
    """The explain helper predicts classification without disk side effects."""

    @covers("REQ-0.0.22-03-05")
    def test_explain_returns_prediction_payload(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)

            payload = ta.explain_sensitivity_for_paths(["src/gzkit/ledger.py", "tests/**"], root)

        self.assertEqual(payload["detected_sensitivity"], "security")
        self.assertIn("ledger_integrity", payload["matching_categories"])

    @covers("REQ-0.0.22-03-05")
    def test_explain_returns_none_when_no_intersection(self):
        from gzkit.governance import trust_audits as ta

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registry(root, _SAFE_REGISTRY)

            payload = ta.explain_sensitivity_for_paths(["docs/user/runbook.md"], root)

        self.assertIsNone(payload["detected_sensitivity"])
        self.assertEqual(payload["matching_categories"], ())


if __name__ == "__main__":
    unittest.main()
