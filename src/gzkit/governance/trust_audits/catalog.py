"""Requirements catalog scope, structure checks (drydock RO-3 tranche 1).

`docs/governance/harbor-ro3-requirements-store.md` § The witness names one scope,
`gz validate --catalog`. Tranche 1 lands its structure checks:

* each file against its committed schema, so a malformed entry fails;
* codes and ids unique within their file, a retired code included, since a
  retired code is kept precisely so it is never reused;
* an outcome's family letter present in the legend.

The edge checks (`depends_on`, `governed_by`, `member_of`, `derives_from`), the
coverage report, BDD alignment, the freeze lock and the forward rule belong to
tranches 3 and 4 and are not run here.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.core.validation_rules import ValidationError
from gzkit.models.catalog import CATALOG_FILES, Catalog, load_catalog
from gzkit.registries import RegistryError, load_registry
from gzkit.schemas import load_schema

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


def audit_catalog(project_root: Path) -> list[ValidationError]:
    """Run the catalog structure checks; any finding makes the caller exit 3."""
    errors = _schema_findings(project_root)
    if errors:
        return errors
    return _structure_findings(load_catalog(project_root))
