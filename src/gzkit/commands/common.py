"""Common utilities and error types for CLI commands."""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, cast

from rich.console import Console

from gzkit.config import GzkitConfig
from gzkit.core.exceptions import GzkitError
from gzkit.ledger import (
    Ledger,
    resolve_adr_lane,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts


class GzCliError(GzkitError):
    """User-facing CLI error.

    Inherits from :class:`GzkitError` so the CLI boundary can catch the
    entire typed hierarchy with a single ``except GzkitError`` clause.
    Exit code defaults to 1 (user/config error) via the base class.
    """


console = Console(
    no_color=os.environ.get("NO_COLOR") is not None,
    force_terminal=os.environ.get("FORCE_COLOR") is not None,
)


ADR_SEMVER_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+(?:[.-][A-Za-z0-9][A-Za-z0-9.-]*)?$")
ADR_POOL_ID_RE = re.compile(r"^ADR-pool\.[A-Za-z0-9][A-Za-z0-9.-]*$")
SEMVER_ONLY_RE = re.compile(r"^\d+\.\d+\.\d+$")
ADR_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _prompt_text(prompt: str, default: str = "") -> str:
    """Prompt for a text response via stdin."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ")
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    return answer if answer else default


def _confirm(prompt: str, default: bool = True) -> bool:
    """Prompt for a yes/no confirmation via stdin."""
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(f"{prompt}{suffix}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    if not answer:
        return default
    return answer in {"y", "yes"}


def _is_pool_adr_id(adr_id: str) -> bool:
    """Return True when an ADR identifier represents a pool entry."""
    return ADR_POOL_ID_RE.match(adr_id) is not None or "-pool." in adr_id


def _apply_pool_adr_status_overrides(adr_id: str, payload: dict[str, Any]) -> None:
    """Force pool ADRs to remain backlog-style on status surfaces."""
    if not _is_pool_adr_id(adr_id):
        return

    payload["attested"] = False
    payload["attestation_status"] = None
    payload["attestation_term"] = None
    payload["validated"] = False
    payload["lifecycle_status"] = "Pending"
    payload["closeout_phase"] = "pre_closeout"

    gates = cast(dict[str, str], payload.get("gates", {}))
    if gates:
        gates["5"] = "pending"


def _reject_pool_adr_for_lifecycle(adr_id: str, action: str) -> None:
    """Block closeout lifecycle operations for pool ADRs."""
    if not _is_pool_adr_id(adr_id):
        return
    msg = f"Pool ADRs cannot be {action}: {adr_id}. Promote this ADR from pool first."
    raise GzCliError(msg)  # noqa: TRY003


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        msg = "gzkit not initialized. Run 'gz init' first."
        raise GzCliError(msg)  # noqa: TRY003
    return GzkitConfig.load(config_path)


def load_manifest(project_root: Path) -> dict[str, Any]:
    """Load the gzkit manifest."""
    manifest_file = project_root / ".gzkit" / "manifest.json"
    if not manifest_file.exists():
        msg = "Missing .gzkit/manifest.json"
        raise GzCliError(msg)  # noqa: TRY003
    return json.loads(manifest_file.read_text(encoding="utf-8"))


def manifest_path(manifest: dict[str, Any], section: str, key: str) -> Path:
    """Resolve a path from a manifest section and key.

    Returns a ``Path`` relative to project root.  Works with both v2
    (sectioned) and v1 (flat) manifest structures.

    Raises ``KeyError`` with a descriptive message when the section or
    key cannot be found.
    """
    # v2: section is a dict containing the key
    if section in manifest and isinstance(manifest[section], dict):
        if key not in manifest[section]:
            msg = f"Key {key!r} not found in manifest section {section!r}"
            raise KeyError(msg)
        return Path(str(manifest[section][key]))

    # v1 fallback: key at top level
    if key in manifest:
        return Path(str(manifest[key]))

    # Neither path resolved
    if section not in manifest:
        msg = f"Section {section!r} not found in manifest and key {key!r} not at top level"
        raise KeyError(msg)
    msg = f"Key {key!r} not found in manifest section {section!r} (section is not a dict)"
    raise KeyError(msg)


def get_git_user() -> str:
    """Get the current git user for attestations."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _gate4_na_reason(project_root: Path, lane: str) -> str | None:
    """Return explicit Gate 4 N/A rationale when BDD suite is not applicable."""
    if lane != "heavy":
        return "Gate 4 applies to heavy lane only."
    return None


def _attestation_gate_snapshot(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
) -> dict[str, Any]:
    """Compute attestation prerequisite state for one ADR."""
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id, {})
    lane = resolve_adr_lane(info, config.mode)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)

    gate2 = gate_statuses.get(2, "pending")
    gate3 = gate_statuses.get(3, "pending")
    gate4 = gate_statuses.get(4, "pending")
    gate4_na = _gate4_na_reason(project_root, lane)

    blockers: list[str] = []
    if gate2 != "pass":
        blockers.append(f"Gate 2 must pass (current: {gate2}).")

    if lane == "heavy":
        if gate3 != "pass":
            blockers.append(f"Gate 3 must pass (current: {gate3}).")
        if gate4 != "pass":
            blockers.append(f"Gate 4 must pass (current: {gate4}).")

    return {
        "lane": lane,
        "gate2": gate2,
        "gate3": gate3 if lane == "heavy" else "n/a",
        "gate4": "n/a" if gate4_na is not None else gate4,
        "gate4_na_reason": gate4_na,
        "ready": not blockers,
        "blockers": blockers,
    }


