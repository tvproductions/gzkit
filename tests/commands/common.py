import io
import os
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch


@dataclass
class CliResult:
    """Simple CLI invocation result."""

    exit_code: int
    output: str


class CliRunner:
    """Minimal stdlib-only CLI test runner."""

    @contextmanager
    def isolated_filesystem(self):
        cwd = Path.cwd()
        old_no_color = os.environ.get("NO_COLOR")
        os.environ["NO_COLOR"] = "1"
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                yield
            finally:
                os.chdir(cwd)
                if old_no_color is None:
                    del os.environ["NO_COLOR"]
                else:
                    os.environ["NO_COLOR"] = old_no_color

    def invoke(self, command, args):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                exit_code = command(args)
            except SystemExit as exc:
                code = exc.code
                exit_code = code if isinstance(code, int) else 1
        return CliResult(
            exit_code=0 if exit_code is None else int(exit_code),
            output=output.getvalue(),
        )


@contextmanager
def _git_subprocess_patcher(
    *,
    branch: str = "main",
    head_sha: str = "abc1234",
    remote: str = "origin",
    clean: bool = True,
    responses: dict[tuple[str, ...], tuple[int, str, str]] | None = None,
) -> Iterator[None]:
    """Patch ``gzkit.utils.git_cmd`` with a fake that simulates a healthy repo.

    This is the ``git`` counterpart to ``_uv_sync_patcher`` — unit tests that
    exercise ``gz git-sync`` or any flow touching ``git_cmd`` should wrap
    their invocation with this context manager instead of spawning real
    subprocesses via ``_init_git_repo``. Typical call:

        with _git_subprocess_patcher():
            result = runner.invoke(main, ["git-sync"])

    The fake responds to common git introspection commands used by
    ``gzkit.git_sync`` and ``gzkit.commands.sync``:

    - ``rev-parse --is-inside-work-tree`` returns ``"true"``
    - ``rev-parse --abbrev-ref HEAD`` returns ``branch``
    - ``rev-parse --show-toplevel`` returns the project root
    - ``rev-parse ...`` returns ``head_sha``
    - ``status --porcelain`` returns empty when ``clean=True``
    - ``rev-list --count`` returns ``"0"``
    - ``log``/``diff`` return empty success

    Pass ``responses`` to override specific ``(args, ...)`` tuples.
    """
    overrides = responses or {}

    def fake_git_cmd(project_root: Path, *args: str) -> tuple[int, str, str]:
        if args in overrides:
            return overrides[args]
        if args == ("rev-parse", "--is-inside-work-tree"):
            return (0, "true", "")
        if args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return (0, branch, "")
        if args == ("rev-parse", "--show-toplevel"):
            return (0, str(project_root), "")
        if args == ("status", "--porcelain"):
            return (0, "" if clean else "?? untracked.txt\n", "")
        if args[:1] == ("rev-parse",):
            return (0, head_sha, "")
        if args[:1] == ("rev-list",):
            return (0, "0", "")
        if args[:1] in (("log",), ("diff",), ("status",), ("branch",), ("show",)):
            return (0, "", "")
        return (0, "", "")

    patchers = [
        patch("gzkit.utils.git_cmd", side_effect=fake_git_cmd),
        patch("gzkit.git_sync.git_cmd", side_effect=fake_git_cmd),
        patch("gzkit.commands.sync.git_cmd", side_effect=fake_git_cmd),
    ]
    _ = remote  # argument kept for documentation / future use
    for p in patchers:
        p.start()
    try:
        yield
    finally:
        for p in patchers:
            p.stop()


