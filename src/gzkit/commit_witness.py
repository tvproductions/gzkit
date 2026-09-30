"""Falsifiability witness for a commit, keyed on its production hunks (GHI #927).

``gz arb red --req`` asks whether a REQ's covering test can fail. A guard added on
the direct-fix route has no REQ, so that question has no subject there, and the
route canon most encourages for defect repair carried no witness at all. The
instance: ``3c255459`` added ``_forbidden_mirror_names`` while touching twelve test
files, none of which drove it, and the suite stayed green.

This witness is keyed on the commit instead. Every production hunk the commit
ADDED is one mutant — that hunk reverted to the parent's text — swept against the
test modules the same commit touched, through :mod:`gzkit.mutation_witness` (so
baseline, activation, bytecode isolation and failure cause are all verified, and
``invalid``/``inconclusive`` stay apart from ``killed``/``survived``).

The commit's own test modules are the declared test set. That is what closes the
hole #927's direction 1 named — "the affected-test set has no declared source" —
and it is the right bar for a commit: a fix that adds a guard owes a test, in the
same commit, that fails without it. A commit touching no test module is reported
as such rather than graded.

A surviving hunk is a guard no test in its commit drives. A diff-shape proxy
("did the commit touch tests/?") passes ``3c255459``; this does not, because it
asks the question per hunk.

Pure deletions are not mutated: re-inserting removed code tests a different claim,
and this witness makes none about it.
"""

from __future__ import annotations

import ast
import re
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.mutation_witness import Mutation, _run, _test_observations, run_mutation_sweep
from gzkit.red_witness import _git, base_tree_worktree

CommitVerdict = Literal["driven", "undriven", "no-tests", "no-production-hunks", "inconclusive"]

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
#: Verbose unittest, so :func:`gzkit.mutation_witness._test_observations` can read IDs.
DEFAULT_RUNNER: tuple[str, ...] = ("uv", "run", "-m", "unittest", "-v")


class HunkWitness(BaseModel):
    """One reverted production hunk and what the commit's tests made of it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Repo-relative production file")
    label: str = Field(..., description="path:start-end of the added lines")
    outcome: str = Field(..., description="killed | survived | invalid | inconclusive")
    reason: str = Field(default="", description="Why, when not a plain kill")


class CommitWitness(BaseModel):
    """The commit-keyed witness result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commit: str = Field(..., description="Resolved commit SHA")
    test_modules: list[str] = Field(default_factory=list, description="Dotted test modules run")
    hunks: list[HunkWitness] = Field(default_factory=list, description="Per-hunk verdicts")
    verdict: CommitVerdict = Field(..., description="Aggregate verdict")
    detail: str = Field(default="", description="Why the verdict, when it is not per-hunk")

    @property
    def undriven(self) -> list[HunkWitness]:
        """Hunks whose revert no test in the commit noticed."""
        return [h for h in self.hunks if h.outcome == "survived"]


def _changed_files(project_root: Path, commit: str) -> list[tuple[str, str]]:
    """Return ``(status, path)`` for each ``.py`` file the commit changed vs its parent."""
    out = _git(["diff", "--name-status", "--no-renames", f"{commit}^", commit], project_root)
    if out.returncode != 0:
        raise RuntimeError(f"cannot diff {commit} against its parent: {out.stderr.strip()}")
    rows = []
    for line in out.stdout.splitlines():
        status, _, path = line.partition("\t")
        if path.endswith(".py"):
            rows.append((status.strip(), path.strip()))
    return rows


def _module_name(path: str) -> str:
    return path[: -len(".py")].replace("/", ".")


def _unique_window(lines: list[str], start: int, end: int) -> tuple[int, int]:
    """Widen ``lines[start:end]`` with context until its text occurs once in the file."""
    text = "".join(lines)
    lo, hi = start, end
    while text.count("".join(lines[lo:hi])) != 1 and (lo > 0 or hi < len(lines)):
        lo, hi = max(lo - 1, 0), min(hi + 1, len(lines))
    return lo, hi


#: Decorators that never read the signature they wrap. A signature annotation on a
#: function decorated with anything else may be read at runtime, so it stays behavior.
_ANNOTATION_BLIND_DECORATORS = frozenset(
    {
        "staticmethod",
        "classmethod",
        "property",
        "setter",
        "getter",
        "deleter",
        "abstractmethod",
        "override",
        "cache",
        "lru_cache",
        "cached_property",
        "wraps",
    }
)


def _decorator_name(node: ast.expr) -> str:
    """Return the bare name a decorator expression calls or refers to."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Attribute):
        return target.attr
    return target.id if isinstance(target, ast.Name) else ""


def _postponed_annotations(tree: ast.Module) -> bool:
    """Return whether the module has ``from __future__ import annotations`` (PEP 563)."""
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


def _drop_signature_annotations(tree: ast.Module) -> None:
    """Blank argument and return annotations no runtime reads.

    Under PEP 563 a signature annotation is a string stored in ``__annotations__``;
    it changes behavior only when something introspects it. Class-field annotations
    are kept (Pydantic builds fields from them), as are signatures under a decorator
    outside :data:`_ANNOTATION_BLIND_DECORATORS`, and every annotation in a module
    that evaluates them at definition time.
    """
    if not _postponed_annotations(tree):
        return
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_decorator_name(d) not in _ANNOTATION_BLIND_DECORATORS for d in node.decorator_list):
            continue
        node.returns = None
        arguments = node.args
        for arg in [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]:
            arg.annotation = None
        for arg in (arguments.vararg, arguments.kwarg):
            if arg is not None:
                arg.annotation = None


def _behavior(source: str) -> str | None:
    """Return an AST fingerprint with docstrings and inert annotations dropped.

    ``None`` when the source does not parse. Signature annotations no runtime reads
    are dropped too (:func:`_drop_signature_annotations`), so a hunk that only
    re-types a function is not swept as a guard.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    _drop_signature_annotations(tree)
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body[0] = ast.Pass()
    return ast.dump(tree)


