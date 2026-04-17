"""@covers decorator, linkage registry, and coverage anchor scanner.

Provides the ``@covers("REQ-X.Y.Z-NN-MM")`` decorator (OBPI-01) and the
canonical scanner used by every coverage-aware command (gz drift, gz covers,
gz adr audit-check). Both decorator-call and docstring/comment forms of
``@covers`` are detected by a single regex utility (see #120).
"""

from __future__ import annotations

import ast
import logging
import pathlib
import re
import types
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

from gzkit.triangle import (
    DiscoveredReq,
    EdgeType,
    LinkageRecord,
    ReqId,
    ReqKind,
    VertexRef,
    VertexType,
    scan_briefs,
)

logger = logging.getLogger(__name__)

_F = TypeVar("_F")

_TESTABLE_KIND = ReqKind.CODE

# Canonical @covers reference regex used by every scanner.
# Catches three forms in a single pattern:
#   @covers("REQ-X.Y.Z-NN-MM")    decorator with double quotes
#   @covers('REQ-X.Y.Z-NN-MM')    decorator with single quotes
#   @covers REQ-X.Y.Z-NN-MM       docstring or comment
# The optional group ``(?:\(\s*['"])?`` handles the decorator-call wrapper;
# the leading ``\s*`` handles the whitespace-separated docstring form.
_COVERS_REF_PATTERN = re.compile(r"@covers\s*(?:\(\s*['\"])?(REQ-\d+\.\d+\.\d+-\d+-\d+)")


def find_covers_in_source(content: str) -> list[tuple[str, int]]:
    """Return ``(req_id, line_number)`` for every ``@covers`` reference in source.

    The single canonical scanner used by gz drift, gz covers, and gz adr
    audit-check. Handles both decorator-call and docstring/comment forms so
    every coverage-aware command sees the same set of references (see #120).
    Line numbers are 1-indexed.
    """
    hits: list[tuple[str, int]] = []
    for match in _COVERS_REF_PATTERN.finditer(content):
        req_id = match.group(1)
        line_num = content[: match.start()].count("\n") + 1
        hits.append((req_id, line_num))
    return hits


# ---------------------------------------------------------------------------
# Global linkage registry
# ---------------------------------------------------------------------------

_LINKAGE_REGISTRY: list[LinkageRecord] = []
_KNOWN_REQS: frozenset[str] | None = None


# ---------------------------------------------------------------------------
# REQ discovery (cached, loaded once per process)
# ---------------------------------------------------------------------------


def _find_project_root() -> pathlib.Path | None:
    """Walk up from CWD to find the project root (directory containing .gzkit/)."""
    current = pathlib.Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".gzkit").is_dir():
            return parent
    return None


def _load_known_reqs() -> frozenset[str]:
    """Scan briefs and cache the set of known REQ identifiers."""
    global _KNOWN_REQS
    if _KNOWN_REQS is not None:
        return _KNOWN_REQS

    root = _find_project_root()
    if root is None:
        _KNOWN_REQS = frozenset()
        return _KNOWN_REQS

    adr_dir = root / "docs" / "design" / "adr"
    if not adr_dir.is_dir():
        _KNOWN_REQS = frozenset()
        return _KNOWN_REQS

    discovered = scan_briefs(adr_dir)
    _KNOWN_REQS = frozenset(str(d.entity.id) for d in discovered)
    return _KNOWN_REQS


# ---------------------------------------------------------------------------
# @covers decorator
# ---------------------------------------------------------------------------


def _qualified_name(fn: object) -> str:
    """Return the fully qualified name of a function or method."""
    module = getattr(fn, "__module__", None) or "<unknown>"
    qualname = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", "<unknown>")
    return f"{module}.{qualname}"


