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
    "adr fidelity": (
        "ADR-0.0.73 OBPI-03 delivers the `gz adr fidelity` gate. "
        "OBPI-04 (Closeout/audit repoint) wires it into the `gz-adr-closeout-ceremony` "
        "and `gz-adr-audit` skills; no separate wielding skill is needed before OBPI-04 lands."
    ),
    "mx enter": (
        "ADR-0.0.74 OBPI-04 delivers the `gz mx enter` command. "
        "The `gz-mx` skill (which will wield this verb) is a later ADR-0.0.74 deliverable; "
        "waiver holds until the skill lands."
    ),
    "obpi repudiate": (
        "Operator-invoked repair verb (ADR-0.0.71-completion-repudiation). "
        "No standalone skill — the action is one-shot operator-gated correction, "
        "not a recurring agent workflow. The `gz-obpi-reconcile` skill covers "
        "post-repudiation verification."
    ),
    "upgrade": (
        "Surface-only refresh verb (ADR-0.0.32 OBPI-14); the gz-deps-upgrade "
        "skill covers dependency upgrades; a dedicated gz-upgrade skill for "
        "canonical surface refresh is deferred post-ADR-0.0.32 closeout."
    ),
    "content": (
        "ADR-0.0.34 OBPI-04 delivers the content CLI surface as an agent-mediated "
        "dialogical authoring entry point; no separate wielding skill is in the "
        "eight-component delivery plan — the agent IS the authoring UI per ADR-0.0.34 § Decision."
    ),
    "governance": (
        "ADR-0.0.37 OBPI-0.0.37-02 delivers the `gz governance render` CLI surface. "
        "A dedicated gz-governance-render skill is deferred to a subsequent feature ADR "
        "once the full governance command group lands (OBPI-03 through OBPI-10)."
    ),
}


def _cli_alignment_sources(project_root: Path) -> list[Path]:
    """Enumerate every operator-facing surface that may carry ``gz <verb>`` strings."""
    sources: list[Path] = []
    features_root = project_root / "features"
    if features_root.is_dir():
        sources.extend(sorted(features_root.rglob("*.feature")))
    runbook = project_root / "docs" / "user" / "runbook.md"
    if runbook.is_file():
        sources.append(runbook)
    for sub in ("commands", "manpages"):
        candidate = project_root / "docs" / "user" / sub
        if candidate.is_dir():
            sources.extend(sorted(candidate.rglob("*.md")))
    return sources


def _collect_verb_references(sources: list[Path], project_root: Path) -> dict[str, list[str]]:
    """Return ``{verb: [<file:line>, …]}`` for every ``gz <verb>`` reference."""
    verbs_seen: dict[str, list[str]] = {}
    for source in sources:
        for lineno, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            rel = f"{source.relative_to(project_root).as_posix()}:{lineno}"
            for pattern in (_BACKTICKED_INVOCATION, _QUOTED_INVOCATION, _STEP_DEF_FIXTURE):
                for match in pattern.finditer(line):
                    verbs_seen.setdefault(match.group(1), []).append(rel)
    return verbs_seen


def audit_cli_alignment(project_root: Path) -> list[ValidationError]:
    """Enforce `.gzkit/rules/governance-core.md` § Operator-doc verb resolution (GHI #198)."""
    sources = _cli_alignment_sources(project_root)
    verbs_seen = _collect_verb_references(sources, project_root)
    known_verbs = _known_cli_verbs()
    errors: list[ValidationError] = []
    for verb, locations in sorted(verbs_seen.items()):
        if verb in _DOC_PROSE_VERBS or verb in known_verbs:
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


def _verb_referenced_in_skill(verb: str, content: str) -> bool:
    """Return ``True`` if the SKILL.md content invokes or names the verb."""
    escaped = re.escape(verb)
    if re.search(rf"\bgz\s+{escaped}\b", content):
        return True
    return bool(re.search(rf"gz_command:\s*{escaped}\b", content))


def _collect_skill_verb_refs(
    skills_root: Path, known_verbs: frozenset[str], project_root: Path
) -> dict[str, set[str]]:
    """Return ``{verb: {skill-rel-path, …}}`` for every verb referenced by a skill."""
    refs: dict[str, set[str]] = {verb: set() for verb in known_verbs}
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            content = skill_md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = skill_md.relative_to(project_root).as_posix()
        for verb in known_verbs:
            if _verb_referenced_in_skill(verb, content):
                refs[verb].add(rel)
    return refs


def _known_cli_verb_paths() -> frozenset[str]:
    """Return every registered leaf command path, recursing into nested subparsers.

    Unlike :func:`_known_cli_verbs` (top-level choices only), this walks the
    full argparse tree and returns space-joined leaf paths — e.g. ``"state"``,
    ``"adr status"``, ``"obpi lock claim"``. Invariant 1 enforces against this
    full surface so multi-word subcommands cannot pass the orphan check by
    invisibility (GHI #588).
    """
    import argparse  # noqa: PLC0415

    from gzkit.cli.main import _build_parser  # noqa: PLC0415

    def _subaction(parser):
        for action in parser._actions:  # noqa: SLF001 — argparse provides no public API
            if isinstance(action, argparse._SubParsersAction):
                return action
        return None

    def _walk(parser, prefix: str) -> set[str]:
        sub = _subaction(parser)
        if sub is None:
            return {prefix} if prefix else set()
        leaves: set[str] = set()
        for name, subparser in sub.choices.items():
            leaves |= _walk(subparser, f"{prefix} {name}".strip())
        return leaves

    return frozenset(_walk(_build_parser(), ""))


def _verb_path_waived(path: str) -> bool:
    """A verb path is waived by an exact entry or by a top-level group key.

    Group keys (e.g. ``"task"``) cascade to every subcommand beneath them —
    they declare the whole namespace intentionally skill-less.
    """
    return path in _NO_SKILL_VERBS or path.split(" ", 1)[0] in _NO_SKILL_VERBS


def _waiver_targets_live_verb(key: str, verb_paths: frozenset[str]) -> bool:
    """Return ``True`` if a waiver key still names a registered verb or group."""
    return any(p == key or p.startswith(f"{key} ") for p in verb_paths)


def audit_skill_alignment(project_root: Path) -> list[ValidationError]:
    """Invariant 1: every registered CLI verb is referenced by at least one skill.

    Scans ``.gzkit/skills/**/SKILL.md`` (authored source) frontmatter
    (``gz_command:``) and body prose for each registered CLI verb path —
    including multi-word subcommands (``gz obpi complete``, ``gz adr status``),
    not just top-level verbs (GHI #588). A verb with no wielding skill and no
    explicit (or group-cascading) waiver is a defect signal per
    ``.gzkit/rules/tool-skill-runbook-alignment.md``.
    """
    skills_root = project_root / ".gzkit" / "skills"
    if not skills_root.is_dir():
        return []
    verb_paths = _known_cli_verb_paths()

    verb_refs = _collect_skill_verb_refs(skills_root, verb_paths, project_root)

    errors: list[ValidationError] = []
    for path in sorted(verb_paths):
        if _verb_path_waived(path) or verb_refs[path]:
            continue
        errors.append(
            ValidationError(
                type="skill_alignment",
                artifact=f"gz {path}",
                message=(
                    f"CLI verb `gz {path}` has no wielding skill under "
                    ".gzkit/skills/**. Author a skill or add an entry to "
                    "`_NO_SKILL_VERBS` with rationale (tool-skill-runbook Invariant 1)."
                ),
            )
        )
    for stale in sorted(k for k in _NO_SKILL_VERBS if not _waiver_targets_live_verb(k, verb_paths)):
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
