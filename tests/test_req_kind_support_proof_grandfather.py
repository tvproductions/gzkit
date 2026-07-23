"""Tests for the SUPPORT-channel grandfather cache loader (GHI #660).

`data/support_proof_grandfather.json` tolerates a fixed pre-cutover set of
SUPPORT REQs (GHI #647). A malformed or drifted-shape file must fail
closed, not silently degrade to an empty tolerated-set (which would flip
every pre-cutover REQ to enforced-fail-close with no operator signal).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError


class TestSupportProofGrandfather(unittest.TestCase):
    def test_missing_file_returns_empty_frozenset(self) -> None:
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            result = _support_proof_grandfather(project_root)

        self.assertEqual(result, frozenset())

    def test_valid_file_returns_grandfathered_reqs(self) -> None:
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "support_proof_grandfather.json").write_text(
                '{"_doc": "snapshot rationale", '
                '"grandfathered_reqs": ["REQ-0.0.1-01-01", "REQ-0.0.1-01-02"]}',
                encoding="utf-8",
            )

            result = _support_proof_grandfather(project_root)

        self.assertEqual(result, frozenset({"REQ-0.0.1-01-01", "REQ-0.0.1-01-02"}))

    def test_malformed_json_raises_instead_of_silently_emptying(self) -> None:
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "support_proof_grandfather.json").write_text(
                "not valid json", encoding="utf-8"
            )

            with self.assertRaises(ValidationError):
                _support_proof_grandfather(project_root)

    def test_missing_doc_rationale_is_tolerated(self) -> None:
        """``_doc`` is present on the real snapshot but not schema-mandated —
        a file without it still loads (only shape/type drift fails closed)."""
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "support_proof_grandfather.json").write_text(
                '{"grandfathered_reqs": ["REQ-0.0.1-01-01"]}', encoding="utf-8"
            )

            result = _support_proof_grandfather(project_root)

        self.assertEqual(result, frozenset({"REQ-0.0.1-01-01"}))

    def test_unknown_top_level_key_raises(self) -> None:
        """extra='forbid' catches drift/typos in the fixed two-key shape."""
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "support_proof_grandfather.json").write_text(
                '{"_doc": "x", "grandfathered_reqs": [], "typo_key": true}',
                encoding="utf-8",
            )

            with self.assertRaises(ValidationError):
                _support_proof_grandfather(project_root)

    def test_non_string_list_item_raises(self) -> None:
        from gzkit.req_kind_support import _support_proof_grandfather

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "support_proof_grandfather.json").write_text(
                '{"_doc": "x", "grandfathered_reqs": [1, 2]}', encoding="utf-8"
            )

            with self.assertRaises(ValidationError):
                _support_proof_grandfather(project_root)


if __name__ == "__main__":
    unittest.main()