def covers(req_id_str: str) -> Callable[[_F], _F]:
    """Declare that a test function covers a governance requirement.

    Validates the REQ identifier format and existence at decoration time,
    then registers a LinkageRecord mapping the test function to the REQ.

    The decorated function's behavior is unchanged -- @covers is metadata-only.

    Raises:
        ValueError: If *req_id_str* has an invalid format or does not exist
            in the extracted brief-defined REQ set.

    """
    req_id = ReqId.parse(req_id_str)

    known = _load_known_reqs()
    if str(req_id) not in known:
        msg = f"Unknown REQ identifier: {req_id_str!r} not found in extracted briefs"
        raise ValueError(msg)

    def decorator(fn: _F) -> _F:
        source_file: str | None = None
        source_line: int | None = None
        code = getattr(fn, "__code__", None)
        if isinstance(code, types.CodeType):
            source_file = code.co_filename
            source_line = code.co_firstlineno

        record = LinkageRecord(
            source=VertexRef(
                vertex_type=VertexType.TEST,
                identifier=_qualified_name(fn),
                location=source_file,
                line=source_line,
            ),
            target=VertexRef(
                vertex_type=VertexType.SPEC,
                identifier=str(req_id),
            ),
            edge_type=EdgeType.COVERS,
        )
        _LINKAGE_REGISTRY.append(record)
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Registry access (for scanner and testing)
# ---------------------------------------------------------------------------


def get_registry() -> list[LinkageRecord]:
    """Return a copy of the global linkage registry."""
    return list(_LINKAGE_REGISTRY)


def set_known_reqs(reqs: frozenset[str]) -> None:
    """Inject known REQ identifiers for testing."""
    global _KNOWN_REQS
    _KNOWN_REQS = reqs


def reset_registry() -> None:
    """Clear the linkage registry and cached known REQs. For testing only."""
    global _KNOWN_REQS
    _LINKAGE_REGISTRY.clear()
    _KNOWN_REQS = None


# ---------------------------------------------------------------------------
# Coverage anchor scanner (OBPI-02)
# ---------------------------------------------------------------------------


