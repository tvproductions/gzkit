"""The reachability ratchet and the `gz check` pipeline must agree (GHI #787).

`check_reachability.py` decides whether a `gz validate` scope is *gated* by
reading `_STEP_GUARD_META` out of `src/gzkit/commands/quality.py` with a regex
(`_CHECK_REGISTRY_RE`). That dict is therefore the ratchet's sole evidence that
a scope runs on a commit path — a step absent from it reads as reachable from
nothing, however loudly it actually runs.

`_build_check_steps`' own coupling checklist called that dict "NOT an
obligation … a refinement, not a duty," on the true observation that `_seam`
falls back to a kebab-cased display name. The fallback keeps the MX seam
correct and is invisible to the ratchet, so the two consumers of one dict
disagreed about whether writing to it was optional. This suite is the witness
that they agree.

It is not a prose grader: both sides are derived by executing real code — the
live step list and the ratchet's own `check_registry_members` — which is why it
escapes the refusal recorded in that docstring against grepping the docstring
itself (`gz validate --tautological-test-audit`,
`.claude/rules/guardrail-feedback-prose.md` § Enforcement posture).
"""

from __future__ import annotations

import importlib.util
import unittest
from types import ModuleType

from gzkit.commands.common import get_project_root

# The canonical authored copy. `gz agent sync control-surfaces` mirrors it to
# `src/gzkit/chores/` for the wheel, and `gz validate --distribution` fails
# closed on any drift between them, so testing one tests both.
_RATCHET = (
    get_project_root()
    / ".gzkit"
    / "chores"
    / "control-surface-validator-reachability"
    / "check_reachability.py"
)


def _load_ratchet() -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_reachability_ratchet", _RATCHET)
    if spec is None or spec.loader is None:
        raise unittest.SkipTest(f"cannot load {_RATCHET}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _live_step_names() -> set[str]:
    from gzkit.commands.quality import _build_check_steps

    return {name for name, _ in _build_check_steps()}


def _fallback_stem(step_name: str) -> str:
    """The guard stem `_seam` derives for a step absent from `_STEP_GUARD_META`."""
    return step_name.lower().replace(" ", "-")


class TestRatchetSeesEveryGatedStep(unittest.TestCase):
    """A step that gates a real scope must be visible to the ratchet."""

    def test_no_live_step_gates_a_scope_the_ratchet_reads_as_ungated(self) -> None:
        ratchet = _load_ratchet()
        root = get_project_root()
        seen_as_gated = ratchet.check_registry_members(root)
        scopes = {flag.lstrip("-") for flag in ratchet.runnable_scopes()}

        invisible = sorted(
            name
            for name in _live_step_names()
            if _fallback_stem(name) in scopes and _fallback_stem(name) not in seen_as_gated
        )

        self.assertEqual(
            invisible,
            [],
            "These gz check steps run a real gz validate scope, but "
            "check_reachability.py reads them as ungated because they are absent "
            f"from _STEP_GUARD_META: {invisible}. Add the entry — the kebab-case "
            "fallback in _seam keeps the MX seam correct and is invisible to the "
            "regex the ratchet uses, so the scope is filed as protecting nothing "
            "while it runs on every commit.",
        )


class TestNoStaleGuardMetaEntry(unittest.TestCase):
    """The inverse: an entry outliving its step tells the ratchet a lie."""

    def test_guard_meta_names_no_step_that_no_longer_exists(self) -> None:
        from gzkit.commands.quality import _STEP_GUARD_META

        orphans = sorted(set(_STEP_GUARD_META) - _live_step_names())

        self.assertEqual(
            orphans,
            [],
            f"_STEP_GUARD_META names steps absent from _build_check_steps(): {orphans}. "
            "Drop them; the ratchet would keep reading their scopes as gated after "
            "the gate was removed, which is the false-green direction.",
        )


if __name__ == "__main__":
    unittest.main()
