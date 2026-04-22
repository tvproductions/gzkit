"""gzkit.justify — pre-execution reasoning walkthrough library substrate.

This package provides the evidence-gathering substrate for ``gz justify``:
Pydantic data models, anchor resolvers (GHI/OBPI/draft), and a concurrent
five-source grounding gather. The CLI surface, templates, and rendering
live in downstream OBPIs under ADR-0.0.19.

Public API is limited to the names in ``__all__``. Internal models
(``RuleCitation``, ``CommitRef``, ``LedgerEvent``) are importable from
``gzkit.justify.models`` but are not re-exported here.
"""

from gzkit.justify.anchors import resolve_anchor
from gzkit.justify.evidence import gather_evidence
from gzkit.justify.models import (
    AnchorKind,
    AnchorRef,
    AnchorResolutionError,
    EvidenceBundle,
)

__all__ = [
    "AnchorKind",
    "AnchorRef",
    "AnchorResolutionError",
    "EvidenceBundle",
    "gather_evidence",
    "resolve_anchor",
]
