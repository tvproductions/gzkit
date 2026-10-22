"""Astral discipline scope: each fact declared once, where Astral's tools read it (RO-9).

`docs/governance/harbor-ro9-astral-toolchain.md` § The witness. The rules, one
per row of the measured population:

- ``version-home-missing`` / ``version-below-floor`` / ``version-restated`` /
  ``version-disagrees``: the Python floor lives in ``requires-python`` and the
  interpreter in ``.python-version`` (``uv python pin``); Ruff and ty infer their
  target from the floor, and CI takes Python from uv. Any other statement of a
  version is a restatement, unless the exception register names it, and then it
  must agree with its home.
- ``lock-unchecked``: automation syncs with ``uv sync --locked``.
- ``pip-in-project``: no ``pip``, ``uv pip`` or ``requirements*.txt`` anywhere in the tree.
- ``setup-python``: uv provides the interpreter.
- ``dev-tool-in-extra``: development tooling lives in ``[dependency-groups]``.
- ``tool-outside-lock``: a locked tool runs through ``uv run``, never ``uvx`` or ``PATH``.
- ``unused-dependency``: a declared development dependency something invokes.
- ``non-astral-unregistered`` / ``exception-without-reason`` / ``exception-stale``:
  every non-Astral tool is a curated exception with a recorded reason. A registered
  ``records`` entry names a module-level table whose strings are data, not an
  invocation (a dated history of argv that ran, a tuple of step names); it is not
  read for argv, and it too needs a reason and a symbol that exists.
- ``build-backend-not-uv`` / ``publish-not-uv``: ``uv_build``, ``uv publish``.

Today's violations seed ``data/astral_discipline_baseline.json``, a shrink-only
ratchet closed at zero. In gzkit's own tree the same rules also run against the
project ``gz init`` scaffolds. A tree with no baseline (an adopter before RO-9
tranche 7 gives it one) has its violations announced, not failed.

Registered as ``gz validate --astral-discipline``; runs in ``gz check`` as the
"Astral discipline" step.
"""

from __future__ import annotations

import ast
import fnmatch
import functools
import importlib.metadata
import json
import re
import tempfile
import tomllib
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.advisory import emit_advisory
from gzkit.core.validation_rules import ValidationError
from gzkit.registries import RegistryError, load_registry

__all__ = [
    "BASELINE_RELPATH",
    "EXCEPTIONS_RELPATH",
    "Violation",
    "audit_astral_discipline",
    "check_discipline_baseline",
    "find_violations",
    "scaffold_violations",
]

BASELINE_NAME = "astral_discipline_baseline.json"
BASELINE_RELPATH = f"data/{BASELINE_NAME}"
EXCEPTIONS_NAME = "astral_exceptions.json"
EXCEPTIONS_RELPATH = f"data/{EXCEPTIONS_NAME}"

_SPEC = "docs/governance/harbor-ro9-astral-toolchain.md"
_RECOVER = "uv run gz validate --astral-discipline"
#: The tools Astral ships, by normalized distribution name.
ASTRAL_TOOLS = frozenset({"ruff", "ty", "uv", "uv-build"})
_SCAFFOLD_PREFIX = "gz init scaffold:"

_VERSION = r"\d+\.\d+(?:\.\d+)?"
_PIN_RE = re.compile(rf"^\s*(?P<v>{_VERSION})\s*$")
_FLOOR_RE = re.compile(rf">=\s*(?P<v>{_VERSION})")
_UV_PYTHON_RE = re.compile(rf"uv python (?:install|pin)\s+(?:--\S+\s+)*(?P<v>{_VERSION})")
_PYTHON_VERSION_KEY_RE = re.compile(rf"""python-version:\s*["']?(?P<v>{_VERSION})""")
_RTD_PYTHON_RE = re.compile(rf"""^\s*python:\s*["']?(?P<v>{_VERSION})""", re.MULTILINE)
_CLASSIFIER_RE = re.compile(rf"Programming Language :: Python :: (?P<v>{_VERSION})$")
_UV_SYNC_RE = re.compile(r"\buv sync\b(?P<flags>[^\n]*)")
_PIP_RE = re.compile(r"\b(?:uv pip|pip install)\b")
_NAME_RE = re.compile(r"\s*(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)")


