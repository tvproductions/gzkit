"""Negative-control fixtures for bound QC steps (ADR-0.0.73 / OBPI-0.0.73-02).

Split out of ``qc_binding.py`` for module-size discipline (<=600 lines,
`.claude/rules/pythonic.md`). Each ``_*_negative_control`` plants a fixture a
genuinely-bound step MUST fail on, returning an exit-style int: ``0`` = step
PASSED its NC (hollow/theater), non-zero = step FAILED its NC (genuinely bound).
``_PRODUCTION_NEGATIVE_CONTROLS`` maps step_id -> NC; ``qc_binding.py`` imports
it and registers each at import time. No behavior change from the split.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.core.validation_rules import ValidationError


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
        _write(
            root / ".gzkit" / "corpus" / "AGENTS.md.jsonl",
            json.dumps(
                {
                    "id": "entry-1",
                    "surface": "AGENTS.md",
                    "section": "attestation",
                    "text": "some corpus content",
                    "tier": "compressible",
                    "classification": "Judgment",
                    "origin": "negative-control",
                    "ts": "2026-01-01T00:00:00+00:00",
                }
            )
            + "\n",
        )
        # A committed rendition with NO provenance sidecar over a real corpus: the
        # rendition's derivation from the corpus is unproven, so the fail-closed gate
        # MUST flag it. A step that passes this fixture is theater. Checked fail-closed
        # because the live gate is staged in warn mode (OBPI-0.0.41 warn->fail).
        _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "old\n")
        return _genuine_when_errors(validate_rendition_freshness(root, fail_closed=True))


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
        # A committed rendition that drops an invariant-tier entry MUST be flagged.
        # Checked fail-closed because the live gate is staged in warn mode
        # (OBPI-0.0.41 warn->fail), sibling-consistent with rendition_freshness.
        _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "missing\n")
        return _genuine_when_errors(validate_rendition_floor_coherence(root, fail_closed=True))


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


def _fidelity_presence_negative_control() -> int:
    from gzkit.governance.trust_audits.fidelity_presence import (  # noqa: PLC0415
        audit_fidelity_presence,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        _write(
            root
            / "docs"
            / "design"
            / "adr"
            / "foundation"
            / "ADR-0.0.1-blockless"
            / "ADR-0.0.1-blockless.md",
            "---\nid: ADR-0.0.1-blockless\nkind: foundation\nlane: Lite\n---\n"
            "# ADR-0.0.1-blockless\n\n## Decision\n\nNo Fidelity Assertions block here.\n",
        )
        return _genuine_when_errors(audit_fidelity_presence(root, grandfather=frozenset()))


def _waiver_ratchet_negative_control() -> int:
    from gzkit.governance.trust_audits.waiver_ratchet import (  # noqa: PLC0415
        audit_waiver_ratchet,
    )

    with _tmp_root() as tmp:
        root = Path(tmp)
        # A surface grown past its committed shrink-ratchet baseline: the audit
        # MUST flag it. A step that passes this fixture is theater.
        _write(
            root / "data" / "waiver_ratchet_registry.json",
            '{"surfaces":[{"data_file":"data/bad_waivers.json",'
            '"mechanism":"shrink-ratchet","entries_path":"waivers","baseline_count":0}]}',
        )
        _write(root / "data" / "bad_waivers.json", '{"waivers":["grew","past","baseline"]}')
        return _genuine_when_errors(audit_waiver_ratchet(root))


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
    "fidelity-presence": _fidelity_presence_negative_control,
    "waiver-ratchet": _waiver_ratchet_negative_control,
}
