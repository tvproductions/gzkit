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

Each mutant runs only the touched modules whose traced run executed its lines or
read its file as text (:mod:`gzkit.reach_trace`, GHI #1260, #1269): a module that
neither runs nor reads a hunk cannot fail because of it, and running every module
for every mutant made a wide commit ungradable within the hang bound. When no
module reaches a hunk, all of them run.

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

A hunk is a textual unit, not a unit of behavior (GHI #1153). A fix that adds a
helper and its call site, or changes a signature and its callers, has hunks whose
lone revert raises instead of asserting, so the revert grades nothing. Such a hunk
is re-mutated one guard statement at a time; a hunk holding no guard statement
(a signature line, a constant) makes no guard claim and is reported as a
declaration, outside the aggregate verdict.
"""

import ast
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.mutation_witness import (
    Mutation,
    MutationWitness,
    _run,
    hang_reason,
    run_mutation_sweep,
)
from gzkit.reach_trace import ModuleReach, reaching_modules, trace_reach
from gzkit.red_witness import _git, base_tree_worktree

CommitVerdict = Literal["driven", "undriven", "no-tests", "no-production-hunks", "inconclusive"]
WitnessUnit = Literal["hunk", "statement", "declaration"]

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
#: Verbose unittest, so :func:`gzkit.unit_run_provenance.read_test_observations` can read IDs.
DEFAULT_RUNNER: tuple[str, ...] = ("uv", "run", "-m", "unittest", "-v")


class HunkWitness(BaseModel):
    """One reverted production hunk and what the commit's tests made of it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Repo-relative production file")
    label: str = Field(..., description="path:start-end of the added lines")
    outcome: str = Field(..., description="killed | survived | invalid | inconclusive")
    reason: str = Field(default="", description="Why, when not a plain kill")
    unit: WitnessUnit = Field(
        default="hunk",
        description="hunk | statement (one guard of an ungradable hunk) | declaration "
        "(an ungradable hunk with no guard statement; outside the aggregate)",
    )
    test_modules: list[str] = Field(
        default_factory=list,
        description="The commit's test modules that graded this row: those whose traced run "
        "executed its lines, or all of them when none did (GHI #1260)",
    )


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
        "contextmanager",
        "asynccontextmanager",
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


def _annotation_names(annotation: ast.expr) -> set[str]:
    """Return the names an annotation refers to, reading quoted annotations too."""
    names = {n.id for n in ast.walk(annotation) if isinstance(n, ast.Name)}
    for node in ast.walk(annotation):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                names |= _annotation_names(ast.parse(node.value, mode="eval").body)
            except SyntaxError:
                continue
    return names


def _drop_signature_annotations(tree: ast.Module, *, deferred: bool) -> set[str]:
    """Blank argument and return annotations no runtime reads; return the names they used.

    A signature annotation changes behavior only when something introspects it,
    once it is no longer evaluated at definition time: under PEP 563 (``from
    __future__ import annotations``) or, from Python 3.14, under PEP 649 for every
    module (``deferred``). Class-field annotations are kept (Pydantic builds fields
    from them), as are signatures under a decorator outside
    :data:`_ANNOTATION_BLIND_DECORATORS`.
    """
    if not (deferred or _postponed_annotations(tree)):
        return set()
    dropped: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_decorator_name(d) not in _ANNOTATION_BLIND_DECORATORS for d in node.decorator_list):
            continue
        arguments = node.args
        args = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
        args += [a for a in (arguments.vararg, arguments.kwarg) if a is not None]
        for annotation in [node.returns, *(a.annotation for a in args)]:
            if annotation is not None:
                dropped |= _annotation_names(annotation)
        node.returns = None
        for arg in args:
            arg.annotation = None
    return dropped


#: Modules imported only for their type names: binding one has no side effect, and
#: nothing re-exports them, so a name from one that no runtime code reads is inert.
_TYPING_MODULES = frozenset({"typing", "typing_extensions", "collections.abc"})


def _drop_annotation_only_imports(tree: ast.Module, names: set[str]) -> None:
    """Remove imported names that no runtime code reads, where that is provably inert.

    Swapping ``Iterator`` for ``Generator`` in an import only annotations read
    changes nothing a run can observe. A name is dropped when nothing left in the
    module reads it and either a dropped annotation named it or it comes from one
    of :data:`_TYPING_MODULES`; the second case keeps a revert of the signature
    hunk alone inert. Any other unread import may be a re-export or run for its
    side effect, so it stays.
    """
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            typing_only = node.module in _TYPING_MODULES
            node.names = [
                alias
                for alias in node.names
                if (bound := alias.asname or alias.name) in used
                or not (typing_only or bound in names)
            ]
        elif isinstance(node, ast.Import):
            node.names = [
                alias
                for alias in node.names
                if (bound := alias.asname or alias.name.split(".")[0]) in used or bound not in names
            ]


def _behavior(source: str, *, deferred: bool = False) -> str | None:
    """Return an AST fingerprint with docstrings and inert annotations dropped.

    ``None`` when the source does not parse. Signature annotations no runtime reads
    are dropped (:func:`_drop_signature_annotations`), with any import only they
    used, so a hunk that only re-types a function is not swept as a guard.
    ``deferred`` says the project runs on Python 3.14 or later (PEP 649).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    _drop_annotation_only_imports(tree, _drop_signature_annotations(tree, deferred=deferred))
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


def _defers_annotations(project_root: Path, commit: str) -> bool:
    """Return whether ``commit``'s ``requires-python`` floor is 3.14 or later (PEP 649)."""
    shown = _git(["show", f"{commit}:pyproject.toml"], project_root)
    if shown.returncode != 0:
        return False
    try:
        floor = tomllib.loads(shown.stdout).get("project", {}).get("requires-python", "")
    except tomllib.TOMLDecodeError:
        return False
    match = re.search(r">=\s*(\d+)\.(\d+)", str(floor))
    return bool(match) and (int(match.group(1)), int(match.group(2))) >= (3, 14)


def _splice(lines: list[str], start: int, end: int, replacement: str, label: str) -> Mutation:
    """Replace ``lines[start:end]`` with ``replacement``, anchored on text unique in the file."""
    lo, hi = _unique_window(lines, start, end)
    find = "".join(lines[lo:hi])
    replace = "".join(lines[lo:start]) + replacement + "".join(lines[end:hi])
    return Mutation(find=find, replace=replace, label=label)


#: Statement shapes that carry a guard: each is replaced with ``pass`` when its hunk
#: cannot be graded whole (GHI #1153).
_GUARD_STATEMENTS = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.TryStar,
    ast.Match,
    ast.Raise,
    ast.Assert,
    ast.Return,
    ast.Continue,
    ast.Break,
)


