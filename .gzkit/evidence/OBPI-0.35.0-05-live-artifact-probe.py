"""Live-artifact probe for OBPI-0.35.0-05 — the measurer behind Stage 4a packet § 6.

Published because § 6 rests on its output, and round 12 established that
classifications published without their measuring artifact are not evidence
(brief `### Step 4b`, round 12 finding 2). Reproduce with:

    uv run gz content compose AGENTS.md --consumer root
    uv run python .gzkit/evidence/OBPI-0.35.0-05-live-artifact-probe.py

Reads the two PERSISTED files plus the committed prior rendition and the corpus
log. Runs no generator itself except through the CLI above, so what it measures
is what landed on disk.

SCOPE, stated so it can be faulted:
  * `independent_scan` is a SECOND OPINION on H1/H2 offsets, not an oracle. It
    is fence-aware, but agreement with production is only informative on an
    input that actually contains a fenced heading-shaped line. The probe
    therefore MEASURES AND PRINTS how many such lines the input carries, and a
    fence-blind control, so a reader can see whether the fence arm was
    exercised at all. On the repository's own AGENTS.md it is not.
  * `unowned_slices_present_verbatim_in_prior` is a CONTAINMENT test. A slice
    copied from the wrong unowned section would still be "present verbatim".
    Positional carry-forward is checked by the covering test
    `test_unowned_section_bytes_are_byte_verbatim`, not here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from gzkit.content.composer import _byte_evidence
from gzkit.content.corpus_store import load_corpus
from gzkit.content.models.corpus import effective_corpus

ROOT = Path()
CANDIDATE = ROOT / ".gzkit/renditions/AGENTS.md/root.candidate.md"
LINEAGE = ROOT / ".gzkit/renditions/AGENTS.md/root.candidate.lineage.json"
PRIOR = ROOT / ".gzkit/renditions/AGENTS.md/root.md"


def _scan(text: bytes, *, fence_aware: bool) -> tuple[list[int], int]:
    """H1/H2 byte offsets. Returns (offsets, heading_shaped_lines_inside_fences)."""
    offsets, fenced_hits, fence, off = [], 0, None, 0
    for line in text.split(b"\n"):
        raw = line.decode("utf-8")
        opener = re.match(r"^(`{3,}|~{3,})", raw.strip())
        if fence_aware and opener:
            tok = opener.group(1)[0]
            fence = None if fence == tok else (fence or tok)
        elif re.match(r"^#{1,2} ", raw):
            if fence_aware and fence:
                fenced_hits += 1
            else:
                offsets.append(off)
        off += len(line) + 1
    return offsets, fenced_hits


def main() -> None:
    cand, prior = CANDIDATE.read_bytes(), PRIOR.read_bytes()
    sections = json.loads(LINEAGE.read_text())
    corpus = load_corpus(ROOT, "AGENTS.md")
    effective = effective_corpus(corpus)

    print(f"SECTIONS {len(sections)}  CANDIDATE_BYTES {len(cand)}  PRIOR_BYTES {len(prior)}")

    # --- partition over the PERSISTED candidate -----------------------------
    spans = sorted((v["byte_span"][0], v["byte_span"][1], k) for k, v in sections.items())
    cursor, gaps, overlaps = 0, [], []
    for start, end, sid in spans:
        if start > cursor:
            gaps.append((cursor, start, sid))
        if start < cursor:
            overlaps.append((cursor, start, sid))
        cursor = max(cursor, end)
    print(
        f"PARTITION contiguous_from_zero={not gaps and not overlaps} gaps={gaps} "
        f"overlaps={overlaps} covers_end={cursor == len(cand)} (cursor={cursor})"
    )

    owned = {k: v for k, v in sections.items() if v["owned"]}
    unowned = {k: v for k, v in sections.items() if not v["owned"]}
    print(f"OWNED {len(owned)}  UNOWNED {len(unowned)}")

    missing = [
        k for k, v in unowned.items() if cand[v["byte_span"][0] : v["byte_span"][1]] not in prior
    ]
    print(
        f"UNOWNED_SLICES_PRESENT_VERBATIM_IN_PRIOR {len(unowned) - len(missing)}/{len(unowned)} "
        f"missing={missing}   [CONTAINMENT, not positional -- see module docstring]"
    )
    print(f"UNOWNED_WITH_ENTRY_IDS {[k for k, v in unowned.items() if v['entry_ids']]}")

    # --- retired entries contribute no lineage id ---------------------------
    live_ids = {e.id for e in effective.entries}
    retired = {e.id for e in corpus.entries} - live_ids
    cited = {i for v in sections.values() for i in v["entry_ids"]}
    print(f"CORPUS all={len(corpus.entries)} live={len(live_ids)} retired={len(retired)}")
    print(f"LINEAGE_CITES {len(cited)}  retired_ids_cited={sorted(cited & retired)}")

    by_id = {e.id: e for e in corpus.entries}
    misplaced = [
        (k, i)
        for k, v in sections.items()
        for i in v["entry_ids"]
        if by_id[i].text.encode("utf-8") not in cand[v["byte_span"][0] : v["byte_span"][1]]
    ]
    print(
        f"CITED_ENTRY_TEXT_INSIDE_ITS_OWN_SLICE {len(cited) - len(misplaced)}/{len(cited)} "
        f"misplaced={misplaced}"
    )
    flat = [i for v in sections.values() for i in v["entry_ids"]]
    print(f"DUPLICATE_ID_EMISSIONS {sorted({i for i in flat if flat.count(i) > 1})}")

    # --- second opinion on boundaries, with its own exercise measured -------
    aware, fenced_hits = _scan(cand, fence_aware=True)
    blind, _ = _scan(cand, fence_aware=False)
    prod = sorted(v["byte_span"][0] for v in sections.values())
    print(
        f"INDEPENDENT_SCAN heads={len(aware)} production_span_starts={len(prod)} "
        f"AGREE={aware == prod}"
    )
    print(
        f"  FENCE_ARM_EXERCISED={fenced_hits > 0} "
        f"(heading_shaped_lines_inside_fences={fenced_hits}); "
        f"fence_blind_control_agrees={blind == prod} "
        f"-- when both agree, this input CANNOT distinguish a fence-aware "
        f"walker from a fence-blind one"
    )

    # --- accounting ---------------------------------------------------------
    inv = sum(len(e.text.encode("utf-8")) for e in effective.entries if e.tier == "invariant")
    com = [e for e in effective.entries if e.tier == "compressible"]
    com_b = sum(len(e.text.encode("utf-8")) for e in com)
    text = cand.decode("utf-8")
    ev = _byte_evidence(
        corpus=corpus,
        candidate_text=text,
        setpoint="lite",
        attributed_compressible=com,
        effective=effective,
    )
    print(
        f"ACCOUNTING invariant={inv} before={com_b} total={len(cand)} "
        f"retired_formula(total-invariant)={len(cand) - inv} shipped_after="
        f"{ev.compressible_bytes_after} after<=before="
        f"{ev.compressible_bytes_after <= ev.compressible_bytes_before} "
        f"after!=total-invariant={ev.compressible_bytes_after != len(cand) - inv}"
    )

    # --- inflation guard: SYNTHETIC attribution, unreachable via the generator
    inv_entries = [e for e in effective.entries if e.tier == "invariant"]
    try:
        _byte_evidence(
            corpus=corpus,
            candidate_text=text,
            setpoint="lite",
            attributed_compressible=[*com, *inv_entries],
            effective=effective,
        )
        print("INFLATION_GUARD did_not_fire=DEFECT")
    except ValueError as exc:
        print(f"INFLATION_GUARD refused=True names_before={str(com_b) in str(exc)}")
        print(
            "  NOTE: this attribution is SYNTHETIC. `generate_candidate` extends "
            "`emitted_compressible` only from `effective.entries`, so after<=before holds "
            "structurally and this guard CANNOT fire through the generator. See packet § 7."
        )


if __name__ == "__main__":
    main()
