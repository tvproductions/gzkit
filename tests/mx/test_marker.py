"""Unit tests for the MX marker module (OBPI-0.0.74-01).

The marker is the single filesystem truth-source for Maintenance Hangar mode:
its presence means MX==TRUE, and it is valid only when bound to a real
``mx_session_opened`` ledger event the tool wrote.

REQ-0.0.74-01-01 (presence + no-gzkit-internal read) and REQ-0.0.74-01-02
(ledger-binding void rule) are BEHAVIOR REQs proven by the ``@covers``-decorated
methods below. REQ-0.0.74-01-03 is a [structural-fence] REQ — its proof channel
is the parent ADR § Boundary Invariants #1 (single MX truth-source) per
ADR-0.0.59, not a ``@covers`` test; ``test_marker_path_is_single_truth_source``
backs it behaviorally but is intentionally not decorated as the fence's proof.
"""

import ast
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _write_ledger(root: Path, events: list[dict]) -> None:
    path = root / ".gzkit" / "ledger.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


class TestMarkerPresence(unittest.TestCase):
    """REQ-0.0.74-01-01: presence == MX==TRUE; no-gzkit-internal robust read."""

    @covers("REQ-0.0.74-01-01")
    def test_absent_marker_is_not_active(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            self.assertFalse(marker.is_active(root))
            self.assertIsNone(marker.read(root))

    @covers("REQ-0.0.74-01-01")
    def test_present_marker_is_active(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="s-1"), root)
            self.assertTrue(marker.is_active(root))

    @covers("REQ-0.0.74-01-01")
    def test_write_read_roundtrip_preserves_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            m = Marker(
                session_id="s-42",
                opened_at="2026-06-20T00:00:00Z",
                reason="re-torque freshness gate",
                attestor="g0",
                inspection_scope=["ADR-0.0.37", "ADR-0.0.74"],
            )
            marker.write(m, root)
            self.assertEqual(marker.read(root), m)

    @covers("REQ-0.0.74-01-01")
    def test_malformed_marker_reads_as_none_but_is_present(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.marker_path(root).write_text("{not json", encoding="utf-8")
            self.assertTrue(marker.is_active(root))  # present on disk...
            self.assertIsNone(marker.read(root))  # ...but unparseable

    @covers("REQ-0.0.74-01-01")
    def test_marker_module_imports_no_gzkit_internals(self) -> None:
        # The "reads even when gzkit is the patient" guarantee: marker.py must
        # not import any gzkit.* subsystem, so a broken/mid-repair gz module
        # can't break the marker read. pydantic + stdlib are fine — pydantic is
        # a pinned core dependency, as present as the interpreter wherever gzkit
        # runs, so it is not "the patient".
        source = Path(marker.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        gzkit_imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "gzkit" or alias.name.startswith("gzkit."):
                        gzkit_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    gzkit_imports.append(f"<relative level={node.level}>")
                elif node.module and (node.module == "gzkit" or node.module.startswith("gzkit.")):
                    gzkit_imports.append(node.module)
        self.assertEqual(
            gzkit_imports,
            [],
            f"marker.py must not import gzkit internals; found {gzkit_imports}",
        )

    def test_marker_path_is_single_truth_source(self) -> None:
        # Backs REQ-0.0.74-01-03 (structural-fence): the path resolves through
        # marker_path() to .gzkit/mx.json under the project root — one source.
        # Intentionally not @covers-decorated: the fence's proof channel is the
        # parent ADR § Boundary Invariants #1, not a test (ADR-0.0.59).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            self.assertEqual(marker.marker_path(root), root / ".gzkit" / "mx.json")


class TestMarkerLedgerBinding(unittest.TestCase):
    """REQ-0.0.74-01-02: marker is void unless bound to a real mx_session_opened."""

    @covers("REQ-0.0.74-01-02")
    def test_handcreated_marker_with_no_event_is_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="forged"), root)
            _write_ledger(root, [{"event": "artifact_edited", "session_id": "other"}])
            self.assertTrue(marker.is_active(root))  # present
            self.assertFalse(marker.is_valid(root))  # but void

    @covers("REQ-0.0.74-01-02")
    def test_marker_with_no_ledger_file_is_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="s-1"), root)
            self.assertFalse(marker.is_valid(root))

    @covers("REQ-0.0.74-01-02")
    def test_marker_bound_to_open_session_is_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="s-1"), root)
            _write_ledger(root, [{"event": "mx_session_opened", "session_id": "s-1"}])
            self.assertTrue(marker.is_valid(root))

    @covers("REQ-0.0.74-01-02")
    def test_marker_with_mismatched_session_id_is_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="s-1"), root)
            _write_ledger(root, [{"event": "mx_session_opened", "session_id": "s-2"}])
            self.assertFalse(marker.is_valid(root))

    @covers("REQ-0.0.74-01-02")
    def test_closed_session_voids_the_marker(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            marker.write(Marker(session_id="s-1"), root)
            _write_ledger(
                root,
                [
                    {"event": "mx_session_opened", "session_id": "s-1"},
                    {"event": "mx_session_closed", "session_id": "s-1"},
                ],
            )
            self.assertFalse(marker.is_valid(root))

    @covers("REQ-0.0.74-01-02")
    def test_absent_marker_is_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(root, [{"event": "mx_session_opened", "session_id": "s-1"}])
            self.assertFalse(marker.is_valid(root))  # no marker file


if __name__ == "__main__":
    unittest.main()