def _iter_test_functions(
    tree: ast.Module,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield module-level and class-level function defs, skipping nested inner functions."""
    funcs: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for top_node in ast.iter_child_nodes(tree):
        if isinstance(top_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(top_node)
        elif isinstance(top_node, ast.ClassDef):
            for child in ast.iter_child_nodes(top_node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append(child)
    return funcs


def scan_test_tree(test_dir: pathlib.Path) -> list[LinkageRecord]:
    """Walk a test directory and discover every @covers annotation.

    Parses each ``.py`` file statically — no test files are imported or
    executed. Decorator-form ``@covers("REQ-...")`` annotations are extracted
    via AST so each linkage carries the qualified function name. Docstring
    and comment-form references (``@covers REQ-...``) are then picked up via
    the canonical regex scanner so audit-check, drift, and gz covers all see
    the same set (see #120). Returns deterministic results sorted by
    (file path, line number).
    """
    records: list[LinkageRecord] = []

    for py_file in sorted(test_dir.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            logger.warning("Skipping unparseable file: %s", py_file)
            continue

        decorator_lines: set[int] = set()
        for node in _iter_test_functions(tree):
            for deco in node.decorator_list:
                req_str = _extract_covers_arg(deco)
                if req_str is None:
                    continue

                try:
                    req_id = ReqId.parse(req_str)
                except ValueError:
                    logger.warning(
                        "Malformed REQ in @covers at %s:%d — %s",
                        py_file,
                        deco.lineno,
                        req_str,
                    )
                    continue

                func_name = _ast_qualified_name(node, tree)
                decorator_lines.add(deco.lineno)
                records.append(
                    LinkageRecord(
                        source=VertexRef(
                            vertex_type=VertexType.TEST,
                            identifier=func_name,
                            location=str(py_file),
                            line=node.lineno,
                        ),
                        target=VertexRef(
                            vertex_type=VertexType.SPEC,
                            identifier=str(req_id),
                        ),
                        edge_type=EdgeType.COVERS,
                        evidence_path=str(py_file),
                        evidence_line=deco.lineno,
                    )
                )

        # Pick up docstring/comment-form @covers that AST cannot see.
        for req_str, line_num in find_covers_in_source(source):
            if line_num in decorator_lines:
                continue
            try:
                req_id = ReqId.parse(req_str)
            except ValueError:
                logger.warning(
                    "Malformed REQ in @covers at %s:%d — %s",
                    py_file,
                    line_num,
                    req_str,
                )
                continue
            records.append(
                LinkageRecord(
                    source=VertexRef(
                        vertex_type=VertexType.TEST,
                        identifier=str(py_file),
                        location=str(py_file),
                        line=line_num,
                    ),
                    target=VertexRef(
                        vertex_type=VertexType.SPEC,
                        identifier=str(req_id),
                    ),
                    edge_type=EdgeType.COVERS,
                    evidence_path=str(py_file),
                    evidence_line=line_num,
                )
            )

    records.sort(key=lambda r: (r.evidence_path or "", r.evidence_line or 0))
    return records


_REQ_TAG_PATTERN = re.compile(r"@(REQ-\d+\.\d+\.\d+-\d+-\d+)")
_SCENARIO_HEADER_PATTERN = re.compile(r"^\s*(?:Scenario(?: Outline)?|Example):\s*(?P<name>.+?)\s*$")
_FEATURE_HEADER_PATTERN = re.compile(r"^\s*Feature:\s*(?P<name>.+?)\s*$")


def scan_feature_tree(features_dir: pathlib.Path) -> list[LinkageRecord]:
    """Walk a behave features directory and discover every ``@REQ-...`` scenario tag.

    For each ``@REQ-X.Y.Z-NN-MM`` tag that precedes a ``Scenario:`` or
    ``Feature:`` header, emits a ``LinkageRecord`` with ``source.identifier``
    set to ``<FeatureName>::<ScenarioName>`` (or ``<FeatureName>`` for
    feature-level tags). This gives ``gz covers`` the same REQ-to-behave
    coverage graph it already has for unit tests, closing the remaining gap
    in GHI #185.
    """
    records: list[LinkageRecord] = []
    if not features_dir.is_dir():
        return records

    for feature_file in sorted(features_dir.rglob("*.feature")):
        try:
            source = feature_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            logger.warning("Skipping unreadable feature file: %s", feature_file)
            continue
        records.extend(_scan_feature_source(feature_file, source))

    records.sort(key=lambda r: (r.evidence_path or "", r.evidence_line or 0))
    return records


def _scan_feature_source(feature_path: pathlib.Path, source: str) -> list[LinkageRecord]:
    """Parse one .feature file and emit linkage records for every @REQ-... tag."""
    records: list[LinkageRecord] = []
    lines = source.splitlines()
    feature_name = _extract_feature_name(lines)

    # Pending tags accumulate on consecutive tag-only lines until a header consumes them.
    pending: list[tuple[str, int]] = []  # (req_id, line_num)

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Collect @REQ tags on this line.
        new_tags = [(m.group(1), idx) for m in _REQ_TAG_PATTERN.finditer(stripped)]

        # If the line is ONLY tags (plus leading/trailing whitespace/@... tokens),
        # it is a tag line attached to the next header. Accumulate and continue.
        if new_tags and _is_tag_only_line(stripped):
            pending.extend(new_tags)
            continue

        scenario_match = _SCENARIO_HEADER_PATTERN.match(line)
        feature_match = _FEATURE_HEADER_PATTERN.match(line)

        if scenario_match:
            scenario_name = scenario_match.group("name")
            identifier = f"{feature_name}::{scenario_name}" if feature_name else scenario_name
            _emit_pending_records(records, pending, feature_path, identifier)
            pending = []
            # A @REQ tag written inline on the same scenario line also counts.
            for req_str, line_num in new_tags:
                _append_feature_record(records, req_str, feature_path, identifier, line_num)
        elif feature_match:
            # Feature-level tags (above the Feature: keyword) attach to the feature.
            identifier = feature_match.group("name")
            feature_name = identifier
            _emit_pending_records(records, pending, feature_path, identifier)
            pending = []

    return records


def _is_tag_only_line(stripped: str) -> bool:
    """True if the line contains only ``@...`` tokens (whitespace-separated)."""
    tokens = stripped.split()
    return all(token.startswith("@") for token in tokens)


def _extract_feature_name(lines: list[str]) -> str | None:
    for line in lines:
        match = _FEATURE_HEADER_PATTERN.match(line)
        if match:
            return match.group("name")
    return None


def _emit_pending_records(
    records: list[LinkageRecord],
    pending: list[tuple[str, int]],
    feature_path: pathlib.Path,
    identifier: str,
) -> None:
    for req_str, line_num in pending:
        _append_feature_record(records, req_str, feature_path, identifier, line_num)


def _append_feature_record(
    records: list[LinkageRecord],
    req_str: str,
    feature_path: pathlib.Path,
    identifier: str,
    line_num: int,
) -> None:
    try:
        req_id = ReqId.parse(req_str)
    except ValueError:
        logger.warning("Malformed @REQ tag at %s:%d — %s", feature_path, line_num, req_str)
        return
    records.append(
        LinkageRecord(
            source=VertexRef(
                vertex_type=VertexType.TEST,
                identifier=identifier,
                location=str(feature_path),
                line=line_num,
            ),
            target=VertexRef(
                vertex_type=VertexType.SPEC,
                identifier=str(req_id),
            ),
            edge_type=EdgeType.COVERS,
            evidence_path=str(feature_path),
            evidence_line=line_num,
        )
    )


def _extract_covers_arg(node: ast.expr) -> str | None:
    """Extract the string argument from a ``@covers("...")`` decorator node."""
    if not isinstance(node, ast.Call):
        return None

    func = node.func
    is_covers = False
    if (
        isinstance(func, ast.Name)
        and func.id == "covers"
        or isinstance(func, ast.Attribute)
        and func.attr == "covers"
    ):
        is_covers = True

    if not is_covers:
        return None

    if len(node.args) != 1:
        return None

    arg = node.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value

    return None


def _ast_qualified_name(func_node: ast.FunctionDef | ast.AsyncFunctionDef, tree: ast.Module) -> str:
    """Build a dotted qualified name for a function from its AST context."""
    for cls_node in ast.walk(tree):
        if not isinstance(cls_node, ast.ClassDef):
            continue
        for item in cls_node.body:
            if item is func_node:
                return f"{cls_node.name}.{func_node.name}"
    return func_node.name


# ---------------------------------------------------------------------------
# Coverage models (OBPI-02)
# ---------------------------------------------------------------------------


class CoverageEntry(BaseModel):
    """Coverage status for a single REQ."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., description="REQ identifier")
    covered: bool = Field(..., description="Whether any test covers this REQ")
    covering_tests: list[str] = Field(
        default_factory=list, description="Qualified names of tests covering this REQ"
    )


class CoverageRollup(BaseModel):
    """Coverage statistics at a given granularity level."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    identifier: str = Field(..., description="ADR-X.Y.Z, OBPI-X.Y.Z-NN, or 'all'")
    total_reqs: int = Field(..., description="Total REQs at this level")
    covered_reqs: int = Field(..., description="REQs with at least one @covers")
    uncovered_reqs: int = Field(..., description="REQs with no @covers")
    coverage_percent: float = Field(..., description="Covered / total * 100")


class CoverageReport(BaseModel):
    """Full coverage report with multi-level rollups."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    by_adr: list[CoverageRollup] = Field(..., description="Per-ADR rollup")
    by_obpi: list[CoverageRollup] = Field(..., description="Per-OBPI rollup")
    entries: list[CoverageEntry] = Field(..., description="Per-REQ coverage entries")
    summary: CoverageRollup = Field(..., description="Overall summary")


# ---------------------------------------------------------------------------
# Coverage computation (OBPI-02)
# ---------------------------------------------------------------------------


def _semver_sort_key(semver: str) -> tuple[int, ...]:
    """Sort key for semantic version strings."""
    try:
        return tuple(int(p) for p in semver.split("."))
    except ValueError:
        return (999, 999, 999)


def compute_coverage(
    known_reqs: list[DiscoveredReq],
    linkage_records: list[LinkageRecord],
    include_doc: bool = False,
) -> CoverageReport:
    """Compute coverage rollup from known REQs and observed linkage records.

    Pure computation — no I/O. Deterministic: same inputs always produce same
    outputs. Results sorted by identifier (semantic version ordering).

    By default, doc-kind REQs (tagged ``[doc]`` in briefs) are excluded —
    tests are for code, and a doc-only ADR has no test surface. Set
    ``include_doc=True`` to surface doc-kind REQs in the report (useful for
    inspecting governance graph completeness rather than test coverage).
    """
    # Filter to testable REQs only — doc REQs have no test surface unless requested
    if include_doc:
        testable_reqs = list(known_reqs)
    else:
        testable_reqs = [r for r in known_reqs if r.entity.kind == _TESTABLE_KIND]

    # Build map: REQ ID → list of covering test identifiers
    coverage_map: dict[str, list[str]] = {}
    for record in linkage_records:
        if record.edge_type == EdgeType.COVERS:
            target_id = record.target.identifier
            coverage_map.setdefault(target_id, []).append(record.source.identifier)

    # Build per-REQ entries
    entries: list[CoverageEntry] = []
    for dreq in testable_reqs:
        req_str = str(dreq.entity.id)
        tests = sorted(set(coverage_map.get(req_str, [])))
        entries.append(CoverageEntry(req_id=req_str, covered=len(tests) > 0, covering_tests=tests))

    entries.sort(key=lambda e: _req_sort_tuple(e.req_id))

    # Group by OBPI
    obpi_groups: dict[str, list[CoverageEntry]] = {}
    for entry in entries:
        parsed = ReqId.parse(entry.req_id)
        obpi_key = f"OBPI-{parsed.semver}-{parsed.obpi_item}"
        obpi_groups.setdefault(obpi_key, []).append(entry)

    by_obpi = [
        _rollup(key, group)
        for key, group in sorted(obpi_groups.items(), key=lambda kv: _obpi_sort_key(kv[0]))
    ]

    # Group by ADR
    adr_groups: dict[str, list[CoverageEntry]] = {}
    for entry in entries:
        parsed = ReqId.parse(entry.req_id)
        adr_key = f"ADR-{parsed.semver}"
        adr_groups.setdefault(adr_key, []).append(entry)

    by_adr = [
        _rollup(key, group)
        for key, group in sorted(
            adr_groups.items(), key=lambda kv: _semver_sort_key(kv[0].removeprefix("ADR-"))
        )
    ]

    # Summary
    summary = _rollup("all", entries)

    return CoverageReport(by_adr=by_adr, by_obpi=by_obpi, entries=entries, summary=summary)


def _rollup(identifier: str, entries: list[CoverageEntry]) -> CoverageRollup:
    """Compute a CoverageRollup from a group of CoverageEntry objects."""
    total = len(entries)
    covered = sum(1 for e in entries if e.covered)
    return CoverageRollup(
        identifier=identifier,
        total_reqs=total,
        covered_reqs=covered,
        uncovered_reqs=total - covered,
        coverage_percent=round(covered / total * 100, 1) if total > 0 else 0.0,
    )


def _req_sort_tuple(req_id_str: str) -> tuple[tuple[int, ...], int, int]:
    """Sort key for REQ ID strings."""
    try:
        parsed = ReqId.parse(req_id_str)
        return (_semver_sort_key(parsed.semver), int(parsed.obpi_item), int(parsed.criterion_index))
    except ValueError:
        return ((999, 999, 999), 999, 999)


def _obpi_sort_key(obpi_key: str) -> tuple[tuple[int, ...], int]:
    """Sort key for OBPI identifiers like 'OBPI-0.15.0-03'."""
    parts = obpi_key.removeprefix("OBPI-")
    segments = parts.rsplit("-", 1)
    if len(segments) == 2:
        return (_semver_sort_key(segments[0]), int(segments[1]))
    return ((999, 999, 999), 999)
