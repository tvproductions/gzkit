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

# Template defaults emitted by OBPI scaffolding that indicate
# a brief was auto-generated but never authored.
TEMPLATE_SCAFFOLD_MARKERS: dict[str, list[str]] = {
    "Allowed Paths": ["src/module/"],
    "Requirements (FAIL-CLOSED)": ["First constraint", "Second constraint"],
    "Acceptance Criteria": ["Given/When/Then behavior criterion"],
    "Discovery Checklist": [
        "path/to/prerequisite",
        "config/file.json",
        "path/to/exemplar",
        "tests/path/to/similar_tests.py",
    ],
    "Verification": ["command --to --verify"],
}


# GHI #194: brief-prescribed gz commands must resolve against the registered
# parser. The pattern matches `(uv run )?gz <verb-chain>` where the chain is
# one or more lowercase verb tokens. Whitespace is `[ \t]` (not `\s`) so the
# chain cannot span newlines — each prescribed command is one line. The
# extractor confines matching to backtick-inline and fenced-code contexts so
# prose mentions like "transcribe gz commands" are not interpreted as
# prescriptive invocations.
_GZ_COMMAND_PATTERN = re.compile(
    r"(?:uv run[ \t]+)?\bgz[ \t]+([a-z][a-z-]*(?:[ \t]+[a-z][a-z-]*)*)",
)
_INLINE_CODE_PATTERN = re.compile(r"`([^`\n]+)`")
_FENCED_BLOCK_PATTERN = re.compile(r"```[a-z]*\n(.*?)\n```", flags=re.DOTALL)


def extract_gz_command_chains(content: str) -> list[list[str]]:
    """Extract every `gz <verb> [<verb>...]` chain from brief code segments.

    Scans inline code (\\`...\\`) and fenced code blocks (\\`\\`\\`...\\`\\`\\`)
    only — prose mentions are ignored by design (brief authors quote
    prescriptive commands; prose references are descriptive). Used by
    ObpiValidator._validate_command_shapes to verify each chain resolves
    against the registered CLI parser tree (GHI #194).
    """
    chains: list[list[str]] = []
    code_segments = _INLINE_CODE_PATTERN.findall(content) + _FENCED_BLOCK_PATTERN.findall(content)
    for segment in code_segments:
        for line in segment.splitlines():
            for match in _GZ_COMMAND_PATTERN.finditer(line):
                chain = match.group(1).split()
                if chain:
                    chains.append(chain)
    return chains


