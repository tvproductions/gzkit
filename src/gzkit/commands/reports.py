"""Publish big-picture reports with retained source and ledger provenance."""

from pathlib import Path

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import get_project_root
from gzkit.config import load_config
from gzkit.reports import publish_report


def report_publish_cmd(
    *,
    source: str,
    report_id: str,
    period: str,
    evidence_cutoff: str,
    as_json: bool = False,
    quiet: bool = False,
) -> None:
    """Preserve report bytes, book publication, and rebuild current/archive views."""
    output = OutputFormatter("quiet" if quiet else "json" if as_json else "human")
    root = get_project_root()
    try:
        result = publish_report(
            root,
            load_config(path=root / ".gzkit.json"),
            Path(source),
            report_id,
            period=period,
            evidence_cutoff=evidence_cutoff,
        )
    except (ValueError, UnicodeError) as exc:
        output.err(f"Report publication refused: {exc}")
        raise SystemExit(1) from exc
    except OSError as exc:
        output.err(
            f"Report publication interrupted: {exc}. Retained bytes or a publication event "
            "may already exist; fix the IO failure and retry the same id and inputs to "
            "finish publication and rebuild views."
        )
        raise SystemExit(2) from exc
    output.data(result)