class Violation(BaseModel):
    """One departure from the discipline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: str = Field(..., description="Rule id, e.g. lock-unchecked")
    file: str = Field(..., description="Repository-relative POSIX path, or a scaffold label")
    subject: str = Field(..., description="What the rule found: a key, a tool, a command")
    detail: str = Field("", description="The offending text, for messages only")


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement_name(spec: str) -> str:
    match = _NAME_RE.match(spec)
    return _norm(match.group("name")) if match else ""


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _workflows(root: Path) -> list[Path]:
    base = root / ".github" / "workflows"
    return sorted([*base.glob("*.yml"), *base.glob("*.yaml")])


def _load_exceptions(root: Path) -> dict[str, Any]:
    try:
        payload = load_registry(root, EXCEPTIONS_NAME)
    except RegistryError:
        return {}
    return payload if isinstance(payload, dict) else {}


class _Project(BaseModel):
    """The facts one tree declares, read once."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pyproject: dict[str, Any]
    floor: str | None
    pin: str | None
    groups: dict[str, list[str]]
    extras: dict[str, list[str]]
    runtime: list[str]
    exceptions: dict[str, Any]

    @property
    def dev_tools(self) -> set[str]:
        return {name for names in self.groups.values() for name in names}


def _project(root: Path) -> _Project:
    text = _read(root / "pyproject.toml")
    pyproject = tomllib.loads(text) if text else {}
    project = pyproject.get("project", {})
    floor_match = _FLOOR_RE.search(str(project.get("requires-python", "")))
    pin_match = _PIN_RE.match(
        _read(root / ".python-version").splitlines()[0] if _read(root / ".python-version") else ""
    )

    def names(specs: Iterable[object]) -> list[str]:
        return [n for spec in specs if isinstance(spec, str) and (n := _requirement_name(spec))]

    return _Project(
        pyproject=pyproject,
        floor=floor_match.group("v") if floor_match else None,
        pin=pin_match.group("v") if pin_match else None,
        groups={g: names(specs) for g, specs in pyproject.get("dependency-groups", {}).items()},
        extras={e: names(specs) for e, specs in project.get("optional-dependencies", {}).items()},
        runtime=names(project.get("dependencies", [])),
        exceptions=_load_exceptions(root),
    )


def _registered_restatements(project: _Project) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(entry.get("file")), str(entry.get("key"))): entry
        for entry in project.exceptions.get("restatements", [])
        if isinstance(entry, dict)
    }


def _version_rules(root: Path, project: _Project) -> Iterator[Violation]:
    if project.floor is None:
        yield Violation(
            rule="version-home-missing", file="pyproject.toml", subject="requires-python"
        )
    if project.pin is None:
        yield Violation(
            rule="version-home-missing", file=".python-version", subject=".python-version"
        )
    if project.floor and project.pin and _version(project.pin) < _version(project.floor):
        yield Violation(rule="version-below-floor", file=".python-version", subject=project.pin)
    tools = project.pyproject.get("tool", {})
    if "target-version" in tools.get("ruff", {}):
        yield Violation(
            rule="version-restated", file="pyproject.toml", subject="tool.ruff.target-version"
        )
    if "python-version" in tools.get("ty", {}).get("environment", {}):
        yield Violation(
            rule="version-restated",
            file="pyproject.toml",
            subject="tool.ty.environment.python-version",
        )
    ty_text = _read(root / "ty.toml")
    if ty_text and "python-version" in tomllib.loads(ty_text).get("environment", {}):
        yield Violation(
            rule="version-restated", file="ty.toml", subject="environment.python-version"
        )
    yield from _registered_version_rules(root, project)
    for path in _workflows(root):
        text = _read(path)
        rel = _rel(root, path)
        for match in _PYTHON_VERSION_KEY_RE.finditer(text):
            yield Violation(
                rule="version-restated", file=rel, subject="python-version", detail=match.group(0)
            )
        for match in _UV_PYTHON_RE.finditer(text):
            yield Violation(
                rule="version-restated", file=rel, subject="uv python", detail=match.group(0)
            )
    for path in sorted((root / ".gzkit" / "skills").glob("**/SKILL.md")):
        for match in _UV_PYTHON_RE.finditer(_read(path)):
            yield Violation(
                rule="version-restated",
                file=_rel(root, path),
                subject="uv python",
                detail=match.group(0),
            )


