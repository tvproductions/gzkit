#!/usr/bin/env python3
"""Currency and scan-record gates for the ``dependency-currency`` chore (GHI #1369).

The chore's other criteria (lock agreement, Python-version discipline, lint,
typecheck) witness that the toolchain is intact, never that it is current, so a
bare ``gz chores run`` passed on a lagging tree and its PASS block moved the
chore's 1-day band. Operator ruling 2026-11-25, verbatim: *"do both - we need
'full monty' deps check, not 'lite'"*. This script is both gates.

``--scan-record`` asks whether the chore *looked*. The chore declares its scan
record as ``staleness.artifacts`` in ``.gzkit/chores/registry.json``; the record
must have changed within the declared ``periodDays``. The rule is #935's: a run
that did no scan cannot clear the gate, and the record is never ``CHORE-LOG.md``.

``--currency`` asks whether the result *is* current, over every surface the
chore inventories:

* Python dependencies, read from ``uv tree --locked --outdated --depth 1``;
* the build pins ``uv tree`` never reads: ``[tool.uv]
  build-constraint-dependencies`` and the ``[build-system] requires`` floor,
  against PyPI;
* the interpreter in ``.python-version``, against uv's newest download of the
  same minor;
* the uv binary the run used, against astral-sh/uv's latest release; its hold
  is written on ``pyproject.toml``'s ``required-version`` line;
* pre-commit hook revisions in ``.pre-commit-config.yaml``;
* GitHub Actions ``uses:`` pins under ``.github/workflows/``. A major tag
  (``@v6``) compares by major version; a commit-SHA pin compares by the version
  its trailing comment names, and a SHA pin with no version comment cannot be
  compared, so it is a finding.

A pin behind upstream passes only as a declared **hold**: the pinning line, or
the comment block directly above it, says ``held`` (or ``hold``) and names
``GHI #N`` on that line, and the issue is open. A comment that merely cites a GHI
as rationale is not a hold: ``pyproject.toml`` cites dozens. A hold is only for an
upstream release that cannot be installed (yanked, or one uv cannot resolve).
A release that breaks the gate is never held: the code moves to it (operator
rulings 2026-11-19, *"we want to move forward with our depencies"*, and
2026-11-25, *"Only uninstallable (Recommended)"*). That condition is the
holder's to state in the GHI; this gate checks the marker and that the issue is
open.
A hold whose issue has closed is a finding. Both gates read upstream over the
network (``gh`` and ``uv``); an unreachable upstream exits 2, never 0.

Exit codes: 0 current, 1 config error, 2 upstream or tool unavailable, 3 policy
breach.
"""

import argparse
import json
import re
import subprocess
import sys
import tomllib
import urllib.request
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.chores_staleness import git_artifact_changed
from gzkit.commands.common import get_project_root
from gzkit.executables import resolve_executable

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

SLUG = "dependency-currency"
UV_REPOSITORY = "astral-sh/uv"
_HOLD = re.compile(r"\b(?:held|hold)\b[^\n]*?GHI #(\d+)", re.IGNORECASE)
_SHA = re.compile(r"^[0-9a-f]{40}$")
_UV_TREE_OUTDATED = re.compile(
    r"(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])? v(?P<current>\S+)"
    r"(?: \([^)]*\))*? \(latest: v(?P<latest>[^)]+)\)"
)
_HOOK_REPO = re.compile(r"^\s*-\s*repo:\s*(?P<url>\S+)")
_HOOK_REV = re.compile(
    r"^\s*rev:\s*['\"]?(?P<rev>[^'\"\s#]+)['\"]?(?:\s*#\s*frozen:\s*(?P<frozen>\S+))?"
)
_GITHUB_URL = re.compile(r"^https://github\.com/(?P<repo>[\w.-]+/[\w.-]+?)(?:\.git)?/?$")
_ACTION_USES = re.compile(
    r"^\s*(?:-\s+)?uses:\s*['\"]?(?P<repo>[\w.-]+/[\w.-]+)(?:/[^@\s'\"]*)?@(?P<ref>[^\s'\"#]+)['\"]?"
    r"(?:\s*#\s*(?P<comment>\S+))?"
)

