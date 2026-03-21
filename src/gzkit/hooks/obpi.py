"""OBPI completion validator engine.

Enforces scope, evidence, and git-sync readiness requirements for OBPI
completion transitions.
"""

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, cast

from gzkit.config import GzkitConfig
from gzkit.git_sync import assess_git_sync_readiness
from gzkit.ledger import Ledger
from gzkit.utils import git_cmd

# Blacklist of non-substantive placeholder tokens
STRICT_PLACEHOLDERS = {
    "tbd",
    "todo",
    "...",
    "none",
    "(none)",
    "-",
    "paste test output here",
    "paste lint/format/type check output here",
    "one-sentence concrete outcome",
}

# Template defaults emitted by superbook.build_obpi_plan() that indicate
# an OBPI brief was auto-generated but never authored.
TEMPLATE_SCAFFOLD_MARKERS: dict[str, list[str]] = {
    "Allowed Paths": ["src/module/"],
    "Requirements (FAIL-CLOSED)": ["First constraint", "Second constraint"],
    "Acceptance Criteria": ["Given/When/Then behavior criterion"],
}


def section_body(content: str, heading: str) -> str | None:
    """Return the body of an H2/H3 section when present."""
    for marker in ("##", "###"):
        pattern = (
            rf"^{re.escape(marker)} {re.escape(heading)}\s*$"
            rf"([\s\S]*?)(?:^{marker} |\n---|\Z)"
        )
        match = re.search(pattern, content, flags=re.MULTILINE)
        if match:
            body = match.group(1).strip()
            if body:
                return body
    return None


def extract_allowed_paths(content: str) -> list[str]:
    """Extract normalized allowlist patterns from an OBPI brief."""
    section = section_body(content, "Allowed Paths")
    if not section:
        return []

    patterns: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue

        backticked = re.findall(r"`([^`]+)`", stripped)
        candidates = backticked or [re.sub(r"^-+\s*", "", stripped).split(" - ", 1)[0]]
        for candidate in candidates:
            normalized = candidate.strip().replace("\\", "/")
            if not normalized or " " in normalized:
                continue
            if normalized.endswith("/"):
                normalized = normalized.rstrip("/") + "/**"
            patterns.append(normalized)

    return patterns


def collect_changed_files(project_root: Path) -> list[str]:
    """Return the live changed-file set for scope validation."""
    files: set[str] = set()
    commands = (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    )
    for command in commands:
        rc, output, _ = git_cmd(project_root, *command)
        if rc != 0:
            continue
        for line in output.splitlines():
            normalized = line.strip().replace("\\", "/")
            if normalized:
                files.add(normalized)
    return sorted(files)


def path_is_allowlisted(path: str, allowlist: list[str]) -> bool:
    """Return True when a changed path matches an allowed path pattern."""
    for pattern in allowlist:
        normalized = pattern.replace("\\", "/")
        if normalized.endswith("/**"):
            prefix = normalized[: -len("/**")]
            if path == prefix or path.startswith(prefix + "/"):
                return True
        if fnmatch(path, normalized):
            return True
    return False


def build_scope_audit(project_root: Path, content: str) -> dict[str, list[str]]:
    """Build a structured allowlist-vs-changed-files payload."""
    allowlist = extract_allowed_paths(content)
    changed_files = collect_changed_files(project_root)
    out_of_scope_files = [
        path for path in changed_files if not path_is_allowlisted(path, allowlist)
    ]
    return {
        "allowlist": allowlist,
        "changed_files": changed_files,
        "out_of_scope_files": out_of_scope_files,
    }


def normalize_scope_audit(raw_scope_audit: Any) -> dict[str, list[str]] | None:
    """Validate and normalize a structured scope-audit payload."""
    if raw_scope_audit is None:
        return None
    if not isinstance(raw_scope_audit, dict):
        return None

    normalized: dict[str, list[str]] = {}
    for field in ("allowlist", "changed_files", "out_of_scope_files"):
        raw_value = raw_scope_audit.get(field)
        if raw_value is None:
            normalized[field] = []
            continue
        if not isinstance(raw_value, list):
            return None
        cleaned: list[str] = []
        for item in raw_value:
            if not isinstance(item, str) or not item.strip():
                return None
            cleaned.append(item.strip().replace("\\", "/"))
        normalized[field] = cleaned
    return normalized


def normalize_git_sync_state(raw_state: Any) -> dict[str, Any] | None:
    """Validate and normalize structured git-sync state."""
    if raw_state is None:
        return None
    if not isinstance(raw_state, dict):
        return None

    normalized: dict[str, Any] = {}
    optional_string_fields = ("branch", "remote", "head", "remote_head")
    for field in optional_string_fields:
        value = raw_state.get(field)
        if value is None:
            normalized[field] = None
        elif isinstance(value, str):
            normalized[field] = value.strip() or None
        else:
            return None

    bool_fields = ("dirty", "diverged")
    for field in bool_fields:
        value = raw_state.get(field)
        if not isinstance(value, bool):
            return None
        normalized[field] = value

    int_fields = ("ahead", "behind")
    for field in int_fields:
        value = raw_state.get(field)
        if not isinstance(value, int):
            return None
        normalized[field] = value

    list_fields = ("actions", "warnings", "blockers")
    for field in list_fields:
        value = raw_state.get(field)
        if not isinstance(value, list):
            return None
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                return None
            cleaned.append(item.strip())
        normalized[field] = cleaned

    return normalized


