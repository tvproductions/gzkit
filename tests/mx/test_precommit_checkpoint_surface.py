"""The pre-commit enforcement surface honors the MX checkpoint (GHI #843).

ADR-0.0.74 Boundary Invariant #2 requires *every* fail-closed funnel to resolve
its severity through the shared checkpoint. The inventory fence OBPI-0.0.74-02
shipped enumerates ``validate_cmd`` and nothing else, so the entire pre-commit
surface sat outside every check -- the gap ADR-0.0.74 Negative #6 predicted in
its own words: *"a funnel that forgets it silently stays hard."*

This module fences the SURFACE. ``tests/test_hooks_guards.py::TestMxCheckpointSeam``
fences the inventory *inside* ``gzkit.hooks.guards``; a chore checker added as its
own pre-commit entrypoint would pass that one while consulting nothing.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_PRECOMMIT = _ROOT / ".pre-commit-config.yaml"

# Local pre-commit hooks that are NOT gzkit-authored governance guards, each with
# the reason it is out of the checkpoint's reach. A new gzkit-authored guard must
# either consult the checkpoint or be excused HERE, in the open, with a reason.
_NOT_A_GZKIT_GUARD = {
    "ruff-check": "third-party linter invoked directly; not a governance guard",
    "ruff-format": "third-party formatter invoked directly",
    "ty-check": "third-party type checker invoked directly",
    "xenon-complexity": "third-party complexity gate invoked directly",
    "interrogate": "third-party docstring gate invoked directly",
    "gitleaks": "third-party secrets scanner; `secrets` is a gate5 floor member and "
    "stays hard by construction -- over-strict, never under-strict",
    "check-todos-fixmes": "informational only; `|| true` can never fail",
    "task-trailer-stamp": "prepare-commit-msg stamper, not a gate",
    "ledger-commit-locus": "post-commit recorder; git ignores its exit status",
    "unittest": "test runner, manual stage",
    "surface-fidelity-cheap": "`gz validate` scopes -- already checkpointed at "
    "validate_cmd.py `_run_scope_checks`",
    "authorship": "`gz validate` scope -- already checkpointed (and demoting: GHI #852)",
    "gz-check-pre-push": "`gz check` -- already checkpointed at quality.py `_apply_mx_seam`",
    "forbid-pytest": "the gzkit.hooks.guards seam itself; fenced by "
    "tests/test_hooks_guards.py::TestMxCheckpointSeam",
}

_CHORES = {
    "validator-reachability": (
        "src/gzkit/chores/control-surface-validator-reachability/check_reachability.py"
    ),
    "ledger-vocabulary-inertness": (
        "src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py"
    ),
}


def _consults_the_checkpoint(source: Path) -> bool:
    """Return True when *source* actually CALLS the checkpoint, by AST not by substring.

    A substring scan is not this check: the first draft of this fence tested
    ``"checkpoint" in text`` and a mutant that severed the real wiring SURVIVED,
    because the word still appeared in a docstring explaining the wiring. That is
    the presence-check failure AGENTS.md names -- a presence check answers "is
    something armed", never "did the governed procedure run". The predicate is
    therefore the call node itself plus a real ``gzkit.mx`` import.
    """
    tree = ast.parse(source.read_text(encoding="utf-8"))
    calls_blocks = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"blocks", "resolve", "is_advisory"}
        for node in ast.walk(tree)
    )
    imports_mx = any(
        isinstance(node, ast.ImportFrom) and (node.module or "").startswith("gzkit.mx")
        for node in ast.walk(tree)
    )
    return calls_blocks and imports_mx


def _load_chore(rel: str):
    """Import a chore checker by path (its directory name is not an identifier)."""
    path = _ROOT / rel
    spec = importlib.util.spec_from_file_location(f"_chore_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _local_hooks() -> list[dict]:
    """Return every `repo: local` hook declared in `.pre-commit-config.yaml`."""
    config = yaml.safe_load(_PRECOMMIT.read_text(encoding="utf-8"))
    return [h for r in config["repos"] if r.get("repo") == "local" for h in r["hooks"]]


def _hangar(td: str) -> Path:
    """Return a project root carrying an active MX marker."""
    root = Path(td)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    (root / ".gzkit" / "mx.json").write_text(json.dumps({"session_id": "t"}), encoding="utf-8")
    return root


class TestCheckpointBlocksHelper(unittest.TestCase):
    """`checkpoint.blocks` is the one composition consumers ask, and it holds the floor."""

    def test_non_floor_guard_stops_blocking_inside_the_hangar(self) -> None:
        from gzkit.mx import checkpoint, levels

        with tempfile.TemporaryDirectory() as td:
            self.assertFalse(checkpoint.blocks("forbid-pytest", levels.ERROR, _hangar(td)))

    def test_floor_members_keep_blocking_inside_the_hangar(self) -> None:
        from gzkit.mx import checkpoint, levels
        from gzkit.mx.invariants import GATE5_INVARIANTS

        with tempfile.TemporaryDirectory() as td:
            root = _hangar(td)
            for member in sorted(GATE5_INVARIANTS):
                with self.subTest(member=member):
                    self.assertTrue(checkpoint.blocks(member, levels.ERROR, root))

    def test_nothing_stops_blocking_outside_the_hangar(self) -> None:
        from gzkit.mx import checkpoint, levels

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".gzkit").mkdir()
            self.assertTrue(checkpoint.blocks("forbid-pytest", levels.ERROR, root))

    def test_critical_pins_even_for_a_non_floor_guard(self) -> None:
        """The `enforcement-floor` precedent (GHI #651): pin by level, not membership."""
        from gzkit.mx import checkpoint, levels

        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(checkpoint.blocks("enforcement-floor", levels.CRITICAL, _hangar(td)))


class TestDemoteNotice(unittest.TestCase):
    """A demoted finding is announced. Advisory means non-grounding, not discarded."""

    def test_notice_carries_the_three_recovery_parts(self) -> None:
        """`.gzkit/rules/guardrail-feedback-prose.md`: what failed, why, the next step."""
        from gzkit.mx import checkpoint

        notice = checkpoint.demote_notice("some-guard")
        self.assertIn("some-guard", notice)
        self.assertIn("mx.json", notice)
        self.assertIn("gz mx exit", notice)

    def test_notice_denies_that_the_guard_was_waived(self) -> None:
        """Demotion is not a waiver; the wording must not let a reader conclude it is."""
        from gzkit.mx import checkpoint

        self.assertIn("NOT waived", checkpoint.demote_notice("some-guard"))


class TestChoreCheckersConsultTheCheckpoint(unittest.TestCase):
    """Each chore checker is its own pre-commit entrypoint and resolves its own severity."""

    def test_chore_guards_demote_inside_the_hangar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _hangar(td)
            for guard, rel in _CHORES.items():
                with self.subTest(guard=guard):
                    self.assertTrue(_load_chore(rel)._mx_demoted(guard, root))

    def test_chore_guards_block_outside_the_hangar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".gzkit").mkdir()
            for guard, rel in _CHORES.items():
                with self.subTest(guard=guard):
                    self.assertFalse(_load_chore(rel)._mx_demoted(guard, root))

    def test_chore_guards_fail_closed_when_the_checkpoint_is_unreadable(self) -> None:
        from gzkit.mx import checkpoint

        with tempfile.TemporaryDirectory() as td:
            root = _hangar(td)
            with mock.patch.object(checkpoint, "blocks", side_effect=RuntimeError("boom")):
                for guard, rel in _CHORES.items():
                    with self.subTest(guard=guard):
                        self.assertFalse(_load_chore(rel)._mx_demoted(guard, root))

    def test_the_inertness_chore_does_not_claim_the_ledger_floor_name(self) -> None:
        """`ledger` means ledger INTEGRITY and never demotes; this chore audits vocabulary.

        Registering it as `ledger` would pin a demotable chore to the floor; the
        inverse error -- a genuine integrity guard registered under a non-floor
        name -- is GHI #852 on the `authorship` scope.
        """
        from gzkit.mx.invariants import GATE5_INVARIANTS

        self.assertNotIn("ledger-vocabulary-inertness", GATE5_INVARIANTS)
        with tempfile.TemporaryDirectory() as td:
            root = _hangar(td)
            chore = _load_chore(_CHORES["ledger-vocabulary-inertness"])
            self.assertTrue(chore._mx_demoted("ledger-vocabulary-inertness", root))
            self.assertFalse(chore._mx_demoted("ledger", root))