def _canonical_attestation_term(attest_status: str, reason: str | None = None) -> str:
    """Render canonical attestation term from stable CLI status token."""
    base = Ledger.canonical_attestation_term(attest_status) or attest_status
    if attest_status in {"partial", "dropped"} and reason:
        return f"{base}: {reason}"
    return base


def resolve_adr_file(project_root: Path, config: GzkitConfig, adr: str) -> tuple[Path, str]:
    """Resolve an ADR file path from an ID, supporting nested layouts."""

    def _pick_unique(
        candidates: list[tuple[Path, str]], requested_id: str
    ) -> tuple[Path, str] | None:
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            # Prefer non-pool ADRs when duplicates exist
            non_pool = [
                entry for entry in candidates if "docs/design/adr/pool" not in str(entry[0])
            ]
            if len(non_pool) == 1:
                return non_pool[0]
            if len(non_pool) > 1:
                rels = ", ".join(
                    str(path.relative_to(project_root)) for path, _resolved in non_pool
                )
                msg = f"Multiple ADR files found for {requested_id}: {rels}"
                raise GzCliError(msg)  # noqa: TRY003
            rels = ", ".join(str(path.relative_to(project_root)) for path, _resolved in candidates)
            msg = f"Multiple ADR files found for {requested_id}: {rels}"
            raise GzCliError(msg)  # noqa: TRY003
        return None

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    adr_dir = project_root / config.paths.adrs

    candidates = [adr_dir / f"{adr}.md"]
    if adr_id != adr:
        candidates.append(adr_dir / f"{adr_id}.md")

    for candidate in candidates:
        if candidate.exists():
            return candidate, candidate.stem

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    exact_matches: list[tuple[Path, str]] = []
    prefix_matches: list[tuple[Path, str]] = []
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        stem_id = adr_file.stem
        parsed_id = metadata.get("id", stem_id)
        # Prefer explicit metadata IDs, but also match filename stems for
        # suffixed IDs like ADR-0.6.0-pool.* when headers use ADR-0.6.0.
        if adr_id == stem_id:
            exact_matches.append((adr_file, stem_id))
            continue
        if adr_id == parsed_id:
            exact_matches.append((adr_file, parsed_id))
            continue
        if stem_id.startswith(f"{adr_id}-"):
            prefix_matches.append((adr_file, stem_id))

    unique = _pick_unique(exact_matches, adr_id)
    if unique:
        return unique
    unique = _pick_unique(prefix_matches, adr_id)
    if unique:
        return unique

    msg = f"ADR not found: {adr}"
    raise GzCliError(msg)  # noqa: TRY003


