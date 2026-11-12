"""The dependency checker: the hexagon's dependency rules, read from the package map.

Stdlib only (``ast``, ``tomllib``); it parses source and never imports or runs it.
gzkit runs it through ``tests/policy/test_import_boundaries.py`` and
``gz validate --hexagon-dependencies``, and an adopter runs it on its own map.

It reads the hexagonal architecture system package map from ``pyproject.toml``
``[tool.py-gzkit.hexagon]`` and reports four kinds of finding
(``docs/governance/hexagonal-architecture.md`` § The dependency rules):

- ``unmapped``: a package or module no region names;
- ``import``: an import the importer's region may not make;
- ``base``: a kernel base subclassed outside its region;
- ``handler``: a handler that does not inherit exactly one use-case ``Protocol``
  from the driving ports, or does not take its name from it.

A module no region names is reported once, as ``unmapped``; its imports are not
judged, since it has no region to judge them by.
"""

import ast
import json
import sys
import tomllib
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = [
    "Finding",
    "PackageMap",
    "PackageMapError",
    "Region",
    "Rule",
    "check",
    "compare",
    "load_baseline",
    "load_package_map",
]


class Region(StrEnum):
    """A part of the hexagon, spelled as the package map spells its keys."""

    KERNEL = "kernel"
    DOMAIN = "domain"
    DRIVING_PORTS = "driving-ports"
    DRIVEN_PORTS = "driven-ports"
    HANDLERS = "handlers"
    DRIVING_ADAPTERS = "driving-adapters"
    REPOSITORY_ADAPTERS = "repository-adapters"
    DRIVEN_ADAPTERS = "driven-adapters"
    CONFIGURATOR = "configurator"


class Rule(StrEnum):
    """The kind of finding."""

    UNMAPPED = "unmapped"
    IMPORT = "import"
    BASE = "base"
    HANDLER = "handler"


_R = Region

#: The specification's per-region table: the other regions each region may import.
MAY_IMPORT: dict[Region, frozenset[Region]] = {
    _R.KERNEL: frozenset(),
    _R.DOMAIN: frozenset({_R.KERNEL}),
    _R.DRIVING_PORTS: frozenset({_R.KERNEL}),
    _R.DRIVEN_PORTS: frozenset({_R.KERNEL}),
    _R.HANDLERS: frozenset({_R.DOMAIN, _R.DRIVING_PORTS, _R.DRIVEN_PORTS, _R.KERNEL}),
    _R.DRIVING_ADAPTERS: frozenset({_R.DRIVING_PORTS, _R.KERNEL}),
    _R.REPOSITORY_ADAPTERS: frozenset({_R.DOMAIN, _R.KERNEL}),
    _R.DRIVEN_ADAPTERS: frozenset({_R.DRIVEN_PORTS, _R.KERNEL}),
    _R.CONFIGURATOR: frozenset(Region),
}

#: Regions inside the walls: their one third-party import is Pydantic.
INNER: frozenset[Region] = frozenset(
    {_R.KERNEL, _R.DOMAIN, _R.DRIVING_PORTS, _R.DRIVEN_PORTS, _R.HANDLERS}
)

#: Regions holding adapters: no adapter imports another adapter.
ADAPTERS: frozenset[Region] = frozenset(
    {_R.DRIVING_ADAPTERS, _R.REPOSITORY_ADAPTERS, _R.DRIVEN_ADAPTERS}
)

#: Each kernel base and the regions a subclass of it may live in.
BASE_REGIONS: dict[str, frozenset[Region]] = {
    "ValueObject": frozenset({_R.DOMAIN}),
    "Entity": frozenset({_R.DOMAIN}),
    "DomainEvent": frozenset({_R.DOMAIN}),
    "Command": frozenset({_R.DRIVING_PORTS}),
    "Query": frozenset({_R.DRIVING_PORTS}),
    "Dto": frozenset({_R.DRIVING_PORTS, _R.DRIVEN_PORTS}),
}

