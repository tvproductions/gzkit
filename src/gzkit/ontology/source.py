"""Source-domain sensor for the gzkit ontology (ADR-0.32.0, OBPI-0.32.0-07).

Images the SOURCE subgraph: product-code ``@covers``/``@surface`` anchors lifted
into first-class source→REQ edges, code-coupling edges (import + definition
relationships between source units), a regenerable Tier-B ``source_anchors.json``
query-before-grep index, and orphan-gap detection over every REQ. It absorbs
``triangle.py``'s edge model by projecting its ``LinkageRecord``s into typed
``OntologyEdge``s; ``triangle.detect_drift`` is re-expressed as a subgraph VIEW
in place (its public surface preserved unchanged).

Parent ADR § Decision (source-domain clause, verbatim): "source (tree-sitter
code-coupling + @covers/@surface anchors; source->REQ first-class; absorbs
triangle.py's edge model and re-expresses detect_drift as a subgraph view)".

Hexagonal seam (``.claude/rules/hexagonal-architecture.md``): source parsing is a
``SourceParser`` PORT (a ``typing.Protocol`` returning domain types) fulfilled by
TWO real adapters — ``AstSourceParser`` (stdlib ``ast``, Python-only, the
STDLIB-FIRST default) and ``TreeSitterSourceParser`` (the attested polyglot
departure). The core depends on the port by injection; either adapter fulfils it.
tree-sitter is imported function-locally, confined to its adapter, so the module
and the ``ast`` adapter are exercisable without importing tree-sitter (rule 6);
no library-native node crosses the port (rule 3).

STDLIB-FIRST departure (parent ADR § Decision, GO-attested Phase-0 airlock-in,
2026-07-02): tree-sitter supplies the deterministic multi-surface (polyglot)
parsing that stdlib ``ast`` (Python-only) cannot — gzkit is a harness that runs
on adopter codebases.
"""

from __future__ import annotations

import ast
import enum
import re
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from gzkit.ontology.model import LinkType, OntologyEdge, Provenance
from gzkit.triangle import EdgeType, LinkageRecord, ReqId, scan_briefs

# ---------------------------------------------------------------------------
# Domain models (stdlib + Pydantic only — no tree-sitter in the core)
# ---------------------------------------------------------------------------


class AnchorKind(enum.StrEnum):
    """Whether a source→REQ anchor is a strict ``@covers`` or a light ``@surface``."""

    COVERS = "covers"
    SURFACE = "surface"


class SourceAnchor(BaseModel):
    """A source→REQ anchor found in product source, with file:line provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_path: str = Field(..., description="POSIX source path where the anchor was found")
    line: int = Field(..., description="1-indexed line of the anchor")
    req_id: str = Field(..., description="Target REQ identifier")
    anchor_kind: AnchorKind = Field(..., description="covers (strict) or surface (light)")

    def to_edge(self) -> OntologyEdge:
        """Project this anchor into a typed source→REQ ``OntologyEdge``.

        A CODE-origin edge distinct from ``triangle.py``'s test→spec COVERS edges:
        ``@covers`` anchors become ``LinkType.COVERS``, ``@surface`` anchors the
        lighter ``LinkType.SURFACE``; both are ``Provenance.OBSERVED`` (extracted
        fact, not authored intent).
        """
        link_type = LinkType.COVERS if self.anchor_kind is AnchorKind.COVERS else LinkType.SURFACE
        return OntologyEdge(
            source_id=self.source_path,
            target_id=self.req_id,
            link_type=link_type,
            provenance=Provenance.OBSERVED,
        )


class CouplingRelation(enum.StrEnum):
    """The kind of code-coupling relationship a parser extracted."""

    IMPORTS = "imports"  # a unit imports a module (resolved to a unit when internal)
    USES_DEFINITION = "uses_definition"  # a unit imports a name DEFINED in the target unit


class CodeCouplingEdge(BaseModel):
    """A code-coupling edge, resolved between source units.

    ``target`` is the resolved target source-unit path when the imported module
    maps to a unit in the scanned tree (``target_is_unit=True``), otherwise the
    bare external module name. ``uses_definition`` edges additionally name the
    ``symbol`` — a name imported from the target unit that is genuinely DEFINED
    there (the definition side of the parse tree, not just imports).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_path: str = Field(..., description="POSIX path of the importing/using source unit")
    target: str = Field(..., description="Resolved target unit POSIX path, or external module name")
    relation: CouplingRelation = Field(
        ..., description="imports (module) or uses_definition (symbol)"
    )
    target_is_unit: bool = Field(
        ..., description="True when target resolves to a source unit in the scanned tree"
    )
    symbol: str | None = Field(
        None, description="For uses_definition: the imported symbol defined in the target unit"
    )


