"""Negative-control fixtures + ``@enforces`` registrations for bound QC steps.

ADR-0.0.73 (OBPI-0.0.73-02) introduced these negative controls; ADR-0.0.74
(OBPI-0.0.74-16) re-authored them onto the single ``@enforces`` enforcement-claim
surface so the qc_binding audit and the meta-validator runner share ONE engine
(Boundary Invariant #6 — no second negative-control framework).

Each claim is split into:

* ``_build_<claim>() -> Path`` — builds the known violation in a fresh temp dir and
  returns its path. The runner (``enforcement._run_single_claim``) removes the dir
  after the entrypoint runs, so fixtures use ``mkdtemp`` rather than a context manager.
* ``_ep_<claim>`` (in ``_qc_nc_entrypoints.py``) — the production enforcement path the
  runner invokes as ``entrypoint(fixture())``.

Genuineness is structural (Boundary Invariant #7): the fixture NEVER calls the
validator; only the runner does, via ``entrypoint(fixture())``. The two formerly
forced controls (``rendition-freshness``, ``rendition-floor-coherence``) are now
UN-FORCED — their entrypoints pass no ``fail_closed=True`` (D1 — genuineness is
absolute).
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit.enforcement import enforces, get_enforcement_registry

from . import _qc_nc_entrypoints as _ep

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _mkroot(slug: str) -> Path:
    """Return a fresh temp dir Path; the runner removes it after the entrypoint runs."""
    return Path(tempfile.mkdtemp(prefix=f"gzkit-qc-nc-{slug}-"))


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    _write(path, "\n".join(json.dumps(record) for record in records) + "\n")


def _minimal_pyproject(root: Path) -> None:
    _write(root / "pyproject.toml", "[project]\nname = 'gzkit-qc-nc'\nversion = '0.0.0'\n")


def _build_empty(slug: str = "empty") -> Path:
    """Violation-by-absence: an empty project where the validator flags a missing artifact."""
    return _mkroot(slug)


# ---------------------------------------------------------------------------
# Per-claim violation fixtures
# ---------------------------------------------------------------------------


def _build_lint() -> Path:
    root = _mkroot("lint")
    _minimal_pyproject(root)
    _write(root / "bad.py", "import sys\n")
    return root


def _build_format() -> Path:
    root = _mkroot("format")
    _minimal_pyproject(root)
    _write(root / "bad.py", "x = [1,\n2]\n")
    return root


def _build_typecheck() -> Path:
    root = _mkroot("typecheck")
    _minimal_pyproject(root)
    _write(root / "bad.py", "name: str = 1\n")
    return root


def _build_test() -> Path:
    root = _mkroot("test")
    _write(
        root / "tests" / "test_failure.py",
        "import unittest\n\nclass TestFailure(unittest.TestCase):\n    def test_fails(self):\n"
        "        self.assertEqual(1, 2)\n",
    )
    return root


def _build_behave() -> Path:
    root = _mkroot("behave")
    _write(
        root / "features" / "missing_step.feature",
        "Feature: missing step\n  Scenario: undefined\n    Given this step has no implementation\n",
    )
    return root


def _build_parity_check() -> Path:
    root = _mkroot("parity-check")
    _write(root / "docs" / "proposals" / "REPORT-TEMPLATE-airlineops-parity.md", "# Bad\n")
    return root


def _build_unscoped_rules() -> Path:
    root = _mkroot("unscoped-rules")
    _write(root / ".gzkit" / "manifest.json", '{"rules": {"unscoped_allowlist": []}}\n')
    _write(root / ".gzkit" / "rules" / "bad.md", '---\npaths: "**"\n---\n# Bad\n')
    return root


def _build_adr_status_freshness() -> Path:
    root = _mkroot("adr-status")
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
    return root


def _build_rendition_freshness() -> Path:
    root = _mkroot("rendition-freshness")
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
    # rendition's derivation from the corpus is unproven, so the gate MUST flag it.
    _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "old\n")
    return root


def _build_rendition_floor_coherence() -> Path:
    root = _mkroot("rendition-floor")
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
    _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.md", "missing\n")
    return root


def _build_invariant_coherence() -> Path:
    root = _mkroot("invariant-coherence")
    # A committed rendition that plays back to a non-empty AGENTS.md, with NO
    # committed AGENTS.md on disk: playback != committed (b"") is genuine drift.
    _write(
        root / ".gzkit" / "renditions" / "AGENTS.md" / "claude.md",
        "# Rendered AGENTS.md\n\nPlayback body the committed surface does not carry.\n",
    )
    return root


def _build_closeout_proof() -> Path:
    root = _mkroot("closeout-proof")
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
    return root


def _build_kind_invariance() -> Path:
    root = _mkroot("kind-invariance")
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
    return root


def _build_interview_transcripts() -> Path:
    root = _mkroot("interviews")
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
    return root


def _build_receipt_shape() -> Path:
    root = _mkroot("receipt-shape")
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
    return root


def _build_insights_shape() -> Path:
    root = _mkroot("insights-shape")
    _write(root / ".gzkit" / "insights" / "agent-insights.jsonl", "{not-json}\n")
    return root


def _build_instructions_files_budget() -> Path:
    root = _mkroot("instr-budget")
    _write(root / "data" / "instructions_files_budget.json", '{"files": {"AGENTS.md": 3}}\n')
    _write(root / "AGENTS.md", "too long\n")
    return root


def _build_agents_md_map_conformance() -> Path:
    root = _mkroot("agents-md-map")
    _write(root / "src" / "gzkit" / "templates" / "agents.md", "## Worked example\nbad\n")
    return root


def _build_complexity_doctrine_links() -> Path:
    root = _mkroot("complexity-links")
    _write(
        root / ".gzkit" / "rules" / "complexity-doctrine.md",
        "See docs/governance/complexity/distilled-characteristics-missing.md "
        "§ nope (corpus revision 1).\n",
    )
    return root


def _build_req_kind_discipline() -> Path:
    root = _mkroot("req-kind")
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
    return root


def _build_tautological_test_audit() -> Path:
    root = _mkroot("tautological")
    _write(
        root / "tests" / "test_bad.py",
        "import unittest\n\nclass TestBad(unittest.TestCase):\n    def test_bad(self):\n"
        "        open('x.txt').read()\n        self.assertTrue(True)\n",
    )
    return root


def _build_task_envelope_coherence() -> Path:
    root = _mkroot("task-envelope")
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
    return root


def _build_lock_handoff_coupling() -> Path:
    root = _mkroot("lock-handoff")
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
    return root


def _build_handoff_documents() -> Path:
    root = _mkroot("handoff-docs")
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
    return root


def _build_preflight() -> Path:
    root = _mkroot("preflight")
    marker = {
        "obpi_id": "OBPI-0.0.1-01-demo",
        "updated_at": "2000-01-01T00:00:00+00:00",
    }
    _write(
        root / ".claude" / "plans" / ".pipeline-active-OBPI-0.0.1-01-demo.json",
        json.dumps(marker) + "\n",
    )
    return root


def _build_surface_fidelity() -> Path:
    root = _mkroot("surface-fidelity")
    _write(root / "AGENTS.md", "> See [missing](docs/missing.md#required-section)\n")
    return root


def _build_fidelity_presence() -> Path:
    root = _mkroot("fidelity-presence")
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
    return root


def _build_waiver_ratchet() -> Path:
    root = _mkroot("waiver-ratchet")
    # A surface grown past its committed shrink-ratchet baseline: the audit MUST flag it.
    _write(
        root / "data" / "waiver_ratchet_registry.json",
        '{"surfaces":[{"data_file":"data/bad_waivers.json",'
        '"mechanism":"shrink-ratchet","entries_path":"waivers","baseline_count":0}]}',
    )
    _write(root / "data" / "bad_waivers.json", '{"waivers":["grew","past","baseline"]}')
    return root


# ---------------------------------------------------------------------------
# Claim registration table — (claim_id, fixture, production entrypoint)
# ---------------------------------------------------------------------------

# Each tuple registers one enforcement claim through the single @enforces primitive
# (Boundary Invariant #6). "qc-binding" is registered separately in qc_binding.py
# (its entrypoint is the theater-signature detector that lives there).
_QC_NEGATIVE_CONTROL_TABLE: tuple[tuple[str, Callable[[], Any], Callable[..., Any]], ...] = (
    ("lint", _build_lint, _ep._ep_lint),
    ("format", _build_format, _ep._ep_format),
    ("typecheck", _build_typecheck, _ep._ep_typecheck),
    ("test", _build_test, _ep._ep_test),
    ("behave", _build_behave, _ep._ep_behave),
    ("skill-audit", lambda: _build_empty("skill-audit"), _ep._ep_skill_audit),
    ("parity-check", _build_parity_check, _ep._ep_parity_check),
    ("readiness-audit", lambda: _build_empty("readiness-audit"), _ep._ep_readiness_audit),
    ("cli-audit", lambda: _build_empty("cli-audit"), _ep._ep_cli_audit),
    ("unscoped-rules", _build_unscoped_rules, _ep._ep_unscoped_rules),
    ("adr-status-freshness", _build_adr_status_freshness, _ep._ep_adr_status_freshness),
    ("rendition-freshness", _build_rendition_freshness, _ep._ep_rendition_freshness),
    (
        "rendition-floor-coherence",
        _build_rendition_floor_coherence,
        _ep._ep_rendition_floor_coherence,
    ),
    ("invariant-coherence", _build_invariant_coherence, _ep._ep_invariant_coherence),
    ("session-green-gate", lambda: _build_empty("session-green-gate"), _ep._ep_session_green_gate),
    ("closeout-proof", _build_closeout_proof, _ep._ep_closeout_proof),
    ("kind-invariance", _build_kind_invariance, _ep._ep_kind_invariance),
    ("interview-transcripts", _build_interview_transcripts, _ep._ep_interview_transcripts),
    ("receipt-shape", _build_receipt_shape, _ep._ep_receipt_shape),
    ("orientation-freshness", lambda: _build_empty("orientation"), _ep._ep_orientation_freshness),
    ("insights-shape", _build_insights_shape, _ep._ep_insights_shape),
    (
        "instructions-files-budget",
        _build_instructions_files_budget,
        _ep._ep_instructions_files_budget,
    ),
    (
        "agents-md-map-conformance",
        _build_agents_md_map_conformance,
        _ep._ep_agents_md_map_conformance,
    ),
    (
        "complexity-doctrine-links",
        _build_complexity_doctrine_links,
        _ep._ep_complexity_doctrine_links,
    ),
    (
        "complexity-thresholds",
        lambda: _build_empty("complexity-thresholds"),
        _ep._ep_complexity_thresholds,
    ),
    ("req-kind-discipline", _build_req_kind_discipline, _ep._ep_req_kind_discipline),
    ("tautological-test-audit", _build_tautological_test_audit, _ep._ep_tautological_test_audit),
    ("task-envelope-coherence", _build_task_envelope_coherence, _ep._ep_task_envelope_coherence),
    ("lock-handoff-coupling", _build_lock_handoff_coupling, _ep._ep_lock_handoff_coupling),
    ("handoff-documents", _build_handoff_documents, _ep._ep_handoff_documents),
    ("preflight", _build_preflight, _ep._ep_preflight),
    ("surface-fidelity", _build_surface_fidelity, _ep._ep_surface_fidelity),
    ("line-endings", lambda: _build_empty("line-endings"), _ep._ep_line_endings),
    (
        "dispatch-attestation",
        lambda: _build_empty("dispatch-attestation"),
        _ep._ep_dispatch_attestation,
    ),
    ("fidelity-presence", _build_fidelity_presence, _ep._ep_fidelity_presence),
    ("waiver-ratchet", _build_waiver_ratchet, _ep._ep_waiver_ratchet),
)

# The known-claims set the @enforces decorator validates against at decoration time.
# Includes the 36 NC ids above + "qc-binding" (registered in qc_binding.py). Defined
# BEFORE the registration loop so the re-entrant _load_known_claims() lookup resolves.
_KNOWN_QC_CLAIM_IDS: frozenset[str] = frozenset(
    {claim_id for claim_id, _f, _e in _QC_NEGATIVE_CONTROL_TABLE} | {"qc-binding"}
)


def _register_marker() -> None:
    """Inert carrier for @enforces registration (the fixture/entrypoint are the contract)."""


def register_qc_negative_controls() -> None:
    """Register the 36 qc negative-control claims via the @enforces primitive (idempotent).

    Called at import time and re-callable after ``reset_enforcement_registry()`` so the
    production claims survive test resets. Skips any claim already registered.
    """
    existing = {r.claim_id for r in get_enforcement_registry()}
    for claim_id, fixture, entrypoint in _QC_NEGATIVE_CONTROL_TABLE:
        if claim_id in existing:
            continue
        enforces(claim_id, fixture, entrypoint)(_register_marker)


register_qc_negative_controls()