class TestPrecommitSurfaceInventory(unittest.TestCase):
    """Every gzkit-authored fail-closed pre-commit hook consults the checkpoint.

    THE fence for GHI #843. Its absence is what let the whole pre-commit surface
    sit outside BI#2 unnoticed: a per-module fence cannot see a hook that is its
    own entrypoint, and nothing enumerated the surface itself.
    """

    def test_every_gzkit_authored_hook_is_checkpointed_or_excused(self) -> None:
        unchecked: list[str] = []
        for hook in _local_hooks():
            hook_id, entry = hook["id"], hook["entry"]
            if hook_id in _NOT_A_GZKIT_GUARD:
                continue
            targets = [_ROOT / m for m in re.findall(r"(src/gzkit/\S+\.py)", entry)]
            if "gzkit.hooks.guards" in entry:
                targets.append(_ROOT / "src/gzkit/hooks/guards.py")
            if not targets:
                unchecked.append(f"{hook_id}: entry names no gzkit source ({entry!r})")
                continue
            for target in targets:
                if not _consults_the_checkpoint(target):
                    unchecked.append(f"{hook_id}: {target.name} never consults the checkpoint")
        self.assertEqual(
            unchecked,
            [],
            "ADR-0.0.74 BI#2: a fail-closed pre-commit funnel must resolve severity "
            "through the shared checkpoint, or be excused in _NOT_A_GZKIT_GUARD "
            "with a stated reason",
        )

    def test_the_excuse_list_only_names_hooks_that_exist(self) -> None:
        """An excuse for a deleted hook is dead weight that hides a real gap later."""
        live = {hook["id"] for hook in _local_hooks()}
        self.assertEqual(sorted(set(_NOT_A_GZKIT_GUARD) - live), [])


if __name__ == "__main__":
    unittest.main()