_REQUIREMENT = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*"
    r"(?:==|>=)\s*(?P<version>[^,;\s]+)"
)
_REQUIRED_VERSION = re.compile(r"^\s*required-version\s*=")
_PRERELEASE = re.compile(r"[a-zA-Z]")
PYPI_URL = "https://pypi.org/pypi/{name}/json"

Surface = Literal["python", "build", "python-version", "uv", "hook", "action"]


class UpstreamUnavailableError(RuntimeError):
    """An upstream version could not be read, so currency cannot be judged."""


class Pin(BaseModel):
    """One pinned dependency on one surface, as the tree declares it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: Surface = Field(..., description="Which inventoried surface pins it")
    name: str = Field(..., description="Package, repository or tool name")
    current: str | None = Field(..., description="Pinned version; None when unreadable")
    location: str = Field(..., description="path:line of the pin")
    latest: str | None = Field(None, description="Upstream latest, when already known")
    hold_ghi: int | None = Field(None, description="GHI a declared hold names")


class Finding(BaseModel):
    """A pin the gate refuses, with the reason it is refused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pin: Pin = Field(..., description="The refused pin")
    latest: str | None = Field(..., description="Upstream latest at check time")
    reason: str = Field(..., description="Why the pin is refused")


def version_key(version: str) -> tuple[int, ...]:
    """Return *version*'s numeric components, ignoring a leading ``v``."""
    return tuple(int(part) for part in re.findall(r"\d+", version.lstrip("vV")))


def is_behind(current: str, latest: str) -> bool:
    """Return True when *current* is older than *latest*.

    A bare major tag (``v6``) is a moving pointer to that major's newest
    release, so it is behind only when upstream's major has moved on.

    Returns:
        True when upstream holds a newer release than the pin names.

    """
    current_key, latest_key = version_key(current), version_key(latest)
    if len(current_key) == 1:
        return current_key[0] < latest_key[0]
    return current_key < latest_key


def hold_ghi(lines: list[str], index: int) -> int | None:
    """Return the GHI a hold names on line *index* or its comment block above."""
    match = _HOLD.search(lines[index])
    if match:
        return int(match.group(1))
    above = index - 1
    while above >= 0 and lines[above].strip().startswith("#"):
        match = _HOLD.search(lines[above])
        if match:
            return int(match.group(1))
        above -= 1
    return None


def _normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def python_pins(uv_tree_text: str, pyproject_text: str) -> list[Pin]:
    """Return each outdated Python dependency ``uv tree --outdated`` reports."""
    lines = pyproject_text.splitlines()
    pins: list[Pin] = []
    for match in _UV_TREE_OUTDATED.finditer(uv_tree_text):
        name = match.group("name")
        index = _declaring_line(lines, name)
        pins.append(
            Pin(
                surface="python",
                name=name,
                current=match.group("current"),
                latest=match.group("latest"),
                location=f"pyproject.toml:{index + 1}" if index is not None else "uv.lock",
                hold_ghi=hold_ghi(lines, index) if index is not None else None,
            )
        )
    return pins


def _declaring_line(lines: list[str], name: str) -> int | None:
    pattern = re.compile(r"[\"']([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*[=<>!~]")
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if match and _normalized(match.group(1)) == _normalized(name):
            return index
    return None


def hook_pins(config_text: str, path: str = ".pre-commit-config.yaml") -> list[Pin]:
    """Return each GitHub-hosted pre-commit hook revision the config pins."""
    lines = config_text.splitlines()
    pins: list[Pin] = []
    repo: str | None = None
    for index, line in enumerate(lines):
        # Both patterns anchor at the line start, so a commented `# - repo:` or
        # `#   rev:` line never matches.
        repo_match = _HOOK_REPO.match(line)
        if repo_match:
            github = _GITHUB_URL.match(repo_match.group("url"))
            repo = github.group("repo") if github else None
            continue
        rev_match = _HOOK_REV.match(line)
        if rev_match and repo is not None:
            rev = rev_match.group("rev")
            pins.append(
                Pin(
                    surface="hook",
                    name=repo,
                    current=rev_match.group("frozen") if _SHA.match(rev) else rev,
                    location=f"{path}:{index + 1}",
                    hold_ghi=hold_ghi(lines, index),
                )
            )
            repo = None
    return pins


