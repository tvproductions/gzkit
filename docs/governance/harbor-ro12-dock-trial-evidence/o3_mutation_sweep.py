# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O3's dock trial, its code-path half: every branch O3's rows cite, red then green.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md`, rulings 27 and
150 to 154). Ruling 150 splits O3's trial: the hook arms are flown against a real
dispatched subagent, and the code-path guards are red-proved by mutants, this script.

Scope (ruling 151). Every row of § Mode Contract that waits on O3's trial: the tag-out
log's issue, hang, clearance and clear refusals, a dispatch's end, and the O3 parts of
refusals 2 and 6 (commencement, the frozen-order fence, acceptance and the repair
package's close with a tag hung). :data:`CITED` holds the functions those rows cite,
``gzkit/mx/tag_out.py`` and ``gzkit/commands/wp_tag.py`` whole (ruling 152) and the
module ``gzkit.work_package_fence`` whole as its row cites it, with ruling 96's direct
helpers of the same module.

Mutants (ruling 152). O2's mechanical AST rule (rulings 94 and 99), imported from
``o2_mutation_sweep`` so the rule cannot drift between the two trials: each ``if`` and
``while`` test, comprehension filter and conditional expression forced true and false,
each boolean return forced true and false, each ``raise`` and early ``return`` made
``pass``, each ``except`` body made ``raise``.

The run (ruling 152). No broad pass: each file's mutants run only against the self-test
modules of the rows that cite it (:data:`MODULES`), nominating every test those modules
execute. An inconclusive row is re-run against each test that failed, one at a time,
until one kills it alone (ruling 91's form). A survivor is recorded for reading: closed
later by a test red-proved alone against it, or disclosed with the reading behind it.

Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o3_mutation_sweep.py --plan
    uv run python docs/governance/harbor-ro12-dock-trial-evidence/o3_mutation_sweep.py <out.json>
"""

import json
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(HERE)]

import o2_mutation_sweep as rule  # noqa: E402

from gzkit.mutation_witness import Mutation, run_mutation_sweep  # noqa: E402

_TAG = ("tests.test_tag_out", "tests.commands.test_wp_tag")
_LIFECYCLE = (
    "tests.test_order_ledger",
    "tests.governance.test_catalog_orders",
    "tests.commands.test_wp_order",
    "tests.test_work_package_ledger",
)
_ACCEPTANCE = ("tests.commands.test_wp_order_acceptance", "tests.test_order_ledger")
_GATE5 = (
    "tests.test_order_ledger",
    "tests.test_order_ledger_schema",
    "tests.commands.test_wp_order_acceptance",
    "tests.governance.test_catalog_repair_reqs",
    "tests.test_work_package_ledger",
)
# The run row's self-test column names the first two; the fence's own CLI tests and the
# tag readers' tests exercise the cited code too, and the record says so.
_RUN = ("tests.test_order_run", "tests.commands.test_wp_order_run", "tests.commands.test_wp_fence")
_END = ("tests.test_dispatch_stamp_hook", "tests.test_hooks")

#: Ruling 151's rows: the functions each file's rows cite; ``None`` takes the whole file.
CITED: dict[str, tuple[str, ...] | None] = {
    # Issue, hang, clearance and clear rows; ruling 152 takes both files whole.
    "src/gzkit/mx/tag_out.py": None,
    "src/gzkit/commands/wp_tag.py": None,
    # The hang row: gz's entry keeps the stamped id only beside a stamped root.
    "src/gzkit/cli/main.py": ("main",),
    # Refusal 2 in the lifecycle row, refusal 6 in the acceptance row.
    "src/gzkit/mx/tag_rows.py": ("order_tags",),
    "src/gzkit/order_ledger.py": ("_check_commenced", "hung_tag_refusal", "_check_accepted"),
    "src/gzkit/commands/wp_order.py": ("wp_order_transition_cmd", "wp_order_accept_cmd"),
    # Refusal 6 in the Gate 5 row: a repair package's close with a tag hung.
    "src/gzkit/work_package_ledger.py": ("_check_repair_close",),
    # Refusal 2 in the run row: the frozen-order fence, the module as the row cites it.
    "src/gzkit/work_package_fence.py": None,
    "src/gzkit/pipeline_stage_fence.py": ("frozen_order_write_refusal",),
    # A dispatch's end, and refusal 1's claiming agents in the clear row.
    "src/gzkit/work_package_run.py": ("record_dispatch_end", "dispatch_over", "claiming_agents"),
    "src/gzkit/dispatch_stamp.py": ("end_hook_output",),
}
#: The self-test modules of the rows that cite each file (ruling 152).
MODULES: dict[str, tuple[str, ...]] = {
    "src/gzkit/mx/tag_out.py": _TAG,
    "src/gzkit/commands/wp_tag.py": _TAG,
    "src/gzkit/cli/main.py": _TAG,
    "src/gzkit/mx/tag_rows.py": tuple(
        dict.fromkeys(("tests.test_tag_rows", *_LIFECYCLE, *_ACCEPTANCE))
    ),
    "src/gzkit/order_ledger.py": tuple(dict.fromkeys((*_LIFECYCLE, *_ACCEPTANCE))),
    "src/gzkit/commands/wp_order.py": (
        "tests.commands.test_wp_order",
        "tests.commands.test_wp_order_acceptance",
    ),
    "src/gzkit/work_package_ledger.py": _GATE5,
    "src/gzkit/work_package_fence.py": _RUN,
    "src/gzkit/pipeline_stage_fence.py": _RUN,
    "src/gzkit/work_package_run.py": (*_END, *_TAG),
    "src/gzkit/dispatch_stamp.py": _END,
}
WORKERS = 4
#: What O2's copy leaves behind that the end row's ``tests.test_hooks`` reads: the Codex
#: hook registry, and the orientation script whose absence makes the settings generator
#: register the session-start advisement hook. O2's sweep ran no hook tests.
EXTRA_COPIED = (".codex", "scripts")


def _copy(root: Path) -> None:
    """Copy O2's tree into *root*, with :data:`EXTRA_COPIED` beside it."""
    rule._copy(root)  # noqa: SLF001
    for name in EXTRA_COPIED:
        shutil.copytree(REPO / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))


def planned(relative: str) -> tuple[dict[str, list[str]], list[Mutation]]:
    """Return *relative*'s scope and its mutants under O2's rule, direct helpers only."""
    found = rule.scope(REPO / relative, CITED[relative], transitive=False)
    return found, rule.mutants(REPO / relative, found["cited"] + found["helpers"])


def _run_file(relative: str) -> dict[str, object]:
    """Sweep one file in its own copy of the tree, re-running each inconclusive row alone."""
    found, mutations = planned(relative)
    modules = MODULES[relative]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _copy(root)
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
    """Print each file's scope, modules and mutant count; run nothing."""
    total = 0
    for relative in CITED:
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
    files = only or list(CITED)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        fresh = {entry["source"]: entry for entry in pool.map(_run_file, files)}
    kept = json.loads(out.read_text(encoding="utf-8"))["sweeps"] if only and out.exists() else []
    by_source = {entry["source"]: entry for entry in kept} | fresh
    sweeps = [by_source[relative] for relative in CITED if relative in by_source]
    record = {"rulings": [150, 151, 152], "workers": WORKERS, "sweeps": sweeps}
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--plan"]:
        raise SystemExit(plan())
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))