def _init_git_repo(path: Path, *, seed_file: str = "README.md") -> str:
    """Initialize a disposable git repo and return the initial short HEAD SHA."""
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    (path / seed_file).write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "seed"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    result = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_obpi(
    path: Path,
    status: str,
    brief_status: str,
    implementation_line: str,
    *,
    lane: str = "Lite",
    key_proof: str = "uv run gz adr status ADR-0.1.0 --json",
    human_attestation: tuple[str, str, str] | None = None,
    tracked_defects: list[str] | None = None,
) -> None:
    lines = [
        "---",
        "id: OBPI-0.1.0-01-demo",
        "parent: ADR-0.1.0",
        "item: 1",
        f"lane: {lane}",
        f"status: {status}",
        "---",
        "",
        "# OBPI-0.1.0-01-demo: Demo",
        "",
        f"**Brief Status:** {brief_status}",
        "",
        "## Evidence",
        "",
        "### Implementation Summary",
        f"- Files created/modified: {implementation_line}",
        "- Validation commands run: uv run -m unittest discover tests",
        "- Date completed: 2026-02-14",
        "",
        "## Key Proof",
        key_proof,
        "",
    ]
    if tracked_defects:
        lines.extend(
            [
                "## Tracked Defects",
                *[f"- {defect}" for defect in tracked_defects],
                "",
            ]
        )
    if human_attestation is not None:
        attestor, attestation, attestation_date = human_attestation
        lines.extend(
            [
                "## Human Attestation",
                f"- Attestor: {attestor}",
                f"- Attestation: {attestation}",
                f"- Date: {attestation_date}",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n")


_uv_sync_patcher = patch("gzkit.commands.init_cmd._run_uv_sync", return_value=None)
_ruff_format_patchers = (
    patch("gzkit.hooks.claude._ruff_format_dir", return_value=None),
    patch("gzkit.hooks.copilot._ruff_format_dir", return_value=None),
)


def start_init_subprocess_patches() -> None:
    """Stub the two subprocess calls that dominate ``gz init`` wall-clock.

    Call from ``setUpModule`` in any test module that invokes
    ``runner.invoke(main, ["init"])``. Stubs:

    * ``_run_uv_sync`` — each real ``uv sync`` costs ~1s.
    * ``_ruff_format_dir`` — each call spawns ``uv run ruff format`` on a
      generated hooks directory; ``gz init`` invokes it 4 times (~600ms
      total per init). Hook templates are already formatted; skipping the
      format step does not affect behavioral correctness under test.

    Paired with ``stop_init_subprocess_patches()`` in ``tearDownModule``.
    GHI #183: per-test budget for test_init/test_skills/test_sync_cmds/
    test_audit drops from ~800ms to <200ms.
    """
    _uv_sync_patcher.start()
    for patcher in _ruff_format_patchers:
        patcher.start()


def stop_init_subprocess_patches() -> None:
    """Stop the init-subprocess patches started by ``start_init_subprocess_patches``."""
    for patcher in _ruff_format_patchers:
        patcher.stop()
    _uv_sync_patcher.stop()


# Back-compat shims for callers that used the narrower helpers during GHI #183
# rollout. Prefer start_init_subprocess_patches / stop_init_subprocess_patches.
def start_uv_sync_patch() -> None:
    """Back-compat alias; prefer ``start_init_subprocess_patches``."""
    start_init_subprocess_patches()


def stop_uv_sync_patch() -> None:
    """Back-compat alias; prefer ``stop_init_subprocess_patches``."""
    stop_init_subprocess_patches()


def _quick_init(mode: str = "lite") -> None:
    """Lightweight project init for tests — skips sync_all and hook setup.

    Creates the minimal scaffold that CLI commands need: .gzkit.json, manifest,
    ledger with project_init event, and design directories.  ~5x faster than
    ``runner.invoke(main, ["init"])`` because it avoids template rendering,
    hook generation, and skill mirroring.
    """
    import json
    from pathlib import Path

    from gzkit.config import GzkitConfig
    from gzkit.ledger import Ledger, project_init_event

    project_root = Path.cwd()
    gzkit_dir = project_root / ".gzkit"
    gzkit_dir.mkdir(exist_ok=True)

    config = GzkitConfig(mode=mode, project_name="test-project")  # type: ignore[arg-type]
    config.save(project_root / ".gzkit.json")

    manifest = {
        "schema": "gzkit.manifest.v2",
        "structure": {
            "source_root": config.paths.source_root,
            "tests_root": config.paths.tests_root,
            "docs_root": config.paths.docs_root,
            "design_root": config.paths.design_root,
        },
        "artifacts": {
            "prd": {"path": config.paths.prd, "schema": "gzkit.prd.v1"},
            "constitution": {"path": config.paths.constitutions, "schema": "gzkit.constitution.v1"},
            "obpi": {"path": config.paths.adrs, "schema": "gzkit.obpi.v1"},
            "adr": {"path": config.paths.adrs, "schema": "gzkit.adr.v1"},
        },
        "data": {
            "eval_datasets": "data/eval",
            "eval_schema": "data/schemas/eval_dataset.schema.json",
            "baselines": "artifacts/baselines",
            "schemas": "data/schemas",
        },
        "ops": {
            "chores": "config/chores",
            "receipts": "artifacts/receipts",
            "proofs": "artifacts/proofs",
        },
        "thresholds": {
            "coverage_floor": 40.0,
            "eval_regression_delta": 0.05,
            "function_lines": 50,
            "module_lines": 600,
            "class_lines": 300,
        },
        "control_surfaces": {
            "agents_md": "AGENTS.md",
            "claude_md": "CLAUDE.md",
            "hooks": ".claude/hooks",
            "skills": ".gzkit/skills",
            "claude_skills": ".claude/skills",
            "codex_skills": ".agents/skills",
            "copilot_skills": ".github/skills",
            "instructions": ".github/instructions",
            "claude_rules": ".claude/rules",
        },
        "verification": {
            "lint": "uv run gz lint",
            "format": "uv run gz format",
            "typecheck": "uv run gz typecheck",
            "test": "uv run gz test",
            "docs": "uv run mkdocs build --strict",
            "bdd": "uv run -m behave features/",
        },
        "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
    }
    (gzkit_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    ledger_path = gzkit_dir / "ledger.jsonl"
    ledger_path.touch()
    ledger = Ledger(ledger_path)
    ledger.append(project_init_event("test-project", mode))

    for d in ["prd", "constitutions", "adr"]:
        (project_root / config.paths.design_root / d).mkdir(parents=True, exist_ok=True)

    from gzkit.personas import scaffold_default_personas

    scaffold_default_personas(project_root)
