"""ADR and OBPI dimension scoring functions for the evaluation engine."""

import re
import statistics
from pathlib import Path

from gzkit.adr_eval import (
    ADR_WEIGHTS,
    DimensionScore,
    ObpiDimensionScores,
    _has_keywords,
    _passes_to_score,
    _word_count,
)
from gzkit.hooks.obpi import TEMPLATE_SCAFFOLD_MARKERS, section_body
from gzkit.qc_binding import register_advisory_qc_step

# ---------------------------------------------------------------------------
# Structural-completeness signals (ADR-0.0.73 / OBPI-07, GHI #624)
# ---------------------------------------------------------------------------
#
# HONESTY CONTRACT: every helper and dimension scorer in this module grades
# STRUCTURAL COMPLETENESS only — section presence, depth, the presence of
# concrete references, the presence of a rejected-alternatives or negative-
# consequences subsection. NONE of them grades decision SUBSTANCE (whether the
# problem is genuinely understood or the decision genuinely justified). Substance
# is a semantic judgment no regex/word-count can make; it lives in the separate
# judge-graded channel (`gzkit.adr_eval_substance`) and is UNGRADED absent a
# recorded judge verdict. The prior code CLAIMED these signals graded substance
# (GHI #624 facade) — that claim is removed. A structural signal is a weak
# positive presence indicator, never a substance verdict.

# Structural presence of concrete referents: code spans, file paths, governance
# IDs. Presence is a completeness signal, NOT evidence the claims are sound.
_CONCRETE_REF_RE = re.compile(
    r"`[^`]+`|\bsrc/|\btests/|\bdocs/|\bGHI #\d|\bOBPI-|\bADR-|\bPRD-|\bREQ-"
)

# Structural presence of weighed-contrast language in an Alternatives section.
_REJECTION_RE = re.compile(
    r"\b(reject|instead|rather than|chosen over|in favor of|trade-?off|discard)",
    re.IGNORECASE,
)

# Structural presence of downside language or a ### Negative subsection.
_NEGATIVE_CONSEQUENCE_RE = re.compile(
    r"###\s+Negative|\b(downside|trade-?off|cost|risk|limitation|drawback|regress)",
    re.IGNORECASE,
)


def _references_concrete_artifacts(text: str) -> bool:
    """Structural signal: section contains concrete referents (presence only)."""
    return bool(_CONCRETE_REF_RE.search(text))