_INNER_THIRD_PARTY = frozenset({"pydantic"})
_USE_CASE = "UseCase"
_HANDLER = "Handler"


class PackageMapError(ValueError):
    """The package map is missing or malformed: a fault in the project's configuration."""


class PackageMap(BaseModel):
    """The hexagonal architecture system package map, as read from ``pyproject.toml``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    package: str = Field(..., min_length=1, description="The import name of the package")
    source_root: str = Field(..., description="Directory holding the package, from the root")
    parts: dict[str, Region] = Field(..., description="Each mapped package and its region")

    def part_of(self, module: str) -> str | None:
        """Return the mapped package *module* belongs to, the longest that matches.

        Returns:
            The mapped package name, or ``None`` when no region names the module.

        """
        matches = [p for p in self.parts if module == p or module.startswith(f"{p}.")]
        return max(matches, key=len) if matches else None

    def is_container(self, module: str) -> bool:
        """Whether *module* only holds mapped packages, as ``gzkit`` and ``gzkit.core`` do.

        Returns:
            ``True`` when a mapped package sits below *module* and none at or above it.

        """
        if self.part_of(module) is not None:
            return False
        return any(p.startswith(f"{module}.") for p in self.parts)

    def unmapped_key(self, module: str) -> str:
        """Name the unmapped finding for *module*: its highest ancestor that holds no part.

        Returns:
            The package or module the finding names.

        """
        pieces = module.split(".")
        for depth in range(1, len(pieces) + 1):
            candidate = ".".join(pieces[:depth])
            if not self.is_container(candidate):
                return candidate
        return module


class Finding(BaseModel):
    """One breach of the dependency rules."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: Rule
    subject: str = Field(..., description="The module, class or package found in breach")
    detail: str = Field("", description="What it reached, or why it breaches")

    @property
    def key(self) -> str:
        """The finding's stable identity, as a baseline records it."""
        tail = f" -> {self.detail}" if self.detail else ""
        return f"{self.rule} {self.subject}{tail}"


def load_package_map(pyproject: Path) -> PackageMap:
    """Read ``[tool.py-gzkit.hexagon]`` from *pyproject*.

    Returns:
        The package map.

    Raises:
        PackageMapError: the table is absent, a key is unknown, or a package is
            mapped to two regions or lies outside the package.

    """
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    table = data.get("tool", {}).get("py-gzkit", {}).get("hexagon")
    if not isinstance(table, dict):
        msg = f"{pyproject.as_posix()}: no [tool.py-gzkit.hexagon] package map"
        raise PackageMapError(msg)
    package = str(table.get("package", ""))
    source_root = str(table.get("source-root", "src"))
    unknown = sorted(set(table) - {"package", "source-root"} - set(Region))
    if unknown:
        msg = f"package map: unknown keys {unknown}; regions are {[r.value for r in Region]}"
        raise PackageMapError(msg)
    parts: dict[str, Region] = {}
    for region in Region:
        for part in table.get(region.value, []):
            if part in parts:
                msg = f"package map: {part} is mapped to {parts[part]} and {region}"
                raise PackageMapError(msg)
            if part != package and not part.startswith(f"{package}."):
                msg = f"package map: {part} lies outside the package {package}"
                raise PackageMapError(msg)
            parts[part] = region
    return PackageMap(package=package, source_root=source_root, parts=parts)


