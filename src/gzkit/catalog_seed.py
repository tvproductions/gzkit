"""What `gz init` writes into `data/catalog/` (RO-14, the fresh-project discrepancy).

The registry seam refuses a missing file as a tree defect (GHI #1067) and no verb
creates the store, so a project `gz init` left without `data/catalog/` could not
run a work package. Operator ruling 2026-11-01, verbatim "Seed at gz init
(Recommended)": init and its repair path write each absent file, and never touch
one that exists.
"""

import importlib.resources
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from gzkit.models.catalog import DELIVERY_EVENTS_FILE
from gzkit.registries import registry_path

if TYPE_CHECKING:
    from pathlib import Path

SEED_FILE = "catalog_seed.json"


def load_seed() -> dict[str, dict[str, object]]:
    """Read the packaged seed, keyed by registry name.

    Returns:
        Each catalog file's payload, without the cutover seeding stamps.

    """
    resource = importlib.resources.files("gzkit").joinpath(SEED_FILE)
    return json.loads(resource.read_text(encoding="utf-8"))["files"]


def seed_catalog(
    project_root: Path, *, now: datetime | None = None, dry_run: bool = False
) -> str | None:
    """Write each `data/catalog/` file the project lacks.

    The cutover is stamped now, never copied from gzkit's: on a repair, a project's
    earlier delivery events must stay legacy rather than be read by the forward rule.

    Returns:
        A human-readable status string, or None when every file exists.

    """
    missing = {
        name: payload
        for name, payload in load_seed().items()
        if not registry_path(project_root, name).exists()
    }
    if not missing:
        return None
    summary = f"{len(missing)} data/catalog/ file(s)"
    if dry_run:
        return f"Would seed {summary}"
    cutover = (now or datetime.now(UTC)).isoformat()
    for name, payload in missing.items():
        doc = {**payload, "cutover": cutover} if name == DELIVERY_EVENTS_FILE else payload
        path = registry_path(project_root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(doc, indent=2, ensure_ascii=False)
        path.write_text(text + "\n", encoding="utf-8")
    return f"Seeded {summary}"
