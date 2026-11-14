"""The output port names no Rich type, and its table caller imports no Rich (GHI #1321).

Read from source with ``ast`` so the check imports nothing it inspects: point 1 of the
core model in ``docs/rnd/hexagonal-specification.md`` (ports use only domain types)
and canon rule 3 of ``.gzkit/rules/hexagonal-architecture.md``.
"""

import ast
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_FORMATTER = _ROOT / "src" / "gzkit" / "cli" / "formatters.py"
_TABLE_CALLER = _ROOT / "src" / "gzkit" / "commands" / "chores_status_cmd.py"


def _rich_names(tree: ast.Module) -> set[str]:
    """Return every local name bound to something imported from ``rich``."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "rich":
            names.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update(
                (alias.asname or alias.name).split(".")[0]
                for alias in node.names
                if alias.name.split(".")[0] == "rich"
            )
    return names


def _public_annotations(tree: ast.Module, class_name: str) -> dict[str, list[ast.expr]]:
    """Return each public method's parameter and return annotations in *class_name*."""
    out: dict[str, list[ast.expr]] = {}
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == class_name):
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                args = item.args.posonlyargs + item.args.args + item.args.kwonlyargs
                notes = [a.annotation for a in args if a.annotation is not None]
                if item.returns is not None:
                    notes.append(item.returns)
                out[item.name] = notes
    return out


def _names_in(expr: ast.expr) -> set[str]:
    found = {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}
    found |= {
        n.value for n in ast.walk(expr) if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }
    return found


class TestOutputPortIsDomainTyped(unittest.TestCase):
    """No public method of ``OutputFormatter`` takes or returns a Rich type."""

    def test_no_public_method_names_a_rich_type(self) -> None:
        tree = ast.parse(_FORMATTER.read_text(encoding="utf-8"))
        rich = _rich_names(tree)
        self.assertTrue(rich, "the adapter imports rich; the check must see those names")
        offenders = sorted(
            name
            for name, notes in _public_annotations(tree, "OutputFormatter").items()
            if any(_names_in(note) & rich for note in notes)
        )
        self.assertEqual(offenders, [])

    def test_a_rich_annotation_is_caught(self) -> None:
        planted = ast.parse(
            "from rich.table import Table\n"
            "class OutputFormatter:\n"
            "    def table(self, view: Table) -> None: ...\n"
        )
        offenders = [
            name
            for name, notes in _public_annotations(planted, "OutputFormatter").items()
            if any(_names_in(note) & _rich_names(planted) for note in notes)
        ]
        self.assertEqual(offenders, ["table"])

    def test_the_table_caller_imports_no_rich(self) -> None:
        tree = ast.parse(_TABLE_CALLER.read_text(encoding="utf-8"))
        self.assertEqual(_rich_names(tree), set())


if __name__ == "__main__":
    unittest.main()
