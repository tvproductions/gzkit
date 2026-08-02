"""`gz check` membership is declared, not accidental (GHI #744).

`_build_check_steps()` is a hand-written literal list that never reads
``VALIDATOR_REGISTRY``. Registering a scope in ``gz validate`` therefore does
NOT enroll it in the commit-time gate, and omitting the second edit produces no
signal — the scope simply never runs. That is how ``--rule-version-markers``, a
*default-tier* scope, failed for eight days while every commit's ``gz check``
passed (fixed instance ``2810b8e51``; the gap that hid it is what this fences).

The fix is not "enroll everything": 42 of 84 scopes are deliberately outside the
gate, and a flag-scoped step costs a full subprocess (the coupling is a command
STRING — ``run_command("uv run gz validate --<flag>")`` — not a function call).
The fix is to make membership **declared**, so adding a scope forces a decision
and drift fails closed.

Two invariants bind here. Membership must match the source (either direction of
drift fails), and every ``default``-tier scope must actually gate — the operator
ruling of 2026-08-02 enrolled the ten that did not, via one bare ``gz validate``
covering the whole tier in a single ~2s subprocess rather than ten.

``data/check_scope_membership.json`` is that declaration. This module recomputes
the true membership from source and fails when the two disagree.
"""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

_FLAG_RE = re.compile(r"gz validate ((?:--[a-z0-9-]+\s*)+)")

# A bare `gz validate` runs the whole default tier in one subprocess. Anchored to
# the WHOLE string so prose mentioning the command in a docstring is not mistaken
# for an invocation — only a string that IS the command counts.
_BARE_VALIDATE_RE = re.compile(r"^(?:uv\s+run\s+)?gz\s+validate\s*$")

_ROOT = Path(__file__).resolve().parents[2]
_VALIDATE_CMD = _ROOT / "src" / "gzkit" / "commands" / "validate_cmd.py"
_QUALITY = _ROOT / "src" / "gzkit" / "quality.py"
_QUALITY_CMD = _ROOT / "src" / "gzkit" / "commands" / "quality.py"
_ROSTER = _ROOT / "data" / "check_scope_membership.json"


