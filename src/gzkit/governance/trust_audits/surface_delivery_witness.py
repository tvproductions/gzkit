"""Surface-delivery witness for per-turn agent-contract surfaces (GHI #712).

Rendered root ``AGENTS.md`` was measured 560 B below Codex's 32,768 B
``project_doc_max_bytes`` with ``uv run gz check`` green. Past that offset the
bytes are not delivered to the agent **at all** under Codex
(openai/codex#7138) — silently. Nothing observed that distance: the operator
ruling of 2026-07-06 decoupled gzkit's own budget ceiling from the vendor cap
(correct hexagonal doctrine — an adapter limit must not gate the core
contract), but decoupling the *ceiling* is not the same as having visibility
into whether the *rendered artifact* has crossed it.

This module supplies the missing observer, in two deliberately different
severities:

* **Warning, never fail-closed** for anything measured against a vendor's cap.
  Gating there would re-couple the core to the adapter limit the 2026-07-06
  ruling decoupled. :class:`ValidationError` carries no severity field and
  ``gz validate`` treats every returned entry as exit-code-changing, so a
  non-gating finding must be emitted as a side effect rather than returned —
  the rule stated in :mod:`gzkit.governance.trust_audits.complexity_thresholds`.
* **Fail-closed** for incoherence between the rendered surface and the
  operator-ratified survival declaration in
  ``data/agents_md_survival_declaration.json``. That declaration is gzkit's own
  artifact, so gating on it couples nothing to any vendor. Without this arm a
  newly authored section would silently inherit an undeclared survival rank,
  and the ranking the witness checks against would rot.

The declaration is the operator's ratified answer (GHI #580, 2026-07-25) to
*which sections must survive truncation*, ordered by RECOVERABILITY: pointers
an agent can chase rank below canon that exists nowhere else in the per-turn
surface.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.advisory import emit_advisory
from gzkit.content.parse import section_id
from gzkit.content.vendors import delivery_cap_for, routes_for
from gzkit.validate import ValidationError

_DECLARATION_REL = Path("data") / "agents_md_survival_declaration.json"
_TYPE = "surface_delivery_witness"
_PREFIX = "[surface-delivery-witness]"
_DECLARATION_REMEDIATION = (
    "The survival declaration ranks every rendered section for truncation "
    f"survival; an id present on one side only leaves a rank pointing at "
    f"nothing or a section with no rank. Reconcile {_DECLARATION_REL.as_posix()} "
    "with the rendered headings in the same patch (GHI #712 / GHI #580)."
)
_DELIVERY_REMEDIATION = (
    "A vendor-limit exceedance is TRACKED, never blocking (operator ruling "
    "2026-08-17: 'when we exceed vendor limits, ghi it so it doesn't block'). "
    "If no OPEN GHI covers this surface's exceedance, file one via "
    "`/ghi-author`, whose Step 0 prior-art sweep resolves the current record "
    "and reopens a recent same-cause close rather than duplicating it. This "
    "prose names no issue number on purpose: a transcribed record is a state "
    "claim that goes stale under the string, so resolve before citing, never "
    "assume. The two remedies both have registered homes and neither lands "
    "in-session: shrink the surface (`uv run gz chores show "
    "instructions-files-diet`) or re-rank so must-survive sections render "
    "first (`ADR-pool.render-order-truncation-survival`, the reorder half). "
    "Raising the configured budget does NOT help — the cap "
    "belongs to the vendor, not to gzkit, and no gzkit ruling can stay it."
)


def _rendered_sections(surface: Path) -> list[tuple[str, int]]:
    """Return ``(section id, byte offset of its heading)`` in document order."""
    sections: list[tuple[str, int]] = []
    offset = 0
    for line in surface.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("## "):
            sections.append((section_id(line.strip()[3:]), offset))
        offset += len(line.encode("utf-8"))
    return sections


def _finding(relpath: str, message: str) -> ValidationError:
    return ValidationError(type=_TYPE, artifact=relpath, message=message)


def _declaration_errors(
    relpath: str, declared: list[dict], cut_line: object, rendered_ids: list[str]
) -> list[ValidationError]:
    """Fail-closed coherence between the declaration and the rendered surface."""
    errors: list[ValidationError] = []
    ranks = [entry.get("rank") for entry in declared]
    if sorted(r for r in ranks if isinstance(r, int)) != list(range(1, len(declared) + 1)):
        errors.append(
            _finding(
                relpath,
                f"survival ranks are not the contiguous sequence 1..{len(declared)}: "
                f"{ranks}. A gapped or duplicated rank sequence makes the "
                "must-survive cut line unresolvable. " + _DECLARATION_REMEDIATION,
            )
        )
    if not isinstance(cut_line, int) or not 1 <= cut_line <= len(declared):
        errors.append(
            _finding(
                relpath,
                f"must_survive_through_rank {cut_line!r} is outside the declared "
                f"range 1..{len(declared)}. " + _DECLARATION_REMEDIATION,
            )
        )
    declared_ids = [entry.get("id") for entry in declared]
    for missing in sorted(set(rendered_ids) - set(declared_ids)):
        errors.append(
            _finding(
                relpath,
                f"rendered section {missing!r} is absent from the survival "
                "declaration, so it carries no survival rank. " + _DECLARATION_REMEDIATION,
            )
        )
    for stale in sorted(str(i) for i in set(declared_ids) - set(rendered_ids)):
        errors.append(
            _finding(
                relpath,
                f"declared section {stale!r} no longer renders in the surface, so "
                "its survival rank is dangling. " + _DECLARATION_REMEDIATION,
            )
        )
    return errors


def _warn(message: str) -> None:
    emit_advisory(f"WARNING {_PREFIX} {message}")


def _observe_delivery(
    project_root: Path,
    relpath: str,
    content_type: str,
    rendered: list[tuple[str, int]],
    must_survive: set[str],
) -> None:
    """Emit the byte-distance observation. Never fail-closed (2026-07-06 ruling)."""
    surface_bytes = len((project_root / relpath).read_bytes())
    for vendor in routes_for(content_type, project_root=project_root):
        cap = delivery_cap_for(content_type, vendor, project_root=project_root)
        if cap is None:
            continue
        if surface_bytes <= cap:
            emit_advisory(
                f"NOTE {_PREFIX} {relpath}: {surface_bytes} B rendered against the "
                f"{vendor} delivery cap {cap} B — {cap - surface_bytes} B of headroom."
            )
        else:
            _warn(
                f"{relpath}: {surface_bytes} B rendered against the {vendor} delivery "
                f"cap {cap} B — {surface_bytes - cap} B OVER. Bytes past the cap are "
                f"not delivered to the agent at all under {vendor}, so content there "
                f"is silently absent rather than merely late. {_DELIVERY_REMEDIATION}"
            )
        # Survival is about the whole section, not its heading. A section whose
        # heading sits under the cap while its body runs past it is truncated
        # just as completely as one that begins past it, and asking only about
        # the offset cannot see that case — which is the case the committed
        # tree actually hits.
        for index, (name, offset) in enumerate(rendered):
            if name not in must_survive:
                continue
            end = rendered[index + 1][1] if index + 1 < len(rendered) else surface_bytes
            if end <= cap:
                continue
            placement = (
                f"begins at byte {offset}, past"
                if offset >= cap
                else f"begins at byte {offset} but runs to {end}, straddling"
            )
            _warn(
                f"{relpath}: section {name!r} is declared must-survive but "
                f"{placement} the {vendor} delivery cap {cap} B — at "
                f"risk of silent loss. A declared-unrecoverable section that is "
                f"not delivered is not in force (AGENTS.md § Behavior Rules — "
                f"Always #4). {_DELIVERY_REMEDIATION}"
            )


def _audit_surface(project_root: Path, relpath: str, entry: object) -> list[ValidationError]:
    surface = project_root / relpath
    sections = entry.get("sections") if isinstance(entry, dict) else None
    if not isinstance(entry, dict) or not isinstance(sections, list):
        return [
            _finding(
                relpath,
                f"survival declaration entry is malformed. {_DECLARATION_REMEDIATION}",
            )
        ]
    if not surface.is_file():
        return [
            _finding(
                relpath,
                "surface carries a survival declaration but does not exist on disk. "
                + _DECLARATION_REMEDIATION,
            )
        ]
    declared: list[dict] = [s for s in sections if isinstance(s, dict)]
    rendered = _rendered_sections(surface)
    cut_line = entry.get("must_survive_through_rank")
    errors = _declaration_errors(relpath, declared, cut_line, [name for name, _ in rendered])
    if errors:
        return errors
    must_survive = {
        str(s["id"]) for s in declared if isinstance(s.get("rank"), int) and s["rank"] <= cut_line
    }
    _observe_delivery(
        project_root, relpath, str(entry.get("content_type", "")), rendered, must_survive
    )
    return []


def audit_surface_delivery_witness(project_root: Path) -> list[ValidationError]:
    """Witness that declared must-survive canon still arrives at its consumer.

    Returns fail-closed findings for declaration/surface incoherence only.
    Vendor-cap distance is reported to stderr and never changes the exit code.
    A project with no declaration is silently unaffected.
    """
    declaration_path = project_root / _DECLARATION_REL
    relpath = _DECLARATION_REL.as_posix()
    if not declaration_path.is_file():
        return []
    try:
        payload = json.loads(declaration_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_finding(relpath, f"survival declaration is not valid JSON: {exc}.")]
    surfaces = payload.get("surfaces") if isinstance(payload, dict) else None
    if not isinstance(surfaces, dict):
        return [_finding(relpath, "survival declaration has no `surfaces` mapping.")]
    errors: list[ValidationError] = []
    for surface_relpath, entry in sorted(surfaces.items()):
        errors.extend(_audit_surface(project_root, str(surface_relpath), entry))
    return errors
