"""The hexagon test gates as a ``gz validate`` scope (RP-7, change order of 2026-11-12).

Holds every test module covering a hexagon region to ``.gzkit/rules/tests.md``
§ Hexagon tests, three rules at once:

- **mock** (#91): a test covering an inner region imports no ``unittest.mock``; a
  test covering only adapters may patch a target outside the package and nothing
  inside it, and a bare ``Mock()`` is a finding, since nothing shows it stands at
  the outer edge;
- **labels** (#91a): each test method carries ``# given``, ``# when`` and
  ``# then`` comments in that order, read with ``tokenize``;
- **covers** (#91b): each test method carries ``@covers``, unless the module
  declares ``# hexagon-test: fake-adapter``.

The regions held are the domain, both port packages, the handlers and the three
adapter regions; the kernel and the configurator are not held (operator rulings of
2026-11-13: *"Regions incl. adapters"*, *"Exclude the kernel"*, *"Per patch
target"*, *"Module comment marker"*). A test module covers a region when it imports a
module the package map in ``pyproject.toml`` ``[tool.py-gzkit.hexagon]`` places
there, at any depth of the file. The variant gate (#91c) is due by the first
hexagon REQ admitted (H15) and is not here.

Today's findings sit in the shrink-only ``data/hexagon_test_baseline.json``: a
finding it does not hold fails, and so does a held finding the tree no longer
produces. A test module that does not parse, a malformed map and an unreadable
baseline fail too. It sits in the default tier, so it runs in every per-change
``gz check``.

Mode contract (``.gzkit/rules/mode-contract.md``): on at the operational
condition; advisory at the hangar and drydock levels, where the MX checkpoint
demotes it like every non-critical scope, restored at the exit re-run.
"""

import ast
import io
import tokenize
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from gzkit.kernel.dependency_checker import (
    PackageMap,
    PackageMapError,
    PackageMapMissingError,
    Region,
    held_keys,
    load_package_map,
)
from gzkit.registries import RegistryError, load_registry, registry_path
from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = [
    "BASELINE",
    "BASELINE_NAME",
    "FAKE_ADAPTER_MARKER",
    "HexagonTestFinding",
    "HexagonTestReadError",
    "TestRule",
    "audit_hexagon_tests",
    "check_hexagon_tests",
]

_TYPE = "hexagon_tests"

#: The shrink-only baseline's registry name, read through ``gzkit.registries``.
BASELINE_NAME = "hexagon_test_baseline.json"

#: The baseline as a reader names it in a message.
BASELINE = f"data/{BASELINE_NAME}"

#: The comment a fake adapter's test module carries to leave the ``@covers`` gate.
FAKE_ADAPTER_MARKER = "hexagon-test: fake-adapter"

_SPEC = ".gzkit/rules/tests.md § Hexagon tests"

_RERUN = "Fix it, then re-run `uv run gz validate --hexagon-tests`."

_INNER = frozenset(
    {Region.DOMAIN, Region.DRIVING_PORTS, Region.DRIVEN_PORTS, Region.HANDLERS},
)

_HELD = _INNER | {Region.DRIVING_ADAPTERS, Region.REPOSITORY_ADAPTERS, Region.DRIVEN_ADAPTERS}

_MOCK = "unittest.mock"

_PATCHERS = frozenset({"patch", "patch.object", "patch.dict", "patch.multiple"})

_DOUBLES = frozenset(
    {
        "Mock",
        "MagicMock",
        "AsyncMock",
        "NonCallableMock",
        "NonCallableMagicMock",
        "PropertyMock",
        "create_autospec",
    },
)

_LABELS = ("given", "when", "then")


class TestRule(StrEnum):
    """The kind of finding, one per gate."""

    __test__ = False

    MOCK = "mock"
    LABELS = "labels"
    COVERS = "covers"


class HexagonTestFinding(BaseModel):
    """One breach of the hexagon test discipline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: TestRule
    subject: str = Field(..., description="The test module, or module::Class.method")
    detail: str = Field("", description="What the test reached, for a mock finding")

    @property
    def key(self) -> str:
        """The finding's stable identity, as the baseline records it."""
        tail = f" -> {self.detail}" if self.detail else ""
        return f"{self.rule} {self.subject}{tail}"


class HexagonTestReadError(ValueError):
    """A test module under the tests directory does not parse."""