def _func_defs(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _called_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            fn = sub.func
            if isinstance(fn, ast.Name):
                out.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                out.add(fn.attr)
    return out


def _flags_in(node: ast.AST) -> tuple[set[str], bool]:
    """Scope stems named under ``node``, and whether a BARE `gz validate` appears.

    A bare invocation carries no flag and runs the entire default tier, so it
    cannot be read off a flag token — it has to be reported separately and
    expanded against the registry's tiers by the caller.
    """
    out: set[str] = set()
    bare = False
    for sub in ast.walk(node):
        if not (isinstance(sub, ast.Constant) and isinstance(sub.value, str)):
            continue
        for group in _FLAG_RE.findall(sub.value):
            out.update(
                tok.strip().lstrip("-").replace("-", "_")
                for tok in group.split()
                if tok.startswith("--")
            )
        if _BARE_VALIDATE_RE.match(sub.value.strip()):
            bare = True
    return out, bare


def registry_scopes(validate_cmd_src: str) -> dict[str, str]:
    """``{stem: tier}`` for every scope declared in ``VALIDATOR_REGISTRY``."""
    scopes: dict[str, str] = {}
    for node in ast.walk(ast.parse(validate_cmd_src)):
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        else:
            continue
        if not (isinstance(target, ast.Name) and target.id == "VALIDATOR_REGISTRY" and value):
            continue
        for entry in ast.walk(value):
            if (
                isinstance(entry, ast.Call)
                and isinstance(entry.func, ast.Name)
                and entry.func.id == "_ScopeEntry"
                and len(entry.args) >= 2
            ):
                scopes[ast.literal_eval(entry.args[0])] = ast.literal_eval(entry.args[1])
    return scopes


def scopes_reached_by_check(
    quality_src: str, quality_cmd_src: str, scopes: dict[str, str] | None = None
) -> set[str]:
    """Scope stems the `gz check` step list actually invokes.

    Resolves each ``_build_check_steps()`` entry to its ``run_*`` function and
    walks that function's callees, collecting the ``gz validate --flag`` tokens
    embedded in string literals along the way. A bare ``gz validate`` expands to
    every ``default``-tier stem in ``scopes`` (GHI #744): one subprocess runs the
    whole tier, so reachability must follow the tier, not a flag token.
    """
    quality_cmd_tree = ast.parse(quality_cmd_src)
    defs = _func_defs(ast.parse(quality_src)) | _func_defs(quality_cmd_tree)

    step_fns: set[str] = set()
    for node in ast.walk(quality_cmd_tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "_build_check_steps"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Tuple) and len(sub.elts) == 2:
                label, fn = sub.elts
                if isinstance(label, ast.Constant) and isinstance(fn, ast.Name):
                    step_fns.add(fn.id)

    reached: set[str] = set()
    saw_bare = False
    seen, frontier = set(step_fns), list(step_fns)
    for _ in range(4):
        nxt: list[str] = []
        for name in frontier:
            body = defs.get(name)
            if body is None:
                continue
            flags, bare = _flags_in(body)
            reached |= flags
            saw_bare = saw_bare or bare
            for callee in _called_names(body) - seen:
                seen.add(callee)
                nxt.append(callee)
        frontier = nxt
    if saw_bare and scopes:
        reached |= {stem for stem, tier in scopes.items() if tier == "default"}
    return reached


class TestExtractorsDetectRealChanges(unittest.TestCase):
    """The fence must be able to fail. Exercised against synthetic sources.

    Without these, `test_declared_membership_matches_source` could pass by
    computing nothing at all — the tautology GHI #730 names, where a check is
    green because its scope structurally cannot see its field.
    """

    def test_registry_scopes_reads_stems_and_tiers(self) -> None:
        src = (
            "VALIDATOR_REGISTRY: tuple[_ScopeEntry, ...] = (\n"
            "    _ScopeEntry('alpha', 'default', True, lambda r, _f: []),\n"
            "    _ScopeEntry('beta', 'explicit', True, lambda r, _f: []),\n"
            ")\n"
        )
        self.assertEqual(registry_scopes(src), {"alpha": "default", "beta": "explicit"})

    def test_a_scope_added_to_the_registry_is_seen(self) -> None:
        """Adding an entry changes the computed set — the fence tracks the source."""
        one = "VALIDATOR_REGISTRY: tuple = (_ScopeEntry('alpha', 'default', True, None),)\n"
        two = one.replace(")\n", "    _ScopeEntry('gamma', 'explicit', True, None),\n)\n").replace(
            "(_ScopeEntry", "(\n    _ScopeEntry"
        )
        self.assertEqual(set(registry_scopes(two)) - set(registry_scopes(one)), {"gamma"})

    def test_bare_validate_reaches_every_default_tier_scope(self) -> None:
        """One bare invocation runs the whole default tier (GHI #744)."""
        quality = (
            "def run_defaults(root):\n    return run_command('uv run gz validate', cwd=root)\n"
        )
        quality_cmd = "def _build_check_steps():\n    return [('Defaults', run_defaults)]\n"
        scopes = {"alpha": "default", "beta": "default", "gamma": "explicit"}
        self.assertEqual(scopes_reached_by_check(quality, quality_cmd, scopes), {"alpha", "beta"})

    def test_prose_naming_the_command_is_not_an_invocation(self) -> None:
        """A docstring mentioning `gz validate` must not count as running it."""
        quality = (
            "def run_defaults(root):\n"
            '    """Recovery: run gz validate to see the failing scope."""\n'
            "    return run_command('uv run gz cli audit', cwd=root)\n"
        )
        quality_cmd = "def _build_check_steps():\n    return [('Defaults', run_defaults)]\n"
        scopes = {"alpha": "default"}
        self.assertEqual(scopes_reached_by_check(quality, quality_cmd, scopes), set())

    def test_flagged_validate_does_not_expand_to_the_whole_tier(self) -> None:
        """`gz validate --one-scope` reaches one scope, not the default tier."""
        quality = (
            "def run_one(root):\n    return run_command('uv run gz validate --alpha', cwd=root)\n"
        )
        quality_cmd = "def _build_check_steps():\n    return [('One', run_one)]\n"
        scopes = {"alpha": "default", "beta": "default"}
        self.assertEqual(scopes_reached_by_check(quality, quality_cmd, scopes), {"alpha"})

    def test_check_flags_are_read_from_command_strings(self) -> None:
        """The coupling is a subprocess string, so the extractor must read strings."""
        quality = (
            "def run_alpha_audit(root):\n"
            "    return run_command('uv run gz validate --alpha-scope', cwd=root)\n"
        )
        quality_cmd = "def _build_check_steps():\n    return [('Alpha', run_alpha_audit)]\n"
        self.assertEqual(scopes_reached_by_check(quality, quality_cmd), {"alpha_scope"})

    def test_a_step_removed_from_the_list_stops_being_reached(self) -> None:
        quality = (
            "def run_alpha_audit(root):\n"
            "    return run_command('uv run gz validate --alpha-scope', cwd=root)\n"
        )
        wired = "def _build_check_steps():\n    return [('Alpha', run_alpha_audit)]\n"
        unwired = "def _build_check_steps():\n    return []\n"
        self.assertEqual(scopes_reached_by_check(quality, wired), {"alpha_scope"})
        self.assertEqual(scopes_reached_by_check(quality, unwired), set())

    def test_flags_reached_through_a_helper_are_followed(self) -> None:
        """Steps that delegate to a helper still count as reaching the scope."""
        quality = (
            "def _helper(root):\n"
            "    return run_command('uv run gz validate --deep-scope', cwd=root)\n"
            "def run_outer_audit(root):\n"
            "    return _helper(root)\n"
        )
        quality_cmd = "def _build_check_steps():\n    return [('Outer', run_outer_audit)]\n"
        self.assertEqual(scopes_reached_by_check(quality, quality_cmd), {"deep_scope"})


class TestCommittedCheckMembership(unittest.TestCase):
    """Fail-closed parity between the declared roster and the real source."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._roster = json.loads(_ROSTER.read_text(encoding="utf-8"))
        cls._in_check = set(cls._roster["in_check"])
        cls._out_of_check = set(cls._roster["out_of_check"])
        scopes = registry_scopes(_VALIDATE_CMD.read_text(encoding="utf-8"))
        cls._scopes = scopes
        cls._registry = set(scopes)
        cls._reached = scopes_reached_by_check(
            _QUALITY.read_text(encoding="utf-8"),
            _QUALITY_CMD.read_text(encoding="utf-8"),
            scopes,
        )

    def test_declared_membership_matches_source(self) -> None:
        """`in_check` is exactly what `gz check` invokes — no more, no less."""
        self.assertEqual(
            self._reached,
            self._in_check,
            "gz check's validate-scope membership changed without updating "
            "data/check_scope_membership.json. A scope newly reached must move to "
            "`in_check`; a scope no longer reached must move to `out_of_check`.",
        )

    def test_every_default_tier_scope_runs_in_the_gate(self) -> None:
        """Default tier means "on when `gz validate` runs bare" — so it must gate.

        Operator ruling 2026-08-02: the 10 default-tier scopes that `gz check`
        never ran (manifest, ledger, documents, briefs, frontmatter, personas,
        surfaces, version, instructions, rule_version_markers) are enrolled. A
        scope declared default-tier but absent from the gate is the exact
        condition that let a --rule-version-markers breach survive eight days of
        green commits, so it now fails closed rather than being merely declared.
        """
        missing = {s for s, tier in self._scopes.items() if tier == "default"} - self._reached
        self.assertEqual(
            missing,
            set(),
            "Default-tier scope(s) are not reachable from gz check. Either wire "
            "them in (a bare `uv run gz validate` covers the whole default tier "
            "in one subprocess) or reclassify them as explicit tier in "
            "VALIDATOR_REGISTRY.",
        )

    def test_every_registered_scope_is_classified(self) -> None:
        """A new `gz validate` scope cannot be silently outside the gate.

        This is the GHI #744 defect proper: registering a scope without the
        matching quality.py edit produced no signal. Now it fails here until the
        scope is explicitly placed in `in_check` or `out_of_check`.
        """
        unclassified = self._registry - self._in_check - self._out_of_check
        self.assertEqual(
            unclassified,
            set(),
            "New gz validate scope(s) are in VALIDATOR_REGISTRY but classified "
            "in neither `in_check` nor `out_of_check` of "
            "data/check_scope_membership.json. Decide whether each belongs in the "
            "commit-time gate (wire it into _build_check_steps and add it to "
            "`in_check`) or not (add it to `out_of_check`).",
        )

    def test_roster_names_no_scope_that_does_not_exist(self) -> None:
        """Retiring a scope must retire its roster entry too."""
        universe = self._registry | self._reached
        self.assertEqual(
            (self._in_check | self._out_of_check) - universe,
            set(),
            "data/check_scope_membership.json names scope(s) that are neither in "
            "VALIDATOR_REGISTRY nor reached by gz check. Remove the stale entries.",
        )

    def test_summary_counts_agree_with_the_lists(self) -> None:
        """`_counts` is a derived view; it may never disagree with its source.

        A hand-edited roster whose summary still reads the old numbers is the
        same Layer-3-shadowing-Layer-1 shape Architectural Boundary 6 forbids,
        just smaller.
        """
        counts = self._roster["_counts"]
        self.assertEqual(counts["registry_scopes"], len(self._registry))
        self.assertEqual(counts["in_check"], len(self._in_check))
        self.assertEqual(counts["out_of_check"], len(self._out_of_check))
        self.assertEqual(
            sorted(counts["reached_outside_registry"]),
            sorted(self._reached - self._registry),
        )

    def test_second_dispatch_path_scopes_are_accounted(self) -> None:
        """Scopes wired outside VALIDATOR_REGISTRY are still classified.

        `--qc-binding`, `--fidelity-presence` and `--waiver-ratchet` dispatch
        through the early-return chain in `validate_cmd.py` and never reach
        VALIDATOR_REGISTRY, despite its header calling itself the "Single source
        of validate dispatch". A registry-only fence would miss them, so the
        roster's universe is the registry UNION what check actually reaches.
        """
        outside_registry = self._reached - self._registry
        self.assertTrue(
            outside_registry <= self._in_check,
            f"Scopes reached by gz check but absent from VALIDATOR_REGISTRY are "
            f"unclassified: {sorted(outside_registry - self._in_check)}",
        )


if __name__ == "__main__":
    unittest.main()
