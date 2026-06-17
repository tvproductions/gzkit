"""Brief reconciliation engine — per-dimension delta computation (OBPI-0.0.37-05).

Walks an OBPI brief and the project tree to detect drift across five
dimensions: allowlist, discovery checklist, verification verbs, REQ count,
and citation tuples. The engine is pure — it reads files only and emits no
ledger events or file writes (REQ-0.0.37-05-07, REQ-0.0.37-05-08). Ledger
emission belongs to OBPI-0.0.37-06.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.governance.brief_path_validity import extract_brief_creates_paths, has_glob_chars
from gzkit.governance.brief_structure import (
    BriefStructure,
    parse_brief,
)

# --- Delta models (frozen) ---


class AllowlistDelta(BaseModel):
    """Drift between a brief's allowlist and the project tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    missing_in_brief: list[str] = Field(
        default_factory=list,
        description="src/ files imported by REQ tests but absent from the allowlist",
    )
    missing_on_disk: list[str] = Field(
        default_factory=list,
        description="Allowlist paths that do not exist on disk",
    )


class DiscoveryDelta(BaseModel):
    """Drift between a brief's discovery checklist and the project tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    unresolved_paths: list[str] = Field(
        default_factory=list,
        description="Discovery-checklist paths that do not exist on disk",
    )


class VerificationDelta(BaseModel):
    """Drift between a brief's verification verbs and the registered CLI."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    unresolved_verbs: list[str] = Field(
        default_factory=list,
        description="`gz <verb>` references not in the CLI verb registry",
    )


class ReqCountDelta(BaseModel):
    """Drift between declared REQs and acceptance-criteria checkboxes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    declared_reqs: int = Field(
        default=0, description="Count of REQUIREMENT: lines in the brief body"
    )
    acceptance_criteria_count: int = Field(
        default=0, description="Count of `- [ ]` lines in Acceptance Criteria"
    )
    delta: int = Field(
        default=0,
        description="declared_reqs minus acceptance_criteria_count",
    )


class CitationDelta(BaseModel):
    """Drift between a brief's citation tuples and the project tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    stale_citations: list[tuple[str, str]] = Field(
        default_factory=list,
        description="(artifact_path, anchor) tuples whose file does not exist",
    )


