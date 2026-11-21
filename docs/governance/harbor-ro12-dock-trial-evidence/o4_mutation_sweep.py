# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O4's dock trial: every branch O4's rows cite and its tasks changed, red then green.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md`, rulings 27 and
195 to 199). Ruling 195 makes O4's trial a red-proof sweep alone, O3's code-path half
reused, with no flight: every O4 refusal is a code path.

Scope (rulings 196 and 197). The two rows of § Mode Contract that wait on O4's trial, the
maintenance record's entry refusals and the list of discrepancies' refusals, by the
functions they cite (:data:`ROW_CITED`); and every function whose body a commit of O4's
tasks 3 and 4, and task 5's ruling-199 fix, changed (:data:`TASKS`), read mechanically
from each commit's diff against that commit's own tree and kept by name where HEAD still
holds it. ``gzkit/mx/log.py`` and ``gzkit/mx/git_commits.py``, new at task 4, and the
module ``gzkit.mx.series``, which the entry row cites, are swept whole (:data:`WHOLE`).
Each cited function takes ruling 96's direct helpers of the same module.

Mutants and the run (ruling 195). O2's mechanical AST rule, imported from
``o2_mutation_sweep`` so the rule cannot drift between trials, and O3's narrowed run,
imported from ``o3_mutation_sweep``: each file's mutants run only against the self-test
modules of the rows that cite its functions (:data:`MODULES`), and an inconclusive row is
re-run against each test that failed, one at a time, until one kills it alone.

Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o4_mutation_sweep.py --plan
    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o4_mutation_sweep.py <out.json>
