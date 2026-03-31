"""Tests for tier-portable identity surface models (ADR-0.0.10, OBPI-0.0.10-02).

Covers: AdrId, ObpiId, ReqId, TaskId, EvidenceId parse/validate,
ID portability, frozen model immutability, IDENTITY_MODELS mapping.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.core.models import (
    IDENTITY_MODELS,
    AdrId,
    EvidenceId,
    ObpiId,
    ReqId,
    TaskId,
)
from gzkit.traceability import covers


class TestAdrId(unittest.TestCase):
    def test_parse_valid(self) -> None:
        adr = AdrId.parse("ADR-0.0.10")
        self.assertEqual(adr.raw, "ADR-0.0.10")
        self.assertEqual(str(adr), "ADR-0.0.10")

    def test_roundtrip(self) -> None:
        self.assertEqual(str(AdrId.parse("ADR-1.2.3")), "ADR-1.2.3")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(AdrId.parse("  ADR-0.0.10  ").raw, "ADR-0.0.10")

    def test_invalid_format(self) -> None:
        for bad in ["ADR-0.0", "adr-0.0.1", "ADR-X.Y.Z", "0.0.1", "OBPI-0.0.1"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                AdrId.parse(bad)

    def test_frozen(self) -> None:
        adr = AdrId.parse("ADR-0.1.0")
        with self.assertRaises(ValidationError):
            adr.raw = "ADR-0.2.0"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            AdrId(raw="ADR-0.0.1", extra="nope")  # type: ignore[call-arg]


class TestObpiId(unittest.TestCase):
    def test_parse_valid(self) -> None:
        obpi = ObpiId.parse("OBPI-0.0.10-01")
        self.assertEqual(obpi.raw, "OBPI-0.0.10-01")
        self.assertEqual(str(obpi), "OBPI-0.0.10-01")

    def test_roundtrip(self) -> None:
        self.assertEqual(str(ObpiId.parse("OBPI-0.0.10-02")), "OBPI-0.0.10-02")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(ObpiId.parse("  OBPI-0.0.10-01  ").raw, "OBPI-0.0.10-01")

    def test_invalid_format(self) -> None:
        for bad in ["OBPI-0.0.10", "obpi-0.0.10-01", "ADR-0.0.10-01"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                ObpiId.parse(bad)

    def test_frozen(self) -> None:
        obpi = ObpiId.parse("OBPI-0.1.0-01")
        with self.assertRaises(ValidationError):
            obpi.raw = "OBPI-0.2.0-01"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            ObpiId(raw="OBPI-0.0.1-01", extra="x")  # type: ignore[call-arg]


class TestReqIdSurface(unittest.TestCase):
    """Test the identity surface ReqId (core.models), not the entity ReqId (triangle)."""

    def test_parse_valid(self) -> None:
        req = ReqId.parse("REQ-0.0.10-02-01")
        self.assertEqual(req.raw, "REQ-0.0.10-02-01")
        self.assertEqual(str(req), "REQ-0.0.10-02-01")

    def test_roundtrip(self) -> None:
        self.assertEqual(str(ReqId.parse("REQ-0.15.0-03-02")), "REQ-0.15.0-03-02")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(ReqId.parse("  REQ-0.0.10-02-01  ").raw, "REQ-0.0.10-02-01")

    def test_invalid_format(self) -> None:
        for bad in ["REQ-0.0.10-02", "REQ-0.0.10", "req-0.0.10-02-01", "OBPI-0.0.10-02-01"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                ReqId.parse(bad)

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            ReqId(raw="REQ-0.0.1-01-01", extra="x")  # type: ignore[call-arg]


class TestTaskIdSurface(unittest.TestCase):
    """Test the identity surface TaskId (core.models), not the entity TaskId (tasks)."""

    def test_parse_valid(self) -> None:
        task = TaskId.parse("TASK-0.20.0-01-01-01")
        self.assertEqual(task.raw, "TASK-0.20.0-01-01-01")
        self.assertEqual(str(task), "TASK-0.20.0-01-01-01")

    def test_roundtrip(self) -> None:
        self.assertEqual(str(TaskId.parse("TASK-0.0.10-01-01-01")), "TASK-0.0.10-01-01-01")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(TaskId.parse("  TASK-0.20.0-01-01-01  ").raw, "TASK-0.20.0-01-01-01")

    def test_invalid_format(self) -> None:
        for bad in [
            "TASK-0.0.10-01",
            "TASK-0.0.10-01-01",
            "task-0.0.10-01-01-01",
            "EV-0.0.10-01-01-01",
        ]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                TaskId.parse(bad)

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            TaskId(raw="TASK-0.0.1-01-01-01", extra="x")  # type: ignore[call-arg]


class TestEvidenceId(unittest.TestCase):
    def test_parse_valid(self) -> None:
        ev = EvidenceId.parse("EV-0.0.10-01-001")
        self.assertEqual(ev.raw, "EV-0.0.10-01-001")
        self.assertEqual(str(ev), "EV-0.0.10-01-001")

    def test_roundtrip(self) -> None:
        self.assertEqual(str(EvidenceId.parse("EV-0.0.10-01-001")), "EV-0.0.10-01-001")

    def test_strips_whitespace(self) -> None:
        self.assertEqual(EvidenceId.parse("  EV-0.0.10-01-001  ").raw, "EV-0.0.10-01-001")

    def test_invalid_format(self) -> None:
        for bad in ["EV-0.0.10-01", "EV-0.0.10", "ev-0.0.10-01-001", "TASK-0.0.10-01-001"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                EvidenceId.parse(bad)

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            EvidenceId(raw="EV-0.0.1-01-001", extra="x")  # type: ignore[call-arg]


class TestIdentityModelsMapping(unittest.TestCase):
    @covers("REQ-0.0.10-02-01")
    def test_all_five_surfaces_present(self) -> None:
        expected = {"ADR", "OBPI", "REQ", "TASK", "EV"}
        self.assertEqual(set(IDENTITY_MODELS.keys()), expected)
        self.assertEqual(len(IDENTITY_MODELS), 5)

    @covers("REQ-0.0.10-02-01")
    def test_mapping_values_correct(self) -> None:
        self.assertIs(IDENTITY_MODELS["ADR"], AdrId)
        self.assertIs(IDENTITY_MODELS["OBPI"], ObpiId)
        self.assertIs(IDENTITY_MODELS["REQ"], ReqId)
        self.assertIs(IDENTITY_MODELS["TASK"], TaskId)
        self.assertIs(IDENTITY_MODELS["EV"], EvidenceId)


class TestTierPortability(unittest.TestCase):
    """Verify same ID string parses identically regardless of tier context."""

    @covers("REQ-0.0.10-02-03")
    def test_adr_portable(self) -> None:
        s = "ADR-0.0.10"
        self.assertEqual(AdrId.parse(s), AdrId.parse(s))
        self.assertEqual(str(AdrId.parse(s)), s)

    @covers("REQ-0.0.10-02-03")
    def test_obpi_portable(self) -> None:
        s = "OBPI-0.0.10-02"
        self.assertEqual(ObpiId.parse(s), ObpiId.parse(s))
        self.assertEqual(str(ObpiId.parse(s)), s)

    @covers("REQ-0.0.10-02-03")
    def test_req_portable(self) -> None:
        s = "REQ-0.0.10-02-01"
        self.assertEqual(ReqId.parse(s), ReqId.parse(s))
        self.assertEqual(str(ReqId.parse(s)), s)

    @covers("REQ-0.0.10-02-03")
    def test_task_portable(self) -> None:
        s = "TASK-0.20.0-01-01-01"
        self.assertEqual(TaskId.parse(s), TaskId.parse(s))
        self.assertEqual(str(TaskId.parse(s)), s)

    @covers("REQ-0.0.10-02-03")
    def test_ev_portable(self) -> None:
        s = "EV-0.0.10-01-001"
        self.assertEqual(EvidenceId.parse(s), EvidenceId.parse(s))
        self.assertEqual(str(EvidenceId.parse(s)), s)

    @covers("REQ-0.0.10-02-03")
    def test_all_surfaces_roundtrip(self) -> None:
        """Every surface ID round-trips through parse -> str."""
        examples = [
            ("ADR", "ADR-0.0.10"),
            ("OBPI", "OBPI-0.0.10-01"),
            ("REQ", "REQ-0.0.10-01-01"),
            ("TASK", "TASK-0.20.0-01-01-01"),
            ("EV", "EV-0.0.10-01-001"),
        ]
        for surface, id_str in examples:
            with self.subTest(surface=surface):
                model_cls = IDENTITY_MODELS[surface]
                parsed = model_cls.parse(id_str)
                self.assertEqual(str(parsed), id_str)


class TestFrozenConfig(unittest.TestCase):
    @covers("REQ-0.0.10-02-02")
    def test_all_models_frozen(self) -> None:
        for name, model_cls in IDENTITY_MODELS.items():
            with self.subTest(model=name):
                self.assertTrue(model_cls.model_config.get("frozen"))

    @covers("REQ-0.0.10-02-02")
    def test_all_models_extra_forbid(self) -> None:
        for name, model_cls in IDENTITY_MODELS.items():
            with self.subTest(model=name):
                self.assertEqual(model_cls.model_config.get("extra"), "forbid")


if __name__ == "__main__":
    unittest.main()
