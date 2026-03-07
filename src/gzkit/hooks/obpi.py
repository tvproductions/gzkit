"""OBPI completion validator engine.

Enforces evidence and human attestation requirements for OBPI transitions.
"""

import re
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger

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


class ObpiValidator:
    """Validates OBPI brief content against governance requirements."""

    def __init__(self, project_root: Path):
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

        # Only enforce completion rules if status is 'completed'
        if status != "completed":
            return []

        errors = []

        # 1. Resolve Lane Inheritance
        parent_id = parse_frontmatter_value(content, "parent")
        if not parent_id:
            errors.append("Missing 'parent' ADR in frontmatter.")
            return errors

        graph = self.ledger.get_artifact_graph()
        parent_info = graph.get(self.ledger.canonicalize_id(parent_id), {})
        lane = resolve_adr_lane(parent_info, self.config.mode)

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

    def _is_foundation_series(self, adr_id: str) -> bool:
        """Return True if the ADR belongs to the 0.0.x foundation series."""
        return bool(re.match(r"^ADR-0\.0\.\d+", adr_id))

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
        # Look for bullet points with content
        bullets = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
        if not bullets:
            # Fallback to simple bullets if no key:value pairs
            bullets = re.findall(r"^- \s*(.+)$", section, flags=re.MULTILINE)

        substantive_count = 0
        for b in bullets:
            if not self._is_placeholder(b):
                substantive_count += 1

        return substantive_count > 0

    def _has_substantive_section(self, content: str, section_name: str) -> bool:
        """Check if a specific section has substantive content beyond the header."""
        pattern = rf"^## {re.escape(section_name)}\s*$([\s\S]*?)(?:^## |\n---|\Z)"
        match = re.search(pattern, content, flags=re.MULTILINE)
        if not match:
            # Try H3
            pattern = rf"^### {re.escape(section_name)}\s*$([\s\S]*?)(?:^### |\n---|\Z)"
            match = re.search(pattern, content, flags=re.MULTILINE)

        if not match:
            return False

        body = match.group(1).strip()
        return not self._is_placeholder(body)

    def _validate_human_attestation(self, content: str) -> list[str]:
        """Validate the existence and content of the human attestation block."""
        errors = []

        # Check for Human Attestation Section
        pattern = r"^## Human Attestation\s*$([\s\S]*?)(?:^## |\n---|\Z)"
        match = re.search(pattern, content, flags=re.MULTILINE)
        if not match:
            return ["Heavy/Foundation OBPI requires a '## Human Attestation' section."]

        body = match.group(1)

        # Validate Attestor
        attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestor_match or not attestor_match.group(1).lower().startswith("human:"):
            errors.append("Human attestation block requires 'Attestor: human:<name>'.")
        elif self._is_placeholder(attestor_match.group(1).partition(":")[2]):
            errors.append("Human attestor name cannot be a placeholder.")

        # Validate Attestation Text
        attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestation_match or self._is_placeholder(attestation_match.group(1)):
            errors.append("Human attestation block requires substantive 'Attestation' text.")

        # Validate Date
        date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})$", body, flags=re.MULTILINE)
        if not date_match:
            errors.append("Human attestation block requires 'Date: YYYY-MM-DD'.")

        return errors