class SourceAnchorIndex(BaseModel):
    """The Tier-B query-before-grep index: every source→REQ anchor + coupling edges."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    anchors: tuple[SourceAnchor, ...] = Field(
        default=(), description="Every source→REQ anchor, deterministically sorted"
    )
    coupling_edges: tuple[CodeCouplingEdge, ...] = Field(
        default=(), description="Code-coupling edges, deterministically sorted"
    )
    parse_failures: tuple[str, ...] = Field(
        default=(),
        description="Sorted rel-paths of units the parser could not fully parse (BI#1)",
    )

    @property
    def edges(self) -> list[OntologyEdge]:
        """The source→REQ anchors expressed as typed ``OntologyEdge``s."""
        return [anchor.to_edge() for anchor in self.anchors]

    def anchors_for(self, req_id: str) -> list[SourceAnchor]:
        """Return every anchor targeting ``req_id`` (query, not grep)."""
        return [anchor for anchor in self.anchors if anchor.req_id == req_id]


class OrphanGapReport(BaseModel):
    """Deterministic orphan-gap report over the source subgraph."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    orphan_reqs: tuple[str, ...] = Field(
        default=(), description="Known brief REQs with no covering source anchor (sorted)"
    )
    unknown_anchor_reqs: tuple[str, ...] = Field(
        default=(), description="Anchor REQ ids that are not a known brief REQ (sorted)"
    )


# ---------------------------------------------------------------------------
# The source-parser PORT (hexagonal-architecture.md rule 5 — second adapter real)
# ---------------------------------------------------------------------------


class SourceParser(Protocol):
    """The structural-source-parse seam ``ast`` and tree-sitter both fulfil.

    Domain-typed contract (rule 3): methods accept source text and return domain
    ``SourceAnchor`` / ``CodeCouplingEdge`` models — never a parser-native node.
    Injected into the core; either adapter may be supplied.
    """

    def scan_anchors(self, unit_path: str, source: str) -> list[SourceAnchor]:
        """Extract ``@covers``/``@surface`` decorator anchors from one unit."""
        ...

    def coupling(self, files: list[tuple[str, str]]) -> list[CodeCouplingEdge]:
        """Build import + definition coupling edges across ``(path, source)`` pairs."""
        ...

    def parse_failures(self, files: list[tuple[str, str]]) -> tuple[str, ...]:
        """Return the sorted rel-paths of units this parser could not fully parse.

        A unit whose parse is incomplete silently drops its ``@covers``/``@surface``
        anchors, so naming it is the source domain's rebuild-fidelity confession
        (parent-ADR Boundary Invariant #1). Domain-typed (rule 3): rel-paths, never
        a parser-native node.
        """
        ...


_ANCHOR_DECORATORS: dict[str, AnchorKind] = {
    "covers": AnchorKind.COVERS,
    "surface": AnchorKind.SURFACE,
}
_REQ_ID_RE = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")


# ---------------------------------------------------------------------------
# Shared, parser-agnostic helpers (core)
# ---------------------------------------------------------------------------


def _req_sort_key(req_id: str) -> tuple[tuple[int, ...], int, int, str]:
    """Semver-aware sort key for a REQ id; unparseable ids sort last, stably."""
    try:
        parsed = ReqId.parse(req_id)
    except ValueError:
        return ((999, 999, 999), 999, 999, req_id)
    semver = tuple(int(p) for p in parsed.semver.split("."))
    return (semver, int(parsed.obpi_item), int(parsed.criterion_index), req_id)


def _sorted_anchors(anchors: list[SourceAnchor]) -> list[SourceAnchor]:
    """Deterministic anchor ordering: path, line, REQ, kind."""
    return sorted(
        anchors,
        key=lambda a: (a.source_path, a.line, _req_sort_key(a.req_id), a.anchor_kind.value),
    )


