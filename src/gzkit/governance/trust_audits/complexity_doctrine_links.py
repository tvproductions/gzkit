"""ADR-0.0.27 complexity-doctrine link-integrity validator.

Scans every citation in cluster ADRs (0.0.27/0.0.28/0.0.29/0.0.30) plus
``.gzkit/rules/complexity-doctrine.md`` and ``docs/governance/complexity/**.md``.
For each citation, parses via the canonical ``parse_citation`` surface and
asserts: (1) cited file exists, (2) section anchor resolves, (3) corpus
revision is portable. Fails closed on any miss; emits ``ValidationError``
list shaped for ``gz validate --complexity-doctrine-links`` (exit 3).

Closes the 2am-Scenario-2 failure mode (operator follows advisor diagnosis
to missing artifact).
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.complexity.citation import (
    Citation,
    is_portable,
    parse_citation,
)
from gzkit.core.validation_rules import ValidationError, parse_frontmatter

# Loose detection: any reference to a docs/governance/complexity/...md path
_DOC_PATH_PATTERN = re.compile(r"docs/governance/complexity/[^\s`\"')\]]+\.md")
# Citation extraction: matches the canonical citation form embedded in prose.
# Mirrors citation.py::_CANONICAL_PATTERN but without ^/$ anchors so the
# substring can be extracted from any line. Capture group is the full
# canonical citation suitable for re-parsing via parse_citation.
_CITATION_EXTRACT_PATTERN = re.compile(
    r"(docs/governance/complexity/[^\s`\"')\]]+\.md\s+§\s+"
    r"[a-z0-9][a-z0-9-]*\s+\(corpus revision\s+\d+\))"
)
_SPECULATIVE_MARKER = "<!-- gz-validate-skip: complexity-doctrine-links -->"
_DOCTRINE_AMENDMENT_HINT = "ADR-pool.doctrine-amendment-protocol"
_HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
_BACKTICK_TOKEN_PATTERN = re.compile(r"`([^`]+)`")

# Cluster ADR directory name prefixes to scan
_CLUSTER_ADR_PREFIXES = (
    "ADR-0.0.27-",
    "ADR-0.0.28-",
    "ADR-0.0.29-",
    "ADR-0.0.30-",
)


def _enumerate_in_scope_artifacts(project_root: Path) -> list[Path]:
    """Return cluster ADR bodies + OBPI briefs + complexity doctrine surfaces.

    Includes complexity-doctrine.md and docs/governance/complexity/**/*.md
    (excluding distilled-characteristics-*).
    """
    artifacts: list[Path] = []
    foundation_root = project_root / "docs" / "design" / "adr" / "foundation"
    if foundation_root.is_dir():
        for cluster_dir in foundation_root.iterdir():
            if not cluster_dir.is_dir():
                continue
            if not any(cluster_dir.name.startswith(p) for p in _CLUSTER_ADR_PREFIXES):
                continue
            for md_file in cluster_dir.rglob("*.md"):
                artifacts.append(md_file)
    doctrine_file = project_root / ".gzkit" / "rules" / "complexity-doctrine.md"
    if doctrine_file.is_file():
        artifacts.append(doctrine_file)
    complexity_docs = project_root / "docs" / "governance" / "complexity"
    if complexity_docs.is_dir():
        for md_file in complexity_docs.glob("*.md"):
            if not md_file.name.startswith("distilled-characteristics-"):
                artifacts.append(md_file)
    return artifacts


def _extract_citations(file: Path) -> list[tuple[int, str]]:
    """Return (lineno, citation_text) for every line referencing a complexity doc.

    Lines preceded by the speculative skip marker are excluded.
    """
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    results: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        if not _DOC_PATH_PATTERN.search(line):
            continue
        # Treat a line as a citation candidate only when it carries BOTH
        # the section marker `§` AND the canonical "(corpus revision"
        # token. Bare path references in prose, allowed-path lists,
        # code-fences, and ADR `§ Decision` heading mentions are
        # documentation surfaces, not citations. The two-signal heuristic
        # narrows the candidate set to lines authored in citation form.
        if "§" not in line or "(corpus revision" not in line:
            continue
        if idx > 0 and lines[idx - 1].strip() == _SPECULATIVE_MARKER:
            continue
        match = _CITATION_EXTRACT_PATTERN.search(line)
        citation_text = match.group(1) if match else line.strip()
        results.append((idx + 1, citation_text))
    return results


def _resolve_distilled_file(citation: Citation, project_root: Path) -> Path | None:
    """Return absolute path if cited file exists; else None."""
    candidate = project_root / citation.distilled_characteristics_path
    return candidate if candidate.is_file() else None


def _slugify_heading_candidates(heading_text: str) -> list[str]:
    """Return candidate slugs for a heading.

    Generates:
    1. Default GitHub-style slug (lowercase, non-alphanumeric -> '-', strip).
    2. For each backtick-delimited identifier, a slug variant with '_' -> '-'.
    """
    default_slug = re.sub(r"[^a-z0-9]+", "-", heading_text.lower()).strip("-")
    candidates = [default_slug]
    for match in _BACKTICK_TOKEN_PATTERN.finditer(heading_text):
        token = match.group(1).lower().replace("_", "-")
        token = re.sub(r"[^a-z0-9-]+", "-", token).strip("-")
        if token and token not in candidates:
            candidates.append(token)
    return candidates


def _resolve_section_anchor(file: Path, anchor: str) -> bool:
    """Walk H1/H2/H3 headings; return True if any candidate slug == anchor."""
    try:
        content = file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    for match in _HEADING_PATTERN.finditer(content):
        heading_text = match.group(2)
        if anchor in _slugify_heading_candidates(heading_text):
            return True
    return False


def _read_current_corpus_revision(project_root: Path) -> int | None:
    """Parse corpus_revision from frontmatter of the most recent distilled file.

    Uses distilled-characteristics-*.md sorted by filename desc.
    """
    complexity_docs = project_root / "docs" / "governance" / "complexity"
    if not complexity_docs.is_dir():
        return None
    candidates = sorted(
        complexity_docs.glob("distilled-characteristics-*.md"),
        key=lambda p: p.name,
        reverse=True,
    )
    if not candidates:
        return None
    content = candidates[0].read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(content)
    value = frontmatter.get("corpus_revision")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_citation_safely(text: str) -> Citation | None:
    """Wrap parse_citation; return None on parse failure rather than raising."""
    try:
        citation = parse_citation(text)
        return citation
    except PydanticValidationError:
        return None


def _make_error(source: Path, lineno: int, project_root: Path, message: str) -> ValidationError:
    """Construct a ValidationError with type='complexity_doctrine_links'."""
    return ValidationError(
        type="complexity_doctrine_links",
        artifact=f"{source.relative_to(project_root).as_posix()}:{lineno}",
        message=message,
    )


def validate_complexity_doctrine_links(project_root: Path) -> list[ValidationError]:
    """Enumerate artifacts, walk each citation, apply the four checks.

    Returns a list of ValidationError on any miss.
    """
    errors: list[ValidationError] = []
    current_revision = _read_current_corpus_revision(project_root)
    for source in _enumerate_in_scope_artifacts(project_root):
        for lineno, citation_text in _extract_citations(source):
            citation = _parse_citation_safely(citation_text)
            if citation is None:
                errors.append(
                    _make_error(
                        source,
                        lineno,
                        project_root,
                        f"Citation does not match canonical form: {citation_text!r}",
                    )
                )
                continue
            distilled_file = _resolve_distilled_file(citation, project_root)
            if distilled_file is None:
                errors.append(
                    _make_error(
                        source,
                        lineno,
                        project_root,
                        f"Cited distilled-characteristics file does not exist: "
                        f"{citation.distilled_characteristics_path}",
                    )
                )
                continue
            if not _resolve_section_anchor(distilled_file, citation.section_anchor):
                errors.append(
                    _make_error(
                        source,
                        lineno,
                        project_root,
                        f"Section anchor '{citation.section_anchor}' does not "
                        f"resolve in {citation.distilled_characteristics_path}",
                    )
                )
                continue
            if current_revision is not None and not is_portable(citation, current_revision):
                errors.append(
                    _make_error(
                        source,
                        lineno,
                        project_root,
                        f"Citation corpus_revision={citation.corpus_revision} is "
                        f"non-portable against current revision={current_revision}. "
                        f"Re-author the citation or amend the citing ADR per "
                        f"{_DOCTRINE_AMENDMENT_HINT}.",
                    )
                )
    return errors
