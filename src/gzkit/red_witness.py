"""Base-tree RED witness for BEHAVIOR-REQ tests (GHI #642).

The OBPI pipeline *instructs* Red-Green-Refactor but ships no mechanical witness
that a BEHAVIOR test was ever observed failing before its implementation existed.
The only mechanical test gate is ``@covers`` parity — coverage, not falsifiability.
A test written after the production code, passing on its first run, is
byte-indistinguishable from a genuine RED-first test.

This module supplies the witness. It reconstructs the base tree in a throwaway
git worktree, copies in **only** the test files (never the production files), and
runs the scoped test there. Three outcomes, and they are not equivalent:

  * ``assertion`` — the test failed on an assertion. A strong RED: the test
    genuinely depends on the implementation under test.
  * ``error``     — the test failed on an ImportError/exception. A *weak* RED:
    it failed for the wrong reason (usually the new symbol does not exist yet).
    Never silently equate this with an assertion RED.
  * ``none``      — the test PASSED without the production code. It cannot fail.
    This is exactly the ``AGENTS.md`` § DO IT RIGHT Rule 6 test "that can't fail
    when business logic changes," and it is rejected.
  * ``not-applicable`` — nothing was withheld, so the experiment never ran. NOT a
    verdict on the test (GHI #839). The premise of every class above is that the
    implementation is ABSENT from the base tree, and ``resolve_base_commit``
    returns HEAD — so once the production code lands, the base tree already
    carries it, every covering test passes, and a ``none`` would be a confident
    accusation against a test that was never actually tested.

Why a base-tree run and not superpowers' commit-the-failing-test witness: gzkit's
trunk is green and pre-commit runs unittest, so a RED can never be committed to
``main``. The witness must be an isolated base-tree run, not a RED commit.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Iterator

FailureClass = Literal["assertion", "error", "none", "not-applicable"]

# `FAILED (failures=2, errors=1)` — unittest's own summary line.
_FAILED_SUMMARY_RE = re.compile(r"FAILED\s*\((?P<body>[^)]*)\)")
_FAILURES_RE = re.compile(r"failures=(\d+)")
_ERRORS_RE = re.compile(r"errors=(\d+)")

_GIT_TIMEOUT_S = 120
_TEST_TIMEOUT_S = 600


class RedWitness(BaseModel):
    """The observed result of running a test against the base tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., min_length=1, description="BEHAVIOR REQ under witness")
    base_commit: str = Field(..., min_length=1, description="Commit the test ran against")
    test_names: list[str] = Field(..., description="unittest-addressable names executed")
    exit_status: int = Field(..., description="Exit code of the base-tree test run")
    failure_class: FailureClass = Field(..., description="assertion | error | none")
    output_tail: str = Field(default="", description="Tail of the base-tree run's output")

    @property
    def is_red(self) -> bool:
        """True when the test demonstrably fails without its implementation.

        A weak RED (``error``) still witnesses falsifiability — the test cannot pass
        without the production change. ``none`` means the test proves nothing, and
        ``not-applicable`` means the RUN proves nothing — different findings, and
        neither is a RED. Enumerated positively rather than as ``!= "none"`` so a
        future class cannot default into counting as falsifiability (GHI #839).
        """
        return self.failure_class in {"assertion", "error"}


def classify_failure(exit_status: int, output: str) -> FailureClass:
    """Classify a base-tree test run into its RED failure class.

    ``errors`` dominates ``failures``: a run that raised (ImportError, TypeError)
    failed for the wrong reason even if some other test in the scope failed on an
    assertion. Collapsing the two would launder a weak RED into a strong one — the
    exact equivalence GHI #642 forbids.
    """
    if exit_status == 0:
        return "none"
    match = _FAILED_SUMMARY_RE.search(output)
    if match is None:
        # Non-zero with no unittest summary: a crash, a collection error, a timeout.
        return "error"
    body = match.group("body")
    errors = _ERRORS_RE.search(body)
    if errors and int(errors.group(1)) > 0:
        return "error"
    failures = _FAILURES_RE.search(body)
    if failures and int(failures.group(1)) > 0:
        return "assertion"
    return "error"


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command, capturing text output with a decode fallback."""
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=_GIT_TIMEOUT_S,
    )


def resolve_base_commit(project_root: Path) -> str:
    """Return the commit the working tree's changes sit on top of (HEAD)."""
    result = _git(["rev-parse", "HEAD"], project_root)
    if result.returncode != 0:
        raise RuntimeError(f"cannot resolve base commit: {result.stderr.strip()}")
    return result.stdout.strip()


