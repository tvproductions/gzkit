"""Sensitivity-scope record walker for ``gz validate --sensitivity``.

Extracted from ``validate_cmd.py`` (the same A3 module split that produced
``validate_briefs.py``) so each validator cluster lives in a focused module.

The split line is rendering: this module owns the *pure* half — walking briefs
and producing records plus findings — while ``validate_cmd`` keeps
``_run_sensitivity_scope``, which renders those findings to ``console`` and
chooses the exit status. Keeping the console-writing half with the dispatcher
matters beyond taste: ``_POLICY_BREACH_ERROR_TYPES`` is dispatcher policy, and
tests patch ``validate_cmd.console`` by module attribute, so a renderer
relocated here would write to a console those patches never rebind.
"""

from pathlib import Path

from gzkit.validate import ValidationError


def _parse_sensitivity_path_list(raw: str) -> tuple[str, ...]:
    """Split comma- or newline-separated path lists into a tuple."""
    pieces: list[str] = []
    for chunk in raw.replace("\r", "\n").split("\n"):
        for piece in chunk.split(","):
            cleaned = piece.strip()
            if cleaned:
                pieces.append(cleaned)
    return tuple(pieces)


def _sensitivity_records(
    project_root: Path,
) -> tuple[list[dict[str, object]], list[ValidationError]]:
    """Walk briefs once and produce per-brief records + companion findings."""
    from gzkit.governance.brief_structure import is_terminal_brief_status  # noqa: PLC0415
    from gzkit.governance.trust_audits.sensitivity import (  # noqa: PLC0415
        _SENSITIVITY_REGISTRY_REL,
        _extract_sensitivity_allowed_paths,
        _iter_sensitivity_briefs,
        _load_floor_grandfather,
        _load_sensitivity_registry,
    )
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        _parse_adr_frontmatter,
    )
    from gzkit.models.security_surfaces import match_globs  # noqa: PLC0415

    findings: list[ValidationError] = []
    records: list[dict[str, object]] = []

    registry, registry_error = _load_sensitivity_registry(project_root)
    if registry_error is not None:
        findings.append(registry_error)
        return records, findings
    assert registry is not None  # noqa: S101

    grandfather = _load_floor_grandfather(project_root)

    for brief_path in _iter_sensitivity_briefs(project_root):
        try:
            brief_text = brief_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = brief_path.relative_to(project_root).as_posix()
        frontmatter = _parse_adr_frontmatter(brief_path) or {}

        # Terminal briefs are sealed historical records; the floor does not
        # re-gate them (GHI #682). Mirrors _classify_brief_sensitivity's skip so
        # the CLI --sensitivity path and audit_sensitivity_binding stay coherent.
        status = frontmatter.get("status")
        if isinstance(status, str) and is_terminal_brief_status(status):
            continue

        declared = frontmatter.get("sensitivity")
        declared_norm = declared.strip() or None if isinstance(declared, str) else None
        if declared_norm in {"None", "null", "~"}:
            declared_norm = None

        allowed_paths = _extract_sensitivity_allowed_paths(brief_text)
        try:
            matching_categories = match_globs(allowed_paths, registry)
        except (ValueError, TypeError):
            findings.append(
                ValidationError(
                    type="sensitivity-malformed-allowlist",
                    artifact=rel,
                    message="Allowed Paths contains an unparseable glob.",
                )
            )
            continue

        detected = "security" if matching_categories else None
        records.append(
            {
                "file": rel,
                "declared_sensitivity": declared_norm,
                "detected_sensitivity": detected,
                "intersecting_paths": allowed_paths,
                "registry_categories": list(matching_categories),
            }
        )

        if detected == "security" and declared_norm not in (None, "security"):
            findings.append(
                ValidationError(
                    type="sensitivity-escape-attempt",
                    artifact=rel,
                    message=(
                        f"declared={declared_norm!r} but detected=security; "
                        f"categories={list(matching_categories)}; "
                        f"intersecting_paths={allowed_paths}"
                    ),
                )
            )
        elif detected == "security" and declared_norm is None and rel not in grandfather:
            # Omission over a security overlap is fail-closed (GHI #625);
            # grandfathered briefs (pre-cutover) stay at the informational floor.
            findings.append(
                ValidationError(
                    type="sensitivity-floor-violation",
                    artifact=rel,
                    message=(
                        f"Brief omits sensitivity: while allowed paths intersect "
                        f"registered security surfaces (detected=security, "
                        f"categories={list(matching_categories)}, "
                        f"intersecting_paths={allowed_paths}). "
                        f".gzkit/rules/security-sensitivity.md §§ 1-2: omission over a "
                        f"security overlap is fail-closed. Declare 'sensitivity: security'; "
                        f"or if the overlap is an incidental false positive, narrow the "
                        f"Allowed Paths or discharge at completion via "
                        f"'gz obpi complete --accept-security-floor'."
                    ),
                )
            )

    # Surface the registry-rel for callers that want to cite it in human output.
    _ = _SENSITIVITY_REGISTRY_REL
    return records, findings
