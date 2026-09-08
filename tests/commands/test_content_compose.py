"""gz content compose command tests — OBPI-0.0.37-21 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from implementation:
compose produces a candidate rendition + byte evidence, is fail-closed on
absent corpus / undeclared setpoint / invariant-floor violation, and NEVER
modifies rendered surfaces.
"""

from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.cli.main import main
from gzkit.content.corpus_store import append_entry
from gzkit.content.lineage import candidate_lineage_path
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.traceability import covers
from tests.commands.common import CliRunner
from tests.content.test_composer import _GEN_CONSUMER, _GEN_SURFACE, _GenerateCandidateFixtureMixin

_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["root"]},
    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
}

_INVARIANT_TEXT = "YOU OWN THE WORK COMPLETELY."
_COMPRESSIBLE_TEXT = "Prefer stdlib JSONL for append-only stores."


def _make_entry(
    entry_id: str, *, tier: str = "compressible", text: str = _COMPRESSIBLE_TEXT
) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="behavior-rules",
        tier=tier,
        classification="Ambiguous",
        text=text,
        origin="test",
        ts="2026-06-14T00:00:00Z",
    )


def _setup_project() -> None:
    """Seed the minimal project structure in the current isolated filesystem."""
    Path("data").mkdir()
    (Path("data") / "vendor-manifest.json").write_text(
        json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
    )
    Path(".gzkit").mkdir()
    Path(".gzkit", "corpus").mkdir()
    root = Path(".")
    append_entry(root, "AGENTS.md", _make_entry("e-inv", tier="invariant", text=_INVARIANT_TEXT))
    append_entry(root, "AGENTS.md", _make_entry("e-compressible"))


class _GeneratedFixtureBuilder(_GenerateCandidateFixtureMixin):
    """Bare instantiation of the shared generator fixture-writer mixin.

    ``_GenerateCandidateFixtureMixin`` (``tests/content/test_composer.py``) is
    designed for multiple inheritance with ``unittest.TestCase`` -- its
    ``setUp`` allocates a temp dir the composer-engine tests call ``self._root``.
    The CLI tests here instead need the same fixture shape written into
    ``CliRunner.isolated_filesystem()``'s cwd, so this subclass skips ``setUp``
    and sets ``_root`` directly -- reusing the fixture-writer methods rather
    than inventing a second fixture shape for the generated CLI path.
    """


_OWNED_CORPUS_TEXT = "Owned body from the corpus."


def _seed_generated_fixture(root: Path, *, manifest: dict | None = None) -> None:
    """Seed corpus + manifest + ownership declaration + prior rendition.

    Mirrors ``generate_candidate``'s own unit-test fixture
    (``tests/content/test_composer.py::_GenerateCandidateFixtureMixin``) so the
    CLI wiring tests exercise the identical generator preconditions rather
    than a hand-rolled approximation.
    """
    fixture = _GeneratedFixtureBuilder()
    fixture._root = root  # noqa: SLF001 -- bare fixture instantiation, see class docstring
    fixture._seed(manifest=manifest)  # noqa: SLF001
    append_entry(
        root,
        _GEN_SURFACE,
        CorpusEntry(
            id="e-owned",
            surface=_GEN_SURFACE,
            section="owned-section",
            tier="compressible",
            classification="Ambiguous",
            text=_OWNED_CORPUS_TEXT,
            origin="test",
            ts="2026-09-07T00:00:00Z",
        ),
    )