def action_pins(workflow_text: str, path: str) -> list[Pin]:
    """Return each GitHub Actions ``uses:`` pin in one workflow file."""
    lines = workflow_text.splitlines()
    pins: list[Pin] = []
    for index, line in enumerate(lines):
        # Anchored to the YAML key, so a commented line or a `uses:` inside a
        # `run:` string is not a pin.
        match = _ACTION_USES.match(line)
        if not match:
            continue
        ref, comment = match.group("ref"), match.group("comment")
        current: str | None = ref
        if _SHA.match(ref):
            current = comment if comment is not None and version_key(comment) else None
        pins.append(
            Pin(
                surface="action",
                name=match.group("repo"),
                current=current,
                location=f"{path}:{index + 1}",
                hold_ghi=hold_ghi(lines, index),
            )
        )
    return pins


def build_pins(pyproject_text: str) -> list[Pin]:
    """Return the build pins ``uv tree`` never reads.

    Read by table through ``tomllib``, so a multi-line array is read and a
    ``requires`` key in another table is not. A requirement with no ``==`` or
    ``>=`` version names nothing to compare and is skipped.

    Returns:
        One pin per ``[build-system] requires`` floor and ``[tool.uv]
        build-constraint-dependencies`` pin that names a version.

    """
    data = tomllib.loads(pyproject_text)
    tool_uv = data.get("tool", {}).get("uv", {})
    declared = [
        *data.get("build-system", {}).get("requires", []),
        *tool_uv.get("build-constraint-dependencies", []),
    ]
    lines = pyproject_text.splitlines()
    pins: list[Pin] = []
    for requirement in map(str, declared):
        match = _REQUIREMENT.match(requirement)
        if match is None:
            continue
        index = next((i for i, line in enumerate(lines) if requirement in line), None)
        pins.append(
            Pin(
                surface="build",
                name=match.group("name"),
                current=match.group("version"),
                location=f"pyproject.toml:{index + 1}" if index is not None else "pyproject.toml",
                hold_ghi=hold_ghi(lines, index) if index is not None else None,
            )
        )
    return pins


def python_version_pin(pinned_text: str, downloads_json: str) -> Pin:
    """Return ``.python-version``'s pin, with the newest stable download of its minor."""
    lines = pinned_text.splitlines()
    index = next(
        (i for i, line in enumerate(lines) if line.strip() and not line.startswith("#")), None
    )
    if index is None:
        return Pin(
            surface="python-version",
            name="cpython",
            current=None,
            latest="none",
            location=".python-version",
        )
    current = lines[index].strip()
    minor = version_key(current)[:2]
    stable = [
        str(entry.get("version", ""))
        for entry in json.loads(downloads_json)
        if entry.get("implementation") == "cpython"
        and entry.get("variant", "default") == "default"
        and not _PRERELEASE.search(str(entry.get("version", "")))
        and version_key(str(entry.get("version", "")))[:2] == minor
    ]
    newest = max(stable, key=version_key, default=current)
    return Pin(
        surface="python-version",
        name="cpython",
        current=current,
        latest=newest,
        location=f".python-version:{index + 1}",
        hold_ghi=hold_ghi(lines, index),
    )


def uv_binary_pin(pyproject_text: str, version: str) -> Pin:
    """Return the running uv binary's pin; its hold sits on ``required-version``."""
    lines = pyproject_text.splitlines()
    index = next((i for i, line in enumerate(lines) if _REQUIRED_VERSION.match(line)), None)
    return Pin(
        surface="uv",
        name="uv",
        current=version,
        location="uv self version",
        hold_ghi=hold_ghi(lines, index) if index is not None else None,
    )


def _refusal(pin: Pin, latest: str, issue_is_open: Callable[[int], bool]) -> str | None:
    if pin.current is None or not version_key(pin.current):
        return "pin names no version"
    if not version_key(latest):
        return f"upstream latest {latest!r} names no version"
    if not is_behind(pin.current, latest):
        return None
    if pin.hold_ghi is None:
        return "behind upstream, no hold"
    if not issue_is_open(pin.hold_ghi):
        return f"held by GHI #{pin.hold_ghi}, which is closed"
    return None


