"""gzkit.justify — pre-execution reasoning walkthrough library + renderer.

This package delivers the substrate and rendering layer for ``gz justify``:
Pydantic data models, GHI/OBPI/draft anchor resolvers, concurrent five-source
evidence gathering, an 8-section ``Walkthrough`` Pydantic model, and a
deterministic Jinja2-backed markdown renderer. The CLI subcommand lives in
``gzkit.commands.justify_cmd`` and dispatches through ``gzkit.justify.cli``.

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
from gzkit.justify.parser import (
    ValidateResult,
    WalkthroughParseError,
    parse_walkthrough,
)
from gzkit.justify.walkthrough import (
    Walkthrough,
    WalkthroughSection,
    render_scaffold,
)

__all__ = [
    "AnchorKind",
    "AnchorRef",
    "AnchorResolutionError",
    "EvidenceBundle",
    "ValidateResult",
    "Walkthrough",
    "WalkthroughParseError",
    "WalkthroughSection",
    "gather_evidence",
    "parse_walkthrough",
    "render_scaffold",
    "resolve_anchor",
]
