"""Shared machinery for the ADR-0.0.20 rule-fold guards (GHI #779).

Three guards — attestation, agent-contract, defect-fix-routing — each scanned the
git-tracked tree for a retired rule path and each carried a byte-identical
``BUCKET_3_ROOTS`` block. Two defects lived in that shape.

**The exemption list conflated two different kinds of exemption**, and that
conflation is why stale grants were undetectable. ``.git/``, ``.venv/`` and
``artifacts/receipts/`` are excluded because they are *not live governed state*;
``docs/governance/trust-doctrine.md`` was excluded because it *narrates* the fold.
Only the second kind can go stale — a narrating file that no longer narrates is a
blanket grant over a live surface — but with both kinds in one tuple there was no
way to say "assert this grant is still needed" without also asserting it of
``.git/``, which holds nothing to assert. Splitting them is what makes the ratchet
expressible at all.

**File-level grants cannot separate a live pointer from narration.** Both sentence
kinds contain the same string: *"the ARB rule file was retired 2026-04-21"*
(narration, legitimate) and *"Rule documented in ``.gzkit/rules/attestation-
enrichment.md``"* (a live pointer sending an agent to a file it cannot open). One
legitimate narrative line bought a whole file immunity, and ten dead pointers
accumulated behind five such grants while the guards reported green (GHI #778).
The ratchet does not solve that directly; it bounds it, by refusing to keep a grant
alive once the narration it was written for is gone.

**Bare-filename citations were invisible regardless of any grant.** ``legacy_paths``
matched full paths only, so *"per attestation-enrichment.md"* — three of the ten
pointers repaired under GHI #778 — passed every guard. Widening to bare filenames
naively is wrong: ``docs/governance/defect-fix-routing.md`` is a **live** file, so
flagging every bare mention of that basename would fire on legitimate references.
The predicate is therefore resolution-based and self-adjusting: a bare citation is
dead only when **no tracked file carries that basename**. That is SAFE for
``attestation-enrichment.md`` (retired, no live counterpart) and correctly inert for
``defect-fix-routing.md`` (retired at the rules path, alive under docs/governance/).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Suffixes worth scanning for a governed-surface pointer. The three guards
# disagreed here — two scanned ``.py`` and one did not — with no stated reason.
# The union is correct: a dead pointer in a docstring misroutes an agent exactly
# as a dead pointer in prose does.
SCANNED_SUFFIXES = (".md", ".json", ".py")

# Roots excluded because they are not live governed state — caches, build output,
# immutable evidentiary records, and append-only historical archives. These can
# never go stale in the ratchet's sense: they are exempt by what they ARE, not by
# a sentence they happen to contain, so asserting "this grant is still needed" of
# ``.git/`` is not a question that has an answer. Keeping them separate from
# ``NARRATION_GRANTS`` is what lets the ratchet bind on the grants that CAN rot.
NON_LIVE_ROOTS = (
    ".git/",
    # Session plans and handoffs are append-only historical snapshots that
    # legitimately quote retired path names when describing past work.
    ".claude/plans/",
    ".gzkit/handoffs/",
    # Local worktrees mirror the working tree, producing duplicate-path false
    # positives identical to the canonical surface they shadow.
    ".claude/worktrees/",
    # Historical chore proof records and one-shot audit artifacts.
    "src/gzkit/chores/",
    "artifacts/audits/",
    # ARB receipts are immutable evidentiary records; a stderr_tail can quote a
    # retired name from the very failure it captured. Scanning them creates a
    # self-perpetuating false positive.
    "artifacts/receipts/",
    # Recorded ceremony attestations and shipped release notes are closed
    # records of what was said at the time. The ADR-0.0.20 ceremony attestation
    # names all three folded rule files by construction — it is the record OF
    # the fold — and rewriting it to satisfy a scan would falsify an
    # attestation, which AGENTS.md § Attestation forbids outright.
    ".gzkit/ceremonies/",
    "docs/releases/",
    # mkdocs build artifact; regenerated from sources.
    "site/",
    # local venv / build caches.
    ".venv/",
    "dist/",
    "build/",
)


def tracked_files(repo_root: Path) -> list[str]:
    """Return every git-tracked path, repo-relative.

    "Live" is operationalized as git-tracked: the committed governed surface.
    Untracked caches, the virtualenv and mkdocs ``site/`` output are not live
    state, and walking them produced the 261k-path ``rglob`` blow-up that pushed
    these guards past the test-health budget (test-isolation chore).
    """
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return [rel for rel in completed.stdout.split("\0") if rel]


def _is_exempt(rel: str, roots: tuple[str, ...]) -> bool:
    return any(rel.startswith(root) or rel == root for root in roots)


def bare_citation_pattern(basename: str) -> re.Pattern[str]:
    """Match *basename* as a citation, never as the tail of a longer filename.

    The lookbehind is load-bearing. A plain substring test reports
    ``OBPI-0.0.20-03-fold-attestation-enrichment.md`` — a **live** OBPI brief
    whose slug merely ends with the retired basename — as a dead pointer, which
    is a false positive on a real governed file (observed in
    ``data/sensitivity_floor_grandfather.json`` while building this guard).
    Requiring the preceding character to be a non-filename character keeps
    ``per attestation-enrichment.md`` and `` `attestation-enrichment.md` `` while
    dropping ``fold-attestation-enrichment.md``.
    """
    return re.compile(r"(?<![\w.-])" + re.escape(basename))


def unresolvable_basenames(legacy_paths: tuple[str, ...], tracked: list[str]) -> set[str]:
    """Return retired basenames that no tracked file provides.

    A bare citation of one of these resolves to nothing, so it is a dead pointer
    wherever it appears. A basename that IS provided by some tracked file is
    excluded — the citation resolves, whatever directory the reader assumes.
    """
    provided = {Path(rel).name for rel in tracked}
    return {name for p in legacy_paths if (name := Path(p).name) not in provided}


def dead_pointer_offenders(
    *,
    legacy_paths: tuple[str, ...],
    narration_grants: tuple[str, ...],
    non_live_roots: tuple[str, ...],
    repo_root: Path,
) -> list[str]:
    """Return live files citing a retired path, by full path or dead bare filename."""
    tracked = tracked_files(repo_root)
    dead_names = unresolvable_basenames(legacy_paths, tracked)
    exempt = tuple(narration_grants) + tuple(non_live_roots)

    offenders: list[str] = []
    for rel in tracked:
        if not rel.endswith(SCANNED_SUFFIXES) or _is_exempt(rel, exempt):
            continue
        try:
            text = (repo_root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        cited = next((p for p in legacy_paths if p in text), None)
        if cited is None:
            cited = next(
                (n for n in sorted(dead_names) if bare_citation_pattern(n).search(text)),
                None,
            )
        if cited is not None:
            offenders.append(f"{rel} contains {cited!r}")
    return offenders


def stale_narration_grants(
    *,
    legacy_paths: tuple[str, ...],
    narration_grants: tuple[str, ...],
    repo_root: Path,
) -> list[str]:
    """Return grants that protect nothing — the ratchet.

    A grant is stale when its path is gone from disk, or when nothing under it
    carries any retired pattern. Either way it is a blanket exemption over a live
    surface, earning its keep by a sentence that is no longer there. Reported so
    the grant is removed rather than left as a silent blind spot.
    """
    tracked = tracked_files(repo_root)
    dead_names = unresolvable_basenames(legacy_paths, tracked)
    bare = [bare_citation_pattern(name) for name in sorted(dead_names)]

    stale: list[str] = []
    for grant in narration_grants:
        target = repo_root / grant
        if not target.exists():
            stale.append(f"{grant} (path no longer exists)")
            continue
        files = [target] if target.is_file() else [p for p in target.rglob("*") if p.is_file()]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if any(p in text for p in legacy_paths) or any(p.search(text) for p in bare):
                break
        else:
            stale.append(f"{grant} (contains no retired pattern)")
    return stale
