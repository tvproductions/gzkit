"""Mutation-sweep witness with a four-way verdict (GHI #963).

A mutation sweep is how gzkit distinguishes a load-bearing guard from a vacuous
test: delete the guard, and a test that still passes was never testing it. The
verdict is used as governance evidence, so the sweep has to be at least as
trustworthy as the tests it grades.

**A failing mutant run is not a kill.** That inference — "the suite failed, so
the mutation took effect and a relevant assertion caught it" — is wrong in four
distinct ways, and each one produces a non-zero exit that looks like a kill:

* the mutation's target text was never present, so nothing was mutated;
* the edit was a no-op, leaving the tree identical to baseline;
* the mutant does not import, so every test fails for a reason that says nothing
  about any guard (the same weak-vs-strong distinction :mod:`gzkit.red_witness`
  refuses to collapse);
* the failures are unrelated tests, or the baseline was already red.

**A surviving run is equally unsafe** — it can conceal a mutation that never
activated, or a test tree that did not really run. That is exactly what GHI #963
observed: CPython validates a cached ``.pyc`` on ``(mtime-seconds, size)``, two
byte-identical-length mutations landed in the same clock second, and the second
subprocess imported the first mutant's bytecode. Its verdict described a tree it
had not tested, and the contamination runs in both directions.

So this module reports **four** outcomes, and the split is the point:
``killed`` and ``survived`` are claims about the GUARD; ``invalid`` and
``inconclusive`` are claims about the RUN. A sweep that lumps them together
reports coverage it never observed.

Isolation is unconditional: every mutant runs in a subprocess with its own
``PYTHONPYCACHEPREFIX``, so there is no stale cache entry for the ``(mtime,
size)`` heuristic to match and each run must compile from source.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.red_witness import classify_failure

MutationOutcome = Literal["killed", "survived", "invalid", "inconclusive"]

_RUN_TIMEOUT_S = 600
# unittest -v writes `test_name (module.Class.test_name) ... FAIL` and a
# `FAIL: test_name (...)` block; the summary line is the reliable one to read.
_TEST_LINE = re.compile(r"^\s*(\w+) \(([^)]+)\)(?: \(.*\))? \.\.\. (ok|FAIL|ERROR|skipped.*)$")
_FAILURE_LINE = re.compile(r"^(FAIL|ERROR): (\w+) \(([^)]+)\)")
_RAN_TESTS = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
_FIXTURE_FRAME = re.compile(
    r"^  File .*, line \d+, in (?:setUp|tearDown|setUpClass|tearDownClass|"
    r"setUpModule|tearDownModule|asyncSetUp|asyncTearDown|_callCleanup)$",
    re.MULTILINE,
)


class Mutation(BaseModel):
    """One text substitution to apply to the source under sweep."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    find: str = Field(..., min_length=1, description="Exact text to replace")
    replace: str = Field(..., description="Replacement text")
    label: str = Field(..., min_length=1, description="Short name for this mutation")
    expected_tests: list[str] = Field(
        default_factory=list,
        description="Nominated unittest IDs; short method names must resolve unambiguously",
    )


