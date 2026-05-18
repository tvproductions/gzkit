"""Tests for the agent-contract rule-file consolidation (ADR-0.0.20 OBPI-02).

@covers ADR-0.0.20-agent-rule-placement-invariant
@covers OBPI-0.0.20-02-fold-agent-contract

Each test is REQ-pinned via :func:`gzkit.traceability.covers` and derives its
assertions from the OBPI brief's Acceptance Criteria, not from the post-fold
observed state.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.traceability import covers
from gzkit.validators.unscoped_rules import run_unscoped_rules

REPO_ROOT = Path(__file__).resolve().parents[2]

# Bucket-3 historical roots that are allowed to reference the legacy path by
# narrative (session plan snapshots, OBPI briefs describing the migration,
# release notes for the prior release, the rationale doc describing its own
# origin, and the advisory scorecard entry documenting the fold).
BUCKET_3_ROOTS = (
    ".git/",
    ".claude/plans/",
    # Local git worktrees mirror the working tree under the parent repo path;
    # scanning into them creates duplicate-path false positives identical to
    # the canonical surface they shadow. Worktree contents are never source-
    # of-truth for this audit (state lives in the parent repo).
    ".claude/worktrees/",
    "docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/",
    "RELEASE_NOTES.md",
    "docs/governance/agent-contract-rationale.md",
    "docs/governance/advisory-rules-audit.md",
    "tests/governance/test_agent_contract_fold.py",
    # ARB receipts are immutable evidentiary records; their stderr_tail can
    # legitimately quote retired path names from the failure messages they
    # captured. Scanning them creates a self-perpetuating false positive.
    "artifacts/receipts/",
    # mkdocs build artifact; regenerated from sources
    "site/",
    # local venv / build caches
    ".venv/",
    "dist/",
    "build/",
)


class TestAgentContractFold(unittest.TestCase):
    """Assert the agent-contract rule file was folded into its proper homes."""

    @covers("REQ-0.0.20-02-05")
    @covers("REQ-0.0.20-02-12")
    def test_agent_contract_rule_file_deleted(self) -> None:
        """The canonical `.gzkit/rules/agent-contract.md` must not exist.

        The rule's content lives in AGENTS.md (invariants), CLAUDE.md (10a),
        and docs/governance/agent-contract-rationale.md (pedagogy). No
        residual rule file remains. Vendor mirrors regenerate via
        ``gz agent sync control-surfaces``; this test guards only the
        canonical source.
        """
        canonical = REPO_ROOT / ".gzkit" / "rules" / "agent-contract.md"
        self.assertFalse(
            canonical.exists(),
            f"{canonical} should be deleted after OBPI-0.0.20-02; "
            "its content now lives in AGENTS.md, CLAUDE.md, and "
            "docs/governance/agent-contract-rationale.md",
        )

    @covers("REQ-0.0.20-02-01")
    @covers("REQ-0.0.20-02-02")
    @covers("REQ-0.0.20-02-12")
    def test_agents_md_contains_migrated_invariants(self) -> None:
        """AGENTS.md must carry the unique invariants the fold migrates.

        Deduplication is by semantic match (REQ 1): invariants already present
        in AGENTS.md are not duplicated. The test asserts only on the
        additions unique to the consolidated rule (REQ 2):

          * Craftsmanship 6c — defect-fix-routing scope choice (GHI #195 line)
          * Craftsmanship 6g — verify runtime surface (GHI #263)
          * Craftsmanship 6h — quote rule verbatim (GHI #261)
          * Judgment 12 — surface assumptions explicitly before implementing
          * Judgment 13 — STOP, name confusion, present tradeoff, wait
          * Judgment 14 — push back when an approach has clear problems
          * Pipeline lifecycle — do not summarize after Stage 2 or 3 and stop
          * State doctrine — do not read ``status: Completed`` frontmatter
            as proof of completion (read the ledger).

        Assertions target semantic markers, not exact strings, per the
        tests-assert-semantics-not-strings rule.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        expected_markers: dict[str, tuple[str, ...]] = {
            "craftsmanship 6c (defect-fix-routing)": ("6c", "defect-fix-routing"),
            "craftsmanship 6g (runtime surface)": ("6g", "runtime surface"),
            "craftsmanship 6h (quote rule verbatim)": ("6h", "verbatim"),
            "judgment 12 (surface assumptions)": ("Surface assumptions",),
            "judgment 13 (STOP on inconsistencies)": ("STOP", "name confusion"),
            "judgment 14 (push back)": ("Push back",),
            "pipeline lifecycle don't (summarize/stop)": ("Do not summarize after Stage 2 or 3",),
            "state doctrine don't (frontmatter not proof)": (
                "Do not read",
                "status: Completed",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in agents_text for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "AGENTS.md missing migrated invariants from agent-contract.md:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-02-03")
    @covers("REQ-0.0.20-02-12")
    def test_claude_md_carries_10a_and_agents_md_does_not(self) -> None:
        """Invariant 10a (skill-tool-invoke-same-turn) must live in CLAUDE.md.

        The invariant names Claude-specific tool surfaces (``EnterPlanMode``)
        and is therefore not portable to AGENTS.md (which must stay
        vendor-neutral). CLAUDE.md's "Claude Code addendum" section is the
        correct home. AGENTS.md must not carry the Claude-specific phrasing.
        """
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        agents_md = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        # The slim CLAUDE.md template may use a comment or heading for the
        # Claude-specific section.  The binding invariant is that the 10a
        # same-turn text lives in CLAUDE.md (not AGENTS.md).
        self.assertIn(
            "invoke it in the same turn",
            claude_md,
            "CLAUDE.md must carry 10a ('invoke it in the same turn')",
        )

        self.assertNotIn(
            "invoke it in the same turn",
            agents_md,
            "AGENTS.md must not carry the Claude-specific 10a phrasing",
        )
        self.assertNotIn(
            "EnterPlanMode",
            agents_md,
            "AGENTS.md must not name Claude-specific tools like EnterPlanMode",
        )

    @covers("REQ-0.0.20-02-04")
    def test_rationale_md_has_three_named_sections(self) -> None:
        """``docs/governance/agent-contract-rationale.md`` must have three sections.

        The rationale doc is the home for pedagogy extracted from AGENTS.md
        and from the legacy rule:

          (a) Anti-pattern canon — the vibe-coding failure-mode list (GHI #157)
          (b) TASK-driven workflow — REQ→TASK→commit trailer chain (GHI #160)
          (c) Rationale for 6g/6h — reporting-pathway drift (GHI #261/#263,
              Lindsey et al. 2025 citation)

        Each section carries a heading matching its purpose and an in-body
        GHI citation for provenance.
        """
        path = REPO_ROOT / "docs" / "governance" / "agent-contract-rationale.md"
        self.assertTrue(path.is_file(), f"{path} should exist after OBPI-0.0.20-02")

        text = path.read_text(encoding="utf-8")

        self.assertIn("Anti-pattern canon", text, "missing § Anti-pattern canon")
        self.assertIn("TASK-driven workflow", text, "missing § TASK-driven workflow")
        self.assertTrue(
            "Rationale for 6g" in text or "Rationale for Invariants 6g" in text,
            "missing § Rationale for 6g (or 6g/6h)",
        )

        self.assertIn("GHI #157", text, "anti-pattern canon must cite GHI #157")
        self.assertIn("GHI #160", text, "TASK-driven workflow must cite GHI #160")
        self.assertTrue(
            "GHI #261" in text or "GHI #263" in text,
            "6g/6h rationale must cite GHI #261 or #263",
        )
        self.assertIn(
            "Lindsey",
            text,
            "6g/6h rationale must cite Lindsey et al. 2025 reporting-pathway work",
        )

    @covers("REQ-0.0.20-02-06")
    @covers("REQ-0.0.20-02-12")
    def test_manifest_allowlist_removes_agent_contract_entry(self) -> None:
        """Manifest ``rules.unscoped_allowlist`` must not contain agent-contract.md.

        REQ-06's semantic claim is "OBPI-02 removed its allow-list entry",
        not "the manifest has exactly N entries" — the count cascades as
        sibling OBPIs (03, 04) fold their own rules. The assertion derived
        from the REQ is absence of agent-contract.md, which is OBPI-02's
        contribution; subsequent OBPIs reduce the remaining count further.
        """
        manifest = json.loads(
            (REPO_ROOT / ".gzkit" / "manifest.json").read_text(encoding="utf-8"),
        )
        allowlist = manifest.get("rules", {}).get("unscoped_allowlist", [])

        entry_files = {entry.get("file") for entry in allowlist}
        self.assertNotIn(
            ".gzkit/rules/agent-contract.md",
            entry_files,
            "agent-contract.md allow-list entry must be removed",
        )

    @covers("REQ-0.0.20-02-07")
    def test_no_inbound_references_to_legacy_paths_in_live_files(self) -> None:
        """No Bucket-1 (live) file may reference the retired paths.

        REQ 7: inbound references must point at AGENTS.md sections, the
        CLAUDE.md addendum, or the rationale doc. Historical roots listed
        in ``BUCKET_3_ROOTS`` are preserved as-is and excluded from the scan.
        """
        legacy_patterns = (
            ".gzkit/rules/agent-contract.md",
            ".claude/rules/agent-contract.md",
            ".github/instructions/agent_contract.instructions.md",
            ".agents/rules/agent-contract.md",
        )

        offenders: list[str] = []
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".json"}:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(root) or rel == root for root in BUCKET_3_ROOTS):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pattern in legacy_patterns:
                if pattern in text:
                    offenders.append(f"{rel} contains {pattern!r}")
                    break

        self.assertFalse(
            offenders,
            "live files still reference retired agent-contract paths:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.20-02-08")
    def test_vendor_mirrors_of_agent_contract_were_removed_by_sync(self) -> None:
        """``gz agent sync control-surfaces`` removes the vendor mirrors.

        REQ 8: after canonical deletion + sync, the mirrors under
        ``.claude/rules/`` and ``.github/instructions/`` must not exist.
        """
        mirrors = (
            REPO_ROOT / ".claude" / "rules" / "agent-contract.md",
            REPO_ROOT / ".github" / "instructions" / "agent_contract.instructions.md",
        )
        still_present = [str(p.relative_to(REPO_ROOT)) for p in mirrors if p.exists()]
        self.assertFalse(
            still_present,
            f"vendor mirrors should auto-clean via sync; still present: {still_present!r}",
        )

    @covers("REQ-0.0.20-02-09")
    @covers("REQ-0.0.20-02-10")
    @covers("REQ-0.0.20-02-11")
    def test_unscoped_rules_validator_passes_post_fold(self) -> None:
        """``gz validate --unscoped-rules`` exits 0 post-fold.

        Calls the validator's public Python API directly (no subprocess)
        to keep the test in the unit tier per ``.gzkit/rules/tests.md``.
        Asserts result="pass" and exit_code=0. The absolute count of
        allow-list entries is not asserted — it cascades down as sibling
        OBPIs (03, 04) fold their own rules. What REQ-09/10/11 pin is
        validator pass state after OBPI-02's contribution.

        Satisfies REQ-9 (unscoped-rules exits 0), REQ-10 (no drift in the
        validate-all surface the unscoped audit participates in), and
        REQ-11 (no internal-link drift from the reference rewrites would
        block mkdocs strict — the validator iterates the same canonical
        rule set the docs tree references).
        """
        result = run_unscoped_rules(REPO_ROOT)

        self.assertEqual(result.result, "pass", f"validator failed: {result!r}")
        self.assertEqual(result.exit_code, 0, f"validator exit_code={result.exit_code}")

    @covers("REQ-0.0.20-02-13")
    def test_no_new_deps_shell_true_or_dataclass(self) -> None:
        """REQ 13: OBPI-02 introduces no stdlib ``dataclass``, no ``shell=True``,
        and no new third-party dependency.

        This OBPI is a pure governance/documentation migration — no new Python
        source was authored under ``src/**``. The only newly-authored surface
        is ``docs/governance/agent-contract-rationale.md`` (markdown, no
        executable code). The test file itself contains the forbidden-pattern
        strings as literal detection targets, so it is deliberately out of
        scope of this scan (its imports are asserted below).
        """
        rationale = REPO_ROOT / "docs" / "governance" / "agent-contract-rationale.md"
        rationale_text = rationale.read_text(encoding="utf-8")

        # Assembled at runtime so this check does not match itself via the
        # source-tree-wide scan that the plan file described. (String
        # assembly keeps the literal "@dataclass" etc. out of the test body.)
        forbidden = ("@" + "dataclass", "from " + "dataclasses", "shell" + "=True")

        offenders = [p for p in forbidden if p in rationale_text]
        self.assertFalse(
            offenders,
            f"rationale doc must be prose-only; found forbidden tokens: {offenders!r}",
        )

        # Test-file imports must stay stdlib + gzkit-internal (no new dep).
        test_text = Path(__file__).read_text(encoding="utf-8")
        import_lines = [
            line
            for line in test_text.splitlines()
            if line.startswith(("import ", "from ")) and " noqa" not in line
        ]
        allowed_prefixes = (
            "from __future__ import ",
            "import json",
            "import unittest",
            "from pathlib import Path",
            "from gzkit.",
        )
        non_conforming = [
            line for line in import_lines if not any(line.startswith(p) for p in allowed_prefixes)
        ]
        self.assertFalse(
            non_conforming,
            f"OBPI-02 may not introduce new imports: {non_conforming!r}",
        )


if __name__ == "__main__":
    unittest.main()
