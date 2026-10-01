"""Gate map, layer C: whether each registered control depends on its gate's guards.

For every registered enforcement claim, each guard statement in the gate
functions the claim names (its gate_targets, else its in-tree source_fn) is
replaced with `pass`, one at a time, in a detached worktree. The claim's own
control is then re-run through a generated unittest probe. killed = the control
stopped passing (it depends on that guard); survived = it still passes with the
guard gone. Outcomes come from gzkit.mutation_witness, so invalid/inconclusive
runs are reported, never counted as kills.

Usage: python gatemap.py <worktree> <shard_index> <shard_count> <out.json>
Read-only with respect to the main checkout.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
SHARD, SHARDS = int(sys.argv[2]), int(sys.argv[3])
OUT = Path(sys.argv[4])

# Children (the probe runs) import gzkit from the worktree, not the main checkout.
os.environ["PYTHONPATH"] = f"{WT / 'src'}{os.pathsep}{WT}"
sys.path[:0] = [str(WT / "src"), str(WT)]

from gzkit.commit_witness import statement_mutations  # noqa: E402
from gzkit.enforcement import production_enforcement_registry  # noqa: E402
from gzkit.mutation_witness import Mutation, run_mutation_sweep  # noqa: E402

PROBE = WT / "tests" / "_gatemap_probe.py"


def _method(claim_id: str) -> str:
    return "test_" + re.sub(r"[^0-9a-zA-Z_]", "_", claim_id)


def _write_probe(claim_ids: list[str]) -> None:
    lines = [
        "import contextlib, io, unittest",
        "from gzkit.enforcement import (",
        "    production_enforcement_registry, _run_claim_once, _run_population_claim,",
        ")",
        "",
        "_BY_ID = {r.claim_id: r for r in production_enforcement_registry()}",
        "",
        "",
        "class GateMap(unittest.TestCase):",
    ]
    for cid in claim_ids:
        lines += [
            f"    def {_method(cid)}(self):",
            f"        rec = _BY_ID[{cid!r}]",
            "        out, err = io.StringIO(), io.StringIO()",
            "        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):",
            "            if callable(rec.population):",
            "                res = _run_population_claim(rec, rec.population)",
            "            else:",
            "                res = _run_claim_once(rec)",
            "        self.assertEqual(res.outcome, 'PASS', res.message[:300])",
            "",
        ]
    PROBE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _span(module: str, name: str) -> tuple[Path, int, int] | None:
    path = WT / "src" / Path(*module.split(".")).with_suffix(".py")
    if not path.exists():
        path = WT / "src" / Path(*module.split(".")) / "__init__.py"
        if not path.exists():
            return None
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return path, node.lineno, node.end_lineno or node.lineno
    return None


def _targets(rec) -> list[tuple[Path, int, int, str]]:
    names = list(rec.gate_targets)
    if not names:
        mod, _, fn = rec.source_fn.rpartition(".")
        names = [f"{mod}:{fn}"]
    found = []
    for t in names:
        mod, _, fn = t.partition(":")
        span = _span(mod, fn)
        if span:
            found.append((*span, t))
    return found


def main() -> None:
    """Sweep this shard's claims, writing results after each claim."""
    recs = sorted(production_enforcement_registry(), key=lambda r: r.claim_id)
    only = set(filter(None, os.environ.get("GATEMAP_ONLY", "").split(",")))
    if only:
        mine = [r for r in recs if r.claim_id in only]
    else:
        mine = [r for i, r in enumerate(recs) if i % SHARDS == SHARD]
    _write_probe([r.claim_id for r in mine])
    results = []
    for rec in mine:
        test_id = f"tests._gatemap_probe.GateMap.{_method(rec.claim_id)}"
        command = [sys.executable, "-m", "unittest", "-v", test_id]
        row = {"claim": rec.claim_id, "expect": bool(rec.expect), "targets": [], "error": ""}
        targets = _targets(rec)
        if not targets:
            row["error"] = "no in-tree gate function to mutate (subprocess-delegated or unresolved)"
            results.append(row)
            continue
        for path, first, last, label in targets:
            source = path.read_text(encoding="utf-8")
            rel = path.relative_to(WT).as_posix()
            muts = [
                Mutation(find=m.find, replace=m.replace, label=m.label, expected_tests=[test_id])
                for m in statement_mutations(source, rel, first, last)
            ]
            if not muts:
                row["targets"].append({"target": label, "guards": 0})
                continue
            try:
                sweep = run_mutation_sweep(WT, path, muts, command)
            except Exception as exc:  # noqa: BLE001 - diagnostic driver; record and continue
                row["targets"].append({"target": label, "error": repr(exc)[:300]})
                continue
            counts: dict[str, int] = {}
            survivors = []
            for w in sweep.witnesses:
                counts[w.outcome] = counts.get(w.outcome, 0) + 1
                if w.outcome == "survived":
                    survivors.append(w.label)
            row["targets"].append(
                {
                    "target": label,
                    "baseline_green": sweep.baseline_green,
                    "baseline_tail": (
                        "" if sweep.baseline_green else sweep.baseline_output_tail[-400:]
                    ),
                    "guards": len(muts),
                    "counts": counts,
                    "survivors": survivors,
                }
            )
        results.append(row)
        OUT.write_text(json.dumps(results, indent=1), encoding="utf-8")
    OUT.write_text(json.dumps(results, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