def verify_gz_chain(verbs: list[str]) -> tuple[bool, str]:
    """Walk a verb chain through the gz parser tree.

    Returns ``(ok, reason)``. The walk advances through subparser levels;
    when the current level has no further subparsers (a leaf verb), the
    remaining tokens are treated as positional arguments (e.g.
    ``gz chores run frontmatter-ledger-coherence`` resolves at ``run`` and
    the slug is a positional). Verbs at intermediate levels MUST be
    registered choices — typos fail closed.
    """
    import argparse  # noqa: PLC0415

    from gzkit.cli.main import _get_parser  # noqa: PLC0415

    parser = _get_parser()
    current: argparse.ArgumentParser = parser
    walked: list[str] = []
    for verb in verbs:
        sub_action = next(
            (a for a in current._actions if isinstance(a, argparse._SubParsersAction)),
            None,
        )
        if sub_action is None:
            # Current parser is a leaf; remaining tokens are positional args.
            return True, f"resolved 'gz {' '.join(walked)}'"
        if verb not in sub_action.choices:
            available = sorted(sub_action.choices.keys())
            sample = ", ".join(available[:8])
            suffix = "..." if len(available) > 8 else ""
            prefix = f"'gz {' '.join(walked)}'" if walked else "'gz'"
            return False, (
                f"{prefix} — '{verb}' is not a registered subcommand at "
                f"this level (available: {sample}{suffix})"
            )
        walked.append(verb)
        # argparse _SubParsersAction.choices values are ArgumentParser at runtime
        # but the stub types them as object; safe cast based on isinstance check above.
        next_parser = sub_action.choices[verb]
        if not isinstance(next_parser, argparse.ArgumentParser):
            return True, f"resolved 'gz {' '.join(walked)}' (leaf choice)"
        current = next_parser
    return True, f"resolved 'gz {' '.join(walked)}'"


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

    def validate_file(self, obpi_path: Path, *, require_authored: bool = False) -> list[str]:
        """Validate an OBPI file for completion readiness.

        Returns a list of error messages (empty if valid).
        """
        if not obpi_path.exists():
            return [f"File not found: {obpi_path}"]

        content = obpi_path.read_text(encoding="utf-8")
        return self.validate_content(content, require_authored=require_authored)

    def validate_content(self, content: str, *, require_authored: bool = False) -> list[str]:
        """Validate OBPI markdown content without requiring a file on disk."""
        from gzkit.ledger import (
            parse_frontmatter_value,
            resolve_adr_lane,
        )

        status = (parse_frontmatter_value(content, "status") or "").strip().lower()

        # Check for template scaffold on any status — these indicate a brief
        # was auto-generated but never authored.  GHI #27.
        scaffold_warnings = self._detect_template_scaffold(content)
        scaffold_warnings.extend(self._detect_lane_section_mismatch(content))
        if status != "completed" and not require_authored:
            return scaffold_warnings

        errors = list(scaffold_warnings)
        if require_authored:
            errors.extend(self._validate_authored_readiness(content))
            if status != "completed":
                return errors

        # 1. Resolve Lane Inheritance
        parent_id = parse_frontmatter_value(content, "parent")
        if not parent_id:
            errors.append("Missing 'parent' ADR in frontmatter.")
            return errors

        graph = self.ledger.get_artifact_graph()
        parent_info = graph.get(self.ledger.canonicalize_id(parent_id), {})
        lane = resolve_adr_lane(parent_info, self.config.mode)

        # GHI #66: Check if OBPI is ledger-completed to use sealed scope evidence
        obpi_id = parse_frontmatter_value(content, "id")
        obpi_info = graph.get(self.ledger.canonicalize_id(obpi_id), {}) if obpi_id else {}
        ledger_completed = obpi_info.get("ledger_completed", False)

        allowlist = extract_allowed_paths(content)
        if not allowlist:
            errors.append("Missing or empty 'Allowed Paths' allowlist.")
        else:
            if ledger_completed:
                completion_evidence = obpi_info.get("latest_completion_evidence") or {}
                scope_audit = normalize_scope_audit(completion_evidence.get("scope_audit"))
                changed_files = scope_audit.get("changed_files", []) if scope_audit else []
            else:
                changed_files = collect_changed_files(self.project_root)
            errors.extend(self._validate_changed_files(changed_files, allowlist))

        if not ledger_completed:
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

    def _validate_authored_readiness(self, content: str) -> list[str]:
        """Validate that a brief is authored enough for execution planning."""
        errors: list[str] = []

        if not self._has_substantive_section(content, "Objective"):
            errors.append("Missing or non-substantive 'Objective' for authored readiness.")

        allowlist = extract_allowed_paths(content)
        if not allowlist:
            errors.append("Missing or empty 'Allowed Paths' for authored readiness.")

        denied_paths = self._section_body(content, "Denied Paths")
        if denied_paths is None or not self._has_bullet_items(denied_paths):
            errors.append("Missing 'Denied Paths' exclusions for authored readiness.")

        requirements = self._section_body(content, "Requirements (FAIL-CLOSED)")
        if requirements is None or not re.search(r"^\d+\.\s+", requirements, flags=re.MULTILINE):
            errors.append("Missing numbered 'Requirements (FAIL-CLOSED)' for authored readiness.")

        discovery = self._section_body(content, "Discovery Checklist")
        if discovery is None:
            errors.append("Missing 'Discovery Checklist' for authored readiness.")
        else:
            if not self._has_substantive_checklist_block(
                discovery,
                start_label="**Prerequisites",
                end_label="**Existing Code",
            ):
                errors.append(
                    "Discovery Checklist is missing substantive 'Prerequisites' entries "
                    "for authored readiness."
                )
            if not self._has_substantive_checklist_block(
                discovery,
                start_label="**Existing Code",
                end_label=None,
            ):
                errors.append(
                    "Discovery Checklist is missing substantive 'Existing Code' entries "
                    "for authored readiness."
                )

        verification = self._section_body(content, "Verification")
        if verification is None or not self._has_specific_verification_command(verification):
            errors.append(
                "Verification must include at least one OBPI-specific "
                "command for authored readiness."
            )

        acceptance = self._section_body(content, "Acceptance Criteria")
        if acceptance is None or "REQ-" not in acceptance:
            errors.append(
                "Acceptance Criteria must include at least one deterministic REQ ID "
                "for authored readiness."
            )

        errors.extend(self._validate_command_shapes(content))

        return errors

    def _validate_command_shapes(self, content: str) -> list[str]:
        """Verify every brief-prescribed `gz X Y Z` invocation resolves (GHI #194).

        Closes the class-of-failure where brief authors transcribe an
        unregistered verb chain (e.g. singular ``gz chore run`` instead of
        plural ``gz chores run``) and the agent only discovers the typo at
        pipeline runtime. Each unique chain is verified once against the
        cached parser tree.
        """
        errors: list[str] = []
        chains = extract_gz_command_chains(content)
        seen: set[tuple[str, ...]] = set()
        for chain in chains:
            key = tuple(chain)
            if key in seen:
                continue
            seen.add(key)
            ok, reason = verify_gz_chain(chain)
            if not ok:
                errors.append(f"Brief command-shape error: {reason}")
        return errors

    def _detect_template_scaffold(self, content: str) -> list[str]:
        """Detect auto-generated template defaults that were never authored.

        Returns a list of warnings identifying which sections still contain
        the scaffold defaults emitted by OBPI template scaffolding.
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

    def _detect_lane_section_mismatch(self, content: str) -> list[str]:
        """Detect body/frontmatter lane contradictions."""
        from gzkit.ledger import parse_frontmatter_value

        warnings: list[str] = []
        frontmatter_lane = (parse_frontmatter_value(content, "lane") or "").strip().lower()
        if not frontmatter_lane:
            return warnings

        lane_body = self._section_body(content, "Lane")
        if lane_body is None:
            return warnings

        expected = "**Heavy**" if frontmatter_lane == "heavy" else "**Lite**"
        opposite = "**Lite**" if frontmatter_lane == "heavy" else "**Heavy**"
        lane_intro = lane_body.splitlines()[0].strip() if lane_body.splitlines() else ""
        if opposite in lane_intro or expected not in lane_intro:
            warnings.append(
                "Lane section body does not match frontmatter lane: "
                f"frontmatter='{frontmatter_lane}', lane_section='{lane_intro}'."
            )
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

    def _has_bullet_items(self, body: str) -> bool:
        """Return True when a section body contains at least one bullet item."""
        return bool(re.search(r"^\s*-\s+", body, flags=re.MULTILINE))

    def _checklist_items(self, block: str) -> list[str]:
        """Extract checklist bullet text from a discovery subsection."""
        items: list[str] = []
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped.startswith("-"):
                continue
            item = re.sub(r"^-\s*(\[[ xX]\]\s*)?", "", stripped).strip()
            if item:
                items.append(item)
        return items

    def _discovery_block(
        self,
        body: str,
        *,
        start_label: str,
        end_label: str | None,
    ) -> str:
        """Extract the lines between two bold discovery labels."""
        start = body.find(start_label)
        if start == -1:
            return ""
        remainder = body[start + len(start_label) :]
        if end_label:
            end = remainder.find(end_label)
            if end != -1:
                return remainder[:end]
        return remainder

    def _has_substantive_checklist_block(
        self,
        body: str,
        *,
        start_label: str,
        end_label: str | None,
    ) -> bool:
        """Return True when a discovery subsection has at least one real item."""
        block = self._discovery_block(body, start_label=start_label, end_label=end_label)
        items = self._checklist_items(block)
        if not items:
            return False
        return any(not self._is_placeholder(item) for item in items)

    def _has_specific_verification_command(self, body: str) -> bool:
        """Return True when verification includes an OBPI-specific command."""
        baseline = {
            "uv run gz validate --documents",
            "uv run gz lint",
            "uv run gz typecheck",
            "uv run gz test",
        }
        commands: list[str] = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("```"):
                continue
            commands.append(stripped)
        if not commands:
            return False
        return any(command not in baseline for command in commands)

    def _validate_human_attestation(self, content: str) -> list[str]:
        """Validate the existence and content of the human attestation block."""
        errors = []

        body = self._section_body(content, "Human Attestation")
        if body is None:
            return ["Heavy/Foundation OBPI requires a '## Human Attestation' section."]

        attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestor_match or self._is_placeholder(attestor_match.group(1).strip().strip("`")):
            errors.append("Human attestor name cannot be empty or a placeholder.")

        attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
        if not attestation_match or self._is_placeholder(attestation_match.group(1)):
            errors.append("Human attestation block requires substantive 'Attestation' text.")

        date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})$", body, flags=re.MULTILINE)
        if not date_match:
            errors.append("Human attestation block requires 'Date: YYYY-MM-DD'.")

        return errors
