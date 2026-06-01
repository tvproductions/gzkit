"""Unit tests for ``gz context <ADR-ID>`` — OBPI-0.28.0-01 (context-core).

Each test maps to one REQ in OBPI-0.28.0-01-context-core's Acceptance
Criteria. Assertions derive from REQ semantics, not from a run of the
implementation (per ``.gzkit/rules/tests.md`` § "Tests assert semantics,
not strings").

@covers ADR-0.28.0-focused-context-loader
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, gate_checked_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _adr_root() -> Path:
    """Return the configured ADR root for the test workspace."""
    return Path(GzkitConfig.load(Path(".gzkit.json")).paths.adrs)


def _seed_adr(adr_root: Path, adr_id: str, *, body: str = "") -> Path:
    """Create a minimal ADR package on disk under ``adr_root``.

    Returns the ADR file path. The package layout matches the foundation /
    pre-release shape used by ``resolve_adr_file``: ``<adr_root>/<bucket>/
    <ADR-ID>/<ADR-ID>.md`` plus an ``obpis/`` directory.
    """
    bucket = "foundation" if adr_id.startswith("ADR-0.0.") else "pre-release"
    pkg_dir = adr_root / bucket / adr_id
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "obpis").mkdir(exist_ok=True)
    adr_file = pkg_dir / f"{adr_id}.md"
    adr_file.write_text(
        body or f"---\nid: {adr_id}\nkind: foundation\nlane: lite\n---\n\n# {adr_id}: seeded\n",
        encoding="utf-8",
    )
    return adr_file


def _seed_obpi(adr_file: Path, item: int, slug: str, body: str = "") -> Path:
    """Create a minimal OBPI brief under the ADR's ``obpis/`` directory."""
    pkg_dir = adr_file.parent
    semver = adr_file.stem.removeprefix("ADR-").split("-", 1)[0]
    obpi_id = f"OBPI-{semver}-{item:02d}-{slug}"
    brief_path = pkg_dir / "obpis" / f"{obpi_id}.md"
    brief_path.write_text(
        body or f"---\nid: {obpi_id}\nlane: Lite\n---\n\n# {obpi_id}: seeded\n",
        encoding="utf-8",
    )
    return brief_path