def check_hexagon_tests(
    package_map: PackageMap, project_root: Path, tests_dir: str = "tests"
) -> list[HexagonTestFinding]:
    """Check every test module covering a held region.

    Returns:
        The findings, sorted by key.

    Raises:
        HexagonTestReadError: a test module does not parse.

    """
    findings: set[HexagonTestFinding] = set()
    root = project_root / tests_dir
    for path in sorted(root.rglob("test*.py")) if root.is_dir() else []:
        rel = path.relative_to(project_root).as_posix()
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
            comments = _comments(source)
        except (SyntaxError, tokenize.TokenError) as exc:
            msg = f"{rel}: the test module does not parse ({exc})"
            raise HexagonTestReadError(msg) from exc
        regions = _regions(package_map, tree)
        if not regions:
            continue
        findings.update(_mock_findings(package_map, rel, tree, inner=bool(regions & _INNER)))
        exempt = any(text == FAKE_ADAPTER_MARKER for _, text in comments)
        for name, node in _test_methods(tree):
            subject = f"{rel}::{name}"
            if not _labelled(node, comments):
                findings.add(HexagonTestFinding(rule=TestRule.LABELS, subject=subject))
            if not exempt and not _has_covers(node):
                findings.add(HexagonTestFinding(rule=TestRule.COVERS, subject=subject))
    return sorted(findings, key=lambda f: f.key)


def audit_hexagon_tests(project_root: Path) -> list[ValidationError]:
    """Check the tests against the package map and the shrink-only baseline.

    Returns:
        One error per finding the baseline does not hold, one per held finding the
        tree no longer produces, or one for a malformed map, test module or baseline.

    """
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    try:
        package_map = load_package_map(pyproject)
        findings = check_hexagon_tests(package_map, project_root)
    except PackageMapMissingError:
        return []
    except PackageMapError as exc:
        message = f"{exc}: the package map cannot be read ({_SPEC}). {_RERUN}"
        return [ValidationError(type=_TYPE, artifact="pyproject.toml", message=message)]
    except HexagonTestReadError as exc:
        message = f"{exc}: a test the gates cannot read never passes ({_SPEC}). {_RERUN}"
        return [ValidationError(type=_TYPE, artifact=str(exc).split(":", 1)[0], message=message)]
    try:
        held = _held(project_root)
    except (RegistryError, ValueError) as exc:
        message = (
            f"{BASELINE}: {exc}. The baseline cannot be read, and a check held to an "
            f"unreadable baseline would pass silently ({_SPEC}). Restore it from git "
            f"(`git checkout -- {BASELINE}`), then re-run `uv run gz validate --hexagon-tests`."
        )
        return [ValidationError(type=_TYPE, artifact=BASELINE, message=message)]
    found = {f.key for f in findings}
    errors = [
        ValidationError(
            type=_TYPE,
            artifact=key.split(" ")[1].split("::")[0],
            message=(
                f"{key}: a new hexagon test finding ({_SPEC}). A hexagon test uses "
                "hand-written fakes and patches only targets outside the package, carries "
                "`# given`, `# when` and `# then` comments in order, and names its REQ with "
                f"`@covers`; never add it to {BASELINE}. {_RERUN}"
            ),
        )
        for key in sorted(found - held)
    ]
    errors.extend(
        ValidationError(
            type=_TYPE,
            artifact=BASELINE,
            message=(
                f"{key}: repaired, and the baseline only shrinks ({_SPEC}); remove it from "
                f"{BASELINE}, then re-run `uv run gz validate --hexagon-tests`."
            ),
        )
        for key in sorted(held - found)
    )
    return errors


def _held(project_root: Path) -> frozenset[str]:
    """Return the finding keys the baseline holds; a project without one holds none.

    Returns:
        The held keys.

    """
    if not registry_path(project_root, BASELINE_NAME).is_file():
        return frozenset()
    return held_keys(load_registry(project_root, BASELINE_NAME))


def _comments(source: str) -> list[tuple[int, str]]:
    """Return each comment's line and its text, stripped of ``#`` and lowered.

    Returns:
        ``(line, text)`` pairs in source order.

    """
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return [
        (tok.start[0], tok.string.lstrip("#").strip().lower())
        for tok in tokens
        if tok.type == tokenize.COMMENT
    ]


