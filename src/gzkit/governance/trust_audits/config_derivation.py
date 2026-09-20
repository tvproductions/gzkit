"""Fence the two axes `--config-registry` declares exhaustive but does not reach.

`data/config_registry.json` guarantees that no top-level data registry enters the
tree **unowned**, and it keeps that guarantee. Its `_doc` scopes the claim to
`data/*.json`, so two things still enter freely: a registry carrying no record of
where its values came from, and a policy threshold hardcoded in a module body.
GHI #1066; census at `docs/governance/config-derivation-census-2026-09-20.md`.

Both arms are SHRINK-ONLY ratchets, the idiom `data/waiver_ratchet_registry.json`
already governs. Neither repairs the population it freezes: the 19 unsourced
registries and the 56 module constants stay exactly as they are, and only their
growth is refused. Freezing is the whole claim -- reading it as a quality
statement about the frozen rows would be the laundering the ratchet exists to
prevent.
"""

import ast
import json
import re
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.registries import RegistryError, load_registry

#: Keys a registry may use to carry provenance. `$schema` is excluded on purpose:
#: it declares shape, never origin.
PROVENANCE_KEYS = ("$comment", "_comment", "_doc", "doc", "citation", "note", "_note", "rationale")

#: Provenance counts only when it points somewhere a reader can GO. Prose that
#: explains what a field means is documentation; this fence is about derivation.
AUTHORITY_RE = re.compile(r"(docs/[\w/.-]+\.md|ADR-[\w.]+|GHI #\d+|operator ruling)", re.I)

#: Names marking a module-level constant as a policy knob. Deliberately broad --
#: the roster's job is to make GROWTH visible, and a reader judges each row.
THRESHOLD_NAME_RE = re.compile(
    r"(MAX|MIN|THRESHOLD|LIMIT|CEILING|FLOOR|BUDGET|CAP|DAYS|COUNT|SIZE|LEN|PCT"
    r"|PERCENT|RATIO|TIMEOUT|DEPTH)",
    re.I,
)

_DERIVATION_BASELINE = "config_derivation_grandfather.json"
_CONSTANT_BASELINE = "module_constant_grandfather.json"
_REACH_BASELINE = "direct_data_reach_grandfather.json"
#: Two modules are excluded from the direct-reach scan. The seam is the one
#: place allowed to name `data/`; this detector matches its own pattern
#: literal, which is a regex definition rather than a config read.
_REACH_SCAN_EXEMPT = (
    "src/gzkit/registries.py",
    "src/gzkit/governance/trust_audits/config_derivation.py",
)

#: A module naming a `data/` registry path resolves its own config location.
#: `gzkit.registries.load_registry` is the one place that may (GHI #1067).
_DATA_REACH_RE = re.compile(
    r"""["']data/[\w.-]+\.json["']"""  # "data/x.json"
    r"""|["']data["']\s*[/)]"""  # "data" / ...  or  Path("data")
    r"""|/\s*["']data["']"""  # root / "data"
)
_RECOVER = "uv run gz validate --config-registry"


def _err(artifact: str, message: str) -> ValidationError:
    """Build a config-derivation validation error."""
    return ValidationError(type="config-registry", artifact=artifact, message=message)


def _baseline(project_root: Path, name: str, key: str) -> set[str] | None:
    """Return a shrink-only baseline's entries, or None when it is unreadable.

    Reads through `gzkit.registries.load_registry`, like any other consumer. A
    fence that resolved its own `data/` path while refusing that of every other
    module would be the first thing to drift (GHI #1067).
    """
    try:
        payload = load_registry(project_root, name)
    except RegistryError:
        return None
    entries = payload.get(key) if isinstance(payload, dict) else None
    return set(entries) if isinstance(entries, list) else None


def records_derivation(payload: object, entry: dict[str, object] | None) -> bool:
    """Report whether a registry's authority is recorded in the file or its declaration.

    Either side satisfies it. A bare array cannot carry a provenance field at all,
    so the declaration in `config_registry.json` is the only place its derivation
    can live -- refusing that would make five registries permanently unfixable.
    """
    if isinstance(entry, dict) and AUTHORITY_RE.search(str(entry.get("derivation", ""))):
        return True
    if not isinstance(payload, dict):
        return False
    blob = " ".join(str(payload[key]) for key in payload if key in PROVENANCE_KEYS)
    return bool(AUTHORITY_RE.search(blob))


