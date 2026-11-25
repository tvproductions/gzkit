"""Templates never state Gate 5 as lane-, kind- or mode-scoped (GHI #1022, GHI #1358).

`AGENTS.md` § Gate Covenant: "Gate 5 is universal: it applies to every OBPI
completion in every lane, kind and sensitivity (ADR-0.0.36)". Every template
under `.gzkit/templates/` and its shipped twin under `src/gzkit/templates/`
seeds a brief, PRD or contract in gzkit and in every adopter, so a template
that scopes Gate 5 teaches the retired rule to every artifact made from it.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIRS = (REPO_ROOT / ".gzkit" / "templates", REPO_ROOT / "src" / "gzkit" / "templates")

_GATE5 = re.compile(r"gate\s*5", re.IGNORECASE)
_SCOPING = re.compile(
    r"\b(heavy|lite|foundation)\b|when required|parent lane|normal mode", re.IGNORECASE
)
_LANE_ONLY = re.compile(r"lane only", re.IGNORECASE)
_GATE_TABLE_ROW = re.compile(r"^\|\s*Gate\s*(\d)[^|]*\|\s*([^|]+?)\s*\|")
_CONDITIONAL_ATTESTOR = re.compile(
    r"(^- Attestor:|attestation).*(when required|otherwise|parent lane)", re.IGNORECASE
)


def _template_lines() -> list[tuple[str, int, str]]:
    found: list[tuple[str, int, str]] = []
    for root in TEMPLATE_DIRS:
        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(REPO_ROOT).as_posix()
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                found.append((rel, number, line))
    return found


def _scopes_gate5(line: str) -> bool:
    """Return True when *line* scopes Gate 5 or the attestation to a lane, kind or mode."""
    row = _GATE_TABLE_ROW.match(line)
    if row:
        return row.group(1) == "5" and row.group(2).lower() != "all"
    if _LANE_ONLY.search(line):
        return "Gate 5 applies in every lane" not in line
    if _CONDITIONAL_ATTESTOR.search(line):
        return True
    return bool(_GATE5.search(line) and _SCOPING.search(line))


def scoping_offenders(lines: list[tuple[str, int, str]]) -> list[str]:
    """Return every template line that states Gate 5 as scoped to a lane, kind or mode."""
    return [f"{rel}:{n}: {line.strip()}" for rel, n, line in lines if _scopes_gate5(line)]


class TestTemplateGate5Universal(unittest.TestCase):
    def test_the_scan_reaches_both_template_trees(self):
        rels = {rel for rel, _, _ in _template_lines()}
        self.assertIn(".gzkit/templates/obpi.md", rels)
        self.assertIn("src/gzkit/templates/obpi.md", rels)

    def test_no_template_scopes_gate_5(self):
        offenders = scoping_offenders(_template_lines())
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_the_retired_shapes_are_each_caught(self):
        retired = [
            "### Gate 5: Human (Heavy only)",
            "| Gate 5 (Human) | Heavy | Human attestation recorded |",
            "# Record attestation text here when required by parent lane",
            "<!-- Heavy lane only: -->",
            "- Attestor: `<name>` when required, otherwise `n/a`",
            "### Gate 5: Human (Heavy + Foundation)",
        ]
        for line in retired:
            with self.subTest(line=line):
                self.assertEqual(len(scoping_offenders([("t.md", 1, line)])), 1)

    def test_the_universal_shapes_pass(self):
        universal = [
            "### Gate 5: Human (all lanes)",
            "| Gate 5 (Human) | All | Human attestation recorded |",
            "| Gate 3 (Docs) | Heavy | Documentation updated |",
            "<!-- Heavy lane only: Gates 3 and 4. Gate 5 applies in every lane. -->",
            "- Attestor: `<name>`",
        ]
        for line in universal:
            with self.subTest(line=line):
                self.assertEqual(scoping_offenders([("t.md", 1, line)]), [])


if __name__ == "__main__":
    unittest.main()
