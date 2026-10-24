"""The identity seam's grammar bodies: one per kind, every reader agreeing.

Drydock RO-2 tranche 1 (`docs/governance/harbor-ro2-identity-seam.md` § The seam,
item 1). Widths are settled once, in the seam, at the strict two digits the JSON
schemas and the REQ grammar already pinned. Measured 2026-10-18 before the
tightening: no OBPI, REQ or TASK id in the ledger, the briefs, the commit
trailers or the scenario tags uses another width, so the tightening rejects no
live id.
"""

import json
import re
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit import tasks, triangle
from gzkit.core import models
from gzkit.core.models import (
    ADR_FRONTMATTER_ID_PATTERN,
    ADR_ID_BODY,
    ADR_POOL_ID_BODY,
    ADR_SHORT_ID_BODY,
    OBPI_FRONTMATTER_ID_PATTERN,
    OBPI_ID_BODY,
    OBPI_SHORT_ID_BODY,
    REQ_ID_BODY,
    REQ_ID_BODY_PLAIN,
    TASK_ID_BODY,
    TASK_ID_BODY_PLAIN,
    TASK_SLUG_ID_BODY,
    AdrId,
    IdKind,
    ObpiId,
    ReqId,
    TaskId,
    id_kind,
    is_foundation_semver,
)

_SCHEMAS = Path(__file__).resolve().parents[1] / "src" / "gzkit" / "schemas"


def _full(body: str, value: str) -> bool:
    return re.fullmatch(body, value) is not None


