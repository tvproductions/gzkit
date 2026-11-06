"""``gz wp req new``: RP-12 O2 task 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: `gz wp req new
<WP-id>` writes one repair REQ with the next `REQ-<n>`, held on that package,
carrying its statement, criteria, kind and problem report, and refuses a package
not of `kind: repair` and an issue the package does not carry (ruling 48); the
REQ lives in `data/catalog/reqs.json` beside the catalog's (ruling 45). A refusal
exits 3 and writes nothing; an unknown package exits 1.
"""

import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from gzkit.cli import main
from gzkit.governance.trust_audits.catalog import audit_catalog
from tests.commands.common import CliRunner, _quick_init
from tests.commands.test_wp_order import _OUTCOME, _package

_CATALOG_REQ = {
    "id": "REQ-4",
    "specialization": "catalog",
    "member_of": "H1",
    "statement": "A resumed session names its predecessor.",
    "criteria": [{"state_or_input": "a handoff", "required_outcome": "named", "evidence": "t"}],
    "kind": "BEHAVIOR",
    "revision": 1,
    "derives_from": [],
    "applies_to": [],
}
_CRITERION = "the hook is generated|it imports a public name|the import ratchet test"


def _seed_catalog() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    family = {"code": "H", "band": "product", "name": "Session", "scope": "One."}
    packages = [
        _package("WP-01-stamp", "repair", [1301]),
        _package("WP-02-resume", "delivery", []),
    ]
    for kind, entries in (
        ("families", [family]),
        ("outcomes", [_OUTCOME]),
        ("reqs", [_CATALOG_REQ]),
        ("externals", []),
        ("work_packages", packages),
        ("orders", []),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _reqs() -> list[dict[str, Any]]:
    text = (Path("data") / "catalog" / "reqs.json").read_text(encoding="utf-8")
    return json.loads(text)["reqs"]


class _ReqCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()
        result = self.runner.invoke(
            main, ["wp", "initiate", "WP-01-stamp", "--operator-text", "open it"]
        )
        self.assertEqual(result.exit_code, 0, result.output)

    def gz(self, *args: str, code: int = 0) -> str:
        result = self.runner.invoke(main, ["wp", "req", *args])
        self.assertEqual(result.exit_code, code, result.output)
        # The console wraps long lines; a refusal's words are read unwrapped.
        return result.output if code == 0 else " ".join(result.output.split())

    def new(self, *extra: str, package: str = "WP-01-stamp", code: int = 0) -> str:
        args = ["new", package, "--statement", "The generator imports by its public name."]
        args += ["--criterion", _CRITERION, "--kind", "BEHAVIOR", "--problem-report", "1301"]
        return self.gz(*args, *extra, code=code)


class ReqNewTests(_ReqCase):
    def test_new_writes_a_repair_req_past_the_highest_id_and_the_store_passes(self) -> None:
        self.new("--aligns-to", "REQ-4")
        _, written = _reqs()
        self.assertEqual(written["id"], "REQ-5")
        self.assertEqual(written["specialization"], "repair")
        self.assertEqual(written["held_on"], "WP-01-stamp")
        self.assertEqual(written["problem_report"], 1301)
        self.assertEqual(written["aligns_to"], "REQ-4")
        self.assertEqual(written["revision"], 1)
        self.assertEqual(written["criteria"][0]["required_outcome"], "it imports a public name")
        self.assertEqual([e for e in audit_catalog(Path.cwd()) if e.field == "reqs"], [])

    def test_a_new_req_may_supersede_one_the_store_holds(self) -> None:
        """Ruling 31: a change to the obligation is a new REQ carrying `supersedes`."""
        self.new()
        self.new("--supersedes", "REQ-5")
        self.assertEqual(_reqs()[-1]["supersedes"], "REQ-5")
        self.assertIsNone(_reqs()[1]["supersedes"])

    def test_a_delivery_package_takes_no_repair_req(self) -> None:
        output = self.new(package="WP-02-resume", code=3)
        self.assertIn("delivery package", output)
        self.assertEqual(len(_reqs()), 1)

    def test_an_issue_the_package_does_not_carry_is_refused(self) -> None:
        args = ["new", "WP-01-stamp", "--statement", "S.", "--criterion", _CRITERION]
        output = self.gz(*args, "--kind", "SUPPORT", "--problem-report", "7", code=3)
        self.assertIn("#7", output)
        self.assertEqual(len(_reqs()), 1)

    def test_a_package_not_open_takes_no_req(self) -> None:
        """Ruling 2: the package stays open while its REQs are found."""
        with patch("gzkit.commands.wp_order.work_package_state", return_value="closed"):
            output = self.new(code=3)
        self.assertIn("is closed", output)
        self.assertEqual(len(_reqs()), 1)

    def test_a_refusal_names_the_flag_and_the_call_to_rerun(self) -> None:
        """Guardrail prose: what failed by the flag typed, why, and the runnable next step."""
        for extra, flag in (
            (("--aligns-to", "REQ-9"), "REQ-9"),
            (("--supersedes", "REQ-9"), "REQ-9"),
            (("--criterion", "only two|parts"), "--criterion"),
        ):
            with self.subTest(flag=flag, extra=extra):
                output = self.new(*extra, code=3)
                self.assertIn(flag, output)
                self.assertIn("Nothing was written", output)
                self.assertIn("uv run gz wp req new", output)
                self.assertNotIn("errors.pydantic.dev", output)
        self.assertEqual(len(_reqs()), 1)

    def test_an_unknown_package_exits_1(self) -> None:
        self.new(package="WP-09-ghost", code=1)
        self.assertEqual(len(_reqs()), 1)


if __name__ == "__main__":
    unittest.main()
