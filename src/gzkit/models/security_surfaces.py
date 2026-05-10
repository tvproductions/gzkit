"""SecuritySurfaceEntry — Pydantic model for the security-surface registry.

The registry (``data/security_surfaces.json``) declares which file globs map to
which security-sensitive category. ``gz validate --sensitivity`` (OBPI-0.0.22-03)
intersects each brief's ``## ALLOWED PATHS`` against the registry; any
intersection forces ``sensitivity: security`` regardless of frontmatter.

This module exposes:
- ``CANONICAL_CATEGORIES`` — the nine category names canonized in ADR-0.0.22.
- ``SecuritySurfaceEntry`` — frozen Pydantic model for one registry row.
- ``load_registry`` — read + parse the on-disk registry.
- ``match_globs`` — return the categories whose globs intersect a glob list.
"""

from __future__ import annotations

import glob as _glob
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

CANONICAL_CATEGORIES: tuple[str, ...] = (
    "credential_handling",
    "subprocess_user_input",
    "crypto_primitives",
    "auth_boundaries",
    "external_api_surfaces",
    "ledger_integrity",
    "arb_receipt_chain",
    "secret_handling",
    "deserialization_user_input",
)


SecurityCategory = Literal[
    "credential_handling",
    "subprocess_user_input",
    "crypto_primitives",
    "auth_boundaries",
    "external_api_surfaces",
    "ledger_integrity",
    "arb_receipt_chain",
    "secret_handling",
    "deserialization_user_input",
]


class SecuritySurfaceEntry(BaseModel):
    """One row in the security-surface registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: SecurityCategory = Field(..., description="Canonical security-sensitivity category.")
    globs: tuple[str, ...] = Field(
        ..., min_length=1, description="Glob patterns that match files in this category."
    )
    rationale: str = Field(..., min_length=1, description="Why this surface is security-sensitive.")

    def model_post_init(self, _context: object) -> None:
        """Reject empty glob entries after model construction."""
        for glob in self.globs:
            if not glob:
                msg = "globs entries must be non-empty strings"
                raise ValueError(msg)


_REGISTRY_ADAPTER = TypeAdapter(tuple[SecuritySurfaceEntry, ...])


def load_registry(path: Path) -> tuple[SecuritySurfaceEntry, ...]:
    """Load the registry from ``path`` and return frozen entry tuple."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _REGISTRY_ADAPTER.validate_python(raw)


def match_globs(
    candidate_globs: Sequence[str],
    registry: Sequence[SecuritySurfaceEntry],
) -> tuple[str, ...]:
    """Return the unique category labels whose globs intersect ``candidate_globs``.

    Two globs "intersect" when one matches the other as a representative path,
    using ``glob.translate(recursive=True)`` so ``**`` matches across directory
    separators correctly. The returned tuple preserves the registry's ordering.
    """
    matched: list[str] = []
    seen: set[str] = set()
    for entry in registry:
        if entry.category in seen:
            continue
        if _entry_intersects(entry.globs, candidate_globs):
            matched.append(entry.category)
            seen.add(entry.category)
    return tuple(matched)


def _entry_intersects(
    registry_globs: Sequence[str],
    candidate_globs: Sequence[str],
) -> bool:
    registry_regexes = [_compile(g) for g in registry_globs]
    candidate_regexes = [_compile(g) for g in candidate_globs]
    for registry_glob, registry_re in zip(registry_globs, registry_regexes, strict=True):
        for candidate_glob, candidate_re in zip(candidate_globs, candidate_regexes, strict=True):
            if registry_re.fullmatch(candidate_glob):
                return True
            if candidate_re.fullmatch(registry_glob):
                return True
    return False


def _compile(pattern: str) -> re.Pattern[str]:
    return re.compile(_glob.translate(pattern, recursive=True, include_hidden=True))


__all__ = [
    "CANONICAL_CATEGORIES",
    "SecurityCategory",
    "SecuritySurfaceEntry",
    "load_registry",
    "match_globs",
]