def resolve_adr_ledger_id(
    adr_file: Path,
    adr_id: str,
    ledger: Ledger,
) -> str:
    """Resolve an ADR ID to its ledger graph key, falling back to file stem.

    When frontmatter ``id:`` (e.g. ``ADR-0.16.0``) differs from the ledger
    registration key (e.g. ``ADR-0.16.0-cms-architecture-formalization``),
    the file stem is tried as a fallback so that graph lookups succeed.
    """
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id)
    if info and info.get("type") == "adr":
        return adr_id
    stem_id = adr_file.stem
    if stem_id != adr_id:
        stem_info = graph.get(stem_id)
        if stem_info and stem_info.get("type") == "adr":
            return stem_id
    return adr_id


def resolve_target_adr(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr: str | None,
) -> str:
    """Resolve ADR id for gate operations."""
    if adr is None:
        pending = ledger.get_pending_attestations()
        if len(pending) == 1:
            adr = pending[0]
        elif not pending:
            msg = "No pending ADRs found. Use --adr to specify one."
            raise GzCliError(msg)  # noqa: TRY003
        else:
            msg = "Multiple pending ADRs found. Use --adr to specify one."
            raise GzCliError(msg)  # noqa: TRY003

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr_id = ledger.canonicalize_id(adr_id)

    adr_file, resolved_adr_id = resolve_adr_file(project_root, config, canonical_adr_id)
    return resolve_adr_ledger_id(adr_file, resolved_adr_id, ledger)


def resolve_obpi(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    obpi: str,
) -> tuple[str, Path | None]:
    """Resolve an OBPI id and optional file path from ledger or matching brief."""
    obpi_input = obpi if obpi.startswith("OBPI-") else f"OBPI-{obpi}"
    canonical_obpi = ledger.canonicalize_id(obpi_input)
    graph = ledger.get_artifact_graph()
    info = graph.get(canonical_obpi)
    if info and info.get("type") != "obpi":
        msg = f"OBPI not found in ledger: {canonical_obpi}"
        raise GzCliError(msg)  # noqa: TRY003

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    matches: list[Path] = []
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        file_id = metadata.get("id", obpi_file.stem)
        if ledger.canonicalize_id(file_id) == canonical_obpi:
            matches.append(obpi_file)

    if len(matches) > 1:
        rels = ", ".join(str(path.relative_to(project_root)) for path in matches)
        msg = f"Multiple OBPI files found for {canonical_obpi}: {rels}"
        raise GzCliError(msg)  # noqa: TRY003

    if info and info.get("type") == "obpi":
        return canonical_obpi, matches[0] if matches else None
    if matches:
        return canonical_obpi, matches[0]
    msg = f"OBPI not found in ledger or briefs: {canonical_obpi}"
    raise GzCliError(msg)  # noqa: TRY003


def resolve_obpi_file(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    obpi: str,
) -> tuple[Path, str]:
    """Resolve an OBPI file path from an ID, supporting rename chains."""
    canonical_obpi, obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    if obpi_file is None:
        msg = f"OBPI file not found for {canonical_obpi}"
        raise GzCliError(msg)  # noqa: TRY003
    return obpi_file, canonical_obpi


# ---------------------------------------------------------------------------
# Closeout form helpers -- canonical implementation in closeout_form.py
# ---------------------------------------------------------------------------
from gzkit.commands.closeout_form import (  # noqa: E402
    _closeout_form_attestation_text as _closeout_form_attestation_text,
)
from gzkit.commands.closeout_form import _closeout_form_path as _closeout_form_path  # noqa: E402
from gzkit.commands.closeout_form import (  # noqa: E402
    _closeout_form_timestamp as _closeout_form_timestamp,
)
from gzkit.commands.closeout_form import (  # noqa: E402
    _render_adr_closeout_form as _render_adr_closeout_form,
)
from gzkit.commands.closeout_form import (  # noqa: E402
    _update_adr_attestation_block as _update_adr_attestation_block,
)
from gzkit.commands.closeout_form import (  # noqa: E402
    _upsert_frontmatter_value as _upsert_frontmatter_value,
)
from gzkit.commands.closeout_form import (  # noqa: E402
    _write_adr_closeout_form as _write_adr_closeout_form,
)