class ReconcileResult(BaseModel):
    """Aggregate per-dimension reconciliation result for a single brief."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    brief_id: str = Field(..., description="OBPI identifier of the reconciled brief")
    allowlist_delta: AllowlistDelta = Field(..., description="Allowlist dimension")
    discovery_delta: DiscoveryDelta = Field(..., description="Discovery dimension")
    verification_delta: VerificationDelta = Field(..., description="Verification-verb dimension")
    req_count_delta: ReqCountDelta = Field(..., description="REQ count dimension")
    citation_delta: CitationDelta = Field(..., description="Citation-tuple dimension")
    has_drift: bool = Field(..., description="True if any dimension reports drift")


# --- Parsing patterns ---

_GZ_VERB_RE = re.compile(r"gz\s+([a-z][a-z0-9-]*)")
_BACKTICK_PATH_RE = re.compile(r"`([^`]+)`")
_REQ_LINE_RE = re.compile(r"REQUIREMENT\s*(?:\[\w+\])?\s*:")
_REQ_ID_RE = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")
_CHECKBOX_RE = re.compile(r"^\s*-\s*\[ \]")
_ALLOWED_HEADING_RE = re.compile(r"^##\s+ALLOWED\s+PATHS\s*$", re.IGNORECASE)
_DISCOVERY_HEADING_RE = re.compile(r"^##\s+DISCOVERY\s+CHECKLIST\s*$", re.IGNORECASE)
_VERIFICATION_HEADING_RE = re.compile(r"^##\s+VERIFICATION\s*$", re.IGNORECASE)
_ACCEPTANCE_HEADING_RE = re.compile(r"^##\s+ACCEPTANCE\s+CRITERIA\s*$", re.IGNORECASE)
_SECTION_HEADING_RE = re.compile(r"^##\s+")

_PATH_PREFIXES = ("src/", "tests/", "docs/", ".gzkit/", "features/")


# --- Engine ---


def reconcile_brief(brief_path: Path, project_root: Path) -> ReconcileResult:
    """Walk a brief and the project tree; compute deltas across five dimensions.

    Pure read-only function: reads ``brief_path`` and probes the project tree
    for existence. Emits no ledger events and writes no files.
    """
    parsed = parse_brief(brief_path)

    if isinstance(parsed, BriefStructure):
        brief_id = parsed.id
        allowlist = list(parsed.allowlist)
        verbs_to_check = _extract_verbs(" ".join(parsed.verification))
        declared_reqs = len(parsed.reqs)
        req_ids = list(parsed.reqs)
        citations = list(parsed.citations)
    else:
        brief_id = str(parsed.raw_frontmatter.get("id", brief_path.stem))
        allowlist = _extract_section_paths(parsed.raw_body, _ALLOWED_HEADING_RE)
        verbs_to_check = _extract_verbs(
            _extract_section_text(parsed.raw_body, _VERIFICATION_HEADING_RE)
        )
        declared_reqs = len(_REQ_LINE_RE.findall(parsed.raw_body))
        req_ids = _extract_req_ids(parsed.raw_body)
        citations = []

    body = _brief_body(brief_path)

    creates_paths = extract_brief_creates_paths(brief_path)
    allowlist_delta = _compute_allowlist_delta(allowlist, req_ids, project_root, creates_paths)
    discovery_delta = _compute_discovery_delta(body, project_root)
    verification_delta = _compute_verb_delta(verbs_to_check)
    acceptance_count = _count_acceptance_criteria(body)
    req_count_delta = ReqCountDelta(
        declared_reqs=declared_reqs,
        acceptance_criteria_count=acceptance_count,
        delta=declared_reqs - acceptance_count,
    )
    citation_delta = _compute_citation_delta(citations, project_root)

    has_drift = (
        bool(allowlist_delta.missing_on_disk)
        or bool(allowlist_delta.missing_in_brief)
        or bool(discovery_delta.unresolved_paths)
        or bool(verification_delta.unresolved_verbs)
        or req_count_delta.delta != 0
        or bool(citation_delta.stale_citations)
    )

    return ReconcileResult(
        brief_id=brief_id,
        allowlist_delta=allowlist_delta,
        discovery_delta=discovery_delta,
        verification_delta=verification_delta,
        req_count_delta=req_count_delta,
        citation_delta=citation_delta,
        has_drift=has_drift,
    )


# --- Helpers ---


def _brief_body(brief_path: Path) -> str:
    """Return the markdown body (frontmatter stripped) of a brief file."""
    text = brief_path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


def _section_lines(body: str, heading_re: re.Pattern[str]) -> list[str]:
    """Return the lines of the section under ``heading_re`` (until next ``##``)."""
    lines = body.splitlines()
    collecting = False
    out: list[str] = []
    for line in lines:
        if heading_re.match(line):
            collecting = True
            continue
        if collecting and _SECTION_HEADING_RE.match(line):
            break
        if collecting:
            out.append(line)
    return out


def _extract_section_text(body: str, heading_re: re.Pattern[str]) -> str:
    """Return the raw text of a section as a single newline-joined string."""
    return "\n".join(_section_lines(body, heading_re))


def _extract_section_paths(body: str, heading_re: re.Pattern[str]) -> list[str]:
    """Collect backtick-wrapped path tokens from a section's bullet lines."""
    paths: list[str] = []
    for line in _section_lines(body, heading_re):
        for token in _BACKTICK_PATH_RE.findall(line):
            if _looks_like_path(token):
                paths.append(token)
    return paths


def _looks_like_path(token: str) -> bool:
    """Return True if a token looks like a project-relative file path."""
    if token.startswith(_PATH_PREFIXES):
        return True
    return "/" in token and "." in token


def _extract_verbs(text: str) -> list[str]:
    """Extract `gz <verb>` verb tokens from arbitrary text, deduplicated."""
    seen: list[str] = []
    for verb in _GZ_VERB_RE.findall(text):
        if verb not in seen:
            seen.append(verb)
    return seen


def _extract_req_ids(body: str) -> list[str]:
    """Extract canonical REQ-IDs (REQ-X.Y.Z-NN-MM) from a brief body, deduplicated."""
    seen: list[str] = []
    for req_id in _REQ_ID_RE.findall(body):
        if req_id not in seen:
            seen.append(req_id)
    return seen


def _extract_gzkit_imports(test_source: str) -> list[str]:
    """Return dotted ``gzkit.*`` module names imported by a test file (AST-parsed)."""
    try:
        tree = ast.parse(test_source)
    except SyntaxError:
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("gzkit"):
            if node.module not in modules:
                modules.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("gzkit") and alias.name not in modules:
                    modules.append(alias.name)
    return modules


def _module_to_src_rel(module: str, project_root: Path) -> str | None:
    """Resolve a dotted ``gzkit.*`` module to its project-relative src/ path.

    Tries ``src/<dotted/path>.py`` then ``src/<dotted/path>/__init__.py``.
    Returns ``None`` when neither exists on disk.
    """
    parts = module.split(".")
    module_file = project_root / "src" / Path(*parts).with_suffix(".py")
    if module_file.exists():
        return module_file.relative_to(project_root).as_posix()
    package_init = project_root / "src" / Path(*parts) / "__init__.py"
    if package_init.exists():
        return package_init.relative_to(project_root).as_posix()
    return None


def _compute_missing_in_brief(
    req_ids: list[str], allowlist: list[str], project_root: Path
) -> list[str]:
    """Report src/ files imported by the brief's REQ tests but absent from the allowlist.

    Neighborhood filter: only src/ files sharing a parent directory with an
    allowlisted src/ path are reported. This isolates the genuine drift signal
    — OBPI work that leaked into a sibling module of the declared scope — while
    excluding cross-cutting test-infrastructure imports (e.g. the ``@covers``
    decorator from ``gzkit.traceability``), which are not subjects-under-test
    and would otherwise produce systematic false positives.
    """
    if not req_ids:
        return []
    src_allowlist = {p.rstrip("/") for p in allowlist if p.startswith("src/")}
    if not src_allowlist:
        return []
    neighborhoods = {Path(p).parent.as_posix() for p in src_allowlist}
    tests_root = project_root / "tests"
    if not tests_root.is_dir():
        return []
    req_set = set(req_ids)
    reported: list[str] = []
    for test_file in sorted(tests_root.rglob("test_*.py")):
        text = test_file.read_text(encoding="utf-8")
        if not any(req in text for req in req_set):
            continue
        for module in _extract_gzkit_imports(text):
            src_rel = _module_to_src_rel(module, project_root)
            if src_rel is None or src_rel in src_allowlist:
                continue
            if Path(src_rel).parent.as_posix() in neighborhoods and src_rel not in reported:
                reported.append(src_rel)
    return reported


def _compute_allowlist_delta(
    allowlist: list[str],
    req_ids: list[str],
    project_root: Path,
    creates_paths: set[str] | None = None,
) -> AllowlistDelta:
    """Report allowlist paths missing on disk and src/ files missing from the allowlist.

    Paths the brief declares it will create (``creates_paths``, GHI #419) are
    exempt from the missing-on-disk check — they exist in contract before they
    exist on disk. Without this exemption a net-new-file OBPI is falsely flagged
    as drifted, which deadlocks the Stage-2 reconcile gate.
    """
    creates = creates_paths or set()
    missing_on_disk = [
        path
        for path in allowlist
        if not (project_root / path).exists() and path.removeprefix("./").rstrip("/") not in creates
    ]
    missing_in_brief = _compute_missing_in_brief(req_ids, allowlist, project_root)
    return AllowlistDelta(missing_in_brief=missing_in_brief, missing_on_disk=missing_on_disk)


def _compute_discovery_delta(body: str, project_root: Path) -> DiscoveryDelta:
    """Report discovery-checklist paths that do not exist on disk.

    Glob prerequisites (``.../**``) are patterns, not literal paths:
    ``(project_root / "dir/**").exists()`` is always False, so existence-checking
    them as literals false-positives on every brief that carries one (GHI #626).
    A path containing a glob metacharacter is skipped.
    """
    paths = _extract_section_paths(body, _DISCOVERY_HEADING_RE)
    unresolved = [
        path for path in paths if not has_glob_chars(path) and not (project_root / path).exists()
    ]
    return DiscoveryDelta(unresolved_paths=unresolved)


def _compute_verb_delta(verbs: list[str]) -> VerificationDelta:
    """Resolve each `gz <verb>` reference against the registered CLI verbs."""
    from gzkit.governance.trust_audits.cli import _known_cli_verbs  # noqa: PLC0415

    try:
        known = _known_cli_verbs()
    except Exception:  # noqa: BLE001 — CLI build failure must not crash the engine
        return VerificationDelta(unresolved_verbs=[])
    unresolved = [verb for verb in verbs if verb not in known]
    return VerificationDelta(unresolved_verbs=unresolved)


def _count_acceptance_criteria(body: str) -> int:
    """Count `- [ ]` checkbox lines in the Acceptance Criteria section."""
    return sum(
        1 for line in _section_lines(body, _ACCEPTANCE_HEADING_RE) if _CHECKBOX_RE.match(line)
    )


def _compute_citation_delta(citations: list[tuple[str, str]], project_root: Path) -> CitationDelta:
    """Report citation tuples whose artifact file does not exist."""
    stale = [
        (artifact_path, anchor)
        for artifact_path, anchor in citations
        if not (project_root / artifact_path).exists()
    ]
    return CitationDelta(stale_citations=stale)
