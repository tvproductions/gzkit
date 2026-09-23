#!/usr/bin/env python3
"""Measure the real duplication between Gate 4 (behave) and Gate 2 (unittest).

This is measurement item ``M-F`` of the program in ``01 § 12``: *"Measure the
real duplication between Gate 4 and Gate 2 before proposing removal."* Its
method is that item's, verbatim -- execute the behave suite with coverage
instrumentation, compare the covered set against the unit suite's, identify
which scenarios cover code no unit test reaches, verify the behave-only REQ
count, and count the ``@wip`` scenarios separately because they never execute.

Carries no literals from the date it was authored: every figure is derived from
the tree it is run against, so a later run reports that tree rather than
confirming a transcribed number (``AGENTS.md`` § Governance doctrine surfaces --
"A value written in a Markdown doc is ILLUSTRATIVE, never authoritative").

Usage::

    uv run python docs/governance/ieee/03-gate4-gate2-duplication-evidence/measure.py
    uv run python .../measure.py --json
    uv run python .../measure.py --coverage          # ~7 min: runs both suites
    uv run python .../measure.py --coverage --per-feature   # ~15 min

Without ``--coverage`` the script reports the structural census only, which is
seconds. The coverage arms execute the suites and are the slow, authoritative
half. Exit status is 0 whenever the measurement completes; this is a census,
not a gate. Stdlib only, per the STDLIB-FIRST doctrine -- the coverage data is
read back through ``coverage json``, never by importing the package.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
FEATURES = REPO / "features"
STEPS = FEATURES / "steps"
TESTS = REPO / "tests"

REQ_TAG = re.compile(r"@(REQ-[A-Za-z0-9._-]+)")
COVERS = re.compile(r'@covers\(\s*"(REQ-[A-Za-z0-9._-]+)"\s*\)')
SCENARIO = re.compile(r"^[ \t]*Scenario(?: Outline)?:[ \t]*(.+?)[ \t]*$", re.M)
TAG_LINE = re.compile(r"^[ \t]*@[A-Za-z0-9@._\- \t]+$", re.M)

COV_CONFIG = """[run]
source = {src}
parallel = true
branch = false
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _feature_files() -> list[Path]:
    return sorted(FEATURES.glob("*.feature"))


def _step_files() -> list[Path]:
    return sorted(STEPS.glob("*.py"))


def _tag_lines(text: str) -> list[str]:
    """Return the tag LINES of a feature, excluding tags written inside comments.

    A ``#`` comment mentioning ``@wip`` is prose about the tag, not the tag. The
    distinction is load-bearing: counting comment mentions inflates the skipped
    population, which is exactly the figure ``M-F`` says to count separately.
    """
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("@"):
            out.append(stripped)
    return out


def structural_census() -> dict[str, Any]:
    """Census the feature suite without executing it: REQ tags, @wip, step-file shape.

    Seconds rather than minutes, and sufficient for every figure in the piece
    except the line-level comparison, which needs the suites to run.
    """
    feature_reqs: set[str] = set()
    wip_reqs: set[str] = set()
    scenario_total = 0
    wip_tag_total = 0
    per_feature: dict[str, dict[str, Any]] = {}

    for path in _feature_files():
        text = _read(path)
        reqs = set(REQ_TAG.findall(text))
        scenarios = SCENARIO.findall(text)
        wip_tags = sum(1 for line in _tag_lines(text) if "@wip" in line.split())
        feature_reqs |= reqs
        scenario_total += len(scenarios)
        wip_tag_total += wip_tags
        if wip_tags:
            wip_reqs |= reqs
        per_feature[path.name] = {
            "scenarios": len(scenarios),
            "req_tags": sorted(reqs),
            "wip_tag_lines": wip_tags,
        }

    covers: set[str] = set()
    for path in sorted(TESTS.rglob("*.py")):
        covers |= set(COVERS.findall(_read(path)))

    behave_only = sorted(feature_reqs - covers)

    step_files = _step_files()
    subprocess_steps = [
        p.name for p in step_files if re.search(r"\bsubprocess\.|Popen\b", _read(p))
    ]
    inprocess_steps = [
        p.name for p in step_files if re.search(r"^\s*(from|import)\s+gzkit", _read(p), re.M)
    ]

    expected_warning = sum(
        1
        for path in _feature_files()
        for line in _tag_lines(_read(path))
        if any(t.startswith("@expected-warning") for t in line.split())
    )

    return {
        "feature_files": len(_feature_files()),
        "scenarios_declared": scenario_total,
        "wip_tag_lines": wip_tag_total,
        "wip_features": sorted(n for n, v in per_feature.items() if v["wip_tag_lines"]),
        "feature_req_tags": len(feature_reqs),
        "covers_reqs_in_tests": len(covers),
        "feature_reqs_with_covers": len(feature_reqs & covers),
        "behave_only_reqs": behave_only,
        "behave_only_req_count": len(behave_only),
        "behave_only_reqs_inside_wip_only": sorted(set(behave_only) & wip_reqs - covers),
        "step_files": len(step_files),
        "step_files_driving_subprocess": len(subprocess_steps),
        "step_files_importing_gzkit": len(inprocess_steps),
        "expected_warning_tag_lines": expected_warning,
        "per_feature": per_feature,
    }


