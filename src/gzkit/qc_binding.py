"""QC-step registry and classifier (ADR-0.0.73, OBPI-0.0.73-01).

The ``QCStep`` frozen Pydantic model records every quality-check step that
``gz check`` runs, classified as ``bound`` / ``advisory`` / ``unenforced``.

Registry membership is DERIVED at call time from ``_build_check_steps()``
in ``gzkit.commands.quality`` — it is never a hand-maintained list.  When
``_build_check_steps()`` gains a new step, ``build_qc_registry()`` raises
``KeyError`` pointing at the unclassified name, forcing the author to add an
entry to ``_STEP_CLASSIFICATION`` before the registry can be built.

Classification semantics:
  bound        — step exits non-zero on violation; ships a negative-control
                 fixture (OBPI-0.0.73-02 validates via negative controls)
  advisory     — step reports findings without gating ``gz check`` exit code
  unenforced   — step exists but cannot currently fail for the right reason
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class QCStep(BaseModel):
    """Immutable descriptor for one ``gz check`` quality-check step.

    Fields
    ------
    id               machine-stable slug (``lint``, ``format``, ...)
    name             human-readable label matching ``_build_check_steps()``
    kind             check category: lint | format | test | typecheck | bdd | audit
    subject          primary surface checked: ``src/``, ``tests/``, ``docs/``,
                     ``.gzkit/``, ``features/``, ``all``
    binding          enforcement claim: ``bound`` | ``advisory`` | ``unenforced``
    wired_into       commands this step runs inside (always ``["gz check"]`` for now)
    theater_flags    facade signatures detected by OBPI-0.0.73-02 (empty in OBPI-01)
    enforcement_locus where enforcement fires: ``subprocess`` | ``python_function``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="Machine-stable slug")
    name: str = Field(..., description="Human-readable label from _build_check_steps()")
    kind: str = Field(..., description="Check category")
    subject: str = Field(..., description="Primary surface checked")
    binding: str = Field(..., description="bound | advisory | unenforced")
    wired_into: list[str] = Field(..., description="Commands this step runs inside")
    theater_flags: list[str] = Field(..., description="Facade signatures detected by OBPI-02")
    enforcement_locus: str = Field(
        ..., description="Where enforcement fires: subprocess | python_function"
    )


# ---------------------------------------------------------------------------
# Classification metadata
# ---------------------------------------------------------------------------

# Tuple layout: (kind, subject, binding, enforcement_locus)
# One entry per step name in _build_check_steps(); KeyError = unclassified step.
_StepMeta = tuple[str, str, str, str]

_STEP_CLASSIFICATION: dict[str, _StepMeta] = {
    "Lint": ("lint", "src/", "bound", "subprocess"),
    "Format": ("format", "src/", "bound", "subprocess"),
    "Typecheck": ("typecheck", "src/", "bound", "subprocess"),
    "Test": ("test", "tests/", "bound", "subprocess"),
    "Behave": ("bdd", "features/", "bound", "subprocess"),
    "Skill audit": ("audit", ".gzkit/skills/", "bound", "python_function"),
    "Parity check": ("audit", "all", "bound", "python_function"),
    "Readiness audit": ("audit", "all", "bound", "python_function"),
    "CLI audit": ("audit", "docs/", "bound", "python_function"),
    "Unscoped rules": ("audit", ".gzkit/rules/", "bound", "python_function"),
    "ADR status freshness": ("audit", "docs/", "bound", "python_function"),
    "Rendition freshness": ("audit", "docs/", "bound", "python_function"),
    "Rendition floor coherence": ("audit", "docs/", "bound", "python_function"),
    "Session green gate": ("audit", ".gzkit/", "bound", "python_function"),
    "Closeout proof": ("audit", "docs/", "bound", "python_function"),
    "Kind invariance": ("audit", "docs/", "bound", "python_function"),
    "Interview transcripts": ("audit", "docs/", "bound", "python_function"),
    "Receipt shape": ("audit", ".gzkit/", "bound", "python_function"),
    "Orientation freshness": ("audit", ".gzkit/", "bound", "python_function"),
    "Insights shape": ("audit", ".gzkit/", "bound", "python_function"),
    "Instructions files budget": ("audit", "docs/", "bound", "python_function"),
    "AGENTS.md map conformance": ("audit", "docs/", "bound", "python_function"),
    "Complexity-doctrine links": ("audit", "docs/", "bound", "python_function"),
    "Complexity-thresholds": ("audit", "docs/", "bound", "python_function"),
    "REQ kind discipline": ("audit", "docs/", "bound", "python_function"),
    "tautological test audit": ("audit", "tests/", "bound", "python_function"),
    "Task envelope coherence": ("audit", "docs/", "bound", "python_function"),
    "Lock-handoff coupling": ("audit", ".gzkit/", "bound", "python_function"),
    "QC binding": ("audit", "src/", "bound", "python_function"),
    "Handoff documents": ("audit", "docs/", "bound", "python_function"),
    "Preflight": ("audit", ".gzkit/", "bound", "python_function"),
    "Surface fidelity": ("audit", "docs/", "bound", "python_function"),
    "Line endings": ("audit", "all", "bound", "python_function"),
    "Dispatch attestation": ("audit", "docs/", "bound", "python_function"),
}


def _name_to_id(name: str) -> str:
    """Convert a step name to a machine-stable slug."""
    return name.lower().replace(" ", "-").replace(".", "-")


# ---------------------------------------------------------------------------
# Registry builder
# ---------------------------------------------------------------------------


def build_qc_registry() -> list[QCStep]:
    """Build the QC-step registry derived from what ``gz check`` actually runs.

    Imports ``_build_check_steps`` lazily to avoid circular imports at module
    load time.  Raises ``KeyError`` when a step name in ``_build_check_steps()``
    has no entry in ``_STEP_CLASSIFICATION`` — the sentinel that forces authors
    to classify new steps when they add them to ``gz check``.
    """
    from gzkit.commands.quality import _build_check_steps  # noqa: PLC0415

    registry: list[QCStep] = []
    for name, _ in _build_check_steps():
        if name not in _STEP_CLASSIFICATION:
            msg = (
                f"QC step {name!r} has no classification entry in "
                f"gzkit.qc_binding._STEP_CLASSIFICATION. "
                f"Add an entry before using build_qc_registry()."
            )
            raise KeyError(msg)
        kind, subject, binding, enforcement_locus = _STEP_CLASSIFICATION[name]
        registry.append(
            QCStep(
                id=_name_to_id(name),
                name=name,
                kind=kind,
                subject=subject,
                binding=binding,
                wired_into=["gz check"],
                theater_flags=[],
                enforcement_locus=enforcement_locus,
            )
        )
    return registry
