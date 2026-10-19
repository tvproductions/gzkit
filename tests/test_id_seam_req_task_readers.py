"""REQ and TASK readers take their grammar from the identity seam (drydock RO-2 tranche 2).

`docs/governance/harbor-ro2-identity-seam.md` § Tranches row 2. Each reader that
once spelled its own width now embeds the seam body, so a width-loose id (one
index digit, three digits) is no longer read as a REQ or TASK id by any of them.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.status import _req_prefix_from_task_id
from gzkit.commands.validate_req_kind import _REQ_ANY_ID_RE
from gzkit.core.models import REQ_SHORT_ID_BODY
from gzkit.governance.req_coverage import _REQ_KIND_TAG_RE
from gzkit.mx.log import parse_artifacts
from gzkit.tasks import has_task_trailer, in_scope_task_id
from gzkit.traceability import _COVERS_REF_PATTERN, _REQ_TAG_PATTERN


class TestSeamWidthsInReaders(unittest.TestCase):
    """Strict two-digit components, the seam's settled width."""

    def test_status_reads_only_the_seam_task_width(self) -> None:
        self.assertEqual(_req_prefix_from_task_id("TASK-0.1.0-01-02-03"), "REQ-0.1.0-01-02")
        self.assertIsNone(_req_prefix_from_task_id("TASK-0.1.0-1-2-3"))

    def test_trailer_detection_takes_numeric_and_slug_forms_only(self) -> None:
        self.assertTrue(has_task_trailer("fix\n\nTask: TASK-0.1.0-01-02-03"))
        self.assertTrue(has_task_trailer("fix\n\nTask: TASK-ro2-req-task"))
        self.assertFalse(has_task_trailer("fix\n\nTask: TASK-0.1.0-1-2-3"))

    def test_scope_lookup_ignores_a_loose_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            ledger.write_text(
                '{"event": "task_started", "task_id": "TASK-0.1.0-1-2-3"}\n', encoding="utf-8"
            )
            self.assertIsNone(in_scope_task_id(ledger, "OBPI-0.1.0-01"))

    def test_req_readers_reject_a_loose_req_id(self) -> None:
        loose = "REQ-0.1.0-1-1"
        self.assertEqual(_REQ_ANY_ID_RE.findall(loose), [])
        self.assertEqual(_REQ_KIND_TAG_RE.findall(f"{loose} [BEHAVIOR]:"), [])
        self.assertIsNone(_COVERS_REF_PATTERN.search(f'@covers("{loose}")'))
        self.assertIsNone(_REQ_TAG_PATTERN.search(f"@{loose}"))

    def test_req_readers_accept_the_seam_req_id(self) -> None:
        strict = "REQ-0.1.0-01-02"
        self.assertEqual(_REQ_ANY_ID_RE.findall(strict), [strict])
        self.assertEqual(_REQ_KIND_TAG_RE.findall(f"{strict} [BEHAVIOR]:"), [(strict, "BEHAVIOR")])

    def test_mx_log_narrates_full_and_short_req_forms_only(self) -> None:
        got = parse_artifacts("closes REQ-0.1.0-01-02, REQ-03-04 and REQ-0.1.0-1-1")
        self.assertEqual(got["REQ"], ["REQ-0.1.0-01-02", "REQ-03-04"])

    def test_short_req_body_is_the_item_criterion_pair(self) -> None:
        self.assertEqual(REQ_SHORT_ID_BODY, r"REQ-\d{2}-\d{2}")


if __name__ == "__main__":
    unittest.main()