class ObpiValidator:
    """Validates OBPI brief content against governance requirements."""

    def __init__(self, project_root: Path):
        """Initialize validator with project root."""
        self.project_root = project_root
        self.config = GzkitConfig.load(project_root / ".gzkit.json")
        self.ledger = Ledger(project_root / self.config.paths.ledger)

    def validate_file(self, obpi_path: Path) -> list[str]:
        """Validate an OBPI file for completion readiness.

        Returns a list of error messages (empty if valid).
        """
        from gzkit.ledger import (
            parse_frontmatter_value,
            resolve_adr_lane,
        )

        if not obpi_path.exists():
            return [f"File not found: {obpi_path}"]

        content = obpi_path.read_text(encoding="utf-8")
        status = (parse_frontmatter_value(content, "status") or "").strip().lower()

        # Check for template scaffold on any status — these indicate a brief
        # was auto-generated but never authored.  GHI #27.
        scaffold_warnings = self._detect_template_scaffold(content)
        if status != "completed":
            return scaffold_warnings

        errors = list(scaffold_warnings)

        # 1. Resolve Lane Inheritance
        parent_id = parse_frontmatter_value(content, "parent")
        if not parent_id:
            errors.append("Missing 'parent' ADR in frontmatter.")
            return errors

        graph = self.ledger.get_artifact_graph()
        parent_info = graph.get(self.ledger.canonicalize_id(parent_id), {})
        lane = resolve_adr_lane(parent_info, self.config.mode)

        allowlist = extract_allowed_paths(content)
        if not allowlist:
            errors.append("Missing or empty 'Allowed Paths' allowlist.")
        else:
            changed_files = collect_changed_files(self.project_root)
            errors.extend(self._validate_changed_files(changed_files, allowlist))

        readiness = assess_git_sync_readiness(self.project_root)
        errors.extend(cast(list[str], readiness["blockers"]))

        # 2. Check for Substantive Implementation Summary
        if not self._has_substantive_summary(content):
            errors.append("Missing or non-substantive 'Implementation Summary'.")

        # 3. Check for Key Proof
        if not self._has_substantive_section(content, "Key Proof"):
            errors.append("Missing or non-substantive 'Key Proof'.")

        # 4. Enforce Heavy/Foundation Human Attestation
        if lane == "heavy" or self._is_foundation_series(parent_id):
            attestation_errors = self._validate_human_attestation(content)
            errors.extend(attestation_errors)

        return errors

    def _detect_template_scaffold(self, content: str) -> list[str]:
        """Detect auto-generated template defaults that were never authored.

        Returns a list of warnings identifying which sections still contain
        the scaffold defaults emitted by ``superbook.build_obpi_plan()``.
        """
        warnings: list[str] = []
        for section_name, markers in TEMPLATE_SCAFFOLD_MARKERS.items():
            body = self._section_body(content, section_name)
            if body is None:
                continue
            for marker in markers:
                if marker in body:
                    warnings.append(
                        f"'{section_name}' contains template placeholder "
                        f"'{marker}' — brief was auto-generated but never authored."
                    )
                    break
        return warnings

    def _validate_changed_files(self, changed_files: list[str], allowlist: list[str]) -> list[str]:
        """Validate the live changed-file set against the allowlist."""
        errors: list[str] = []
        if not changed_files:
            errors.append(
                "Changed-files audit found no modified paths. "
                "Completion requires live scope evidence."
            )
            return errors

        for path in changed_files:
            if not path_is_allowlisted(path, allowlist):
                errors.append(
                    "Changed-files audit found out-of-allowlist path: "
                    f"{path}. Amend the OBPI or revert the change."
                )
        return errors

    def _is_foundation_series(self, adr_id: str) -> bool:
        """Return True if the ADR belongs to the 0.0.x foundation series."""
        return bool(re.match(r"^ADR-0\.0\.\d+", adr_id))

    def _section_body(self, content: str, heading: str) -> str | None:
        """Return the body of an H2/H3 section when present."""
        return section_body(content, heading)

    def _is_placeholder(self, text: str) -> bool:
        """Return True if text consists only of placeholder tokens."""
        clean = text.strip().lower()
        if not clean:
            return True
        return clean in STRICT_PLACEHOLDERS or any(p in clean for p in ["paste", "one-sentence"])

    def _has_substantive_summary(self, content: str) -> bool:
        """Check for substantive bullets in the Implementation Summary."""
        match = re.search(
            r"^### Implementation Summary\s*$([\s\S]*?)(?:^### |\n---|\Z)",
            content,
            flags=re.MULTILINE,
        )
        if not match:
            return False

        section = match.group(1)
        bullets = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
        if not bullets:
            bullets = re.findall(r"^- \s*(.+)$", section, flags=re.MULTILINE)

        substantive_count = 0
        for bullet in bullets:
            if not self._is_placeholder(bullet):
                substantive_count += 1

        return substantive_count > 0

    def _has_substantive_section(self, content: str, section_name: str) -> bool:
        """Check if a specific section has substantive content beyond the header."""
        body = self._section_body(content, section_name)
        if body is None:
            return False
        return not self._is_placeholder(body)

    def _validate_human_attestation(self, content: str) -> list[str]:
        """Validate the existence and content of the human attestation block."""
        errors = []

        body = self._section_body(content, "Human Attestation")
        if body is None:
            return ["Heavy/Foundation OBPI requires a '## Human Attestation' section."]

        attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestor_match or not attestor_match.group(1).lower().startswith("human:"):
            errors.append("Human attestation block requires 'Attestor: human:<name>'.")
        elif self._is_placeholder(attestor_match.group(1).partition(":")[2]):
            errors.append("Human attestor name cannot be a placeholder.")

        attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestation_match or self._is_placeholder(attestation_match.group(1)):
            errors.append("Human attestation block requires substantive 'Attestation' text.")

        date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})$", body, flags=re.MULTILINE)
        if not date_match:
            errors.append("Human attestation block requires 'Date: YYYY-MM-DD'.")

        return errors