def judge(
    pins: Iterable[Pin],
    latest_release: Callable[[Pin], str],
    issue_is_open: Callable[[int], bool],
) -> list[Finding]:
    """Return a finding for each pin that is behind upstream and not held open."""
    findings: list[Finding] = []
    for pin in pins:
        latest = pin.latest or latest_release(pin)
        reason = _refusal(pin, latest, issue_is_open)
        if reason is not None:
            findings.append(Finding(pin=pin, latest=latest, reason=reason))
    return findings


def scan_breach(newest: datetime | None, now: datetime, period_days: int) -> str | None:
    """Return why the scan record fails its period, or None when it is fresh."""
    if newest is None:
        return "no scan record is on file"
    age = (now - newest).days
    if age > period_days:
        return f"the scan record last changed {newest.date().isoformat()}, {age}d ago"
    return None


def _say(text: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    stream.write(f"{text}\n")


def _run(argv: list[str], root: Path) -> str:
    try:
        completed = subprocess.run(  # noqa: S603 — argv this script builds; executable resolved
            [resolve_executable(argv[0]), *argv[1:]],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        msg = f"`{' '.join(argv)}` could not run: {exc}"
        raise UpstreamUnavailableError(msg) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()[-1:] or ["no output"]
        msg = f"`{' '.join(argv)}` exited {completed.returncode}: {detail[0]}"
        raise UpstreamUnavailableError(msg)
    return completed.stdout


def subprocess_runner(root: Path) -> Callable[[list[str]], str]:
    """Return a runner that executes an argv in *root* and returns its stdout."""
    return lambda argv: _run(argv, root)


def pypi_latest(name: str) -> str:
    """Return *name*'s latest release on PyPI."""
    url = PYPI_URL.format(name=name)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 — fixed https URL
            return str(json.load(response)["info"]["version"])
    except (OSError, ValueError, KeyError) as exc:
        msg = f"PyPI could not answer for {name}: {exc}"
        raise UpstreamUnavailableError(msg) from exc


def github_latest(
    run: Callable[[list[str]], str], pypi: Callable[[str], str] = pypi_latest
) -> Callable[[Pin], str]:
    """Return a reader of each pin's latest release, one query per repository or package."""
    cache: dict[str, str] = {}

    def latest(pin: Pin) -> str:
        if pin.surface == "build":
            key = f"pypi:{pin.name}"
            if key not in cache:
                cache[key] = pypi(pin.name)
            return cache[key]
        repo = UV_REPOSITORY if pin.surface == "uv" else pin.name
        if repo not in cache:
            cache[repo] = run(["gh", "api", f"repos/{repo}/releases/latest", "--jq", ".tag_name"])
            cache[repo] = cache[repo].strip()
        return cache[repo]

    return latest


def issue_is_open(run: Callable[[list[str]], str]) -> Callable[[int], bool]:
    """Return a reader of whether a GHI is open."""

    def is_open(number: int) -> bool:
        argv = ["gh", "issue", "view", str(number), "--json", "state", "--jq", ".state"]
        return run(argv).strip() == "OPEN"

    return is_open


def collect_pins(root: Path, run: Callable[[list[str]], str]) -> list[Pin]:
    """Read every inventoried surface of the tree at *root*."""
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    uv_tree = run(["uv", "tree", "--locked", "--outdated", "--depth", "1"])
    pins = [*python_pins(uv_tree, pyproject), *build_pins(pyproject)]
    pinned = root / ".python-version"
    if pinned.is_file():
        downloads = run(["uv", "python", "list", "--only-downloads", "--output-format", "json"])
        pins.append(python_version_pin(pinned.read_text(encoding="utf-8"), downloads))
    uv_version = run(["uv", "self", "version", "--short"]).strip()
    pins.append(uv_binary_pin(pyproject, uv_version))
    hooks = root / ".pre-commit-config.yaml"
    if hooks.is_file():
        pins.extend(hook_pins(hooks.read_text(encoding="utf-8")))
    workflows = root / ".github" / "workflows"
    for workflow in sorted([*workflows.glob("*.yml"), *workflows.glob("*.yaml")]):
        rel = workflow.relative_to(root).as_posix()
        pins.extend(action_pins(workflow.read_text(encoding="utf-8"), rel))
    return pins


def _declared_staleness(root: Path) -> dict | None:
    registry = root / ".gzkit" / "chores" / "registry.json"
    try:
        chores = json.loads(registry.read_text(encoding="utf-8")).get("chores", [])
    except OSError, json.JSONDecodeError, AttributeError:
        return None
    for chore in chores:
        if isinstance(chore, dict) and chore.get("slug") == SLUG:
            staleness = chore.get("staleness")
            return staleness if isinstance(staleness, dict) else None
    return None


def check_scan_record(
    root: Path,
    now: datetime,
    changed: Callable[[tuple[str, ...]], datetime | None] | None = None,
) -> int:
    """Gate: the chore's declared scan record changed within its period."""
    staleness = _declared_staleness(root) or {}
    period = staleness.get("periodDays")
    artifacts = staleness.get("artifacts")
    if not isinstance(period, int) or not isinstance(artifacts, list) or not artifacts:
        _say(
            f"BLOCKERS:\n- {SLUG} declares no staleness.periodDays and staleness.artifacts in "
            ".gzkit/chores/registry.json, so there is no scan record to date.",
            err=True,
        )
        return 1
    reader = changed if changed is not None else git_artifact_changed(root, now)
    newest = reader(tuple(str(a) for a in artifacts))
    breach = scan_breach(newest, now, period)
    if breach is None:
        _say(f"scan record fresh: {', '.join(artifacts)} (period {period}d)")
        return 0
    _say(
        f"POLICY BREACH:\n  {SLUG}: {breach}, past its {period}d period.\n"
        "    Why: the other criteria pass on a tree nobody looked at; only the scan record "
        "shows the procedure ran (GHI #935, #1369).\n"
        f"    Fix: perform the chore's Workflow, writing {', '.join(artifacts)}, then run "
        f"`uv run gz chores run {SLUG}`.",
        err=True,
    )
    return 3


def check_currency(
    root: Path,
    run: Callable[[list[str]], str] | None = None,
    pypi: Callable[[str], str] = pypi_latest,
) -> int:
    """Gate: every inventoried pin is current, or held by an open GHI."""
    runner = run if run is not None else subprocess_runner(root)
    try:
        findings = judge(
            collect_pins(root, runner), github_latest(runner, pypi), issue_is_open(runner)
        )
    except UpstreamUnavailableError as exc:
        _say(f"BLOCKERS:\n- currency cannot be judged: {exc}", err=True)
        return 2
    except tomllib.TOMLDecodeError as exc:
        _say(
            f"BLOCKERS:\n- pyproject.toml does not parse ({exc}), so its build pins cannot be "
            "read. Fix the file, then re-run this gate.",
            err=True,
        )
        return 1
    if not findings:
        _say("every inventoried dependency is current or held by an open GHI")
        return 0
    _say(f"POLICY BREACH: {len(findings)} dependency pin(s) are not current:", err=True)
    for finding in findings:
        pin = finding.pin
        _say(
            f"  {pin.location}  {pin.surface} {pin.name} {pin.current or '?'} "
            f"(latest {finding.latest}): {finding.reason}",
            err=True,
        )
    _say(
        "    Why: the chore brings every dependency to upstream latest each run; a pin held "
        "behind says `held: GHI #N` on the pinning line or the comment above it, and the "
        "issue is open.\n"
        "    Fix: apply the gz-deps-upgrade procedure and repair the code to the new "
        "release; hold only a release that cannot be installed, naming its GHI.",
        err=True,
    )
    return 3


def main(argv: list[str] | None = None) -> int:
    """Run the gate named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    gate = parser.add_mutually_exclusive_group(required=True)
    gate.add_argument("--scan-record", action="store_true", help="the scan record is fresh")
    gate.add_argument("--currency", action="store_true", help="every pin is current or held")
    args = parser.parse_args(argv)
    root = get_project_root()
    if args.scan_record:
        return check_scan_record(root, datetime.now(UTC))
    return check_currency(root)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[missing-union-attribute]
    raise SystemExit(main())