def _registered_version_rules(root: Path, project: _Project) -> Iterator[Violation]:
    """Classifiers and Read the Docs' interpreter: restatements unless registered, and agreeing."""
    registered = _registered_restatements(project)
    classifiers = [
        m.group("v")
        for c in project.pyproject.get("project", {}).get("classifiers", [])
        if (m := _CLASSIFIER_RE.search(str(c)))
    ]
    key = ("pyproject.toml", "project.classifiers")
    if classifiers and key not in registered:
        yield Violation(rule="version-restated", file=key[0], subject=key[1])
    elif (
        classifiers
        and project.floor
        and min(classifiers, key=_version) != ".".join(project.floor.split(".")[:2])
    ):
        yield Violation(
            rule="version-disagrees", file=key[0], subject=key[1], detail=", ".join(classifiers)
        )
    rtd = _read(root / ".readthedocs.yaml")
    rtd_match = _RTD_PYTHON_RE.search(rtd)
    key = (".readthedocs.yaml", "build.tools.python")
    if rtd_match and key not in registered:
        yield Violation(rule="version-restated", file=key[0], subject=key[1])
    elif rtd_match and project.pin and not project.pin.startswith(rtd_match.group("v")):
        yield Violation(
            rule="version-disagrees", file=key[0], subject=key[1], detail=rtd_match.group(0)
        )


def _yaml_code(text: str) -> str:
    """Drop full-line YAML (and shell) comments: a comment naming a tool documents, never runs it.

    Inline ``#`` stays, because it also opens a pin comment after a SHA and
    appears inside shell strings; only a line that is nothing but a comment
    is dropped (RO-9 tranche 3: the release workflow's note on what replaced
    `twine check` read as a use of twine).
    """
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def _automation_rules(root: Path) -> Iterator[Violation]:
    for path in _workflows(root):
        text = _yaml_code(_read(path))
        rel = _rel(root, path)
        if "actions/setup-python" in text:
            yield Violation(rule="setup-python", file=rel, subject="actions/setup-python")
        for match in _UV_SYNC_RE.finditer(text):
            if "--locked" not in match.group("flags"):
                yield Violation(
                    rule="lock-unchecked", file=rel, subject="uv sync", detail=match.group(0)
                )
        for _ in _PIP_RE.finditer(text):
            yield Violation(rule="pip-in-project", file=rel, subject="pip")
        if "pypa/gh-action-pypi-publish" in text:
            yield Violation(rule="publish-not-uv", file=rel, subject="pypa/gh-action-pypi-publish")
        if re.search(r"\btwine\b", text):
            yield Violation(rule="publish-not-uv", file=rel, subject="twine")
    for name in (".readthedocs.yaml", ".pre-commit-config.yaml"):
        for _ in _PIP_RE.finditer(_yaml_code(_read(root / name))):
            yield Violation(rule="pip-in-project", file=name, subject="pip")
    for path in _requirements_files(root):
        yield Violation(rule="pip-in-project", file=_rel(root, path), subject=path.name)


#: Directories that are an environment, a build output or a cache, never the project's own tree.
_NOT_THE_TREE = frozenset({".git", ".venv", "venv", "site", "node_modules", "__pycache__"})