def hunk_mutations(project_root: Path, commit: str, path: str) -> list[Mutation]:
    """Build one revert-this-hunk mutation per hunk that added lines to ``path``."""
    new_src = _git(["show", f"{commit}:{path}"], project_root)
    old_src = _git(["show", f"{commit}^:{path}"], project_root)
    if new_src.returncode != 0:
        return []
    new_lines = new_src.stdout.splitlines(keepends=True)
    old_lines = old_src.stdout.splitlines(keepends=True) if old_src.returncode == 0 else []
    diff = _git(["diff", "-U0", "--no-renames", f"{commit}^", commit, "--", path], project_root)
    mutations: list[Mutation] = []
    for line in diff.stdout.splitlines():
        match = _HUNK_HEADER.match(line)
        if not match:
            continue
        o_start, o_len = int(match.group(1)), int(match.group(2) or 1)
        n_start, n_len = int(match.group(3)), int(match.group(4) or 1)
        if n_len == 0:
            continue  # pure deletion: not mutated (see module docstring)
        n0 = n_start - 1
        old_block = old_lines[o_start - 1 : o_start - 1 + o_len] if o_len else []
        lo, hi = _unique_window(new_lines, n0, n0 + n_len)
        find = "".join(new_lines[lo:hi])
        tail = "".join(new_lines[n0 + n_len : hi])
        replace = "".join(new_lines[lo:n0]) + "".join(old_block) + tail
        original = "".join(new_lines)
        fingerprint = _behavior(original)
        if fingerprint is not None and _behavior(original.replace(find, replace, 1)) == fingerprint:
            continue  # comment/docstring/blank-only hunk: reverting it changes no behavior
        mutations.append(
            Mutation(find=find, replace=replace, label=f"{path}:{n_start}-{n_start + n_len - 1}")
        )
    return mutations


def _sweep_hunks(
    project_root: Path, sha: str, production: list[str], command: list[str]
) -> list[HunkWitness]:
    """Sweep each production file's added hunks in a worktree at ``sha``."""
    hunks: list[HunkWitness] = []
    with base_tree_worktree(project_root, sha) as worktree:
        with tempfile.TemporaryDirectory() as cache:
            baseline = _run(command, worktree, Path(cache))
        executed, _, _ = _test_observations((baseline.stdout or "") + (baseline.stderr or ""))
        expected = sorted(executed)
        for path in production:
            mutations = [
                m.model_copy(update={"expected_tests": expected})
                for m in hunk_mutations(project_root, sha, path)
            ]
            if not mutations:
                continue
            sweep = run_mutation_sweep(worktree, worktree / path, mutations, command)
            hunks.extend(
                HunkWitness(path=path, label=w.label, outcome=w.outcome, reason=w.reason)
                for w in sweep.witnesses
            )
    return hunks


def _aggregate(hunks: list[HunkWitness]) -> CommitVerdict:
    """Any survivor is undriven; only an all-killed sweep is driven."""
    outcomes = {h.outcome for h in hunks}
    if "survived" in outcomes:
        return "undriven"
    return "driven" if outcomes == {"killed"} else "inconclusive"


def run_commit_witness(
    project_root: Path,
    commit: str,
    tests_dir: str = "tests",
    runner: tuple[str, ...] = DEFAULT_RUNNER,
) -> CommitWitness:
    """Sweep every production hunk ``commit`` added against the tests it touched."""
    resolved = _git(["rev-parse", "--verify", f"{commit}^{{commit}}"], project_root)
    if resolved.returncode != 0:
        raise RuntimeError(f"cannot resolve commit {commit!r}: {resolved.stderr.strip()}")
    sha = resolved.stdout.strip()
    prefix = f"{tests_dir.rstrip('/')}/"
    live = [p for s, p in _changed_files(project_root, sha) if not s.startswith("D")]
    tests = sorted(p for p in live if p.startswith(prefix))
    production = sorted(p for p in live if not p.startswith(prefix))
    modules = [_module_name(p) for p in tests]

    if not production:
        return CommitWitness(
            commit=sha,
            test_modules=modules,
            verdict="no-production-hunks",
            detail="the commit adds or changes no production .py file",
        )
    if not tests:
        return CommitWitness(
            commit=sha,
            verdict="no-tests",
            detail=f"the commit changes {len(production)} production file(s) and no test "
            "module, so nothing in it can fail when its guards are removed",
        )
    hunks = _sweep_hunks(project_root, sha, production, [*runner, *modules])
    if not hunks:
        return CommitWitness(
            commit=sha,
            test_modules=modules,
            verdict="no-production-hunks",
            detail="no production hunk changes behavior (pure deletions, comments, docstrings)",
        )
    return CommitWitness(commit=sha, test_modules=modules, hunks=hunks, verdict=_aggregate(hunks))
