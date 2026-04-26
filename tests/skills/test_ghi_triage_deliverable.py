"""ghi-triage v4 deliverable contract — GHI #324.

Pins the rank-deliverable rendering and rank-input validation against the
v4 contract. The deliverable equation is:

    deliverable == script(static_args, agent_cognition_input)

with no `agent_render(...)` term in the equation. Byte-stable rendering
across runs (given a frozen issue set + frozen agent input) is the regression
gate that catches inline-Python heredoc rendering, prose drift, and any
future "let's add one nice touch" inline addition that v3 collapsed onto
the agent.
"""

from __future__ import annotations

import importlib.util
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
    spec = importlib.util.spec_from_file_location("ghi_triage_script", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_TRIAGE = _load_triage_module()


def _issue(number: int, title: str, body: str = "", labels: tuple[str, ...] = ()) -> object:
    return _TRIAGE.Issue(
        number=number,
        title=title,
        labels=list(labels),
        body=body,
        created_at="2026-04-25T00:00:00Z",
        updated_at="2026-04-25T00:00:00Z",
    )


class TestRankDeliverableIsByteStable(unittest.TestCase):
    """deliverable == script(static_args, agent_cognition_input)."""

    def setUp(self) -> None:
        self.issues = [
            _issue(324, "ghi-triage skill: vibed deliverable contract", labels=("defect",)),
            _issue(323, "behave-req-tags fires on Draft briefs", labels=("defect",)),
            _issue(316, "ghi-author: cross-repo defect filing", labels=("enhancement",)),
        ]
        self.issue_index = {i.number: i for i in self.issues}
        self.routes = {324: "direct-fix", 323: "direct-fix", 316: "OBPI"}
        self.precedent = 110
        self.agent_input = {
            "rankings": [
                {
                    "number": 324,
                    "severity": "blocking",
                    "action": "fix triage skill rendering",
                    "why": "operator-facing surface degrades chat output every invocation",
                },
                {
                    "number": 323,
                    "severity": "degrading",
                    "action": "scope behave-req-tags to post-impl briefs",
                    "why": "validator currently fires on Draft briefs that have no scenarios yet",
                },
            ]
        }

    def test_render_rank_is_deterministic_across_invocations(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        outputs = {
            _TRIAGE.render_rank(
                items,
                self.issue_index,
                self.routes,
                self.precedent,
                len(self.issues),
            )
            for _ in range(20)
        }
        self.assertEqual(len(outputs), 1, "render_rank produced non-byte-stable output")

    def test_render_rank_preserves_caller_supplied_order(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        rendered = _TRIAGE.render_rank(
            items, self.issue_index, self.routes, self.precedent, len(self.issues)
        )
        idx_324 = rendered.find("#324")
        idx_323 = rendered.find("#323")
        self.assertGreater(idx_324, -1)
        self.assertGreater(idx_323, -1)
        self.assertLess(idx_324, idx_323, "agent-supplied order must be preserved verbatim")

    def test_render_rank_includes_severity_route_action_why_and_title(self) -> None:
        items = _TRIAGE.parse_rank_input(self.agent_input, set(self.issue_index))
        rendered = _TRIAGE.render_rank(
            items, self.issue_index, self.routes, self.precedent, len(self.issues)
        )
        self.assertIn("[blocking]", rendered)
        self.assertIn("direct-fix", rendered)
        self.assertIn("fix triage skill rendering", rendered)
        self.assertIn("operator-facing surface degrades chat output every invocation", rendered)
        self.assertIn("vibed deliverable contract", rendered)


class TestRankInputRenderingEdgeContract(unittest.TestCase):
    """Constrains WHY/ACTION shape so determinism doesn't leak through input."""

    def setUp(self) -> None:
        self.known = {324, 323}

    def _payload(self, **overrides: object) -> dict:
        entry: dict[str, object] = {
            "number": 324,
            "severity": "blocking",
            "action": "fix it",
            "why": "operator surface degrades every run",
        }
        entry.update(overrides)
        return {"rankings": [entry]}

    def test_severity_must_be_enum(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(severity="critical"), self.known)

    def test_why_too_long_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(why="x" * 121), self.known)

    def test_action_too_long_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(action="x" * 81), self.known)

    def test_why_with_newline_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(why="first clause\nsecond clause"), self.known)

    def test_why_with_markdown_chars_rejected(self) -> None:
        for bad in ("**bold** thing", "list `code`", "head # one", "pipe | cell"):
            with (
                self.subTest(bad=bad),
                self.assertRaises(_TRIAGE.RankInputError),
            ):
                _TRIAGE.parse_rank_input(self._payload(why=bad), self.known)

    def test_unknown_issue_number_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(self._payload(number=9999), self.known)

    def test_duplicate_issue_number_rejected(self) -> None:
        payload = {
            "rankings": [
                {"number": 324, "severity": "blocking", "action": "a", "why": "b"},
                {"number": 324, "severity": "latent", "action": "c", "why": "d"},
            ]
        }
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input(payload, self.known)

    def test_empty_rankings_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input({"rankings": []}, self.known)

    def test_non_dict_payload_rejected(self) -> None:
        with self.assertRaises(_TRIAGE.RankInputError):
            _TRIAGE.parse_rank_input([{"number": 324}], self.known)

    def test_well_formed_payload_accepted(self) -> None:
        items = _TRIAGE.parse_rank_input(self._payload(), self.known)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].number, 324)
        self.assertEqual(items[0].severity, "blocking")


if __name__ == "__main__":
    unittest.main()