def _run_under_coverage(argv: list[str], data_dir: Path, cfg: Path) -> int:
    data_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["COVERAGE_PROCESS_START"] = str(cfg)
    env["COVERAGE_FILE"] = str(data_dir / ".coverage")
    cmd = ["uv", "run", "coverage", "run", f"--rcfile={cfg}", *argv]
    return subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True).returncode


def _covered_lines(data_dir: Path, cfg: Path) -> dict[str, set[int]]:
    """Combine a run's parallel data files and read the covered set back as JSON.

    ``coverage json`` is the read path rather than ``import coverage`` so the
    script stays stdlib-only; the package is a development tool invoked as a
    subprocess, the way this repository invokes every other verifier.
    """
    combined = data_dir / "combined.db"
    env = dict(os.environ)
    env["COVERAGE_FILE"] = str(combined)
    parts = [str(p) for p in sorted(data_dir.glob(".coverage.*"))]
    if not parts:
        return {}
    subprocess.run(
        ["uv", "run", "coverage", "combine", f"--rcfile={cfg}", "--keep", *parts],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    out = data_dir / "coverage.json"
    subprocess.run(
        ["uv", "run", "coverage", "json", f"--rcfile={cfg}", "-o", str(out)],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )
    if not out.exists():
        return {}
    payload = json.loads(out.read_text(encoding="utf-8"))
    return {
        str(Path(name).resolve()): set(info.get("executed_lines", []))
        for name, info in payload.get("files", {}).items()
    }


def _diff(a: dict[str, set[int]], b: dict[str, set[int]]) -> dict[str, list[int]]:
    """Lines covered in ``a`` that ``b`` never reaches, by file."""
    out: dict[str, list[int]] = {}
    for name, lines in a.items():
        only = sorted(lines - b.get(name, set()))
        if only:
            out[str(Path(name).relative_to(REPO)) if str(name).startswith(str(REPO)) else name] = (
                only
            )
    return out


def coverage_census(per_feature: bool, workdir: Path) -> dict[str, Any]:
    """Run both suites under identical instrumentation and diff their covered sets.

    Identical is the operative word. A third of the step files drive ``gz`` as a
    subprocess, so in-process-only capture would score those runs as reaching
    nothing and understate Gate 4 in the same direction as the hypothesis under
    test. ``COVERAGE_PROCESS_START`` is set for both sides.
    """
    cfg = workdir / "cov.cfg"
    cfg.write_text(COV_CONFIG.format(src=REPO / "src" / "gzkit"), encoding="utf-8")

    behave_exit = _run_under_coverage(["-m", "behave", "features/"], workdir / "behave", cfg)
    unit_exit = _run_under_coverage(
        ["-m", "unittest", "discover", "-s", "tests"], workdir / "unit", cfg
    )
    behave = _covered_lines(workdir / "behave", cfg)
    unit = _covered_lines(workdir / "unit", cfg)

    behave_only = _diff(behave, unit)
    unit_only = _diff(unit, behave)
    b_total = sum(len(v) for v in behave.values())
    u_total = sum(len(v) for v in unit.values())
    bo_total = sum(len(v) for v in behave_only.values())

    result: dict[str, Any] = {
        "behave_exit": behave_exit,
        "unit_exit": unit_exit,
        "behave_covered_lines": b_total,
        "unit_covered_lines": u_total,
        "behave_only_lines": bo_total,
        "unit_only_lines": sum(len(v) for v in unit_only.values()),
        "lines_covered_by_both": b_total - bo_total,
        "behave_only_share_of_behave": round(bo_total / b_total, 4) if b_total else None,
        "files_with_behave_only_lines": len(behave_only),
        "behave_only_by_file": {
            k: len(v) for k, v in sorted(behave_only.items(), key=lambda kv: -len(kv[1]))
        },
    }

    if per_feature:
        attribution: dict[str, int] = {}
        wanted = {k: set(v) for k, v in behave_only.items()}
        for path in _feature_files():
            d = workdir / "perfeat" / path.stem
            _run_under_coverage(["-m", "behave", str(path.relative_to(REPO))], d, cfg)
            cov = _covered_lines(d, cfg)
            rel = {
                str(Path(n).relative_to(REPO)): ls
                for n, ls in cov.items()
                if str(n).startswith(str(REPO))
            }
            hit = sum(len(rel.get(f, set()) & ls) for f, ls in wanted.items())
            if hit:
                attribution[path.name] = hit
            shutil.rmtree(d, ignore_errors=True)
        result["behave_only_lines_by_feature"] = dict(
            sorted(attribution.items(), key=lambda kv: -kv[1])
        )
    return result


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the requested census arms, and report."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="Emit the full census as JSON.")
    ap.add_argument(
        "--coverage", action="store_true", help="Execute both suites under coverage (slow)."
    )
    ap.add_argument(
        "--per-feature",
        action="store_true",
        help="Attribute behave-only lines to features (implies --coverage; very slow).",
    )
    ap.add_argument("--keep", type=Path, default=None, help="Keep coverage data in this dir.")
    args = ap.parse_args(argv)

    census: dict[str, Any] = {"commit": _commit(), "structural": structural_census()}

    if args.coverage or args.per_feature:
        workdir = args.keep or Path(tempfile.mkdtemp(prefix="mf-coverage-"))
        workdir.mkdir(parents=True, exist_ok=True)
        census["coverage"] = coverage_census(args.per_feature, workdir)
        census["coverage"]["workdir"] = str(workdir)

    if args.json:
        json.dump(census, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0

    _report(census)
    return 0


def _commit() -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
    return proc.stdout.strip() or "unknown"


def _report(census: dict[str, Any]) -> None:
    s = census["structural"]
    print(f"measured at {census['commit']}")
    print()
    print("STRUCTURAL")
    print(f"  feature files                        {s['feature_files']}")
    print(f"  scenarios declared                   {s['scenarios_declared']}")
    print(f"  @wip tag lines (never execute)       {s['wip_tag_lines']}  in {s['wip_features']}")
    print(f"  step files                           {s['step_files']}")
    print(f"    importing gzkit (in-process)       {s['step_files_importing_gzkit']}")
    print(f"    driving a subprocess               {s['step_files_driving_subprocess']}")
    print(f"  @expected-warning tag lines          {s['expected_warning_tag_lines']}")
    print()
    print("REQ OVERLAP")
    print(f"  REQs tagged in features              {s['feature_req_tags']}")
    print(f"  distinct @covers REQs in tests/      {s['covers_reqs_in_tests']}")
    print(f"  feature REQs also @covers-ed         {s['feature_reqs_with_covers']}")
    print(f"  behave-only REQs                     {s['behave_only_req_count']}")
    print(f"  behave-only REQs only inside @wip    {len(s['behave_only_reqs_inside_wip_only'])}")

    c = census.get("coverage")
    if not c:
        print()
        print("(run with --coverage for the line-level comparison)")
        return
    print()
    print("COVERAGE")
    print(f"  behave suite exit                    {c['behave_exit']}")
    print(f"  unit suite exit                      {c['unit_exit']}")
    print(f"  lines covered by behave              {c['behave_covered_lines']}")
    print(f"  lines covered by unittest            {c['unit_covered_lines']}")
    print(f"  covered by BOTH                      {c['lines_covered_by_both']}")
    print(f"  behave-only                          {c['behave_only_lines']}")
    print(f"  unit-only                            {c['unit_only_lines']}")
    share = c["behave_only_share_of_behave"]
    if share is not None:
        print(f"  behave-only share of behave's own    {share:.2%}")
    print(f"  files with any behave-only line      {c['files_with_behave_only_lines']}")
    for name, n in list(c["behave_only_by_file"].items())[:15]:
        print(f"      {n:5d}  {name}")
    by_feature = c.get("behave_only_lines_by_feature")
    if by_feature:
        print()
        print("  behave-only lines reached, by feature (non-exclusive):")
        for name, n in list(by_feature.items())[:20]:
            print(f"      {n:5d}  {name}")


if __name__ == "__main__":
    raise SystemExit(main())