class MutationWitness(BaseModel):
    """The observed result of running the tree with one mutation applied."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str = Field(..., description="Mutation label")
    outcome: MutationOutcome = Field(..., description="killed | survived | invalid | inconclusive")
    reason: str = Field(default="", description="Why this outcome, when it is not a plain kill")
    target_present: bool = Field(default=False, description="The find-text existed in the source")
    source_changed: bool = Field(default=False, description="The edit actually altered the bytes")
    imports: bool = Field(
        default=False, description="Legacy field: source compiled; runtime import is not proven"
    )
    compiles: bool = Field(default=False, description="The mutated source compiled successfully")
    source_sha256: str = Field(default="", description="Digest of exact mutated source bytes")
    executed_tests: list[str] = Field(default_factory=list, description="Observed non-skipped IDs")
    tests_run: int = Field(default=0, description="unittest's reported run count")
    exit_status: int = Field(default=-1, description="Exit code of the mutated test run")
    failure_class: str = Field(default="", description="assertion | error | none")
    failing_tests: list[str] = Field(default_factory=list, description="Tests that failed")
    pycache_prefix: str = Field(default="", description="Isolated bytecode cache for this run")
    output_tail: str = Field(default="", description="Tail of the mutated run's output")


class MutationSweep(BaseModel):
    """All witnesses from one sweep, with run verdicts kept apart from guard verdicts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str = Field(..., description="File that was mutated")
    baseline_green: bool = Field(..., description="The unmutated tree passed")
    baseline_output_tail: str = Field(default="", description="Tail of the baseline run")
    source_sha256: str = Field(default="", description="Original source byte digest")
    restored_source_sha256: str = Field(default="", description="Restored source byte digest")
    baseline_executed_tests: list[str] = Field(default_factory=list)
    baseline_tests_run: int = Field(default=0)
    witnesses: list[MutationWitness] = Field(default_factory=list, description="Per-mutation")

    @property
    def killed(self) -> int:
        """Mutations a named, relevant test caught."""
        return sum(1 for w in self.witnesses if w.outcome == "killed")

    @property
    def survived(self) -> int:
        """Mutations that activated and no test caught."""
        return sum(1 for w in self.witnesses if w.outcome == "survived")

    @property
    def invalid(self) -> int:
        """Runs that graded nothing — absent target, no-op edit, unimportable mutant."""
        return sum(1 for w in self.witnesses if w.outcome == "invalid")

    @property
    def inconclusive(self) -> int:
        """Runs whose failure cannot be attributed to the guard under test."""
        return sum(1 for w in self.witnesses if w.outcome == "inconclusive")

    @property
    def is_conclusive(self) -> bool:
        """True only when every mutation produced a verdict about its guard.

        Deliberately not ``killed == len(witnesses)``: a sweep may legitimately
        contain a surviving mutant. What it may not contain, and still be quoted
        as evidence, is a row that graded nothing.
        """
        return bool(self.witnesses) and not (self.invalid or self.inconclusive)


def _test_id(method: str, context: str) -> str:
    """Normalize the two stdlib unittest identity display formats."""
    return context if context.endswith("." + method) else f"{context}.{method}"


def _test_observations(output: str) -> tuple[set[str], list[str], int]:
    """Read completed, non-skipped unittest IDs and failure identities.

    Unknown/custom runner output is inconclusive. This parses execution reports;
    it does not decide whether an assertion expresses the intended requirement.
    """
    executed: set[str] = set()
    failures: list[str] = []
    for line in output.splitlines():
        if match := _TEST_LINE.match(line):
            method, context, status = match.groups()
            if not status.startswith("skipped"):
                executed.add(_test_id(method, context))
        if match := _FAILURE_LINE.match(line):
            _, method, context = match.groups()
            identity = _test_id(method, context)
            executed.add(identity)
            if identity not in failures:
                failures.append(identity)
    summaries = _RAN_TESTS.findall(output)
    count = int(summaries[0]) if len(summaries) == 1 else 0
    return executed, failures, count


def _resolve_tests(selectors: list[str], executed: set[str]) -> set[str] | None:
    """Require each nominated selector to identify one actually executed test."""
    if not selectors:
        return None
    resolved: set[str] = set()
    for selector in selectors:
        matches = {identity for identity in executed if identity == selector}
        if "." not in selector:
            matches = {identity for identity in executed if identity.rsplit(".", 1)[-1] == selector}
        if len(matches) != 1:
            return None
        resolved.update(matches)
    return resolved


def _run(command: list[str], cwd: Path, pycache_prefix: Path) -> subprocess.CompletedProcess[str]:
    """Run the test command with an isolated bytecode cache (GHI #963)."""
    import os  # noqa: PLC0415 — only needed to copy the ambient environment

    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = str(pycache_prefix)
    return subprocess.run(  # noqa: S603 — the command is supplied by the sweep's author
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=_RUN_TIMEOUT_S,
    )


def _compiles(source: Path, cwd: Path, pycache_prefix: Path) -> bool:
    """Check syntax only; the test execution must separately establish usable behavior."""
    result = _run(
        [
            "python3",
            "-c",
            f"import py_compile; py_compile.compile({str(source)!r}, doraise=True)",
        ],
        cwd,
        pycache_prefix,
    )
    return result.returncode == 0


