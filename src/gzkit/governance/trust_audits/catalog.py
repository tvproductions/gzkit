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
Tranche 4's forward rule then reads the delivery events since the cutover in
`data/catalog/delivery_events.json` and announces the ones naming no REQ or
outcome (`gzkit.governance.trust_audits.catalog_forward`). RO-5 tranche 1 adds
the work-package store's checks and reads its two events against it; the freeze
lock is RO-5's verbs'.
"""

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
from gzkit.governance.trust_audits.catalog_forward import forward_rule_reading
from gzkit.ledger import Ledger
from gzkit.models.catalog import (
    CATALOG_FILES,
    DELIVERY_EVENTS_FILE,
    Catalog,
    WorkPackage,
    load_catalog,
    load_delivery_events,
)
from gzkit.registries import RegistryError, load_registry, registry_path
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


def _duplicates(
    kind: str,
    label: str,
    values: list[str],
    rule: str = "A code is never reused, a retired one included.",
) -> list[ValidationError]:
    repeated = sorted(value for value, count in Counter(values).items() if count > 1)
    if not repeated:
        return []
    return [
        _err(
            kind,
            f"{label} {', '.join(repeated)} appear more than once in data/{CATALOG_FILES[kind]}. "
            f"{rule}",
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
    return errors + work_package_findings(catalog)


def _kind_breaches(package: WorkPackage, outcomes: frozenset[str]) -> list[str]:
    """Rulings 1 and 4: a delivery package names its outcome, a repair its issues and lane.

    Returns:
        Each breach, as a clause completing "Work package <id> ...".

    """
    if package.kind == "delivery":
        breaches = [] if package.outcome else ["names no outcome"]
        if package.outcome and package.outcome not in outcomes:
            breaches.append(f"names outcome {package.outcome}, which the catalog does not hold")
        if package.issues or package.lane:
            breaches.append("holds an issue or a lane, which a delivery package derives")
        return breaches
    breaches = [] if package.issues else ["names no issue"]
    if package.lane is None:
        breaches.append("stores no lane")
    if package.outcome:
        breaches.append("names an outcome, which a repair package has in place of none")
    return breaches


def _record_breaches(package: WorkPackage, reqs: frozenset[str]) -> list[str]:
    """Amendment 4: alteration and departure ids unique, and each departure well formed.

    Returns:
        Each breach, as a clause completing "Work package <id> ...".

    """
    breaches = [
        f"repeats {label} id {value}"
        for label, ids in (
            ("alteration", [a.id for a in package.alterations]),
            ("departure", [d.id for d in package.departures]),
        )
        for value, count in Counter(ids).items()
        if count > 1
    ]
    for departure in package.departures:
        if (departure.duration == "temporary") != (departure.clear_by is not None):
            breaches.append(
                f"departure {departure.id} is {departure.duration} and "
                f"{'lacks' if departure.clear_by is None else 'carries'} a clear-by condition"
            )
        if departure.req is not None and departure.req not in reqs:
            breaches.append(
                f"departure {departure.id} names {departure.req}, absent from the catalog"
            )
    return breaches


def _series_findings(packages: tuple[WorkPackage, ...]) -> list[ValidationError]:
    """Ruling 6 and ruling 2: one id series, each alias and each issue in one package only.

    A number is the id series' key, so two packages sharing one share an id or reuse it.

    Returns:
        One finding per repeated number, issue or alias family.

    """
    numbers = [f"WP-{package.id.split('-')[1]}" for package in packages]
    issues = [f"#{issue}" for package in packages for issue in package.issues]
    aliases = [alias for package in packages for alias in package.aliases]
    errors = _duplicates(
        "work_packages",
        "Work package numbers",
        numbers,
        "One id series: a number names one package, never reused (RO-5 ruling 6).",
    )
    errors += _duplicates(
        "work_packages",
        "Issues",
        issues,
        "Each issue belongs to exactly one repair package (RO-5 ruling 2).",
    )
    return errors + _duplicates(
        "work_packages", "Aliases", aliases, "An alias resolves to one package (RO-5 ruling 6)."
    )


def work_package_findings(catalog: Catalog) -> list[ValidationError]:
    """Read the work-package store against RO-5's rulings.

    The rulings are `docs/governance/harbor-ro5-work-packages.md`'s.

    Returns:
        The store's findings, empty when it holds.

    """
    outcomes = frozenset(outcome.code for outcome in catalog.outcomes)
    reqs = frozenset(req.id for req in catalog.reqs)
    errors = _series_findings(catalog.work_packages)
    for package in catalog.work_packages:
        breaches = _kind_breaches(package, outcomes) + _record_breaches(package, reqs)
        if breaches:
            errors.append(
                _err(
                    "work_packages",
                    f"Work package {package.id} ({package.kind}) {'; '.join(breaches)}. "
                    "RO-5 rulings 1, 2, 4 and 6 and the 2026-10-28 amendment rule its shape "
                    "(docs/governance/harbor-ro5-work-packages.md).",
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


def _booked_findings(ledger: Ledger, catalog: Catalog) -> list[ValidationError]:
    """Read the work-package events against the store: a booked package is never dropped.

    An id the ledger names is never reused (RO-5 ruling 6), so the store keeps its record.

    Returns:
        One finding naming every booked package the store no longer holds.

    """
    held = {package.id for package in catalog.work_packages}
    booked = {
        str(row.extra.get("work_package"))
        for event_type in (
            "work_package_transitioned",
            "work_package_changed",
            "work_package_issue_closed",
        )
        for row in ledger.query(event_type=event_type)
    }
    if missing := sorted(booked - held):
        return [
            _err(
                "work_packages",
                f"Work packages {', '.join(missing)} have ledger events but no record in "
                f"data/{CATALOG_FILES['work_packages']}. An id is never reused (RO-5 ruling 6), "
                "so restore the record.",
            )
        ]
    return []


def audit_catalog(project_root: Path) -> list[ValidationError]:
    """Run the catalog checks; any finding makes the caller exit 3.

    The coverage report is advisory: it is announced and never a finding. The
    forward rule is a finding since RO-5 tranche 4.
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
    errors += _booked_findings(Ledger(project_root / config.paths.ledger), catalog)
    if any(outcome.user_facing for outcome in catalog.outcomes):
        errors += bdd_findings(catalog, scan_catalog_bindings(project_root))
    if gaps := coverage_gaps(catalog, needs):
        emit_advisory(
            f"catalog-coverage: {len(gaps)} of {len(needs)} PRD needs have no deriving "
            f"REQ: {', '.join(gaps)}"
        )
    errors += _forward_rule_findings(project_root, config, catalog)
    return errors


