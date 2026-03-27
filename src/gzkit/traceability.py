"""@covers decorator and linkage registry for test-to-spec traceability.

Provides the ``@covers("REQ-X.Y.Z-NN-MM")`` decorator that test functions use
to declare which governance requirement they prove. The decorator validates the
REQ identifier format, checks that the REQ exists in extracted briefs, and
registers a LinkageRecord in a global registry for scanner consumption.
"""

from __future__ import annotations

import pathlib
import types
from collections.abc import Callable
from typing import TypeVar

from gzkit.triangle import (
    EdgeType,
    LinkageRecord,
    ReqId,
    VertexRef,
    VertexType,
    scan_briefs,
)

_F = TypeVar("_F")

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