def _module_name_for(rel_path: str) -> str:
    """Map a POSIX source path to its importable dotted module name.

    ``b.py → b`` · ``d/e.py → d.e`` · ``pkg/__init__.py → pkg``.
    """
    stem = rel_path[:-3] if rel_path.endswith(".py") else rel_path
    if stem.endswith("/__init__"):
        stem = stem[: -len("/__init__")]
    return stem.replace("/", ".")


def _assemble_coupling_edges(
    files: list[tuple[str, str]],
    imports_by_unit: dict[str, list[tuple[str, tuple[str, ...]]]],
    defs_by_unit: dict[str, set[str]],
) -> list[CodeCouplingEdge]:
    """Assemble coupling edges from per-unit imports + definitions (parser-agnostic).

    Resolves each import to a source unit via the module map (edges BETWEEN source
    units), and emits a ``uses_definition`` edge when a ``from``-imported symbol is
    genuinely defined in the target unit. Deterministic sorted output.
    """
    module_map = {_module_name_for(rel): rel for rel, _ in files}
    edges: set[CodeCouplingEdge] = set()
    for rel_path, imports in imports_by_unit.items():
        for module, symbols in imports:
            target_unit = module_map.get(module)
            is_unit = target_unit is not None
            edges.add(
                CodeCouplingEdge(
                    source_path=rel_path,
                    target=target_unit if is_unit else module,
                    relation=CouplingRelation.IMPORTS,
                    target_is_unit=is_unit,
                )
            )
            if target_unit is not None:
                target_defs = defs_by_unit.get(target_unit, set())
                for symbol in symbols:
                    if symbol in target_defs:
                        edges.add(
                            CodeCouplingEdge(
                                source_path=rel_path,
                                target=target_unit,
                                relation=CouplingRelation.USES_DEFINITION,
                                target_is_unit=True,
                                symbol=symbol,
                            )
                        )
    return sorted(edges, key=lambda e: (e.source_path, e.target, e.relation.value, e.symbol or ""))


# ---------------------------------------------------------------------------
# Adapter 1 — stdlib ast (Python-only; the STDLIB-FIRST default)
# ---------------------------------------------------------------------------


