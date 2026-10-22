"""Requirements catalog scope, structure checks (drydock RO-3 tranche 1).

`docs/governance/harbor-ro3-requirements-store.md` § The witness names one scope,
`gz validate --catalog`. Tranche 1 lands its structure checks:

* each file against its committed schema, so a malformed entry fails;
* codes and ids unique within their file, a retired code included, since a
  retired code is kept precisely so it is never reused;
* an outcome's family letter present in the legend.

Once the structure holds, tranche 3's edge checks, coverage report and BDD
alignment run from `gzkit.governance.trust_audits.catalog_edges`, over the PRD,
the manifest's gates, the ledger, the features and the tests this module reads.
The forward rule is tranche 4's; the freeze lock is RO-5's.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.advisory import emit_advisory
from gzkit.config import GzkitConfig
from gzkit.core.id_resolver import IdResolutionError, load_identity_context, resolve
from gzkit.core.models import IdKind
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.catalog_edges import (
    bdd_findings,
    coverage_gaps,
    edge_findings,
    prd_needs,
)
from gzkit.ledger import Ledger
from gzkit.models.catalog import CATALOG_FILES, Catalog, load_catalog
from gzkit.registries import RegistryError, load_registry
from gzkit.schemas import load_schema
from gzkit.traceability import scan_catalog_bindings

_TYPE = "catalog"
_RECOVER = (
    "The catalog's shape is ruled in docs/governance/harbor-ro3-requirements-store.md "
    "(The store), and its families in docs/governance/ieee/requirements-model.md "
    "(decision 8.3). Correct the file, then re-run `uv run gz validate --catalog`."
)


def _err(kind: str, message: str) -> ValidationError:
    return ValidationError(
        type=_TYPE,
        artifact=f"data/{CATALOG_FILES[kind]}",
        message=f"{message} {_RECOVER}",
        field=kind,
    )


def _schema_findings(project_root: Path) -> list[ValidationError]:
    """Read each file through the seam and validate it against its committed schema."""
    errors: list[ValidationError] = []
    for kind, name in CATALOG_FILES.items():
        try:
            payload = load_registry(project_root, name)
        except RegistryError as exc:
            errors.append(_err(kind, str(exc)))
            continue
        validator = Draft202012Validator(load_schema(f"catalog_{kind}"))
        problems = sorted(
            f"{'/'.join(str(p) for p in problem.absolute_path) or '(root)'}: {problem.message}"
            for problem in validator.iter_errors(payload)
        )
        if problems:
            errors.append(
                _err(kind, f"data/{name} does not match its schema: {'; '.join(problems)}.")
            )
    return errors


def _duplicates(kind: str, label: str, values: list[str]) -> list[ValidationError]:
    repeated = sorted(value for value, count in Counter(values).items() if count > 1)
    if not repeated:
        return []
    return [
        _err(
            kind,
            f"{label} {', '.join(repeated)} appear more than once in data/{CATALOG_FILES[kind]}. "
            f"A code is never reused, a retired one included.",
        )
    ]


def _structure_findings(catalog: Catalog) -> list[ValidationError]:
    errors = _duplicates("families", "Family codes", [f.code for f in catalog.families])
    errors += _duplicates("outcomes", "Outcome codes", [o.code for o in catalog.outcomes])
    errors += _duplicates("reqs", "REQ ids", [r.id for r in catalog.reqs])
    legend = {family.code for family in catalog.families}
    strays = sorted(o.code for o in catalog.outcomes if o.code[0] not in legend)
    if strays:
        errors.append(
            _err(
                "outcomes",
                f"Outcomes {', '.join(strays)} name a family the legend in "
                f"data/{CATALOG_FILES['families']} does not hold.",
            )
        )
    return errors


def _needs(project_root: Path, config: GzkitConfig) -> tuple[str, ...]:
    """Read the live needs from every PRD under the configured PRD directory."""
    prd_dir = project_root / config.paths.prd
    paths = sorted(prd_dir.glob("PRD-*.md")) if prd_dir.is_dir() else []
    return tuple(need for path in paths for need in prd_needs(path.read_text(encoding="utf-8")))


def _gates(project_root: Path, config: GzkitConfig) -> frozenset[int]:
    """Read the gates the manifest declares across its lanes."""
    manifest = project_root / config.paths.manifest
    if not manifest.is_file():
        return frozenset()
    lanes = json.loads(manifest.read_text(encoding="utf-8")).get("gates", {})
    return frozenset(gate for gates in lanes.values() for gate in gates)


def _governs(project_root: Path, config: GzkitConfig) -> Callable[[str], bool]:
    """Return a check that an id resolves to an ADR through the RO-2 seam, read once."""
    context = None

    def governs(identifier: str) -> bool:
        nonlocal context
        if context is None:
            ledger = Ledger(project_root / config.paths.ledger)
            context = load_identity_context(ledger, project_root, config.paths.design_root)
        try:
            return resolve(identifier, context).kind is IdKind.ADR
        except IdResolutionError:
            return False

    return governs


def audit_catalog(project_root: Path) -> list[ValidationError]:
    """Run the catalog checks; any finding makes the caller exit 3.

    The coverage report is advisory: it is announced and never a finding.
    """
    errors = _schema_findings(project_root)
    if errors:
        return errors
    catalog = load_catalog(project_root)
    errors = _structure_findings(catalog)
    if errors:
        return errors
    config = GzkitConfig.load(project_root / ".gzkit.json")
    needs = _needs(project_root, config)
    errors = edge_findings(
        catalog,
        needs=frozenset(needs),
        gates=_gates(project_root, config),
        governs=_governs(project_root, config),
    )
    if any(outcome.user_facing for outcome in catalog.outcomes):
        errors += bdd_findings(catalog, scan_catalog_bindings(project_root))
    if gaps := coverage_gaps(catalog, needs):
        emit_advisory(
            f"catalog-coverage: {len(gaps)} of {len(needs)} PRD needs have no deriving "
            f"REQ: {', '.join(gaps)}"
        )
    return errors
