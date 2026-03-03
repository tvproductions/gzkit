"""Common utilities and error types for CLI commands."""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, cast

from rich.console import Console

from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts


class GzCliError(Exception):
    """User-facing CLI error."""


console = Console(
    no_color=os.environ.get("NO_COLOR") is not None,
    force_terminal=os.environ.get("FORCE_COLOR") is not None,
)

COMMAND_DOCS: dict[str, str] = {
    "init": "docs/user/commands/init.md",
    "prd": "docs/user/commands/prd.md",
    "constitute": "docs/user/commands/constitute.md",
    "specify": "docs/user/commands/specify.md",
    "plan": "docs/user/commands/plan.md",
    "status": "docs/user/commands/status.md",
    "state": "docs/user/commands/state.md",
    "git-sync": "docs/user/commands/git-sync.md",
    "attest": "docs/user/commands/attest.md",
    "implement": "docs/user/commands/implement.md",
    "gates": "docs/user/commands/gates.md",
    "migrate-semver": "docs/user/commands/migrate-semver.md",
    "register-adrs": "docs/user/commands/register-adrs.md",
    "skill audit": "docs/user/commands/skill-audit.md",
    "closeout": "docs/user/commands/closeout.md",
    "audit": "docs/user/commands/audit.md",
    "check-config-paths": "docs/user/commands/check-config-paths.md",
    "cli audit": "docs/user/commands/cli-audit.md",
    "parity check": "docs/user/commands/parity-check.md",
    "readiness audit": "docs/user/commands/readiness-audit.md",
    "adr status": "docs/user/commands/adr-status.md",
    "adr promote": "docs/user/commands/adr-promote.md",
    "adr audit-check": "docs/user/commands/adr-audit-check.md",
    "adr emit-receipt": "docs/user/commands/adr-emit-receipt.md",
    "obpi emit-receipt": "docs/user/commands/obpi-emit-receipt.md",
    "agent sync control-surfaces": "docs/user/commands/agent-sync-control-surfaces.md",
}

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
    raise GzCliError(f"Pool ADRs cannot be {action}: {adr_id}. Promote this ADR from pool first.")


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        raise GzCliError("gzkit not initialized. Run 'gz init' first.")
    return GzkitConfig.load(config_path)


def load_manifest(project_root: Path) -> dict[str, Any]:
    """Load the gzkit manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        raise GzCliError("Missing .gzkit/manifest.json")
    return json.loads(manifest_path.read_text())


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


def _resolve_adr_lane(info: dict[str, Any], default_mode: str) -> str:
    """Resolve lane from ADR metadata with mode fallback."""
    lane = str(info.get("lane") or default_mode).lower()
    return lane if lane in {"lite", "heavy"} else default_mode


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
    lane = _resolve_adr_lane(info, config.mode)
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


def _run_exec(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
    """Run a subprocess command and return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


def _git_cmd(project_root: Path, *args: str) -> tuple[int, str, str]:
    """Run git command in project root."""
    return _run_exec(["git", *args], cwd=project_root)


def _compute_git_sync_state(project_root: Path, branch: str, remote: str) -> dict[str, Any]:
    """Compute ahead/behind/divergence against remote branch."""
    warnings: list[str] = []
    ahead = 0
    behind = 0
    diverged = False

    rc_head, head, err_head = _git_cmd(project_root, "rev-parse", branch)
    if rc_head != 0:
        warnings.append(err_head or f"Could not resolve local branch: {branch}")
        return {
            "head": None,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_remote, remote_head, err_remote = _git_cmd(project_root, "rev-parse", f"{remote}/{branch}")
    if rc_remote != 0:
        warnings.append(err_remote or f"Could not resolve remote branch: {remote}/{branch}")
        return {
            "head": head,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_ahead, ahead_s, _ = _git_cmd(
        project_root, "rev-list", "--count", f"{remote}/{branch}..{branch}"
    )
    rc_behind, behind_s, _ = _git_cmd(
        project_root, "rev-list", "--count", f"{branch}..{remote}/{branch}"
    )
    if rc_ahead == 0 and ahead_s.isdigit():
        ahead = int(ahead_s)
    if rc_behind == 0 and behind_s.isdigit():
        behind = int(behind_s)
    diverged = ahead > 0 and behind > 0

    return {
        "head": head,
        "remote_head": remote_head,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "warnings": warnings,
    }


def _head_is_merge_commit(project_root: Path) -> bool:
    """Return True when HEAD itself is a merge commit."""
    rc_merge, merge_head, _ = _git_cmd(
        project_root, "rev-list", "--max-count=1", "--merges", "HEAD"
    )
    rc_head, head_sha, _ = _git_cmd(project_root, "rev-parse", "HEAD")
    return rc_merge == 0 and rc_head == 0 and bool(merge_head) and merge_head == head_sha


def _git_status_lines(project_root: Path) -> tuple[list[str], str | None]:
    """Return porcelain status lines, or an error if status can't be read."""
    rc_status, status_out, err_status = _git_cmd(project_root, "status", "--porcelain")
    if rc_status != 0:
        return [], err_status or "Could not read git status."
    lines = [line for line in status_out.splitlines() if line.strip()]
    return lines, None


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
                raise GzCliError(f"Multiple ADR files found for {requested_id}: {rels}")
            rels = ", ".join(str(path.relative_to(project_root)) for path, _resolved in candidates)
            raise GzCliError(f"Multiple ADR files found for {requested_id}: {rels}")
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

    raise GzCliError(f"ADR not found: {adr}")


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
            raise GzCliError("No pending ADRs found. Use --adr to specify one.")
        else:
            raise GzCliError("Multiple pending ADRs found. Use --adr to specify one.")

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr_id = ledger.canonicalize_id(adr_id)

    _adr_file, resolved_adr_id = resolve_adr_file(project_root, config, canonical_adr_id)
    return resolved_adr_id


def _parse_frontmatter_value(content: str, key: str) -> str | None:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        raw_key, _, raw_value = line.partition(":")
        if raw_key.strip() != key:
            continue
        return raw_value.strip().strip("\"'")
    return None


def _upsert_frontmatter_value(content: str, key: str, value: str) -> str:
    """Set or insert a top-level frontmatter key/value pair."""
    lines = content.splitlines()
    if not lines:
        return f"---\n{key}: {value}\n---\n"

    if lines[0].strip() != "---":
        prefixed = ["---", f"{key}: {value}", "---", "", *lines]
        return "\n".join(prefixed).rstrip() + "\n"

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        lines.extend([f"{key}: {value}", "---"])
        return "\n".join(lines).rstrip() + "\n"

    replaced = False
    for idx in range(1, end_idx):
        raw_key, sep, _raw_value = lines[idx].partition(":")
        if sep and raw_key.strip() == key:
            lines[idx] = f"{key}: {value}"
            replaced = True
            break

    if not replaced:
        lines.insert(end_idx, f"{key}: {value}")

    return "\n".join(lines).rstrip() + "\n"
