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

#: Audit SUBJECTS, not resource paths (GHI #938). `.github/workflows/` appears
#: below as the POPULATION the "Python version pins" control audits — the set of
#: interpreter declarations it reads. It is never joined to a root and opened
#: here, so no `PathConfig` field could govern it: a field would say where
#: workflows live, which is the thing this table is asserting ABOUT.
_AUDIT_SUBJECT_LITERALS: tuple[str, ...] = (".github/workflows/",)


_STEP_CLASSIFICATION: dict[str, _StepMeta] = {
    "Lint": ("lint", "src/", "bound", "subprocess"),
    "Format": ("format", "src/", "bound", "subprocess"),
    "Typecheck": ("typecheck", "src/", "bound", "subprocess"),
    # Enrolled here in the same commit it joined `gz check`, matching the
    # precedent the "Advisory scorecard coverage" and "Pool interview schema"
    # comments below record. Subject is `src/` — the population it measures is
    # every module under it. `bound`: the gate exits 3 on a breach and gates the
    # `gz check` exit code; the ratchet's whole defect was having no caller, so
    # classifying it advisory would re-create that hole under a different name.
    "Module size": ("audit", "src/", "bound", "subprocess"),
    "Test": ("test", "tests/", "bound", "subprocess"),
    "Behave": ("bdd", "features/", "bound", "subprocess"),
    "Docs build": ("audit", "docs/", "bound", "subprocess"),
    # One bare `gz validate` gates the whole default tier (GHI #744). Subject is
    # "all" because the tier spans manifest, ledger, docs, briefs and rules.
    "Validate default scopes": ("audit", "all", "bound", "subprocess"),
    "Skill audit": ("audit", ".gzkit/skills/", "bound", "python_function"),
    "Parity check": ("audit", "all", "bound", "python_function"),
    "Readiness audit": ("audit", "all", "bound", "python_function"),
    "CLI audit": ("audit", "docs/", "bound", "python_function"),
    "Unscoped rules": ("audit", ".gzkit/rules/", "bound", "python_function"),
    # Enrolled the same commit it joined `gz check`. Subject is
    # `.github/workflows/` because that is the POPULATION it audits — the
    # interpreter declarations. `.python-version` is the authority it reads
    # them against, not the audited set, the same distinction the Advisory
    # scorecard entry below draws.
    "Python version pins": ("audit", ".github/workflows/", "bound", "python_function"),
    "ADR status freshness": ("audit", "docs/", "bound", "python_function"),
    # GHI #754: enrolled here the same commit it joined `gz check`. Its subject is
    # `.gzkit/rules/` because the population it audits is the canonical rule set,
    # not the scorecard document it reads them against.
    "Advisory scorecard coverage": ("audit", ".gzkit/rules/", "bound", "python_function"),
    "OBPI lifecycle coherence": ("audit", ".gzkit/", "bound", "python_function"),
    # Spans both surfaces by construction (GHI #676): the ledger half reads
    # `.gzkit/ledger.jsonl`, the brief half reads `docs/design/adr/**`.
    "Adversarial validation": ("audit", "all", "bound", "python_function"),
    # The falsifiability gate is itself falsifiable: its NC builds a completed brief
    # whose BEHAVIOR REQ has no RED witness, and asserts the audit catches it (GHI #642).
    "RED parity": ("audit", "all", "bound", "python_function"),
    # Producer-side contract parity: its NC undeclares a real producer field and
    # asserts the audit catches it, which the committed-row fence cannot (GHI #877).
    "Producer field parity": ("audit", "all", "bound", "python_function"),
    "Rendition freshness": ("audit", "docs/", "bound", "python_function"),
    "Rendition floor coherence": ("audit", "docs/", "bound", "python_function"),
    "Invariant coherence": ("audit", "docs/", "bound", "python_function"),
    "Corpus retirement witness": ("audit", ".gzkit/", "bound", "python_function"),
    # Enrolled in the same commit it joined `gz check`, per the precedent above.
    # Subject is `src/`: the population is the wheel-shipped Markdown under it,
    # selected by pyproject's own include block rather than a transcribed glob.
    # `python_function` like its sibling — the step shells out to `gz validate`,
    # but the catch/no-catch decision is gzkit Python, not an external tool.
    "Wheel path literals": ("audit", "src/", "bound", "python_function"),
    "Brief structure": ("audit", "docs/", "bound", "python_function"),
    "Session green gate": ("audit", ".gzkit/", "bound", "python_function"),
    "Closeout proof": ("audit", "docs/", "bound", "python_function"),
    "Kind invariance": ("audit", "docs/", "bound", "python_function"),
    "Persona witness": ("audit", "docs/", "bound", "python_function"),
    "Interview transcripts": ("audit", "docs/", "bound", "python_function"),
    # GHI #719: enrolled here in the same commit it joined `gz check`, matching
    # the precedent the "Advisory scorecard coverage" comment above records.
    # Subject is `docs/` — the population it audits is
    # `docs/design/adr/pool/*-interview.json`.
    "Pool interview schema": ("audit", "docs/", "bound", "python_function"),
    "Receipt shape": ("audit", ".gzkit/", "bound", "python_function"),
    "Orientation freshness": ("audit", ".gzkit/", "bound", "python_function"),
    "Insights shape": ("audit", ".gzkit/", "bound", "python_function"),
    "Instructions files budget": ("audit", "docs/", "bound", "python_function"),
    "AGENTS.md map conformance": ("audit", "docs/", "bound", "python_function"),
    "Complexity-doctrine links": ("audit", "docs/", "bound", "python_function"),
    "Complexity-thresholds": ("audit", "docs/", "bound", "python_function"),
    "REQ kind discipline": ("audit", "docs/", "bound", "python_function"),
    "Status writer coverage": ("audit", "src/", "bound", "python_function"),
    "Transcribed ADR counts": ("audit", "docs/", "bound", "python_function"),
    "tautological test audit": ("audit", "tests/", "bound", "python_function"),
    "Task envelope coherence": ("audit", "docs/", "bound", "python_function"),
    "Lock-exchange coupling": ("audit", ".gzkit/", "bound", "python_function"),
    "QC binding": ("audit", "src/", "bound", "python_function"),
    "Fidelity presence": ("audit", "docs/", "bound", "python_function"),
    "Waiver ratchet": ("audit", "data/", "bound", "python_function"),
    "Config registry": ("audit", "data/", "bound", "python_function"),
    "Gate callers": ("audit", "src/", "bound", "python_function"),
    "Exemption controls": ("audit", "src/", "bound", "python_function"),
    "Handoff documents": ("audit", "docs/", "bound", "python_function"),
    "Preflight": ("audit", ".gzkit/", "bound", "python_function"),
    "Surface fidelity": ("audit", "docs/", "bound", "python_function"),
    "Line endings": ("audit", "all", "bound", "python_function"),
    "Authorship policy": ("audit", "all", "bound", "python_function"),
    "Smoke tier": ("audit", "tests/", "bound", "python_function"),
    "Dispatch absorption marker": ("audit", "docs/", "bound", "python_function"),
    "Enforcement floor": ("audit", "src/", "bound", "python_function"),
    "ADR taxonomy": ("audit", "docs/", "bound", "python_function"),
}


