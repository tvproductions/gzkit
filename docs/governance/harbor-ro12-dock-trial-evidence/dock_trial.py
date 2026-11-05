# noqa: INP001 — a dated evidence script run by path, never imported as a package
"""RP-12 O1's dock trial: the cwd-escape guard against a real dispatched subagent.

A dated evidence script (`docs/governance/harbor-ro12-contractor-kit.md` § The
cwd-escape guard, ruling 27): it builds a throwaway coordinator project P the way
an adopter installs gzkit, with this checkout as an editable dependency so P's
`uv run gz` and its hooks run the code under trial, and a throwaway target T. It
books a dispatch in P for T, then runs headless `claude -p` in P, whose main
session spawns one real subagent carrying the dispatch line. #1296's cases:

1. the subagent runs a ledger-writing verb with its shell left at P's root:
   refused, P's `insight_recorded` count unchanged;
2. the subagent runs the same verb in T, the root its dispatch intends: booked;
3. the main session runs it in P: booked, unaffected.

Three runs: the guard on with a foreground subagent, the guard on with a
background one, and the guard off (the stamp hook removed from P's settings),
the red witness, where case 1's write must land. A logging hook in P records
each Agent and Bash payload, so the Agent tool's return is measured foreground
and background (ruling 40's open limit). Usage:

    uv run python docs/governance/harbor-ro12-dock-trial-evidence/dock_trial.py <scratch-dir>

It writes `<scratch-dir>/trial.json`; the trial's record cites what it printed.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
VERB = "gz insights remember --type discovery --scope dock-trial --summary"
LOGGER = """\
import json, os, sys
payload = json.load(sys.stdin)
with open(os.environ["DOCK_TRIAL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(json.dumps(payload) + "\\n")
"""
CATALOG = {
    "id": "WP-01-dock",
    "kind": "repair",
    "outcome": None,
    "issues": [1296],
    "lane": "lite",
    "aliases": [],
    "modules": ["data/catalog/"],
    "initial_conditions": "NA",
    "procedure": "NA",
    "test_and_inspection": "NA",
    "system_restoration": "NA",
    "oqe": [],
    "alterations": [],
    "departures": [],
}


def _run(argv: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=900,
    )
    return f"exit {result.returncode}\n{result.stdout}{result.stderr}"


def _gz(project: Path, *args: str) -> str:
    return _run(["uv", "run", "--project", str(project), "gz", *args], project)


def _setup(base: Path) -> tuple[Path, Path]:
    shutil.rmtree(base, ignore_errors=True)
    project, target = base / "P", base / "T"
    project.mkdir(parents=True)
    target.mkdir()
    checkout_gz = str(REPO / ".venv" / "bin" / "gz")
    for root, extra in ((project, []), (target, ["--no-skeleton"])):
        _run(["git", "init", "-q"], root)
        _run([checkout_gz, "init", "--yes", *extra], root)
    _run(["uv", "add", "--dev", "--editable", str(REPO)], project)
    catalog = project / "data" / "catalog"
    held = json.loads((catalog / "work_packages.json").read_text(encoding="utf-8"))
    held["work_packages"] = [CATALOG]
    (catalog / "work_packages.json").write_text(json.dumps(held, indent=2), encoding="utf-8")
    _gz(project, "wp", "initiate", "WP-01-dock", "--operator-text", "dock trial")
    _gz(
        project,
        "wp",
        "freeze",
        "WP-01-dock",
        "--risk-note",
        "r",
        "--review-receipt",
        "v",
        "--evidence",
        "e",
    )
    _gz(project, "wp", "commence", "WP-01-dock", "--evidence", "e")
    hook = project / ".claude" / "hooks" / "dock-trial-log.py"
    hook.write_text(LOGGER, encoding="utf-8")
    logged = f'uv run python "{hook}"'
    local = {
        "permissions": {"allow": ["Bash", "Agent"]},
        "hooks": {
            "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": logged}]}],
            "PostToolUse": [
                {"matcher": "Agent", "hooks": [{"type": "command", "command": logged}]}
            ],
        },
    }
    (project / ".claude" / "settings.local.json").write_text(
        json.dumps(local, indent=2), encoding="utf-8"
    )
    return project, target


def _rows(root: Path, event: str) -> list[dict]:
    text = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row.get("event") == event]


def _summaries(root: Path) -> list[str]:
    """Read which case each booked insight came from: the ledger row holds its hash only.

    Returns:
        The summary of each dock-trial insight, oldest first.

    """
    path = root / ".gzkit" / "insights" / "agent-insights.jsonl"
    if not path.exists():
        return []
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    return [str(row.get("summary")) for row in rows if row.get("scope") == "dock-trial"]


def _dispatch(project: Path, target: str) -> str:
    out = _gz(
        project,
        "wp",
        "dispatch",
        "WP-01-dock",
        "--role",
        "Implementer",
        "--model",
        "sonnet",
        "--issue",
        "1296",
        "--root",
        target,
        "--json",
    )
    event, _end = json.JSONDecoder().raw_decode(out.split("\n", 1)[1])
    return event["dispatch_id"]


def _guard(project: Path, *, on: bool) -> None:
    """Remove the stamp hook from P's settings for the red run, or restore it."""
    settings = project / ".claude" / "settings.json"
    kept = project / ".claude" / "settings.json.trial"
    if on:
        if kept.exists():
            kept.replace(settings)
        return
    shutil.copy(settings, kept)
    data = json.loads(settings.read_text(encoding="utf-8"))
    for phase in data["hooks"].values():
        for entry in phase:
            entry["hooks"] = [h for h in entry["hooks"] if "dispatch-stamp" not in h["command"]]
        phase[:] = [entry for entry in phase if entry["hooks"]]
    settings.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _prompt(dispatch_id: str, project: Path, target: Path, *, background: bool) -> str:
    sub = (
        f"GZKIT-DISPATCH: {dispatch_id}\n\n"
        "You are a dispatched agent in a dock trial. Run these two Bash commands, one at a time, "
        "exactly as written, and report each one's full output:\n"
        f"1. uv run {VERB} subagent-case-1; echo EXIT=$?\n"
        f"2. cd {target} && uv run --project {project} {VERB} subagent-case-2; echo EXIT=$?\n"
        "Do nothing else."
    )
    how = (
        "with run_in_background set to true, then wait for its completion notification "
        "before you go on"
        if background
        else "in the foreground"
    )
    return (
        "This is a dock trial; do exactly these steps and nothing else.\n"
        f"1. Use the Agent tool once, subagent_type general-purpose, {how}, "
        "with exactly this prompt "
        f"between the markers:\n<<<\n{sub}\n>>>\n"
        f"2. Then run this Bash command yourself: uv run {VERB} main-session-case-3; echo EXIT=$?\n"
        "3. Reply with the subagent's report and your command's output, verbatim."
    )


def _trial(project: Path, target: Path, label: str, *, background: bool, guard: bool) -> dict:
    dispatch_id = _dispatch(project, target.resolve().as_posix())
    log = project.parent / f"{label}.payloads.jsonl"
    _guard(project, on=guard)
    before = {
        "P": len(_rows(project, "insight_recorded")),
        "T": len(_rows(target, "insight_recorded")),
    }
    env = {**os.environ, "DOCK_TRIAL_LOG": str(log)}
    for name in ("GZKIT_DISPATCH_ROOT", "GZKIT_DISPATCH_ID"):
        env.pop(name, None)
    output = _run(
        [
            "claude",
            "-p",
            _prompt(dispatch_id, project, target, background=background),
            "--model",
            "sonnet",
        ],
        project,
        env=env,
    )
    _guard(project, on=True)
    after_p, after_t = _rows(project, "insight_recorded"), _rows(target, "insight_recorded")
    payloads = (
        [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        if log.exists()
        else []
    )
    agent_returns = [
        {key: p.get(key) for key in ("hook_event_name", "tool_name")}
        | {
            "tool_response_keys": sorted((p.get("tool_response") or {}).keys()),
            "agentId": (p.get("tool_response") or {}).get("agentId"),
        }
        for p in payloads
        if p.get("tool_name") == "Agent"
    ]
    return {
        "label": label,
        "guard": guard,
        "background": background,
        "dispatch_id": dispatch_id,
        "insights_before": before,
        "insights_after": {"P": len(after_p), "T": len(after_t)},
        "summaries_in_P": _summaries(project),
        "summaries_in_T": _summaries(target),
        "claims": [
            {k: row.get(k) for k in ("dispatch_id", "agent_id", "source")}
            for row in _rows(project, "dispatch_claimed")
            if row.get("dispatch_id") == dispatch_id
        ],
        "subagent_bash_calls": [
            {"agent_id": p.get("agent_id"), "command": (p.get("tool_input") or {}).get("command")}
            for p in payloads
            if p.get("tool_name") == "Bash" and p.get("agent_id")
        ],
        "agent_returns": agent_returns,
        "claude_output": output,
    }


def main() -> None:
    """Build the projects, fly the three runs and write the record."""
    base = Path(sys.argv[1]).resolve()
    project, target = _setup(base)
    runs = [
        _trial(project, target, "guard-on-foreground", background=False, guard=True),
        _trial(project, target, "guard-on-background", background=True, guard=True),
        _trial(project, target, "guard-off", background=False, guard=False),
    ]
    (base / "trial.json").write_text(json.dumps(runs, indent=2), encoding="utf-8")
    for run in runs:
        sys.stdout.write(
            f"{run['label']} before {run['insights_before']} after {run['insights_after']}\n"
            f"  P: {run['summaries_in_P']} T: {run['summaries_in_T']} claims: {run['claims']}\n"
        )


if __name__ == "__main__":
    main()
