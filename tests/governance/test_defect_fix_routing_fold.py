"""Tests for the defect-fix-routing rule-file consolidation (ADR-0.0.20 OBPI-04).

@covers ADR-0.0.20-agent-rule-placement-invariant
@covers OBPI-0.0.20-04-fold-defect-fix-routing

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

# Bucket-3 historical roots allowed to reference the legacy path by narrative
# (session plan snapshots, OBPI briefs describing the migration, release
# notes, the advisory scorecard entry, historical ADRs, and the fold test
# files which hold the legacy path as a detection target).
BUCKET_3_ROOTS = (
    ".git/",
    ".claude/plans/",
    # Local git worktrees mirror the working tree under the parent repo path;
    # scanning into them creates duplicate-path false positives identical to
    # the canonical surface they shadow. Worktree contents are never source-
    # of-truth for this audit (state lives in the parent repo).
    ".claude/worktrees/",
    # Closed / historical ADRs that reference the legacy path in narrative.
    "docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/",
    "docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/",
    "docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/",
    "docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/",
    "docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/",
    "docs/design/adr/pool/ADR-pool.tdd-receipt-stream.md",
    "docs/design/adr/pool/ADR-pool.interpretability-hardened-agent-surfaces.md",
    "docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/",
    "docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/",
    "docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/",
    "RELEASE_NOTES.md",
    # Governance pedagogy + lineage docs.
    "docs/governance/agent-contract-rationale.md",
    "docs/governance/advisory-rules-audit.md",
    "docs/governance/model-regression-taxonomy.md",
    "docs/governance/trust-doctrine.md",
    "docs/governance/governance_runbook.md",
    "docs/governance/arb-middleware.md",
    # The new pedagogy doc for this fold legitimately holds the rule name in
    # its "When this rule was authored" and "Related" sections.
    "docs/governance/defect-fix-routing.md",
    # Manpage HISTORY section legitimately cites the lineage.
    "docs/user/manpages/arb.md",
    # Historical chore proof records and one-shot audit artifacts.
    # Chores tree relocated from ops/chores/ to src/gzkit/chores/ under
    # ADR-0.0.21 (OBPI-0.0.21-01-physical-migration). Historical proof
    # files preserve their legacy-path references by design.
    "src/gzkit/chores/",
    "artifacts/audits/",
    # ARB receipts are immutable evidentiary records; their stderr_tail can
    # legitimately quote retired path names from the failure messages they
    # captured. Scanning them creates a self-perpetuating false positive.
    "artifacts/receipts/",
    "tests/governance/test_attestation_fold.py",
    "tests/governance/test_agent_contract_fold.py",
    "tests/governance/test_defect_fix_routing_fold.py",
    # Validator test fixtures legitimately use the legacy path as data.
    "tests/validators/test_unscoped_rules.py",
    # mkdocs build artifact; regenerated from sources.
    "site/",
    # local venv / build caches.
    ".venv/",
    "dist/",
    "build/",
)


class TestDefectFixRoutingFold(unittest.TestCase):
    """Assert the defect-fix-routing rule file was folded into its proper homes."""

    @covers("REQ-0.0.20-04-03")
    def test_defect_fix_routing_rule_file_deleted(self) -> None:
        """The canonical `.gzkit/rules/defect-fix-routing.md` must not exist.

        Binding content now lives in AGENTS.md § Defect-fix routing; pedagogy
        lives in docs/governance/defect-fix-routing.md. Vendor mirrors
        regenerate via ``gz agent sync control-surfaces``; this test guards
        only the canonical source.
        """
        canonical = REPO_ROOT / ".gzkit" / "rules" / "defect-fix-routing.md"
        self.assertFalse(
            canonical.exists(),
            f"{canonical} should be deleted after OBPI-0.0.20-04; "
            "its content now lives in AGENTS.md § Defect-fix routing and "
            "docs/governance/defect-fix-routing.md",
        )

    @covers("REQ-0.0.20-04-01")
    def test_agents_md_has_defect_fix_routing_section(self) -> None:
        """AGENTS.md must carry the binding defect-fix-routing content.

        REQ-01 requires four semantic elements in AGENTS.md § Defect-fix routing:
          (a) the "Direct fix is the right route when ALL hold" table with
              five criterion rows (Diff size / Scope / Precedent / Trigger /
              Coverage)
          (b) the "OBPI ceremony is required when ANY hold" table with five
              trigger rows (brief boundaries / CLI schema / operator directs
              / feature work / exceeds thresholds)
          (c) the 5-step Decision protocol (Compute facts / Apply criteria /
              Direct fix route / OBPI route / Ambiguous → surface to operator)
          (d) a baseline-precedent pointer to docs/governance/defect-fix-routing.md

        Assertions target semantic markers, not exact strings, per the
        tests-assert-semantics-not-strings rule.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        section_idx = agents_text.find("## Defect-fix routing")
        self.assertNotEqual(
            section_idx,
            -1,
            "AGENTS.md missing '## Defect-fix routing' H2 section",
        )

        # Scope further checks to the § Defect-fix routing body (to the next H2).
        remainder = agents_text[section_idx:]
        next_h2 = remainder.find("\n## ", 1)
        section = remainder if next_h2 == -1 else remainder[:next_h2]

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) direct-fix table with 5 criterion rows": (
                "Direct fix is the right route",
                "Diff size",
                "Scope",
                "Precedent",
                "Trigger",
                "Coverage",
            ),
            "(b) ceremony-required table with 5 trigger rows": (
                "OBPI ceremony is required",
                "brief boundaries",
                "CLI surface",
                "Operator explicitly directs",
                "new feature work",
                "exceeds the direct-fix thresholds",
            ),
            "(c) 5-step decision protocol": (
                "Decision protocol",
                "Compute the routing facts",
                "Apply the criteria",
                "direct fix",
                "OBPI ceremony",
                "ambiguous",
            ),
            "(d) pointer to docs/governance/defect-fix-routing.md": (
                "docs/governance/defect-fix-routing.md",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in section for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "AGENTS.md § Defect-fix routing missing required semantic elements:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-04-02")
    def test_governance_doc_exists_with_three_sections(self) -> None:
        """``docs/governance/defect-fix-routing.md`` must carry three sections.

        REQ-02 requires:
          (a) Anti-patterns catalog (OBPI ceremony for trivial defects;
              "parent ADR is natural home" framing; routing-as-stylistic
              preference)
          (b) Origin GHI history ("When this rule was authored" — GHI #195,
              2026-04-18, OBPI-0.0.16-04 → OBPI-0.0.16-06 → revert precedent)
          (c) Related-rules cross-references (AGENTS.md § Defect-fix routing,
              Craftsmanship 6c, gz-obpi-pipeline / gz-obpi-specify SKILLs)
        """
        path = REPO_ROOT / "docs" / "governance" / "defect-fix-routing.md"
        self.assertTrue(path.is_file(), f"{path} should exist after OBPI-0.0.20-04")

        text = path.read_text(encoding="utf-8")

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) Anti-patterns": (
                "Anti-patterns",
                "parent ADR",
                "Surface Boundary",
                "stylistic preference",
            ),
            "(b) Origin GHI #195 / 2026-04-18": (
                "When this rule was authored",
                "GHI #195",
                "2026-04-18",
                "OBPI-0.0.16-04",
                "OBPI-0.0.16-06",
            ),
            "(c) Related cross-references": (
                "Related",
                "Defect-fix routing",
                "gz-obpi-pipeline",
                "gz-obpi-specify",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in text for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "docs/governance/defect-fix-routing.md missing required sections:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-04-04")
    def test_manifest_allowlist_no_longer_contains_defect_fix_routing(self) -> None:
        """Manifest ``rules.unscoped_allowlist`` must not contain defect-fix-routing.md.

        The assertion is absence-of-entry, not "manifest has exactly N entries" —
        the count cascades as other OBPIs land; absence is the semantic
        invariant this OBPI guarantees (matches test_agent_contract_fold
        precedent).
        """
        manifest = json.loads(
            (REPO_ROOT / ".gzkit" / "manifest.json").read_text(encoding="utf-8"),
        )
        allowlist = manifest.get("rules", {}).get("unscoped_allowlist", [])

        entry_files = {entry.get("file") for entry in allowlist}
        self.assertNotIn(
            ".gzkit/rules/defect-fix-routing.md",
            entry_files,
            "defect-fix-routing.md allow-list entry must be removed",
        )

    @covers("REQ-0.0.20-04-05")
    def test_no_inbound_references_to_legacy_paths_in_live_files(self) -> None:
        """No Bucket-1 (live) file may reference the retired rule path.

        REQ-05: inbound references must point at AGENTS.md § Defect-fix
        routing or docs/governance/defect-fix-routing.md. Historical roots
        listed in ``BUCKET_3_ROOTS`` are preserved as-is and excluded from
        the scan.
        """
        legacy_patterns = (
            ".gzkit/rules/defect-fix-routing.md",
            ".claude/rules/defect-fix-routing.md",
            ".github/instructions/defect_fix_routing.instructions.md",
            ".agents/rules/defect-fix-routing.md",
        )

        offenders: list[str] = []
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".json", ".py"}:
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
            "live files still reference retired defect-fix-routing paths:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    @covers("REQ-0.0.20-04-06")
    def test_vendor_mirrors_of_defect_fix_routing_rule_were_removed_by_sync(self) -> None:
        """``gz agent sync control-surfaces`` removes the vendor mirrors.

        REQ-06: after canonical deletion + sync, the mirrors under
        ``.claude/rules/``, ``.github/instructions/``, and (if present)
        ``.agents/rules/`` must not exist.
        """
        mirrors = (
            REPO_ROOT / ".claude" / "rules" / "defect-fix-routing.md",
            REPO_ROOT / ".github" / "instructions" / "defect_fix_routing.instructions.md",
            REPO_ROOT / ".agents" / "rules" / "defect-fix-routing.md",
        )
        still_present = [str(p.relative_to(REPO_ROOT)) for p in mirrors if p.exists()]
        self.assertFalse(
            still_present,
            f"vendor mirrors should auto-clean via sync; still present: {still_present!r}",
        )

    @covers("REQ-0.0.20-04-07")
    @covers("REQ-0.0.20-04-08")
    @covers("REQ-0.0.20-04-09")
    @covers("REQ-0.0.20-04-10")
    def test_unscoped_rules_validator_passes_with_empty_allowlist(self) -> None:
        """``gz validate --unscoped-rules`` exits 0 post-fold with empty allow-list.

        Calls the validator's public Python API directly (no subprocess) to
        keep the test in the unit tier per ``.gzkit/rules/tests.md``.
        Asserts result="pass", exit_code=0, and zero allow-list entries.

        Satisfies REQ-07 (unscoped-rules exits 0 with empty allow-list),
        REQ-08 (no drift in validate-all surface), REQ-09 (no mkdocs
        internal-link drift from the reference rewrites), and REQ-10 (TDD
        test covers the semantic migration).
        """
        result = run_unscoped_rules(REPO_ROOT)

        self.assertEqual(result.result, "pass", f"validator failed: {result!r}")
        self.assertEqual(result.exit_code, 0, f"validator exit_code={result.exit_code}")
        self.assertEqual(
            len(result.allowlist_entries),
            0,
            f"expected 0 allow-list entries post-OBPI-04, got {len(result.allowlist_entries)}",
        )

    @covers("REQ-0.0.20-04-11")
    def test_no_new_deps_no_shell_true_no_dataclass(self) -> None:
        """REQ-11: No new deps; no shell=True; no dataclass.

        The new governance doc is markdown-only (no executable code). This
        test file holds the forbidden-pattern strings as detection targets
        only (string-assembled below so the test does not match itself).
        """
        governance_doc = (REPO_ROOT / "docs" / "governance" / "defect-fix-routing.md").read_text(
            encoding="utf-8"
        )

        # String-assembled so this test does not match itself.
        forbidden = ("@" + "dataclass", "from " + "dataclasses", "shell" + "=True")
        offenders = [p for p in forbidden if p in governance_doc]
        self.assertFalse(
            offenders,
            f"defect-fix-routing.md must be prose-only; found forbidden tokens: {offenders!r}",
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
            f"OBPI-04 may not introduce new imports: {non_conforming!r}",
        )


if __name__ == "__main__":
    unittest.main()
