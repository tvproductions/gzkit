"""``gzkit.cli``'s lazy exports are visible to a static reader (RO-9 tranche 4).

``gzkit.cli`` supplies most of ``__all__`` through a PEP 562 ``__getattr__`` so
``gz --help`` imports none of them. A name a ``__getattr__`` supplies is invisible
to Ruff and ty, which read ``__all__`` against the module's bindings (F822), so
each lazy export is also imported under ``if TYPE_CHECKING:``. That block binds
nothing at runtime, so the import cost stays deferred.
"""

import ast
import importlib
import unittest
from pathlib import Path

_CLI_INIT = Path("src") / "gzkit" / "cli" / "__init__.py"


def _is_type_checking_guard(node: ast.If) -> bool:
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _statically_bound(tree: ast.Module) -> set[str]:
    """Return the names bound at module level, a TYPE_CHECKING block included.

    Returns:
        Every name an import, definition or assignment binds at module scope.
    """
    statements: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.If) and _is_type_checking_guard(node):
            statements.extend(node.body)
        else:
            statements.append(node)
    bound: set[str] = set()
    for node in statements:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            bound.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            bound.update(t.id for t in targets if isinstance(t, ast.Name))
    return bound


def _declared_all(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
        ):
            return list(ast.literal_eval(node.value))
    return []


class TestLazyExportsDeclared(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = ast.parse(_CLI_INIT.read_text(encoding="utf-8"))

    def test_every_export_is_statically_bound(self) -> None:
        self.assertTrue(_declared_all(self.tree), f"{_CLI_INIT} declares no __all__")
        unbound = sorted(set(_declared_all(self.tree)) - _statically_bound(self.tree))
        self.assertEqual(unbound, [], "names in __all__ a static reader cannot resolve")

    def test_every_export_resolves_to_its_lazy_target(self) -> None:
        cli = importlib.import_module("gzkit.cli")
        for name in _declared_all(self.tree):
            with self.subTest(name=name):
                target = cli._LAZY_ATTRS.get(name)
                if target is None:
                    continue
                module_path, attr = target
                expected = getattr(importlib.import_module(module_path), attr)
                self.assertIs(getattr(cli, name), expected)


if __name__ == "__main__":
    unittest.main()