def _requirements_files(root: Path) -> list[Path]:
    """Every ``requirements*.txt`` at any depth: uv's project model admits none beside the lock."""
    found: list[Path] = []
    for directory, dirnames, filenames in root.walk():
        dirnames[:] = [d for d in dirnames if d not in _NOT_THE_TREE]
        found.extend(directory / n for n in filenames if fnmatch.fnmatch(n, "requirements*.txt"))
    return sorted(found)


def _dependency_rules(root: Path, project: _Project) -> Iterator[Violation]:
    for extra, names in sorted(project.extras.items()):
        overlap = sorted(set(names) & project.dev_tools)
        if extra == "dev" or overlap:
            yield Violation(
                rule="dev-tool-in-extra",
                file="pyproject.toml",
                subject=extra,
                detail=", ".join(overlap),
            )
    backend = str(project.pyproject.get("build-system", {}).get("build-backend", ""))
    if backend and backend != "uv_build":
        yield Violation(rule="build-backend-not-uv", file="pyproject.toml", subject=backend)
    declared = (
        set(project.runtime) | project.dev_tools | {n for ns in project.extras.values() for n in ns}
    )
    tools = {
        _norm(str(entry.get("name", ""))): entry
        for entry in project.exceptions.get("tools", [])
        if isinstance(entry, dict)
    }
    for name in sorted(declared - ASTRAL_TOOLS - set(tools)):
        yield Violation(rule="non-astral-unregistered", file="pyproject.toml", subject=name)
    for name, entry in sorted(tools.items()):
        if not str(entry.get("reason", "")).strip():
            yield Violation(rule="exception-without-reason", file=EXCEPTIONS_RELPATH, subject=name)
        if name not in declared and not entry.get("external"):
            yield Violation(rule="exception-stale", file=EXCEPTIONS_RELPATH, subject=name)
    index = _invocation_index(_invocation_corpus(root))
    for name in sorted(project.dev_tools):
        if not _invoked(name, index):
            yield Violation(rule="unused-dependency", file="pyproject.toml", subject=name)


def _invocation_corpus(root: Path) -> str:
    """Return the text in which a development tool's invocation may appear."""
    paths: list[Path] = [*_workflows(root), root / ".pre-commit-config.yaml", root / "mkdocs.yml"]
    for directory in ("src", "tests", "features", "scripts", ".gzkit/hooks"):
        base = root / directory
        paths.extend(
            p for p in base.rglob("*") if p.suffix in {".py", ".json", ".toml", ""} and p.is_file()
        )
    return "\n".join(_read(p) for p in paths if "__pycache__" not in p.parts)


@functools.cache
def _distribution_modules() -> dict[str, frozenset[str]]:
    """Map each installed distribution's normalized name to its top-level modules."""
    try:
        mapping = importlib.metadata.packages_distributions()
    except OSError, ValueError:
        return {}
    by_dist: dict[str, set[str]] = {}
    for module, dists in mapping.items():
        for dist in dists:
            by_dist.setdefault(_norm(dist), set()).add(module)
    return {dist: frozenset(mods) for dist, mods in by_dist.items()}


_INVOCATION_RES = (
    re.compile(r"\b(?:uv run|uvx|uv tool run)(?:\s+--?\S+)*\s+([A-Za-z0-9_.-]+)"),
    re.compile(r"-m\s+([A-Za-z0-9_.]+)"),
    re.compile(r"^\s*(?:import|from)\s+([A-Za-z0-9_]+)", re.MULTILINE),
    re.compile(r"""[\[(]\s*["']([A-Za-z0-9_.-]+)["']"""),
    re.compile(r"\bname:\s*([A-Za-z0-9_.-]+)"),
)


def _invocation_index(corpus: str) -> frozenset[str]:
    """Every word the corpus runs, imports, quotes or names, read in one pass per form."""
    return frozenset(m.group(1) for pattern in _INVOCATION_RES for m in pattern.finditer(corpus))