def _name_to_id(name: str) -> str:
    """Convert a step name to a machine-stable slug."""
    return name.lower().replace(" ", "-").replace(".", "-")


# ---------------------------------------------------------------------------
# Advisory self-registration channel (ADR-0.0.73 / OBPI-07)
# ---------------------------------------------------------------------------
#
# Bound steps are DERIVED from ``_build_check_steps()`` and must never be
# hand-listed.  Advisory steps (e.g. ``gz adr evaluate``) grade quality WITHOUT
# gating ``gz check``'s exit code, so they are not in ``_build_check_steps()``.
# They self-register here so ``gz validate --qc-binding`` can still classify and
# audit them — closing the gap where an advisory checker presents shape-graded
# scores as authoritative truth with nothing classifying it.

_SELF_REGISTERED_ADVISORY_STEPS: list[QCStep] = []


def register_advisory_qc_step(
    *,
    name: str,
    kind: str,
    subject: str,
    wired_into: list[str],
    enforcement_locus: str,
) -> None:
    """Register an ``advisory`` QC step that runs outside ``gz check``'s pipeline.

    Idempotent by id: re-registration (e.g. on module re-import) replaces the
    prior entry rather than duplicating it.  Advisory steps carry no theater
    flags and are not required to fail a negative control — they report findings
    without gating the ``gz check`` exit code.
    """
    step = QCStep(
        id=_name_to_id(name),
        name=name,
        kind=kind,
        subject=subject,
        binding="advisory",
        wired_into=wired_into,
        theater_flags=[],
        enforcement_locus=enforcement_locus,
    )
    _SELF_REGISTERED_ADVISORY_STEPS[:] = [
        existing for existing in _SELF_REGISTERED_ADVISORY_STEPS if existing.id != step.id
    ]
    _SELF_REGISTERED_ADVISORY_STEPS.append(step)


# ---------------------------------------------------------------------------
# Registry builder
# ---------------------------------------------------------------------------


def build_qc_registry() -> list[QCStep]:
    """Build the QC-step registry derived from what ``gz check`` actually runs.

    Imports ``_build_check_steps`` lazily to avoid circular imports at module
    load time.  Raises ``KeyError`` when a step name in ``_build_check_steps()``
    has no entry in ``_STEP_CLASSIFICATION`` — the sentinel that forces authors
    to classify new steps when they add them to ``gz check``.

    Importing ``gzkit.adr_eval`` (the safe entry point for the adr_eval /
    adr_eval_scoring import cycle) triggers the evaluator's advisory
    self-registration, so the derived bound steps plus the self-registered
    advisory steps are both present whenever the registry is built — neither is
    a hand-maintained list.
    """
    import gzkit.adr_eval  # noqa: F401, PLC0415 — triggers gz-adr-evaluate self-registration
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
    registry.extend(_SELF_REGISTERED_ADVISORY_STEPS)
    return registry
