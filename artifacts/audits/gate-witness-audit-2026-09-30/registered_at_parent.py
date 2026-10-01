"""Whether each hollow gate was a registered enforcement claim before its fix.

Criterion (fixed before running): at the fix commit's PARENT, does any registered
enforcement claim name, in its source_fn or gate_targets, a production function
the fix commit modified? Functions are those in src/gzkit whose line span at the
fix commit overlaps an added/changed line of that commit's diff.

Runs each parent's registry in a detached worktree (never pushed), importing that
commit's own code, so the registry is the one that existed at the time.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
PY = REPO / ".venv" / "bin" / "python"
SCRATCH = Path(sys.argv[1])
CASES = [
    ("#889", "c9e296d8e"),
    ("#996", "eb91f20b6"),
    ("#995", "9cc334ee4"),
    ("#960", "edbab5ae4"),
    ("#959", "ac57c15a8"),
    ("#888", "f289bd483"),
    ("#932", "a2a952959"),
    ("#933", "82f8ab453"),
    ("#851", "1edf9dc1b"),
    ("#1007", "1edf9dc1b"),
    ("#1124", "1a5317c89"),
    ("#803", "d266be9ff"),
]

DUMP = r"""
import json, sys
import gzkit.enforcement as e
recs = None
for name in ("production_enforcement_registry",):
    if hasattr(e, name):
        recs = getattr(e, name)()
if recs is None:
    e._ensure_production_claims_registered()
    recs = e.get_enforcement_registry()
out = []
for r in recs:
    out.append({"claim": r.claim_id, "source_fn": getattr(r, "source_fn", ""),
                "gate_targets": list(getattr(r, "gate_targets", ()) or ())})
print(json.dumps(out))
"""


def git(*args: str, cwd: Path = REPO) -> str:
    """Return stdout of a git command run in ``cwd``."""
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout


def modified_functions(sha: str) -> set[str]:
    """Return 'module:function' for src/gzkit functions the commit's added lines touch."""
    out: set[str] = set()
    diff = git("diff", "-U0", "--no-renames", f"{sha}^", sha, "--", "src/gzkit")
    path, changed = None, {}
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            changed.setdefault(path, set())
        m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if m and path and path.endswith(".py"):
            start, length = int(m.group(1)), int(m.group(2) or 1)
            changed[path].update(range(start, start + max(length, 1)))
    for p, lines in changed.items():
        if not p.endswith(".py") or not lines:
            continue
        try:
            src = git("show", f"{sha}:{p}")
        except subprocess.CalledProcessError:
            continue
        module = p[len("src/") : -3].replace("/", ".")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                span = set(range(node.lineno, (node.end_lineno or node.lineno) + 1))
                if span & lines:
                    out.add(f"{module}:{node.name}")
    return out


def registry_at(parent: str) -> list[dict] | str:
    """Dump the enforcement registry from ``parent``'s own code, or an error string."""
    wt = SCRATCH / f"reg-{parent[:9]}"
    if not wt.exists():
        git("worktree", "add", "--detach", str(wt), parent)
    try:
        res = subprocess.run(
            [str(PY), "-c", DUMP],
            cwd=wt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={"PYTHONPATH": f"{wt / 'src'}", "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
        )
        if res.returncode != 0:
            return "registry import failed: " + res.stderr.strip().splitlines()[-1][:200]
        return json.loads(res.stdout.strip().splitlines()[-1])
    finally:
        git("worktree", "remove", "--force", str(wt))


def names(rec: dict) -> set[str]:
    """Return the ``module:function`` names a registry record points at."""
    got = set(rec["gate_targets"])
    mod, _, fn = rec["source_fn"].rpartition(".")
    if mod:
        got.add(f"{mod}:{fn}")
    return got


rows: list[dict[str, Any]] = []
for ghi, sha in CASES:
    parent = git("rev-parse", "--short=9", f"{sha}^").strip()
    funcs = modified_functions(sha)
    reg = registry_at(parent)
    if isinstance(reg, str):
        rows.append(
            {"ghi": ghi, "fix": sha, "parent": parent, "error": reg, "modified": sorted(funcs)}
        )
        continue
    hits = sorted({r["claim"] for r in reg if names(r) & funcs})
    rows.append(
        {
            "ghi": ghi,
            "fix": sha,
            "parent": parent,
            "claims_at_parent": len(reg),
            "modified": sorted(funcs),
            "registered_claims_naming_a_modified_fn": hits,
        }
    )
(SCRATCH / "registered_at_parent.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
for r in rows:
    print(
        r["ghi"],
        r["fix"],
        "parent",
        r["parent"],
        "| claims:",
        r.get("claims_at_parent"),
        "| hit:",
        r.get("registered_claims_naming_a_modified_fn", r.get("error")),
        "| modified fns:",
        len(r["modified"]),
    )
