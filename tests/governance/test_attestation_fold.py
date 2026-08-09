"""Tests for the attestation-enrichment rule-file consolidation (ADR-0.0.20 OBPI-03).

@covers ADR-0.0.20-agent-rule-placement-invariant
@covers OBPI-0.0.20-03-fold-attestation-enrichment

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

from . import _fold_guard

REPO_ROOT = Path(__file__).resolve().parents[2]

LEGACY_PATHS = (
    ".gzkit/rules/attestation-enrichment.md",
    ".claude/rules/attestation-enrichment.md",
    ".github/instructions/attestation_enrichment.instructions.md",
    ".agents/rules/attestation-enrichment.md",
)

# Not-live roots beyond the shared set: these hold the retired path as a
# detection target by construction, so they must contain it to do their job.
NON_LIVE_ROOTS = _fold_guard.NON_LIVE_ROOTS + (
    "tests/governance/test_attestation_fold.py",
    "tests/governance/test_agent_contract_fold.py",
)

# Live files granted an exemption because they NARRATE the fold rather than
# pointing at it. Unlike NON_LIVE_ROOTS these can rot — a file stops narrating
# and the blanket grant survives, covering whatever pointer lands there next.
# `test_no_stale_narration_grants` is the ratchet that refuses to keep one.
#
# This list was five entries longer until GHI #778. Those five were blanket
# grants covering *live pointers* — "rule documented in X", "per X", "the ARB
# receipt-ID requirement in X" — sentences that send an agent somewhere to read
# a rule, not sentences narrating that the rule moved. A file-level exemption
# cannot tell the two apart, so one legitimate narrative line bought the whole
# file immunity and ten dead pointers accumulated behind it while this test
# stayed green. GHI #779 is the mechanism that let them accumulate undetected.
NARRATION_GRANTS = (
    # Closed / historical ADRs that reference the legacy path in narrative.
    "docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/",
    "docs/design/adr/foundation/ADR-0.0.19-pre-execution-reasoning-walkthrough/",
    "docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/",
    "docs/design/adr/pool/ADR-pool.tdd-receipt-stream.md",
    "docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/",
    "docs/design/adr/pool/ADR-pool.tdd-emission-and-graph-rot-remediation.md",
    "RELEASE_NOTES.md",
    # arb-middleware.md states its own consolidation lineage and the manpage
    # carries a HISTORY section; both must name the retired file to say so.
    "docs/governance/arb-middleware.md",
    "docs/user/manpages/arb.md",
    # Surfaced by the GHI #779 bare-citation widening; both genuinely narrate.
    # The OBPI-0.0.22-06 scorecard records that it REWROTE a citation of the
    # retired path, and the pool ADR's Baseline note states which three rule
    # files ADR-0.0.20 deleted — neither can say that without the name.
    "docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/",
    "docs/design/adr/pool/ADR-pool.instruction-file-reconciliation.md",
)


class TestAttestationFold(unittest.TestCase):
    """Assert the attestation-enrichment rule file was folded into its proper homes."""

    @covers("REQ-0.0.20-03-03")
    @covers("REQ-0.0.20-03-14")
    def test_attestation_rule_file_deleted(self) -> None:
        """The canonical `.gzkit/rules/attestation-enrichment.md` must not exist.

        The rule's binding content lives in AGENTS.md § Attestation; the ARB
        middleware deep-dive lives in docs/governance/arb-middleware.md.
        Vendor mirrors regenerate via ``gz agent sync control-surfaces``;
        this test guards only the canonical source.
        """
        canonical = REPO_ROOT / ".gzkit" / "rules" / "attestation-enrichment.md"
        self.assertFalse(
            canonical.exists(),
            f"{canonical} should be deleted after OBPI-0.0.20-03; "
            "its content now lives in AGENTS.md § Attestation and "
            "docs/governance/arb-middleware.md",
        )

    @covers("REQ-0.0.20-03-01")
    @covers("REQ-0.0.20-03-14")
    def test_agents_md_has_attestation_section(self) -> None:
        """AGENTS.md must carry the binding attestation content.

        REQ-01 requires five semantic elements in AGENTS.md § Attestation:
          (a) the em-dash enrichment pattern with provenance note
          (b) the canonical invocations table (lint, typecheck, tests,
              coverage, docs — five rows)
          (c) the "Applies to" list (obpi complete, adr emit-receipt, git
              commit)
          (d) Lite/Heavy lane behavior (Lite warn / Heavy fail-closed)
          (e) a worked example

        Assertions target semantic markers, not exact strings, per the
        tests-assert-semantics-not-strings rule.
        """
        agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        attestation_idx = agents_text.find("## Attestation")
        self.assertNotEqual(
            attestation_idx,
            -1,
            "AGENTS.md missing '## Attestation' H2 section",
        )

        # Scope further checks to the § Attestation body (to the next H2).
        remainder = agents_text[attestation_idx:]
        next_h2 = remainder.find("\n## ", 1)
        section = remainder if next_h2 == -1 else remainder[:next_h2]

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) em-dash pattern with provenance": (
                "verbatim",
                "concrete characterization",
            ),
            "(b) canonical invocations table (5 rows)": (
                "Lint clean",
                "Type check clean",
                "Tests pass",
                "Coverage floor",
                "Docs build clean",
                "arb-ruff-",
                "arb-step-unittest-",
            ),
            "(c) applies-to list": (
                "obpi complete",
                "adr emit-receipt",
                "git commit",
            ),
            "(d) lane behavior (Lite warn / Heavy fail-closed)": (
                "Lite lane",
                "warning",
                "Heavy lane",
                "fail-closed",
            ),
            "(e) worked example": (
                # OBPI-0.0.54-03 lifted the "### Worked example" heading and
                # its inline content into docs/governance/agent-contract-rationale.md
                # (map-not-encyclopedia doctrine — prohibited heading title).
                # AGENTS.md now surfaces the guidance via the one-line pointer
                # only. REQ semantic preserved: AGENTS.md surfaces worked-example
                # guidance to the operator, now through the anchored link.
                "agent-contract-rationale.md#attestation--worked-example",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in section for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "AGENTS.md § Attestation missing required semantic elements:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-03-02")
    def test_arb_middleware_doc_exists_with_five_sections(self) -> None:
        """``docs/governance/arb-middleware.md`` must carry the five sections.

        REQ-02 requires:
          (a) ARB Middleware — Core Concept
          (b) Available Commands (ruff / step / typecheck / coverage /
              validate / advise / patterns)
          (c) Receipt Schema and Storage (schemas + receipts_root)
          (d) Exit Codes (0 / 1 / 2)
          (e) Rationale (why receipts not narrative; why canonical
              commands; TDD RED evidence is not ARB-shaped — GHI #157)
        """
        path = REPO_ROOT / "docs" / "governance" / "arb-middleware.md"
        self.assertTrue(path.is_file(), f"{path} should exist after OBPI-0.0.20-03")

        text = path.read_text(encoding="utf-8")

        expected_markers: dict[str, tuple[str, ...]] = {
            "(a) Core Concept": ("ARB Middleware", "Core Concept"),
            "(b) Available Commands": (
                "uv run gz arb ruff",
                "uv run gz arb step",
                "uv run gz arb typecheck",
                "uv run gz arb coverage",
                "uv run gz arb validate",
                "uv run gz arb advise",
                "uv run gz arb patterns",
            ),
            "(c) Receipt Schema and Storage": (
                "arb_lint_receipt.schema.json",
                "arb_step_receipt.schema.json",
                "artifacts/receipts/",
                "arb.receipts_root",
            ),
            "(d) Exit Codes": ("Exit codes", "0:", "1:", "2:"),
            "(e) Rationale": (
                "receipts, not narrative",
                "canonical commands",
                "GHI #157",
            ),
        }

        missing: list[str] = []
        for label, markers in expected_markers.items():
            if not all(marker in text for marker in markers):
                missing.append(f"{label}: markers={markers!r}")

        self.assertFalse(
            missing,
            "docs/governance/arb-middleware.md missing required sections:\n"
            + "\n".join(f"  - {m}" for m in missing),
        )

    @covers("REQ-0.0.20-03-04")
    @covers("REQ-0.0.20-03-14")
    def test_manifest_allowlist_removes_attestation_enrichment_entry(self) -> None:
        """Manifest ``rules.unscoped_allowlist`` must not contain attestation-enrichment.md.

        OBPI-03's REQ-04 semantic is **absence of the attestation-enrichment.md
        entry** — not "manifest has exactly N entries". The count cascades as
        sibling OBPIs (04, 05) land; absence is the invariant this OBPI
        guarantees (matches ``test_agent_contract_fold`` precedent).
        """
        manifest = json.loads(
            (REPO_ROOT / ".gzkit" / "manifest.json").read_text(encoding="utf-8"),
        )
        allowlist = manifest.get("rules", {}).get("unscoped_allowlist", [])

        entry_files = {entry.get("file") for entry in allowlist}
        self.assertNotIn(
            ".gzkit/rules/attestation-enrichment.md",
            entry_files,
            "attestation-enrichment.md allow-list entry must be removed",
        )

    @covers("REQ-0.0.20-03-05")
    @covers("REQ-0.0.20-03-06")
    @covers("REQ-0.0.20-03-07")
    def test_no_inbound_references_to_legacy_paths_in_live_files(self) -> None:
        """No Bucket-1 (live) file may reference the retired rule path.

        REQ-05/06/07: inbound references must point at AGENTS.md § Attestation
        or docs/governance/arb-middleware.md. Roots listed in ``NON_LIVE_ROOTS``
        and files in ``NARRATION_GRANTS`` are excluded from the scan.

        "Live" is operationalized as git-tracked files — the committed governed
        surface. Untracked caches (``.ruff_cache``), the virtualenv, mkdocs
        ``site/`` output, and sibling git worktrees are not live state and are
        excluded by definition; scanning them also produced the whole-tree
        ``rglob`` blow-up (261k paths) that pushed this test past the
        test-health budget (test-isolation chore).

        Since GHI #779 the scan also catches a **bare** citation
        (``per attestation-enrichment.md``), which matched no full path and was
        therefore invisible regardless of any grant — three of the ten pointers
        repaired under GHI #778 had that shape.
        """
        offenders = _fold_guard.dead_pointer_offenders(
            legacy_paths=LEGACY_PATHS,
            narration_grants=NARRATION_GRANTS,
            non_live_roots=NON_LIVE_ROOTS,
            repo_root=REPO_ROOT,
        )
        self.assertFalse(
            offenders,
            "live files still reference retired attestation-enrichment paths:\n"
            + "\n".join(f"  - {o}" for o in offenders),
        )

    def test_no_stale_narration_grants(self) -> None:
        """Every narration grant must still protect a real reference (GHI #779).

        A grant is earned by a sentence that must name the retired file to say
        what it says. When that sentence goes, the grant does not — it stays as a
        blanket file-level exemption over a live surface, and the next dead
        pointer to land in that file is invisible. Measured at authoring: six of
        the seven ``docs/governance/`` grants on the sibling routing guard
        protected a string their file no longer contained, and two grants named
        paths that had been deleted from disk entirely.

        This does not make a file-level grant able to tell a live pointer from
        narration — that is the open half of GHI #779. It bounds the damage by
        refusing to keep a grant alive past the narration that justified it.
        """
        stale = _fold_guard.stale_narration_grants(
            legacy_paths=LEGACY_PATHS,
            narration_grants=NARRATION_GRANTS,
            repo_root=REPO_ROOT,
        )
        self.assertFalse(
            stale,
            "narration grants that protect nothing — remove them so the files "
            "are scanned like any other:\n" + "\n".join(f"  - {s}" for s in stale),
        )

    @covers("REQ-0.0.20-03-08")
    def test_vendor_mirrors_of_attestation_rule_were_removed_by_sync(self) -> None:
        """``gz agent sync control-surfaces`` removes the vendor mirrors.

        REQ-08: after canonical deletion + sync, the mirrors under
        ``.claude/rules/`` and ``.github/instructions/`` must not exist.
        """
        mirrors = (
            REPO_ROOT / ".claude" / "rules" / "attestation-enrichment.md",
            REPO_ROOT / ".github" / "instructions" / "attestation_enrichment.instructions.md",
        )
        still_present = [str(p.relative_to(REPO_ROOT)) for p in mirrors if p.exists()]
        self.assertFalse(
            still_present,
            f"vendor mirrors should auto-clean via sync; still present: {still_present!r}",
        )

    @covers("REQ-0.0.20-03-09")
    @covers("REQ-0.0.20-03-10")
    @covers("REQ-0.0.20-03-11")
    @covers("REQ-0.0.20-03-12")
    def test_unscoped_rules_validator_passes_post_fold(self) -> None:
        """``gz validate --unscoped-rules`` exits 0 post-fold.

        Calls the validator's public Python API directly (no subprocess)
        to keep the test in the unit tier per ``.gzkit/rules/tests.md``.
        Asserts result="pass" and exit_code=0. The allow-list cardinality
        is not this OBPI's invariant (it cascades as sibling folds land);
        absence of the attestation-enrichment entry is covered by
        ``test_manifest_allowlist_removes_attestation_enrichment_entry``.

        Satisfies REQ-09 (unscoped-rules exits 0), REQ-10 (no drift in the
        validate-all surface), REQ-11 (no ARB test regression from
        docstring rewrites — the validator iterates the same canonical
        rule set), and REQ-12 (no mkdocs-internal-link drift from the
        reference rewrites).
        """
        result = run_unscoped_rules(REPO_ROOT)

        self.assertEqual(result.result, "pass", f"validator failed: {result!r}")
        self.assertEqual(result.exit_code, 0, f"validator exit_code={result.exit_code}")
        # Allow-list cardinality is not this OBPI's invariant; absence of
        # the attestation-enrichment entry is covered elsewhere. The count
        # may drop to 0 as sibling fold OBPIs land.
        self.assertGreaterEqual(
            len(result.allowlist_entries),
            0,
            f"allow-list unexpectedly negative: {len(result.allowlist_entries)}",
        )

    @covers("REQ-0.0.20-03-15")
    @covers("REQ-0.0.20-03-16")
    def test_no_arb_schema_change_and_no_new_deps(self) -> None:
        """REQ-15/16: No ARB schema changes; no new deps / shell=True / dataclass.

        ARB receipt schemas (`arb_lint_receipt.schema.json`,
        `arb_step_receipt.schema.json`) remain unchanged — their ``$id``
        values are load-bearing and preserved verbatim. The new
        governance doc is markdown-only (no executable code). The test
        file itself holds the forbidden-pattern strings as detection
        targets only (string-assembled below).
        """
        lint_schema = REPO_ROOT / "data" / "schemas" / "arb_lint_receipt.schema.json"
        step_schema = REPO_ROOT / "data" / "schemas" / "arb_step_receipt.schema.json"
        self.assertTrue(lint_schema.is_file(), f"missing {lint_schema}")
        self.assertTrue(step_schema.is_file(), f"missing {step_schema}")

        lint_body = json.loads(lint_schema.read_text(encoding="utf-8"))
        step_body = json.loads(step_schema.read_text(encoding="utf-8"))
        self.assertEqual(lint_body.get("$id"), "gzkit.arb.lint_receipt.schema.json")
        self.assertEqual(step_body.get("$id"), "gzkit.arb.step_receipt.schema.json")

        middleware_doc = (REPO_ROOT / "docs" / "governance" / "arb-middleware.md").read_text(
            encoding="utf-8"
        )

        # String-assembled so this test does not match itself.
        forbidden = ("@" + "dataclass", "from " + "dataclasses", "shell" + "=True")
        offenders = [p for p in forbidden if p in middleware_doc]
        self.assertFalse(
            offenders,
            f"arb-middleware.md must be prose-only; found forbidden tokens: {offenders!r}",
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
            # stdlib, no new dependency: git ls-files scopes the live-files scan
            # in test_no_inbound_references_to_legacy_paths_in_live_files to the
            # tracked governed surface (never shell=True).
            "import subprocess",
            "import unittest",
            "from pathlib import Path",
            "from gzkit.",
            # Sibling test helper, not a dependency (GHI #779). The three fold
            # guards carried a byte-identical scan and grant block; the shared
            # module is where the ratchet and the bare-citation predicate live.
            # This clause's stated bar is "stdlib + gzkit-internal (no new dep)",
            # which an intra-package import satisfies exactly.
            "from . import _fold_guard",
        )
        non_conforming = [
            line for line in import_lines if not any(line.startswith(p) for p in allowed_prefixes)
        ]
        self.assertFalse(
            non_conforming,
            f"OBPI-03 may not introduce new imports: {non_conforming!r}",
        )


if __name__ == "__main__":
    unittest.main()
