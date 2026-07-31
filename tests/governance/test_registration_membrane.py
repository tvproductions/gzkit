"""Tests for OBPI-0.34.0-05 REQ-04: the registration membrane (GHI #706).

Both `adr_created` ledger ingress points — `gz register-adrs` and first-run
`gz init` — must refuse to book a hand-placed `kind: foundation` ADR package
that is absent from the populated `data/foundation_grandfather.json`, while
every package in the manifest still books normally.

The guard is MANIFEST-AWARE, never a bare `kind: foundation` refusal: a bare
refusal would reject all 74 grandfathered foundations and contradict the
closure it enforces (brief Requirement 5).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from tests.commands.common import CliRunner, SilencedConsoleTestCase, _quick_init

_FOUNDATION_PACKAGE = (
    "---\n"
    "id: ADR-0.0.99-hand-placed-foundation\n"
    "parent: PRD-GZKIT-1.0.0\n"
    "lane: heavy\n"
    "kind: foundation\n"
    "semver: 0.0.99\n"
    "---\n\n"
    "# ADR-0.0.99: hand-placed foundation\n"
)


def _write_foundation_package(config: GzkitConfig) -> Path:
    """Place a `kind: foundation` ADR package on disk and return its path."""
    adr_dir = Path(config.paths.adrs) / "foundation"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / "ADR-0.0.99-hand-placed-foundation.md"
    adr_file.write_text(_FOUNDATION_PACKAGE, encoding="utf-8")
    return adr_file


def _write_manifest(*entries: str) -> None:
    """Write `data/foundation_grandfather.json` with identity-only entries."""
    manifest = Path("data")
    manifest.mkdir(parents=True, exist_ok=True)
    (manifest / "foundation_grandfather.json").write_text(
        json.dumps(
            [
                {
                    "id": entry,
                    "title": entry,
                    "semver": "0.0.99",
                    "frozen_at": "2026-07-30",
                }
                for entry in entries
            ]
        ),
        encoding="utf-8",
    )


class TestRegisterAdrsMembrane(unittest.TestCase):
    """REQ-0.34.0-05-04: the `gz register-adrs` ingress honors the membrane."""

    @covers("REQ-0.34.0-05-04")
    def test_ungrandfathered_foundation_books_no_adr_created(self) -> None:
        """A foundation package absent from the manifest must produce no ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _write_foundation_package(config)
            _write_manifest("ADR-0.0.10-some-other-foundation")

            runner.invoke(main, ["register-adrs"])

            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")
            self.assertNotIn(
                "ADR-0.0.99-hand-placed-foundation",
                ledger_text,
                "un-grandfathered kind: foundation must not enter Layer-2 (GHI #706)",
            )

    @covers("REQ-0.34.0-05-04")
    def test_grandfathered_foundation_books_normally(self) -> None:
        """A foundation package present in the manifest must still book."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            _write_foundation_package(config)
            _write_manifest("ADR-0.0.99-hand-placed-foundation")

            runner.invoke(main, ["register-adrs"])

            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")
            self.assertIn(
                "ADR-0.0.99-hand-placed-foundation",
                ledger_text,
                "the grandfathered roster must keep booking (brief Requirement 5)",
            )


class TestBomPrefixedFoundationRefused(unittest.TestCase):
    """A BOM before `---` must not defeat the membrane or the closure gate.

    Reading with `encoding="utf-8"` retains a leading U+FEFF, so the frontmatter
    parser misses the opening marker: the membrane sees "no kind" and admits the
    ADR, while `--taxonomy` sees "no frontmatter" and skips it. The package
    enters Layer-2 and the permanent gate stays green (Step-4b round-2 finding).
    Malformed input must be refused, never invisibly accepted.
    """

    @covers("REQ-0.34.0-05-04")
    def test_bom_prefixed_foundation_books_no_adr_created(self) -> None:
        """A BOM-prefixed un-grandfathered foundation must produce no ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "foundation"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.99-hand-placed-foundation.md").write_text(
                "﻿" + _FOUNDATION_PACKAGE, encoding="utf-8"
            )
            _write_manifest("ADR-0.0.10-some-other-foundation")

            runner.invoke(main, ["register-adrs"])

            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")

        self.assertNotIn(
            "ADR-0.0.99-hand-placed-foundation",
            ledger_text,
            "a BOM must not smuggle an un-grandfathered foundation past the membrane",
        )

    @covers("REQ-0.34.0-05-04")
    def test_interior_bom_foundation_books_no_adr_created(self) -> None:
        """A BOM AFTER the opening `---` must not smuggle the package past either.

        `utf-8-sig` strips U+FEFF only at byte zero; an interior one blinds the
        parser identically, and "no kind" reads as permission at every guard.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "foundation"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.99-hand-placed-foundation.md").write_text(
                _FOUNDATION_PACKAGE.replace("---", "---﻿", 1), encoding="utf-8"
            )
            _write_manifest("ADR-0.0.10-some-other-foundation")

            runner.invoke(main, ["register-adrs"])

            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")

        self.assertNotIn(
            "ADR-0.0.99-hand-placed-foundation",
            ledger_text,
            "an interior BOM must not smuggle an un-grandfathered foundation past the membrane",
        )

    @covers("REQ-0.34.0-05-04")
    def test_no_frontmatter_package_still_books(self) -> None:
        """Compatibility control: a legacy ADR with NO frontmatter must still book.

        BOM normalization must never CREATE frontmatter. A round-5 attempt to
        also strip leading blank space did exactly that — a `---` horizontal rule
        at the head of a pool document parsed as a frontmatter block — and was
        reverted. This control pins the compatibility direction.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "pool"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-pool.legacy-example.md").write_text(
                "# ADR: pool.legacy-example\n", encoding="utf-8"
            )
            _write_manifest("ADR-0.0.10-some-other-foundation")

            runner.invoke(main, ["register-adrs"])

            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")

        self.assertIn(
            "ADR-pool.legacy-example",
            ledger_text,
            "a frontmatter-less legacy ADR must still register",
        )

    @covers("REQ-0.34.0-05-04")
    def test_undecodable_package_is_refused_in_a_controlled_way(self) -> None:
        """A UTF-16 package must be refused with exit 0 and prose — never a crash.

        Asserting ledger absence alone would let an unhandled UnicodeDecodeError
        (which aborts the whole registration pass) masquerade as a controlled
        refusal.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "foundation"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.99-hand-placed-foundation.md").write_bytes(
                _FOUNDATION_PACKAGE.encode("utf-16")
            )
            _write_manifest("ADR-0.0.10-some-other-foundation")

            result = runner.invoke(main, ["register-adrs"])
            ledger_text = Path(config.paths.ledger).read_text(encoding="utf-8")

        self.assertEqual(result.exit_code, 0, "refusal must be controlled, not a crash")
        self.assertIn("Refused:", result.output, "the refusal must state what failed")
        self.assertNotIn(
            "ADR-0.0.99-hand-placed-foundation",
            ledger_text,
            "an undecodable package must be refused rather than booked on filename identity",
        )

    @covers("REQ-0.34.0-05-04")
    def test_bom_prefixed_foundation_caught_by_closure_gate(self) -> None:
        """The closure audit must still see a BOM-prefixed foundation."""
        from gzkit.governance.trust_audits.taxonomy import audit_foundation_closure

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs) / "foundation" / "ADR-0.0.99-hand-placed-foundation"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.0.99-hand-placed-foundation.md").write_text(
                "﻿" + _FOUNDATION_PACKAGE, encoding="utf-8"
            )
            _write_manifest("ADR-0.0.10-some-other-foundation")

            errors = audit_foundation_closure(Path().resolve())

        self.assertTrue(
            errors,
            "a BOM must not make the closure gate skip a foundation package",
        )


class TestInitMembrane(SilencedConsoleTestCase):
    """REQ-0.34.0-05-04: the first-run `gz init` ingress honors the same membrane.

    Silenced base: `_register_existing_artifacts` is driven directly rather than
    through `CliRunner.invoke`, so its Rich console output has no capture and
    leaks into the suite's stdout. Neither test asserts on that output.
    """

    def _run_first_run_registration(self) -> str:
        """Drive the first-run registration path and return the ledger text."""
        from gzkit.commands import init_cmd

        config = GzkitConfig.load(Path(".gzkit.json"))
        _write_foundation_package(config)
        ledger = Ledger(Path(config.paths.ledger))

        with patch.object(init_cmd, "_confirm", return_value=True):
            init_cmd._register_existing_artifacts(
                Path().resolve(), config.paths.design_root, ledger, "heavy"
            )

        return Path(config.paths.ledger).read_text(encoding="utf-8")

    @covers("REQ-0.34.0-05-04")
    def test_ungrandfathered_foundation_books_no_adr_created(self) -> None:
        """First-run init must not book a foundation package absent from the manifest."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_manifest("ADR-0.0.10-some-other-foundation")

            ledger_text = self._run_first_run_registration()

        self.assertNotIn(
            "ADR-0.0.99-hand-placed-foundation",
            ledger_text,
            "the gz init ingress is the second door of the same membrane (GHI #706)",
        )

    @covers("REQ-0.34.0-05-04")
    def test_grandfathered_foundation_books_normally(self) -> None:
        """First-run init must still book a manifest member."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_manifest("ADR-0.0.99-hand-placed-foundation")

            ledger_text = self._run_first_run_registration()

        self.assertIn(
            "ADR-0.0.99-hand-placed-foundation",
            ledger_text,
            "the grandfathered roster must keep booking at the init door too",
        )


if __name__ == "__main__":
    unittest.main()
