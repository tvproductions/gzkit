"""Orphaned-implementation trust audit (GHI #438).

Fail-closed when a non-completed OBPI brief has ledger evidence of a
lock-claim, allowed-path artifact edits, and a force-release without an
intervening ``obpi_completion_*`` event — the silent broken state
reproduced in the ADR-0.0.31 closeout (OBPI-0.0.31-02).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.orphaned_implementation import (
    audit_orphaned_implementation,
)

_BRIEF_TEMPLATE = """---
id: {obpi_id}
parent: ADR-0.0.99-fixture
item: 1
lane: Lite
status: {status}
---

# {obpi_id}

## Allowed Paths

{allowed_paths}

{extra_body}
"""


def _write_brief(
    root: Path,
    obpi_id: str,
    status: str,
    allowed: list[str],
    extra_body: str = "",
) -> Path:
    parent = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.99-fixture" / "obpis"
    parent.mkdir(parents=True, exist_ok=True)
    brief = parent / f"{obpi_id}.md"
    bullets = "\n".join(f"- `{path}`" for path in allowed)
    brief.write_text(
        _BRIEF_TEMPLATE.format(
            obpi_id=obpi_id,
            status=status,
            allowed_paths=bullets,
            extra_body=extra_body,
        ),
        encoding="utf-8",
    )
    return brief


def _write_ledger(root: Path, events: list[dict]) -> Path:
    ledger = root / ".gzkit" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        "\n".join(json.dumps(ev) for ev in events) + "\n",
        encoding="utf-8",
    )
    return ledger


def _claim(obpi_id: str, ts: str) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_lock_claimed",
        "id": obpi_id,
        "ts": ts,
        "agent": "test-agent",
    }


def _release(obpi_id: str, ts: str, force: bool) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_lock_released",
        "id": obpi_id,
        "ts": ts,
        "agent": "test-agent",
        "force": force,
    }


def _edited(path: str, ts: str) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "artifact_edited",
        "id": path,
        "ts": ts,
        "path": path,
    }


def _completion(obpi_id: str, ts: str) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_completion_uncovered_accept",
        "id": obpi_id,
        "ts": ts,
        "obpi_id": obpi_id,
        "req_id": "REQ-0.0.99-01-01",
        "operator": "Test Operator",
        "rationale": "test",
        "acceptance_type": "agent-relayed-operator-attestation",
    }


class TestOrphanedImplementation(unittest.TestCase):
    def test_no_adr_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_completed_obpi_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-01-x", "Completed", ["docs/sample.md"])
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-01-x", "2026-05-10T10:00:00+00:00"),
                    _edited("docs/sample.md", "2026-05-10T10:30:00+00:00"),
                    _release("OBPI-0.0.99-01-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_draft_obpi_with_no_lock_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-02-x", "Draft", ["docs/sample.md"])
            _write_ledger(root, [])
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_orphaned_implementation_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                "OBPI-0.0.99-03-x",
                "Draft",
                ["docs/governance/advisory-rules-audit.md"],
            )
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-03-x", "2026-05-10T11:02:27+00:00"),
                    _edited(
                        "docs/governance/advisory-rules-audit.md",
                        "2026-05-10T11:30:00+00:00",
                    ),
                    _release(
                        "OBPI-0.0.99-03-x",
                        "2026-05-10T12:04:25+00:00",
                        force=True,
                    ),
                ],
            )
            errors = audit_orphaned_implementation(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "orphaned_implementation")
            self.assertIn("OBPI-0.0.99-03-x", errors[0].message)
            self.assertIn("docs/governance/advisory-rules-audit.md", errors[0].message)
            self.assertIn("--from=verify", errors[0].message)

    def test_completion_event_between_claim_release_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-04-x", "Draft", ["docs/sample.md"])
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-04-x", "2026-05-10T10:00:00+00:00"),
                    _edited("docs/sample.md", "2026-05-10T10:30:00+00:00"),
                    _completion("OBPI-0.0.99-04-x", "2026-05-10T10:45:00+00:00"),
                    _release("OBPI-0.0.99-04-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_non_force_release_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-05-x", "Draft", ["docs/sample.md"])
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-05-x", "2026-05-10T10:00:00+00:00"),
                    _edited("docs/sample.md", "2026-05-10T10:30:00+00:00"),
                    _release("OBPI-0.0.99-05-x", "2026-05-10T11:00:00+00:00", force=False),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_edits_outside_allowed_paths_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-06-x", "Draft", ["src/gzkit/foo.py"])
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-06-x", "2026-05-10T10:00:00+00:00"),
                    _edited("docs/unrelated.md", "2026-05-10T10:30:00+00:00"),
                    _release("OBPI-0.0.99-06-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_skip_marker_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                "OBPI-0.0.99-07-x",
                "Draft",
                ["docs/sample.md"],
                extra_body="<!-- gz-validate-skip: orphaned-implementation GHI-999 -->\n",
            )
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-07-x", "2026-05-10T10:00:00+00:00"),
                    _edited("docs/sample.md", "2026-05-10T10:30:00+00:00"),
                    _release("OBPI-0.0.99-07-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_glob_allowed_path_root_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                "OBPI-0.0.99-08-x",
                "Draft",
                ["src/gzkit/**/*.py"],
            )
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-08-x", "2026-05-10T10:00:00+00:00"),
                    _edited("src/gzkit/governance/foo.py", "2026-05-10T10:30:00+00:00"),
                    _release("OBPI-0.0.99-08-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            errors = audit_orphaned_implementation(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("src/gzkit/governance/foo.py", errors[0].message)

    def test_backslash_path_in_ledger_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                "OBPI-0.0.99-09-x",
                "Draft",
                ["docs/design/adr/foundation/ADR-0.0.99-fixture/audit/AUDIT.md"],
            )
            _write_ledger(
                root,
                [
                    _claim("OBPI-0.0.99-09-x", "2026-05-10T10:00:00+00:00"),
                    _edited(
                        "docs\\design\\adr\\foundation\\ADR-0.0.99-fixture\\audit\\AUDIT.md",
                        "2026-05-10T10:30:00+00:00",
                    ),
                    _release("OBPI-0.0.99-09-x", "2026-05-10T11:00:00+00:00", force=True),
                ],
            )
            errors = audit_orphaned_implementation(root)
            self.assertEqual(len(errors), 1)

    def test_edit_outside_lock_window_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(root, "OBPI-0.0.99-10-x", "Draft", ["docs/sample.md"])
            _write_ledger(
                root,
                [
                    _edited("docs/sample.md", "2026-05-10T09:00:00+00:00"),
                    _claim("OBPI-0.0.99-10-x", "2026-05-10T10:00:00+00:00"),
                    _release("OBPI-0.0.99-10-x", "2026-05-10T11:00:00+00:00", force=True),
                    _edited("docs/sample.md", "2026-05-10T12:00:00+00:00"),
                ],
            )
            self.assertEqual(audit_orphaned_implementation(root), [])

    def test_real_project_passes(self) -> None:
        from gzkit.commands.common import get_project_root

        root = get_project_root()
        errors = audit_orphaned_implementation(root)
        self.assertEqual(
            errors,
            [],
            f"orphaned-implementation audit reported findings on the real project: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