class TestContentComposeCmd(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-21-01")
    def test_compose_produces_candidate_and_byte_evidence(self) -> None:
        """Success path: candidate file written + byte evidence printed; exit 0."""
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "root",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "root.candidate.md"
            self.assertTrue(candidate_path.exists(), "Candidate file should be written")
            self.assertEqual(candidate_path.read_text(encoding="utf-8"), candidate_text)
            self.assertIn("Byte evidence", result.output)
            self.assertIn("setpoint=lite", result.output)

    @covers("REQ-0.0.37-21-04")
    def test_compose_exits_nonzero_on_absent_corpus(self) -> None:
        """Absent corpus → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            Path("data").mkdir()
            (Path("data") / "vendor-manifest.json").write_text(
                json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
            )
            Path(".gzkit").mkdir()
            Path("candidate.md").write_text("some text", encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "root",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "root.candidate.md"
            self.assertFalse(candidate_path.exists(), "No candidate should be written on error")

    @covers("REQ-0.0.37-21-04")
    def test_compose_exits_nonzero_on_undeclared_setpoint(self) -> None:
        """Undeclared (surface, consumer) setpoint → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\nsome content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "unknown-vendor",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            rend_dir = Path(".gzkit") / "renditions" / "AGENTS.md"
            self.assertFalse(
                (rend_dir / "unknown-vendor.candidate.md").exists(),
                "No candidate should be written on error",
            )

    @covers("REQ-0.0.37-21-03")
    @covers("REQ-0.0.37-21-04")
    def test_compose_refuses_invariant_floor_violation(self) -> None:
        """Candidate dropping an invariant-tier entry → exit 1, no candidate written."""
        with self._runner.isolated_filesystem():
            _setup_project()
            # Candidate text does NOT contain the invariant entry
            Path("candidate.md").write_text("some compressed content only", encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "root",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            candidate_path = Path(".gzkit") / "renditions" / "AGENTS.md" / "root.candidate.md"
            self.assertFalse(candidate_path.exists(), "No candidate on invariant violation")

    @covers("REQ-0.0.37-21-05")
    def test_compose_does_not_modify_rendered_surfaces(self) -> None:
        """After compose, AGENTS.md and CLAUDE.md are byte-unchanged."""
        with self._runner.isolated_filesystem():
            _setup_project()
            agents_text = "# AGENTS\nsome content"
            claude_text = "# CLAUDE\nsome content"
            Path("AGENTS.md").write_text(agents_text, encoding="utf-8")
            Path("CLAUDE.md").write_text(claude_text, encoding="utf-8")

            candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            args = [
                "content",
                "compose",
                "AGENTS.md",
                "--consumer",
                "root",
                "--candidate",
                "candidate.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(Path("AGENTS.md").read_text(encoding="utf-8"), agents_text)
            self.assertEqual(Path("CLAUDE.md").read_text(encoding="utf-8"), claude_text)

    @covers("REQ-0.35.0-05-08")
    def test_compose_reads_piped_stdin_when_not_a_tty(self) -> None:
        """No --candidate, stdin piped (not a tty): explicit path, stdin content used.

        Regression guard (ADR-0.35.0 Task 4 contract): the generated path is
        selected only when stdin IS a tty; a piped/redirected stdin must keep
        routing through the existing explicit-candidate ``compose()`` path so
        ``echo "$text" | gz content compose ...`` keeps working unchanged.
        """
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\npiped compressed content"

            with patch("sys.stdin", io.StringIO(candidate_text)):
                args = ["content", "compose", "AGENTS.md", "--consumer", "root"]
                result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            candidate_out = candidate_path(Path("."), "AGENTS.md", "root")
            self.assertTrue(candidate_out.exists())
            self.assertEqual(candidate_out.read_text(encoding="utf-8"), candidate_text)

    @covers("REQ-0.35.0-05-04")
    @covers("REQ-0.35.0-05-08")
    def test_compose_generates_candidate_and_lineage_on_tty_stdin(self) -> None:
        """No --candidate, stdin IS a tty: GENERATED path, stdin never read.

        The candidate is derived from the corpus via ``generate_candidate()``
        and the staged ``<consumer>.candidate.lineage.json`` artifact is
        written alongside it (REQ-0.35.0-05-04).
        """
        with self._runner.isolated_filesystem():
            _seed_generated_fixture(Path("."))
            fake_stdin = MagicMock()
            fake_stdin.isatty.return_value = True

            with patch("sys.stdin", fake_stdin):
                args = ["content", "compose", _GEN_SURFACE, "--consumer", _GEN_CONSUMER]
                result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            fake_stdin.read.assert_not_called()

            lineage_out = candidate_lineage_path(Path("."), _GEN_SURFACE, _GEN_CONSUMER)
            self.assertTrue(lineage_out.exists(), "Candidate lineage artifact should be written")
            document = json.loads(lineage_out.read_text(encoding="utf-8"))
            self.assertEqual(set(document), {"owned-section", "unowned-section"})
            for section in document.values():
                self.assertIn("owned", section)
                self.assertIn("entry_ids", section)
                self.assertIn("byte_span", section)

            candidate_out = candidate_path(Path("."), _GEN_SURFACE, _GEN_CONSUMER)
            self.assertTrue(candidate_out.exists())
            self.assertIn(_OWNED_CORPUS_TEXT, candidate_out.read_text(encoding="utf-8"))

    def test_compose_generates_candidate_when_stdin_is_empty_and_not_a_tty(self) -> None:
        """No --candidate, stdin not a tty but carries no content: GENERATED path.

        Regression guard: `/dev/null`-redirected invocations (CI, scripts,
        behave scenarios) present a non-tty stdin with zero bytes. Empty
        stdin IS "no caller-supplied text" per the brief's contract, so this
        must select the generated path exactly as an interactive tty does --
        never silently fall through to `compose()` against an empty string.
        """
        with self._runner.isolated_filesystem():
            _seed_generated_fixture(Path("."))

            with patch("sys.stdin", io.StringIO("")):
                args = ["content", "compose", _GEN_SURFACE, "--consumer", _GEN_CONSUMER]
                result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            lineage_out = candidate_lineage_path(Path("."), _GEN_SURFACE, _GEN_CONSUMER)
            self.assertTrue(lineage_out.exists(), "Candidate lineage artifact should be written")

    def test_compose_generates_candidate_when_stdin_is_whitespace_only(self) -> None:
        """Whitespace-only non-tty stdin is also "no caller-supplied text": GENERATED path."""
        with self._runner.isolated_filesystem():
            _seed_generated_fixture(Path("."))

            with patch("sys.stdin", io.StringIO("   \n\t\n")):
                args = ["content", "compose", _GEN_SURFACE, "--consumer", _GEN_CONSUMER]
                result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            lineage_out = candidate_lineage_path(Path("."), _GEN_SURFACE, _GEN_CONSUMER)
            self.assertTrue(lineage_out.exists(), "Candidate lineage artifact should be written")

    def test_compose_generated_path_refuses_off_route_consumer(self) -> None:
        """Generated path, off-route consumer: exit 1, no candidate, no lineage.

        The manifest below declares a temperature for ``vendorC`` (so a
        setpoint-only check would wrongly admit it) but no route -- pinning
        that the generated path is refused by ``generate_candidate``'s own
        route check (REQ-0.35.0-05-05), not merely because a setpoint happens
        to be undeclared.
        """
        manifest = {
            "content_type_routes": {"TestType": [_GEN_CONSUMER]},
            "content_type_temperatures": {
                "TestType": {_GEN_CONSUMER: "lite", "vendorC": "lite"},
            },
            "surface_content_types": {_GEN_SURFACE: "TestType"},
        }
        with self._runner.isolated_filesystem():
            _seed_generated_fixture(Path("."), manifest=manifest)
            fake_stdin = MagicMock()
            fake_stdin.isatty.return_value = True

            with patch("sys.stdin", fake_stdin):
                args = ["content", "compose", _GEN_SURFACE, "--consumer", "vendorC"]
                result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            candidate_out = candidate_path(Path("."), _GEN_SURFACE, "vendorC")
            self.assertFalse(candidate_out.exists(), "No candidate should be written on refusal")
            lineage_out = candidate_lineage_path(Path("."), _GEN_SURFACE, "vendorC")
            self.assertFalse(lineage_out.exists(), "No lineage should be written on refusal")

    def test_compose_persists_candidate_via_write_bytes_never_write_text(self) -> None:
        """The candidate is persisted through `write_bytes`, never `write_text`.

        Fix 3 (cross-vendor adversarial review): `Path.write_text` opens with
        `newline=None`, which performs platform-dependent line-ending
        translation (LF -> CRLF on Windows). That translation changes the
        PERSISTED byte length from the length the lineage's byte spans were
        computed over, invalidating every offset (adversary's simulation:
        generated=31244 persisted=31520). `write_bytes` never translates.
        Asserted behaviorally at the write boundary -- write_text on the exact
        candidate output path is refused; the persisted bytes must equal the
        in-memory candidate's own UTF-8 encoding exactly.
        """
        with self._runner.isolated_filesystem():
            _setup_project()
            candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
            Path("candidate.md").write_text(candidate_text, encoding="utf-8")

            candidate_out = candidate_path(Path("."), "AGENTS.md", "root")
            original_write_text = Path.write_text

            def _guarded_write_text(self_path: Path, *args: object, **kwargs: object) -> int:
                if self_path.name == candidate_out.name and self_path.parent.name == "AGENTS.md":
                    raise AssertionError(
                        f"{self_path} (the candidate output) must be persisted via "
                        "write_bytes, never write_text -- write_text's platform "
                        "newline translation would corrupt the byte offsets the "
                        "lineage was computed over."
                    )
                return original_write_text(self_path, *args, **kwargs)

            with patch.object(Path, "write_text", _guarded_write_text):
                args = [
                    "content",
                    "compose",
                    "AGENTS.md",
                    "--consumer",
                    "root",
                    "--candidate",
                    "candidate.md",
                ]
                result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(candidate_out.read_bytes(), candidate_text.encode("utf-8"))

    @covers("REQ-0.35.0-05-04")
    def test_explicit_candidate_removes_a_stale_generated_lineage(self) -> None:
        """A generated->explicit compose sequence does not leave a stale lineage map.

        Fix 4 (cross-vendor adversarial review): the explicit path overwrites
        `<consumer>.candidate.md` but previously left a prior GENERATED run's
        `<consumer>.candidate.lineage.json` untouched, so a supported
        generated -> explicit workflow left a provenance map describing
        DIFFERENT bytes than the new candidate (observed: lineage unchanged
        while candidate bytes changed underneath it).
        """
        with self._runner.isolated_filesystem():
            _seed_generated_fixture(Path("."))
            fake_stdin = MagicMock()
            fake_stdin.isatty.return_value = True
            with patch("sys.stdin", fake_stdin):
                args = ["content", "compose", _GEN_SURFACE, "--consumer", _GEN_CONSUMER]
                result = self._runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, msg=result.output)
            lineage_out = candidate_lineage_path(Path("."), _GEN_SURFACE, _GEN_CONSUMER)
            self.assertTrue(lineage_out.exists(), "Generated path should stage a lineage")

            explicit_text = f"{_INVARIANT_TEXT}\nhand-authored explicit candidate"
            Path("explicit.md").write_text(explicit_text, encoding="utf-8")
            args = [
                "content",
                "compose",
                _GEN_SURFACE,
                "--consumer",
                _GEN_CONSUMER,
                "--candidate",
                "explicit.md",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertFalse(
                lineage_out.exists(),
                "A stale generated-path lineage must not survive an explicit overwrite",
            )
