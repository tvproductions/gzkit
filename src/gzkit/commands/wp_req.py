"""``gz wp req new``, the repair requirement's writer (RP-12 O2 task 2).

The verb the operator ruled on 2026-11-05 (RP-12 ruling 48, *"a"*): it writes one
repair REQ with the next `REQ-<n>`, held on its repair package, carrying its
statement, criteria, kind and problem report, into `data/catalog/reqs.json`
beside the catalog's REQs (ruling 45), through `gzkit.req_store`. It writes
repair REQs only; catalog REQs stay RP-11's intake. A refusal exits 3 and writes
nothing, naming the flag at fault and the call to re-run; an unknown package
exits 1.
"""

from typing import NoReturn

from pydantic import ValidationError as PydanticValidationError

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.wp_order import open_package_refusal
from gzkit.core.exceptions import PolicyBreachError, ResourceNotFoundError
from gzkit.models.catalog import Criterion, RepairReq, load_catalog
from gzkit.req_store import ReqStoreError, next_req_id, stage_repair_req, write_reqs

_FLAGS = {
    "statement": "--statement",
    "criteria": "--criterion",
    "kind": "--kind",
    "problem_report": "--problem-report",
    "aligns_to": "--aligns-to",
    "supersedes": "--supersedes",
}
_CRITERION_PARTS = ("state or input", "required outcome", "evidence")


def _refuse(failed: str, why: str) -> NoReturn:
    msg = (
        f"{failed} {why} Nothing was written; correct the call and re-run "
        "`uv run gz wp req new <WP-id> --statement <text> --criterion "
        "'<state>|<outcome>|<evidence>' --kind <kind> --problem-report <issue>`."
    )
    raise PolicyBreachError(msg)


def _criterion(spec: str) -> Criterion:
    """Read `STATE|OUTCOME|EVIDENCE` into one criterion.

    Returns:
        The criterion.

    """
    parts = [part.strip() for part in spec.split("|")]
    if len(parts) != len(_CRITERION_PARTS) or not all(parts):
        _refuse(
            f"--criterion {spec!r} is not three non-empty parts joined by '|'.",
            f"A criterion names its {', '.join(_CRITERION_PARTS)} (requirements model § The "
            "records).",
        )
    state, outcome, evidence = parts
    return Criterion(state_or_input=state, required_outcome=outcome, evidence=evidence)


def _schema_errors(exc: PydanticValidationError) -> str:
    """Name each refused field by the flag the operator typed, never the model's field.

    Returns:
        One clause per refused field, joined by semicolons.

    """
    return "; ".join(
        f"{_FLAGS.get(str(error['loc'][0]), str(error['loc'][0]))}: {error['msg']}"
        for error in exc.errors()
    )


def wp_req_new_cmd(
    *, work_package: str, record: dict[str, object], criteria: list[str], as_json: bool
) -> None:
    """Write one repair REQ with the next id, held on its repair package (RP-12 ruling 48).

    ``record`` carries the verb's fields bar the id, the package and the criteria:
    the statement, the kind, the problem report, and the optional design REQ it
    aligns to and REQ it supersedes. ``criteria`` are `STATE|OUTCOME|EVIDENCE`
    specs. A refusal exits 3 through `_refuse` and writes nothing.

    Raises:
        ResourceNotFoundError: The package is not in the store; nothing is written.

    """
    ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    package = next((wp for wp in catalog.work_packages if wp.id == work_package), None)
    if package is None:
        msg = (
            f"Work package {work_package!r} is not in data/catalog/work_packages.json. "
            "A repair REQ is held on a package the catalog holds; create one with `gz wp new`."
        )
        raise ResourceNotFoundError(msg)
    try:
        req = RepairReq.model_validate(
            {
                **record,
                "criteria": [_criterion(spec) for spec in criteria],
                "id": next_req_id(catalog),
                "specialization": "repair",
                "held_on": package.id,
                "revision": 1,
            }
        )
    except PydanticValidationError as exc:
        _refuse(f"{_schema_errors(exc)}.", "The repair requirement is ruled by RP-12 ruling 45.")
    try:
        staged = stage_repair_req(catalog, req)
    except ReqStoreError as exc:
        _refuse(
            " ".join(exc.breaches),
            "The rulings are in docs/governance/harbor-ro12-contractor-kit.md.",
        )
    if refusal := open_package_refusal(root, package, "A repair REQ"):
        _refuse(*refusal)
    write_reqs(root, staged)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(req if as_json else f"Wrote {req.id}, a repair REQ held on {package.id}.")
