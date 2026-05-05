"""Handler for ``gz complexity distill`` (GHI #400).

Wraps the OBPI-0.0.27-04 distillation engine
(:mod:`gzkit.complexity.distillation`) and OBPI-0.0.27-03 measurement
pipeline (:mod:`gzkit.complexity.measurement`) for ad-hoc operator
invocation. The destination CLI verb declared (deferred) by
``.gzkit/skills/gz-complexity-distill/SKILL.md``; this module is the
landing site that closes the deferral and the waiver path.

Output Contract (binding via ``REQ-0.0.27-06-04``): a human-readable
progress summary on stdout naming the corpus revision under measurement,
the baseline artifact path produced, the destination distilled-document
path written, and the count of per-metric sections rendered.

Exit codes (binding):

- ``0`` clean run.
- ``1`` user/config error (bad ``--today``, missing corpus, bad baseline JSON).
- ``2`` system/IO error (measurement tool missing, write failure).
- ``3`` policy breach — would overwrite an existing same-date document
  (REQ-0.0.27-04-05 no-overwrite guard) without ``--allow-dated-sibling``.
"""

from __future__ import annotations

import json
import sys
from datetime import date as DateClass
from pathlib import Path

from pydantic import ValidationError

from gzkit.complexity.baseline import BaselineArtifact
from gzkit.complexity.distillation import DocumentExistsError, render_document
from gzkit.complexity.measurement import (
    CANONICAL_METRICS,
    CorpusLoaderError,
    MissingMeasurementToolError,
    WholeProjectMeasurementRejectedError,
    measure_corpus,
    safe_load_corpus,
)

DEFAULT_CORPUS_PATH = Path("data/exemplar_corpus.json")
DEFAULT_OUTPUT_DIR = Path("docs/governance/complexity")


def complexity_distill_cmd(
    *,
    corpus: str | None = None,
    baseline_json: str | None = None,
    output_dir: str | None = None,
    baseline_dir: str | None = None,
    prior: str | None = None,
    no_prior: bool = False,
    allow_dated_sibling: bool = False,
    today_override: str | None = None,
) -> int:
    """Compose measurement + distillation render; emit Output Contract summary.

    Returns ``0`` on success and ``raise SystemExit(code)`` for non-zero exits
    so the CLI dispatcher (which discards handler return values) sees the
    correct process exit status. Tests can collapse both paths by catching
    ``SystemExit`` and reading ``exc.code`` (justify_cmd precedent).
    """
    try:
        today = _resolve_today(today_override)
    except ValueError as exc:
        print(f"error: invalid --today value: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    base_dir = Path(baseline_dir) if baseline_dir else out_dir / "baselines" / today.isoformat()

    try:
        baseline_artifact_path, baseline = _resolve_baseline(
            corpus_arg=corpus, baseline_json_arg=baseline_json, baseline_output_dir=base_dir
        )
    except (FileNotFoundError, CorpusLoaderError, ValidationError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except (MissingMeasurementToolError, WholeProjectMeasurementRejectedError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    prior_path = _resolve_prior(prior=prior, no_prior=no_prior, output_dir=out_dir, today=today)

    try:
        document_path = render_document(
            baseline=baseline,
            baseline_artifact_path=baseline_artifact_path,
            prior_distillation_path=prior_path,
            output_dir=out_dir,
            today=today,
            allow_dated_sibling=allow_dated_sibling,
        )
    except DocumentExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(3) from exc
    except OSError as exc:
        print(f"error: write failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    _print_summary(
        baseline=baseline,
        baseline_artifact_path=baseline_artifact_path,
        document_path=document_path,
    )
    return 0


def _resolve_today(today_override: str | None) -> DateClass:
    """Return today's date or parse ``today_override`` as ``YYYY-MM-DD``."""
    if today_override is None:
        return DateClass.today()
    return DateClass.fromisoformat(today_override)


def _resolve_baseline(
    *, corpus_arg: str | None, baseline_json_arg: str | None, baseline_output_dir: Path
) -> tuple[Path, BaselineArtifact]:
    """Return ``(baseline_artifact_path, baseline)`` from corpus or baseline JSON.

    ``--baseline-json PATH`` short-circuits measurement: the file is parsed
    directly and its path is reported as the baseline artifact path. This
    is the test-injection path; production runs use ``--corpus``.
    """
    if baseline_json_arg is not None:
        baseline_path = Path(baseline_json_arg)
        payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        return baseline_path, BaselineArtifact.model_validate(payload)
    corpus_path = Path(corpus_arg) if corpus_arg else DEFAULT_CORPUS_PATH
    corpus = safe_load_corpus(corpus_path)
    artifact = measure_corpus(corpus, baseline_output_dir)
    return baseline_output_dir / "baseline.json", artifact


def _resolve_prior(
    *, prior: str | None, no_prior: bool, output_dir: Path, today: DateClass
) -> Path | None:
    """Return the prior distillation path or ``None`` for cold-start."""
    if no_prior:
        return None
    if prior is not None:
        return Path(prior)
    return _find_latest_prior(output_dir=output_dir, today=today)


def _find_latest_prior(*, output_dir: Path, today: DateClass) -> Path | None:
    """Latest ``distilled-characteristics-*.md`` under *output_dir*, today excluded."""
    if not output_dir.is_dir():
        return None
    today_iso = today.isoformat()
    candidates = sorted(
        path
        for path in output_dir.glob("distilled-characteristics-*.md")
        if today_iso not in path.stem
    )
    return candidates[-1] if candidates else None


def _print_summary(
    *, baseline: BaselineArtifact, baseline_artifact_path: Path, document_path: Path
) -> None:
    """Emit the Output Contract summary lines (REQ-0.0.27-06-04)."""
    print("Distillation pass complete.")
    print(f"  Corpus revision: {baseline.corpus_revision}")
    print(f"  Baseline artifact: {baseline_artifact_path.as_posix()}")
    print(f"  Distilled document: {document_path.as_posix()}")
    print(f"  Per-metric sections rendered: {len(CANONICAL_METRICS)}")


__all__ = [
    "DEFAULT_CORPUS_PATH",
    "DEFAULT_OUTPUT_DIR",
    "complexity_distill_cmd",
]