class TestContextCmdCore(unittest.TestCase):
    """REQ-derived tests for ``gz context <ADR-ID>``."""

    @covers("REQ-0.28.0-01-01")
    def test_help_documents_adr_positional(self) -> None:
        """REQ-01: gz context --help exits 0 and documents <ADR-ID>."""
        runner = CliRunner()
        result = runner.invoke(main, ["context", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ADR-ID", result.output.upper())

    @covers("REQ-0.28.0-01-02")
    def test_resolves_adr_and_exits_zero(self) -> None:
        """REQ-02: For a valid ADR ID, exits 0 with stdout output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(result.output.strip(), "expected non-empty stdout")

    @covers("REQ-0.28.0-01-03")
    def test_payload_contains_adr_body_verbatim(self) -> None:
        """REQ-03: Payload contains the target ADR body verbatim."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            sentinel = "SENTINEL_ADR_BODY_TOKEN_4471"
            body = (
                f"---\nid: ADR-0.0.99\nkind: foundation\nlane: lite\n---\n\n"
                f"# ADR-0.0.99: seeded\n\n{sentinel}\n"
            )
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99", body=body)
            _seed_obpi(adr_file, 1, "seeded-unit")
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            self.assertIn(sentinel, result.output)

    @covers("REQ-0.28.0-01-04")
    def test_payload_contains_all_obpi_briefs(self) -> None:
        """REQ-04: Payload includes every OBPI brief body, delimited by OBPI ID heading."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(
                adr_file,
                1,
                "first",
                body="---\nid: OBPI-0.0.99-01-first\nlane: Lite\n---\n\nBRIEF_TOKEN_ALPHA\n",
            )
            _seed_obpi(
                adr_file,
                2,
                "second",
                body="---\nid: OBPI-0.0.99-02-second\nlane: Lite\n---\n\nBRIEF_TOKEN_BETA\n",
            )
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            self.assertIn("BRIEF_TOKEN_ALPHA", result.output)
            self.assertIn("BRIEF_TOKEN_BETA", result.output)
            self.assertIn("OBPI-0.0.99-01-first", result.output)
            self.assertIn("OBPI-0.0.99-02-second", result.output)

    @covers("REQ-0.28.0-01-05")
    def test_payload_lists_covers_test_paths_grouped_by_req(self) -> None:
        """REQ-05: test files are listed AND grouped by the REQ they cover.

        Two tests cover two distinct REQs; the payload must render a per-REQ
        group header for each (the "grouped by REQ" clause) with the file path
        nested under its own REQ — not a flat undifferentiated list.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            test_dir = Path("tests/seeded_context")
            test_dir.mkdir(parents=True)
            (test_dir / "__init__.py").write_text("", encoding="utf-8")
            (test_dir / "test_seeded.py").write_text(
                "from gzkit.traceability import covers\n"
                "import unittest\n\n"
                "class T(unittest.TestCase):\n"
                "    @covers('REQ-0.0.99-01-01')\n"
                "    def test_x(self) -> None:\n"
                "        self.assertTrue(True)\n\n"
                "    @covers('REQ-0.0.99-01-02')\n"
                "    def test_y(self) -> None:\n"
                "        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            self.assertIn("test_seeded.py", result.output)
            # Grouped by REQ: each covered REQ gets its own group header.
            self.assertIn("REQ-0.0.99-01-01", result.output)
            self.assertIn("REQ-0.0.99-01-02", result.output)
            # The REQ-01 group header precedes the REQ-02 group header
            # (sorted grouping), proving per-REQ structure, not a flat list.
            self.assertLess(
                result.output.index("REQ-0.0.99-01-01"),
                result.output.index("REQ-0.0.99-01-02"),
            )

    @covers("REQ-0.28.0-01-06")
    def test_payload_governance_current_gate_derives_from_ledger(self) -> None:
        """REQ-06: governance-rules section names lane, lifecycle, current gate,
        and next action — with the current gate sourced from LEDGER state, not
        the frontmatter ``status:`` field (AGENTS.md Never-rule #7).

        The fixture forces frontmatter and ledger to disagree: frontmatter
        declares ``status: Completed`` (a status-derived heuristic would map that
        to Gate 5), while the ledger records only gate 2 cleared. A ledger-sourced
        renderer must show Gate 2 and must not echo the frontmatter-implied Gate 5.
        This assertion fails for any implementation that derives the gate from
        frontmatter — it pins the value and its source, not mere string presence.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            body = (
                "---\nid: ADR-0.0.99\nkind: foundation\nlane: lite\n"
                "status: Completed\n---\n\n# ADR-0.0.99: seeded\n"
            )
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99", body=body)
            _seed_obpi(adr_file, 1, "seeded-unit")
            config = GzkitConfig.load(Path(".gzkit.json"))
            ledger = Ledger(Path(config.paths.ledger))
            ledger.append(
                gate_checked_event(
                    adr_id="ADR-0.0.99",
                    gate=2,
                    status="pass",
                    command="uv run -m unittest",
                    returncode=0,
                )
            )
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            lower = result.output.lower()
            self.assertIn("governance rules", lower)
            self.assertIn("lane", lower)
            self.assertIn("lifecycle", lower)
            self.assertIn("next required action", lower)
            # Gate is ledger-sourced: the highest gate cleared in the ledger (2),
            # NOT the frontmatter-status mapping (which would render Gate 5).
            self.assertIn("Gate 2", result.output)
            self.assertNotIn("Gate 5", result.output)

    @covers("REQ-0.28.0-01-07")
    def test_unresolvable_adr_id_exits_nonzero_with_blockers(self) -> None:
        """REQ-07: Unresolvable ADR ID exits non-zero with BLOCKERS: stderr message."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["context", "ADR-9.9.9-does-not-exist"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("BLOCKERS", result.output)
            # REQ-07: the message must NAME the missing ADR, not just fail.
            self.assertIn("ADR-9.9.9-does-not-exist", result.output)

    @covers("REQ-0.28.0-01-08")
    def test_payload_is_plain_markdown_no_ansi(self) -> None:
        """REQ-08: Payload contains no ANSI escapes — pipeable to any harness."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            # REQ-08 forbids terminal-control characters. ANSI sequences
            # all begin with ESC (\x1b); asserting its absence is the REQ
            # semantic. (A redundant duplicate embedding a raw ESC byte in
            # source was removed; ``[`` is valid Markdown and is not forbidden.)
            self.assertNotIn("\x1b[", result.output)


class TestContextCmdSlim(unittest.TestCase):
    """REQ-derived tests for ``gz context --slim <ADR-ID>``."""

    @covers("REQ-0.28.0-02-01")
    def test_help_documents_slim_flag(self) -> None:
        """REQ-01: gz context --help exits 0 and documents --slim."""
        runner = CliRunner()
        result = runner.invoke(main, ["context", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--slim", result.output)

    @covers("REQ-0.28.0-02-02")
    def test_slim_omits_governance_section(self) -> None:
        """REQ-02: --slim payload omits the governance-rules section entirely."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            result = runner.invoke(main, ["context", "--slim", "ADR-0.0.99"])
            self.assertEqual(result.exit_code, 0)
            lower = result.output.lower()
            self.assertNotIn("governance rules", lower)
            self.assertNotIn("lifecycle", lower)
            self.assertNotIn("current gate", lower)
            self.assertNotIn("next required action", lower)

    @covers("REQ-0.28.0-02-03")
    def test_slim_preserves_adr_body_and_obpi_briefs(self) -> None:
        """REQ-03: --slim preserves ADR body and OBPI brief bodies (purely subtractive)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            sentinel_adr = "SENTINEL_ADR_SLIM_4472"
            body = (
                f"---\nid: ADR-0.0.99\nkind: foundation\nlane: lite\n---\n\n"
                f"# ADR-0.0.99: seeded\n\n{sentinel_adr}\n"
            )
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99", body=body)
            _seed_obpi(
                adr_file,
                1,
                "seeded-unit",
                body="---\nid: OBPI-0.0.99-01-seeded-unit\nlane: Lite\n---\n\nBRIEF_SLIM_TOKEN\n",
            )
            result = runner.invoke(main, ["context", "--slim", "ADR-0.0.99"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(sentinel_adr, result.output)
            self.assertIn("BRIEF_SLIM_TOKEN", result.output)

    @covers("REQ-0.28.0-02-04")
    def test_slim_delta_is_only_governance_section(self) -> None:
        """REQ-04: The only delta between default and --slim is the governance-rules section."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            default_output = runner.invoke(main, ["context", "ADR-0.0.99"]).output
            slim_output = runner.invoke(main, ["context", "--slim", "ADR-0.0.99"]).output
            # Byte-level subtractive proof: the slim payload is a strict PREFIX
            # of the default payload (governance is appended last), so the entire
            # delta is the tail bytes that follow the slim prefix.
            self.assertTrue(
                default_output.startswith(slim_output),
                "slim payload is not a byte-prefix of the default payload",
            )
            delta = default_output[len(slim_output) :]
            self.assertGreater(len(delta), 0, "default and slim are identical")
            # REQ-04: the delta IS the governance-rules section — nothing else.
            # It opens with the governance header and carries all four fields.
            self.assertTrue(
                delta.lstrip().startswith("---"),
                f"delta does not open with the governance section: {delta!r}",
            )
            self.assertIn("## Governance rules", delta)
            for field in (
                "**Lane:**",
                "**Lifecycle:**",
                "**Current gate:**",
                "**Next required action:**",
            ):
                self.assertIn(field, delta)

    @covers("REQ-0.28.0-02-05")
    def test_obpi01_default_mode_still_includes_governance_section(self) -> None:
        """REQ-05: OBPI-01 contract preserved — default mode payload includes governance section."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_file = _seed_adr(_adr_root(), "ADR-0.0.99")
            _seed_obpi(adr_file, 1, "seeded-unit")
            result = runner.invoke(main, ["context", "ADR-0.0.99"])
            lower = result.output.lower()
            self.assertIn("governance rules", lower)
            self.assertIn("lane", lower)
            self.assertIn("lifecycle", lower)


if __name__ == "__main__":
    unittest.main()