class AstSourceParser:
    """Stdlib ``ast`` source parser — Python-only, the STDLIB-FIRST default adapter."""

    def scan_anchors(self, unit_path: str, source: str) -> list[SourceAnchor]:
        """Walk ``ast`` decorator lists for ``@covers``/``@surface`` anchors."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        anchors: list[SourceAnchor] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for deco in node.decorator_list:
                anchor = _ast_anchor_from_decorator(deco, unit_path)
                if anchor is not None:
                    anchors.append(anchor)
        return _sorted_anchors(anchors)

    def coupling(self, files: list[tuple[str, str]]) -> list[CodeCouplingEdge]:
        """Extract imports + definitions per unit via ``ast``, then assemble edges."""
        imports_by_unit: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
        defs_by_unit: dict[str, set[str]] = {}
        for rel, text in files:
            imports_by_unit[rel], defs_by_unit[rel] = _ast_imports_and_defs(text)
        return _assemble_coupling_edges(files, imports_by_unit, defs_by_unit)

    def parse_failures(self, files: list[tuple[str, str]]) -> tuple[str, ...]:
        """Rel-paths whose source is not valid Python (``ast.parse`` raises)."""
        failures: list[str] = []
        for rel, text in files:
            try:
                ast.parse(text)
            except SyntaxError:
                failures.append(rel)
        return tuple(sorted(failures))


def _ast_anchor_from_decorator(deco: ast.expr, unit_path: str) -> SourceAnchor | None:
    """Return a ``SourceAnchor`` for an ``@covers("REQ-...")`` / ``@surface(...)`` decorator."""
    if not isinstance(deco, ast.Call):
        return None
    func = deco.func
    name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
    kind = _ANCHOR_DECORATORS.get(name) if name is not None else None
    if kind is None or len(deco.args) != 1:
        return None
    arg = deco.args[0]
    if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
        return None
    if not _REQ_ID_RE.fullmatch(arg.value):
        return None
    return SourceAnchor(source_path=unit_path, line=deco.lineno, req_id=arg.value, anchor_kind=kind)


def _ast_imports_and_defs(text: str) -> tuple[list[tuple[str, tuple[str, ...]]], set[str]]:
    """Extract ``(module, symbols)`` imports and top-level definition names via ``ast``."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], set()
    imports: list[tuple[str, tuple[str, ...]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((alias.name, ()) for alias in node.names)
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and node.level == 0  # skip relative imports (flat module map can't resolve them)
            and node.module != "__future__"  # a compiler directive, not real coupling
        ):
            imports.append((node.module, tuple(alias.name for alias in node.names)))
    defs = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    return imports, defs


# ---------------------------------------------------------------------------
# Adapter 2 — tree-sitter (polyglot; the attested departure, function-local import)
# ---------------------------------------------------------------------------


class TreeSitterSourceParser:
    """Polyglot source parser — the attested tree-sitter departure adapter.

    The sole tree-sitter import site (function-local, so the module core and the
    ``ast`` adapter never touch tree-sitter — hexagonal rule 6). Returns domain
    models only; no tree-sitter node crosses the port (rule 3).
    """

    def scan_anchors(self, unit_path: str, source: str) -> list[SourceAnchor]:
        """Walk tree-sitter ``decorator`` nodes for ``@covers``/``@surface`` anchors."""
        source_bytes = source.encode("utf-8")
        root = _ts_parser().parse(source_bytes).root_node
        anchors: list[SourceAnchor] = []
        stack = [root]
        while stack:
            node = stack.pop()
            if node.type == "decorator":
                anchor = _ts_anchor_from_decorator(node, source_bytes, unit_path)
                if anchor is not None:
                    anchors.append(anchor)
            stack.extend(node.named_children)
        return _sorted_anchors(anchors)

    def coupling(self, files: list[tuple[str, str]]) -> list[CodeCouplingEdge]:
        """Extract imports + definitions per unit via tree-sitter, then assemble edges."""
        parser = _ts_parser()
        imports_by_unit: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
        defs_by_unit: dict[str, set[str]] = {}
        for rel, text in files:
            source_bytes = text.encode("utf-8")
            root = parser.parse(source_bytes).root_node
            imports_by_unit[rel] = _walk_imports(root, source_bytes)
            defs_by_unit[rel] = _walk_definitions(root, source_bytes)
        return _assemble_coupling_edges(files, imports_by_unit, defs_by_unit)

    def parse_failures(self, files: list[tuple[str, str]]) -> tuple[str, ...]:
        """Rel-paths whose tree-sitter parse tree contains ERROR/MISSING nodes."""
        parser = _ts_parser()
        failures = [
            rel for rel, text in files if parser.parse(text.encode("utf-8")).root_node.has_error
        ]
        return tuple(sorted(failures))


def _ts_parser() -> Any:
    """Construct a tree-sitter Python parser (the confined dependency site)."""
    import tree_sitter as ts  # noqa: PLC0415 — adapter-confined dependency
    import tree_sitter_python as tsp  # noqa: PLC0415

    return ts.Parser(ts.Language(tsp.language()))


def _first_child_of_type(node: Any, node_type: str) -> Any:
    """Return the first named child of ``node`` with ``node_type``, or None."""
    for child in node.named_children:
        if child.type == node_type:
            return child
    return None


def _ts_anchor_from_decorator(
    node: Any, source_bytes: bytes, unit_path: str
) -> SourceAnchor | None:
    """Return a ``SourceAnchor`` for a tree-sitter ``@covers(...)``/``@surface(...)`` decorator."""
    call = _first_child_of_type(node, "call")
    if call is None:
        return None
    func = call.child_by_field_name("function")
    if func is None or func.type != "identifier":
        return None
    kind = _ANCHOR_DECORATORS.get(_node_text(func, source_bytes))
    if kind is None:
        return None
    args = call.child_by_field_name("arguments")
    string_node = _first_child_of_type(args, "string") if args is not None else None
    if string_node is None:
        return None
    value = _ts_string_value(string_node, source_bytes)
    if not _REQ_ID_RE.fullmatch(value):
        return None
    return SourceAnchor(
        source_path=unit_path,
        line=node.start_point[0] + 1,
        req_id=value,
        anchor_kind=kind,
    )


def _ts_string_value(string_node: Any, source_bytes: bytes) -> str:
    """Return a tree-sitter string node's content, unwrapping the quotes."""
    content = _first_child_of_type(string_node, "string_content")
    if content is not None:
        return _node_text(content, source_bytes)
    return _node_text(string_node, source_bytes).strip("'\"")


def _walk_imports(node: Any, source_bytes: bytes) -> list[tuple[str, tuple[str, ...]]]:
    """Walk the parse tree, yielding ``(module, imported_symbols)`` per import."""
    results: list[tuple[str, tuple[str, ...]]] = []
    stack = [node]
    while stack:
        current = stack.pop()
        if current.type == "import_statement":
            for child in current.named_children:
                module = _import_module_name(child, source_bytes)
                if module is not None:
                    results.append((module, ()))
        elif current.type == "import_from_statement":
            module_node = current.child_by_field_name("module_name")
            # dotted_name = absolute import. relative_import (``from .x``) is skipped
            # for parity with the ast adapter (the flat module map can't resolve it);
            # ``from __future__`` is a distinct future_import_statement, never reaching here.
            if module_node is not None and module_node.type == "dotted_name":
                symbols = tuple(
                    _symbol_name(name_node, source_bytes)
                    for name_node in current.children_by_field_name("name")
                )
                results.append((_node_text(module_node, source_bytes), symbols))
        stack.extend(current.named_children)
    return results


def _walk_definitions(root: Any, source_bytes: bytes) -> set[str]:
    """Return the names of top-level ``def`` / ``class`` definitions in a unit.

    A *decorated* definition is wrapped by tree-sitter in a ``decorated_definition``
    node, so we unwrap it via the ``definition`` field — otherwise a ``@decorator``ed
    top-level function/class would be invisible (and disagree with the ``ast``
    adapter, which sees it as a plain ``FunctionDef``).
    """
    names: set[str] = set()
    for child in root.named_children:
        definition = child
        if child.type == "decorated_definition":
            definition = child.child_by_field_name("definition")
        if definition is not None and definition.type in (
            "function_definition",
            "class_definition",
        ):
            name_node = definition.child_by_field_name("name")
            if name_node is not None:
                names.add(_node_text(name_node, source_bytes))
    return names


def _import_module_name(child: Any, source_bytes: bytes) -> str | None:
    """Extract the dotted module name from an ``import a.b`` / ``import a as x`` child."""
    if child.type == "dotted_name":
        return _node_text(child, source_bytes)
    if child.type == "aliased_import":
        name = child.child_by_field_name("name")
        return _node_text(name, source_bytes) if name is not None else None
    return None


def _symbol_name(node: Any, source_bytes: bytes) -> str:
    """Extract an imported symbol name, unwrapping ``import x as y`` to ``x``."""
    if node.type == "aliased_import":
        name = node.child_by_field_name("name")
        if name is not None:
            return _node_text(name, source_bytes)
    return _node_text(node, source_bytes)


def _node_text(node: Any, source_bytes: bytes) -> str:
    """Decode a tree-sitter node's source span to text."""
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8")


# ---------------------------------------------------------------------------
# Index build / load / orphan-gaps (core — depends on the injected port)
# ---------------------------------------------------------------------------


def _find_project_root() -> Path | None:
    """Walk up from CWD to the directory containing ``.gzkit/``."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".gzkit").is_dir():
            return parent
    return None


def _default_source_root() -> Path:
    root = _find_project_root() or Path.cwd()
    return root / "src"


def _default_index_path() -> Path:
    root = _find_project_root() or Path.cwd()
    return root / ".gzkit" / "ontology" / "source_anchors.json"


def _iter_py_files(source_root: Path) -> list[Path]:
    """Deterministically ordered ``*.py`` files under ``source_root``."""
    return sorted(source_root.rglob("*.py"))


def _read_units(source_root: Path) -> list[tuple[str, str]]:
    """Read every ``*.py`` unit as ``(posix_rel_path, source_text)``."""
    return [
        (f.relative_to(source_root).as_posix(), f.read_text(encoding="utf-8"))
        for f in _iter_py_files(source_root)
    ]


def _scan_all_anchors(parser: SourceParser, files: list[tuple[str, str]]) -> list[SourceAnchor]:
    """Scan every unit's anchors through the injected parser."""
    anchors: list[SourceAnchor] = []
    for rel_path, text in files:
        anchors.extend(parser.scan_anchors(rel_path, text))
    return _sorted_anchors(anchors)


def build_source_anchor_index(
    source_root: Path | None = None,
    *,
    parser: SourceParser | None = None,
    index_path: Path | None = None,
    write: bool = True,
) -> SourceAnchorIndex:
    """Build the deterministic Tier-B ``source_anchors.json`` index (REQ-04).

    Parses source through the injected ``SourceParser`` port (defaulting to the
    polyglot tree-sitter adapter), assembling ``@covers``/``@surface`` anchors and
    code-coupling edges, deterministically sorted so identical source trees yield
    byte-identical JSON that round-trips through its model. Tier-B: regenerable,
    never authoritative (parent ADR Boundary Invariant #2).
    """
    root = Path(source_root) if source_root is not None else _default_source_root()
    parser = parser if parser is not None else TreeSitterSourceParser()
    files = _read_units(root)
    anchors = _scan_all_anchors(parser, files)
    coupling = parser.coupling(files)

    index = SourceAnchorIndex(
        anchors=tuple(anchors),
        coupling_edges=tuple(coupling),
        parse_failures=parser.parse_failures(files),
    )
    if write:
        out = Path(index_path) if index_path is not None else _default_index_path()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(index.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return index


def load_source_anchor_index(path: Path | None = None) -> SourceAnchorIndex:
    """Load the ``source_anchors.json`` index from disk (REQ-04)."""
    src = Path(path) if path is not None else _default_index_path()
    return SourceAnchorIndex.model_validate_json(src.read_text(encoding="utf-8"))


def _known_brief_reqs() -> set[str]:
    """Resolve the set of known brief REQ ids from the ADR tree."""
    root = _find_project_root()
    if root is None:
        return set()
    adr_dir = root / "docs" / "design" / "adr"
    if not adr_dir.is_dir():
        return set()
    return {str(d.entity.id) for d in scan_briefs(adr_dir)}


def detect_orphan_gaps(
    source_root: Path | None = None,
    *,
    parser: SourceParser | None = None,
    known_reqs: set[str] | None = None,
) -> OrphanGapReport:
    """Detect orphan gaps over the source subgraph (REQ-05).

    Symmetric: ``orphan_reqs`` are known brief REQs with no covering source
    anchor; ``unknown_anchor_reqs`` are anchor REQ ids that are not a known brief
    REQ. Both sorted deterministically. Anchors are scanned through the injected
    ``SourceParser`` port.
    """
    root = Path(source_root) if source_root is not None else _default_source_root()
    parser = parser if parser is not None else TreeSitterSourceParser()
    anchor_reqs = {a.req_id for a in _scan_all_anchors(parser, _read_units(root))}
    known = known_reqs if known_reqs is not None else _known_brief_reqs()

    orphans = sorted(known - anchor_reqs, key=_req_sort_key)
    unknown = sorted(anchor_reqs - known, key=_req_sort_key)
    return OrphanGapReport(orphan_reqs=tuple(orphans), unknown_anchor_reqs=tuple(unknown))


# ---------------------------------------------------------------------------
# triangle edge-model absorption (source→ontology projection)
# ---------------------------------------------------------------------------


def source_subgraph_edges(linkage_records: list[LinkageRecord]) -> list[OntologyEdge]:
    """Absorb ``triangle.py``'s edge model into typed ontology source→REQ edges (REQ-06).

    Projects the source→REQ COVERS layer of the triangle into ``LinkType.COVERS``
    ``OntologyEdge``s (``Provenance.OBSERVED``). Triangle's PROVES/JUSTIFIES edges
    are test↔code relations outside the source→REQ subgraph and have no ontology
    ``LinkType`` (the model is owned by OBPI-01, not editable here), so they are
    not projected — the source subgraph images the coverage layer only.
    """
    edges: list[OntologyEdge] = []
    for record in linkage_records:
        if record.edge_type == EdgeType.COVERS:
            edges.append(
                OntologyEdge(
                    source_id=record.source.identifier,
                    target_id=record.target.identifier,
                    link_type=LinkType.COVERS,
                    provenance=Provenance.OBSERVED,
                )
            )
    return edges
