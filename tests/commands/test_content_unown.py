"""gz content unown command tests — attested ratchet-raise path (OBPI-0.35.0-04 Task 3).

Un-owning a section is the ONE move that raises the decrease-only unowned-byte
ratchet (`src/gzkit/content/ownership.py::record_unowned_total` refuses every
other attempt to raise it). ADR-0.35.0 § Decision item 3 names an undefined
reversal path as "the one agents invent" -- this command is the governed,
attested exception: the same corpus-attestation shape as `gz content retire`
(REQ-0.35.0-04-04), gating the one legitimate raise (REQ-0.35.0-04-05).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
from gzkit.content.ownership import load_declaration, measure_section_spans
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_SURFACE_TEXT = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "## Beta Section\n"
    "beta body\n"
)

_DECLARATION_PATH = Path(".gzkit") / "ownership" / "Doc.md.json"
_LEDGER_PATH = Path(".gzkit") / "ledger.jsonl"

# A genesis declaration (floor_event_id=None) is only load-bearing valid when
# its floor equals the summed span of its own declared-'unowned' sections
# (REQ-0.35.0-04-02) -- derive that sum from measure_section_spans, never
# hardcode it, so the default seed stays coherent regardless of
# _SURFACE_TEXT's exact byte layout. With the default alpha="corpus-owned",
# beta-section is the only section declared 'unowned' at seed time.
_SEED_FLOOR = measure_section_spans(_SURFACE_TEXT)["beta-section"]


def _seed_surface() -> None:
    Path("Doc.md").write_text(_SURFACE_TEXT, encoding="utf-8")


def _seed_declaration(*, alpha: str = "corpus-owned", floor: int | None = None) -> None:
    sections = {
        "doc-title": "corpus-owned",
        "alpha-section": alpha,
        "beta-section": "unowned",
    }
    if floor is None:
        spans = measure_section_spans(_SURFACE_TEXT)
        floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")
    _DECLARATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DECLARATION_PATH.write_text(
        json.dumps(
            {
                "surface": "Doc.md",
                "sections": sections,
                "unowned_byte_floor": floor,
                "measured_at": "2026-09-02T00:00:00Z",
                "floor_event_id": None,
            }
        ),
        encoding="utf-8",
    )


def _ledger_events() -> list[dict]:
    if not _LEDGER_PATH.exists():
        return []
    return [
        json.loads(line) for line in _LEDGER_PATH.read_text(encoding="utf-8").splitlines() if line
    ]


def _unown(runner: CliRunner, *, section: str = "alpha-section", attestor: str, reason: str):
    return runner.invoke(
        main,
        [
            "content",
            "unown",
            "Doc.md",
            "--section",
            section,
            "--attestor",
            attestor,
            "--reason",
            reason,
        ],
    )


class TestContentUnownFailClosed(unittest.TestCase):
    """REQ-0.35.0-04-04: empty/whitespace attestor or reason -> refuse, nothing written."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _assert_refused_byte_unchanged(
        self, *, section: str = "alpha-section", attestor: str, reason: str
    ) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration()
            before_bytes = _DECLARATION_PATH.read_bytes()
            before_ledger_count = len(_ledger_events())

            result = _unown(self._runner, section=section, attestor=attestor, reason=reason)

            self.assertNotEqual(result.exit_code, 0)
            after_bytes = _DECLARATION_PATH.read_bytes()
            self.assertEqual(
                before_bytes, after_bytes, "declaration must be byte-unchanged on refusal"
            )
            after_ledger_count = len(_ledger_events())
            self.assertEqual(
                before_ledger_count, after_ledger_count, "no ledger event may be emitted"
            )

    @covers("REQ-0.35.0-04-04")
    def test_empty_attestor_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="", reason="a real reason")

    @covers("REQ-0.35.0-04-04")
    def test_whitespace_only_attestor_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="   ", reason="a real reason")

    @covers("REQ-0.35.0-04-04")
    def test_empty_reason_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="g0", reason="")

    @covers("REQ-0.35.0-04-04")
    def test_whitespace_only_reason_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="g0", reason="   ")

    def test_unknown_section_id_is_refused(self) -> None:
        """An id naming no declared section is refused; nothing written.

        Would break if production stopped checking membership before
        mutating -- e.g. if an unknown id silently no-opped with exit 0, or
        wrote a new section entry instead of refusing.
        """
        self._assert_refused_byte_unchanged(
            section="does-not-exist", attestor="g0", reason="a real reason"
        )

    def test_already_unowned_section_is_refused(self) -> None:
        """A section already 'unowned' has nothing to raise the floor by.

        Would break if production stopped distinguishing 'corpus-owned' from
        other states before mutating -- e.g. if it re-raised the floor for an
        already-unowned section, double-counting its byte span.
        """
        self._assert_refused_byte_unchanged(
            section="beta-section", attestor="g0", reason="a real reason"
        )


class TestContentUnownRaisesTheFloor(unittest.TestCase):
    """REQ-0.35.0-04-05: attested raise-path un-owns a corpus-owned section."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-05")
    def test_section_becomes_unowned_and_floor_rises_by_its_span(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["sections"]["alpha-section"], "unowned")
            self.assertEqual(declaration["unowned_byte_floor"], _SEED_FLOOR + span)

    @covers("REQ-0.35.0-04-05")
    def test_ledger_event_carries_all_five_required_fields(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            events = [e for e in _ledger_events() if e.get("section") == "alpha-section"]
            self.assertEqual(len(events), 1, msg=_ledger_events())
            event = events[0]
            self.assertEqual(event["section"], "alpha-section")
            self.assertEqual(event["prior_unowned_byte_floor"], _SEED_FLOOR)
            self.assertEqual(event["new_unowned_byte_floor"], _SEED_FLOOR + span)
            self.assertEqual(event["attestor"], "g0")
            self.assertEqual(event["reason"], "moving to prose doc")


class TestContentUnownAttestedRoundTrip(unittest.TestCase):
    """REQ-0.35.0-04-02/-05: a `gz content unown` raise reloads cleanly.

    The chain-validation `load_declaration` now enforces (Stage-2 fix cycle,
    closing the adversary's direct-hand-edit finding) must not reject the
    ONE legitimate raise path it exists to protect -- the declaration
    `gz content unown` writes carries a `floor_event_id` that resolves
    against the very ledger event this same command emits.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-02")
    def test_attested_raise_reloads_cleanly_because_its_chain_resolves(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")
            self.assertEqual(result.exit_code, 0, msg=result.output)

            # The resulting declaration must reload through the SAME
            # fail-closed loader every other caller uses -- no special-cased
            # trust for the command that just wrote it.
            declaration = load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path.cwd())
            self.assertEqual(declaration.sections["alpha-section"], "unowned")
            self.assertIsNotNone(declaration.floor_event_id)


class TestContentUnownPartialFailure(unittest.TestCase):
    """Ledger write fails after the declaration write already succeeded.

    Layer-2 truth gap the command is honest about: exit 2 (not 1) signals
    "half happened" distinctly from every exit-1 refusal above, where the
    declaration is byte-unchanged.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_ledger_append_failure_exits_2_with_declaration_persisted(self) -> None:
        """Would break if production collapsed this branch into the exit-1
        refusal path, or rolled back the already-written declaration instead
        of leaving it (falsely claiming nothing happened when it did), or
        dropped the declaration path from the error message.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["sections"]["alpha-section"], "unowned")
            self.assertEqual(declaration["unowned_byte_floor"], _SEED_FLOOR + span)
            self.assertIn(_DECLARATION_PATH.as_posix(), result.output)


if __name__ == "__main__":
    unittest.main()