"""

import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(HERE)]

import o2_mutation_sweep as rule  # noqa: E402
import o3_mutation_sweep as narrowed  # noqa: E402

from gzkit.mutation_witness import Mutation, run_mutation_sweep  # noqa: E402

#: The task trailers whose commits ruling 196 takes, task 5's for ruling 199's fix.
TASKS = (
    "TASK-rp12-o4-task3-carry",
    "TASK-rp12-o4-task4-record-view",
    "TASK-rp12-o4-task5-dock-trial",
)
#: Ruling 196's two rows: the functions each cites.
ROW_CITED: dict[str, tuple[str, ...]] = {
    "src/gzkit/mx/entries.py": ("record_entry_book", "maintenance_record"),
    "src/gzkit/mx/discrepancies.py": ("record_discrepancy", "record_discrepancy_clear"),
    # The row named it under `gzkit.mx.discrepancies`; it lives in `record_rows`.
    "src/gzkit/mx/record_rows.py": ("discrepancy_list",),
}
#: Swept whole: task 4's new modules and the module the entry row cites (ruling 197).
WHOLE = ("src/gzkit/mx/log.py", "src/gzkit/mx/git_commits.py", "src/gzkit/mx/series.py")

_ENTRY = ("tests.test_entries", "tests.commands.test_wp_entry")
_DSC = ("tests.test_discrepancies", "tests.commands.test_wp_discrepancy")
_LOG = (
    "tests.mx.test_mx_log",
    "tests.test_entries",
    "tests.commands.test_wp_entry",
    "tests.commands.test_mx_exit",
)
# The carry's own tests (rulings 171, 184 to 188, 199) sit in the tag-out log's module
# and the order ledger's, beside O2's and O3's rows' modules for the same files.
_CARRY = ("tests.test_tag_out", "tests.test_order_ledger", "tests.test_discrepancies")
#: The self-test modules of the rows that cite each file's functions.
MODULES: dict[str, tuple[str, ...]] = {
    "src/gzkit/mx/entries.py": tuple(dict.fromkeys((*_ENTRY, *_LOG))),
    "src/gzkit/mx/discrepancies.py": tuple(dict.fromkeys((*_DSC, *_CARRY))),
    "src/gzkit/mx/series.py": tuple(dict.fromkeys((*_ENTRY, *_DSC, "tests.test_tag_out"))),
    "src/gzkit/mx/record_rows.py": tuple(dict.fromkeys((*_DSC, *_CARRY))),
    "src/gzkit/mx/log.py": _LOG,
    "src/gzkit/mx/git_commits.py": _LOG,
    "src/gzkit/commands/mx_cmd.py": _LOG,
    "src/gzkit/commands/wp_entry.py": _ENTRY,
    "src/gzkit/cli/parser_wp_entry.py": _ENTRY,
    "src/gzkit/cli/parser_governance.py": _ENTRY,
    "src/gzkit/commands/wp_discrepancy.py": _DSC,
    "src/gzkit/mx/tag_out.py": tuple(dict.fromkeys((*narrowed._TAG, *_CARRY))),  # noqa: SLF001
    "src/gzkit/commands/wp_tag.py": narrowed._TAG,  # noqa: SLF001
    "src/gzkit/order_ledger.py": tuple(
        dict.fromkeys((*narrowed._LIFECYCLE, *narrowed._GATE5, *_CARRY))  # noqa: SLF001
    ),
    "src/gzkit/commands/wp_order.py": (
        "tests.commands.test_wp_order",
        "tests.commands.test_wp_order_acceptance",
    ),
    "src/gzkit/work_package_ledger.py": tuple(
        dict.fromkeys((*narrowed._GATE5, *_CARRY))  # noqa: SLF001
    ),
    "src/gzkit/work_package_run.py": tuple(
        dict.fromkeys((*narrowed._RUN, *_CARRY, "tests.commands.test_wp"))  # noqa: SLF001
    ),
}
WORKERS = 4
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.MULTILINE)


def _git(*args: str) -> str:
    """Run git in the checkout and return its output.

    Returns:
        Its standard output.

    """
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, errors="replace", check=True
    ).stdout


@cache
def commits() -> tuple[str, ...]:
    """Return every commit carrying one of :data:`TASKS` that touches Python source.

    Returns:
        The commit hashes, oldest first.

    """
    found: list[str] = []
    for task in TASKS:
        out = _git("log", "--reverse", "--format=%H", f"--grep=^Task: {task}$", "--", "src/*.py")
        found.extend(out.split())
    return tuple(found)


def _changed_lines(sha: str, relative: str) -> set[int]:
    """Return the post-image lines *sha*'s diff touches in *relative*, a deletion's neighbour."""
    diff = _git("diff", "-U0", f"{sha}^", sha, "--", relative)
    lines: set[int] = set()
    for start, count in _HUNK.findall(diff):
        first, span = int(start), int(count or "1")
        lines.update(range(first, first + span) if span else (first, first + 1))
    return lines


def changed_functions() -> dict[str, dict[str, list[str]]]:
    """Return, per file, the functions O4's commits changed, by name, and those HEAD lost.

    A function is changed when a line its body spans in the commit's own tree is one the
    commit's diff adds or replaces, or borders one it deletes (ruling 197).

    Returns:
        ``{file: {"changed": [...], "gone": [...]}}`` for every Python file touched.

    """
    named: dict[str, set[str]] = {}
    for sha in commits():
        for relative in _git("diff", "--name-only", f"{sha}^", sha, "--", "src/*.py").split():
            lines = _changed_lines(sha, relative)
            try:
                text = _git("show", f"{sha}:{relative}")
            except subprocess.CalledProcessError:
                continue
            for name, func in rule._functions(rule.ast.parse(text)).items():  # noqa: SLF001
                span = set(range(func.lineno, (func.end_lineno or func.lineno) + 1))
                if span & lines:
                    named.setdefault(relative, set()).add(name)
    result: dict[str, dict[str, list[str]]] = {}
    for relative, names in sorted(named.items()):
        path = REPO / relative
        held: set[str] = set()
        if path.exists():
            held = set(rule._functions(rule.ast.parse(path.read_text(encoding="utf-8"))))  # noqa: SLF001
        result[relative] = {"changed": sorted(names & held), "gone": sorted(names - held)}
    return result


@cache
def selection() -> dict[str, tuple[str, ...] | None]:
    """Return each file's cited functions, ``None`` taking the file whole.

    Returns:
        The rows' functions joined with the changed ones, :data:`WHOLE` whole.

    """
    cited: dict[str, set[str]] = {k: set(v) for k, v in ROW_CITED.items()}
    for relative, found in changed_functions().items():
        cited.setdefault(relative, set()).update(found["changed"])
    chosen: dict[str, tuple[str, ...] | None] = {
        relative: tuple(sorted(names)) for relative, names in cited.items() if names
    }
    chosen.update(dict.fromkeys(WHOLE))
    return dict(sorted(chosen.items()))


def planned(relative: str) -> tuple[dict[str, list[str]], list[Mutation]]:
    """Return *relative*'s scope and its mutants under O2's rule, direct helpers only."""
    found = rule.scope(REPO / relative, selection()[relative], transitive=False)
    return found, rule.mutants(REPO / relative, found["cited"] + found["helpers"])


def _run_file(relative: str) -> dict[str, object]:
    """Sweep one file in its own copy of the tree, re-running each inconclusive row alone."""
    found, mutations = planned(relative)
    modules = MODULES[relative]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        narrowed._copy(root)  # noqa: SLF001
        target = root / relative
        probe = run_mutation_sweep(root, target, [], rule._command(modules))  # noqa: SLF001
        tests = probe.baseline_executed_tests
        nominated = [m.model_copy(update={"expected_tests": tests}) for m in mutations]
        sweep = run_mutation_sweep(root, target, nominated, rule._command(modules))  # noqa: SLF001
        by_label = {m.label: m for m in mutations}
        follow = [
            {
                "label": w.label,
                "broad_outcome": w.outcome,
                **rule._alone(root, target, by_label[w.label], list(w.failing_tests)),  # noqa: SLF001
            }
            for w in sweep.witnesses
            if w.outcome == "inconclusive"
        ]
    counts = {
        "killed": sweep.killed,
        "survived": sweep.survived,
        "invalid": sweep.invalid,
        "inconclusive": sweep.inconclusive,
    }
    sys.stdout.write(f"{relative} {counts}\n")
    sys.stdout.flush()
    return {
        "source": relative,
        "tree": narrowed._tree(),  # noqa: SLF001
        "scope": found,
        "modules": list(modules),
        "baseline_green": sweep.baseline_green,
        "baseline_tests_run": sweep.baseline_tests_run,
        "source_restored": sweep.source_sha256 == sweep.restored_source_sha256,
        "counts": counts,
        "mutants": [rule._witness_entry(w) for w in sweep.witnesses],  # noqa: SLF001
        "follow_ups": follow,
    }


def plan() -> int:
    """Print the commits read, each file's scope, modules and mutant count; run nothing."""
    sys.stdout.write(f"commits ({len(commits())}): {', '.join(c[:9] for c in commits())}\n")
    for relative, found in changed_functions().items():
        if found["gone"]:
            sys.stdout.write(f"  {relative} lost since: {', '.join(found['gone'])}\n")
    total = 0
    for relative in selection():
        found, mutations = planned(relative)
        total += len(mutations)
        sys.stdout.write(f"\n{relative}: {len(mutations)} mutants\n")
        sys.stdout.write(f"  cited ({len(found['cited'])}): {', '.join(found['cited'])}\n")
        sys.stdout.write(f"  helpers ({len(found['helpers'])}): {', '.join(found['helpers'])}\n")
        sys.stdout.write(f"  modules: {', '.join(MODULES[relative])}\n")
    sys.stdout.write(f"\ntotal mutants: {total}\n")
    return 0


def main(out: Path, only: list[str]) -> int:
    """Sweep every file, or only those named, and write the record to *out*.

    With files named, an existing record at *out* keeps its other files' sweeps and the
    named files' entries are replaced.

    Returns:
        Zero once the record is written.

    """
    files = only or list(selection())
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        fresh = {entry["source"]: entry for entry in pool.map(_run_file, files)}
    kept = json.loads(out.read_text(encoding="utf-8"))["sweeps"] if only and out.exists() else []
    by_source = {entry["source"]: entry for entry in kept} | fresh
    sweeps = [by_source[relative] for relative in selection() if relative in by_source]
    record = {
        "rulings": [195, 196, 197],
        "workers": WORKERS,
        "commits": list(commits()),
        "changed": changed_functions(),
        "sweeps": sweeps,
    }
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--plan"]:
        raise SystemExit(plan())
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))