def statement_mutations(source: str, path: str, first: int, last: int) -> list[Mutation]:
    """Build one ``pass``-for-this-guard mutation per guard statement starting in ``first..last``.

    A statement that does not open its line (``if x: return``) is reached through the
    statement that does. A mutant that does not parse, or changes no behavior, is not
    built.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines(keepends=True)
    fingerprint = _behavior(source)
    spans = sorted(
        {
            (node.lineno, node.end_lineno or node.lineno)
            for node in ast.walk(tree)
            if isinstance(node, _GUARD_STATEMENTS)
            and first <= node.lineno <= last
            and node.col_offset
            == len(lines[node.lineno - 1]) - len(lines[node.lineno - 1].lstrip())
        }
    )
    mutations = []
    for start, end in spans:
        line = lines[start - 1]
        indent = line[: len(line) - len(line.lstrip())]
        mutation = _splice(lines, start - 1, end, f"{indent}pass\n", f"{path}:{start}-{end}")
        behavior = _behavior(source.replace(mutation.find, mutation.replace, 1))
        if behavior is not None and behavior != fingerprint:
            mutations.append(mutation)
    return mutations


def _hunk_units(project_root: Path, commit: str, path: str) -> list[tuple[Mutation, int, int]]:
    """Return each revert-this-hunk mutation with the 1-based added-line range it reverts."""
    new_src = _git(["show", f"{commit}:{path}"], project_root)
    old_src = _git(["show", f"{commit}^:{path}"], project_root)
    if new_src.returncode != 0:
        return []
    new_lines = new_src.stdout.splitlines(keepends=True)
    old_lines = old_src.stdout.splitlines(keepends=True) if old_src.returncode == 0 else []
    diff = _git(["diff", "-U0", "--no-renames", f"{commit}^", commit, "--", path], project_root)
    deferred = _defers_annotations(project_root, commit)
    units: list[tuple[Mutation, int, int]] = []
    for line in diff.stdout.splitlines():
        match = _HUNK_HEADER.match(line)
        if not match:
            continue
        o_start, o_len = int(match.group(1)), int(match.group(2) or 1)
        n_start, n_len = int(match.group(3)), int(match.group(4) or 1)
        if n_len == 0:
            continue  # pure deletion: not mutated (see module docstring)
        n0, n_end = n_start - 1, n_start + n_len - 1
        old_block = old_lines[o_start - 1 : o_start - 1 + o_len] if o_len else []
        mutation = _splice(new_lines, n0, n_end, "".join(old_block), f"{path}:{n_start}-{n_end}")
        original = "".join(new_lines)
        fingerprint = _behavior(original, deferred=deferred)
        reverted = original.replace(mutation.find, mutation.replace, 1)
        if fingerprint is not None and _behavior(reverted, deferred=deferred) == fingerprint:
            continue  # comment/docstring/blank-only hunk: reverting it changes no behavior
        units.append((mutation, n_start, n_end))
    return units


def _sweep_reached(
    worktree: Path,
    path: str,
    units: list[tuple[Mutation, int, int]],
    reach: dict[str, ModuleReach],
    runner: tuple[str, ...],
) -> list[tuple[MutationWitness, list[str], bool]]:
    """Sweep each unit against the modules that reach its lines (GHI #1260).

    Units that share a module set share one sweep, so each set pays one baseline.
    Returns, in unit order, the witness, the modules that graded it, and whether
    that sweep's baseline was green.
    """
    groups: dict[tuple[str, ...], list[int]] = {}
    for index, (_, first, last) in enumerate(units):
        modules = tuple(reaching_modules(reach, path, first, last))
        groups.setdefault(modules, []).append(index)
    graded: dict[int, tuple[MutationWitness, list[str], bool]] = {}
    for modules, indexes in groups.items():
        expected = sorted(set().union(*(reach[m].tests for m in modules)))
        mutations = [units[i][0].model_copy(update={"expected_tests": expected}) for i in indexes]
        sweep = run_mutation_sweep(worktree, worktree / path, mutations, [*runner, *modules])
        for index, witness in zip(indexes, sweep.witnesses, strict=True):
            graded[index] = (witness, list(modules), sweep.baseline_green)
    return [graded[i] for i in range(len(units))]


def _regrade(
    worktree: Path,
    path: str,
    hunk: HunkWitness,
    span: tuple[int, int],
    reach: dict[str, ModuleReach],
    runner: tuple[str, ...],
) -> list[HunkWitness]:
    """Re-mutate an ungradable hunk one guard statement at a time (GHI #1153)."""
    source = worktree / path
    statements = [
        (m, *_label_span(m.label))
        for m in statement_mutations(source.read_text(encoding="utf-8"), path, *span)
    ]
    if not statements:
        reason = f"no guard statement to grade; the hunk's revert: {hunk.reason}"
        return [hunk.model_copy(update={"reason": reason, "unit": "declaration"})]
    return [
        HunkWitness(
            path=path,
            label=w.label,
            outcome=w.outcome,
            reason=f"guard in {hunk.label}" + (f": {w.reason}" if w.reason else ""),
            unit="statement",
            test_modules=modules,
        )
        for w, modules, _ in _sweep_reached(worktree, path, statements, reach, runner)
    ]


def _label_span(label: str) -> tuple[int, int]:
    """Return the ``first, last`` line pair a ``path:first-last`` mutation label names."""
    first, _, last = label.rsplit(":", 1)[1].partition("-")
    return int(first), int(last)


def _sweep_hunks(
    project_root: Path, sha: str, production: list[str], runner: tuple[str, ...], modules: list[str]
) -> list[HunkWitness]:
    """Sweep each production file's added hunks in a worktree at ``sha``."""
    hunks: list[HunkWitness] = []
    with base_tree_worktree(project_root, sha) as worktree:
        reach = trace_reach(worktree, modules, runner, _run)
        for path in production:
            units = _hunk_units(project_root, sha, path)
            if not units:
                continue
            # The mutations are built from `git show` text, which has LF endings; a CRLF
            # checkout (Windows, no `eol=lf`) never contains it, so sweep that text instead.
            blob = _git(["show", f"{sha}:{path}"], project_root)
            (worktree / path).write_bytes(blob.stdout.encode("utf-8"))
            for (_, first, last), (w, graded_by, green) in zip(
                units, _sweep_reached(worktree, path, units, reach, runner), strict=True
            ):
                row = HunkWitness(
                    path=path,
                    label=w.label,
                    outcome=w.outcome,
                    reason=w.reason,
                    test_modules=graded_by,
                )
                if green and w.outcome in ("invalid", "inconclusive"):
                    hunks.extend(_regrade(worktree, path, row, (first, last), reach, runner))
                else:
                    hunks.append(row)
    return hunks


def _aggregate(hunks: list[HunkWitness]) -> CommitVerdict:
    """Any survivor is undriven; only an all-killed sweep is driven.

    A declaration row makes no guard claim, so it does not enter the verdict.
    """
    outcomes = {h.outcome for h in hunks if h.unit != "declaration"}
    if "survived" in outcomes:
        return "undriven"
    return "driven" if outcomes == {"killed"} else "inconclusive"


def run_commit_witness(
    project_root: Path,
    commit: str,
    tests_dir: str = "tests",
    runner: tuple[str, ...] = DEFAULT_RUNNER,
    features_dir: str = "features",
) -> CommitWitness:
    """Sweep every production hunk ``commit`` added against the tests it touched.

    A behave step module under ``features_dir`` is test code the unit runner never
    imports: it is neither a production hunk nor a test module here. Counting it as
    production made every commit that carries its Gate 4 scenarios read
    ``undriven`` whatever its guards did (measured 2026-10-15, OBPI-0.35.0-20).
    """
    resolved = _git(["rev-parse", "--verify", f"{commit}^{{commit}}"], project_root)
    if resolved.returncode != 0:
        raise RuntimeError(f"cannot resolve commit {commit!r}: {resolved.stderr.strip()}")
    sha = resolved.stdout.strip()
    prefix = f"{tests_dir.rstrip('/')}/"
    behave_prefix = f"{features_dir.rstrip('/')}/"
    live = [p for s, p in _changed_files(project_root, sha) if not s.startswith("D")]
    tests = sorted(p for p in live if p.startswith(prefix))
    production = sorted(
        p for p in live if not p.startswith(prefix) and not p.startswith(behave_prefix)
    )
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
    try:
        hunks = _sweep_hunks(project_root, sha, production, runner, modules)
    except subprocess.TimeoutExpired:
        # Only a module's traced run on the commit's tree can still raise here: each
        # mutant's run is graded inside the sweep. Without that baseline no hunk can
        # be graded (GHI #1179).
        return CommitWitness(
            commit=sha,
            test_modules=modules,
            verdict="inconclusive",
            detail="the experiment is void: "
            + hang_reason("the commit's own tests, run on the commit's own tree,"),
        )
    if not hunks:
        return CommitWitness(
            commit=sha,
            test_modules=modules,
            verdict="no-production-hunks",
            detail="no production hunk changes behavior (pure deletions, comments, docstrings)",
        )
    return CommitWitness(commit=sha, test_modules=modules, hunks=hunks, verdict=_aggregate(hunks))
