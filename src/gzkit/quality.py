"""Code quality commands for gzkit.

Provides unified interface to linting, formatting, testing, and type checking.
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QualityResult(BaseModel):
    """Result of a quality check."""

    model_config = ConfigDict(extra="forbid")

    success: bool
    command: str
    stdout: str
    stderr: str
    returncode: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def run_command(command: str, cwd: Path | None = None) -> QualityResult:
    """Run a shell command and capture output.

    Args:
        command: Command to run.
        cwd: Working directory.

    Returns:
        QualityResult with command output.

    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        return QualityResult(
            success=result.returncode == 0,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return QualityResult(
            success=False,
            command=command,
            stdout="",
            stderr=str(e),
            returncode=-1,
        )


def _find_parents_subscript_lines(source: str) -> list[int]:
    """Find line numbers where Path(__file__).parents[N] appears in code.

    Uses AST to detect actual subscript access on .parents attributes
    chained from Path(__file__) calls. String literals and comments
    containing the pattern text are not flagged.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if not isinstance(node.value, ast.Attribute) or node.value.attr != "parents":
            continue
        inner = node.value.value
        while isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
            inner = inner.func.value
        if not (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)):
            continue
        if inner.func.id != "Path":
            continue
        if inner.args and isinstance(inner.args[0], ast.Name) and inner.args[0].id == "__file__":
            violations.append(node.lineno)
    return violations


def run_parents_pattern_lint(project_root: Path) -> QualityResult:
    """Detect Path(__file__).parents[N] usage in src/gzkit/ via AST.

    Catches module-level root derivations that should use manifest-based
    resolution instead. Only scans source code — test files are excluded
    because they legitimately use Path(__file__).parent for fixture location.

    @covers OBPI-0.0.7-05-lint-rule-and-check-expansion
    """
    src_dir = project_root / "src" / "gzkit"
    if not src_dir.exists():
        return QualityResult(
            success=True,
            command="parents-pattern lint",
            stdout="src/gzkit/ not found; skipping.",
            stderr="",
            returncode=0,
        )

    violations: list[str] = []

    for py_file in sorted(src_dir.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8")
        except OSError:
            continue
        hit_lines = _find_parents_subscript_lines(source)
        if not hit_lines:
            continue
        rel_path = py_file.relative_to(project_root).as_posix()
        lines = source.splitlines()
        for line_no in hit_lines:
            text = lines[line_no - 1].strip() if line_no <= len(lines) else ""
            violations.append(f"{rel_path}:{line_no}: {text}")

    if violations:
        return QualityResult(
            success=False,
            command="parents-pattern lint",
            stdout=("Path(__file__).parents[N] violations found:\n" + "\n".join(violations)),
            stderr="Use manifest-based path resolution instead.",
            returncode=1,
        )

    return QualityResult(
        success=True,
        command="parents-pattern lint",
        stdout="No Path(__file__).parents[N] violations found.",
        stderr="",
        returncode=0,
    )


def run_lint(project_root: Path) -> QualityResult:
    """Run linting (ruff check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from linting.

    """
    ruff_result = run_command("uvx ruff check src tests", cwd=project_root)
    path_contract_result = run_adr_path_contract_lint(project_root)
    parents_result = run_parents_pattern_lint(project_root)

    sub_results = [ruff_result, path_contract_result, parents_result]
    success = all(r.success for r in sub_results)
    returncode = 0 if success else next((r.returncode for r in sub_results if not r.success), 1)
    stdout = "\n".join(output for output in [r.stdout for r in sub_results] if output.strip())
    stderr = "\n".join(output for output in [r.stderr for r in sub_results] if output.strip())

    return QualityResult(
        success=success,
        command="uvx ruff check src tests + ADR path contract lint + parents-pattern lint",
        stdout=stdout,
        stderr=stderr,
        returncode=returncode,
    )


def run_adr_path_contract_lint(project_root: Path) -> QualityResult:
    """Enforce ADR docs path contracts.

    This check blocks regressions to legacy series-folder links like
    ``docs/design/adr/adr-0.2.x/...``.
    """
    docs_design_root = project_root / "docs" / "design"
    files_to_scan: list[Path] = []
    if docs_design_root.exists():
        files_to_scan.extend(sorted(docs_design_root.rglob("*.md")))

    agents_file = project_root / "AGENTS.md"
    if agents_file.exists():
        files_to_scan.append(agents_file)

    if not files_to_scan:
        return QualityResult(
            success=True,
            command="ADR path contract lint",
            stdout="No docs/design markdown files found for ADR path contract lint.",
            stderr="",
            returncode=0,
        )

    # Keep airlineops historical references valid while blocking gzkit-local regressions.
    allow_substrings = ("airlineops/docs/design/adr/adr-",)
    forbidden_patterns = (
        re.compile(r"docs/design/adr/adr-[^/\\s`]+/"),
        re.compile(r"\.\./adr/adr-[^/\\s`]+/"),
        re.compile(r"docs/design/adr/(foundation|pre-release)/adr-[^/\\s`]+/"),
    )

    violations: list[str] = []
    for file_path in files_to_scan:
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            violations.append(f"{file_path.as_posix()}:1: unable to read file ({exc})")
            continue

        rel_path = (
            file_path.relative_to(project_root)
            if file_path.is_relative_to(project_root)
            else file_path
        )
        rel_display = rel_path.as_posix()
        for line_no, line in enumerate(lines, start=1):
            if any(allowed in line for allowed in allow_substrings):
                continue
            if any(pattern.search(line) for pattern in forbidden_patterns):
                trimmed = line.strip()
                violations.append(f"{rel_display}:{line_no}: {trimmed}")

    if violations:
        return QualityResult(
            success=False,
            command="ADR path contract lint",
            stdout="Legacy ADR path references found:\n" + "\n".join(violations),
            stderr="Use foundation/pre-release/<major>.0 ADR package paths.",
            returncode=1,
        )

    return QualityResult(
        success=True,
        command="ADR path contract lint",
        stdout="ADR path contract check passed.",
        stderr="",
        returncode=0,
    )


def run_format_check(project_root: Path) -> QualityResult:
    """Run format check (ruff format --check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from format check.

    """
    return run_command("uvx ruff format --check .", cwd=project_root)


def run_format(project_root: Path) -> QualityResult:
    """Run auto-formatting (ruff format + ruff check --fix).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from formatting.

    """
    # Run ruff format first
    format_result = run_command("uvx ruff format .", cwd=project_root)
    if not format_result.success:
        return format_result

    # Then run ruff check --fix
    fix_result = run_command("uvx ruff check --fix src tests", cwd=project_root)

    # Combine results
    return QualityResult(
        success=fix_result.success,
        command="uvx ruff format . && uvx ruff check --fix src tests",
        stdout=format_result.stdout + "\n" + fix_result.stdout,
        stderr=format_result.stderr + "\n" + fix_result.stderr,
        returncode=fix_result.returncode,
    )


def run_typecheck(project_root: Path) -> QualityResult:
    """Run type checking (ty check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from type checking.

    """
    return run_command("uvx ty check src", cwd=project_root)


def run_tests(project_root: Path) -> QualityResult:
    """Run unit tests (unittest discover).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from testing.

    """
    return run_command("uv run -m unittest discover tests", cwd=project_root)


def run_behave(project_root: Path) -> QualityResult:
    """Run BDD scenarios via behave.

    Behave is part of the test floor: `gz test` and `gz check` must run it
    so feature/CLI contract drift is caught alongside unit failures.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from the behave run.

    """
    return run_command("uv run -m behave", cwd=project_root)


class DriftAdvisoryResult(BaseModel):
    """Result of an advisory drift detection check."""

    model_config = ConfigDict(extra="forbid")

    advisory: bool = True
    has_drift: bool
    unlinked_specs: list[str]
    orphan_tests: list[str]
    unjustified_code_changes: list[str]
    total_drift_count: int
    scan_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "advisory": self.advisory,
            "has_drift": self.has_drift,
            "unlinked_specs": self.unlinked_specs,
            "orphan_tests": self.orphan_tests,
            "unjustified_code_changes": self.unjustified_code_changes,
            "total_drift_count": self.total_drift_count,
            "scan_timestamp": self.scan_timestamp,
        }


class CheckResult(BaseModel):
    """Result of running all quality checks."""

    model_config = ConfigDict(extra="forbid")

    success: bool
    lint: QualityResult
    format: QualityResult
    typecheck: QualityResult
    test: QualityResult
    behave: QualityResult
    skill_audit: QualityResult
    parity_check: QualityResult
    readiness_audit: QualityResult
    drift: DriftAdvisoryResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "success": self.success,
            "lint": self.lint.to_dict(),
            "format": self.format.to_dict(),
            "typecheck": self.typecheck.to_dict(),
            "test": self.test.to_dict(),
            "behave": self.behave.to_dict(),
            "skill_audit": self.skill_audit.to_dict(),
            "parity_check": self.parity_check.to_dict(),
            "readiness_audit": self.readiness_audit.to_dict(),
        }
        if self.drift is not None:
            result["drift"] = self.drift.to_dict()
        return result


def run_drift_advisory(project_root: Path) -> DriftAdvisoryResult:
    """Run advisory drift detection using the triangle engine.

    Reuses the same detection engine as ``gz drift``. Results are advisory —
    drift findings do not affect the overall check pass/fail status.
    """
    from datetime import UTC, datetime

    from gzkit.commands.drift import get_changed_files, scan_covers_references
    from gzkit.triangle import detect_drift, scan_briefs

    briefs_dir = project_root / "docs" / "design" / "adr"
    tests_dir = project_root / "tests"

    discovered = scan_briefs(briefs_dir)
    reqs = [d.entity for d in discovered]
    linkages = scan_covers_references(tests_dir)
    changed_vertices = get_changed_files(project_root)
    timestamp = datetime.now(UTC).isoformat()
    report = detect_drift(reqs, linkages, changed_vertices, timestamp)

    return DriftAdvisoryResult(
        has_drift=report.summary.total_drift_count > 0,
        unlinked_specs=report.unlinked_specs,
        orphan_tests=report.orphan_tests,
        unjustified_code_changes=report.unjustified_code_changes,
        total_drift_count=report.summary.total_drift_count,
        scan_timestamp=report.scan_timestamp,
    )


def run_all_checks(project_root: Path) -> CheckResult:
    """Run all quality checks.

    Args:
        project_root: Project root directory.

    Returns:
        CheckResult with all check results.

    """
    lint = run_lint(project_root)
    format_check = run_format_check(project_root)
    typecheck = run_typecheck(project_root)
    test = run_tests(project_root)
    behave = run_behave(project_root)
    skill_audit = run_skill_audit(project_root)
    parity_check = run_parity_check(project_root)
    readiness_audit = run_readiness_audit(project_root)

    success = all(
        [
            lint.success,
            format_check.success,
            typecheck.success,
            test.success,
            behave.success,
            skill_audit.success,
            parity_check.success,
            readiness_audit.success,
        ]
    )

    drift = run_drift_advisory(project_root)

    return CheckResult(
        success=success,
        lint=lint,
        format=format_check,
        typecheck=typecheck,
        test=test,
        behave=behave,
        skill_audit=skill_audit,
        parity_check=parity_check,
        readiness_audit=readiness_audit,
        drift=drift,
    )


def run_pymarkdown(project_root: Path) -> QualityResult:
    """Run PyMarkdown linting on documentation.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from PyMarkdown.

    """
    return run_command("uv run -m pymarkdown scan docs/", cwd=project_root)


def run_skill_audit(project_root: Path) -> QualityResult:
    """Run skill lifecycle/parity audit."""
    return run_command("uv run gz skill audit", cwd=project_root)


def run_parity_check(project_root: Path) -> QualityResult:
    """Run deterministic parity regression checks."""
    return run_command("uv run gz parity check", cwd=project_root)


def run_readiness_audit(project_root: Path) -> QualityResult:
    """Run readiness audit over four disciplines and five primitives."""
    return run_command("uv run gz readiness audit", cwd=project_root)


def run_eval(project_root: Path) -> QualityResult:
    """Run offline eval harnesses against reference datasets.

    Loads all eval datasets, scores each case per surface, and returns
    a QualityResult with structured output. Fully deterministic — no
    network calls or LLM invocations.

    Args:
        project_root: Project root directory for resolving data paths.

    Returns:
        QualityResult with eval suite output.

    """
    from gzkit.eval.runner import run_eval_suite

    try:
        result = run_eval_suite(data_dir=project_root / "data" / "eval")
        lines = [
            f"Eval suite: {result.surfaces_scored} surfaces scored",
            f"Overall score: {result.overall_score}/4.0",
            f"Success: {result.success}",
        ]
        for ss in result.surface_scores:
            lines.append(
                f"  {ss.surface}: {ss.overall}/4.0 "
                f"({ss.cases_passed}/{ss.cases_total} cases passed)"
            )
        return QualityResult(
            success=result.success,
            command="eval harness",
            stdout="\n".join(lines),
            stderr="",
            returncode=0 if result.success else 1,
        )
    except (OSError, ValueError, KeyError) as exc:
        return QualityResult(
            success=False,
            command="eval harness",
            stdout="",
            stderr=str(exc),
            returncode=2,
        )


# ---------------------------------------------------------------------------
# Product proof gate
# ---------------------------------------------------------------------------

_ALLOWED_PATHS_RE = re.compile(r"^## ALLOWED PATHS\s*$", re.MULTILINE | re.IGNORECASE)
_BRIEF_SECTION_RE = re.compile(r"^## ", re.MULTILINE)


class ObpiProofStatus(BaseModel):
    """Product proof status for a single OBPI."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI identifier")
    runbook_found: bool = Field(False, description="Runbook entry references this OBPI")
    command_doc_found: bool = Field(False, description="Command doc exists with content")
    docstring_found: bool = Field(False, description="Public interface has docstrings")
    governance_artifact_found: bool = Field(
        False, description="Governance artifact exists in .gzkit/ with content"
    )
    test_evidence_found: bool = Field(
        False, description="Test file exists with substantive content"
    )
    bdd_evidence_found: bool = Field(
        False, description="BDD feature file exists with substantive content"
    )
    release_artifact_found: bool = Field(
        False, description="Release manifest exists in docs/releases/ with substantive content"
    )

    @property
    def has_proof(self) -> bool:
        """Return True if any documentation proof source was found."""
        return (
            self.runbook_found
            or self.command_doc_found
            or self.docstring_found
            or self.governance_artifact_found
            or self.test_evidence_found
            or self.bdd_evidence_found
            or self.release_artifact_found
        )

    @property
    def proof_type(self) -> str:
        """Return the type of documentation proof found."""
        if self.runbook_found:
            return "runbook"
        if self.command_doc_found:
            return "command_doc"
        if self.docstring_found:
            return "docstring"
        if self.governance_artifact_found:
            return "governance_artifact"
        if self.test_evidence_found:
            return "test_evidence"
        if self.bdd_evidence_found:
            return "bdd_evidence"
        if self.release_artifact_found:
            return "release_artifact"
        return "MISSING"


class ProductProofResult(BaseModel):
    """Result of product proof validation for an ADR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="ADR identifier")
    success: bool = Field(..., description="True if all OBPIs have proof")
    obpi_proofs: list[ObpiProofStatus] = Field(..., description="Per-OBPI proof status")
    missing_count: int = Field(..., description="Number of OBPIs without proof")


def _extract_allowed_paths(brief_text: str) -> list[str]:
    """Extract file paths from the ALLOWED PATHS section of an OBPI brief."""
    match = _ALLOWED_PATHS_RE.search(brief_text)
    if not match:
        return []
    rest = brief_text[match.end() :]
    next_section = _BRIEF_SECTION_RE.search(rest)
    section_text = rest[: next_section.start()] if next_section else rest
    paths: list[str] = []
    for line in section_text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            # Extract path from `- `path` — description` format
            path_match = re.match(r"-\s+`([^`]+)`", line)
            if path_match:
                paths.append(path_match.group(1))
    return paths


def _extract_obpi_slug(obpi_id: str) -> str:
    """Extract the slug portion after the version-item prefix."""
    # OBPI-0.23.0-02-product-proof-gate → product-proof-gate
    parts = obpi_id.split("-", 3)
    return parts[3] if len(parts) > 3 else obpi_id


def _check_runbook_proof(obpi_id: str, slug: str, runbook_text: str) -> bool:
    """Check if the runbook references this OBPI by ID or slug keywords."""
    if obpi_id in runbook_text:
        return True
    keywords = slug.replace("-", " ")
    return keywords.lower() in runbook_text.lower()


def _check_command_doc_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any command doc in allowed paths exists with substantive content."""
    for path_str in allowed_paths:
        if not path_str.startswith("docs/user/commands/"):
            continue
        doc_path = project_root / path_str
        if not doc_path.is_file():
            continue
        content = doc_path.read_text(encoding="utf-8").strip()
        # Substantive = more than just a heading (>100 chars after stripping)
        if len(content) > 100:
            return True
    return False


def _check_docstring_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if Python source files in allowed paths have public interface docstrings."""
    for path_str in allowed_paths:
        if not path_str.endswith(".py") or not path_str.startswith("src/"):
            continue
        src_path = project_root / path_str
        if not src_path.is_file():
            continue
        try:
            tree = ast.parse(src_path.read_text(encoding="utf-8"), filename=path_str)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if node.name.startswith("_"):
                continue
            docstring = ast.get_docstring(node)
            if docstring and len(docstring.strip()) > 10:
                return True
    return False


def _check_governance_artifact_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if governance artifacts in .gzkit/ exist with substantive content."""
    for path_str in allowed_paths:
        if not path_str.startswith(".gzkit/"):
            continue
        artifact_path = project_root / path_str
        if not artifact_path.is_file():
            continue
        content = artifact_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


def _check_test_evidence_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any test file in allowed paths exists with substantive content."""
    for path_str in allowed_paths:
        if not path_str.startswith("tests/") or not path_str.endswith(".py"):
            continue
        test_path = project_root / path_str
        if not test_path.is_file():
            continue
        content = test_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


def _check_bdd_evidence_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any BDD feature file in allowed paths exists with substantive content."""
    for path_str in allowed_paths:
        if not path_str.startswith("features/") or not path_str.endswith(".feature"):
            continue
        feature_path = project_root / path_str
        if not feature_path.is_file():
            continue
        content = feature_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


def _check_release_artifact_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any release artifact in docs/releases/ exists with substantive content (#118).

    Recognizes patch-release manifests and similar release evidence files
    produced by ``gz patch release`` (e.g. ``docs/releases/PATCH-vX.Y.Z.md``)
    so OBPIs that ship release artifacts can satisfy product proof.
    """
    for path_str in allowed_paths:
        if not path_str.startswith("docs/releases/"):
            continue
        artifact_path = project_root / path_str
        if not artifact_path.is_file():
            continue
        content = artifact_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


def check_product_proof(
    adr_id: str,
    obpi_files: dict[str, Path],
    project_root: Path,
) -> ProductProofResult:
    """Validate that each OBPI in an ADR has product proof.

    Checks four proof types per OBPI (at least one must exist):
    - runbook: keyword match in docs/user/runbook.md
    - command_doc: file exists with substantive content in docs/user/commands/
    - docstring: public interfaces in source files have docstrings
    - governance_artifact: .gzkit/ file exists with substantive content

    Args:
        adr_id: ADR identifier.
        obpi_files: Map of OBPI ID to brief file path.
        project_root: Project root directory.

    Returns:
        ProductProofResult with per-OBPI proof status.

    """
    runbook_path = project_root / "docs" / "user" / "runbook.md"
    runbook_text = ""
    if runbook_path.exists():
        runbook_text = runbook_path.read_text(encoding="utf-8")

    proofs: list[ObpiProofStatus] = []
    for obpi_id, brief_path in sorted(obpi_files.items()):
        brief_text = brief_path.read_text(encoding="utf-8")
        allowed_paths = _extract_allowed_paths(brief_text)
        slug = _extract_obpi_slug(obpi_id)

        runbook_found = _check_runbook_proof(obpi_id, slug, runbook_text)
        command_doc_found = _check_command_doc_proof(allowed_paths, project_root)
        docstring_found = _check_docstring_proof(allowed_paths, project_root)
        governance_artifact_found = _check_governance_artifact_proof(allowed_paths, project_root)
        test_evidence_found = _check_test_evidence_proof(allowed_paths, project_root)
        bdd_evidence_found = _check_bdd_evidence_proof(allowed_paths, project_root)
        release_artifact_found = _check_release_artifact_proof(allowed_paths, project_root)

        proofs.append(
            ObpiProofStatus(
                obpi_id=obpi_id,
                runbook_found=runbook_found,
                command_doc_found=command_doc_found,
                docstring_found=docstring_found,
                governance_artifact_found=governance_artifact_found,
                test_evidence_found=test_evidence_found,
                bdd_evidence_found=bdd_evidence_found,
                release_artifact_found=release_artifact_found,
            )
        )

    missing = sum(1 for p in proofs if not p.has_proof)
    return ProductProofResult(
        adr_id=adr_id,
        success=missing == 0,
        obpi_proofs=proofs,
        missing_count=missing,
    )
