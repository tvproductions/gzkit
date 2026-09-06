"""Code quality commands for gzkit.

Provides unified interface to linting, formatting, testing, and type checking.
"""

import ast
import concurrent.futures
import json
import os
import re
import shlex
import subprocess
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS
from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.exchange_records import exchange_dir
from gzkit.handoff_validation import (
    HandoffValidationError,
    build_tracked_path_index,
    parse_frontmatter,
    validate_handoff_document,
)


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
    *,
    env_overrides: Mapping[str, str | None] | None = None,
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
        env_overrides: Per-call child-environment adjustments layered over the
            inherited environment. A ``None`` value UNSETS the variable, which a
            plain ``{**os.environ, ...}`` merge cannot express — the distinction
            matters for variables whose mere presence is the signal (GHI #793:
            ``FORCE_COLOR`` forces Rich colour when set to *anything*, so
            blanking it is not the same as removing it). Callers that need the
            child's behaviour pinned rather than inherited use this; the default
            inherits, unchanged.

    Returns:
        QualityResult with command output.

    """
    if isinstance(command, str):
        argv = shlex.split(command)
        display = command
    else:
        argv = list(command)
        display = shlex.join(argv)

    # Force UTF-8 stdio in the spawned child (GHI #661): a piped Python child
    # (behave's pretty formatter, unittest, mkdocs) otherwise picks a
    # locale-dependent stdout encoding and crashes with UnicodeEncodeError
    # emitting a non-ASCII glyph (U+2713) on a non-UTF-8 console — the write-side
    # companion of the read-side errors="replace" decode (GHI #582). This makes
    # the child's own sys.stdout UTF-8 regardless of console code page; it is a
    # no-op where the locale is already UTF-8.
    # Annotated rather than inferred: the override loop below assigns from a
    # `str | None` mapping, and without the annotation the dict widens to
    # `dict[str, str | None]`, which matches no `subprocess.run` overload.
    child_env: dict[str, str] = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for key, value in (env_overrides or {}).items():
        if value is None:
            child_env.pop(key, None)
        else:
            child_env[key] = value
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            check=False,
            env=child_env,
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


def _find_parents_access_lines(source: str) -> list[int]:
    """Find line numbers where ``Path(__file__).parents`` is accessed in code.

    Uses AST to detect ``.parents`` attribute access chained from a
    ``Path(__file__)`` call. String literals and comments containing the
    pattern text are not flagged.

    BOTH forms are positional root derivations and both are flagged: the
    subscripted ``Path(__file__).parents[2]`` and the bare
    ``for p in Path(__file__).parents``. Matching only ``ast.Subscript`` left
    the bare form uncovered, which is why `hardcoded-root-eradication` had to
    carry text-matching greps over ``src/gzkit/eval/`` and ``src/gzkit/hooks/``
    as its only witness for it — greps that could not tell code from a comment
    and failed on one (GHI #782). Widening here is what made those greps safe
    to delete without losing coverage.

    ``Path(__file__).parent`` (singular) is a different attribute, is not a
    positional walk, and is not flagged.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or node.attr != "parents":
            continue
        inner = node.value
        while isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
            inner = inner.func.value
        if not (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)):
            continue
        if inner.func.id != "Path":
            continue
        if inner.args and isinstance(inner.args[0], ast.Name) and inner.args[0].id == "__file__":
            violations.append(node.lineno)
    return sorted(set(violations))


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
        hit_lines = _find_parents_access_lines(source)
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
    # Lint the whole repository (matching ``ruff format .`` and the pre-commit
    # ruff-check hook), not just ``src tests`` — a narrower scope let lint pass
    # in ``gz check`` while the pre-commit hook blocked the same file at commit
    # time (the "green here, red at commit" gate divergence). ruff honors its
    # own excludes + .gitignore, so generated/vendored trees are skipped.
    ruff_result = run_command("uv run ruff check .", cwd=project_root)
    path_contract_result = run_adr_path_contract_lint(project_root)
    parents_result = run_parents_pattern_lint(project_root)

    sub_results = [ruff_result, path_contract_result, parents_result]
    success = all(r.success for r in sub_results)
    returncode = 0 if success else next((r.returncode for r in sub_results if not r.success), 1)
    stdout = "\n".join(output for output in [r.stdout for r in sub_results] if output.strip())
    stderr = "\n".join(output for output in [r.stderr for r in sub_results] if output.strip())

    return QualityResult(
        success=success,
        command="uv run ruff check . + ADR path contract lint + parents-pattern lint",
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

    # Then run ruff check --fix over the whole repo (same scope as run_lint and
    # the pre-commit ruff-check hook), so the auto-fixer covers everything the
    # lint gate checks.
    fix_result = run_command("uv run ruff check --fix .", cwd=project_root)

    # Combine results
    return QualityResult(
        success=fix_result.success,
        command="uv run ruff format . && uv run ruff check --fix .",
        stdout=format_result.stdout + "\n" + fix_result.stdout,
        stderr=format_result.stderr + "\n" + fix_result.stderr,
        returncode=fix_result.returncode,
    )


def run_typecheck(project_root: Path) -> QualityResult:
    """Run type checking (ty check).

    The command is READ from ``CANONICAL_STEP_COMMANDS["typecheck"]`` rather
    than re-spelled here. GHI #199 was an ARB receipt labelled ``typecheck``
    measuring a different scope than this gate; re-spelling the command in both
    places is what made that divergence possible, and a test asserting the two
    agree would only detect it after the fact. Deriving makes it unrepresentable.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from type checking.

    """
    return run_command(CANONICAL_STEP_COMMANDS["typecheck"], cwd=project_root)


def run_tests(project_root: Path) -> QualityResult:
    """Run the unittest test suite via the parallel runner.

    The command is READ from ``CANONICAL_STEP_COMMANDS["unittest"]`` rather than
    re-spelled here, exactly as ``run_typecheck`` reads its own entry. GHI #856
    was this gate and the ARB attestation label of the same name running
    DIFFERENT commands: the ``unittest-parallel`` accelerator was adopted here
    and on the pre-commit hook (GHI #512) and never carried to the attestation
    surface, so proving "Tests pass" cost 144.23s while this gate proved the
    same tree in 41.34s. Re-spelling the command in both places is what made
    that divergence possible; a test asserting the two agree would only detect
    it after the fact. Deriving makes it unrepresentable.

    ``--buffer`` captures each test's stdout/stderr and replays it ONLY for tests
    that fail or error (GHI #723). Negative-path tests deliberately trigger
    fail-closed surfaces, and ``.gzkit/rules/guardrail-feedback-prose.md``
    requires those surfaces to emit rich, alarming, actionable prose — so a
    PASSING negative-path test used to print a convincing failure into the CI
    log. The log for a run with exactly one real failure carried 26 error-shaped
    lines across 303, and triage twice targeted a fixture instead of the defect,
    each time proposing a remedy that would have made a negative control unable
    to fail. Buffering removes the noise without weakening any test: a genuine
    failure still replays its own output under a ``Stderr:`` section.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from testing.

    """
    return run_command(CANONICAL_STEP_COMMANDS["unittest"], cwd=project_root)


def run_behave(project_root: Path, tags: list[str] | None = None) -> QualityResult:
    """Run BDD scenarios via behave, optionally filtered by tag list.

    Three verification contracts share this one function. State the scope per
    call site, never as a blanket -- the ``tags`` parameter existing is not
    evidence that a caller passing none has overlooked it:

      ``quality.run_all_checks``     -> NO tags; the ``gz check`` gate
      ``gz test --bdd``              -> NO tags; ADR closeout, same full scope
      ``_run_obpi_scoped_behave``    -> tags from ``resolve_obpi_behave_tags``,
                                        i.e. the REQs of one OBPI brief

    THE GATE RUNS UNFILTERED ON PURPOSE, and the purpose is recorded here for
    the first time (operator ruling 2026-08-26; the call had read as an
    unreasoned claim). Measured that day: 443 scenarios across 68 feature
    files, of which 326 carry an effective ``@REQ-`` tag and 117 do NOT. The
    untagged 117 cluster by file rather than scattering -- 29 in
    ``subagent_pipeline.feature``, 12 in ``task_governance.feature``, 9 each in
    ``obpi_lock.feature`` and ``persona.feature`` -- and NO feature file
    carries a feature-level tag, so tag inheritance covers nothing. A
    ``@REQ``-based filter at the gate would therefore drop a quarter of the
    suite silently, which is a gate verifying less rather than a gate running
    faster. The rest of the vocabulary cannot partition it either: past
    ``@wip`` (35, already excluded beneath every call by ``behave.ini``'s
    ``default_tags = ~@wip``) and ``@dispatch`` (31), every tag is a
    near-singleton. Behave is ~34% of ``gz check`` wall clock (34.2s of 100.4s,
    10-core host, same date); that cost is bought coverage. Re-measure before
    proposing any selection predicate -- these are dated measurements, not
    thresholds anything reads.

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

    shards = _plan_behave_shards(project_root, _behave_shard_count(project_root))
    if len(shards) < 2:
        return run_command("uv run -m behave", cwd=project_root)
    return _run_behave_shards(project_root, shards)


def _behave_shard_count(project_root: Path) -> int:
    """Return the declared Behave shard count; 1 means single-process.

    Read from ``data/check_step_concurrency.json`` under the root PASSED IN,
    never an ambient one -- the same discipline `_ruff_format_dir` had to learn
    the hard way (GHI #909), and the cwd-capture shape GHI #857 tracks.

    An absent or unreadable declaration means one process, which is exactly
    today's behaviour. That is the case in ADOPTER projects, on the same footing
    as ``_step_concurrency_classes``: the declaration describes gzkit's own step
    set and is project-local, so this speedup is gzkit's own and adopters are
    unaffected rather than broken. Shipping it to them would mean inventing a
    package-data surface, which is scope this change does not carry.
    """
    path = project_root / "data" / "check_step_concurrency.json"
    if not path.is_file():
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        count = int(data["steps"]["Behave"]["shards"])
    except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError):
        return 1
    return max(count, 1)


def _plan_behave_shards(project_root: Path, count: int) -> list[list[Path]]:
    """Partition ``features/*.feature`` into ``count`` size-balanced shards.

    Longest-processing-time: heaviest file first, each into the lightest shard
    so far. Byte size is a proxy for runtime, and a coarse one -- it is used
    because it is free and monotonic, not because it is accurate.

    THE PARTITION IS THE SAFETY PROPERTY. Every file lands in exactly one shard,
    which is what conserves the scenario set and what keeps the one feature that
    writes ``dist/`` inside a single process. Balance is only the speedup.

    Discovery is RECURSIVE because behave's own is: ``uv run -m behave`` walks
    ``features/`` to any depth, while ``_run_behave_shards`` passes only the
    paths planned here. A non-recursive glob therefore does not shard the work
    differently, it drops it -- silently, under a green ``✓ Behave`` (GHI #917).
    """
    features_dir = project_root / "features"
    if count < 2 or not features_dir.is_dir():
        return []
    by_weight = sorted(
        features_dir.rglob("*.feature"), key=lambda p: p.stat().st_size, reverse=True
    )
    if len(by_weight) < 2:
        return []

    buckets: list[list[Path]] = [[] for _ in range(min(count, len(by_weight)))]
    weights = [0] * len(buckets)
    for feature in by_weight:
        lightest = weights.index(min(weights))
        buckets[lightest].append(feature)
        weights[lightest] += feature.stat().st_size
    return buckets


def _run_behave_shards(project_root: Path, shards: list[list[Path]]) -> QualityResult:
    """Run each shard in its own process and aggregate one QualityResult.

    Threads dispatch subprocesses; nothing behave-related runs in this
    interpreter. That matters because ``features/environment.py`` ``chdir``s per
    scenario and ``os.chdir`` is process-global -- scenarios can never be
    threaded inside one interpreter, and can always be split across processes.
    """

    def one(shard: list[Path]) -> QualityResult:
        argv = ["uv", "run", "-m", "behave", *[str(path) for path in shard]]
        return run_command(argv, cwd=project_root)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(shards)) as pool:
        results = list(pool.map(one, shards))
    return _aggregate_shard_results(results, [[p.name for p in shard] for shard in shards])


def _aggregate_shard_results(
    results: list[QualityResult], shard_names: list[list[str]]
) -> QualityResult:
    """Fold shard results into one, FAILING SHARDS FIRST and attributed.

    Concurrent runs produce one summary each, so without ordering and
    attribution an operator scrolls a 400-scenario transcript to find which one
    broke. A gate whose failures are hard to read is a gate people route around,
    which is a worse outcome than the seconds this saves.
    """
    ordered = sorted(range(len(results)), key=lambda i: results[i].success)
    blocks: list[str] = []
    error_blocks: list[str] = []
    for i in ordered:
        result = results[i]
        verdict = "passed" if result.success else f"FAILED (exit {result.returncode})"
        header = (
            f"===== behave shard {i + 1}/{len(results)} {verdict} "
            f"[{', '.join(shard_names[i])}] ====="
        )
        blocks.append(f"{header}\n{result.stdout}")
        if result.stderr:
            error_blocks.append(f"{header}\n{result.stderr}")

    codes = [result.returncode for result in results]
    failed = [code for code in codes if code != 0]
    return QualityResult(
        success=not failed,
        command=f"uv run -m behave (sharded x{len(results)})",
        stdout="\n".join(blocks),
        stderr="\n".join(error_blocks),
        returncode=max(failed) if failed else 0,
    )


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
    # Unfiltered on purpose -- see ``run_behave``'s docstring for the
    # 2026-08-26 measurement (117 of 443 scenarios carry no ``@REQ`` tag).
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


def run_mkdocs(project_root: Path) -> QualityResult:
    """Build the docs site strictly, so broken nav and dead links fail closed.

    ``mkdocs build --strict`` was already a canonical ARB step
    (``CANONICAL_STEP_COMMANDS``) and the Gate-3 docs command, but it was never
    in the ``gz check`` aggregator. That gap let a stale ``mkdocs.yml`` nav
    entry — pointing at a manpage renamed in an earlier pass — sit broken under
    a fully green ``gz check`` until a rename sweep happened to run the build by
    hand (observed 2026-07-26). Dead enforcement of the class GHI #515 named:
    a real gate that nothing routes into the aggregator operators actually run.

    Absent ``mkdocs.yml`` the project ships no docs site, and the step passes.
    Adopter projects are not required to author one, so failing on the absence
    of a file they never wrote would make ``gz check`` unadoptable — the same
    presence-test shape ``gz audit`` already uses for its docs arm.
    """
    if not (project_root / "mkdocs.yml").is_file():
        return QualityResult(
            success=True,
            command="uv run mkdocs build --strict",
            stdout="skipped: no mkdocs.yml (project ships no docs site)",
            stderr="",
            returncode=0,
        )
    return run_command("uv run mkdocs build --strict", cwd=project_root)


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


def run_python_version_pins_audit(project_root: Path) -> QualityResult:
    """Run the interpreter-pin coherence audit.

    Fails closed when a CI workflow declares a Python version that disagrees
    with `.python-version`, which is what uv resolves the project interpreter
    from. Without it the two drift silently and both sides stay green.
    """
    return run_command("uv run gz validate --python-version-pins", cwd=project_root)


def run_validate_default_scopes(project_root: Path) -> QualityResult:
    """Run every default-tier `gz validate` scope in one pass (GHI #744).

    Ten default-tier scopes — manifest, ledger, documents, briefs, frontmatter,
    personas, surfaces, version, instructions, rule_version_markers — were
    registered but unreachable from `gz check`, which is how a
    `--rule-version-markers` breach survived eight days of green commits.

    A BARE `gz validate` runs the whole default tier in a single subprocess
    (~2s for 12 scopes), so enrolling them costs one process rather than ten.
    Flag-scoped steps stay separate where a step needs its own name in the
    progress display or its own MX seam.
    """
    return run_command("uv run gz validate", cwd=project_root)


def run_adr_status_fresh_audit(project_root: Path) -> QualityResult:
    """Run the adr-status.md freshness audit (GHI #322 / Architectural Boundary 6).

    Fails closed when `docs/governance/GovZero/adr-status.md` drifts from
    on-disk ADR canon — the original surface that GHI #322 surfaced.
    Recovery: `uv run gz register-adrs` regenerates the index.
    """
    return run_command("uv run gz validate --adr-status-fresh", cwd=project_root)


def run_pool_interview_audit(project_root: Path) -> QualityResult:
    """Run the pool ADR interview schema audit (GHI #719).

    Fails closed when a `docs/design/adr/pool/*-interview.json` record drifts
    from the answers schema `gz interview adr --from` already enforces.

    Enrolled as a `gz check` step rather than left flag-gated, for the reason
    GHI #754 records one function below: a gate nobody pulls cannot fail. The
    defect this closes IS the asymmetry — the non-pool path validates on every
    single use, so a pool-side check that runs only when an operator remembers
    the flag would leave the two guarantees exactly as unequal as GHI #719
    found them.
    """
    return run_command("uv run gz validate --pool-interview", cwd=project_root)


def run_advisory_scorecard_audit(project_root: Path) -> QualityResult:
    """Run the advisory-scorecard coverage audit (GHI #212 / GHI #754).

    Fails closed when a canonical rule under `.gzkit/rules/` is absent from the
    scorecard's Coverage Ledger, or has been bumped past the rule-version it was
    last scored at — unreviewed coverage in the surface that tracks which
    doctrine is mechanically enforced.

    Enrolled as a `gz check` step under GHI #754. It had been registered
    `explicit`, so it ran in no pipeline at all: not in the default validate
    tier, not in pre-commit, not in CI. A gate nobody pulls cannot fail, and its
    absence from `gz check` also kept it outside the ADR-0.0.73 QC-step
    registry — which is derived from what `gz check` actually runs (Boundary
    Invariant #1) — so it carried no negative control either.

    Recovery: `uv run gz validate --advisory-scorecard` names each unscored rule
    and the ledger row to add.
    """
    return run_command("uv run gz validate --advisory-scorecard", cwd=project_root)


def run_taxonomy_audit(project_root: Path) -> QualityResult:
    """Run the ADR taxonomy gate (ADR-0.34.0 Foundation Sunset, OBPI-05).

    Fails closed on a `kind: foundation` ADR absent from the closed grandfather
    manifest (OBPI-01's closed-kind + manifest-integrity assertions) or on a
    grandfathered foundation left in non-terminal `foundation_limbo`
    (OBPI-03's terminal-partition assertion, read from Layer-2 never frontmatter).
    Recovery: `uv run gz validate --taxonomy` names the offending ADR ids.
    """
    return run_command("uv run gz validate --taxonomy", cwd=project_root)


def run_obpi_lifecycle_coherence_audit(project_root: Path) -> QualityResult:
    """Run the OBPI lifecycle-coherence census (GHI #584 / Architectural Boundary 6).

    Fails closed when an `obpi_created` event carries no disposition and either
    its parent ADR does not resolve or its brief is absent from disk — Layer-2
    asserting an artifact Layer-1 cannot show. Recovery:
    `uv run python -m gzkit.governance.obpi_park_backfill --dry-run`.
    """
    return run_command("uv run gz validate --obpi-lifecycle-coherence", cwd=project_root)


def run_adversarial_validation_audit(project_root: Path) -> QualityResult:
    """Run the Step-4b adversary-verdict capture gate (GHI #676).

    Fails closed when a post-cutover heavy-lane completion receipt carries no
    paired `adversarial_validation` ledger event, when a refuted verdict has no
    recorded resolution, or when a terminal heavy-lane brief omits its
    `### Step 4b` evidence section.
    Recovery: re-run `uv run gz obpi complete` with `--adversary-verdict` and
    `--adversary`, or add the brief's Step-4b section.
    """
    return run_command("uv run gz validate --adversarial-validation", cwd=project_root)


def run_red_parity_audit(project_root: Path) -> QualityResult:
    """Run the BEHAVIOR-REQ RED falsifiability gate (GHI #642).

    Fails closed when a post-cutover heavy-lane BEHAVIOR REQ carries no
    `red_receipt_emitted` witness, or carries one whose `failure_class` is `none`
    (its covering test passed with the production hunks withheld, so it cannot fail).
    Recovery: `uv run gz arb red --req <REQ> --obpi <OBPI>`.
    """
    return run_command("uv run gz validate --red-parity", cwd=project_root)


def run_producer_fields_audit(project_root: Path) -> QualityResult:
    """Run the producer-side ledger contract-parity gate (GHI #877, reopened).

    Fails when a ledger producer writes a payload field that `schemas/ledger.json`
    or the typed union does not declare. The typed union is `extra="forbid"`, so
    such a producer writes a row that replay then refuses — and a fence reading
    committed rows cannot see it until the producer first fires.
    Recovery: declare the field in BOTH contracts.
    """
    return run_command("uv run gz validate --producer-fields", cwd=project_root)


def run_rendition_freshness_audit(project_root: Path) -> QualityResult:
    """Run the rendition-freshness gate (OBPI-0.0.37-22).

    Fails closed (exit 3) when the corpus has mutated after the committed
    rendition for any (surface, consumer) pair.
    Recovery: `uv run gz content compose <surface>` and attest.
    """
    return run_command("uv run gz validate --rendition-freshness", cwd=project_root)


def run_rendition_floor_coherence_audit(project_root: Path) -> QualityResult:
    """Run the canon→rendition invariant-floor gate (GHI #623, corrective to ADR-0.0.37).

    Fails closed (exit 3) when a committed rendition omits an invariant-tier
    corpus entry — the content witness `--rendition-freshness` (a timestamp
    comparison) does not perform.
    Recovery: `uv run gz content compose <surface>` with a candidate carrying
    every invariant entry verbatim, then recommit the rendition.
    """
    return run_command("uv run gz validate --rendition-floor-coherence", cwd=project_root)


def run_brief_structure_audit(project_root: Path) -> QualityResult:
    """Run the OBPI brief structural-schema gate (GHI #615 cut 3).

    Fails closed when a live (non-terminal) brief does not satisfy
    ``BriefStructure``. The schema shipped with ADR-0.0.37-04 but nothing ever
    enforced it — ``parse_brief`` defaulted to permissive and briefs fell back
    to regex-scraped ``LegacyBriefShape``. Sealed briefs are out of scope: their
    only available repair would rewrite an attested artifact. Recovery:
    `uv run python scripts/migrate_brief_frontmatter.py --dry-run`.
    """
    return run_command("uv run gz validate --brief-structure", cwd=project_root)


def run_invariant_coherence_audit(project_root: Path) -> QualityResult:
    """Run the composition-drift gate: AGENTS.md vs committed rendition playback.

    Fails closed when a rendered surface (AGENTS.md) has drifted from the
    committed rendition it is played back from (ADR-0.0.37). governance-core
    declares this gate "in the gz check default scope"; its omission from the
    curated pipeline let committed AGENTS.md<->rendition drift sail through the
    pre-push gate silently. The validator is clean-run-pure (no ledger write on
    match), so it is gate-safe like its rendition siblings. Recovery on drift:
    `uv run gz agent sync control-surfaces` to re-render, then commit.
    """
    return run_command("uv run gz validate --invariant-coherence", cwd=project_root)


def run_wheel_path_literals_audit(project_root: Path) -> QualityResult:
    """Run the delivered-instruction resolvability gate over wheel-shipped Markdown.

    Fails closed when content the wheel hands an adopter names a path only the
    authoring environment can resolve (GHI #900). ``--distribution`` proves the
    bytes ARRIVE; it never asked whether the instruction they carry RESOLVES.

    Wired here explicitly even though the scope is default-tier, for the reason
    its `corpus_retirement_witness` sibling records: the reachability ratchet
    reads this curated pipeline, not the bare-`gz validate` default tier, so a
    scope absent here reads as ungated -- which for a check whose whole subject
    is inert coverage would be the defect wearing the fix's clothes. Recovery:
    replace the literal with a reader-supplied override, a repo-relative path,
    or a `$HOME`/`~` form, and move the surrounding prose with it.
    """
    return run_command("uv run gz validate --wheel-path-literals", cwd=project_root)


def run_corpus_retirement_witness_audit(project_root: Path) -> QualityResult:
    """Run the corpus retirement-witness gate: Layer-1 tombstone vs Layer-2 witness.

    Fails closed when a corpus retraction row changed canon with no ledger event
    naming the id it retired (GHI #885 bypass ingress, GHI #878 partial write).
    Subject-bound: a witness matches by ``retired_entry_id``, never by event type
    alone. Wired here explicitly even though the scope is default-tier, matching
    its `invariant_coherence` sibling -- the reachability ratchet reads the
    curated pipeline, not the bare-`gz validate` default tier, so a scope absent
    here reads as ungated. Recovery: `uv run gz content reconcile-retirements
    <surface>`.
    """
    return run_command("uv run gz validate --corpus-retirement-witness", cwd=project_root)


def run_session_green_gate_audit(project_root: Path) -> QualityResult:
    """Run the session-green-gate declaration audit (ADR-0.0.68 / OBPI-0.0.68-02).

    Fails closed (exit 3) when .pre-commit-config.yaml declares no
    stages: [pre-push] hook running gz check. Recovery: add the hook
    (OBPI-0.0.68-01) and run pre-commit install --hook-type pre-push.
    """
    return run_command("uv run gz validate --session-green-gate", cwd=project_root)


def run_closeout_proof_audit(project_root: Path) -> QualityResult:
    """Run the closeout-proof derived view (ADR-0.0.69 / OBPI-0.0.69-03).

    Fails closed (exit 3) when any in-closeout ADR has unproven REQs.
    Exit 0: all proven. Exit 3: any unproven. Exit 2: dispatch I/O error.
    Recovery: ``gz validate --closeout-proof`` to see per-REQ details.
    """
    return run_command("uv run gz validate --closeout-proof", cwd=project_root)


def run_kind_invariance_audit(project_root: Path) -> QualityResult:
    """Run the kind-invariance audit for foundation-tier ADRs (OBPI-0.0.35-04).

    Fails closed when any ``kind: foundation`` ADR is missing or has a
    placeholder-only "## Why foundation tier?" section. Recovery: add/update
    the section with a substantive one-sentence answer to the invariance test
    ('Without this ADR, the project would not be the project because ...').
    """
    return run_command("uv run gz validate --kind-invariance", cwd=project_root)


def run_persona_witness_audit(project_root: Path) -> QualityResult:
    """Run the persona-witness audit for ADRs (GHI #741).

    Fails closed when any ADR is missing ``## Persona`` or carries a body with
    no authored content — a placeholder token, an unfilled author-prompt, or
    unsubstituted template residue such as ``{persona}``. Recovery: author the
    behavioral identity for agents working on that ADR (``uv run gz personas
    list`` for reusable definitions). Pre-cutover population is booked in
    ``data/persona_grandfather.json``, which is shrink-only.
    """
    return run_command("uv run gz validate --persona-witness", cwd=project_root)


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


def run_status_writer_coverage_audit(project_root: Path) -> QualityResult:
    """Run the OBPI-status writer-coverage audit (GHI #669).

    Fails closed (exit 3) when a function under ``src/gzkit/**`` writes a
    frontmatter ``status:`` key without consulting the single invariant monitor
    ADR-0.31.0 Decision item 4 declares, and without a registered reason.
    Recovery: route the write through ``guarded_obpi_status_write``, or consult
    ``obpi_status_write_refusal`` directly and supply your own consequence, or —
    if the writer does not touch an OBPI brief — register it with a reason
    naming its scope in ``trust_audits/status_writer_coverage.py``.
    """
    return run_command("uv run gz validate --status-writer-coverage", cwd=project_root)


def run_transcribed_adr_counts_audit(project_root: Path) -> QualityResult:
    """Run the transcribed-ADR-count audit (GHI #768).

    Fails closed (exit 3) when a surface declared live in
    ``data/transcribed_count_surfaces.json`` states an ADR's OBPI count as a
    number. The count is computed by ``gz adr status``; a second copy in prose
    has no reconciliation path and goes stale on the next add, withdraw, park,
    or fold. Recovery: delete the number and cite the command. A DATED RECORD
    belongs under a declared historical section or carries the inline
    ``<!-- historical-count -->`` marker — never rewrite history to match today.
    """
    return run_command("uv run gz validate --transcribed-adr-counts", cwd=project_root)


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


def run_task_envelope_coherence_audit(project_root: Path) -> QualityResult:
    """Run the task-envelope-coherence audit (ADR-0.0.64 / OBPI-04).

    Fails closed (exit 3) on Heavy lane when: (a) worklog events are emitted
    under an active TASK with no task_id, (b) an OBPI has all-seq=01 TASKs and
    no req_atomic exemption, or (c) layer-drift across the four discovery channels.
    Recovery: populate task_id on worklog events, use gz task start --seq next
    for subdivision, or declare req_atomic in brief frontmatter for atomic REQs.
    """
    return run_command("uv run gz validate --task-envelope-coherence", cwd=project_root)


def run_lock_exchange_coupling_audit(project_root: Path) -> QualityResult:
    """Run the lock-handoff coupling audit (ADR-0.0.41 / OBPI-04).

    Fails closed (exit 3) when any obpi_lock_released event in the ledger
    (post-OBPI-02 cutover) lacks a valid handoff_path, references a missing
    file, has a predated frontmatter timestamp, or is missing min-info fields.
    Recovery: uv run gz validate --lock-exchange-coupling for diagnostics.
    """
    return run_command("uv run gz validate --lock-exchange-coupling", cwd=project_root)


def run_qc_binding_audit(project_root: Path) -> QualityResult:
    """Run the QC-binding behavioral audit (ADR-0.0.73 / OBPI-0.0.73-02).

    Fails closed (exit 3) when any bound QC step exhibits a theater signature
    or passes its own negative-control fixture.
    Recovery: uv run gz validate --qc-binding to see per-step details.
    """
    return run_command("uv run gz validate --qc-binding", cwd=project_root)


def run_enforcement_floor_audit(project_root: Path) -> QualityResult:
    """Run the enforcement-claim meta-validator as a gz check step (ADR-0.0.74/OBPI-19).

    READ-ONLY on a clean run — no ledger mutation when all claims PASS (root=None).
    Fails closed when any enrolled claim lacks a passing un-forced NC (FACADE or TEST_BUG).
    Recovery: uv run gz validate --qc-binding to see per-step details; address any FACADE.
    """
    from gzkit.enforcement import run_meta_validator  # noqa: PLC0415

    result = run_meta_validator(root=None)
    failures = [r for r in result.claim_results if r.outcome != "PASS"]
    if failures:
        output = "\n".join(r.message for r in failures)
        return QualityResult(
            success=False,
            command="enforcement-floor-audit",
            stdout=output,
            stderr="",
            returncode=3,
        )
    return QualityResult(
        success=True,
        command="enforcement-floor-audit",
        stdout=f"Enforcement floor: {result.verified_count} claims verified.",
        stderr="",
        returncode=0,
    )


def run_fidelity_presence_audit(project_root: Path) -> QualityResult:
    """Run the fidelity-presence enforcement audit (ADR-0.0.73 / OBPI-0.0.73-08).

    Fails closed (exit 3) when any non-pool ADR Decision lacks a parseable
    ## Fidelity Assertions block (Boundary Invariant #4), minus the
    grandfathered pre-existing block-less ADRs in
    data/fidelity_presence_grandfather.json.
    Recovery: uv run gz validate --fidelity-presence to see the offending ADRs.
    """
    return run_command("uv run gz validate --fidelity-presence", cwd=project_root)


def run_waiver_ratchet_audit(project_root: Path) -> QualityResult:
    """Run the waiver-ratchet honesty audit (ADR-0.0.73 / OBPI-0.0.73-09).

    Fails closed (exit 3) when any registered waiver/grandfather/baseline surface
    lacks or violates its declared honesty mechanism (closed-set lock, dated
    cutover, or monotonic shrink-ratchet), or when an on-disk waiver data file is
    not registered (the silent-bypass). Mechanizes Boundary Invariant #8.
    Recovery: uv run gz validate --waiver-ratchet to see the offending surfaces.
    """
    return run_command("uv run gz validate --waiver-ratchet", cwd=project_root)


def run_config_registry_audit(project_root: Path) -> QualityResult:
    """Run the config-registry declaration gate (GHI #929).

    Fails closed (exit 3) when a top-level ``data/*.json`` registry is owned by
    neither ``data/config_registry.json`` nor ``data/waiver_ratchet_registry.json``,
    when a declared registry is a phantom, when a declared owner does not actually
    reference its registry, or when a ``relates_to`` edge is one-way. Companion to
    the waiver-ratchet gate; between them the two are exhaustive over ``data/*.json``.
    Recovery: uv run gz validate --config-registry to see the offending surfaces.
    """
    return run_command("uv run gz validate --config-registry", cwd=project_root)


def run_gate_callers_audit(project_root: Path) -> QualityResult:
    """Run the uncalled-gate inventory (GHI #785).

    Fails closed (exit 3) when a validate scope or chore gate script has no
    automatic caller and is not recorded in data/uncalled_gate_grandfather.json,
    or when an acceptance has gone stale (the gate gained a caller, or no longer
    exists). This is the only mechanism that asks which gates nothing invokes;
    every other reachability check polices its own membership.
    Recovery: uv run gz validate --gate-callers to see the offending gates.
    """
    return run_command("uv run gz validate --gate-callers", cwd=project_root)


def run_exemption_controls_audit(project_root: Path) -> QualityResult:
    """Run the exemption-control inventory (GHI #797).

    Fails closed (exit 3) when an enforcement claim has not declared whether
    its gate has an exemption surface and is not recorded in
    data/exemption_control_grandfather.json, when a declaration names a
    control that is not registered, or when an acceptance has gone stale.
    A gate with an exemption makes two claims and the floor proved only the
    first; four gates failed on the second half in one session, two of them
    while their controls were registered, enrolled and passing.
    Recovery: uv run gz validate --exemption-controls to see the claims.
    """
    return run_command("uv run gz validate --exemption-controls", cwd=project_root)


# Handoff-document enforcement cutover (OBPI-0.0.72-02). Register entries
# authored on or after this instant MUST pass validate_handoff_document; the
# pre-existing legacy entries under .gzkit/handoffs/ that predate this gate are
# grandfathered so the wiring lands green over the existing corpus. This mirrors
# the lock_exchange_coupling cutover posture (grandfather legacy, fail-close
# go-forward). The boundary sits just past the newest existing entry; legacy
# cleanup is tracked separately (see OBPI-0.0.72-02 evidence/concerns).
_HANDOFF_ENFORCEMENT_CUTOVER = "2026-06-15T00:00:00Z"

# Section-population grandfather (GHI #692). Path-scoped, NOT date-scoped: the
# four hollow entries were authored 2026-07-15, a month AFTER the cutover above,
# so moving that date forward to cover them would also re-open every other
# post-cutover contract. Registered as a `shrink-ratchet` honesty surface in
# data/waiver_ratchet_registry.json; the file's _doc carries the rationale.
_HANDOFF_SECTION_GRANDFATHER_REL = "data/handoff_section_grandfather.json"
_HANDOFF_SECTION_ENTRIES_KEY = "grandfathered_handoffs"


def _handoff_section_grandfather(project_root: Path) -> frozenset[str]:
    """Return the repo-relative handoff paths whose empty sections are tolerated.

    Fails OPEN to the empty set (enforce everything) when the manifest is absent
    or unreadable: a missing waiver file must never silently widen the gate. The
    waiver-ratchet audit is what fail-closes on an unregistered or grown file.
    """
    path = project_root / _HANDOFF_SECTION_GRANDFATHER_REL
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return frozenset()
    if not isinstance(payload, dict):
        return frozenset()
    entries = payload.get(_HANDOFF_SECTION_ENTRIES_KEY)
    if not isinstance(entries, list):
        return frozenset()
    return frozenset(str(entry) for entry in entries)


def _is_non_obpi_register_entry(content: str) -> bool:
    """Return True when a register entry is for a lock key that is not an OBPI token.

    The token-block invariant governs OBPI tokens. The MX hangar's `mx-session`
    lock rides the same lock rail but is a session mutex, not a token, so its
    release record has no OBPI id and no parent ADR to carry (GHI #848).
    """
    return bool(re.search(r"^obpi_id:\s*(?!OBPI-)\S+", content, re.MULTILINE))


def _handoff_predates_cutover(content: str, cutover: datetime) -> bool:
    """Return True when a handoff is grandfathered (pre-cutover or undatable).

    Datability keys off the frontmatter ``timestamp`` (which every canonical
    writer emits). An entry whose frontmatter is unparseable or carries no
    parseable timestamp is treated as legacy and grandfathered — it cannot have
    been authored by the reconciled go-forward writers.
    """
    try:
        frontmatter = parse_frontmatter(content)
    except HandoffValidationError:
        return True
    raw = frontmatter.get("timestamp")
    if not isinstance(raw, str):
        return True
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed < cutover


def run_handoff_document_audit(project_root: Path) -> QualityResult:
    """Gate-wire validate_handoff_document over both register-entry stores (OBPI-0.0.72-02).

    Before this gate, validate_handoff_document was a strict consumer with no
    authoring-time enforcement, so invalid-frontmatter register entries shipped.
    Each entry authored on or after _HANDOFF_ENFORCEMENT_CUTOVER must validate
    clean; pre-cutover (and undatable) legacy entries are grandfathered so the
    gate lands green over the existing corpus.

    Scans BOTH `.gzkit/handoffs/` (session handoffs, ADR-0.0.65) and
    `.gzkit/locks/exchange/` (token exchange records, ADR-0.0.41). The two are
    separate systems that share only a document format (GHI #763), and that shared
    format is exactly why one validator covers both. Adding the second directory
    here is not optional bookkeeping: when the exchange writers moved out of
    `.gzkit/handoffs/`, a single-directory scan would have silently dropped every
    exchange record from the only authoring-time gate they had, and the gate would
    have kept reporting green.
    """
    stores = [project_root / ".gzkit" / "handoffs", exchange_dir(project_root)]
    present = [d for d in stores if d.is_dir()]
    if not present:
        return QualityResult(
            success=True,
            command="handoff-document audit",
            stdout="No register-entry store on disk; skipping.",
            stderr="",
            returncode=0,
        )

    cutover = datetime.fromisoformat(_HANDOFF_ENFORCEMENT_CUTOVER.replace("Z", "+00:00"))
    section_waived = _handoff_section_grandfather(project_root)
    # One tracked-path index for the whole corpus (GHI #858). Built here rather
    # than per document because this is the only caller that validates hundreds
    # in one pass, and it is the reason the step cost 19% of `gz check`.
    git_index = build_tracked_path_index(project_root)
    blocking: list[str] = []
    grandfathered = 0
    hollow = 0
    for path in sorted(p for d in present for p in d.glob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # HandoffFrontmatter is the OBPI token-block contract: it requires a
        # well-formed OBPI id and parent ADR. A register entry for a NON-OBPI
        # lock key - the `mx-session` mutex - cannot satisfy it by construction,
        # so scanning it asserts a contract it can never meet and traps the
        # tree: the ledger event is append-only and references the record, so
        # the record cannot be deleted either (GHI #848).
        if _is_non_obpi_register_entry(content):
            continue
        rel = path.relative_to(project_root).as_posix()
        allow_empty = rel in section_waived
        violations = validate_handoff_document(
            content, project_root, allow_empty_sections=allow_empty, git_index=git_index
        )
        if allow_empty:
            hollow += 1
        if not violations:
            continue
        if _handoff_predates_cutover(content, cutover):
            grandfathered += 1
            continue
        blocking.extend(f"{rel}: {violation}" for violation in violations)

    if blocking:
        return QualityResult(
            success=False,
            command="handoff-document audit",
            stdout=(
                "Handoff register entries authored on/after the enforcement cutover "
                f"({_HANDOFF_ENFORCEMENT_CUTOVER}) failed validate_handoff_document:\n"
                + "\n".join(blocking)
            ),
            stderr=(
                "A register entry is fail-closed on the token-block invariant "
                "(.gzkit/rules/token-block-discipline.md): its frontmatter must "
                "satisfy HandoffFrontmatter and it must carry the seven required "
                "sections. Fix the offending frontmatter/sections and re-run "
                "uv run gz check."
            ),
            returncode=3,
        )

    summary = "All post-cutover handoff register entries valid."
    if grandfathered:
        plural = "entry" if grandfathered == 1 else "entries"
        summary += f" ({grandfathered} pre-cutover legacy {plural} grandfathered.)"
    if hollow:
        # State the waived set in the PASS line, not only in the manifest. A green
        # that hides what it did not check is the GHI #692 facade one level up.
        plural = "entry" if hollow == 1 else "entries"
        summary += (
            f" ({hollow} hollow {plural} tolerated per {_HANDOFF_SECTION_GRANDFATHER_REL}"
            " — sections empty, context NOT preserved; shrink-only.)"
        )
    return QualityResult(
        success=True,
        command="handoff-document audit",
        stdout=summary,
        stderr="",
        returncode=0,
    )


def run_surface_fidelity_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.33-05 surface-fidelity composite.

    Fails closed when any of bullet_retention, surface_weight or
    pointer_integrity report errors. Invariant 4 (scenario reachability)
    was retired 2026-07-25 — see ADR-0.0.33 § Amendment (2026-07-25).
    """
    return run_command("uv run gz validate --surface-fidelity", cwd=project_root)


def run_line_endings_audit(project_root: Path) -> QualityResult:
    """Run the cross-platform line-ending audit (GHI #570).

    Fails closed when `.gitattributes` lacks the `* text=auto eol=lf`
    directive or any tracked text surface still carries CRLF — the recurring
    Windows<->Mac hazard (ADR-0.0.1; one-off fixes GHIs #478/#161/#384).
    """
    return run_command("uv run gz validate --line-endings", cwd=project_root)


def run_smoke_tier(project_root: Path) -> QualityResult:
    """Run the smoke/BVT tier against its declared budget (GHI #724).

    Fails closed when the tier is empty or exceeds the ceiling in
    `.gzkit/rules/tests.md`. Cheap by construction — the tier exists precisely
    so the build-verification loop fits a budget the full suite cannot.
    """
    return run_command("uv run gz smoke", cwd=project_root)


def run_module_size_audit(project_root: Path) -> QualityResult:
    """Run the shrink-only module-size ratchet as an automatic gate.

    The ratchet has had teeth since its 2026-08-01 cutover and no automatic
    caller: it spoke only when a human ran
    `gz chores advise module-sloc-cap-radon`. That is how a 297-SLOC breach
    shipped in v0.34.2 with every gate green — the gate was not wrong, it was
    never asked.

    Invokes the chore's own script rather than re-implementing the band check.
    A second implementation would be a second threshold authority, which
    `.gzkit/rules/complexity-thresholds.md` § Invariant names outright as
    "doctrine drift by another name" — the very drift that script was written
    to remove.

    The `--self-test` arm runs first because a gate with no automatic caller
    and a gate whose teeth are never verified are the same failure class: the
    self-test drives all four breach directions over synthetic data and costs
    no radon run. The chore's remaining criterion (the full unit suite) is
    deliberately NOT run here — `gz check` already runs it as its own step.
    """
    from gzkit.commands.chores import _resolve_chore_dir  # noqa: PLC0415

    script = _resolve_chore_dir("module-sloc-cap-radon").path / "check_module_size.py"
    self_test = run_command(["uv", "run", "python", str(script), "--self-test"], cwd=project_root)
    if not self_test.success:
        return self_test
    return run_command(["uv", "run", "python", str(script)], cwd=project_root)


def run_authorship_audit(project_root: Path) -> QualityResult:
    """Run the commit-authorship policy audit (GHI #725).

    Fails closed when the effective `git user.email` violates the project's
    declared `authorship.required_email_suffix`. A no-op in projects that
    declare no policy, so adopters inherit no identity rule of gzkit's.
    Recovery: `git config --local user.email '<handle>@users.noreply.github.com'`.
    """
    return run_command("uv run gz validate --authorship", cwd=project_root)


_POOL_ADR_DISPATCH = "docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md"
_DISPATCH_ABSORPTION_MARKER = "absorbed_into: ADR-0.0.73"


def run_dispatch_absorption_marker_audit(project_root: Path) -> QualityResult:
    """Verify the dispatch-attestation pool ADR is annotated as absorbed (OBPI-0.0.73-05).

    Fails closed (exit 3) when the pool ADR lacks the absorption marker —
    enforcing that the "checker not bound" concern is permanently tracked in
    the QC registry once absorbed, and can never silently drift back to an
    unannotated state.
    Recovery: ensure ADR-pool.obpi-pipeline-dispatch-attestation.md contains
    `absorbed_into: ADR-0.0.73` in its frontmatter.

    **This audits the absorption MARKER, never a dispatch (GHI #770).** Its
    entire subject is a frontmatter string; it cannot answer "did any subagent
    dispatch happen?", which is the concern the pool ADR was absorbed to
    resolve. It shipped as `run_dispatch_attestation_audit` / step
    `dispatch-attestation` and was renamed because a step named for an
    attestation it does not perform is the facade signature ADR-0.0.73 exists
    to catch. Whether a mandated persona dispatch occurred is reported by
    `gzkit.adr_eval_dispatch` in the evaluation scorecard; the receipt
    machinery that would *cause* one to be recorded remains
    `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6.
    """
    pool_adr = project_root / _POOL_ADR_DISPATCH
    if not pool_adr.exists():
        return QualityResult(
            success=False,
            command="dispatch-absorption-marker audit",
            stdout="",
            stderr=(
                f"Pool ADR not found: {_POOL_ADR_DISPATCH}. "
                "Expected as the absorption target of ADR-0.0.73 OBPI-05."
            ),
            returncode=3,
        )
    content = pool_adr.read_text(encoding="utf-8")
    if _DISPATCH_ABSORPTION_MARKER not in content:
        return QualityResult(
            success=False,
            command="dispatch-absorption-marker audit",
            stdout="",
            stderr=(
                f"{_POOL_ADR_DISPATCH} is missing the absorption marker "
                f"`{_DISPATCH_ABSORPTION_MARKER}`. "
                "Add it to the frontmatter to confirm the pool ADR is absorbed into ADR-0.0.73."
            ),
            returncode=3,
        )
    return QualityResult(
        success=True,
        command="dispatch-absorption-marker audit",
        stdout=f"Pool ADR annotated as absorbed into ADR-0.0.73 ({_DISPATCH_ABSORPTION_MARKER}).",
        stderr="",
        returncode=0,
    )


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

    Bare directory entries (`src/gzkit/schemas/`, `tests/`) carry no glob `*`
    but are equally common scoping for model/generator/schema OBPIs whose only
    deliverables live under a directory. They expand the same way as globs —
    into the concrete files beneath them — so directory-scoped OBPIs are not
    invisible to every file-granular checker (surfaced at ADR-0.30.0 closeout:
    OBPI-01/02 scoped `src/gzkit/schemas/` and `tests/` as bare directories).
    """
    expanded: list[str] = []
    for path_str in allowed_paths:
        if "*" in path_str:
            try:
                for matched in project_root.glob(path_str):
                    if matched.is_file():
                        expanded.append(matched.relative_to(project_root).as_posix())
            except (ValueError, OSError):
                continue
            continue
        candidate = project_root / path_str
        if path_str.endswith("/") or candidate.is_dir():
            try:
                for matched in candidate.glob("**/*"):
                    if matched.is_file():
                        expanded.append(matched.relative_to(project_root).as_posix())
            except (ValueError, OSError):
                continue
            continue
        expanded.append(path_str)
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
    foundation walkthroughs) name ``ADR-CLOSEOUT-FORM.md``,
    ``EVALUATION_SCORECARD.md``, and ``EVALUATION_SUBSTANCE.md`` under
    ``docs/design/adr/**/`` in their allowed paths. Those files are the durable
    artifacts that OBPI produces; without this classifier they trip the
    product-proof MISSING gate despite being substantive evidence.

    ``EVALUATION_SUBSTANCE.md`` joined the set with GHI #769, which split the
    judge's scorecard off the machine-regenerated one. It is the more
    substantive of the two by construction — the scorecard is a deterministic
    structural lint, the substance file is the recorded judgment.
    """
    for path_str in allowed_paths:
        if not path_str.startswith("docs/design/adr/"):
            continue
        filename = Path(path_str).name
        if filename not in {
            "ADR-CLOSEOUT-FORM.md",
            "EVALUATION_SCORECARD.md",
            "EVALUATION_SUBSTANCE.md",
        }:
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