def _substantive_sentence_count(text: str) -> int:
    """Count sentences over 8 words — a structural depth signal, not substance."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return sum(1 for sentence in sentences if _word_count(sentence) > 8)


def _has_rejected_alternatives_subsection(alternatives: str) -> bool:
    """Structural signal: an Alternatives section of real length names rejections."""
    return _word_count(alternatives) > 15 and bool(_REJECTION_RE.search(alternatives))


def _has_negative_consequences_subsection(consequences: str) -> bool:
    """Structural signal: a Consequences section names downsides (presence only)."""
    return bool(_NEGATIVE_CONSEQUENCE_RE.search(consequences))


# ---------------------------------------------------------------------------
# ADR dimension scoring (deterministic)
# ---------------------------------------------------------------------------


def _score_problem_clarity(content: str) -> tuple[int, list[str]]:
    """Score STRUCTURAL COMPLETENESS of the Intent section (NOT substance, GHI #624).

    The four checks are presence signals only: the Intent exists, has depth
    (word count), contains concrete references, and contains multiple longer
    sentences. A high score means the Problem section is structurally complete —
    it does NOT mean the problem is clearly understood. That substance judgment
    is UNGRADED here and belongs to the judge channel (gzkit.adr_eval_substance).
    """
    findings: list[str] = []
    intent = section_body(content, "Intent")
    checks = 0
    total = 4
    if intent:
        checks += 1
    else:
        findings.append("Missing ## Intent section")
    if intent and _word_count(intent) > 120:
        checks += 1
    else:
        findings.append("Intent section is short (<120 words)")
    if intent and _references_concrete_artifacts(intent):
        checks += 1
    else:
        findings.append("Intent contains no concrete references (code, path, or issue)")
    if intent and _substantive_sentence_count(intent) >= 2:
        checks += 1
    else:
        findings.append("Intent has fewer than two longer (>8-word) sentences")
    return _passes_to_score(checks, total), findings


def _score_decision_justification(content: str) -> tuple[int, list[str]]:
    """Score STRUCTURAL COMPLETENESS of the Decision section (NOT substance, GHI #624).

    The four checks are presence signals only: the Decision exists, has depth,
    an Alternatives section names rejections, and a Consequences section names
    downsides. A high score means the Decision is structurally complete — it does
    NOT mean the decision is well justified. That substance judgment is UNGRADED
    here and belongs to the judge channel (gzkit.adr_eval_substance).
    """
    findings: list[str] = []
    decision = section_body(content, "Decision")
    checks = 0
    total = 4
    if decision:
        checks += 1
    else:
        findings.append("Missing ## Decision section")
    if decision and _word_count(decision) > 100:
        checks += 1
    else:
        findings.append("Decision section is short (<100 words)")
    alternatives = section_body(content, "Alternatives Considered")
    if alternatives and _has_rejected_alternatives_subsection(alternatives):
        checks += 1
    else:
        findings.append("No Alternatives section naming explicit rejections")
    consequences = section_body(content, "Consequences")
    if consequences and _has_negative_consequences_subsection(consequences):
        checks += 1
    else:
        findings.append("No Consequences section naming downsides")
    return _passes_to_score(checks, total), findings


def _count_checklist_items(content: str) -> list[str]:
    checklist = section_body(content, "Checklist")
    if not checklist:
        return []
    return re.findall(r"^- \[[ x]\] (.+)$", checklist, re.MULTILINE)


def _score_feature_checklist(content: str, obpi_count: int) -> tuple[int, list[str]]:
    findings: list[str] = []
    items = _count_checklist_items(content)
    checks = 0
    total = 4
    if items:
        checks += 1
    else:
        findings.append("Missing or empty ## Checklist section")
    if items and all(re.match(r"OBPI-", item) for item in items):
        checks += 1
    else:
        findings.append("Checklist items not prefixed with OBPI-")
    if items and len(items) == obpi_count:
        checks += 1
    else:
        findings.append(f"Checklist count ({len(items)}) != OBPI file count ({obpi_count})")
    if len(items) >= 2:
        word_counts = [_word_count(i) for i in items]
        mean_wc = statistics.mean(word_counts)
        if mean_wc > 0 and statistics.stdev(word_counts) / mean_wc < 0.5:
            checks += 1
        else:
            findings.append("Checklist items have inconsistent granularity")
    elif items:
        checks += 1
    return _passes_to_score(checks, total), findings


def _score_obpi_decomposition(
    obpi_paths: list[Path], obpi_contents: list[str]
) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 4

    if obpi_paths:
        checks += 1
    else:
        findings.append("No OBPI brief files found")

    # Numbering gaps
    numbers = []
    for p in obpi_paths:
        m = re.search(r"OBPI-[\d.]+-(\d+)", p.stem)
        if m:
            numbers.append(int(m.group(1)))
    if numbers and numbers == list(range(1, len(numbers) + 1)):
        checks += 1
    else:
        findings.append("OBPI numbering has gaps")

    # Scaffold detection
    scaffold_count = 0
    for content in obpi_contents:
        for markers in TEMPLATE_SCAFFOLD_MARKERS.values():
            if any(marker in content for marker in markers):
                scaffold_count += 1
                break
    if scaffold_count == 0:
        checks += 1
    else:
        findings.append(f"{scaffold_count}/{len(obpi_paths)} OBPIs contain scaffold")

    # Distinct paths
    all_paths: list[set[str]] = []
    for content in obpi_contents:
        ap = section_body(content, "Allowed Paths") or ""
        paths = set(re.findall(r"`([^`]+)`", ap))
        all_paths.append(paths)
    if (
        len(all_paths) >= 2
        and all(
            len(a & b) / max(len(a | b), 1) < 0.5
            for i, a in enumerate(all_paths)
            for b in all_paths[i + 1 :]
            if a and b
        )
        or len(all_paths) <= 1
    ):
        checks += 1
    else:
        findings.append("OBPI allowed paths overlap significantly")

    return _passes_to_score(checks, total), findings


def _score_lane_assignment(content: str, obpi_contents: list[str]) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 3

    lane_match = re.search(r"^lane:\s*(\w+)", content, re.MULTILINE)
    if lane_match:
        checks += 1
    else:
        findings.append("No lane in ADR frontmatter")

    adr_lane = (lane_match.group(1).lower() if lane_match else "").lower()
    obpi_lanes_ok = True
    for oc in obpi_contents:
        obpi_lane_m = re.search(r"^lane:\s*(\w+)", oc, re.MULTILINE)
        if obpi_lane_m:
            obpi_lane = obpi_lane_m.group(1).lower()
            if adr_lane == "lite" and obpi_lane == "heavy":
                obpi_lanes_ok = False
    if obpi_lanes_ok:
        checks += 1
    else:
        findings.append("OBPI lane exceeds parent ADR lane")

    if adr_lane == "heavy":
        has_contract = _has_keywords(
            content, ["cli", "api", "schema", "contract", "command", "endpoint"]
        )
        if has_contract:
            checks += 1
        else:
            findings.append("Heavy ADR lacks external contract references")
    else:
        checks += 1

    return _passes_to_score(checks, total), findings


def _score_scope_discipline(content: str) -> tuple[int, list[str]]:
    findings: list[str] = []
    checks = 0
    total = 3

    consequences = section_body(content, "Consequences")
    non_goals = section_body(content, "Non-Goals")
    if consequences or non_goals:
        checks += 1
    else:
        findings.append("Missing Consequences and Non-Goals sections")

    if (
        non_goals
        and _word_count(non_goals) > 20
        or consequences
        and _has_keywords(consequences, ["not", "exclude", "out of scope"])
    ):
        checks += 1
    else:
        findings.append("No explicit exclusions or non-goals stated")

    if _has_keywords(content, ["guardrail", "boundary", "constraint", "scope"]):
        checks += 1
    else:
        findings.append("No scope boundary language found")

    return _passes_to_score(checks, total), findings


def _score_evidence_requirements(
    obpi_contents: list[str],
) -> tuple[int, list[str]]:
    findings: list[str] = []
    if not obpi_contents:
        return 1, ["No OBPI briefs to evaluate"]

    gates_present = 0
    commands_present = 0
    criteria_present = 0
    for oc in obpi_contents:
        if any(
            section_body(oc, h)
            for h in ["Quality Gates", "Quality Gates (Heavy)", "Quality Gates (Lite)"]
        ):
            gates_present += 1
        if section_body(oc, "Acceptance Criteria"):
            ac = section_body(oc, "Acceptance Criteria") or ""
            if "Given/When/Then behavior criterion" not in ac:
                criteria_present += 1
        verification = section_body(oc, "Verification") or ""
        if re.search(r"uv run|bash|python|gz ", verification):
            commands_present += 1

    total = len(obpi_contents)
    checks = 0
    check_total = 3
    if gates_present == total:
        checks += 1
    else:
        findings.append(f"Quality Gates missing in {total - gates_present}/{total} OBPIs")
    if commands_present > 0:
        checks += 1
    else:
        findings.append("No verification commands found in any OBPI")
    if criteria_present == total:
        checks += 1
    else:
        findings.append(
            f"Acceptance Criteria placeholder in {total - criteria_present}/{total} OBPIs"
        )

    return _passes_to_score(checks, check_total), findings


# Alignment-to-precedent lexicon. Widened beyond the original four tokens
# (GHI #631): foundation ADRs name precedents via synonyms ("canonical",
# "mirrors", "aligns with", "reuse", ...) the narrow matcher silently missed,
# manufacturing false-RED 1.0 scores on the canonical foundation-ADR shape.
_PRECEDENT_KEYWORDS = [
    "existing pattern",
    "exemplar",
    "precedent",
    "follows",
    "prior art",
    "established",
    "canonical",
    "mirrors",
    "consistent with",
    "aligns with",
    "in keeping with",
    "reuse",
]


def _score_architectural_alignment(content: str, obpi_contents: list[str]) -> tuple[int, list[str]]:
    """Score STRUCTURAL alignment-to-precedent signals (NOT substance, GHI #624/#631).

    Foundation ADRs keep their src paths in OBPI briefs (the canonical shape) and
    name precedents via synonyms or a substantive Alternatives section, not the
    four original keywords. Matching only the narrative false-negatived every such
    ADR into a 1.0 that fail-closed ``--evaluation-justify-binding`` and forced a
    justify band-aid defending a wrong number (GHI #631).
    """
    findings: list[str] = []
    checks = 0
    total = 3

    # Check 1: concrete source-path references — accept the narrative OR any OBPI
    # brief, since foundation ADRs legitimately keep src paths in their briefs.
    src_ref = r"`src/[^`]+`"
    if re.search(src_ref, content) or any(re.search(src_ref, oc) for oc in obpi_contents):
        checks += 1
    else:
        findings.append("No source file path references in ADR or its OBPI briefs")

    # Check 2: alignment-to-precedent — explicit precedent language (widened
    # lexicon) OR a substantive Alternatives Considered section, since weighing
    # alternatives IS engaging with the prior approaches this dimension grades.
    alternatives = section_body(content, "Alternatives Considered") or ""
    if _has_keywords(content, _PRECEDENT_KEYWORDS) or _has_rejected_alternatives_subsection(
        alternatives
    ):
        checks += 1
    else:
        findings.append("No exemplar/precedent language or substantive Alternatives section")

    if _has_keywords(content, ["anti-pattern", "do not", "avoid", "prohibited"]):
        checks += 1
    else:
        findings.append("No anti-pattern guidance")

    return _passes_to_score(checks, total), findings


def score_adr_deterministic(
    content: str, obpi_count: int, obpi_paths: list[Path], obpi_contents: list[str]
) -> list[DimensionScore]:
    """Score ADR on 8 weighted dimensions."""
    scorers = [
        lambda: _score_problem_clarity(content),
        lambda: _score_decision_justification(content),
        lambda: _score_feature_checklist(content, obpi_count),
        lambda: _score_obpi_decomposition(obpi_paths, obpi_contents),
        lambda: _score_lane_assignment(content, obpi_contents),
        lambda: _score_scope_discipline(content),
        lambda: _score_evidence_requirements(obpi_contents),
        lambda: _score_architectural_alignment(content, obpi_contents),
    ]
    results: list[DimensionScore] = []
    for (dim_name, weight), scorer in zip(ADR_WEIGHTS, scorers, strict=True):
        score, findings = scorer()
        results.append(
            DimensionScore(
                dimension=dim_name,
                weight=weight,
                score=score,
                weighted=round(score * weight, 3),
                findings=findings,
            )
        )
    return results


# ---------------------------------------------------------------------------
# OBPI dimension scoring (deterministic)
# ---------------------------------------------------------------------------


def _score_obpi_independence(content: str) -> int:
    deps = re.findall(r"depends on OBPI-|requires OBPI-|after OBPI-", content, re.IGNORECASE)
    declared = section_body(content, "Dependencies") or ""
    undeclared = [d for d in deps if d.lower() not in declared.lower()]
    if not deps:
        return 4
    if not undeclared:
        return 3
    return 2 if len(undeclared) == 1 else 1


def _score_obpi_testability(content: str) -> int:
    # Try common heading variants for quality gates
    gates = ""
    for heading in ["Quality Gates", "Quality Gates (Heavy)", "Quality Gates (Lite)"]:
        gates = section_body(content, heading) or gates
    verification = section_body(content, "Verification") or ""
    evidence = section_body(content, "Evidence") or ""
    combined = gates + verification + evidence
    if "command --to --verify" in combined:
        return 1
    commands = re.findall(r"uv run|bash|python|gz |unittest", combined)
    if len(commands) >= 3:
        return 4
    if len(commands) >= 1:
        return 3
    if _word_count(combined) > 20:
        return 2
    return 1


def _score_obpi_value(content: str) -> int:
    objective = section_body(content, "Objective") or ""
    if not objective or objective.endswith(".") and _word_count(objective) < 5:
        return 1
    for markers in TEMPLATE_SCAFFOLD_MARKERS.values():
        if any(m in objective for m in markers):
            return 1
    wc = _word_count(objective)
    if wc > 30:
        return 4
    if wc > 20:
        return 3
    if wc > 10:
        return 2
    return 1


def _score_obpi_size(content: str) -> int:
    ap = section_body(content, "Allowed Paths") or ""
    paths = re.findall(r"`([^`]+)`", ap)
    real_paths = [p for p in paths if "src/module" not in p]
    count = len(real_paths)
    if 2 <= count <= 8:
        return 4
    if 1 <= count <= 12:
        return 3
    if count > 12:
        return 2
    return 1


def _score_obpi_clarity(content: str) -> int:
    reqs = section_body(content, "Requirements (FAIL-CLOSED)") or ""
    criteria = section_body(content, "Acceptance Criteria") or ""
    ap = section_body(content, "Allowed Paths") or ""

    checks = 0
    total = 4
    if re.search(r"^\d+\.\s+REQUIREMENT:", reqs, re.MULTILINE) and "First constraint" not in reqs:
        checks += 1
    if "REQ-" in criteria and "Given/When/Then behavior criterion" not in criteria:
        checks += 1
    if ("`src/" in ap or "`tests/" in ap) and "src/module/" not in ap:
        checks += 1
    numbered = re.findall(r"^\d+\.\s+", reqs, re.MULTILINE)
    if len(numbered) >= 2:
        checks += 1

    return _passes_to_score(checks, total)


def score_obpis_deterministic(
    obpi_paths: list[Path], obpi_contents: list[str]
) -> list[ObpiDimensionScores]:
    """Score each OBPI on 5 dimensions."""
    results: list[ObpiDimensionScores] = []
    for path, content in zip(obpi_paths, obpi_contents, strict=True):
        ind = _score_obpi_independence(content)
        test = _score_obpi_testability(content)
        val = _score_obpi_value(content)
        siz = _score_obpi_size(content)
        cla = _score_obpi_clarity(content)
        avg = round(statistics.mean([ind, test, val, siz, cla]), 2)
        results.append(
            ObpiDimensionScores(
                obpi_id=path.stem,
                independence=ind,
                testability=test,
                value=val,
                size=siz,
                clarity=cla,
                average=avg,
            )
        )
    return results


# ---------------------------------------------------------------------------
# QC-step self-registration (ADR-0.0.73 / OBPI-07, GHI #624)
# ---------------------------------------------------------------------------
#
# `gz adr evaluate` is itself a QC step the verification-layer mechanism governs.
# It self-registers as `advisory` — it grades quality, it does not gate `gz
# check` — so `gz validate --qc-binding` can classify and audit it. The evaluator
# now grades decision substance (above), so the score it renders is no longer a
# shape-graded value presented as authoritative truth.
register_advisory_qc_step(
    name="ADR Evaluate",
    kind="audit",
    subject="docs/",
    wired_into=["gz adr evaluate"],
    enforcement_locus="python_function",
)