def policy_constants(project_root: Path) -> list[str]:
    """Return `path::NAME` for every module-level numeric policy constant."""
    found: list[str] = []
    for path in sorted((project_root / "src" / "gzkit").rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        relative = path.relative_to(project_root).as_posix()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names, value = [node.target.id], node.value
            else:
                continue
            if not isinstance(value, ast.Constant) or isinstance(value.value, bool):
                continue
            if not isinstance(value.value, (int, float)):
                continue
            found.extend(
                f"{relative}::{name}"
                for name in names
                if name.isupper() and THRESHOLD_NAME_RE.search(name)
            )
    return found


def audit_derivation(
    project_root: Path, entries: dict[str, dict[str, object]], data_root: Path
) -> list[ValidationError]:
    """Refuse a registry that records no authority and is not grandfathered."""
    baseline = _baseline(project_root, _DERIVATION_BASELINE, "grandfathered")
    if baseline is None:
        return [
            _err(
                f"data/{_DERIVATION_BASELINE}",
                f"The derivation baseline data/{_DERIVATION_BASELINE} is missing or "
                f"unparseable, so every unsourced registry would pass unobserved. Restore it. "
                f"Re-run `{_RECOVER}`.",
            )
        ]
    if not data_root.is_dir():
        return []

    errors: list[ValidationError] = []
    present: set[str] = set()
    for found in sorted(data_root.glob("*.json")):
        present.add(found.name)
        if found.name in baseline:
            continue
        try:
            payload = json.loads(found.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if records_derivation(payload, entries.get(found.name)):
            continue
        errors.append(
            _err(
                found.name,
                f"Config registry data/{found.name} records no authority for its values. "
                f"Execution reads thresholds from JSON, and `AGENTS.md` § Governance doctrine "
                f"surfaces requires citing the authority, not the value -- otherwise no reader "
                f"can tell a deliberate choice from an inherited accident (GHI #1066). Add a "
                f"provenance field citing a docs/**.md path, an ADR, a GHI or an operator "
                f"ruling; a bare array puts a `derivation` on its config_registry.json entry "
                f"instead. The grandfather list is shrink-only and may not absorb this. "
                f"Re-run `{_RECOVER}`.",
            )
        )

    errors.extend(
        _err(
            stale,
            f"The derivation baseline grandfathers data/{stale}, which no longer exists. "
            f"A baseline naming a phantom inflates its own count and hides a later addition. "
            f"Remove the entry. Re-run `{_RECOVER}`.",
        )
        for stale in sorted(baseline - present)
    )
    return errors


def audit_module_constants(project_root: Path) -> list[ValidationError]:
    """Refuse a module-level policy constant absent from the shrink-only roster."""
    baseline = _baseline(project_root, _CONSTANT_BASELINE, "constants")
    if baseline is None:
        return [
            _err(
                f"data/{_CONSTANT_BASELINE}",
                f"The module-constant roster data/{_CONSTANT_BASELINE} is missing or "
                f"unparseable, so a new hardcoded threshold would enter unobserved. Restore "
                f"it. Re-run `{_RECOVER}`.",
            )
        ]
    found = set(policy_constants(project_root))
    return [
        _err(
            entry,
            f"Module-level policy constant {entry} is not in the shrink-only roster "
            f"data/{_CONSTANT_BASELINE}. data/config_registry.json scopes its "
            f"exhaustiveness to data/*.json, so a threshold in a module body is unreachable "
            f"by the gate meant to catch unowned config (GHI #1066). Put the value in the "
            f"config surface, or rename it out of the policy shape if it is an implementation "
            f"detail. The roster may only shrink. Re-run `{_RECOVER}`.",
        )
        for entry in sorted(found - baseline)
    ]


def audit_direct_data_reach(project_root: Path) -> list[ValidationError]:
    """Refuse a module that resolves a `data/` registry path instead of using the seam.

    A single read seam is only single while nothing routes around it -- principle
    3 of the shape campaign Movement F adopts, *"No Parallel Systems: one loader,
    one source of truth"*. The roster is shrink-only, so the thirty readers that
    predate the seam migrate incrementally while a thirty-first is refused.
    """
    baseline = _baseline(project_root, _REACH_BASELINE, "modules")
    if baseline is None:
        return [
            _err(
                f"data/{_REACH_BASELINE}",
                f"The direct-reach roster data/{_REACH_BASELINE} is missing or "
                f"unparseable, so a new parallel config reader would enter unobserved. "
                f"Restore it. Re-run `{_RECOVER}`.",
            )
        ]

    found: set[str] = set()
    source_root = project_root / "src" / "gzkit"
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(project_root).as_posix()
        if relative in _REACH_SCAN_EXEMPT:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _DATA_REACH_RE.search(text):
            found.add(relative)

    errors = [
        _err(
            module,
            f"Module {module} resolves a data/ registry path itself instead of calling "
            f"gzkit.registries.load_registry. A single read seam is single only while "
            f"nothing routes around it (GHI #1067), and hexagonal rule 4 requires taking "
            f"the location as a parameter rather than naming it. Call the seam. The "
            f"roster may only shrink. Re-run `{_RECOVER}`.",
        )
        for module in sorted(found - baseline)
    ]
    errors.extend(
        _err(
            stale,
            f"The direct-reach roster names {stale}, which no longer reaches into data/ "
            f"directly. A stale entry lets a later regression hide under it. Remove the "
            f"entry -- the roster may only shrink, and this is how it shrinks. "
            f"Re-run `{_RECOVER}`.",
        )
        for stale in sorted(baseline - found)
    )
    return errors