def changed_test_files(
    project_root: Path, base_commit: str, tests_dir: str = "tests"
) -> list[Path]:
    """Return repo-relative test files that differ from the base tree.

    Both arms matter: a modified test file appears in ``git diff``, and a brand-new
    test file appears only in ``ls-files --others``. Missing the second arm would
    silently witness nothing for every new test module.
    """
    paths: set[str] = set()
    diff = _git(["diff", "--name-only", base_commit, "--", tests_dir], project_root)
    if diff.returncode == 0:
        paths.update(line for line in diff.stdout.splitlines() if line.strip())
    untracked = _git(["ls-files", "--others", "--exclude-standard", "--", tests_dir], project_root)
    if untracked.returncode == 0:
        paths.update(line for line in untracked.stdout.splitlines() if line.strip())
    return sorted(Path(p) for p in paths if p.endswith(".py"))


def withheld_production_files(
    project_root: Path, base_commit: str, tests_dir: str = "tests"
) -> list[Path]:
    """Return the repo-relative Python files the graft deliberately leaves behind.

    This is the exact complement of :func:`changed_test_files`: the graft copies in
    changed TEST modules, so everything else that differs from the base tree is what
    the experiment withholds. Defined by exclusion rather than by a source directory
    because the withheld set is a property of the graft, not of any one repository's
    layout — a project with production modules outside ``src/`` withholds those too.

    The experiment's premise — the implementation under test is ABSENT from the base
    tree — is checked here, never assumed. It holds while work is in flight and fails
    the moment the production code lands, because ``resolve_base_commit`` returns
    HEAD. An empty result means nothing was withheld, so the run cannot tell a hollow
    test from a present implementation and must report neither (GHI #839).

    Deliberately keyed on the PRODUCTION side rather than on ``changed_test_files``:
    with the code committed and the tests still uncommitted, the changed-test list is
    non-empty while the implementation is present anyway, and a check keyed there
    would still hand back a false ``none``.

    Scoped to ``.py`` for the same reason the graft is: a dirty ledger, a receipt, or
    a scratch file is not a withheld production hunk, and counting one would restore
    the premise on a tree that has none.
    """
    prefix = f"{tests_dir.rstrip('/')}/"
    paths: set[str] = set()
    diff = _git(["diff", "--name-only", base_commit], project_root)
    if diff.returncode == 0:
        paths.update(line for line in diff.stdout.splitlines() if line.strip())
    untracked = _git(["ls-files", "--others", "--exclude-standard"], project_root)
    if untracked.returncode == 0:
        paths.update(line for line in untracked.stdout.splitlines() if line.strip())
    return sorted(Path(p) for p in paths if p.endswith(".py") and not p.startswith(prefix))


@contextmanager
def base_tree_worktree(project_root: Path, base_commit: str) -> Iterator[Path]:
    """Check out ``base_commit`` into a throwaway detached worktree, then remove it.

    The worktree is removed with ``--force`` because the test run leaves artifacts
    (``__pycache__``, receipts) that would otherwise make git refuse.
    """
    tmp = Path(tempfile.mkdtemp(prefix="gzkit-red-"))
    worktree = tmp / "base"
    created = _git(["worktree", "add", "--detach", str(worktree), base_commit], project_root)
    if created.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f"cannot create base worktree: {created.stderr.strip()}")
    try:
        yield worktree
    finally:
        _git(["worktree", "remove", "--force", str(worktree)], project_root)
        shutil.rmtree(tmp, ignore_errors=True)