# ---------------------------------------------------------------------------
# Version sync helpers — canonical implementation in version_sync.py
# ---------------------------------------------------------------------------
from gzkit.commands.version_sync import _VERSION_BADGE_RE as _VERSION_BADGE_RE  # noqa: E402
from gzkit.commands.version_sync import (  # noqa: E402
    _extract_adr_version as _extract_adr_version,
)
from gzkit.commands.version_sync import (  # noqa: E402
    _parse_semver_tuple as _parse_semver_tuple,
)
from gzkit.commands.version_sync import (  # noqa: E402
    _read_current_project_version as _read_current_project_version,
)
from gzkit.commands.version_sync import (  # noqa: E402
    aggregate_audit_evidence as aggregate_audit_evidence,
)
from gzkit.commands.version_sync import check_version_sync as check_version_sync  # noqa: E402
from gzkit.commands.version_sync import (  # noqa: E402
    sync_project_version as sync_project_version,
)

# ---------------------------------------------------------------------------
# Ceremony enforcement helpers (ADR-0.23.0 / OBPI-0.23.0-04)
# ---------------------------------------------------------------------------

_CLOSING_ARG_HEADING_RE = re.compile(r"^## Closing Argument\s*$", re.MULTILINE)
_NEXT_H2_RE = re.compile(r"^## ", re.MULTILINE)
_EVIDENCE_SUB_RE = re.compile(r"^### (?:Implementation Summary|Key Proof)\b", re.MULTILINE)
_CLOSING_ARG_PLACEHOLDER = "*To be authored at completion from delivered evidence.*"


def extract_closing_argument(brief_text: str) -> str | None:
    """Extract the Closing Argument section from an OBPI brief.

    Returns the argument text (before evidence subsections), or None if
    the section is missing, empty, or still a placeholder.
    """
    match = _CLOSING_ARG_HEADING_RE.search(brief_text)
    if not match:
        return None
    rest = brief_text[match.end() :]
    end = len(rest)
    for pattern in (_NEXT_H2_RE, _EVIDENCE_SUB_RE):
        m = pattern.search(rest)
        if m:
            end = min(end, m.start())
    text = rest[:end].strip()
    if not text or text == _CLOSING_ARG_PLACEHOLDER:
        return None
    return text


def gather_reviewer_assessments(adr_package_dir: Path) -> dict[str, Path]:
    """Find REVIEW-*.md reviewer artifacts in the ADR package.

    Searches briefs/ and obpis/ subdirectories.
    """
    reviews: dict[str, Path] = {}
    for subdir in ("briefs", "obpis"):
        d = adr_package_dir / subdir
        if not d.is_dir():
            continue
        for p in sorted(d.glob("REVIEW-*.md")):
            reviews[p.stem.removeprefix("REVIEW-")] = p
    return reviews


def _extract_review_fields(review_path: Path) -> dict[str, str]:
    """Extract structured fields from a REVIEW-*.md artifact.

    Returns a dict with keys: verdict, docs_quality, closing_argument_quality,
    promises_met (as "N/M" string).
    """
    content = review_path.read_text(encoding="utf-8")
    fields: dict[str, str] = {
        "verdict": "unknown",
        "docs_quality": "",
        "closing_argument_quality": "",
    }

    yes_count = 0
    total_count = 0
    for line in content.splitlines():
        if line.startswith("**Verdict:**"):
            fields["verdict"] = line.split("**Verdict:**", 1)[1].strip()
        elif line.startswith("**Assessment:**"):
            value = line.split("**Assessment:**", 1)[1].strip()
            if not fields["docs_quality"]:
                fields["docs_quality"] = value
            elif not fields["closing_argument_quality"]:
                fields["closing_argument_quality"] = value
        elif "**[YES]**" in line:
            yes_count += 1
            total_count += 1
        elif "**[NO]**" in line:
            total_count += 1

    fields["promises_met"] = f"{yes_count}/{total_count}" if total_count > 0 else "n/a"
    return fields


