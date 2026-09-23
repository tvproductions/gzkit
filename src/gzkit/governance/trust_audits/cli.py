"""CLI verb alignment audits — operator-doc / skill / verb coherence.

* ``audit_cli_alignment`` — every ``gz <verb>`` reference in operator docs and
  features resolves to a registered parser verb (GHI #198).
* ``audit_skill_alignment`` — every registered CLI verb has at least one
  wielding skill, or a waiver in ``_NO_SKILL_VERBS`` with rationale (GHI #202).
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.governance.brief_structure import is_terminal_brief_status
from gzkit.governance.deprecations import find_deprecated_verb
from gzkit.validate import ValidationError
from gzkit.verb_references import (
    DOC_BARE_SEGMENTS,
    DOC_SEGMENTS,
    SPECULATIVE_MARKER,
    extract_verb_references,
    verify_gz_chain,
)

_DOC_PROSE_VERBS: frozenset[str] = frozenset()

# Manpages live at docs/user/manpages/<verb>.md — never with a gz- prefix. A
# reference to manpages/gz-<verb>.md is a dead operator-doc pointer using a
# convention no manpage file uses (GHI #532).
_MANPAGE_GZ_PREFIX_REF = re.compile(r"manpages/(gz-[a-z0-9-]+\.md)")
#: Skill prose citing a gzkit implementation module (GHI #896). Existence only —
#: whether the prose still describes the code is a reading, not a state.
_SRC_MODULE_REF = re.compile(r"src/gzkit/[a-z0-9_/]+\.py")
_BRIEF_STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)
_ADR_PACKAGE_MARKER = "design/adr"

# Ceremony artifacts inside an ADR package that record what was true at audit or
# closeout time. Sealed on the same ground as a terminal brief (GHI #532).
_SEALED_ADR_ARTIFACTS: frozenset[str] = frozenset(
    {"EVALUATION_SCORECARD.md", "EVALUATION_SUBSTANCE.md", "ADR-CLOSEOUT-FORM.md"}
)

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
    "obpi repudiate": (
        "Operator-invoked repair verb (ADR-0.0.71-completion-repudiation). "
        "No standalone skill — the action is one-shot operator-gated correction, "
        "not a recurring agent workflow. The `gz-obpi-sync` skill covers "
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
    "knowledge generate": (
        "ADR-0.30.0 OBPI-0.30.0-04 delivers the `gz knowledge generate/refresh` CLI surface "
        "for OKF bundle generation. No dedicated wielding skill — operator invokes directly "
        "as part of governance documentation maintenance workflow."
    ),
    "knowledge refresh": (
        "ADR-0.30.0 OBPI-0.30.0-04 delivers the `gz knowledge generate/refresh` CLI surface "
        "for OKF bundle generation. No dedicated wielding skill — operator invokes directly "
        "as part of governance documentation maintenance workflow."
    ),
}


def _cli_alignment_sources(project_root: Path) -> list[Path]:
    """Enumerate every operator-facing surface that may carry ``gz <verb>`` strings.

    Tracks `AGENTS.md` § Governance doctrine surfaces (operator-doc verb resolution),
    which declares ``docs/**/*.md``, ``features/**/*.feature`` and
    ``.gzkit/skills/**/SKILL.md``. This function used to enumerate four
    directories under ``docs/user`` instead, so the rest of the declared field
    was never opened — the enumeration WAS the blind spot, the same derivation
    error as scoping an allowlist by its examples rather than its obligation
    (GHI #745).

    ``docs/releases/`` is excluded at enumeration, matching
    :func:`_manpage_alignment_sources`: ``gz patch release`` renders one manifest
    row per discovered GHI from that issue's title, so an issue *about* a dead
    verb carries the string as quoted evidence rather than as a pointer.

    ``docs/reports/`` is excluded on the same ground. ``gz report publish`` retains
    immutable assessments whose bytes are witnessed by a ``report_published``
    sha256, and their prose quotes versions and verbs as evidence of what was true
    at a moment. They are sealed records in the :func:`_is_exempt_source` sense, so
    the speculative marker is unavailable by construction: applying it would mean
    *editing* witnessed bytes, which breaks the witness every later publication
    verifies (GHI #532 precedent, same reasoning as the terminal-brief exemption).

    The surfaces an agent executes from are read too: chore docs (``gz-chore-runner``
    Step 5 follows a CHORE.md), rules, and the root ``AGENTS.md`` (GHI #1006).
    A chore's ``proofs/`` are run records and stay out, like ``docs/releases/``.
    """
    sources: list[Path] = []
    docs_root = project_root / "docs"
    if docs_root.is_dir():
        retained_roots = (docs_root / "releases", docs_root / "reports")
        sources.extend(
            path
            for path in sorted(docs_root.rglob("*.md"))
            if not any(root in path.parents for root in retained_roots)
        )
    features_root = project_root / "features"
    if features_root.is_dir():
        sources.extend(sorted(features_root.rglob("*.feature")))
    skills_root = project_root / ".gzkit" / "skills"
    if skills_root.is_dir():
        sources.extend(sorted(skills_root.rglob("SKILL.md")))
    chores_root = project_root / ".gzkit" / "chores"
    if chores_root.is_dir():
        sources.extend(
            path
            for path in sorted(chores_root.rglob("*.md"))
            if "proofs" not in path.relative_to(chores_root).parts
        )
    rules_root = project_root / ".gzkit" / "rules"
    if rules_root.is_dir():
        sources.extend(sorted(rules_root.rglob("*.md")))
    agent_contract = project_root / "AGENTS.md"
    if agent_contract.is_file():
        sources.append(agent_contract)
    return sources


def _is_exempt_source(path: Path, text: str) -> bool:
    """Return ``True`` for artifacts whose unresolvable verbs are not defects.

    Two exemption grounds, both structural — never a per-reference judgment:

    * **Pool ADRs** (operator ruling, 2026-08-02). Describing a proposed CLI
      surface is what a pool ADR is FOR, so its verbs are unregistered by
      definition rather than by mistake. 530 sites across 79 files.
    * **Sealed records** — terminal briefs, ADR-package ``audit/`` artifacts,
      evaluation scorecards, and closeout forms. These are evidence of what was
      true at a moment. Marking them speculative would mean *editing* them, and
      a later hand reaching into a sealed record is the defect the terminal-brief
      exemption already exists to prevent (GHI #532 precedent).

    ``Superseded`` needs no separate arm: it is already a member of
    ``BRIEF_TERMINAL_STATUSES``, so the terminal check covers the
    "self-declared SUPERSEDED docs" class GHI #745 proposed as a third exemption.

    Everything outside these classes carries the speculative marker instead —
    explicit, greppable, and removed by whoever lands the verb.
    """
    posix = path.as_posix()
    if "design/adr/pool/" in posix:
        return True
    if _ADR_PACKAGE_MARKER not in posix:
        return False
    if "/audit/" in posix or path.name in _SEALED_ADR_ARTIFACTS:
        return True
    status_match = _BRIEF_STATUS_RE.search(text)
    return bool(status_match and is_terminal_brief_status(status_match.group(1)))


def _collect_verb_references(
    sources: list[Path], project_root: Path
) -> dict[tuple[str, ...], list[str]]:
    """Return ``{verb-chain: [<file:line>, …]}`` for every ``gz <verb>`` reference.

    Delegates to the shared extractor in :mod:`gzkit.verb_references` (GHI #748).
    This function previously reimplemented that extraction — without multi-word
    chains, without the speculative-skip marker, and (before GHI #745) without
    fenced blocks — while guarding the wider surface of the two call sites.
    """
    references: dict[tuple[str, ...], list[str]] = {}
    for source in sources:
        try:
            content = source.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if _is_exempt_source(source, content):
            continue
        rel_path = source.relative_to(project_root).as_posix()
        for ref in extract_verb_references(
            content, segments=DOC_SEGMENTS, bare_segments=DOC_BARE_SEGMENTS
        ):
            references.setdefault(ref.chain, []).append(f"{rel_path}:{ref.lineno}")
    return references


def audit_cli_alignment(project_root: Path) -> list[ValidationError]:
    """Enforce `AGENTS.md` § Governance doctrine surfaces, verb resolution (GHI #198).

    Resolution walks the live parser tree via
    :func:`gzkit.verb_references.verify_gz_chain`, so a multi-word reference is
    checked at every level — ``gz adr bogus`` no longer passes because its first
    token is registered (GHI #588 / #748). Trailing positional arguments after a
    leaf verb resolve; unregistered intermediate verbs fail closed.
    """
    from gzkit.governance.trust_audits.lifecycle_pointers import (  # noqa: PLC0415
        audit_lifecycle_pointers,
    )

    sources = _cli_alignment_sources(project_root)
    references = _collect_verb_references(sources, project_root)
    # Second arm, same family (GHI #846): a doc naming a verb that does not
    # resolve and a skill claiming a pending step from a terminal ADR are the
    # same class of unresolvable pointer. It rides this scope rather than its
    # own because `validate_cmd.py` is grandfathered at its ceiling and the
    # grandfather list is shrink-only, so no new scope can be registered there.
    errors: list[ValidationError] = audit_lifecycle_pointers(project_root)
    for chain, locations in sorted(references.items()):
        if chain[0] in _DOC_PROSE_VERBS:
            continue
        ok, reason = verify_gz_chain(chain)
        if ok:
            continue
        errors.append(
            ValidationError(
                type="cli_alignment",
                artifact=locations[0],
                message=(
                    f"`gz {' '.join(chain)}` does not resolve: {reason}. "
                    f"Seen at {len(locations)} location(s). Rename the reference, "
                    f"register the verb, or mark it speculative with "
                    f"`{SPECULATIVE_MARKER}` on the preceding line."
                ),
            )
        )
    return errors


def _manpage_alignment_sources(project_root: Path) -> list[Path]:
    """Operator-doc surfaces that may carry ``manpages/<verb>.md`` references.

    ``AGENTS.md`` § Governance doctrine surfaces declares
    one scope for both bindings, so this reads the enumeration
    :func:`_cli_alignment_sources` owns — ADR/OBPI briefs included, where the
    gz-<verb>.md convention drift accumulated; terminal briefs are filtered by
    the caller. It used to be a copy of that enumeration, which is how the two
    would drift the moment one widened (GHI #1006).
    """
    return _cli_alignment_sources(project_root)


def audit_manpage_alignment(project_root: Path) -> list[ValidationError]:
    """Fail closed on operator-doc references to the non-existent ``manpages/gz-<verb>.md``.

    Manpages live at ``docs/user/manpages/<verb>.md``; no manpage file uses a
    ``gz-`` prefix. A ``manpages/gz-<verb>.md`` reference is therefore always a
    dead pointer — the same class of defect as an unresolvable ``gz <verb>``
    reference (``AGENTS.md`` § Governance doctrine surfaces, verb
    resolution). The recovery is unconditional: drop the ``gz-`` prefix (a
    planned-but-unlanded manpage still uses ``<verb>.md``), so the check needs no
    speculative-marker escape. Terminal OBPI briefs are exempt — their
    references are sealed historical records (GHI #532), scoped via the same
    :func:`is_terminal_brief_status` predicate ``--brief-command-shape`` and the
    ``--sensitivity`` floor use.
    """
    errors: list[ValidationError] = []
    for source in _manpage_alignment_sources(project_root):
        try:
            text = source.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if _ADR_PACKAGE_MARKER in source.as_posix():
            status_match = _BRIEF_STATUS_RE.search(text)
            if status_match and is_terminal_brief_status(status_match.group(1)):
                continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in _MANPAGE_GZ_PREFIX_REF.finditer(line):
                bad = match.group(1)
                errors.append(
                    ValidationError(
                        type="manpage_alignment",
                        artifact=f"{source.relative_to(project_root).as_posix()}:{lineno}",
                        message=(
                            f"`manpages/{bad}` uses the non-existent gz- prefixed manpage "
                            f"convention; manpages live at {MANPAGE_DIR.as_posix()}/<verb>.md. "
                            f"Drop the gz- prefix (-> manpages/{bad[3:]}). "
                            f"(AGENTS.md § Governance doctrine surfaces; GHI #532.)"
                        ),
                    )
                )
    return errors


def audit_skill_code_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on skill prose citing a ``src/gzkit/`` module that does not exist.

    This function walks the same ``.gzkit/skills/**/SKILL.md`` surface as
    :func:`audit_cli_alignment` and :func:`audit_manpage_alignment`, which resolve
    the ``gz <verb>`` strings a skill NAMES and the manpage filenames it POINTS AT.
    Neither read the implementation a skill DESCRIBES, so a rename or a
    module-to-package split left the pointer rotting with nothing objecting
    (GHI #896). Measured before this arm existed: three cited paths did not
    resolve across seven skills, and ``uv run gz check`` was green.

    The class is the one ``AGENTS.md`` § DO IT RIGHT 1a names from the other side —
    a skill citing ``src/gzkit/<module>.py`` is a CONSUMER of that module's path,
    and nothing verified the consumer when the surface moved. Its canonical
    instance is GHI #884's origin: ``69bc4a84`` mandated the Codex plugin as the
    only tier-1 dispatch surface and, in the same commit, left the prose
    describing that gate claiming the proof was ``step.command[0]``.

    Scope is the EXISTENCE half only, deliberately. Whether prose still describes
    what the code DOES is a reading, not a state gzkit models; whether a cited
    path resolves is mechanical, and it is the half that measured 3-for-3 wrong.
    Non-``src/gzkit`` paths are out of scope for the same reason — widening
    without measuring is how a checklist comes to undercount its obligations
    (GHI #854).
    """
    errors: list[ValidationError] = []
    skills_root = project_root / ".gzkit" / "skills"
    if not skills_root.is_dir():
        return errors
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in _SRC_MODULE_REF.finditer(line):
                relpath = match.group(0)
                if (project_root / relpath).is_file():
                    continue
                package = project_root / relpath[: -len(".py")]
                recovery = (
                    f"It is now the package {relpath[: -len('.py')]}/ — cite that, or the "
                    "specific module inside it."
                    if package.is_dir()
                    else "Cite the module that replaced it, or drop the pointer."
                )
                errors.append(
                    ValidationError(
                        type="skill_code_citation",
                        artifact=(f"{skill_md.relative_to(project_root).as_posix()}:{lineno}"),
                        message=(
                            f"`{relpath}` does not exist, so this skill points an agent at "
                            f"a module that is not there. {recovery} "
                            "(GHI #896; AGENTS.md § DO IT RIGHT 1a.)"
                        ),
                    )
                )
    return errors


_CODE_CITATION_SKIP_MARKER = "<!-- gz-validate-skip: code-citation -->"
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s)")


def audit_doc_code_citations(project_root: Path) -> list[ValidationError]:
    """Fail closed on governance prose citing a ``src/gzkit/`` module that does not exist.

    The sibling :func:`audit_skill_code_citations` resolves the same citations
    over ``.gzkit/skills/**/SKILL.md`` and declined to widen its population
    without measuring first (GHI #896, citing #854). The measurement arrived:
    when this arm landed, ``docs/governance/**`` cited 123 distinct
    ``src/gzkit/`` paths and six did not resolve — two of them
    ``src/gzkit/cli.py`` and ``src/gzkit/governance/trust_audits.py``, the very
    paths #896 repaired in the skills population and left rotting in this one,
    because the arm it built could not see here (GHI #1083).

    Unlike skill prose, governance prose LEGITIMATELY cites a path that does not
    resolve, in three shapes measured at #1083: a dated audit record citing a
    path that was correct at its date; corrective prose quoting a superseded
    path beside its replacement; and an unexecuted campaign spec naming a module
    it proposes to build (``src/gzkit/governance/vocabulary.py`` has never
    existed, and its document is headed *PREPARED — NOT YET EXECUTED*). Each is
    exempted by ``<!-- gz-validate-skip: code-citation -->``.

    **The marker exempts the one ITEM it precedes** — a list item and its
    continuation lines, or a paragraph — ending at the next blank line or the
    next list item. :mod:`briefs` scopes its own marker to the next LINE, which
    does not transfer here: governance prose is hard-wrapped, so a citation sits
    mid-paragraph and a line-scoped marker could not be inserted without
    splitting the prose it exempts. Block-to-blank-line does not transfer
    either — a Markdown list is contiguous, so it would exempt every sibling
    item as well as the intended one. Fenced code blocks are not read at all.

    Scope is the EXISTENCE half only, as in the sibling: whether a cited path
    resolves is mechanical, and whether a cited LINE still holds drifts on every
    edit to the cited file. This arm does not claim the second half.
    """
    errors: list[ValidationError] = []
    docs_root = project_root / "docs" / "governance"
    if not docs_root.is_dir():
        return errors
    for doc in sorted(docs_root.rglob("*.md")):
        try:
            text = doc.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        lines = text.splitlines()
        in_fence = False
        exempt = False
        exempt_first = False
        for idx, line in enumerate(lines):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if not line.strip():
                exempt = exempt_first = False
                continue
            if line.strip() == _CODE_CITATION_SKIP_MARKER:
                exempt = exempt_first = True
                continue
            if exempt:
                if exempt_first:
                    # The exempted item's own first line, which is itself a list
                    # item when the marker precedes one.
                    exempt_first = False
                    continue
                if _LIST_ITEM_RE.match(line):
                    exempt = False  # a sibling item; the exemption ended
                else:
                    continue
            for match in _SRC_MODULE_REF.finditer(line):
                relpath = match.group(0)
                if (project_root / relpath).is_file():
                    continue
                package = project_root / relpath[: -len(".py")]
                recovery = (
                    f"It is now the package {relpath[: -len('.py')]}/ — cite that, or the "
                    "specific module inside it."
                    if package.is_dir()
                    else "Cite the module that replaced it, or precede the block with "
                    f"{_CODE_CITATION_SKIP_MARKER} when the citation is historical, "
                    "corrective, or prospective."
                )
                errors.append(
                    ValidationError(
                        type="doc_code_citation",
                        artifact=f"{doc.relative_to(project_root).as_posix()}:{idx + 1}",
                        message=(
                            f"`{relpath}` does not exist, so this document points a reader at a "
                            f"module that is not there. {recovery} "
                            "(GHI #1083; AGENTS.md § DO IT RIGHT 1a.)"
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
    """Return True when a verb path is waived by an exact entry or a top-level group key.

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
        # A deprecated verb INVERTS Invariant 1: wrapping a retired verb in a
        # skill routes agents onto it, which is the defect GHI #705 recorded.
        # Absence of a wielding skill is the passing state; presence is the
        # failure. Without this inversion Invariant 1 and
        # `gz validate --deprecated-verb-prescription` contradict each other.
        deprecated = find_deprecated_verb(path)
        if deprecated is not None:
            if verb_refs[path]:
                errors.append(
                    ValidationError(
                        type="skill_alignment",
                        artifact=f"gz {path}",
                        message=(
                            f"CLI verb `gz {path}` is deprecated but is still wrapped by a "
                            f"skill under .gzkit/skills/**. A skill wrapping a retired verb "
                            f"routes agents onto it (GHI {deprecated.ghi}). Retire the skill "
                            f"per .gzkit/rules/skill-surface-sync.md § Retirement policy "
                            f"(delete from every surface root) and point callers at "
                            f"`{deprecated.successor}`."
                        ),
                    )
                )
            continue
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