def _forward_rule_findings(
    project_root: Path, config: GzkitConfig, catalog: Catalog
) -> list[ValidationError]:
    """Refuse post-cutover delivery events naming no REQ, outcome or work package.

    Fail-closed since RO-5 tranche 4 (operator, 2026-10-28: "Fail-closed, legacy
    exempt (Recommended)"): an event naming an OBPI or ADR id is frozen legacy.

    Returns:
        One finding counting the unnamed events by type, or none.

    """
    if not registry_path(project_root, DELIVERY_EVENTS_FILE).is_file():
        return []
    registry = load_delivery_events(project_root)
    rows = [event.model_dump() for event in Ledger(project_root / config.paths.ledger).read_all()]
    outcomes = frozenset(outcome.code for outcome in catalog.outcomes)
    packages = frozenset(package.id for package in catalog.work_packages)
    reading = forward_rule_reading(rows, registry, outcomes, packages)
    if not reading.unnamed:
        return []
    counts = ", ".join(f"{kind} {count}" for kind, count in reading.unnamed.items())
    return [
        ValidationError(
            type=_TYPE,
            artifact=f"data/{DELIVERY_EVENTS_FILE}",
            message=(
                f"{sum(reading.unnamed.values())} of {reading.read} delivery events since "
                f"{registry.cutover.isoformat()} name no REQ, outcome or work package and no "
                f"OBPI or ADR ({counts}). A delivery event names its REQ, its outcome or its "
                "work package (RO-3 ruling 4, fail-closed since RO-5 tranche 4; "
                "docs/governance/harbor-ro5-work-packages.md). Book the work under a work "
                "package or a REQ, then re-run `uv run gz validate --catalog`."
            ),
            field="delivery_events",
        )
    ]
