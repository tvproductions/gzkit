"""ghi-triage routes a tracked GHI by duplication alone, never by fix() precedent (GHI #1374).

The precedent criterion ("≥3 `fix(` commits in 60 days") was dropped from defect-fix
routing by operator ruling on 2026-09-17: a GHI always authorizes direct repair, so the
count is moot for tracked defects (`docs/governance/defect-fix-routing.md`). Triage
routes only GHIs, so its route must not change with the count. The count may still be
reported as information.
"""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / ".gzkit"
    / "skills"
    / "ghi-triage"
    / "scripts"
    / "triage.py"
)


def _load_triage_module():
    spec = importlib.util.spec_from_file_location("ghi_triage_routing_script", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_TRIAGE = _load_triage_module()


def _issue(number: int, title: str):
    return _TRIAGE.Issue(
        number=number,
        title=title,
        labels=["defect"],
        body="",
        created_at="2026-11-26T00:00:00Z",
        updated_at="2026-11-26T00:00:00Z",
    )


def _routes(issues, precedent: int) -> dict[int, str]:
    payload = json.loads(
        _TRIAGE.render_json(issues, precedent=precedent, duplicates={2: 1}, blocker_resolver=None)
    )
    return {record["number"]: record["route"] for record in payload["issues"]}


class TestTriageRouteIgnoresPrecedent(unittest.TestCase):
    def test_a_tracked_defect_routes_direct_fix_at_any_precedent_count(self) -> None:
        issues = [_issue(1, "surface: a defect"), _issue(2, "surface: a defect")]
        for precedent in (0, 2, 3, 400):
            with self.subTest(precedent=precedent):
                self.assertEqual(_routes(issues, precedent), {1: "direct-fix", 2: "close"})

    def test_the_count_is_still_reported(self) -> None:
        payload = json.loads(
            _TRIAGE.render_json(
                [_issue(1, "surface: a defect")], precedent=0, duplicates={}, blocker_resolver=None
            )
        )
        self.assertEqual(payload["precedent_60d"], 0)


if __name__ == "__main__":
    unittest.main()