def _imported(tree: ast.Module) -> Iterator[str]:
    """Yield every absolute module name the file imports, at any depth."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            yield node.module
            yield from (f"{node.module}.{alias.name}" for alias in node.names)


def _regions(package_map: PackageMap, tree: ast.Module) -> set[Region]:
    """Return the held regions the module's imports reach.

    Returns:
        The held regions covered.

    """
    regions: set[Region] = set()
    for name in _imported(tree):
        part = package_map.part_of(name)
        if part is not None and package_map.parts[part] in _HELD:
            regions.add(package_map.parts[part])
    return regions


def _bindings(tree: ast.Module) -> dict[str, str]:
    """Map each name the file's imports bind to the dotted name it stands for.

    Returns:
        The bound name and its dotted target.

    """
    bound: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name, target = _import_binding(alias)
                bound[name] = target
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            bound.update({a.asname or a.name: f"{node.module}.{a.name}" for a in node.names})
    return bound


def _import_binding(alias: ast.alias) -> tuple[str, str]:
    """Return the name ``import x.y [as z]`` binds and what it stands for.

    Returns:
        ``(z, x.y)`` with an alias, else ``(x, x)``.

    """
    if alias.asname:
        return alias.asname, alias.name
    head = alias.name.split(".", 1)[0]
    return head, head


def _dotted(expr: ast.expr, bound: dict[str, str]) -> str | None:
    """Resolve *expr* to a dotted name through the file's imports.

    Returns:
        The dotted name, or ``None`` when *expr* is not an imported name or attribute.

    """
    if isinstance(expr, ast.Name):
        return bound.get(expr.id)
    if isinstance(expr, ast.Attribute):
        base = _dotted(expr.value, bound)
        return f"{base}.{expr.attr}" if base else None
    return None


def _in_package(package_map: PackageMap, name: str) -> bool:
    return name == package_map.package or name.startswith(f"{package_map.package}.")


def _mock_findings(
    package_map: PackageMap, rel: str, tree: ast.Module, *, inner: bool
) -> set[HexagonTestFinding]:
    """Return the module's mock findings.

    Returns:
        One finding for a mock import in an inner-region test, otherwise one per
        package target patched and per bare double.

    """
    imports_mock = any(n == _MOCK or n.startswith(f"{_MOCK}.") for n in _imported(tree))
    if inner:
        if imports_mock:
            return {HexagonTestFinding(rule=TestRule.MOCK, subject=rel, detail=_MOCK)}
        return set()
    bound = _bindings(tree)
    out: set[HexagonTestFinding] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = _dotted(node.func, bound)
        if func is None or not func.startswith(f"{_MOCK}."):
            continue
        helper = func.removeprefix(f"{_MOCK}.")
        detail = _breach(package_map, helper, node, bound)
        if detail:
            out.add(HexagonTestFinding(rule=TestRule.MOCK, subject=rel, detail=detail))
    return out


def _breach(package_map: PackageMap, helper: str, node: ast.Call, bound: dict[str, str]) -> str:
    """Name what a mock call reaches inside the package, or ``""`` for an outer target.

    Returns:
        The finding's detail, or an empty string when the call stands at the outer edge.

    """
    if helper in _DOUBLES:
        return f"{helper}()"
    if helper not in _PATCHERS or not node.args:
        return ""
    return _patch_breach(package_map, helper, node, bound)


def _patch_breach(
    package_map: PackageMap, helper: str, node: ast.Call, bound: dict[str, str]
) -> str:
    """Name the package target a patcher replaces, or ``""`` for an outer one.

    Returns:
        The patched target inside the package, the unresolved expression, or ``""``.

    """
    target = node.args[0]
    if isinstance(target, ast.Constant) and isinstance(target.value, str):
        return target.value if _in_package(package_map, target.value) else ""
    dotted = _dotted(target, bound)
    if dotted is None:
        return f"{helper}({ast.unparse(target)})"
    if not _in_package(package_map, dotted):
        return ""
    attr = node.args[1] if len(node.args) > 1 else None
    if isinstance(attr, ast.Constant) and isinstance(attr.value, str):
        return f"{dotted}.{attr.value}"
    return dotted


def _test_methods(tree: ast.Module) -> Iterator[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    """Yield each ``test*`` method of each class, named ``Class.method``."""
    for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test"
            ):
                yield f"{cls.name}.{node.name}", node


def _labelled(
    node: ast.FunctionDef | ast.AsyncFunctionDef, comments: list[tuple[int, str]]
) -> bool:
    """Whether the method's comments hold given, when and then, in that order.

    Returns:
        ``True`` when the three labels appear in order inside the method.

    """
    end = node.end_lineno or node.lineno
    wanted = iter(_LABELS)
    label = next(wanted)
    for line, text in comments:
        if node.lineno <= line <= end and _is_label(text, label):
            label = next(wanted, "")
            if not label:
                return True
    return False


def _is_label(text: str, label: str) -> bool:
    if not text.startswith(label):
        return False
    rest = text[len(label) :]
    return not rest or not rest[0].isalnum()


def _has_covers(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether the method carries ``@covers``, called or bare, by any import path.

    Returns:
        ``True`` when a decorator's name is ``covers``.

    """
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
        if name == "covers":
            return True
    return False
