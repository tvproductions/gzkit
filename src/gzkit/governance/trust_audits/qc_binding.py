"""QC-binding behavioral audit (ADR-0.0.73 / OBPI-0.0.73-02).

Detects theater in bound QC steps via two channels:
1. Six static theater-signature checks (calibrated on ADR-0.0.37 facade)
2. Negative-control execution: a step that passes its own NC is theater

Usage::

    from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
    errors = audit_qc_binding(project_root)
    # Non-empty → exit 3; empty → exit 0
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.core.validation_rules import ValidationError
from gzkit.qc_binding import QCStep

# ---------------------------------------------------------------------------
# Six theater signatures calibrated on the ADR-0.0.37 facade
# ---------------------------------------------------------------------------

THEATER_SIGNATURES: tuple[str, ...] = (
    "mtime-where-name-says-content",
    "empty-input-passes",
    "copy-vs-self",
    "fixture-only",
    "skip-if-PASS",
    "prose-graded-by-nothing",
    "shape-graded-not-substance",
)

_THEATER_SIGNATURE_DESCRIPTIONS: dict[str, str] = {
    "mtime-where-name-says-content": (
        "Step checks file modification time instead of content "
        "(name implies content-checking but implementation uses mtime)"
    ),
    "empty-input-passes": (
        "Step always passes when given empty or absent input "
        "(no content → no violation is theater, not a clean check)"
    ),
    "copy-vs-self": (
        "Fixture compares content to itself — tautological assertion "
        "(fixture == expected is always true; the check can never fail)"
    ),
    "fixture-only": (
        "Step only runs against its own fixture, never the real project "
        "(a step that never sees real code cannot catch real violations)"
    ),
    "skip-if-PASS": (
        "Step short-circuits when a prior artifact is already in PASS state "
        "(skipping on PASS means the check never runs the second time)"
    ),
    "prose-graded-by-nothing": (
        "Step outputs prose that is never machine-verified "
        "(agent-written prose without a bound checker is theater)"
    ),
    "shape-graded-not-substance": (
        "Step renders an authoritative truth-score from prose SHAPE or KEYWORD "
        "presence rather than decision substance (a score satisfiable by keyword "
        "or format presence alone grades shape, not truth — GHI #624)"
    ),
}

# ---------------------------------------------------------------------------
# Negative-control registry
# ---------------------------------------------------------------------------

# Module-level NC registry: step_id → callable returning int (exit code).
# A callable returning 0 means the step PASSED its NC → hollow → theater.
# A callable returning non-zero means the step FAILED its NC → bound → genuine.
# Populated by register_negative_control(); the qc-binding step (the step this
# ADR owns) is wired at the bottom of this module.
_NEGATIVE_CONTROLS: dict[str, Callable[[], int]] = {}

# Acknowledged negative-control coverage debt (ADR-0.0.73, OBPI-06).
# These bound steps have no negative control yet. OBPI-0.0.73-02's checklist
# promised "each step ships a fixture it must fail on"; its code deferred that
# wiring, leaving the behavioral channel inert. Rather than let the audit pass
# green-by-emptiness (an unwired bound step verifies nothing — the very
# 'empty-input-passes' theater signature), every unwired bound step is listed
# here EXPLICITLY so the gap is visible and tracked. The audit FAILS on every
# entry in this set: acknowledged debt is not green evidence. This keeps the
# project red until the owed negative controls are authored, while preserving a
# separate message for a NEW bound step that is neither wired nor acknowledged.
# Authoring honest NCs for these is tracked OBPI-02 correction work.
_NEGATIVE_CONTROL_DEBT: frozenset[str] = frozenset({})


def register_negative_control(step_id: str, nc: Callable[[], int]) -> None:
    """Register a negative-control callable for a bound step.

    The callable must return an exit-code-like integer: 0 if the negative
    control passed (step is hollow/theater), non-zero if the step genuinely
    failed (step is bound). OBPI-06 registers entries for all existing steps.
    """
    _NEGATIVE_CONTROLS[step_id] = nc


def _tmp_root() -> TemporaryDirectory[str]:
    return TemporaryDirectory(prefix="gzkit-qc-nc-")


def _genuine_when_errors(errors: list[ValidationError]) -> int:
    return 1 if errors else 0


def _genuine_when_command_fails(command: str, root: Path) -> int:
    from gzkit.quality import run_command  # noqa: PLC0415

    return 1 if not run_command(command, cwd=root).success else 0


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    _write(path, "\n".join(json.dumps(record) for record in records) + "\n")


def _minimal_pyproject(root: Path) -> None:
    _write(root / "pyproject.toml", "[project]\nname = 'gzkit-qc-nc'\nversion = '0.0.0'\n")


def _lint_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _minimal_pyproject(root)
        _write(root / "bad.py", "import sys\n")
        return _genuine_when_command_fails("uv run ruff check .", root)


def _format_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _minimal_pyproject(root)
        _write(root / "bad.py", "x = [1,\n2]\n")
        return _genuine_when_command_fails("uv run ruff format --check .", root)


def _typecheck_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _minimal_pyproject(root)
        _write(root / "bad.py", "name: str = 1\n")
        return _genuine_when_command_fails("uv run ty check .", root)


def _test_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / "tests" / "test_failure.py",
            "import unittest\n\nclass TestFailure(unittest.TestCase):\n    def test_fails(self):\n"
            "        self.assertEqual(1, 2)\n",
        )
        return _genuine_when_command_fails("uv run -m unittest discover tests", root)


def _behave_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / "features" / "missing_step.feature",
            "Feature: missing step\n"
            "  Scenario: undefined\n"
            "    Given this step has no implementation\n",
        )
        return _genuine_when_command_fails("uv run -m behave", root)


def _command_missing_project_negative_control(command: str) -> int:
    with _tmp_root() as tmp:
        return _genuine_when_command_fails(command, Path(tmp))


def _parity_check_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "proposals" / "REPORT-TEMPLATE-airlineops-parity.md", "# Bad\n")
        return _genuine_when_command_fails("uv run gz parity check", root)


def _unscoped_rules_negative_control() -> int:
    from gzkit.validators.unscoped_rules import run_unscoped_rules  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / ".gzkit" / "manifest.json", '{"rules": {"unscoped_allowlist": []}}\n')
        _write(root / ".gzkit" / "rules" / "bad.md", '---\npaths: "**"\n---\n# Bad\n')
        return 1 if run_unscoped_rules(root).exit_code == 3 else 0


def _adr_status_freshness_negative_control() -> int:
    from gzkit.governance.trust_audits.taxonomy import audit_adr_status_fresh  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / "docs" / "governance" / "GovZero" / "adr-status.md", "stale\n")
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.1-example"
            / "ADR-0.0.1-example.md",
            "---\nid: ADR-0.0.1-example\nlane: Lite\nkind: foundation\n---\n# Example\n",
        )
        return _genuine_when_errors(audit_adr_status_fresh(root))


def _rendition_freshness_negative_control() -> int:
    from gzkit.governance.trust_audits.rendition_freshness import (  # noqa: PLC0415
        validate_rendition_freshness,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "old\n")
        time.sleep(0.01)
        _write(root / ".gzkit" / "corpus" / "AGENTS.md.jsonl", "{}\n")
        return _genuine_when_errors(validate_rendition_freshness(root))


def _rendition_floor_coherence_negative_control() -> int:
    from gzkit.governance.trust_audits.rendition_floor_coherence import (  # noqa: PLC0415
        validate_rendition_floor_coherence,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / ".gzkit" / "corpus" / "AGENTS.md.jsonl",
            json.dumps(
                {
                    "id": "invariant-entry",
                    "surface": "AGENTS.md",
                    "section": "attestation",
                    "text": "MUST APPEAR VERBATIM",
                    "tier": "invariant",
                    "classification": "Judgment",
                    "origin": "negative-control",
                    "ts": "2026-01-01T00:00:00+00:00",
                }
            )
            + "\n",
        )
        _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "missing\n")
        return _genuine_when_errors(validate_rendition_floor_coherence(root))


def _session_green_gate_negative_control() -> int:
    from gzkit.governance.trust_audits.session_green_gate import (  # noqa: PLC0415
        audit_session_green_gate,
    )

    with _tmp_root() as tmp:
        return _genuine_when_errors(audit_session_green_gate(Path(tmp)))


def _closeout_proof_negative_control() -> int:
    from gzkit.governance.trust_audits.closeout_proof import (  # noqa: PLC0415
        validate_closeout_proof,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / ".gzkit" / "ceremonies" / "ADR-0.0.99.ceremony.json",
            json.dumps(
                {
                    "adr_id": "ADR-0.0.99",
                    "started_at": "2026-06-16T00:00:00+00:00",
                    "updated_at": "2026-06-16T00:00:00+00:00",
                    "completed_at": None,
                }
            )
            + "\n",
        )
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.99"
            / "obpis"
            / "OBPI-0.0.99-01-closeout.md",
            "---\nid: OBPI-0.0.99-01-closeout\nparent: ADR-0.0.99\n---\n"
            "# Brief\n\n## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.99-01-01 [BEHAVIOR]: must have a covering test\n",
        )
        return _genuine_when_errors(validate_closeout_proof(root, adr_id="ADR-0.0.99"))


def _kind_invariance_negative_control() -> int:
    from gzkit.governance.trust_audits.kind_invariance import audit_kind_invariance  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.1-missing"
            / "ADR-0.0.1-missing.md",
            "# ADR-0.0.1 Missing\n",
        )
        return _genuine_when_errors(audit_kind_invariance(root))


def _interviews_negative_control() -> int:
    from gzkit.commands.validate_briefs import _validate_interviews  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.88-no-transcript"
        _write(
            adr_dir / "ADR-0.0.88-no-transcript.md",
            "---\nid: ADR-0.0.88-no-transcript\nkind: foundation\nlane: Lite\n---\n"
            "# ADR-0.0.88\n\n## Decision\n\nNo embedded transcript here.\n",
        )
        _write(
            adr_dir / "obpis" / "OBPI-0.0.88-01-demo.md",
            "---\nid: OBPI-0.0.88-01-demo\nparent: ADR-0.0.88-no-transcript\n---\n# Brief\n",
        )
        return _genuine_when_errors(_validate_interviews(root))


def _receipt_shape_negative_control() -> int:
    from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.36-attestation"
            / "ADR-0.0.36-attestation.md",
            "---\ndate: 2026-01-01\n---\n# ADR-0.0.36\n",
        )
        _write_jsonl(
            root / ".gzkit" / "ledger.jsonl",
            [
                {
                    "event": "obpi_receipt_emitted",
                    "id": "receipt-bad",
                    "ts": "2026-01-02T00:00:00+00:00",
                    "attestor": "agent:auto",
                    "evidence": {
                        "attestation_requirement": "optional",
                        "obpi_completion": "completed",
                    },
                }
            ],
        )
        return _genuine_when_errors(audit_receipt_shape(root))


def _orientation_freshness_negative_control() -> int:
    from gzkit.governance.trust_audits.orientation import (
        audit_orientation_freshness,  # noqa: PLC0415
    )

    with _tmp_root() as tmp:
        return _genuine_when_errors(audit_orientation_freshness(Path(tmp)))


def _insights_shape_negative_control() -> int:
    from gzkit.governance.trust_audits.insights import audit_insights_shape  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / ".gzkit" / "insights" / "agent-insights.jsonl", "{not-json}\n")
        return _genuine_when_errors(audit_insights_shape(root))


def _instructions_files_budget_negative_control() -> int:
    from gzkit.governance.trust_audits.instructions_files_budget import (  # noqa: PLC0415
        audit_instructions_files_budget,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / "data" / "instructions_files_budget.json", '{"files": {"AGENTS.md": 3}}\n')
        _write(root / "AGENTS.md", "too long\n")
        return _genuine_when_errors(audit_instructions_files_budget(root))


def _agents_md_map_conformance_negative_control() -> int:
    from gzkit.governance.trust_audits.agents_md_map_conformance import (  # noqa: PLC0415
        audit_agents_md_map_conformance,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / "src" / "gzkit" / "templates" / "agents.md", "## Worked example\nbad\n")
        return _genuine_when_errors(audit_agents_md_map_conformance(root))


def _complexity_doctrine_links_negative_control() -> int:
    from gzkit.governance.trust_audits.complexity_doctrine_links import (  # noqa: PLC0415
        validate_complexity_doctrine_links,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / ".gzkit" / "rules" / "complexity-doctrine.md",
            "See docs/governance/complexity/distilled-characteristics-missing.md "
            "§ nope (corpus revision 1).\n",
        )
        return _genuine_when_errors(validate_complexity_doctrine_links(root))


def _complexity_thresholds_negative_control() -> int:
    from gzkit.governance.trust_audits.complexity_thresholds import (  # noqa: PLC0415
        validate_complexity_thresholds,
    )

    with _tmp_root() as tmp:
        return _genuine_when_errors(validate_complexity_thresholds(Path(tmp)))


def _req_kind_discipline_negative_control() -> int:
    from gzkit.commands.validate_req_kind import _validate_req_kind_discipline  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.1-parent"
            / "obpis"
            / "OBPI-0.0.1-01-demo.md",
            "---\nid: OBPI-0.0.1-01-demo\nparent: ADR-0.0.1-parent\n---\n"
            "# Brief\n\n## Allowed Paths\n\n- `src/demo.py`\n\n## Acceptance Criteria\n\n"
            "- [ ] REQ-0.0.1-01-01 [BEHAVIOR]: must be tested\n",
        )
        return _genuine_when_errors(_validate_req_kind_discipline(root))


def _tautological_test_audit_negative_control() -> int:
    from gzkit.tautological_tests import audit_drift  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / "tests" / "test_bad.py",
            "import unittest\n\nclass TestBad(unittest.TestCase):\n    def test_bad(self):\n"
            "        open('x.txt').read()\n        self.assertTrue(True)\n",
        )
        return _genuine_when_errors(audit_drift(root))


def _task_envelope_coherence_negative_control() -> int:
    from gzkit.commands.validate_task_envelope import (  # noqa: PLC0415
        _validate_task_envelope_coherence,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write_jsonl(
            root / ".gzkit" / "ledger.jsonl",
            [
                {
                    "event": "task_started",
                    "ts": "2026-06-01T00:00:00+00:00",
                    "obpi_id": "OBPI-0.0.1-01",
                    "task_id": "TASK-0.0.1-01-01-01",
                },
                {
                    "event": "artifact_edited",
                    "ts": "2026-06-01T00:00:01+00:00",
                    "obpi_id": "OBPI-0.0.1-01",
                    "path": "src/demo.py",
                },
            ],
        )
        return _genuine_when_errors(_validate_task_envelope_coherence(root))


def _lock_handoff_coupling_negative_control() -> int:
    from gzkit.governance.trust_audits.lock_handoff_coupling import (  # noqa: PLC0415
        validate_lock_handoff_coupling,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write_jsonl(
            root / ".gzkit" / "ledger.jsonl",
            [
                {
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.0.41-03-cutover",
                    "ts": "2026-06-01T00:00:00+00:00",
                },
                {
                    "event": "obpi_lock_released",
                    "id": "OBPI-0.0.1-01-demo",
                    "ts": "2026-06-01T00:00:01+00:00",
                    "agent": "agent-a",
                },
            ],
        )
        return _genuine_when_errors(validate_lock_handoff_coupling(root))


def _handoff_documents_negative_control() -> int:
    from gzkit.quality import run_handoff_document_audit  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root / ".gzkit" / "handoffs" / "bad.md",
            "---\n"
            "mode: CREATE\n"
            "adr_id: ADR-0.0.72\n"
            "branch: main\n"
            "timestamp: '2026-06-16T00:00:00+00:00'\n"
            "agent: agent:test\n"
            "---\n"
            "## Current State Summary\n\n"
            "This malformed post-cutover handoff is missing required sections.\n",
        )
        return 1 if not run_handoff_document_audit(root).success else 0


def _preflight_negative_control() -> int:
    with _tmp_root() as tmp:
        root = Path(tmp)
        marker = {
            "obpi_id": "OBPI-0.0.1-01-demo",
            "updated_at": "2000-01-01T00:00:00+00:00",
        }
        _write(
            root / ".claude" / "plans" / ".pipeline-active-OBPI-0.0.1-01-demo.json",
            json.dumps(marker) + "\n",
        )
        return _genuine_when_command_fails("uv run gz preflight", root)


def _surface_fidelity_negative_control() -> int:
    from gzkit.governance.trust_audits import validate_surface_fidelity  # noqa: PLC0415

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(root / "AGENTS.md", "> See [missing](docs/missing.md#required-section)\n")
        return _genuine_when_errors(validate_surface_fidelity(root))


def _line_endings_negative_control() -> int:
    from gzkit.governance.trust_audits.cross_platform import audit_line_endings  # noqa: PLC0415

    with _tmp_root() as tmp:
        return _genuine_when_errors(audit_line_endings(Path(tmp)))


def _dispatch_attestation_negative_control() -> int:
    from gzkit.quality import run_dispatch_attestation_audit  # noqa: PLC0415

    with _tmp_root() as tmp:
        return 1 if not run_dispatch_attestation_audit(Path(tmp)).success else 0


# ---------------------------------------------------------------------------
# Error builder
# ---------------------------------------------------------------------------


def _err(step_name: str, message: str) -> ValidationError:
    return ValidationError(type="qc_binding", artifact=step_name, message=message)


# ---------------------------------------------------------------------------
# Theater-signature detection
# ---------------------------------------------------------------------------


def _check_theater_signatures(step: QCStep) -> list[ValidationError]:
    """Return one ValidationError per theater signature found in step.theater_flags.

    The canonical signatures are the six ADR-0.0.37 facade signatures plus the
    seventh ``shape-graded-not-substance`` (GHI #624, OBPI-0.0.73-07); any flag
    from ``THEATER_SIGNATURES`` found in step.theater_flags produces an error.
    Unknown flags are noted but not treated as canonical.
    """
    errors: list[ValidationError] = []
    for flag in step.theater_flags:
        if flag in THEATER_SIGNATURES:
            description = _THEATER_SIGNATURE_DESCRIPTIONS.get(flag, "")
            errors.append(
                _err(
                    step.name,
                    f"Theater signature '{flag}': {description}. "
                    "Implement a genuine check that fails for the right reason.",
                )
            )
    return errors


# ---------------------------------------------------------------------------
# Negative-control execution
# ---------------------------------------------------------------------------


def _check_negative_control(
    step: QCStep,
    nc_registry: dict[str, Callable[[], int]] | None = None,
) -> list[ValidationError]:
    """Run the step's negative control; flag if it exits 0 (hollow step).

    When ``nc_registry`` is None, the module-level ``_NEGATIVE_CONTROLS``
    registry is used. Passing an explicit registry is the test-isolation path.

    A step with no registered NC is skipped — absence of an NC is not itself
    a finding (OBPI-06 adds NCs; OBPI-02 ships the infrastructure only).
    """
    registry = nc_registry if nc_registry is not None else _NEGATIVE_CONTROLS
    nc = registry.get(step.id)
    if nc is None:
        return []
    exit_code = nc()
    if exit_code == 0:
        return [
            _err(
                step.name,
                "Hollow step: passed its own negative-control fixture (exit 0 when "
                "non-zero expected). A genuinely bound check must fail on its "
                "negative control.",
            )
        ]
    return []


# ---------------------------------------------------------------------------
# Main audit entry point
# ---------------------------------------------------------------------------


def audit_qc_binding(
    project_root: Path,  # noqa: ARG001 — registry-protocol parity; OBPI-06 may use it
    *,
    nc_registry: dict[str, Callable[[], int]] | None = None,
) -> list[ValidationError]:
    """Behavioral QC-binding audit (ADR-0.0.73 / OBPI-0.0.73-02).

    For every QC step in the registry:
    - Runs theater-signature detection (via step.theater_flags)
    - For ``bound`` steps, runs the registered negative control (if any)

    Returns a list of ValidationErrors; non-empty → caller should exit 3.
    An unclassified step (``build_qc_registry`` KeyError) is surfaced as a
    single error on the "registry" artifact rather than crashing.
    """
    from gzkit.qc_binding import build_qc_registry  # noqa: PLC0415

    try:
        registry = build_qc_registry()
    except KeyError as exc:
        return [
            ValidationError(
                type="qc_binding",
                artifact="registry",
                message=f"QC registry build failed — unclassified step: {exc}",
            )
        ]

    active_nc = nc_registry if nc_registry is not None else _NEGATIVE_CONTROLS
    errors: list[ValidationError] = []
    for step in registry:
        errors.extend(_check_theater_signatures(step))
        if step.binding == "bound":
            if step.id in active_nc:
                errors.extend(_check_negative_control(step, active_nc))
            elif step.id in _NEGATIVE_CONTROL_DEBT:
                errors.append(
                    _err(
                        step.name,
                        f"Negative-control debt: bound step '{step.id}' has no registered "
                        "negative control. This debt is acknowledged, but acknowledged "
                        "debt is not passing evidence; author a genuine fixture via "
                        f"register_negative_control('{step.id}', ...) and remove the id "
                        "from _NEGATIVE_CONTROL_DEBT.",
                    )
                )
            else:
                errors.append(
                    _err(
                        step.name,
                        f"Green-by-emptiness: bound step '{step.id}' has no registered "
                        "negative control and is not in the acknowledged "
                        "_NEGATIVE_CONTROL_DEBT set. ADR-0.0.73 forbids a bound QC step "
                        "that cannot fail its own negative control — it verifies nothing "
                        "(the 'empty-input-passes' theater signature). Register one via "
                        f"register_negative_control('{step.id}', ...), or if its NC "
                        "authoring is tracked correction work, add it to "
                        "_NEGATIVE_CONTROL_DEBT.",
                    )
                )
    return errors


# ---------------------------------------------------------------------------
# Negative control for the qc-binding step itself (the step this ADR owns)
# ---------------------------------------------------------------------------


def _qc_binding_negative_control() -> int:
    """Genuine negative control for the ``qc-binding`` step.

    Feeds the theater detector a step that IS theater (it carries a canonical
    signature) and reports whether the detector fired, as an exit-style int:
    ``0`` means the detector MISSED the planted theater (hollow → the step would
    be flagged), non-zero means it caught it (genuinely bound). If
    ``_check_theater_signatures`` were ever gutted so it stopped flagging known
    signatures, this control returns 0 and the ``qc-binding`` step is itself
    flagged hollow — a check that cannot fail for the right reason fails here.
    """
    planted = QCStep(
        id="nc-planted-theater",
        name="NC Planted Theater",
        kind="audit",
        subject="src/",
        binding="bound",
        wired_into=["gz check"],
        theater_flags=["copy-vs-self"],
        enforcement_locus="python_function",
    )
    return 1 if _check_theater_signatures(planted) else 0


register_negative_control("qc-binding", _qc_binding_negative_control)

_PRODUCTION_NEGATIVE_CONTROLS: dict[str, Callable[[], int]] = {
    "lint": _lint_negative_control,
    "format": _format_negative_control,
    "typecheck": _typecheck_negative_control,
    "test": _test_negative_control,
    "behave": _behave_negative_control,
    "skill-audit": lambda: _command_missing_project_negative_control("uv run gz skill audit"),
    "parity-check": _parity_check_negative_control,
    "readiness-audit": lambda: _command_missing_project_negative_control(
        "uv run gz readiness audit"
    ),
    "cli-audit": lambda: _command_missing_project_negative_control("uv run gz cli audit"),
    "unscoped-rules": _unscoped_rules_negative_control,
    "adr-status-freshness": _adr_status_freshness_negative_control,
    "rendition-freshness": _rendition_freshness_negative_control,
    "rendition-floor-coherence": _rendition_floor_coherence_negative_control,
    "session-green-gate": _session_green_gate_negative_control,
    "closeout-proof": _closeout_proof_negative_control,
    "kind-invariance": _kind_invariance_negative_control,
    "interview-transcripts": _interviews_negative_control,
    "receipt-shape": _receipt_shape_negative_control,
    "orientation-freshness": _orientation_freshness_negative_control,
    "insights-shape": _insights_shape_negative_control,
    "instructions-files-budget": _instructions_files_budget_negative_control,
    "agents-md-map-conformance": _agents_md_map_conformance_negative_control,
    "complexity-doctrine-links": _complexity_doctrine_links_negative_control,
    "complexity-thresholds": _complexity_thresholds_negative_control,
    "req-kind-discipline": _req_kind_discipline_negative_control,
    "tautological-test-audit": _tautological_test_audit_negative_control,
    "task-envelope-coherence": _task_envelope_coherence_negative_control,
    "lock-handoff-coupling": _lock_handoff_coupling_negative_control,
    "handoff-documents": _handoff_documents_negative_control,
    "preflight": _preflight_negative_control,
    "surface-fidelity": _surface_fidelity_negative_control,
    "line-endings": _line_endings_negative_control,
    "dispatch-attestation": _dispatch_attestation_negative_control,
}

for _step_id, _negative_control in _PRODUCTION_NEGATIVE_CONTROLS.items():
    register_negative_control(_step_id, _negative_control)