#: Directory names some wheels ship at top level by mistake (vulture's lists ``dev``).
#: They name no module a project imports, so they never count as an invocation.
_NOT_MODULES = frozenset(
    {"dev", "doc", "docs", "example", "examples", "scripts", "src", "test", "tests"}
)


def _invoked(name: str, index: frozenset[str]) -> bool:
    candidates = {name, name.replace("-", "_"), *_distribution_modules().get(name, frozenset())}
    return any(c in index for c in candidates - _NOT_MODULES if not c.startswith("_"))


def _records(project: _Project) -> list[dict[str, Any]]:
    return [r for r in project.exceptions.get("records", []) if isinstance(r, dict)]


def _record_nodes(tree: ast.Module, symbols: set[str]) -> dict[str, set[int]]:
    """Map each named module-level assignment to the ids of every node inside it."""
    found: dict[str, set[int]] = {}
    for stmt in tree.body:
        targets = stmt.targets if isinstance(stmt, ast.Assign) else []
        if isinstance(stmt, ast.AnnAssign):
            targets = [stmt.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id in symbols:
                found[target.id] = {id(node) for node in ast.walk(stmt)}
    return found


def _record_rules(root: Path, project: _Project) -> Iterator[Violation]:
    for record in _records(project):
        subject = f"{record.get('file', '')}:{record.get('symbol', '')}"
        if not str(record.get("reason", "")).strip():
            yield Violation(
                rule="exception-without-reason", file=EXCEPTIONS_RELPATH, subject=subject
            )
        text = _read(root / str(record.get("file", "")))
        symbol = str(record.get("symbol", ""))
        if not text or symbol not in _record_nodes(ast.parse(text), {symbol}):
            yield Violation(rule="exception-stale", file=EXCEPTIONS_RELPATH, subject=subject)


def _provenance_rules(root: Path, project: _Project) -> Iterator[Violation]:
    tools = project.dev_tools
    yield from _argv_provenance(root, tools, _records(project))
    for path in sorted((root / "src").glob("**/chores/**/acceptance.json")):
        for command in _strings(json.loads(_read(path) or "null")):
            if subject := _uvx_locked_tool(command.split(), tools):
                yield Violation(rule="tool-outside-lock", file=_rel(root, path), subject=subject)
    for line in _read(root / ".pre-commit-config.yaml").splitlines():
        parts = line.split("entry:", 1)[-1].split() if "entry:" in line else []
        if subject := _uvx_locked_tool(parts, tools):
            yield Violation(
                rule="tool-outside-lock", file=".pre-commit-config.yaml", subject=subject
            )


def _uvx_locked_tool(parts: list[str], tools: set[str]) -> str | None:
    """Return the locked dev tool a ``uvx <tool>`` command fetches from outside the lock."""
    if len(parts) > 1 and parts[0] == "uvx" and _norm(parts[1]) in tools:
        return _norm(parts[1])
    return None


def _argv_provenance(
    root: Path, tools: set[str], records: list[dict[str, Any]]
) -> Iterator[Violation]:
    """Flag argv literals under ``src`` that run a locked dev tool outside ``uv run``.

    A registered record's own table is skipped: it holds argv that ran, kept as history.
    """
    for path in sorted((root / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = _rel(root, path)
        tree = ast.parse(_read(path))
        symbols = {str(r.get("symbol", "")) for r in records if r.get("file") == rel}
        skipped = set().union(*_record_nodes(tree, symbols).values())
        for node in ast.walk(tree):
            if not isinstance(node, ast.List | ast.Tuple) or id(node) in skipped:
                continue
            words = _leading_words(node.elts)
            if subject := _uvx_locked_tool(words, tools):
                yield Violation(rule="tool-outside-lock", file=rel, subject=subject)
            elif len(words) > 1 and _norm(words[0]) in tools and _norm(words[1]) not in tools:
                yield Violation(rule="tool-outside-lock", file=rel, subject=_norm(words[0]))


def _leading_words(elements: list[ast.expr]) -> list[str]:
    """Return the string literals an argv starts with, up to its first computed element."""
    words: list[str] = []
    for element in elements:
        if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
            break
        words.append(element.value)
    return words


def _strings(node: object) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


def find_violations(root: Path) -> list[Violation]:
    """Return every violation in one tree."""
    project = _project(root)
    return [
        *_version_rules(root, project),
        *_automation_rules(root),
        *_dependency_rules(root, project),
        *_provenance_rules(root, project),
        *_record_rules(root, project),
    ]


def scaffold_violations() -> list[Violation]:
    """Return the violations in the project ``gz init`` scaffolds, labelled as such."""
    from gzkit.commands.init_cmd import scaffold_project_skeleton  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        scaffold_project_skeleton(root, "scaffold-probe", "src", "tests")
        found = find_violations(root)
    return [v.model_copy(update={"file": f"{_SCAFFOLD_PREFIX}{v.file}"}) for v in found]


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="astral_discipline", artifact=artifact, message=message)


def check_discipline_baseline(
    violations: Iterable[Violation], rows: list[dict]
) -> list[ValidationError]:
    """Compare today's violations with the baseline, which may only shrink and must stay exact."""
    current = Counter((v.rule, v.file, v.subject) for v in violations)
    seeded: dict[tuple[str, str, str], int] = {}
    errors: list[ValidationError] = []
    for row in rows:
        key = (str(row["rule"]), str(row["file"]), str(row["subject"]))
        if key in seeded:
            errors.append(
                _err(
                    "::".join(key),
                    f"{BASELINE_RELPATH} holds this violation twice. The baseline is keyed by "
                    f"rule, file and subject ({_SPEC} § The witness). Merge the rows and re-run "
                    f"`{_RECOVER}`.",
                )
            )
        seeded[key] = int(row["count"])
    for key, count in sorted(current.items()):
        allowed = seeded.get(key, 0)
        if count > allowed:
            errors.append(
                _err(
                    "::".join(key),
                    f"{count - allowed} new {key[0]} violation(s) that {BASELINE_RELPATH} does "
                    f"not hold. Each fact is declared once, where Astral's tools read it, and the "
                    f"baseline only shrinks ({_SPEC} § The discipline). Remove the restatement or "
                    f"route the tool through uv as the rule names, then re-run `{_RECOVER}`.",
                )
            )
    for key, count in sorted(seeded.items()):
        have = current.get(key, 0)
        if have < count:
            action = "Delete the row" if have == 0 else f"Lower its count to {have}"
            errors.append(
                _err(
                    "::".join(key),
                    f"{BASELINE_RELPATH} holds {count} violation(s) here and the scan finds "
                    f"{have}. The baseline may not carry dead rows ({_SPEC} § The witness). "
                    f"{action}, set "
                    f"baseline_count in data/waiver_ratchet_registry.json to the row count, and "
                    f"re-run `{_RECOVER}`.",
                )
            )
    return errors


def audit_astral_discipline(root: Path) -> list[ValidationError]:
    """Run every rule against the tree, and against the scaffold in gzkit's own tree."""
    violations = find_violations(root)
    if (root / "src" / "gzkit" / "commands" / "init_cmd.py").is_file():
        violations.extend(scaffold_violations())
    try:
        rows = load_registry(root, BASELINE_NAME)["violations"]
    except RegistryError:
        for violation in violations:
            emit_advisory(
                f"astral-discipline [{violation.rule}]: {violation.file}: {violation.subject}. "
                f"No {BASELINE_RELPATH} yet, so this is announced, not failed ({_SPEC})."
            )
        return []
    except (KeyError, TypeError) as exc:
        return [
            _err(
                BASELINE_RELPATH,
                f"{BASELINE_RELPATH} is malformed ({exc}) ({_SPEC} § The witness). Restore it from "
                f"git and re-run `{_RECOVER}`.",
            )
        ]
    return check_discipline_baseline(violations, rows)
