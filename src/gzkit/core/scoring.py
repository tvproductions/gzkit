"""Deterministic ADR decomposition helpers for OBPI planning and validation.

Extracted from gzkit.decomposition. All functions are pure domain logic.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict


class DecompositionScorecard(BaseModel):
    """Structured decomposition scorecard for one ADR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    data_state: int
    logic_engine: int
    interface: int
    observability: int
    lineage: int
    dimension_total: int
    baseline_min: int
    baseline_max: int | None
    baseline_selected: int
    split_single_narrative: int
    split_surface_boundary: int
    split_state_anchor: int
    split_testability_ceiling: int
    split_total: int
    final_target_obpi_count: int

    @property
    def baseline_range_label(self) -> str:
        """Render stable baseline range label."""
        if self.baseline_max is None:
            return f"{self.baseline_min}+"
        if self.baseline_min == self.baseline_max:
            return str(self.baseline_min)
        return f"{self.baseline_min}-{self.baseline_max}"

    def to_markdown(self) -> str:
        """Render scorecard block for ADR markdown templates."""
        lines = [
            "- Data/State: " + str(self.data_state),
            "- Logic/Engine: " + str(self.logic_engine),
            "- Interface: " + str(self.interface),
            "- Observability: " + str(self.observability),
            "- Lineage: " + str(self.lineage),
            "- Dimension Total: " + str(self.dimension_total),
            "- Baseline Range: " + self.baseline_range_label,
            "- Baseline Selected: " + str(self.baseline_selected),
            "- Split Single-Narrative: " + str(self.split_single_narrative),
            "- Split Surface Boundary: " + str(self.split_surface_boundary),
            "- Split State Anchor: " + str(self.split_state_anchor),
            "- Split Testability Ceiling: " + str(self.split_testability_ceiling),
            "- Split Total: " + str(self.split_total),
            "- Final Target OBPI Count: " + str(self.final_target_obpi_count),
        ]
        return "\n".join(lines)


def baseline_range_for_total(dimension_total: int) -> tuple[int, int | None]:
    """Map dimension score total to baseline OBPI range."""
    if dimension_total <= 3:
        return 1, 2
    if dimension_total <= 6:
        return 3, 3
    if dimension_total <= 8:
        return 4, 4
    return 5, None


def default_dimension_scores(lane: str, semver: str) -> dict[str, int]:
    """Return lane-aware default decomposition scores."""
    if semver.startswith("0.0."):
        default = 2
    elif lane == "heavy":
        default = 1
    else:
        default = 0
    return {
        "data_state": default,
        "logic_engine": default,
        "interface": default,
        "observability": default,
        "lineage": default,
    }


def _is_in_range(value: int, lower: int, upper: int | None) -> bool:
    if value < lower:
        return False
    if upper is None:
        return True
    return value <= upper


def compute_scorecard(
    *,
    data_state: int,
    logic_engine: int,
    interface: int,
    observability: int,
    lineage: int,
    split_single_narrative: int,
    split_surface_boundary: int,
    split_state_anchor: int,
    split_testability_ceiling: int,
    baseline_selected: int | None = None,
) -> DecompositionScorecard:
    """Compute deterministic scorecard totals and final OBPI target."""
    dimensions = {
        "Data/State": data_state,
        "Logic/Engine": logic_engine,
        "Interface": interface,
        "Observability": observability,
        "Lineage": lineage,
    }
    for label, value in dimensions.items():
        if value not in (0, 1, 2):
            msg = f"{label} score must be 0, 1, or 2 (got {value})."
            raise ValueError(msg)

    splits = {
        "Single-Narrative": split_single_narrative,
        "Surface Boundary": split_surface_boundary,
        "State Anchor": split_state_anchor,
        "Testability Ceiling": split_testability_ceiling,
    }
    for label, value in splits.items():
        if value not in (0, 1):
            msg = f"{label} split flag must be 0 or 1 (got {value})."
            raise ValueError(msg)

    dimension_total = sum(dimensions.values())
    baseline_min, baseline_max = baseline_range_for_total(dimension_total)
    selected = baseline_selected if baseline_selected is not None else baseline_min
    if not _is_in_range(selected, baseline_min, baseline_max):
        msg = (
            "Baseline selected must be inside computed baseline range "
            f"{baseline_min if baseline_max is None else f'{baseline_min}-{baseline_max}'}."
        )
        raise ValueError(msg)

    split_total = sum(splits.values())
    final_target = selected + split_total
    return DecompositionScorecard(
        data_state=data_state,
        logic_engine=logic_engine,
        interface=interface,
        observability=observability,
        lineage=lineage,
        dimension_total=dimension_total,
        baseline_min=baseline_min,
        baseline_max=baseline_max,
        baseline_selected=selected,
        split_single_narrative=split_single_narrative,
        split_surface_boundary=split_surface_boundary,
        split_state_anchor=split_state_anchor,
        split_testability_ceiling=split_testability_ceiling,
        split_total=split_total,
        final_target_obpi_count=final_target,
    )


def build_checklist_seed(semver: str, target_count: int) -> str:
    """Build deterministic checklist stub from final OBPI target count."""
    if target_count <= 0:
        msg = "Final target OBPI count must be positive."
        raise ValueError(msg)
    lines = [
        f"- [ ] OBPI-{semver}-{index:02d}: Define scope, constraints, and acceptance criteria"
        for index in range(1, target_count + 1)
    ]
    return "\n".join(lines)