def _extract_review_verdict(review_path: Path) -> str:
    """Extract the verdict from a REVIEW-*.md artifact."""
    return _extract_review_fields(review_path)["verdict"]


def render_defense_brief_section(
    closing_args: dict[str, str],
    proof_obpis: Any,
    reviews: dict[str, Path],
) -> str:
    """Render the Defense Brief markdown section for ADR-CLOSEOUT-FORM.md.

    Args:
        closing_args: OBPI ID to closing argument text.
        proof_obpis: ProductProofResult (or None). Accessed via duck typing.
        reviews: OBPI ID to REVIEW-*.md path.
    """
    lines = ["## Defense Brief", ""]

    lines.append("### Closing Arguments")
    lines.append("")
    if closing_args:
        for obpi_id, arg in closing_args.items():
            lines.append(f"#### {obpi_id}")
            lines.append("")
            lines.append(arg)
            lines.append("")
    else:
        lines.append("*No closing arguments found.*")
        lines.append("")

    lines.append("### Product Proof")
    lines.append("")
    if proof_obpis is not None and hasattr(proof_obpis, "obpi_proofs"):
        lines.append("| OBPI | Proof Type | Status |")
        lines.append("|------|-----------|--------|")
        for p in proof_obpis.obpi_proofs:
            status = "FOUND" if p.has_proof else "MISSING"
            lines.append(f"| {p.obpi_id} | {p.proof_type} | {status} |")
        lines.append("")
    else:
        lines.append("*No product proof data available.*")
        lines.append("")

    lines.append("### Reviewer Assessment")
    lines.append("")
    if reviews:
        lines.append("| OBPI | Verdict | Promises Met | Docs Quality | Closing Arg | Artifact |")
        lines.append("|------|---------|-------------|-------------|-------------|----------|")
        for obpi_id, path in sorted(reviews.items()):
            fields = _extract_review_fields(path)
            lines.append(
                f"| {obpi_id} | {fields['verdict']} | {fields['promises_met']} "
                f"| {fields['docs_quality']} | {fields['closing_argument_quality']} "
                f"| `{path.name}` |"
            )
        lines.append("")
    else:
        lines.append("*No reviewer assessments found.*")
        lines.append("")

    return "\n".join(lines)


def compute_defense_brief(
    obpi_files: dict[str, Path],
    adr_package_dir: Path,
    proof_result: Any,
) -> str:
    """Compute the full Defense Brief section for an ADR closeout.

    Reads closing arguments from OBPI briefs, gathers reviewer artifacts,
    and combines with product proof data into a single markdown section.
    """
    closing_args: dict[str, str] = {}
    for obpi_id, brief_path in sorted(obpi_files.items()):
        arg = extract_closing_argument(brief_path.read_text(encoding="utf-8"))
        if arg:
            closing_args[obpi_id] = arg
    reviews = gather_reviewer_assessments(adr_package_dir)
    return render_defense_brief_section(closing_args, proof_result, reviews)


def _cli_main():
    """Return the gzkit.cli.main module for test-mock compatibility.

    Tests patch dependencies at ``gzkit.cli.main.<name>``.  After the
    cli/main.py restructure (OBPI-0.0.4-01), handler functions live in
    separate command modules.  This helper lets command modules look up
    shared dependencies through main.py's namespace so ``mock.patch``
    targets continue to work.
    """
    import sys  # deferred to avoid top-level import of sys just for this helper

    return sys.modules["gzkit.cli.main"]
