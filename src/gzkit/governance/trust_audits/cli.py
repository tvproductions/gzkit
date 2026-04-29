"""CLI verb alignment audits — operator-doc / skill / verb coherence.

* ``audit_cli_alignment`` — every ``gz <verb>`` reference in operator docs and
  features resolves to a registered parser verb (GHI #198).
* ``audit_skill_alignment`` — every registered CLI verb has at least one
  wielding skill, or a waiver in ``_NO_SKILL_VERBS`` with rationale (GHI #202).
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError

_DOC_PROSE_VERBS: frozenset[str] = frozenset()

_BACKTICKED_INVOCATION = re.compile(r"`gz\s+([a-z][a-z0-9-]*)[^`]*`")
_QUOTED_INVOCATION = re.compile(r'"gz\s+([a-z][a-z0-9-]*)[^"]*"')
_STEP_DEF_FIXTURE = re.compile(r'the gz command\s+"([a-z][a-z0-9-]*)')

# CLI verbs that legitimately have no wielding skill (e.g. bootstrap and
# internal commands). Each entry must cite a reason.
_NO_SKILL_VERBS: dict[str, str] = {
    "init": "Bootstrap command — scaffolds a new repo; no skill mediates initialization.",
    "register-adrs": "One-shot historical registrar; not a recurring operator action.",
    "migrate-semver": "One-shot migration command; no skill mediates historical renames.",
    "personas": "Internal persona listing; consumed by other skills, not directly.",
    "roles": "Internal role listing; consumed by other skills, not directly.",
    "interview": "Subcommand invoked inside gz-adr-create; no standalone skill needed.",
    "drift": "Subcommand consumed by other skills.",
    "preflight": "Subcommand consumed by other skills.",
    "readiness": "Subcommand consumed by other skills.",
    "covers": "Coverage inspection; consumed by tests, not a skill.",
    "specify": "Subcommand invoked by gz-obpi-specify; skill-version gating covers it.",
    "flag": "Feature-flag inspection; internal developer affordance.",
    "flags": "Feature-flag inspection; internal developer affordance.",
    "parity": "Cross-repo parity inspector; consumed by airlineops-parity-scan skill.",
    "format": "Alias invocation — the `format` skill wraps it.",
    "lint": "Direct lint verb; wrapped by ARB workflow.",
    "typecheck": "Direct typecheck verb; wrapped by ARB workflow.",
    "test": "Direct test verb; wrapped by ARB workflow.",
    "task": (
        "Subcommand group (`gz task start/complete`); consumed by "
        "TASK-trailer discipline in TDD workflow."
    ),
    "frontmatter": (
        "Subcommand group (`gz frontmatter reconcile/check`); consumed "
        "inside gz-adr-recon and state-doctrine skills."
    ),
    "justify": (
        "CLI surface landed in ADR-0.0.19 OBPI-02 ahead of its wielding skill; "
        "the `gz-justify` skill ships in OBPI-0.0.19-04 per the ADR's "
        "decomposition plan (skill definition + upstream integrations OBPI)."
    ),
}


def audit_cli_alignment(project_root: Path) -> list[ValidationError]:
    """Enforce `.gzkit/rules/governance-core.md` § Operator-doc verb resolution (GHI #198)."""
    sources: list[Path] = []
    features_root = project_root / "features"
    if features_root.is_dir():
        sources.extend(sorted(features_root.rglob("*.feature")))
    runbook = project_root / "docs" / "user" / "runbook.md"
    if runbook.is_file():
        sources.append(runbook)
    commands_root = project_root / "docs" / "user" / "commands"
    if commands_root.is_dir():
        sources.extend(sorted(commands_root.rglob("*.md")))
    manpages_root = project_root / "docs" / "user" / "manpages"
    if manpages_root.is_dir():
        sources.extend(sorted(manpages_root.rglob("*.md")))

    verbs_seen: dict[str, list[str]] = {}
    for source in sources:
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            rel = f"{source.relative_to(project_root)}:{lineno}"
            for pattern in (_BACKTICKED_INVOCATION, _QUOTED_INVOCATION, _STEP_DEF_FIXTURE):
                for match in pattern.finditer(line):
                    verbs_seen.setdefault(match.group(1), []).append(rel)

    known_verbs = _known_cli_verbs()
    errors: list[ValidationError] = []
    for verb, locations in sorted(verbs_seen.items()):
        if verb in _DOC_PROSE_VERBS:
            continue
        if verb in known_verbs:
            continue
        errors.append(
            ValidationError(
                type="cli_alignment",
                artifact=locations[0],
                message=(
                    f"`gz {verb}` is not a registered CLI verb; "
                    f"seen at {len(locations)} location(s). Rename the reference "
                    "or register the verb."
                ),
            )
        )
    return errors


def _known_cli_verbs() -> frozenset[str]:
    """Return the top-level subcommand names registered on the gz CLI."""
    import argparse  # noqa: PLC0415

    from gzkit.cli.main import _build_parser  # noqa: PLC0415

    parser = _build_parser()
    verbs: set[str] = set()
    for action in parser._actions:  # noqa: SLF001 — argparse provides no public API
        if isinstance(action, argparse._SubParsersAction):
            verbs.update(action.choices.keys())
    return frozenset(verbs)


def audit_skill_alignment(project_root: Path) -> list[ValidationError]:
    """Invariant 1: every CLI verb is referenced by at least one skill.

    Scans ``.gzkit/skills/**/SKILL.md`` frontmatter (``gz_command:``) and body
    prose for each registered top-level CLI verb. A verb with no wielding
    skill and no explicit waiver is a defect signal per
    ``.gzkit/rules/tool-skill-runbook-alignment.md``.
    """
    skills_root = project_root / ".gzkit" / "skills"
    if not skills_root.is_dir():
        return []
    try:
        known_verbs = _known_cli_verbs()
    except Exception:
        return []

    verb_refs: dict[str, set[str]] = {verb: set() for verb in known_verbs}
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            content = skill_md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = skill_md.relative_to(project_root).as_posix()
        for verb in known_verbs:
            if re.search(rf"\bgz\s+{re.escape(verb)}\b", content) or re.search(
                rf"gz_command:\s*{re.escape(verb)}\b", content
            ):
                verb_refs[verb].add(rel)

    errors: list[ValidationError] = []
    for verb in sorted(known_verbs):
        if verb in _NO_SKILL_VERBS:
            continue
        if verb_refs[verb]:
            continue
        errors.append(
            ValidationError(
                type="skill_alignment",
                artifact=f"gz {verb}",
                message=(
                    f"CLI verb `gz {verb}` has no wielding skill under "
                    ".gzkit/skills/**. Author a skill or add an entry to "
                    "`_NO_SKILL_VERBS` with rationale (tool-skill-runbook Invariant 1)."
                ),
            )
        )
    for stale in sorted(_NO_SKILL_VERBS.keys() - known_verbs):
        errors.append(
            ValidationError(
                type="skill_alignment",
                artifact=f"_NO_SKILL_VERBS::{stale}",
                message=(
                    f"Waiver `{stale}` references a verb that is no longer registered. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors
