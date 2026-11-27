"""FoundationGrandfatherManifest — frozen identity-only entry model (ADR-0.34.0).

Backs the closed ``kind: foundation`` grandfather manifest.

``data/foundation_grandfather.json`` is the committed closed membership set
for ADR ``kind: foundation``. Each entry is IDENTITY-ONLY — ``id``, ``title``,
``semver``, ``frozen_at`` — and carries no Layer-2 lifecycle fact. Lifecycle is
read live from the ledger; baking it into this committed Layer-1 file would be
the exact state-doctrine drift the ADR-0.0.37 frontmatter-lie demonstrated
(parent ADR § Decision, Alternative 3 REJECTED).

The foundation kind is closed in every project, adopters included (GHI #1402;
operator, 2026-11-27: *"They must not persist and we must not permit adopters to
use them"*). The manifest names the only foundation ADRs any project may hold:
gzkit's frozen legacy roster. A project without it holds none.

This module exposes:
- ``FoundationGrandfatherManifest`` — frozen per-entry model (``extra="forbid"``).
- ``load_manifest`` — read + parse the on-disk manifest into entry tuples.
"""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class FoundationGrandfatherManifest(BaseModel):
    """One identity-only row in the closed foundation grandfather manifest.

    Deliberately carries no ``lifecycle`` field: lifecycle is a Layer-2 fact
    read live from the ledger, never baked into this committed Layer-1 file.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Foundation ADR identifier, e.g. ADR-0.0.37.")
    title: str = Field(..., description="Foundation ADR title.")
    semver: str = Field(..., description="Foundation semver, e.g. 0.0.37.")
    frozen_at: str = Field(
        ..., description="ISO date the entry was frozen into the grandfather manifest."
    )


_MANIFEST_ADAPTER = TypeAdapter(tuple[FoundationGrandfatherManifest, ...])


def load_manifest(path: Path) -> tuple[FoundationGrandfatherManifest, ...]:
    """Load the manifest from ``path`` and return a frozen entry tuple."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _MANIFEST_ADAPTER.validate_python(raw)


GRANDFATHER_MANIFEST_REL = Path("data") / "foundation_grandfather.json"


__all__ = [
    "GRANDFATHER_MANIFEST_REL",
    "FoundationGrandfatherManifest",
    "load_manifest",
]
