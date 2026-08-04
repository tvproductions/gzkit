"""Tests for the req-kind grandfathering cache loader (GHI #544).

`data/req_kind_grandfathering.json` gates which REQs are exempt from the
BEHAVIOR proof-channel fail-close. A malformed or mistyped cache file must
surface as a fail-closed error, not silently fall back to an empty cache.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.req_kind import ReqKind
from tests.commands.common import SilencedConsoleTestCase


class TestLoadReqKindGrandfatheringCache(unittest.TestCase):
    def test_missing_file_returns_empty_cache(self) -> None:
        from gzkit.req_kind import load_req_kind_grandfathering_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            cache = load_req_kind_grandfathering_cache(project_root)

        self.assertEqual(cache, {})

    def test_valid_json_returns_parsed_cache(self) -> None:
        from gzkit.req_kind import load_req_kind_grandfathering_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "req_kind_grandfathering.json").write_text(
                '{"REQ-0.0.1-01-01": "SUPPORT"}', encoding="utf-8"
            )

            cache = load_req_kind_grandfathering_cache(project_root)

        self.assertEqual(cache, {"REQ-0.0.1-01-01": "SUPPORT"})

    def test_malformed_json_raises_instead_of_silently_emptying(self) -> None:
        """Truncated/invalid JSON must fail closed, not degrade to `{}`."""
        from gzkit.req_kind import load_req_kind_grandfathering_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "req_kind_grandfathering.json").write_text(
                '{"REQ-0.0.1-01-01": ', encoding="utf-8"
            )

            with self.assertRaises(ValidationError):
                load_req_kind_grandfathering_cache(project_root)

    def test_non_string_kind_value_raises(self) -> None:
        """A non-string kind value must fail closed."""
        from gzkit.req_kind import load_req_kind_grandfathering_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "req_kind_grandfathering.json").write_text(
                '{"REQ-0.0.1-01-01": 5}', encoding="utf-8"
            )

            with self.assertRaises(ValidationError):
                load_req_kind_grandfathering_cache(project_root)

    def _load_with_kind(self, raw_kind: str) -> dict[str, ReqKind]:
        """Write a one-entry cache carrying *raw_kind* and load it."""
        from gzkit.req_kind import load_req_kind_grandfathering_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "req_kind_grandfathering.json").write_text(
                json.dumps({"REQ-0.0.1-01-01": raw_kind}), encoding="utf-8"
            )
            return load_req_kind_grandfathering_cache(project_root)

    def test_kind_value_outside_the_taxonomy_raises(self) -> None:
        """An override naming no real kind must fail closed, not resolve to BEHAVIOR.

        The value domain of this cache is exactly `ReqKind`. A string that names
        no kind is an operator override that cannot be honoured; silently
        coercing it broadens BEHAVIOR proof-channel enforcement onto a REQ the
        operator explicitly exempted -- the failure this loader's fail-closed
        contract exists to prevent.
        """
        for typo in ("STRUCTURAL_FENCE", "behaviour", "FENCE", ""):
            with self.subTest(kind=typo), self.assertRaises(ValidationError):
                self._load_with_kind(typo)

    def test_kind_value_case_is_normalised_not_rejected(self) -> None:
        """Operators author `support` and `SUPPORT`; both name one kind."""
        from gzkit.req_kind import ReqKind

        for spelling in ("support", "SUPPORT", "Support"):
            with self.subTest(kind=spelling):
                self.assertEqual(
                    self._load_with_kind(spelling)["REQ-0.0.1-01-01"],
                    ReqKind.SUPPORT,
                )

    def test_hyphenated_fence_kind_round_trips(self) -> None:
        """`STRUCTURAL-FENCE` is the canonical wire spelling of the fence kind."""
        from gzkit.req_kind import ReqKind

        self.assertEqual(
            self._load_with_kind("structural-fence")["REQ-0.0.1-01-01"],
            ReqKind.STRUCTURAL_FENCE,
        )


class TestCoversCmdSurfacesMalformedCache(SilencedConsoleTestCase):
    """CLI-wiring regression: `gz covers` must not swallow a malformed cache."""

    def test_covers_cmd_raises_gz_cli_error_on_malformed_cache(self) -> None:
        from unittest.mock import patch

        from gzkit.commands import covers as covers_mod
        from gzkit.commands.common import GzCliError

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "design" / "adr").mkdir(parents=True)
            (project_root / "tests").mkdir()
            (project_root / "features").mkdir()
            data_dir = project_root / "data"
            data_dir.mkdir()
            (data_dir / "req_kind_grandfathering.json").write_text(
                "not valid json", encoding="utf-8"
            )

            with (
                patch.object(covers_mod, "get_project_root", return_value=project_root),
                patch.object(covers_mod, "scan_briefs", return_value=[]),
                patch.object(covers_mod, "scan_test_tree", return_value=[]),
                patch.object(covers_mod, "scan_feature_tree", return_value=[]),
                self.assertRaises(GzCliError),
            ):
                covers_mod.covers_cmd(target="OBPI-0.0.1-01-fixture", as_json=True)


if __name__ == "__main__":
    unittest.main()
