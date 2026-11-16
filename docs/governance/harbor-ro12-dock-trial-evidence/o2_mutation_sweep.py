# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O2's dock trial: every branch of O2's cited code mutated, red then green.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md`, rulings 27 and
90 to 99). Ruling 27 has each order's dock trial show each refusal red then green, and
ruling 90 chose a mutation sweep for O2.

Scope (ruling 92). Every function and verb O2's rows of § Mode Contract cite, each swept
whole, with ``gzkit.acceptance_store`` taken in the functions that branch on
``is_run_id`` (:data:`CITED`), ``gz validate --catalog``'s own path among them (ruling 98),
and (ruling 94) every helper of the same module those
functions call by name directly, ruling 96 (:func:`scope`). The tests are the
twelve modules ruling 92 names (:data:`MODULES`).

Mutants (ruling 94). Every branch is mutated by a mechanical AST rule, with no judgement
of what refuses: each ``if`` test, ``while`` test (ruling 99), comprehension filter and
conditional expression is forced true and forced false (``(test) or True``,
``(test) and False``, so a walrus still binds), each ``raise`` becomes ``pass``, and each
early ``return`` (any ``return`` that is not the last statement of its function's body)
becomes ``pass``. Ruling 99 adds two more: each ``except`` handler's body becomes
``raise``, so the error it caught passes through, and each boolean return has its value
forced true and forced false, a boolean return being one whose value is a comparison, a
``not`` or a boolean operation of those, or any return of a function annotated ``-> bool``.
The schema conditionals of ``order_transitioned`` are JSON, which the AST pass cannot read; their
``required`` lists and property rules keep their hand-written mutants
(:data:`SCHEMA_MUTANTS`). A mutant that changes a refusal's recovery step or a
manpage's documented output is a test gap, never wording (ruling 97). ``--plan`` prints
the scope and the mutants and runs nothing.

The run. Each mutant runs through :func:`gzkit.mutation_witness.run_mutation_sweep` in an
isolated copy of the tree against the twelve modules, nominating every test they execute,
so a broad kill is a test of the twelve failing on an assertion. Each mutant not killed
is then re-run, and the record keeps the two outcomes apart:

* inconclusive (ruling 91): re-run against each test that failed in the broad run, one
  at a time, until one kills it alone; a row none kills is disclosed with its tests.
* survived (ruling 95): re-run against the test modules outside the twelve that import
  the swept module or are named for it (``test_<stem>``, ``test_<stem>_*``, which reaches
  a verb's CLI tests); each test that fails there is then run alone the same way.

Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o2_mutation_sweep.py --plan
    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o2_mutation_sweep.py <out.json>
"""

import ast
import json
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(REPO / "src")]

from gzkit.mutation_witness import (  # noqa: E402
    Mutation,
    MutationSweep,
    MutationWitness,
    run_mutation_sweep,
)

BOOTSTRAP = "import sys; sys.path[:0] = ['src', '.']; import unittest; unittest.main(module=None)"
MODULES = (
    "tests.test_order_ledger",
    "tests.test_order_ledger_schema",
    "tests.test_order_run",
    "tests.test_work_package_ledger",
    "tests.commands.test_wp_order",
    "tests.commands.test_wp_order_run",
    "tests.commands.test_wp_order_acceptance",
    "tests.commands.test_wp_req",
    "tests.governance.test_catalog_orders",
    "tests.governance.test_catalog_repair_reqs",
    # Ruling 92, as put: the two modules join the rows' ten self-test modules.
    "tests.commands.test_wp_run",
    "tests.commands.test_wp_acceptance",
)
#: Ruling 92's functions per file; ``None`` takes every function in the file.
CITED: dict[str, tuple[str, ...] | None] = {
    "src/gzkit/order_ledger.py": None,
    "src/gzkit/commands/wp_order.py": None,
    "src/gzkit/governance/trust_audits/catalog.py": (
        # Ruling 98: the path of `gz validate --catalog` that reads the rows' breaches.
        "audit_catalog",
        "_structure_findings",
        "order_findings",
        "_repair_req_breaches",
        "req_breaches",
        "_supersession_cycles",
        "_alias_breaches",
        "order_breaches",
        "_booked_order_findings",
        "_booked_req_findings",
    ),
    "src/gzkit/work_package_run.py": (
        "_require_order",
        "_package_order",
        "_order_subject",
        "_check_not_stopped",
        "_dispatch_subject",
        "record_work_package_dispatch",
        "_check_blockable",
        "record_work_package_block",
        "record_work_package_unblock",
        "open_unclaimed_dispatches",
        "run_positions",
    ),
    "src/gzkit/work_package_ledger.py": (
        "_check_repair_close",
        "_check_baselined",
        "_check_closed",
        "footprint_sealed",
        "declared_modules",
    ),
    "src/gzkit/order_store.py": ("stage_order",),
    "src/gzkit/commands/wp_req.py": None,
    "src/gzkit/req_store.py": ("stage_repair_req",),
    "src/gzkit/work_package_fence.py": None,
    "src/gzkit/commands/wp.py": (
        "wp_dispatch_cmd",
        "wp_block_cmd",
        "wp_unblock_cmd",
        "_with_modules",
    ),
    "src/gzkit/acceptance_package.py": ("order_contract",),
    "src/gzkit/acceptance_store.py": (
        "resolve_brief",
        "_without_departed",
        "initialize",
        "record_human_review",
        "owed_ids",
        "acceptance_verb",
    ),
    "src/gzkit/schemas/ledger.json": (),
}
#: Ruling 96: ruling 94's helpers are those a cited function calls directly, never their
#: own helpers in turn; ``--plan`` prints both sets.
HELPERS_TRANSITIVE = False
WORKERS = 4

_SCHEMA_INDENT = " " * 12


def _blank_string(field: str, *, last: bool) -> Mutation:
    """Drop the ``min_length`` rule from one string property of ``order_transitioned``."""
    tail = "\n" if last else ",\n"
    return Mutation(
        find=(
            f'              "{field}": {{\n'
            '                "type": "string",\n'
            '                "min_length": 1\n'
            f"              }}{tail}"
        ),
        replace=(
            f'              "{field}": {{\n'
            '                "type": "string"\n'
            f"              }}{tail}"
        ),
        label=f"ledger.json:order_transitioned a blank {field} passes",
    )


#: The schema conditionals' property rules and ``required`` lists, kept by ruling 94.
SCHEMA_MUTANTS: tuple[Mutation, ...] = (
    _blank_string("attestor", last=False),
    _blank_string("attestation_text", last=True),
    _blank_string("residual_risk", last=True),
    _blank_string("superseded_by", last=True),
    _blank_string("revisit_condition", last=True),
    Mutation(
        find=(
            '              "acceptance_ready": {\n'
            '                "type": "boolean"\n'
            "              }\n"
        ),
        replace=(
            '              "acceptance_ready": {\n'
            '                "type": ["boolean", "null"]\n'
            "              }\n"
        ),
        label="ledger.json:order_transitioned a null acceptance_ready passes",
    ),
    *(
        Mutation(
            find=_SCHEMA_INDENT
            + '"required": [\n'
            + ",\n".join(f'{_SCHEMA_INDENT}  "{field}"' for field in fields)
            + f"\n{_SCHEMA_INDENT}],\n",
            replace=_SCHEMA_INDENT + '"required": [],\n',
            label=f"ledger.json:order_transitioned {when} books without {fields[0]}",
        )
        for when, fields in (
            ("accepted", ("acceptance_ready",)),
            ("closed", ("decision", "attestor", "attestation_text")),
            ("proceed", ("residual_risk",)),
            ("redirect", ("superseded_by",)),
            ("pause", ("revisit_condition",)),
        )
    ),
)

_Func = ast.FunctionDef | ast.AsyncFunctionDef


def _functions(tree: ast.Module) -> dict[str, _Func]:
    """Return the module's top-level functions and class methods by name."""
    found: dict[str, _Func] = {}
    for node in tree.body:
        if isinstance(node, _Func):
            found[node.name] = node
        elif isinstance(node, ast.ClassDef):
            found.update(
                {f"{node.name}.{m.name}": m for m in node.body if isinstance(m, _Func)}
            )
    return found


def _calls(func: _Func, names: set[str]) -> set[str]:
    """Return the same-module functions *func* calls by bare name."""
    return {
        node.func.id
        for node in ast.walk(func)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names
    }


def scope(path: Path, cited: tuple[str, ...] | None, *, transitive: bool) -> dict[str, list[str]]:
    """Return ruling 92's cited functions in *path* and the helpers ruling 94 adds.

    Returns:
        ``cited`` and ``helpers``, each a sorted list of function names.

    Raises:
        SystemExit: a cited function is not in *path*, so the scope table has drifted.

    """
    if cited == ():
        return {"cited": [], "helpers": []}
    functions = _functions(ast.parse(path.read_text(encoding="utf-8")))
    taken = set(functions) if cited is None else set(cited)
    missing = taken - set(functions)
    if missing:
        msg = f"{path}: cited functions not found: {sorted(missing)}"
        raise SystemExit(msg)
    helpers: set[str] = set()
    frontier = set(taken)
    while frontier:
        called = set().union(*(_calls(functions[n], set(functions)) for n in frontier))
        new = called - taken - helpers
        helpers |= new
        frontier = new if transitive else set()
    return {"cited": sorted(taken), "helpers": sorted(helpers)}


class _Source:
    """A source file's bytes with line offsets, for byte-exact unique edits."""

    def __init__(self, text: str) -> None:
        self.data = text.encode("utf-8")
        self.starts = [0]
        for line in self.data.splitlines(keepends=True):
            self.starts.append(self.starts[-1] + len(line))

    def offset(self, lineno: int, col: int) -> int:
        return self.starts[lineno - 1] + col

    def edit(self, node: ast.expr | ast.stmt, new: str, label: str) -> Mutation | None:
        """Replace *node*'s span with *new*, its context widened until the find is unique."""
        begin = self.offset(node.lineno, node.col_offset)
        end = self.offset(node.end_lineno or node.lineno, node.end_col_offset or 0)
        first, last = node.lineno, node.end_lineno or node.lineno
        lines = len(self.starts) - 1
        while True:
            lo, hi = self.starts[first - 1], self.starts[last]
            find = self.data[lo:hi]
            if self.data.count(find) == 1:
                replace = find[: begin - lo] + new.encode("utf-8") + find[end - lo :]
                return Mutation(
                    find=find.decode("utf-8"), replace=replace.decode("utf-8"), label=label
                )
            if first == 1 and last == lines:
                return None
            first, last = max(1, first - 1), min(lines, last + 1)

    def segment(self, node: ast.expr | ast.stmt) -> str:
        begin = self.offset(node.lineno, node.col_offset)
        end = self.offset(node.end_lineno or node.lineno, node.end_col_offset or 0)
        return self.data[begin:end].decode("utf-8")


def _final_returns(func: _Func) -> set[int]:
    """Return the ids of the returns that end a function body, its nested functions' too."""
    return {
        id(node.body[-1])
        for node in ast.walk(func)
        if isinstance(node, _Func) and isinstance(node.body[-1], ast.Return)
    }


def _is_boolean(value: ast.expr) -> bool:
    """Return whether *value* is a comparison, a ``not`` or a boolean operation of those."""
    if isinstance(value, ast.Compare):
        return True
    if isinstance(value, ast.UnaryOp):
        return isinstance(value.op, ast.Not)
    if isinstance(value, ast.BoolOp):
        return all(_is_boolean(operand) for operand in value.values)
    return False


def _boolean_returns(func: _Func) -> list[ast.expr]:
    """Return the values of ruling 99's boolean returns in *func* and its nested functions."""
    found: list[ast.expr] = []

    def visit(node: ast.AST, owner: _Func) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _Func):
                visit(child, child)
                continue
            if isinstance(child, ast.Return) and child.value is not None:
                annotated = isinstance(owner.returns, ast.Name) and owner.returns.id == "bool"
                if annotated or _is_boolean(child.value):
                    found.append(child.value)
            visit(child, owner)

    visit(func, func)
    return found


def _handler_body(handler: ast.ExceptHandler) -> ast.stmt:
    """Return a node spanning *handler*'s whole body, for one edit."""
    span = ast.Pass()
    first, last = handler.body[0], handler.body[-1]
    span.lineno, span.col_offset = first.lineno, first.col_offset
    span.end_lineno, span.end_col_offset = last.end_lineno, last.end_col_offset
    return span


def _branch_mutants(src: _Source, name: str, func: _Func, prefix: str) -> list[Mutation]:
    """Apply ruling 94's rule, widened by ruling 99, to every branch of one function."""
    finals = _final_returns(func)
    found: list[Mutation | None] = []
    for value in _boolean_returns(func):
        where = f"{prefix}:{name}:{value.lineno}:{value.col_offset}"
        text = src.segment(value)
        found.extend((
            src.edit(value, f"(({text}) or True)", f"{where} boolreturn forced true"),
            src.edit(value, f"(({text}) and False)", f"{where} boolreturn forced false"),
        ))
    for node in ast.walk(func):
        tests: list[tuple[ast.expr, str]] = []
        if isinstance(node, ast.If):
            tests.append((node.test, "if"))
        elif isinstance(node, ast.While):
            tests.append((node.test, "while"))
        elif isinstance(node, ast.IfExp):
            tests.append((node.test, "ifexp"))
        elif isinstance(node, ast.comprehension):
            tests.extend((test, "filter") for test in node.ifs)
        for test, kind in tests:
            where = f"{prefix}:{name}:{test.lineno}:{test.col_offset}"
            text = src.segment(test)
            found.extend((
                src.edit(test, f"(({text}) or True)", f"{where} {kind} forced true"),
                src.edit(test, f"(({text}) and False)", f"{where} {kind} forced false"),
            ))
        where = f"{prefix}:{name}:{getattr(node, 'lineno', 0)}:{getattr(node, 'col_offset', 0)}"
        if isinstance(node, ast.Raise):
            found.append(src.edit(node, "pass", f"{where} raise removed"))
        if isinstance(node, ast.ExceptHandler):
            found.append(src.edit(_handler_body(node), "raise", f"{where} handler re-raises"))
        if isinstance(node, ast.Return) and id(node) not in finals:
            found.append(src.edit(node, "pass", f"{where} early return removed"))
    return [m for m in found if m is not None]


def mutants(path: Path, functions: list[str]) -> list[Mutation]:
    """Every branch mutant in *functions* of *path*, de-duplicated by edit."""
    if path.suffix == ".json":
        return list(SCHEMA_MUTANTS)
    text = path.read_text(encoding="utf-8")
    src = _Source(text)
    table = _functions(ast.parse(text))
    seen: set[tuple[str, str]] = set()
    out: list[Mutation] = []
    for name in functions:
        for mutation in _branch_mutants(src, name, table[name], path.name):
            key = (mutation.find, mutation.replace)
            if key not in seen:
                seen.add(key)
                out.append(mutation)
    return out


def _importers(relative: str) -> list[str]:
    """Return the test modules outside the twelve that import or are named for the module.

    A verb's tests reach it through ``gzkit.cli.main`` and import nothing of it, so a test
    module whose file name begins ``test_<stem>`` is taken as well.
    """
    dotted = relative.removeprefix("src/").removesuffix(".py").replace("/", ".")
    parent, _, leaf = dotted.rpartition(".")
    found: list[str] = []
    for path in sorted((REPO / "tests").rglob("test*.py")):
        module = path.relative_to(REPO).with_suffix("").as_posix().replace("/", ".")
        if module in MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        named = path.stem == f"test_{leaf}" or path.stem.startswith(f"test_{leaf}_")
        if named or any(_imports(node, parent, leaf) for node in ast.walk(tree)):
            found.append(module)
    return found


def _imports(node: ast.AST, parent: str, leaf: str) -> bool:
    """Report whether *node* imports the module ``parent.leaf``."""
    dotted = f"{parent}.{leaf}"
    if isinstance(node, ast.Import):
        return any(alias.name == dotted for alias in node.names)
    if not isinstance(node, ast.ImportFrom):
        return False
    return node.module == dotted or (
        node.module == parent and any(alias.name == leaf for alias in node.names)
    )


def _command(tests: list[str] | tuple[str, ...]) -> list[str]:
    return [sys.executable, "-c", BOOTSTRAP, "-v", *tests]


def _witness_entry(w: MutationWitness) -> dict[str, object]:
    return {
        "label": w.label,
        "outcome": w.outcome,
        "reason": w.reason,
        "failure_class": w.failure_class,
        "failing_tests": w.failing_tests,
    }


def _alone(root: Path, target: Path, mutation: Mutation, tests: list[str]) -> dict[str, object]:
    """Run *mutation* against each test alone until one kills it."""
    tried: list[dict[str, object]] = []
    for test in tests:
        rerun = run_mutation_sweep(
            root, target, [mutation.model_copy(update={"expected_tests": [test]})], _command([test])
        )
        w = rerun.witnesses[0]
        tried.append({
            "test": test,
            "baseline_green": rerun.baseline_green,
            "outcome": w.outcome,
            "failure_class": w.failure_class,
        })
        if w.outcome == "killed":
            return {"outcome": "killed", "killed_by": test, "tried": tried}
    return {"outcome": "disclosed", "killed_by": None, "tried": tried}


def _follow_up(
    root: Path, relative: str, mutation: Mutation, broad: MutationWitness
) -> dict[str, object]:
    """Re-run one non-kill under ruling 91 (inconclusive) or ruling 95 (survived)."""
    target = root / relative
    entry: dict[str, object] = {"label": broad.label, "broad_outcome": broad.outcome}
    if broad.outcome == "inconclusive":
        entry["ruling"] = 91
        entry.update(_alone(root, target, mutation, list(broad.failing_tests)))
        return entry
    entry["ruling"] = 95
    outside = _importers(relative)
    entry["outside_modules"] = outside
    if not outside:
        entry.update({"outcome": "no test outside imports the module", "killed_by": None})
        return entry
    probe = run_mutation_sweep(root, target, [], _command(outside))
    nominated = mutation.model_copy(update={"expected_tests": probe.baseline_executed_tests})
    wide = run_mutation_sweep(root, target, [nominated], _command(outside)).witnesses[0]
    entry["outside_baseline_green"] = probe.baseline_green
    entry["outside"] = _witness_entry(wide)
    if wide.outcome == "survived":
        entry.update({"outcome": "survived outside", "killed_by": None})
        return entry
    entry.update(_alone(root, target, mutation, list(wide.failing_tests)))
    return entry


def _sweep_entry(relative: str, found: dict[str, list[str]], sweep: MutationSweep) -> dict:
    return {
        "source": relative,
        "scope": found,
        "baseline_green": sweep.baseline_green,
        "baseline_tests_run": sweep.baseline_tests_run,
        "source_restored": sweep.source_sha256 == sweep.restored_source_sha256,
        "conclusive": sweep.is_conclusive,
        "counts": {
            "killed": sweep.killed,
            "survived": sweep.survived,
            "invalid": sweep.invalid,
            "inconclusive": sweep.inconclusive,
        },
        "mutants": [_witness_entry(w) for w in sweep.witnesses],
    }


def _copy(root: Path) -> None:
    """Copy what the tests read into *root*, leaving bytecode behind."""
    names = ("src", "tests", "data", ".gzkit", "docs", ".claude", "pyproject.toml", ".gzkit.json")
    for name in names:
        source = REPO / name
        if source.is_dir():
            shutil.copytree(source, root / name, ignore=shutil.ignore_patterns("__pycache__"))
        elif source.exists():
            shutil.copy2(source, root / name)


def _planned(relative: str) -> tuple[dict[str, list[str]], list[Mutation]]:
    found = scope(REPO / relative, CITED[relative], transitive=HELPERS_TRANSITIVE)
    taken = found["cited"] + found["helpers"]
    return found, mutants(REPO / relative, taken)


def _run_file(relative: str) -> tuple[dict, list[dict[str, object]]]:
    """Sweep one file in its own copy of the tree, then follow up each non-kill."""
    found, planned = _planned(relative)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _copy(root)
        target = root / relative
        probe = run_mutation_sweep(root, target, [], _command(MODULES))
        tests = probe.baseline_executed_tests
        nominated = [m.model_copy(update={"expected_tests": tests}) for m in planned]
        sweep = run_mutation_sweep(root, target, nominated, _command(MODULES))
        by_label = {m.label: m for m in planned}
        follow = [
            {"source": relative, **_follow_up(root, relative, by_label[w.label], w)}
            for w in sweep.witnesses
            if w.outcome in {"inconclusive", "survived"}
        ]
    counts = (sweep.killed, sweep.survived, sweep.invalid, sweep.inconclusive)
    sys.stdout.write(f"{relative} {counts}\n")
    sys.stdout.flush()
    return _sweep_entry(relative, found, sweep), follow


def plan() -> int:
    """Print each file's scope, both helper readings, and its mutant count."""
    total = 0
    for relative, cited in CITED.items():
        direct = scope(REPO / relative, cited, transitive=False)
        closure = scope(REPO / relative, cited, transitive=True)
        found, planned = _planned(relative)
        total += len(planned)
        sys.stdout.write(f"\n{relative}: {len(planned)} mutants\n")
        sys.stdout.write(f"  cited ({len(found['cited'])}): {', '.join(found['cited'])}\n")
        sys.stdout.write(f"  helpers, direct ({len(direct['helpers'])}): ")
        sys.stdout.write(", ".join(direct["helpers"]) + "\n")
        extra = sorted(set(closure["helpers"]) - set(direct["helpers"]))
        sys.stdout.write(f"  added if transitive ({len(extra)}): {', '.join(extra)}\n")
    sys.stdout.write(f"\ntotal mutants under HELPERS_TRANSITIVE={HELPERS_TRANSITIVE}: {total}\n")
    return 0


def main(out: Path) -> int:
    """Run every file's sweep and follow-ups, and write the record to *out*.

    Returns:
        Zero once the record is written.

    """
    record: dict[str, object] = {
        "modules": list(MODULES),
        "helpers_transitive": HELPERS_TRANSITIVE,
        "workers": WORKERS,
        "sweeps": [],
        "follow_ups": [],
    }
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(_run_file, CITED))
    record["sweeps"] = [entry for entry, _ in results]
    record["follow_ups"] = [row for _, rows in results for row in rows]
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--plan"]:
        raise SystemExit(plan())
    raise SystemExit(main(Path(sys.argv[1])))
