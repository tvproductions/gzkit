"""Insights surface — schema for `.gzkit/insights/agent-insights.jsonl`.

The file is a Layer-2 trust surface witnessing course-correction lessons
(AGENTS.md § Behavior Rules — Always #11) and observed defects. This
package locks its read-side schema; `gz validate --insights-shape`
enforces it (GHI #358).
"""

from gzkit.insights.model import InsightRecord, InsightType

__all__ = ["InsightRecord", "InsightType"]