def _witness_one(
    mutation: Mutation,
    *,
    source: Path,
    original: str,
    cwd: Path,
    command: list[str],
    baseline_tests: set[str],
) -> MutationWitness:
    """Apply one mutation, run the tree in isolation, and classify what happened."""
    if mutation.find not in original:
        return MutationWitness(
            label=mutation.label,
            outcome="invalid",
            reason="mutation target absent from the source — nothing was mutated",
        )
    mutated = original.replace(mutation.find, mutation.replace, 1)
    if mutated == original:
        return MutationWitness(
            label=mutation.label,
            outcome="invalid",
            reason="mutation is a no-op — the tree is identical to baseline",
            target_present=True,
        )

    source.write_bytes(mutated.encode("utf-8"))
    with tempfile.TemporaryDirectory() as cache:
        prefix = Path(cache)
        if not _compiles(source, cwd, prefix):
            return MutationWitness(
                label=mutation.label,
                outcome="invalid",
                reason="mutated source does not compile — the failure is the edit, not a guard",
                target_present=True,
                source_changed=True,
                pycache_prefix=str(prefix),
            )
        result = _run(command, cwd, prefix)
        output = (result.stdout or "") + (result.stderr or "")
        executed, failing, count = _test_observations(output)

        def observed(outcome: MutationOutcome, reason: str = "") -> MutationWitness:
            """Build the witness from what this run actually observed."""
            return MutationWitness(
                label=mutation.label,
                outcome=outcome,
                reason=reason,
                target_present=True,
                source_changed=True,
                imports=True,
                compiles=True,
                source_sha256=hashlib.sha256(mutated.encode("utf-8")).hexdigest(),
                executed_tests=sorted(executed),
                tests_run=count,
                exit_status=result.returncode,
                failure_class=classify_failure(result.returncode, output),
                failing_tests=failing,
                pycache_prefix=str(prefix),
                output_tail="\n".join(output.splitlines()[-40:]),
            )

        nominated = _resolve_tests(mutation.expected_tests, baseline_tests)
        if nominated is None:
            return observed(
                "inconclusive", "nominated tests are absent, skipped, or ambiguous in baseline"
            )
        if count == 0 or not nominated.issubset(executed):
            return observed(
                "inconclusive", "nominated tests did not execute in a completed mutant run"
            )
        if result.returncode == 0:
            return observed("survived")
        if classify_failure(result.returncode, output) != "assertion":
            return observed("inconclusive", "the run did not report a clean assertion failure")
        if _FIXTURE_FRAME.search(output):
            return observed("inconclusive", "a fixture assertion failed outside the test body")
        if not (set(failing) & nominated):
            return observed(
                "inconclusive",
                "no expected test failed — the run witnessed collateral, not this guard's "
                f"coverage (expected any of {mutation.expected_tests})",
            )
        return observed("killed")


def run_mutation_sweep(
    project_root: Path,
    source: Path,
    mutations: list[Mutation],
    command: list[str],
) -> MutationSweep:
    """Run a mutation sweep, verifying baseline, activation, isolation and cause.

    The source file is always restored, including when a mutant leaves it
    unimportable — a sweep that can strand a broken tree is worse than no sweep.
    """
    original_bytes = source.read_bytes()
    original = original_bytes.decode("utf-8")
    with tempfile.TemporaryDirectory() as cache:
        baseline = _run(command, project_root, Path(cache))
    baseline_output = (baseline.stdout or "") + (baseline.stderr or "")
    baseline_tests, _, baseline_count = _test_observations(baseline_output)
    baseline_green = baseline.returncode == 0 and baseline_count > 0 and bool(baseline_tests)

    witnesses: list[MutationWitness] = []
    try:
        for mutation in mutations:
            if not baseline_green:
                witnesses.append(
                    MutationWitness(
                        label=mutation.label,
                        outcome="inconclusive",
                        reason="baseline is not green — no mutant's failure can be attributed",
                    )
                )
                continue
            witnesses.append(
                _witness_one(
                    mutation,
                    source=source,
                    original=original,
                    cwd=project_root,
                    command=command,
                    baseline_tests=baseline_tests,
                )
            )
            source.write_bytes(original_bytes)
    finally:
        source.write_bytes(original_bytes)

    return MutationSweep(
        source=str(source),
        baseline_green=baseline_green,
        source_sha256=hashlib.sha256(original_bytes).hexdigest(),
        restored_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        baseline_executed_tests=sorted(baseline_tests),
        baseline_tests_run=baseline_count,
        baseline_output_tail="\n".join(baseline_output.splitlines()[-40:]),
        witnesses=witnesses,
    )
