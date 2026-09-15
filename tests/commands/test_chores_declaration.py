"""Chore class declaration in the registry (GHI #999).

The declaration is what makes a chore's nature checkable: why it exists
(``class``), where it stops (``rung``), whether it may run on a cadence
(``idempotent``), what its staleness means, what "no repair" means for it,
what it refuses to touch, and which rule it serves. Design authority:
``docs/governance/chore-class-system.md`` § The declaration, and the fence.
"""

import sys
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.chores import _load_chores_registry
from tests.commands.common import CliRunner, _quick_init
from tests.commands.test_chores import _project_chores_root, _write_acceptance, _write_v2_registry

_PYTHON = '"' + sys.executable.replace("\\", "/") + '"'


def _declaration(**overrides: object) -> dict[str, object]:
    """Return a complete, valid declaration; overrides replace or drop keys (None drops)."""
    base: dict[str, object] = {
        "class": "coherence",
        "rung": "propose",
        "idempotent": True,
        "staleness": {"signal": "content-delta", "surfaces": [".gzkit/rules"], "graceDays": 7},
        "remediation": {
            "category": "no_fix_planned",
            "details": "Conflicts are rulings; the chore recommends and stops.",
        },
        "nonAuthority": "Never edits either conflicting rule; resolution is the operator's.",
        "governingRule": ".gzkit/rules/governance-core.md",
    }
    for key, value in overrides.items():
        if value is None:
            base.pop(key, None)
        else:
            base[key] = value
    return base


def _write_chore(declaration: dict[str, object] | None, slug: str = "declared-chore") -> None:
    chore_path = str(_project_chores_root() / slug)
    pointer: dict[str, object] = {
        "slug": slug,
        "title": "Declared chore",
        "version": "1.0.0",
        "path": chore_path,
        "lane": "lite",
        "timeoutSeconds": 60,
    }
    if declaration is not None:
        pointer.update(declaration)
    _write_v2_registry([pointer])
    _write_acceptance(
        chore_path,
        [{"type": "exitCodeEquals", "command": f'{_PYTHON} -c "print(1)"', "expected": 0}],
    )