def _graft_test_files(project_root: Path, worktree: Path, test_files: list[Path]) -> None:
    """Copy ONLY the test files into the base worktree.

    The production hunks are deliberately left behind. That asymmetry is the whole
    experiment: the test meets the code as it was before the implementation landed.
    """
    for rel in test_files:
        source = project_root / rel
        if not source.is_file():
            continue
        target = worktree / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


#: Default runner. Parameterized rather than hard-coded so the core can be exercised
#: without naming the technology it shells out to (Cockburn, Hexagonal § 1.1).
DEFAULT_TEST_RUNNER: tuple[str, ...] = ("uv", "run", "-m", "unittest")


def run_red_witness(
    *,
    project_root: Path,
    req_id: str,
    test_names: list[str],
    base_commit: str | None = None,
    tests_dir: str = "tests",
    test_runner: list[str] | None = None,
) -> RedWitness:
    """Run ``test_names`` against the base tree and classify how they fail.

    Raises:
        ValueError: when no covering test names were supplied — a BEHAVIOR REQ with
            no covering test is a coverage defect, not a falsifiability one, and the
            ``@covers`` parity gate is what must report it.

    """
    if not test_names:
        raise ValueError(f"no covering tests supplied for {req_id}; nothing to witness")

    base = base_commit or resolve_base_commit(project_root)

    # Check the premise BEFORE spending a worktree on it. With nothing withheld the
    # base tree already carries the implementation, so the run would pass and be
    # classified `none` — an accusation the experiment never earned (GHI #839).
    withheld = withheld_production_files(project_root, base, tests_dir)
    if not withheld:
        return RedWitness(
            req_id=req_id,
            base_commit=base,
            test_names=sorted(test_names),
            exit_status=0,
            failure_class="not-applicable",
            output_tail=(
                f"RED witness did not run: no production hunks were withheld against "
                f"base {base[:12]}. The base tree already carries the implementation "
                f"under test, so the covering test would pass there no matter what it "
                f"asserts. This is NOT a finding about the test."
            ),
        )

    test_files = changed_test_files(project_root, base, tests_dir)
    runner = list(test_runner) if test_runner else list(DEFAULT_TEST_RUNNER)

    with base_tree_worktree(project_root, base) as worktree:
        _graft_test_files(project_root, worktree, test_files)
        result = subprocess.run(
            [*runner, *test_names],
            cwd=worktree,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=_TEST_TIMEOUT_S,
        )

    output = (result.stdout or "") + (result.stderr or "")
    return RedWitness(
        req_id=req_id,
        base_commit=base,
        test_names=sorted(test_names),
        exit_status=int(result.returncode),
        failure_class=classify_failure(int(result.returncode), output),
        output_tail=output[-4000:],
    )


def resolve_covering_test_names(project_root: Path, req_id: str) -> list[str]:
    """Return unittest-addressable names for the tests covering ``req_id``.

    Mirrors ``gzkit.commands.quality._resolve_obpi_test_names`` but scoped to one
    REQ rather than a whole OBPI.
    """
    from gzkit.commands.quality import _test_name_from_record
    from gzkit.traceability import EdgeType, scan_test_tree
    from gzkit.triangle import ReqId

    names: set[str] = set()
    for record in scan_test_tree(project_root / "tests"):
        if record.edge_type != EdgeType.COVERS:
            continue
        try:
            target = ReqId.parse(record.target.identifier)
        except ValueError:
            continue
        if str(target) != req_id:
            continue
        name = _test_name_from_record(record, project_root)
        if name is not None:
            names.add(name)
    return sorted(names)


__all__ = [
    "FailureClass",
    "RedWitness",
    "base_tree_worktree",
    "changed_test_files",
    "DEFAULT_TEST_RUNNER",
    "classify_failure",
    "resolve_base_commit",
    "resolve_covering_test_names",
    "run_red_witness",
    "withheld_production_files",
]
