"""BDD steps for distribution invariant T0 smoke test (OBPI-0.0.32-06).

Builds the gzkit wheel via uv build, installs it into a fresh temp venv,
runs gz init in a clean tempdir using the installed binary, and asserts
byte-equivalence of the resulting .gzkit/ tree against the frozen
data/distribution_baseline_manifest.json.

@covers REQ-0.0.32-06-01
@covers REQ-0.0.32-06-02
@covers REQ-0.0.32-06-03
@covers REQ-0.0.32-06-04
@covers REQ-0.0.32-06-06
@covers REQ-0.0.32-06-07
@covers REQ-0.0.32-06-08
@covers REQ-0.0.32-06-09
@covers REQ-0.0.32-06-10
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from behave import given, then, when

from gzkit.rules import NESTED_SURFACE_NAMES


def _gzkit_project_root() -> Path:
    env = os.environ.get("GZKIT_PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    # features/steps/distribution_invariant_steps.py -> parents[2] is gzkit root
    return Path(__file__).resolve().parents[2]


def _project_python(gzkit_root: Path) -> str:
    """Return the project's pinned Python version for the smoke venv.

    The T0 distribution invariant proves the wheel installs and imports under
    the project's declared interpreter. The smoke venv must pin to it: a
    floating ``uv venv`` tests whatever interpreter uv happens to discover,
    not the ``requires-python`` floor the invariant claims to prove (GHI #482).
    """
    pin = (gzkit_root / ".python-version").read_text(encoding="utf-8").strip()
    assert pin, f".python-version is empty at {gzkit_root}"
    return pin


def _venv_bin(venv_path: Path, name: str) -> Path:
    # uv venv lays out interpreter/scripts at Scripts/*.exe on Windows, bin/* on POSIX.
    if sys.platform == "win32":
        return venv_path / "Scripts" / f"{name}.exe"
    return venv_path / "bin" / name


def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output


@given("an empty distribution-test project directory")
def step_fresh_empty(context) -> None:
    cwd = Path.cwd()
    assert not (cwd / ".gzkit").exists(), f"tempdir {cwd} is not fresh"
    context.project_root = cwd
    context.gzkit_root = _gzkit_project_root()
    context.smoke_start_ns = time.monotonic_ns()


@given('the gzkit baseline manifest at "{rel_path}"')
def step_baseline_manifest(context, rel_path: str) -> None:
    context.gzkit_root = _gzkit_project_root()
    manifest_path = context.gzkit_root / rel_path
    assert manifest_path.is_file(), f"baseline manifest missing: {manifest_path}"
    with manifest_path.open(encoding="utf-8") as f:
        context.baseline = json.load(f)


@when("I build the wheel with uv build")
def step_uv_build(context) -> None:
    # Clean prior wheels so we pick the freshly built one
    dist = context.gzkit_root / "dist"
    if dist.exists():
        for wheel in dist.glob("*.whl"):
            wheel.unlink()
    code, output = _run(["uv", "build", "--wheel"], cwd=context.gzkit_root)
    assert code == 0, f"uv build failed (exit {code}):\n{output}"
    wheels = sorted(dist.glob("py_gzkit-*.whl"))
    assert wheels, f"no wheel produced in {dist}"
    context.wheel_path = wheels[-1]


@when("I install the built wheel into a fresh temporary venv")
def step_install_into_venv(context) -> None:
    venv_path = context.project_root / ".smoke-venv"

    def _cleanup_venv() -> None:
        if venv_path.exists():
            shutil.rmtree(venv_path, ignore_errors=True)

    context.add_cleanup(_cleanup_venv)
    python_pin = _project_python(context.gzkit_root)
    code, output = _run(
        ["uv", "venv", "--python", python_pin, str(venv_path)],
        cwd=context.project_root,
    )
    assert code == 0, f"uv venv failed (exit {code}):\n{output}"
    venv_python = _venv_bin(venv_path, "python")
    assert venv_python.exists(), f"venv python missing at {venv_python}"
    code, output = _run(
        [
            "uv",
            "pip",
            "install",
            str(context.wheel_path),
            "--python",
            str(venv_python),
        ],
        cwd=context.project_root,
    )
    assert code == 0, f"uv pip install failed (exit {code}):\n{output}"
    context.venv_gz = _venv_bin(venv_path, "gz")
    assert context.venv_gz.exists(), f"venv gz binary missing at {context.venv_gz}"


@when('I run "{command}" in the project directory using the venv\'s gz binary')
def step_run_venv_gz(context, command: str) -> None:
    parts = command.split()
    assert parts and parts[0] == "gz", f"expected 'gz ...' command, got: {command}"
    cmd = [str(context.venv_gz), *parts[1:], "--no-skeleton"]
    code, output = _run(cmd, cwd=context.project_root)
    assert code == 0, f"gz init failed (exit {code}):\n{output}"
    context.gzkit_dir = context.project_root / ".gzkit"
    assert context.gzkit_dir.is_dir(), f".gzkit/ not created at {context.gzkit_dir}"


@then("every baseline manifest entry is present in the project's .gzkit tree")
def step_baseline_entries_present(context) -> None:
    missing: list[str] = []
    for surface, entries in context.baseline["surfaces"].items():
        for entry in entries:
            target = context.gzkit_dir / surface / entry
            if not target.is_file():
                missing.append(f"{surface}/{entry}")
    runtime_s = (time.monotonic_ns() - context.smoke_start_ns) / 1e9
    print(f"\n[OBPI-0.0.32-06] smoke runtime: {runtime_s:.1f}s")
    assert not missing, (
        f"baseline entries missing in installed .gzkit ({len(missing)}):\n  "
        + "\n  ".join(missing[:20])
    )


@then("no installed .gzkit artifact under a tracked surface is absent from the baseline manifest")
def step_no_extra_artifacts(context) -> None:
    # Reverse-direction drift check: scan .gzkit/<surface>/ for any artifact
    # matching the surface's expected file shape; flag anything not in baseline.
    extras: list[str] = []
    surface_patterns = {
        "skills": lambda p: p.name == "SKILL.md",
        # Generated per-subtree surfaces are Layer-3 projections `gz agent sync`
        # writes at init, never wheel-shipped canon -- the baseline holds zero of
        # them. The Claude redirect joined AGENTS.md there under GHI #923.
        "rules": lambda p: p.suffix == ".md" and p.name not in NESTED_SURFACE_NAMES,
        "personas": lambda p: p.suffix == ".md",
        "templates": lambda p: p.suffix == ".md",
    }
    for surface, matcher in surface_patterns.items():
        surface_dir = context.gzkit_dir / surface
        if not surface_dir.is_dir():
            continue
        baseline_entries = set(context.baseline["surfaces"].get(surface, []))
        for path in surface_dir.rglob("*"):
            if not path.is_file() or not matcher(path):
                continue
            rel = path.relative_to(surface_dir).as_posix()
            if rel not in baseline_entries:
                extras.append(f"{surface}/{rel}")
    assert not extras, (
        f"installed .gzkit artifacts not in baseline manifest ({len(extras)}):\n  "
        + "\n  ".join(extras[:20])
    )


@then('the manifest has schema_version "{version}"')
def step_schema_version(context, version: str) -> None:
    assert context.baseline["schema_version"] == version, (
        f"schema_version mismatch: expected {version}, got {context.baseline['schema_version']}"
    )


@then('the manifest surfaces include "{surface}"')
def step_surface_present(context, surface: str) -> None:
    assert surface in context.baseline["surfaces"], f"surface {surface!r} missing from manifest"


@then('each "{surface}" entry resolves to a real file under "{rel_root}"')
def step_entries_resolve(context, surface: str, rel_root: str) -> None:
    root = context.gzkit_root / rel_root
    missing: list[str] = []
    for entry in context.baseline["surfaces"][surface]:
        candidate = root / entry
        if not candidate.is_file():
            missing.append(str(candidate))
    assert not missing, f"{surface} entries not found ({len(missing)}):\n  " + "\n  ".join(
        missing[:10]
    )
