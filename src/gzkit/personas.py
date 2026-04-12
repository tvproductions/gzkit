"""Trait composition model for persona identity frames.

Persona traits compose orthogonally — each activates an independent behavioral
dimension without interfering with existing traits (PERSONA/ICLR 2026).  This
module provides a deterministic composition function that produces a persona
frame from frontmatter and optional body text, plus vendor adapter functions
that translate canonical frames into vendor-specific formats.

See ADR-0.0.11 for the research basis and OBPI-0.0.11-03 for the composition
specification.  See OBPI-0.0.13-04 for vendor adapter design.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from gzkit.models.persona import PersonaFrontmatter

if TYPE_CHECKING:
    from gzkit.models.persona import PersonaDriftReport, TraitCheckResult

# Project-agnostic starter personas scaffolded by ``gz init``.
# Content MUST NOT reference any specific project, language, or tool.
DEFAULT_PERSONAS: dict[str, str] = {
    "default-agent": """\
---
name: default-agent
traits:
  - methodical
  - governance-aware
  - clear-communicator
anti-traits:
  - assumptions-without-evidence
  - scope-creep
  - incomplete-work
grounding: >-
  I work inside a governed repository where every artifact traces to intent.
  I read the brief before I plan, the plan before I implement, and the
  evidence before I attest. Governance is not overhead — it is the discipline
  that keeps multi-session work coherent and auditable.
---

# Default Agent Persona

Starter persona for the primary agent session in a governed repository.
Projects should customize traits, anti-traits, and grounding to reflect
their specific workflow and values.
""",
    "default-reviewer": """\
---
name: default-reviewer
traits:
  - thorough
  - evidence-driven
  - constructive
anti-traits:
  - rubber-stamping
  - nitpicking-without-context
  - vague-feedback
grounding: >-
  I verify work against stated requirements. Every finding I report is
  grounded in evidence — a specific file, a specific test, a specific
  requirement. I distinguish between blocking issues and suggestions.
  When work meets its acceptance criteria, I say so clearly.
---

# Default Reviewer Persona

Starter persona for review and verification roles. Projects should
customize to reflect their quality standards and review culture.
""",
}


def scaffold_default_personas(project_root: Path) -> list[Path]:
    """Scaffold default persona files into ``.gzkit/personas/``.

    Creates the directory if needed and writes each default persona file
    only when no file with that name already exists.  Returns the list of
    newly created paths (empty when all defaults already exist).
    """
    personas_dir = project_root / ".gzkit" / "personas"
    personas_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for name, content in DEFAULT_PERSONAS.items():
        target = personas_dir / f"{name}.md"
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created.append(target)
    return created


def _parse_anchors(body: str, heading: str) -> dict[str, str]:
    """Extract name→description mapping from a markdown list under *heading*.

    Expects lines like ``- **Name**: Description text.`` under a ``## Heading``
    section.  Matching is case-insensitive on the bold name.
    """
    result: dict[str, str] = {}
    in_section = False
    item_re = re.compile(r"^- \*\*(.+?)\*\*:\s*(.+)$")

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lstrip("# ").strip().lower() == heading.lower()
            continue
        if in_section:
            m = item_re.match(stripped)
            if m:
                name = m.group(1).strip().lower()
                desc = m.group(2).strip()
                result[name] = desc

    return result


def compose_persona_frame(fm: PersonaFrontmatter, body: str = "") -> str:
    """Compose a deterministic persona frame from frontmatter and body.

    The output follows the canonical template defined in OBPI-0.0.11-03:

    1. Grounding text emitted verbatim as the opening behavioral anchor.
    2. Each trait emitted as ``You are {name}: {description}`` when the body
       contains a matching ``## Behavioral Anchors`` entry, or ``You are
       {name}.`` otherwise.
    3. Anti-traits emitted under ``What this persona does NOT do:`` with
       descriptions from ``## Anti-patterns`` when available.

    Composition is deterministic: identical inputs always produce identical
    output.  Traits compose by concatenation because they activate orthogonal
    behavioral dimensions (PERSONA/ICLR 2026).
    """
    trait_descs = _parse_anchors(body, "Behavioral Anchors") if body else {}
    anti_descs = _parse_anchors(body, "Anti-patterns") if body else {}

    sections: list[str] = []

    # 1. Grounding text verbatim
    sections.append(fm.grounding.strip())

    # 2. Trait composition (orthogonal concatenation, declaration order)
    trait_lines: list[str] = []
    for trait in fm.traits:
        desc = trait_descs.get(trait.lower())
        if desc:
            trait_lines.append(f"You are {trait}: {desc}")
        else:
            trait_lines.append(f"You are {trait}.")
    sections.append("\n\n".join(trait_lines))

    # 3. Anti-trait suppression section
    if fm.anti_traits:
        anti_lines: list[str] = []
        for at in fm.anti_traits:
            desc = anti_descs.get(at.lower())
            if desc:
                anti_lines.append(f"- {at}: {desc}")
            else:
                anti_lines.append(f"- {at}")
        sections.append("What this persona does NOT do:\n" + "\n".join(anti_lines))

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Vendor adapter functions (OBPI-0.0.13-04)
# ---------------------------------------------------------------------------


def render_persona_claude(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame in Claude's native system prompt format.

    Delegates to ``compose_persona_frame`` which already produces the canonical
    Claude format: grounding anchor, trait instructions, anti-trait constraints.
    """
    return compose_persona_frame(fm, body)