class _Module(BaseModel):
    """One parsed source module."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    is_package: bool
    tree: ast.Module


def _modules(package_map: PackageMap, project_root: Path) -> list[_Module]:
    root = project_root / package_map.source_root
    found: list[_Module] = []
    for path in sorted((root / package_map.package).rglob("*.py")):
        rel = path.relative_to(root).with_suffix("")
        is_package = rel.name == "__init__"
        parts = rel.parts[:-1] if is_package else rel.parts
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
        found.append(_Module(name=".".join(parts), is_package=is_package, tree=tree))
    return found


def _imports(module: _Module, known: frozenset[str]) -> Iterator[str]:
    """Yield the dotted name of every module *module* imports, relative ones resolved."""
    for node in ast.walk(module.tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_from(module, node)
            for alias in node.names:
                candidate = f"{base}.{alias.name}"
                yield candidate if candidate in known else base


def _resolve_from(module: _Module, node: ast.ImportFrom) -> str:
    if not node.level:
        return node.module or ""
    anchor = module.name.split(".")
    if not module.is_package:
        anchor = anchor[:-1]
    anchor = anchor[: len(anchor) - (node.level - 1)]
    return ".".join([*anchor, node.module] if node.module else anchor)


def _import_findings(
    package_map: PackageMap, module: _Module, region: Region, known: frozenset[str]
) -> Iterator[Finding]:
    own = package_map.part_of(module.name)
    for target in sorted(set(_imports(module, known))):
        reason = _import_breach(package_map, own, region, target)
        if reason:
            yield Finding(rule=Rule.IMPORT, subject=module.name, detail=reason)


def _import_breach(package_map: PackageMap, own: str | None, region: Region, target: str) -> str:
    """Return what *target* is when the import breaches the table, else an empty string."""
    top = target.split(".", maxsplit=1)[0]
    if top != package_map.package:
        outside = top in sys.stdlib_module_names or region not in INNER
        return "" if outside or top in _INNER_THIRD_PARTY else f"{top} (third-party)"
    target_part = package_map.part_of(target)
    if target_part is None:
        return "" if region is Region.CONFIGURATOR else package_map.unmapped_key(target)
    return "" if _may_reach(package_map, own, region, target_part) else target_part


def _may_reach(package_map: PackageMap, own: str | None, region: Region, target_part: str) -> bool:
    """Whether a module of *own* in *region* may import the mapped package *target_part*."""
    target_region = package_map.parts[target_part]
    same_region = target_region is region and region not in ADAPTERS
    return target_part == own or same_region or target_region in MAY_IMPORT[region]


def _qualified_bases(module: _Module) -> Iterator[tuple[ast.ClassDef, list[str]]]:
    """Yield each class in *module* with its bases as dotted names, imports resolved."""
    aliases = dict(_aliases(module))
    for node in ast.walk(module.tree):
        if isinstance(node, ast.ClassDef):
            yield node, [_dotted(base, aliases) for base in node.bases]


def _aliases(module: _Module) -> Iterator[tuple[str, str]]:
    """Yield each name an import binds in *module*, with the dotted name it stands for."""
    for node in ast.walk(module.tree):
        if isinstance(node, ast.ImportFrom):
            base = _resolve_from(module, node)
            yield from ((a.asname or a.name, f"{base}.{a.name}") for a in node.names)
        elif isinstance(node, ast.Import):
            yield from (_import_binding(alias) for alias in node.names)


def _import_binding(alias: ast.alias) -> tuple[str, str]:
    """``import a.b`` binds ``a``; ``import a.b as x`` binds ``x`` to ``a.b``."""
    if alias.asname:
        return alias.asname, alias.name
    top = alias.name.split(".")[0]
    return top, top


def _dotted(expr: ast.expr, aliases: dict[str, str]) -> str:
    if isinstance(expr, ast.Name):
        return aliases.get(expr.id, expr.id)
    if isinstance(expr, ast.Attribute):
        return f"{_dotted(expr.value, aliases)}.{expr.attr}"
    if isinstance(expr, ast.Subscript):
        return _dotted(expr.value, aliases)
    return ""


def _base_findings(
    package_map: PackageMap, module: _Module, region: Region | None
) -> Iterator[Finding]:
    if region is Region.KERNEL:
        return
    where = region.value if region else "no region"
    for cls, bases in _qualified_bases(module):
        for name in _kernel_bases(package_map, bases):
            allowed = BASE_REGIONS.get(name)
            if allowed is not None and region not in allowed:
                subject = f"{module.name}.{cls.name}"
                yield Finding(
                    rule=Rule.BASE, subject=subject, detail=f"{name} subclassed in {where}"
                )


def _kernel_bases(package_map: PackageMap, bases: list[str]) -> Iterator[str]:
    """Yield the name of each base in *bases* that the kernel defines."""
    for base in bases:
        owner, _, name = base.rpartition(".")
        owner_part = package_map.part_of(owner) if owner else None
        if owner_part is not None and package_map.parts[owner_part] is Region.KERNEL:
            yield name


def _use_case_names(package_map: PackageMap, modules: list[_Module]) -> frozenset[str]:
    """Return the names of every use-case ``Protocol`` declared in the driving ports."""
    names: set[str] = set()
    for module in modules:
        part = package_map.part_of(module.name)
        if part is None or package_map.parts[part] is not Region.DRIVING_PORTS:
            continue
        for cls, bases in _qualified_bases(module):
            is_protocol = any(b.rpartition(".")[2] == "Protocol" for b in bases)
            if is_protocol and cls.name.endswith(_USE_CASE):
                names.add(cls.name)
    return frozenset(names)


def _handler_findings(
    package_map: PackageMap, module: _Module, use_cases: frozenset[str]
) -> Iterator[Finding]:
    for cls, bases in _qualified_bases(module):
        if cls.name.startswith("_") or cls not in module.tree.body:
            continue
        protocols = [_use_case(package_map, b, use_cases) for b in bases]
        named = [p for p in protocols if p]
        subject = f"{module.name}.{cls.name}"
        if len(named) != 1:
            detail = f"inherits {len(named)} use-case Protocols; a handler inherits exactly one"
            yield Finding(rule=Rule.HANDLER, subject=subject, detail=detail)
            continue
        expected = named[0].removesuffix(_USE_CASE) + _HANDLER
        if cls.name != expected:
            yield Finding(
                rule=Rule.HANDLER, subject=subject, detail=f"named for {named[0]}: {expected}"
            )


def _use_case(package_map: PackageMap, base: str, use_cases: frozenset[str]) -> str:
    owner, _, name = base.rpartition(".")
    part = package_map.part_of(owner) if owner else None
    in_ports = part is not None and package_map.parts[part] is Region.DRIVING_PORTS
    return name if in_ports and name in use_cases else ""


def check(package_map: PackageMap, project_root: Path) -> list[Finding]:
    """Check every module of the mapped package against the dependency rules.

    Returns:
        Every finding, sorted by key.

    """
    modules = _modules(package_map, project_root)
    known = frozenset(m.name for m in modules)
    use_cases = _use_case_names(package_map, modules)
    findings: set[Finding] = set()
    for module in modules:
        part = package_map.part_of(module.name)
        region = package_map.parts[part] if part else None
        findings.update(_base_findings(package_map, module, region))
        if region is None:
            if not (module.is_package and package_map.is_container(module.name)):
                key = package_map.unmapped_key(module.name)
                findings.add(Finding(rule=Rule.UNMAPPED, subject=key))
            continue
        findings.update(_import_findings(package_map, module, region, known))
        if region is Region.HANDLERS:
            findings.update(_handler_findings(package_map, module, use_cases))
    return sorted(findings, key=lambda f: f.key)


def compare(findings: list[Finding], baseline: frozenset[str]) -> tuple[list[str], list[str]]:
    """Split findings against a shrink-only baseline.

    Returns:
        ``(new, repaired)``: keys found and not held, and keys held and no longer found.

    """
    found = {f.key for f in findings}
    return sorted(found - baseline), sorted(baseline - found)


def load_baseline(path: Path) -> frozenset[str]:
    """Read a baseline file: a JSON object whose ``findings`` list holds finding keys.

    Returns:
        The held keys.

    """
    return frozenset(json.loads(path.read_text(encoding="utf-8")).get("findings", []))