class TestOneBodyPerKind(unittest.TestCase):
    """Each body accepts its kind's forms and refuses the others."""

    def test_adr_forms(self) -> None:
        cases = (
            (ADR_ID_BODY, "ADR-0.28.0-focused-context-loader", True),
            (ADR_ID_BODY, "ADR-0.28.0", False),
            (ADR_SHORT_ID_BODY, "ADR-0.28.0", True),
            (ADR_SHORT_ID_BODY, "ADR-0.28", False),
            (ADR_POOL_ID_BODY, "ADR-pool.chores-system-maturity-absorption", True),
            (ADR_POOL_ID_BODY, "ADR-pool", False),
            (ADR_ID_BODY, "ADR-pool.chores", False),
        )
        for body, value, expected in cases:
            with self.subTest(body=body, value=value):
                self.assertEqual(_full(body, value), expected)

    def test_obpi_forms_pin_a_two_digit_item(self) -> None:
        cases = (
            (OBPI_ID_BODY, "OBPI-0.28.0-01-context-core", True),
            (OBPI_ID_BODY, "OBPI-0.28.0-01", False),
            (OBPI_SHORT_ID_BODY, "OBPI-0.28.0-01", True),
            (OBPI_SHORT_ID_BODY, "OBPI-0.28.0-1", False),
            (OBPI_SHORT_ID_BODY, "OBPI-0.28.0-100", False),
        )
        for body, value, expected in cases:
            with self.subTest(body=body, value=value):
                self.assertEqual(_full(body, value), expected)

    def test_req_and_task_forms_pin_two_digit_components(self) -> None:
        cases = (
            (REQ_ID_BODY_PLAIN, "REQ-0.0.37-01-01", True),
            (REQ_ID_BODY_PLAIN, "REQ-0.0.37-1-1", False),
            (REQ_ID_BODY, "REQ-0.0.37-01-01", True),
            (TASK_ID_BODY_PLAIN, "TASK-0.20.0-01-01-01", True),
            (TASK_ID_BODY_PLAIN, "TASK-0.20.0-1-1-1", False),
            (TASK_ID_BODY, "TASK-0.20.0-01-01-01", True),
            (TASK_SLUG_ID_BODY, "TASK-ro2-seam", True),
            (TASK_SLUG_ID_BODY, "TASK-fix-git-log-encoding-#1257", True),
            (TASK_SLUG_ID_BODY, "TASK-Ro2", False),
        )
        for body, value, expected in cases:
            with self.subTest(body=body, value=value):
                self.assertEqual(_full(body, value), expected)

    def test_foundation_is_the_zero_zero_series(self) -> None:
        for semver, expected in (
            ("0.0.10", True),
            ("0.0.1", True),
            ("0.28.0", False),
            ("1.0.0", False),
        ):
            with self.subTest(semver=semver):
                self.assertEqual(is_foundation_semver(semver), expected)

    def test_kind_is_read_from_the_leading_token(self) -> None:
        cases = (
            ("ADR-0.28.0", IdKind.ADR),
            ("ADR-pool.chores", IdKind.ADR),
            ("OBPI-0.28.0-01", IdKind.OBPI),
            ("REQ-0.28.0-01-01", IdKind.REQ),
            ("TASK-ro2-seam", IdKind.TASK),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertIs(id_kind(value), expected)
        for value in ("GHI-12", "adr-0.1.0", "PRD-GZKIT-1.0.0", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                id_kind(value)


class TestReadersTakeTheirGrammarFromTheSeam(unittest.TestCase):
    """The strict parsers and the identity surfaces agree because they share bodies."""

    def test_triangle_reexports_the_req_body(self) -> None:
        self.assertIs(triangle.REQ_ID_BODY, models.REQ_ID_BODY)
        self.assertIs(triangle.REQ_ID_BODY_PLAIN, models.REQ_ID_BODY_PLAIN)

    def test_tasks_parser_refuses_a_width_the_seam_refuses(self) -> None:
        self.assertEqual(str(tasks.TaskId.parse("TASK-0.20.0-01-02-03")), "TASK-0.20.0-01-02-03")
        with self.assertRaises(ValueError):
            tasks.TaskId.parse("TASK-0.20.0-1-2-3")

    def test_identity_surfaces_refuse_a_width_the_seam_refuses(self) -> None:
        for model, bad in (
            (ObpiId, "OBPI-0.0.10-1"),
            (ReqId, "REQ-0.0.10-2-1"),
            (TaskId, "TASK-0.20.0-1-1-1"),
        ):
            with self.subTest(model=model.__name__), self.assertRaises(ValidationError):
                model.parse(bad)
        self.assertEqual(str(AdrId.parse("ADR-0.0.10")), "ADR-0.0.10")


class TestJsonSchemasTakeTheirPatternsFromTheSeam(unittest.TestCase):
    """Every id pattern the two OBPI schemas and the ADR schema declare is a seam pattern."""

    def _pattern(self, schema: str, *path: str) -> str:
        node = json.loads((_SCHEMAS / schema).read_text(encoding="utf-8"))
        for key in path:
            node = node[key]
        return node["pattern"]

    def test_obpi_schema(self) -> None:
        self.assertEqual(
            self._pattern("obpi.json", "properties", "frontmatter", "properties", "id"),
            OBPI_FRONTMATTER_ID_PATTERN,
        )

    def test_adr_schema(self) -> None:
        self.assertEqual(
            self._pattern("adr.json", "properties", "frontmatter", "properties", "id"),
            ADR_FRONTMATTER_ID_PATTERN,
        )

    def test_obpi_brief_structure_schema(self) -> None:
        schema = "obpi_brief_structure.json"
        node = json.loads((_SCHEMAS / schema).read_text(encoding="utf-8"))
        found = {
            match
            for match in re.findall(r'"pattern":\s*"([^"]+)"', json.dumps(node))
            if re.search(r"ADR|OBPI|REQ|TASK", match)
        }
        expected = {
            json.dumps(OBPI_FRONTMATTER_ID_PATTERN)[1:-1],
            json.dumps(f"^{ADR_ID_BODY}$")[1:-1],
            json.dumps(f"^{REQ_ID_BODY_PLAIN}$")[1:-1],
            json.dumps(f"^{TASK_ID_BODY_PLAIN}$")[1:-1],
        }
        self.assertEqual(found, expected)

    def test_identity_surfaces_use_the_seam_bodies(self) -> None:
        for model, body in (
            (AdrId, ADR_SHORT_ID_BODY),
            (ObpiId, OBPI_SHORT_ID_BODY),
            (ReqId, REQ_ID_BODY_PLAIN),
            (TaskId, TASK_ID_BODY_PLAIN),
        ):
            with self.subTest(model=model.__name__):
                metadata = model.model_fields["raw"].metadata
                self.assertIn(f"^{body}$", [getattr(m, "pattern", None) for m in metadata])

    def test_frontmatter_models_use_the_schema_patterns(self) -> None:
        adr = models.AdrFrontmatter.model_fields["id"].metadata
        obpi = models.ObpiFrontmatter.model_fields["id"].metadata
        self.assertIn(ADR_FRONTMATTER_ID_PATTERN, [getattr(m, "pattern", None) for m in adr])
        self.assertIn(OBPI_FRONTMATTER_ID_PATTERN, [getattr(m, "pattern", None) for m in obpi])


if __name__ == "__main__":
    unittest.main()