def render_persona_codex(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame as an AGENTS.md-compatible instruction block.

    Produces a structured markdown block with heading, grounding, behavioral
    traits list, and anti-patterns list suitable for Codex AGENTS.md files.
    """
    trait_descs = _parse_anchors(body, "Behavioral Anchors") if body else {}
    anti_descs = _parse_anchors(body, "Anti-patterns") if body else {}

    sections: list[str] = [f"# Persona: {fm.name}"]
    sections.append(fm.grounding.strip())

    trait_lines: list[str] = []
    for trait in fm.traits:
        desc = trait_descs.get(trait.lower())
        if desc:
            trait_lines.append(f"- {trait}: {desc}")
        else:
            trait_lines.append(f"- {trait}")
    sections.append("## Behavioral Traits\n\n" + "\n".join(trait_lines))

    if fm.anti_traits:
        anti_lines: list[str] = []
        for at in fm.anti_traits:
            desc = anti_descs.get(at.lower())
            if desc:
                anti_lines.append(f"- {at}: {desc}")
            else:
                anti_lines.append(f"- {at}")
        sections.append("## Anti-Patterns\n\n" + "\n".join(anti_lines))

    return "\n\n".join(sections)


def render_persona_copilot(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame as a copilot-instructions.md-compatible fragment.

    Produces a compact markdown section with heading, grounding, and inline
    trait/anti-trait lists suitable for ``.github/copilot-instructions.md``.
    """
    sections: list[str] = [f"## Persona: {fm.name}"]
    sections.append(fm.grounding.strip())
    sections.append("Behavioral traits: " + ", ".join(fm.traits))
    if fm.anti_traits:
        sections.append("Behaviors to avoid: " + ", ".join(fm.anti_traits))
    return "\n\n".join(sections)


def _rebuild_raw_persona(fm: PersonaFrontmatter, body: str) -> str:
    """Reconstruct canonical persona markdown from frontmatter and body.

    Used as the fallback when no vendor adapter is registered — the raw
    canonical format is copied verbatim.
    """
    fm_dict = {
        "name": fm.name,
        "traits": list(fm.traits),
        "anti-traits": list(fm.anti_traits),
        "grounding": fm.grounding,
    }
    fm_yaml = yaml.dump(fm_dict, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_yaml}---\n\n{body}"


VENDOR_ADAPTERS: dict[str, Callable[[PersonaFrontmatter, str], str]] = {
    "claude": render_persona_claude,
    "codex": render_persona_codex,
    "copilot": render_persona_copilot,
}
"""Registry mapping vendor name to persona adapter function."""


# ---------------------------------------------------------------------------
# Drift detection engine (OBPI-0.0.13-05)
# ---------------------------------------------------------------------------

TraitProxyFn = Callable[
    [Path, list[dict[str, object]], list[dict[str, object]]],
    tuple[str, str],
]
"""Signature: (project_root, ledger_events, audit_records) -> (status, detail)."""


def _scan_ledger_events(project_root: Path) -> list[dict[str, object]]:
    """Read ledger events as raw dicts for proxy evaluation.

    Returns an empty list if the ledger does not exist.
    """
    import json  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return []
    events: list[dict[str, object]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _scan_obpi_audit_logs(project_root: Path) -> list[dict[str, object]]:
    """Collect OBPI audit records from all ADR log directories.

    Scans ``docs/design/adr/**/logs/obpi-audit.jsonl`` for structured
    evidence records.
    """
    import json  # noqa: PLC0415

    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    records: list[dict[str, object]] = []
    for log_path in adr_root.rglob("obpi-audit.jsonl"):
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


# -- Proxy functions --------------------------------------------------------


def _governance_activity_proxy(
    _root: Path,
    events: list[dict[str, object]],
    _audits: list[dict[str, object]],
) -> tuple[str, str]:
    """Check for governance lifecycle events in the ledger."""
    governance_types = {"gate_checked", "attested", "audit_receipt_emitted", "obpi_receipt_emitted"}
    count = sum(1 for e in events if e.get("event") in governance_types)
    if count > 0:
        return "pass", f"{count} governance events found in ledger"
    return "fail", "No governance activity events in ledger"


def _test_evidence_proxy(
    _root: Path,
    _events: list[dict[str, object]],
    audits: list[dict[str, object]],
) -> tuple[str, str]:
    """Check OBPI audit logs for test evidence."""
    for rec in audits:
        raw_ev = rec.get("evidence")
        if not isinstance(raw_ev, dict):
            continue
        test_count = raw_ev.get("test_count")  # type: ignore[union-attr]
        tests_passed = raw_ev.get("tests_passed")  # type: ignore[union-attr]
        if isinstance(test_count, int) and test_count > 0 and tests_passed is True:
            return "pass", f"Audit shows {test_count} tests passing"
    if not audits:
        return "fail", "No OBPI audit records found"
    return "fail", "No passing test evidence in audit records"


def _evidence_quality_proxy(
    _root: Path,
    _events: list[dict[str, object]],
    audits: list[dict[str, object]],
) -> tuple[str, str]:
    """Check for substantive criteria evaluations in audit records."""
    for rec in audits:
        raw_ev = rec.get("evidence")
        if not isinstance(raw_ev, dict):
            continue
        criteria = raw_ev.get("criteria_evaluated")  # type: ignore[union-attr]
        if isinstance(criteria, list):
            passing = [c for c in criteria if isinstance(c, dict) and c.get("result") == "PASS"]
            if passing:
                return "pass", f"{len(passing)} criteria evaluated with PASS"
    if not audits:
        return "fail", "No OBPI audit records found"
    return "fail", "No substantive criteria evaluations found"


def _completion_quality_proxy(
    _root: Path,
    _events: list[dict[str, object]],
    audits: list[dict[str, object]],
) -> tuple[str, str]:
    """Check for completed OBPI brief transitions in audit records."""
    for rec in audits:
        if rec.get("brief_status_after") == "Completed":
            return "pass", "OBPI brief completed in audit trail"
    for rec in audits:
        if rec.get("action_taken") == "attestation_recorded":
            return "pass", "Attestation recorded in audit trail"
    if not audits:
        return "fail", "No OBPI audit records found"
    return "fail", "No completion transitions found in audit records"


def _plan_discipline_proxy(
    _root: Path,
    events: list[dict[str, object]],
    _audits: list[dict[str, object]],
) -> tuple[str, str]:
    """Check that ADR creation events precede gate checks."""
    adr_created_ts: list[str] = []
    gate_checked_ts: list[str] = []
    for e in events:
        ts = e.get("ts", "")
        if not isinstance(ts, str):
            continue
        if e.get("event") == "adr_created":
            adr_created_ts.append(ts)
        elif e.get("event") == "gate_checked":
            gate_checked_ts.append(ts)
    if not adr_created_ts:
        return "fail", "No ADR creation events found in ledger"
    if not gate_checked_ts:
        return "pass", "ADR created; no gate checks yet (plan-first discipline)"
    earliest_adr = min(adr_created_ts)
    earliest_gate = min(gate_checked_ts)
    if earliest_adr <= earliest_gate:
        return "pass", "ADR creation precedes first gate check"
    return "fail", "Gate checks occurred before ADR was created"


# -- Trait proxy registry ---------------------------------------------------

TRAIT_PROXY_REGISTRY: dict[str, tuple[str, TraitProxyFn]] = {
    "governance-aware": ("governance_activity", _governance_activity_proxy),
    "governance-fidelity": ("governance_activity", _governance_activity_proxy),
    "evidence-anchoring": ("governance_activity", _governance_activity_proxy),
    "test-first": ("test_evidence", _test_evidence_proxy),
    "thorough": ("test_evidence", _test_evidence_proxy),
    "architectural-rigor": ("test_evidence", _test_evidence_proxy),
    "evidence-driven": ("evidence_quality", _evidence_quality_proxy),
    "evidence-based-assessment": ("evidence_quality", _evidence_quality_proxy),
    "evidence-to-decision": ("evidence_quality", _evidence_quality_proxy),
    "precision": ("evidence_quality", _evidence_quality_proxy),
    "complete-units": ("completion_quality", _completion_quality_proxy),
    "atomic-edits": ("completion_quality", _completion_quality_proxy),
    "ceremony-completion": ("completion_quality", _completion_quality_proxy),
    "methodical": ("plan_discipline", _plan_discipline_proxy),
    "plan-then-write": ("plan_discipline", _plan_discipline_proxy),
    "stage-discipline": ("plan_discipline", _plan_discipline_proxy),
    "sequential-flow": ("plan_discipline", _plan_discipline_proxy),
}
"""Maps trait keywords to (proxy_name, proxy_function) pairs."""


def _check_trait(
    trait: str,
    project_root: Path,
    events: list[dict[str, object]],
    audits: list[dict[str, object]],
    *,
    is_anti_trait: bool = False,
) -> TraitCheckResult:
    """Evaluate a single trait against the proxy registry."""
    from gzkit.models.persona import TraitCheckResult  # noqa: PLC0415

    entry = TRAIT_PROXY_REGISTRY.get(trait)
    if entry is None:
        return TraitCheckResult(
            trait=trait,
            status="no_evidence",
            proxy="unmapped",
            detail=f"No behavioral proxy registered for '{trait}'",
            is_anti_trait=is_anti_trait,
        )
    proxy_name, proxy_fn = entry
    status, detail = proxy_fn(project_root, events, audits)
    if is_anti_trait and status == "pass":
        status = "pass"
        detail = f"(inverse) {detail}"
    elif is_anti_trait and status == "fail":
        status = "pass"
        detail = f"(inverse: anti-trait not evidenced) {detail}"
    return TraitCheckResult(
        trait=trait,
        status=status,
        proxy=proxy_name,
        detail=detail,
        is_anti_trait=is_anti_trait,
    )


def evaluate_persona_drift(
    project_root: Path,
    persona_name: str | None = None,
) -> PersonaDriftReport:
    """Evaluate trait adherence for one or all personas.

    Loads personas from ``.gzkit/personas/``, pre-scans ledger and audit
    artifacts once, then evaluates each persona's traits against the
    proxy registry.
    """
    import datetime  # noqa: PLC0415

    from gzkit.models.persona import (  # noqa: PLC0415
        PersonaDriftReport,
        PersonaDriftResult,
        discover_persona_files,
        parse_persona_file,
    )

    personas_dir = project_root / ".gzkit" / "personas"
    files = discover_persona_files(personas_dir)
    events = _scan_ledger_events(project_root)
    audits = _scan_obpi_audit_logs(project_root)

    results: list[PersonaDriftResult] = []
    for f in files:
        try:
            fm, _body = parse_persona_file(f)
        except ValueError:
            continue
        if persona_name is not None and fm.name != persona_name:
            continue
        checks: list[TraitCheckResult] = []
        for trait in fm.traits:
            checks.append(_check_trait(trait, project_root, events, audits))
        for anti_trait in fm.anti_traits:
            checks.append(
                _check_trait(anti_trait, project_root, events, audits, is_anti_trait=True)
            )
        has_drift = any(c.status == "fail" for c in checks)
        results.append(PersonaDriftResult(persona=fm.name, checks=checks, has_drift=has_drift))

    total_checks = sum(len(r.checks) for r in results)
    drift_count = sum(1 for r in results for c in r.checks if c.status == "fail")
    return PersonaDriftReport(
        personas=results,
        total_personas=len(results),
        total_checks=total_checks,
        drift_count=drift_count,
        scan_timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
    )


def render_persona_for_vendor(vendor: str, fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame for the given vendor.

    Looks up the vendor in ``VENDOR_ADAPTERS``.  If no adapter is registered,
    returns the raw canonical markdown as fallback (REQ-0.0.13-04-04).
    """
    adapter = VENDOR_ADAPTERS.get(vendor)
    if adapter is not None:
        return adapter(fm, body)
    return _rebuild_raw_persona(fm, body)