class TestDeclaredChoreLoads(unittest.TestCase):
    """A fully declared chore loads with its declaration exposed to consumers."""

    def test_declaration_fields_reach_the_chore_definition(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_chore(_declaration())

            _path, registry = _load_chores_registry()

            declaration = registry["declared-chore"].declaration
            self.assertIsNotNone(declaration)
            assert declaration is not None
            self.assertEqual(declaration.chore_class, "coherence")
            self.assertEqual(declaration.rung, "propose")
            self.assertTrue(declaration.idempotent)
            self.assertEqual(declaration.staleness.signal, "content-delta")
            self.assertEqual(declaration.staleness.surfaces, (".gzkit/rules",))
            self.assertEqual(declaration.remediation.category, "no_fix_planned")
            self.assertEqual(declaration.governing_rule, ".gzkit/rules/governance-core.md")

    def test_an_elapsed_time_scan_record_reaches_the_chore_definition(self) -> None:
        record = ".gzkit/chores/declared-chore/proofs/scan-record.md"
        staleness = {"signal": "elapsed-time", "periodDays": 30, "artifacts": [record]}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_chore(_declaration(staleness={**staleness, "graceDays": 7}))

            _path, registry = _load_chores_registry()

            declaration = registry["declared-chore"].declaration
            assert declaration is not None
            self.assertEqual(declaration.staleness.artifacts, (record,))


class TestMalformedDeclarationIsRefused(unittest.TestCase):
    """Attempting a declaration commits the chore to a complete, valid one.

    A partial declaration is refused rather than read as undeclared, so a chore
    cannot escape the class contract by declaring only the fields that suit it.
    """

    CASES: tuple[tuple[str, dict[str, object], str], ...] = (
        (
            "partial declaration names the missing field",
            {"class": "coherence"},
            "rung",
        ),
        (
            "remediation category without details",
            _declaration(remediation={"category": "no_fix_planned"}),
            "remediation.details",
        ),
        (
            "empty remediation details",
            _declaration(remediation={"category": "workaround", "details": ""}),
            "remediation.details",
        ),
        (
            "class outside the five",
            _declaration(**{"class": "janitorial"}),
            "class",
        ),
        (
            "rung outside the four",
            _declaration(rung="autofix"),
            "rung",
        ),
        (
            "elapsed-time staleness with no period",
            _declaration(staleness={"signal": "elapsed-time", "graceDays": 3}),
            "staleness",
        ),
        (
            # A content-delta chore is due when its inputs move; with no declared
            # inputs nothing can ever move, so the chore would read current forever.
            "content-delta staleness with no surfaces",
            _declaration(staleness={"signal": "content-delta", "graceDays": 7}),
            "staleness",
        ),
        (
            # An empty scope must never be read as "everything" (SRE ch. 7, Diskerase).
            "content-delta staleness with an empty surface list",
            _declaration(staleness={"signal": "content-delta", "surfaces": [], "graceDays": 7}),
            "staleness",
        ),
        (
            "surfaces declared on a signal that never reads them",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "surfaces": ["src/gzkit"],
                    "graceDays": 7,
                }
            ),
            "staleness",
        ),
        (
            "absolute surface path",
            _declaration(
                staleness={"signal": "content-delta", "surfaces": ["/etc"], "graceDays": 7}
            ),
            "staleness.surfaces",
        ),
        (
            "surface path escaping the repository",
            _declaration(
                staleness={"signal": "content-delta", "surfaces": ["../other"], "graceDays": 7}
            ),
            "staleness.surfaces",
        ),
        (
            "surface path naming the whole repository",
            _declaration(staleness={"signal": "content-delta", "surfaces": ["."], "graceDays": 7}),
            "staleness.surfaces",
        ),
        (
            "backslash-separated surface path",
            _declaration(
                staleness={"signal": "content-delta", "surfaces": ["src\\gzkit"], "graceDays": 7}
            ),
            "staleness.surfaces",
        ),
        (
            # An empty scan record must never be read as "no record needed" (GHI #935).
            "elapsed-time staleness with an empty artifact list",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "artifacts": [],
                    "graceDays": 7,
                }
            ),
            "staleness",
        ),
        (
            "artifacts declared on a signal that never reads them",
            _declaration(
                staleness={
                    "signal": "content-delta",
                    "surfaces": [".gzkit/rules"],
                    "artifacts": [".gzkit/chores/declared-chore/proofs/report.md"],
                    "graceDays": 7,
                }
            ),
            "staleness",
        ),
        (
            "absolute artifact path",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "artifacts": ["/tmp/scan.md"],
                    "graceDays": 7,
                }
            ),
            "staleness.artifacts",
        ),
        (
            # The run log's newest commit moves on a FAIL run, so declaring it would
            # reopen the run-twice bypass the scan record exists to close (GHI #935).
            "the run log declared as the scan record",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "artifacts": [".gzkit/chores/declared-chore/proofs/CHORE-LOG.md"],
                    "graceDays": 7,
                }
            ),
            "staleness.artifacts",
        ),
        (
            # A pattern matches the run log too; git dates it by the log's commits.
            "glob declared as the scan record",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "artifacts": [".gzkit/chores/declared-chore/proofs/*.md"],
                    "graceDays": 7,
                }
            ),
            "staleness.artifacts",
        ),
        (
            "directory declared as the scan record",
            _declaration(
                staleness={
                    "signal": "elapsed-time",
                    "periodDays": 30,
                    "artifacts": [".gzkit/chores/declared-chore/proofs/"],
                    "graceDays": 7,
                }
            ),
            "staleness.artifacts",
        ),
        (
            "empty non-authority",
            _declaration(nonAuthority=""),
            "nonAuthority",
        ),
        (
            "governing rule that is not a rule path or none",
            _declaration(governingRule="the pythonic rule"),
            "governingRule",
        ),
    )

    def test_each_malformed_declaration_blocks_the_registry(self) -> None:
        for label, declaration, field in self.CASES:
            with self.subTest(label):
                runner = CliRunner()
                with runner.isolated_filesystem():
                    _quick_init()
                    _write_chore(declaration)

                    result = runner.invoke(main, ["chores", "list"])

                    self.assertNotEqual(result.exit_code, 0)
                    self.assertIn(f"chores[declared-chore].{field}", result.output)

    def test_a_declared_no_repair_is_accepted(self) -> None:
        """no_fix_planned is a first-class value, distinct from an absent remediation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            staleness = {"signal": "elapsed-time", "periodDays": 30, "graceDays": 7}
            _write_chore(_declaration(staleness=staleness))

            result = runner.invoke(main, ["chores", "list"])

            self.assertEqual(result.exit_code, 0, result.output)


class TestUndeclaredChoreIsRefused(unittest.TestCase):
    """An undeclared chore does not run; absence defaults to the safe reading.

    Operator ruling 2026-09-13 ("Warn, flip at step 5"): absence warned while no
    chore was declared, and flips to refusal once every registered chore carries
    a declaration. A chore with no declared rung has no writing license a run
    could be held to (``docs/governance/chore-class-system.md`` § The
    declaration, and the fence).
    """

    def test_run_refuses_an_undeclared_chore_before_executing_anything(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_chore(None, slug="undeclared-chore")

            result = runner.invoke(main, ["chores", "run", "undeclared-chore"])

            self.assertEqual(result.exit_code, 1, result.output)
            self.assertIn("undeclared-chore", result.output)
            self.assertIn("no class declaration", result.output)
            log = Path(".gzkit/chores/undeclared-chore/proofs/CHORE-LOG.md")
            self.assertFalse(log.exists(), "a refused chore must not run or log")

    def test_run_of_a_declared_chore_makes_no_announcement(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _write_chore(_declaration())

            result = runner.invoke(main, ["chores", "run", "declared-chore"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertNotIn("no class declaration", result.output)

    def test_list_counts_the_undeclared_estate(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_root = _project_chores_root()
            pointers: list[dict[str, object]] = []
            for slug, declaration in (("one-declared", _declaration()), ("two-bare", None)):
                pointer: dict[str, object] = {
                    "slug": slug,
                    "title": slug,
                    "version": "1.0.0",
                    "path": str(chore_root / slug),
                    "lane": "lite",
                    "timeoutSeconds": 60,
                }
                if declaration is not None:
                    pointer.update(declaration)
                pointers.append(pointer)
                criterion = {"type": "exitCodeEquals", "command": f'{_PYTHON} -c "print(1)"'}
                _write_acceptance(str(chore_root / slug), [{**criterion, "expected": 0}])
            _write_v2_registry(pointers)

            result = runner.invoke(main, ["chores", "list"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("1 of 2 chores carry no class declaration", result.output)
            self.assertIn("refuses", result.output)


if __name__ == "__main__":
    unittest.main()