def extract_markdown_section(content: str, section_title: str) -> str | None:
    """Extract a markdown section body for a given H2 title."""
    pattern = re.compile(
        rf"(?ms)^## {re.escape(section_title)}\n(.*?)(?=^## |\Z)",
    )
    match = pattern.search(content)
    if not match:
        return None
    return match.group(1).strip("\n")


def parse_checklist_items(content: str) -> list[str]:
    """Parse checklist checkbox items from ADR markdown."""
    section = extract_markdown_section(content, "Checklist")
    if section is None:
        return []

    item_re = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$")
    items: list[str] = []
    active_item: list[str] | None = None
    for raw_line in section.splitlines():
        line = raw_line.rstrip()
        match = item_re.match(line)
        if match:
            if active_item:
                normalized = re.sub(r"\s+", " ", " ".join(active_item)).strip()
                if normalized:
                    items.append(normalized)
            active_item = [match.group(1).strip()]
            continue
        if active_item is None:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        active_item.append(stripped)

    if active_item:
        normalized = re.sub(r"\s+", " ", " ".join(active_item)).strip()
        if normalized:
            items.append(normalized)

    return items


def _parse_baseline_range(label: str) -> tuple[int, int | None] | None:
    match = re.fullmatch(r"(\d+)-(\d+)", label.strip())
    if match:
        lower = int(match.group(1))
        upper = int(match.group(2))
        if lower <= upper:
            return lower, upper
        return None
    match = re.fullmatch(r"(\d+)\+", label.strip())
    if match:
        return int(match.group(1)), None
    match = re.fullmatch(r"(\d+)", label.strip())
    if match:
        value = int(match.group(1))
        return value, value
    return None


def parse_scorecard(content: str) -> tuple[DecompositionScorecard | None, list[str]]:
    """Parse and validate deterministic decomposition scorecard from ADR markdown."""
    section = extract_markdown_section(content, "Decomposition Scorecard")
    if section is None:
        return None, ["Missing required section: 'Decomposition Scorecard'."]

    key_values: dict[str, str] = {}
    key_re = re.compile(r"^\s*-\s*([^:]+):\s*(.+?)\s*$")
    for line in section.splitlines():
        match = key_re.match(line)
        if match:
            key_values[match.group(1).strip()] = match.group(2).strip()

    required_keys = (
        "Data/State",
        "Logic/Engine",
        "Interface",
        "Observability",
        "Lineage",
        "Dimension Total",
        "Baseline Range",
        "Baseline Selected",
        "Split Single-Narrative",
        "Split Surface Boundary",
        "Split State Anchor",
        "Split Testability Ceiling",
        "Split Total",
        "Final Target OBPI Count",
    )
    missing = [key for key in required_keys if key not in key_values]
    if missing:
        return None, [f"Decomposition scorecard missing key: {key}" for key in missing]

    errors: list[str] = []
    parsed_ints: dict[str, int] = {}
    int_keys = (
        "Data/State",
        "Logic/Engine",
        "Interface",
        "Observability",
        "Lineage",
        "Dimension Total",
        "Baseline Selected",
        "Split Single-Narrative",
        "Split Surface Boundary",
        "Split State Anchor",
        "Split Testability Ceiling",
        "Split Total",
        "Final Target OBPI Count",
    )
    for key in int_keys:
        raw = key_values[key]
        try:
            parsed_ints[key] = int(raw)
        except ValueError:
            errors.append(f"Decomposition scorecard '{key}' must be an integer (got '{raw}').")

    baseline_range = _parse_baseline_range(key_values["Baseline Range"])
    if baseline_range is None:
        errors.append("Decomposition scorecard 'Baseline Range' must be '<min>-<max>' or '<min>+'.")
    if errors:
        return None, errors

    try:
        card = compute_scorecard(
            data_state=parsed_ints["Data/State"],
            logic_engine=parsed_ints["Logic/Engine"],
            interface=parsed_ints["Interface"],
            observability=parsed_ints["Observability"],
            lineage=parsed_ints["Lineage"],
            split_single_narrative=parsed_ints["Split Single-Narrative"],
            split_surface_boundary=parsed_ints["Split Surface Boundary"],
            split_state_anchor=parsed_ints["Split State Anchor"],
            split_testability_ceiling=parsed_ints["Split Testability Ceiling"],
            baseline_selected=parsed_ints["Baseline Selected"],
        )
    except ValueError as exc:
        return None, [str(exc)]

    declared_range = baseline_range
    assert declared_range is not None
    computed_range = (card.baseline_min, card.baseline_max)
    if declared_range != computed_range:
        expected = card.baseline_range_label
        errors.append(
            "Decomposition scorecard 'Baseline Range' mismatch: "
            f"declared '{key_values['Baseline Range']}', expected '{expected}'."
        )
    if parsed_ints["Dimension Total"] != card.dimension_total:
        errors.append(
            "Decomposition scorecard 'Dimension Total' mismatch: "
            f"declared {parsed_ints['Dimension Total']}, expected {card.dimension_total}."
        )
    if parsed_ints["Split Total"] != card.split_total:
        errors.append(
            "Decomposition scorecard 'Split Total' mismatch: "
            f"declared {parsed_ints['Split Total']}, expected {card.split_total}."
        )
    if parsed_ints["Final Target OBPI Count"] != card.final_target_obpi_count:
        errors.append(
            "Decomposition scorecard 'Final Target OBPI Count' mismatch: "
            f"declared {parsed_ints['Final Target OBPI Count']}, "
            f"expected {card.final_target_obpi_count}."
        )

    if errors:
        return None, errors
    return card, []
