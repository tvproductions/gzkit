"""Presentation layer for complexity advisor diagnoses (OBPI-0.0.29-06).

Exports two presenter classes for formatting AdvisorDiagnosis lists:
- :class:`AdHocPresenter` — verbose output with doctrinal excerpts and source snippets.
- :class:`AutoChainPresenter` — concise one-line output per diagnosis.
- :class:`Presenter` — Protocol defining the render contract.

Both presenters follow the standard interface:
    render(diagnoses: list[AdvisorDiagnosis], metrics_checked: int = 0,
           functions_checked: int = 0) -> str
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis

__all__ = [
    "Presenter",
    "AdHocPresenter",
    "AutoChainPresenter",
]


@runtime_checkable
class Presenter(Protocol):
    """Protocol defining the presenter contract for diagnosis rendering."""

    def render(
        self,
        diagnoses: list[AdvisorDiagnosis],
        metrics_checked: int = 0,
        functions_checked: int = 0,
    ) -> str:
        """Render a list of diagnoses to a formatted string.

        Args:
            diagnoses: List of AdvisorDiagnosis objects to render.
            metrics_checked: Number of metrics checked (for reporting).
            functions_checked: Number of functions checked (for reporting).

        Returns:
            Formatted output string.

        """
        ...


class AdHocPresenter:
    """Verbose presenter for ad-hoc complexity diagnosis output.

    Includes full doctrinal frame, source code snippets, and all diagnosis
    details. Used when operator requests detailed analysis.
    """

    def render(
        self,
        diagnoses: list[AdvisorDiagnosis],
        metrics_checked: int = 0,
        functions_checked: int = 0,
    ) -> str:
        """Render diagnoses with full detail (doctrinal frame, source snippets).

        Args:
            diagnoses: List of AdvisorDiagnosis objects to render.
            metrics_checked: Number of metrics checked.
            functions_checked: Number of functions checked.

        Returns:
            Verbose formatted output; "no crossings" message if diagnoses empty.

        """
        if not diagnoses:
            return (
                f"No crossings detected. "
                f"Checked {metrics_checked} metrics across "
                f"{functions_checked} functions."
            )

        lines: list[str] = []
        for diagnosis in diagnoses:
            lines.append(self._format_diagnosis(diagnosis))

        return "\n".join(lines)

    def _format_diagnosis(self, diagnosis: AdvisorDiagnosis) -> str:
        """Format a single diagnosis with full detail.

        Args:
            diagnosis: The diagnosis to format.

        Returns:
            Multi-line formatted string for this diagnosis.

        """
        parts: list[str] = []

        # Header with metric, band, value, archetype
        parts.append(
            f"Metric: {diagnosis.metric} | "
            f"Band: {diagnosis.crossing_band} | "
            f"Value: {diagnosis.crossing_value} | "
            f"Archetype: {diagnosis.archetype}"
        )

        # Doctrinal frame (authority, citation, excerpt)
        parts.append(
            f"Authority: {diagnosis.doctrinal_frame.authority}\n"
            f"Citation: {diagnosis.doctrinal_frame.citation}\n"
            f"Excerpt: {diagnosis.doctrinal_frame.excerpt}"
        )

        # Recommended move
        parts.append(f"Recommended: {diagnosis.recommended_move}")

        # Proof ranges with source code snippets
        for proof in diagnosis.proof:
            snippet = self._read_source_snippet(proof.file_path, proof.start_line, proof.end_line)
            parts.append(
                f"File: {proof.file_path} "
                f"(lines {proof.start_line}-{proof.end_line}, {proof.ast_node_kind})\n"
                f"{snippet}"
            )

        # Intrinsic attestation if present
        if diagnosis.intrinsic_attestation:
            parts.append(f"Attestation: {diagnosis.intrinsic_attestation.attestation_id}")

        return "\n".join(parts)

    def _read_source_snippet(self, file_path: str, start_line: int, end_line: int) -> str:
        """Read source code lines from file.

        Args:
            file_path: Path to the source file.
            start_line: First line to read (1-indexed inclusive).
            end_line: Last line to read (1-indexed inclusive).

        Returns:
            Formatted source code snippet or fallback message.

        """
        try:
            path = Path(file_path)
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()

            # Convert 1-indexed to 0-indexed
            start_idx = start_line - 1
            end_idx = end_line

            # Clamp to file bounds
            start_idx = max(0, start_idx)
            end_idx = min(len(lines), end_idx)

            if start_idx >= len(lines):
                return "<source unavailable>"

            selected = lines[start_idx:end_idx]
            return "\n".join(selected)
        except FileNotFoundError:
            return "<source unavailable>"


class AutoChainPresenter:
    """Concise presenter for auto-chain complexity diagnosis output.

    Produces one-line summaries per diagnosis without doctrinal excerpts.
    Includes a hint to run ad-hoc for full detail.
    """

    def render(
        self,
        diagnoses: list[AdvisorDiagnosis],
        metrics_checked: int = 0,
        functions_checked: int = 0,
    ) -> str:
        """Render diagnoses with concise one-line summary.

        Args:
            diagnoses: List of AdvisorDiagnosis objects to render.
            metrics_checked: Number of metrics checked (unused in auto-chain).
            functions_checked: Number of functions checked (unused in auto-chain).

        Returns:
            Concise formatted output (empty string if no diagnoses).

        """
        if not diagnoses:
            return ""

        lines: list[str] = []
        for diagnosis in diagnoses:
            lines.append(self._format_diagnosis_oneline(diagnosis))

        # Add hint to run ad-hoc for full detail
        lines.append("Run `gz complexity advise <path>` for full detail.")

        return "\n".join(lines)

    def _format_diagnosis_oneline(self, diagnosis: AdvisorDiagnosis) -> str:
        """Format a single diagnosis as one-line summary.

        Args:
            diagnosis: The diagnosis to format.

        Returns:
            One-line summary (no doctrinal excerpt).

        """
        return (
            f"{diagnosis.metric} {diagnosis.crossing_band} "
            f"({diagnosis.crossing_value}): "
            f"{diagnosis.archetype} -> {diagnosis.recommended_move}"
        )
