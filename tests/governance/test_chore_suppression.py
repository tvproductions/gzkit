"""A chore never discharges a finding by suppression (GHI #999 step 6).

`docs/governance/chore-class-system.md` § Suppression: `ruff --add-noqa`,
`ty --add-ignore` and `pyrefly suppress` turn an exit code green and change
nothing about correctness, and gzkit's attestation evidence is exit codes.
Operator ruling 2026-09-13, verbatim "Static chore check (Recommended)": the
witness reads what a chore instructs and what its criteria run. A marker an
agent hand-writes during a run is outside it, and the rule says so.

`SHELL_OPERATORS_RE` already refuses `&&`, `||`, `|`, `<` and `>` in a
criterion at registry load, so this audit holds the two hiding routes that
refusal leaves open: a shell interpreter, whose script body `; exit 0` passes
the operator check, and a flag that forces a passing exit.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_chore_suppression

_WORKFLOW = "## Workflow\n\n### 1. Scan — observe\n\n"


def _tree(root: Path, *, workflow: str = "", commands: tuple[str, ...] = ()) -> None:
    """Write one registered chore with the given workflow text and criterion commands."""
    chores = root / ".gzkit" / "chores"
    (chores / "demo").mkdir(parents=True)
    (root / ".gzkit.json").write_text("{}", encoding="utf-8")
    entry = {"slug": "demo", "path": ".gzkit/chores/demo", "lane": "lite"}
    (chores / "registry.json").write_text(json.dumps({"chores": [entry]}), encoding="utf-8")
    (chores / "demo" / "CHORE.md").write_text(
        "# Demo\n\n" + _WORKFLOW + workflow + "\n## Acceptance Criteria\n\nSee JSON.\n",
        encoding="utf-8",
    )
    criteria = [{"type": "exitCodeEquals", "command": c, "expected": 0} for c in commands]
    (chores / "demo" / "acceptance.json").write_text(
        json.dumps({"criteria": criteria}), encoding="utf-8"
    )


def _audit(*, workflow: str = "", commands: tuple[str, ...] = ()) -> list:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _tree(root, workflow=workflow, commands=commands)
        return audit_chore_suppression(root)


class TestLiveTree(unittest.TestCase):
    def test_no_registered_chore_instructs_or_runs_a_suppression(self) -> None:
        root = Path(__file__).resolve().parents[2]
        errors = audit_chore_suppression(root)
        self.assertEqual(errors, [], "\n".join(f"{e.artifact}: {e.message}" for e in errors))


class TestCriterionHidesItsExitStatus(unittest.TestCase):
    """A criterion is the channel a chore discharges a finding through."""

    def test_a_flag_forcing_a_passing_exit_fails(self) -> None:
        errors = _audit(commands=("uv run ruff check --exit-zero .",))
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0].artifact, ".gzkit/chores/demo/acceptance.json")

    def test_a_shell_interpreter_fails_because_its_script_can_end_exit_zero(self) -> None:
        # `;` is not in SHELL_OPERATORS_RE, so this reaches the runner and exits 0.
        errors = _audit(commands=('sh -c "uv run ruff check . ; exit 0"',))
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0].artifact, ".gzkit/chores/demo/acceptance.json")

    def test_a_shell_named_by_absolute_path_is_still_a_shell(self) -> None:
        self.assertEqual(len(_audit(commands=('/bin/bash -c "true"',))), 1)

    def test_a_suppression_writer_as_a_criterion_fails(self) -> None:
        errors = _audit(commands=("uv run ruff check --add-noqa src",))
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0].artifact, ".gzkit/chores/demo/acceptance.json")

    def test_each_offending_criterion_is_its_own_finding(self) -> None:
        errors = _audit(commands=("uv run ruff check --exit-zero .", "uvx ty check --add-ignore"))
        self.assertEqual(len(errors), 2, errors)

    def test_an_honest_criterion_passes(self) -> None:
        # The frontier-model-card-currency shape: an interpreter that is not a shell.
        commands = ("uv run ruff check .", "python3 -c \"assert True, 'ok'\"", "uv run gz smoke")
        self.assertEqual(_audit(commands=commands), [])


class TestChoreDocInstructsASuppression(unittest.TestCase):
    """A workflow step that writes suppression markers is the prohibited repair."""

    def test_a_fenced_suppression_writer_fails(self) -> None:
        errors = _audit(workflow="```bash\nuvx ty check --add-ignore src\n```\n")
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0].artifact, ".gzkit/chores/demo/CHORE.md")

    def test_an_inline_suppression_writer_fails(self) -> None:
        errors = _audit(workflow="Silence the rest with `pyrefly suppress src`.\n")
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0].artifact, ".gzkit/chores/demo/CHORE.md")

    def test_a_report_capture_in_the_workflow_is_not_a_suppression(self) -> None:
        # Observe steps write a tool's findings to a proof; the exit status of a
        # capture discharges nothing, because criteria are what `gz chores run` gates.
        workflow = (
            "```bash\nuvx xenon --max-absolute B src/ > proofs/xenon.txt 2>&1 || true\n"
            "uv run ruff check --exit-zero --output-format json . > proofs/ruff.json\n```\n"
        )
        self.assertEqual(_audit(workflow=workflow), [])

    def test_naming_the_flag_alone_in_prose_is_not_an_instruction(self) -> None:
        self.assertEqual(_audit(workflow="Never discharge a finding with `--add-noqa`.\n"), [])


if __name__ == "__main__":
    unittest.main()
