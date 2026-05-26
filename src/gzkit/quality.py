"""Code quality commands for gzkit.

Provides unified interface to linting, formatting, testing, and type checking.
"""

import ast
import re
import shlex
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.doc_coverage.manifest import MANPAGE_DIR


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


def run_command(
    command: str | Sequence[str],
    cwd: Path | None = None,
) -> QualityResult:
    """Run a command without shell interpretation and capture output.

    Governance gate execution must not depend on shell parsing of configurable
    command strings (GHI #415). String input is tokenized once via
    ``shlex.split`` and dispatched as argv with ``shell=False``; sequence
    input is forwarded as argv directly. Pipes, redirects, env-var
    expansion, and command chaining are not supported by design — callers
    must compose explicit argv if those semantics are needed.

    Args:
        command: Command to run, either as a string (tokenized via shlex)
            or as a pre-built argv sequence.
        cwd: Working directory.

    Returns:
        QualityResult with command output.

    """
    if isinstance(command, str):
        argv = shlex.split(command)
        display = command
    else:
        argv = list(command)
        display = shlex.join(argv)

    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            check=False,
        )
        return QualityResult(
            success=result.returncode == 0,
            command=display,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return QualityResult(
            success=False,
            command=display,
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
    ruff_result = run_command("uv run ruff check src tests", cwd=project_root)
    path_contract_result = run_adr_path_contract_lint(project_root)
    parents_result = run_parents_pattern_lint(project_root)

    sub_results = [ruff_result, path_contract_result, parents_result]
    success = all(r.success for r in sub_results)
    returncode = 0 if success else next((r.returncode for r in sub_results if not r.success), 1)
    stdout = "\n".join(output for output in [r.stdout for r in sub_results] if output.strip())
    stderr = "\n".join(output for output in [r.stderr for r in sub_results] if output.strip())

    return QualityResult(
        success=success,
        command="uv run ruff check src tests + ADR path contract lint + parents-pattern lint",
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
    return run_command("uv run ruff format --check .", cwd=project_root)


def run_format(project_root: Path) -> QualityResult:
    """Run auto-formatting (ruff format + ruff check --fix).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from formatting.

    """
    # Run ruff format first
    format_result = run_command("uv run ruff format .", cwd=project_root)
    if not format_result.success:
        return format_result

    # Then run ruff check --fix
    fix_result = run_command("uv run ruff check --fix src tests", cwd=project_root)

    # Combine results
    return QualityResult(
        success=fix_result.success,
        command="uv run ruff format . && uv run ruff check --fix src tests",
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
    return run_command("uv run ty check src", cwd=project_root)


def run_tests(project_root: Path) -> QualityResult:
    """Run the unittest test suite.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from testing.

    """
    return run_command("uv run -m unittest discover tests", cwd=project_root)


def run_behave(project_root: Path, tags: list[str] | None = None) -> QualityResult:
    """Run BDD scenarios via behave, optionally filtered by tag list.

    ADR closeout (``gz test --bdd``) runs the full suite; OBPI-scoped
    pipeline stages can pass ``tags`` (e.g. ``["@REQ-0.0.16-01-05"]``) to
    run only scenarios covering that OBPI's requirements.

    Args:
        project_root: Project root directory.
        tags: Optional list of behave scenario tags (with leading ``@``) to
            filter on. When non-empty, invokes ``behave --tags=<tag1>,<tag2>``.
            None or empty list runs every scenario under ``features/``.

    Returns:
        QualityResult from the behave run.

    """
    if tags:
        tag_arg = ",".join(tags)
        return run_command(f"uv run -m behave --tags={tag_arg}", cwd=project_root)
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
    cli_audit: QualityResult
    preflight: QualityResult
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
            "cli_audit": self.cli_audit.to_dict(),
            "preflight": self.preflight.to_dict(),
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
    cli_audit = run_cli_audit(project_root)
    preflight = run_preflight(project_root)

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
            cli_audit.success,
            preflight.success,
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
        cli_audit=cli_audit,
        preflight=preflight,
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


def run_cli_audit(project_root: Path) -> QualityResult:
    """Run CLI documentation coverage audit.

    Part of the canonical quality path so workflow drift (e.g. a new subcommand
    not yet documented in the operator runbook) is caught by ``gz check``
    before release.
    """
    return run_command("uv run gz cli audit", cwd=project_root)


def run_unscoped_rules_audit(project_root: Path) -> QualityResult:
    """Run the agent-rule placement invariant audit (ADR-0.0.20).

    Fails closed (exit 3) on any `.gzkit/rules/*.md` that carries
    `paths: "**"` or lacks a `paths:` frontmatter entry without an
    allow-list exception under `rules.unscoped_allowlist`.
    """
    return run_command("uv run gz validate --unscoped-rules", cwd=project_root)


def run_adr_status_fresh_audit(project_root: Path) -> QualityResult:
    """Run the adr-status.md freshness audit (GHI #322 / Architectural Boundary 6).

    Fails closed when `docs/governance/GovZero/adr-status.md` drifts from
    on-disk ADR canon — the original surface that GHI #322 surfaced.
    Recovery: `uv run gz register-adrs` regenerates the index.
    """
    return run_command("uv run gz validate --adr-status-fresh", cwd=project_root)


def run_kind_invariance_audit(project_root: Path) -> QualityResult:
    """Run the kind-invariance audit for foundation-tier ADRs (OBPI-0.0.35-04).

    Fails closed when any ``kind: foundation`` ADR is missing or has a
    placeholder-only "## Why foundation tier?" section. Recovery: add/update
    the section with a substantive one-sentence answer to the invariance test
    ('Without this ADR, the project would not be the project because ...').
    """
    return run_command("uv run gz validate --kind-invariance", cwd=project_root)


def run_receipt_shape_audit(project_root: Path) -> QualityResult:
    """Run the receipt-shape deprecated-shape audit (OBPI-0.0.36-03).

    Fails closed (exit 3) when any obpi_receipt_emitted event dated on or after
    ADR-0.0.36's cutoff carries a deprecated shape: attestation_requirement:optional,
    obpi_completion without attested_ prefix, or attestor matching ^agent:.
    Recovery: pre-cutoff receipts are registered in data/historical_self_close_waivers.json
    under OBPI-0.0.36-04.
    """
    return run_command("uv run gz validate --receipt-shape", cwd=project_root)


def run_req_kind_discipline_audit(project_root: Path) -> QualityResult:
    """Run the REQ kind discipline audit (OBPI-0.0.59-02).

    Fails closed (exit 3) when any OBPI brief has mixed-state [kind] tags
    (some tagged, some not) or per-kind proof-citation gaps. All-untagged
    briefs pass in legacy/grandfathered mode.
    Recovery: add [BEHAVIOR], [SUPPORT], or [STRUCTURAL-FENCE] tag to each
    untagged REQ in the brief's Acceptance Criteria section, and supply the
    required proof citations per the kind.
    """
    return run_command("uv run gz validate --req-kind-discipline", cwd=project_root)


def run_insights_shape_audit(project_root: Path) -> QualityResult:
    """Run the agent-insights.jsonl record-shape audit (GHI #358).

    Fails closed (exit 3) when any line in `.gzkit/insights/agent-insights.jsonl`
    drifts from the canonical `InsightRecord` schema. Pre-lock entries are
    waived by content hash in `_INSIGHTS_SHAPE_WAIVERS`; new writes must
    conform.
    """
    return run_command("uv run gz validate --insights-shape", cwd=project_root)


def run_instructions_files_budget_audit(project_root: Path) -> QualityResult:
    """Run the AGENTS.md/CLAUDE.md/.claude/rules char-budget audit (GHI #373).

    Fails closed (exit 3) when any tracked instructions/memory file exceeds
    its per-file char budget defined in `data/instructions_files_budget.json`.
    Recovery: `/gz-context-diet` lifts inline pedagogy to `docs/governance/`.
    """
    return run_command("uv run gz validate --instructions-files-budget", cwd=project_root)


def run_agents_md_map_conformance_audit(project_root: Path) -> QualityResult:
    """Run the AGENTS.md map-not-encyclopedia conformance audit (ADR-0.0.54).

    Fails closed (exit 3) when the template `src/gzkit/templates/agents.md`
    violates shape criteria (a)/(b)/(c) — paragraph length without binding
    marker, prohibited subsection title, unresolvable link — or when the
    rendered `AGENTS.md` exceeds the budget declared in
    `data/instructions_files_budget.json`. Recovery: `/gz-context-diet`.
    """
    return run_command("uv run gz validate --agents-md-map-conformance", cwd=project_root)


def run_complexity_doctrine_links_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.27 complexity-doctrine link-integrity audit.

    Fails closed when any citation in the cluster ADRs (0.0.27 / 0.0.28 /
    0.0.29 / 0.0.30) or the rule body references a missing file, unresolved
    anchor, or non-portable corpus revision.
    """
    return run_command("uv run gz validate --complexity-doctrine-links", cwd=project_root)


def run_complexity_thresholds_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.28 complexity-thresholds rule-body audit.

    Fails closed when the rule body fails to parse into a ``ThresholdTable``,
    or when any canonical metric is missing a per-metric section. Emits a
    ``bootstrap-mode`` warning (non-policy-breach) when the rule body
    declares the bootstrap-absolutes carve-out section.
    """
    return run_command("uv run gz validate --complexity-thresholds", cwd=project_root)


def run_orientation_freshness_audit(project_root: Path) -> QualityResult:
    """Run the SessionStart orientation hook freshness audit (GHI #341).

    Fails closed when the SessionStart hook in `.claude/settings.json` or
    `.codex/hooks.json` no longer invokes `scripts/session_orientation.py`,
    or when the script drops the `Git remote state` heading or the
    `collect_state` -> `collect_remote_state` wiring that GHI #338 added.
    Recovery: `uv run gz agent sync control-surfaces` for hook drift; restore
    the script edit for script drift.
    """
    return run_command("uv run gz validate --orientation-freshness", cwd=project_root)


def run_tautological_test_audit(project_root: Path) -> QualityResult:
    """Run the tautological-test drift gate (OBPI-0.0.59-04).

    Fails closed (exit 3) when the current count of filesystem-op+assertion
    co-occurrences in tests/** exceeds baseline + waivers count.
    Recovery: update data/tautological_test_baseline.json or add waivers to
    data/tautological_test_waivers.json with rationale-key entries.
    """
    return run_command("uv run gz validate --tautological-test-audit", cwd=project_root)


def run_surface_fidelity_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.33-05 surface-fidelity composite (all four invariants).

    Fails closed when any of bullet_retention, surface_weight,
    pointer_integrity, or scenario_reachability report errors.
    """
    return run_command("uv run gz validate --surface-fidelity", cwd=project_root)


def run_interviews_audit(project_root: Path) -> QualityResult:
    """Run the interview-transcript audit (GHI #511 retarget / GHI #515).

    Fails closed when an ADR with OBPI briefs lacks an embedded
    ``## Q&A Transcript`` section and is not waived in
    ``data/interview_transcript_waivers.json``. Wiring this scope into the
    gated pipeline closes the structural root cause GHI #511 named: a
    validator outside ``gz check`` is never exercised, so its divergence
    from reality goes unnoticed. Recovery: add the section to the ADR body,
    or — for a pre-convention ADR with no recoverable transcript — append a
    waiver entry with rationale.
    """
    return run_command("uv run gz validate --interviews", cwd=project_root)


def run_preflight(project_root: Path) -> QualityResult:
    """Run preflight scan for stale pipeline markers and orphan receipts.

    Part of the canonical quality path so stale workflow artifacts apply
    self-healing pressure in the default operator loop rather than
    accumulating silently.
    """
    return run_command("uv run gz preflight", cwd=project_root)


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
        False, description="Governance artifact exists in .gzkit/ or docs/governance/ with content"
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
    concepts_page_found: bool = Field(
        False, description="Concepts page exists in docs/user/concepts/ with substantive content"
    )
    decision_doc_found: bool = Field(
        False, description="Brief contains a substantive Confirm/Exclude/Absorb decision"
    )
    closeout_artifact_found: bool = Field(
        False,
        description=(
            "Closeout artifact (ADR-CLOSEOUT-FORM.md / EVALUATION_SCORECARD.md) "
            "exists with substantive content for closeout-kind OBPIs"
        ),
    )
    data_or_schema_artifact_found: bool = Field(
        False,
        description=(
            "Data registry (data/**/*.json) or JSON-schema (src/gzkit/schemas/**/*.json) "
            "artifact exists with substantive content"
        ),
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
            or self.concepts_page_found
            or self.decision_doc_found
            or self.closeout_artifact_found
            or self.data_or_schema_artifact_found
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
        if self.concepts_page_found:
            return "concepts_page"
        if self.decision_doc_found:
            return "decision_doc"
        if self.closeout_artifact_found:
            return "closeout_artifact"
        if self.data_or_schema_artifact_found:
            return "data_or_schema_artifact"
        return "MISSING"


class ProductProofResult(BaseModel):
    """Result of product proof validation for an ADR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="ADR identifier")
    success: bool = Field(..., description="True if all OBPIs have proof")
    obpi_proofs: list[ObpiProofStatus] = Field(..., description="Per-OBPI proof status")
    missing_count: int = Field(..., description="Number of OBPIs without proof")


def _expand_allowed_paths(allowed_paths: list[str], project_root: Path) -> list[str]:
    """Expand glob patterns in allowed_paths to concrete relative file paths.

    Brief authors commonly list ALLOWED PATHS as globs (`src/gzkit/models/**`,
    `tests/governance/**`). Each downstream proof classifier filters by literal
    prefix/suffix on the raw string, so unexpanded globs are silently invisible.
    Expansion materializes each glob into the set of real files it matches and
    leaves literal entries unchanged (GHI #363).
    """
    expanded: list[str] = []
    for path_str in allowed_paths:
        if "*" not in path_str:
            expanded.append(path_str)
            continue
        try:
            for matched in project_root.glob(path_str):
                if matched.is_file():
                    expanded.append(matched.relative_to(project_root).as_posix())
        except (ValueError, OSError):
            continue
    return expanded


def _check_data_or_schema_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if a data registry or JSON-schema artifact is present with substantive content.

    Schema-shaped and registry-shaped OBPIs (e.g. ADR-0.0.22-01 schema field
    additions, ADR-0.0.22-02 data/security_surfaces.json) produce durable JSON
    artifacts whose existence the prior proof types could not see (GHI #363).
    """
    for path_str in allowed_paths:
        is_data = path_str.startswith("data/") and path_str.endswith(".json")
        is_schema = path_str.startswith("src/gzkit/schemas/") and path_str.endswith(".json")
        if not (is_data or is_schema):
            continue
        artifact_path = project_root / path_str
        if not artifact_path.is_file():
            continue
        content = artifact_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


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


def _check_runbook_proof(
    obpi_id: str,
    slug: str,
    runbook_text: str,
    allowed_paths: list[str] | None = None,
) -> bool:
    """Check if the runbook references this OBPI, or is a direct allowed path.

    GHI #265 relaxed the match: OBPI slugs rarely appear verbatim in runbook
    section headings (``OBPI-0.0.18-02-runbook-prd-to-adr`` wants to credit a
    section titled ``## PRD → ADR Derivation``). When the OBPI's allowed paths
    list ``docs/user/runbook.md`` and the runbook has substantive content, the
    OBPI clearly did runbook work regardless of slug-keyword coincidence. Keep
    the slug/id match as a short-circuit, fall back to allowed-path presence
    with a substantive-content bar.
    """
    if obpi_id in runbook_text:
        return True
    keywords = slug.replace("-", " ")
    if keywords.lower() in runbook_text.lower():
        return True
    return bool(
        allowed_paths
        and "docs/user/runbook.md" in allowed_paths
        and len(runbook_text.strip()) > 100
    )


def _check_concepts_page_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any concepts page under ``docs/user/concepts/`` exists with content.

    Added in GHI #265 to give Foundation-doctrine ADRs (concepts pages, doctrine
    references) a named product-proof path. Foundation ADRs that land operator-
    facing doctrine under ``docs/user/concepts/`` satisfy proof via this
    check instead of tripping the closeout blocker.
    """
    for path_str in allowed_paths:
        if not path_str.startswith("docs/user/concepts/"):
            continue
        page_path = project_root / path_str
        if not page_path.is_file():
            continue
        content = page_path.read_text(encoding="utf-8").strip()
        if len(content) > 100:
            return True
    return False


def _check_command_doc_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if any command doc in allowed paths exists with substantive content."""
    for path_str in allowed_paths:
        if not path_str.startswith(f"{MANPAGE_DIR.as_posix()}/"):
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
    """Check governance artifacts (.gzkit/ or docs/governance/) for substantive content.

    Foundation doctrine OBPIs ship content under docs/governance/ (trust-doctrine.md,
    advisory-rules-audit.md, distribution_invariant_catalog.md, governance_runbook.md,
    state-doctrine.md, etc.); .gzkit/ alone was too narrow and silently classified
    those OBPIs as MISSING product proof (GHI #440, extending #89's type).
    """
    for path_str in allowed_paths:
        if not (path_str.startswith(".gzkit/") or path_str.startswith("docs/governance/")):
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


def _check_closeout_artifact_proof(allowed_paths: list[str], project_root: Path) -> bool:
    """Check if a closeout-kind artifact in allowed paths exists with substantive content.

    Closeout-only OBPIs (whose work is external GHI filings, grep sweeps, and
    foundation walkthroughs) name ``ADR-CLOSEOUT-FORM.md`` and
    ``EVALUATION_SCORECARD.md`` under ``docs/design/adr/**/`` in their allowed
    paths. Those files are the durable artifacts that OBPI produces; without
    this classifier they trip the product-proof MISSING gate despite being
    substantive evidence.
    """
    for path_str in allowed_paths:
        if not path_str.startswith("docs/design/adr/"):
            continue
        filename = Path(path_str).name
        if filename not in {"ADR-CLOSEOUT-FORM.md", "EVALUATION_SCORECARD.md"}:
            continue
        artifact_path = project_root / path_str
        if not artifact_path.is_file():
            continue
        content = artifact_path.read_text(encoding="utf-8").strip()
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


_DECISION_PATTERN = re.compile(
    r"(?:Decision:\s*\*{0,2}\s*|^\*{2})(Confirm|Exclude|Absorb)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _check_decision_doc_proof(brief_text: str) -> bool:
    """Check if the brief contains a substantive Confirm/Exclude/Absorb decision.

    Decision-only OBPIs (Confirm existing code, Exclude domain-specific code)
    produce no file-based artifacts — the decision rationale in the brief IS
    the product proof.
    """
    return bool(_DECISION_PATTERN.search(brief_text))


def check_product_proof(
    adr_id: str,
    obpi_files: dict[str, Path],
    project_root: Path,
) -> ProductProofResult:
    """Validate that each OBPI in an ADR has product proof.

    Checks four proof types per OBPI (at least one must exist):
    - runbook: keyword match in docs/user/runbook.md
    - command_doc: file exists with substantive content in docs/user/manpages/
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
        raw_allowed_paths = _extract_allowed_paths(brief_text)
        allowed_paths = _expand_allowed_paths(raw_allowed_paths, project_root)
        slug = _extract_obpi_slug(obpi_id)

        runbook_found = _check_runbook_proof(obpi_id, slug, runbook_text, allowed_paths)
        command_doc_found = _check_command_doc_proof(allowed_paths, project_root)
        docstring_found = _check_docstring_proof(allowed_paths, project_root)
        governance_artifact_found = _check_governance_artifact_proof(allowed_paths, project_root)
        test_evidence_found = _check_test_evidence_proof(allowed_paths, project_root)
        bdd_evidence_found = _check_bdd_evidence_proof(allowed_paths, project_root)
        release_artifact_found = _check_release_artifact_proof(allowed_paths, project_root)
        concepts_page_found = _check_concepts_page_proof(allowed_paths, project_root)
        decision_doc_found = _check_decision_doc_proof(brief_text)
        closeout_artifact_found = _check_closeout_artifact_proof(allowed_paths, project_root)
        data_or_schema_artifact_found = _check_data_or_schema_proof(allowed_paths, project_root)

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
                concepts_page_found=concepts_page_found,
                decision_doc_found=decision_doc_found,
                closeout_artifact_found=closeout_artifact_found,
                data_or_schema_artifact_found=data_or_schema_artifact_found,
            )
        )

    missing = sum(1 for p in proofs if not p.has_proof)
    return ProductProofResult(
        adr_id=adr_id,
        success=missing == 0,
        obpi_proofs=proofs,
        missing_count=missing,
    )
