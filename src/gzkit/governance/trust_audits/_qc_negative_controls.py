"""Negative-control fixtures + ``@enforces`` registrations for bound QC steps.

ADR-0.0.73 (OBPI-0.0.73-02) introduced these negative controls; ADR-0.0.74
(OBPI-0.0.74-16) re-authored them onto the single ``@enforces`` enforcement-claim
surface so the qc_binding audit and the meta-validator runner share ONE engine
(Boundary Invariant #6 — no second negative-control framework).

Each claim is split into:

* ``_build_<claim>() -> Path`` — builds the known violation in a fresh directory
  inside the runner-owned workspace and returns its path. The runner owns and
  removes that workspace after the entrypoint runs.
* ``_ep_<claim>`` (in ``_qc_nc_entrypoints.py``) — the production enforcement path the
  runner invokes as ``entrypoint(fixture())``.

Genuineness is structural (Boundary Invariant #7): the fixture NEVER calls the
validator; only the runner does, via ``entrypoint(fixture())``. The two formerly
forced controls (``rendition-freshness``, ``rendition-floor-coherence``) are now
UN-FORCED — their entrypoints pass no ``fail_closed=True`` (D1 — genuineness is
absolute).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.enforcement import create_fixture_tempdir, enforces, get_enforcement_registry

from . import _qc_nc_composite as _cx
from . import _qc_nc_corpus as _cr
from . import _qc_nc_entrypoints as _ep
from ._qc_claim_exemptions import QC_CLAIM_EXEMPTS

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _mkroot(slug: str) -> Path:
    """Return a fresh directory owned by the active enforcement runner."""
    return create_fixture_tempdir(prefix=f"gzkit-qc-nc-{slug}-")


#: Audit SUBJECT, not a resource path (GHI #938). `.github/skills` appears in
#: this module only as a member of the mirror roster a negative control writes
#: fixtures across, inside a temporary tree — never a location in this
#: repository. The literal names the population under test.
_AUDIT_SUBJECT_LITERALS: tuple[str, ...] = (".github/skills",)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    _write(path, "\n".join(json.dumps(record) for record in records) + "\n")


def _minimal_pyproject(root: Path) -> None:
    _write(root / "pyproject.toml", "[project]\nname = 'gzkit-qc-nc'\nversion = '0.0.0'\n")


def _build_empty(slug: str = "empty") -> Path:
    """Violation-by-absence: an empty project where the validator flags a missing artifact.

    DEPRECATED as a violation fixture (GHI #699 generator #2). A bare directory
    violates every claim at once, so the finding it produces is the validator's
    "missing artifact" branch — never the branch the claim actually names. Each
    remaining caller is being replaced by a minimal VALID project carrying exactly
    one planted violation; do not add new callers.
    """
    return _mkroot(slug)


def _build_cli_audit() -> Path:
    """Build a valid doc-coverage manifest whose one command has a mismatched manpage heading.

    `.gzkit.json` clears `ensure_initialized`; the manifest, index, and README Quick
    Start are all well-formed. The single violation is the manpage's H1 naming a
    different command. Without the manifest the command raises an uncaught
    FileNotFoundError, which also exits 1 — so the old empty fixture scored a crash
    as enforcement (GHI #699).
    """
    root = _mkroot("cli-audit")
    _write(root / ".gzkit.json", "{}\n")
    _write(
        root / "config" / "doc-coverage.json",
        json.dumps(
            {
                "version": "1.0.0",
                "description": "NC fixture manifest",
                "commands": {
                    "demo": {
                        "surfaces": {
                            "manpage": True,
                            "index_entry": True,
                            "operator_runbook": False,
                            "governance_runbook": False,
                            "docstring": False,
                        },
                        "governance_relevant": False,
                    }
                },
            },
            indent=2,
        )
        + "\n",
    )
    from gzkit.doc_coverage.manifest import MANPAGE_DIR, MANPAGE_INDEX  # noqa: PLC0415

    _write(root / MANPAGE_INDEX, "# Index\n\n- [demo](demo.md)\n")
    # The violation: the manpage documents a different command than it is named for.
    _write(root / MANPAGE_DIR / "demo.md", "# gz wrong-name\n")
    # A registered verb — `gz --help` is rejected by the Quick Start validator and
    # would add a second finding, defeating the one-violation isolation.
    _write(root / "README.md", "## Quick Start\n\n```bash\nuv run gz init\n```\n")
    return root


def _build_skill_audit() -> Path:
    """Build a mirrored skill whose SKILL.md omits the required `owner` field.

    All four mirror roots carry byte-identical copies so mirror drift does not add a
    second finding, and the canonical root is non-empty so the CANONICAL-ROOT-EMPTY
    branch does not fire. The one violation is the missing required field.
    """
    root = _mkroot("skill-audit")
    _write(root / ".gzkit.json", "{}\n")
    # Computed, not hardcoded: a literal date would silently drift past the
    # staleness window and add a second finding, re-degenerating the fixture.
    reviewed = datetime.now(tz=UTC).date().isoformat()
    skill = (
        "---\n"
        "name: demo-skill\n"
        "description: Demo skill for the negative control.\n"
        "lifecycle_state: active\n"
        f"last_reviewed: {reviewed}\n"
        "metadata:\n"
        "  skill-version: 0.1.0\n"
        # The violation: no `owner:` key.
        "---\n\n"
        "# demo-skill\n"
    )
    for mirror in (".gzkit/skills", ".agents/skills", ".claude/skills", ".github/skills"):
        _write(root / mirror / "demo-skill" / "SKILL.md", skill)
    return root


def _build_readiness_audit() -> Path:
    """Every REQUIRED readiness surface present except one.

    `required_failures` is evaluated independently of the score and eval conjuncts,
    so omitting exactly one required surface isolates that check: the required list
    has a single entry naming CLAUDE.md. An empty project failed all six at once
    and proved only that *something* was missing (GHI #699).
    """
    root = _mkroot("readiness-audit")
    _write(root / "AGENTS.md", "# Agents\n")
    # The violation: CLAUDE.md — the one required surface deliberately absent.
    _write(root / ".github" / "discovery-index.json", "{}\n")
    _write(root / "docs" / "user" / "reference" / "agent-input-disciplines.md", "# Disciplines\n")
    _write(
        root / "src" / "gzkit" / "templates" / "obpi.md",
        "## Objective\n\n## Allowed Paths\n\n## Denied Paths\n\n## Discovery Checklist\n",
    )
    return root


def _build_session_green_gate() -> Path:
    """Plant a pre-push hook whose entry is `gz check-config-paths`, not `gz check`.

    The claim is token-adjacency: a hook naming a *different* verb that merely starts
    with "gz check" does not run the session green gate. An absent config file proves
    only the existence branch and leaves that logic uncovered.
    """
    root = _mkroot("session-green-gate")
    _write(
        root / ".pre-commit-config.yaml",
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: gz-check\n"
        "        name: gz check\n"
        "        entry: gz check-config-paths\n"
        "        language: system\n"
        "        stages: [pre-push]\n",
    )
    return root


def _build_orientation_freshness() -> Path:
    """Wire both SessionStart hooks correctly, then omit one required section heading.

    Everything the audit checks except the heading set is satisfied, so the single
    finding is the heading regression (GHI #338) rather than three missing-file
    findings that never reach the heading or collector-wiring checks.
    """
    root = _mkroot("orientation")
    _write(
        root / ".claude" / "settings.json",
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "uv run python scripts/session_orientation.py",
                                }
                            ]
                        }
                    ]
                }
            }
        ),
    )
    _write(
        root / ".codex" / "hooks.json",
        json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "command": (
                                'uv run --cache-dir "$(git rev-parse --show-toplevel)'
                                '/.gzkit/cache/uv" python scripts/session_orientation.py'
                            )
                        }
                    ]
                }
            }
        ),
    )
    _write(
        root / "scripts" / "session_orientation.py",
        '"""Orientation stub."""\n\n'
        # The violation: "Git remote state" is absent from the heading set.
        'SECTION_HEADINGS = ("Repo state",)\n\n\n'
        "def collect_remote_state() -> dict:\n"
        '    """Collect remote state."""\n'
        "    return {}\n\n\n"
        "def collect_state() -> dict:\n"
        '    """Collect state."""\n'
        "    return collect_remote_state()\n",
    )
    return root


def _build_complexity_thresholds() -> Path:
    """Ship the real threshold table with one canonical metric's bands removed.

    Exercises the loader, the Pydantic contract, and the canonical-metric coverage
    check. An absent data file short-circuits before any of the three.
    """
    root = _mkroot("complexity-thresholds")
    import importlib.resources  # noqa: PLC0415

    source = importlib.resources.files("gzkit.rules").joinpath("complexity-thresholds.json")
    table = json.loads(source.read_text(encoding="utf-8"))
    table["bands"] = [b for b in table.get("bands", []) if b.get("metric") != "cohesion_lcom4"]
    _write(
        root / ".gzkit" / "rules" / "complexity-thresholds.json",
        json.dumps(table, indent=2) + "\n",
    )
    return root


def _build_line_endings() -> Path:
    """Present a .gitattributes whose directive is too weak to normalize line endings.

    `*.py text` exists but does not pin `eol=lf`, so the audit must flag the weak
    directive — a branch an absent file never reaches.
    """
    root = _mkroot("line-endings")
    _write(root / ".gitattributes", "*.py text\n")
    return root


def _build_authorship_policy() -> Path:
    """Declare an authorship policy that no git identity can satisfy.

    An absent `.gzkit.json` proves only that the scope no-ops for adopters who
    declare nothing — the branch this audit is FOR is a policy that binds. The
    suffix uses the reserved `.invalid` TLD (RFC 2606) so the control fires
    identically on every machine, whatever `user.email` that machine resolves —
    including one whose global config already satisfies gzkit's real policy.
    """
    root = _mkroot("authorship-policy")
    _write(
        root / ".gzkit.json",
        json.dumps({"authorship": {"required_email_suffix": "@qc-negative-control.invalid"}}),
    )
    return root


def _build_smoke_tier() -> Path:
    """Present a `tests/` tree that exists but declares no smoke member.

    An absent `tests/` proves only that the path is checked. The branch that
    matters is a populated project whose smoke tier is EMPTY — the
    green-by-emptiness case, where a budget gate passes because it measured
    nothing.
    """
    root = _mkroot("smoke-tier")
    _write(root / "tests" / "test_ordinary.py", "def test_nothing():\n    pass\n")
    # The project must OPT IN, or the empty tier is a passing advisory for
    # adopters rather than a breach — which would make this control vacuous.
    _write(root / ".gzkit.json", json.dumps({"smoke": {"required": True}}))
    return root


def _build_dispatch_absorption_marker() -> Path:
    """Present the pool ADR WITHOUT its absorption marker.

    The claim is that the ADR records `absorbed_into: ADR-0.0.73`. A missing file
    proves only that the path is checked, never that the marker is.
    """
    root = _mkroot("dispatch-absorption-marker")
    pool = root / "docs" / "design" / "adr" / "pool"
    _write(
        pool / "ADR-pool.obpi-pipeline-dispatch-attestation.md",
        "---\nid: ADR-pool.obpi-pipeline-dispatch-attestation\n---\n\n"
        "# OBPI pipeline dispatch attestation\n",
    )
    return root


# ---------------------------------------------------------------------------
# Per-claim violation fixtures
# ---------------------------------------------------------------------------


def _build_lint() -> Path:
    root = _mkroot("lint")
    _minimal_pyproject(root)
    _write(root / "bad.py", "import sys\n")
    return root


def _build_format() -> Path:
    root = _mkroot("format")
    _minimal_pyproject(root)
    _write(root / "bad.py", "x = [1,\n2]\n")
    return root


def _build_module_size() -> Path:
    """Violation: a module over the block band with no grandfather entry.

    The band is planted at 3 rather than the corpus p95 so the fixture module
    can be six lines instead of a thousand — the gate reads its threshold from
    the table, so a small table exercises the same code path a large one does.
    Omitting ``data/module_size_grandfather.json`` leaves the listed set empty,
    which isolates the "over the band and NOT listed" direction; the other three
    directions are driven by the gate's own ``--self-test``.
    """
    root = _mkroot("module-size")
    _write(
        root / ".gzkit" / "rules" / "complexity-thresholds.json",
        json.dumps(
            {
                "bands": [
                    {
                        "metric": "radon_raw_nloc",
                        "trigger_semantic": "block",
                        "absolute_number": 3,
                    }
                ]
            }
        ),
    )
    _write(root / "src" / "big.py", "".join(f"x{i} = {i}\n" for i in range(6)))
    return root


def _build_typecheck() -> Path:
    root = _mkroot("typecheck")
    _minimal_pyproject(root)
    _write(root / "bad.py", "name: str = 1\n")
    return root


def _build_test() -> Path:
    root = _mkroot("test")
    _write(
        root / "tests" / "test_failure.py",
        "import unittest\n\nclass TestFailure(unittest.TestCase):\n    def test_fails(self):\n"
        "        self.assertEqual(1, 2)\n",
    )
    return root


def _build_docs_build() -> Path:
    """Build a docs site whose nav names a page that does not exist.

    A missing nav target is only a WARNING to mkdocs; it fails the build solely
    because ``--strict`` promotes warnings to errors. That makes it the right
    violation for this claim: a control that made mkdocs fail some other way
    (malformed YAML, missing config) would stay green if ``--strict`` were ever
    dropped from the command, which is the exact regression the claim guards.

    This is the shape that shipped broken in this repo — a nav entry pointing at
    a manpage renamed in an earlier pass, green under ``gz check`` until someone
    ran the build by hand (2026-07-26).
    """
    root = _mkroot("docs-build")
    _write(root / "docs" / "index.md", "# Home\n")
    _write(
        root / "mkdocs.yml",
        "site_name: gzkit-qc-nc\nnav:\n  - Home: index.md\n  - Missing: absent-page.md\n",
    )
    return root


def _build_behave() -> Path:
    """Build a scenario whose step FAILS — not one whose step is merely undefined.

    The bare feature file made behave exit 1 with
    ``ConfigError: No steps directory``: a configuration bail before any scenario
    was evaluated, indistinguishable from a real failure at exit 1 (GHI #699). A
    steps module makes behave run the scenario and fail it on the assertion, which
    is the outcome the claim actually names.
    """
    root = _mkroot("behave")
    _write(
        root / "features" / "failing.feature",
        "Feature: failing\n  Scenario: fails\n    Given the step asserts false\n",
    )
    _write(
        root / "features" / "steps" / "demo_steps.py",
        "from behave import given\n\n\n"
        '@given("the step asserts false")\n'
        "def step_impl(context):\n"
        '    raise AssertionError("planted negative-control failure")\n',
    )
    return root


def _build_parity_check() -> Path:
    root = _mkroot("parity-check")
    _write(root / "docs" / "proposals" / "REPORT-TEMPLATE-airlineops-parity.md", "# Bad\n")
    return root


def _build_unscoped_rules() -> Path:
    root = _mkroot("unscoped-rules")
    _write(root / ".gzkit" / "manifest.json", '{"rules": {"unscoped_allowlist": []}}\n')
    _write(root / ".gzkit" / "rules" / "bad.md", '---\npaths: "**"\n---\n# Bad\n')
    return root


def _build_python_version_pins() -> Path:
    """Plant a CI interpreter declaration that contradicts ``.python-version``.

    The drift this audit exists to catch is invisible on a clean tree by
    construction: both sides stay green while CI tests a different interpreter
    than ``uv run`` uses. An audit for that class which only ever runs against
    an agreeing tree would reproduce the defect it was built to close, so it
    ships with a tree it must go red on.
    """
    root = _mkroot("python-version-pins")
    _write(root / ".python-version", "3.13.15\n")
    _write(root / "pyproject.toml", 'requires-python = ">=3.13"\n')
    _write(
        root / ".github" / "workflows" / "ci.yml",
        "jobs:\n  build:\n    steps:\n"
        "      - uses: actions/setup-python@v6\n"
        '        with:\n          python-version: "3.13.14"\n',
    )
    return root


def _build_status_writer_coverage() -> Path:
    """Plant a ``status:`` writer that bypasses the single invariant monitor.

    GHI #669 is about a guard whose coverage was ASSERTED rather than
    demonstrated — every writer routed through the monitor by convention, and
    nothing would have noticed the next one that did not. An audit for that
    class which only ever runs on a clean tree would reproduce the defect it
    was built to close, so it ships with a tree it must go red on.
    """
    root = _mkroot("status-writer-coverage")
    _write(
        root / "src" / "gzkit" / "commands" / "rogue_writer.py",
        "def promote_brief(content: str) -> str:\n"
        '    return _upsert_frontmatter_value(content, "status", "Completed")\n',
    )
    return root


def _build_transcribed_adr_counts() -> Path:
    """Plant a live transcribed OBPI count, plus the record that must survive.

    GHI #768's binding constraint is that a remedy must not falsify the
    archive: most of the 135 `N/M` figures under `docs/` are dated records that
    are CORRECT as history. So this control plants both poles — a live claim the
    audit must catch, and a historical one under a declared section that it must
    leave alone. A control planting only the violation would pass just as well
    against an audit that flagged everything, which is the blanket sweep the
    issue forbids.
    """
    root = _mkroot("transcribed-adr-counts")
    _write(
        root / "data" / "transcribed_count_surfaces.json",
        json.dumps(
            {
                "surfaces": [
                    {"path": "docs/governance/live.md", "historical_sections": ["Amendments"]}
                ]
            }
        ),
    )
    _write(
        root / "docs" / "governance" / "live.md",
        "# Campaign\n\n"
        "## Queue\n\n"
        "- [ ] `ADR-0.35.0-canon-entry-corpus-landing` is `Draft` 0/10 landed.\n\n"
        "## 9. Amendments (carried forward)\n\n"
        "- 2026-07-29: `ADR-0.35.0-canon-entry-corpus-landing` read 0/9 landed.\n",
    )
    return root


def _build_obpi_lifecycle_coherence() -> Path:
    """Seed one undisposed OBPI whose parent does not resolve and whose brief is absent.

    Proves the census can fail — a gate that cannot go red on a known-bad tree
    is green-by-emptiness, not evidence (GHI #584).
    """
    root = _mkroot("obpi-lifecycle-coherence")
    _write(
        root / ".gzkit" / "ledger.jsonl",
        json.dumps(
            {
                "schema": "gzkit.ledger.v1",
                "event": "obpi_created",
                "id": "OBPI-9.9.9-01-phantom",
                "ts": "2026-01-01T00:00:00+00:00",
                "parent": "ADR-9.9.9-vanished",
            }
        )
        + "\n",
    )
    return root


def _build_adr_status_freshness() -> Path:
    root = _mkroot("adr-status")
    _write(root / "docs" / "governance" / "GovZero" / "adr-status.md", "stale\n")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.1-example"
        / "ADR-0.0.1-example.md",
        "---\nid: ADR-0.0.1-example\nlane: Lite\nkind: foundation\n---\n# Example\n",
    )
    return root


def _build_pool_interview_schema() -> Path:
    """Violation: a pool interview record carrying the invented nested key.

    Plants the REAL drift shape rather than a degenerate one, per the doctrine
    ``_build_theater_signature_scan`` records: commit ``8b0a2f32`` found exactly
    this ``forcing_functions`` nested key on two committed records, where the
    CLI loader would have rejected it and the pool bucket had no reader to. It
    was repaired by hand with no guard left behind — PASS-on-violation here
    means the audit catches the actual class that shipped (GHI #719).
    """
    root = _mkroot("pool-interview")
    _write(
        root / "docs" / "design" / "adr" / "pool" / "sample-thing-interview.json",
        json.dumps(
            {
                "id": "ADR-pool.sample-thing",
                "title": "Sample Thing",
                "semver": "pool",
                "lane": "heavy",
                "parent": "ADR-0.8.0",
                "intent": "why",
                "decision": "what",
                "positive_consequences": "good",
                "negative_consequences": "bad",
                "checklist": "steps",
                "alternatives": "rejected",
                "forcing_functions": {"pre_mortem": "the shape 8b0a2f32 repaired"},
            }
        ),
    )
    return root


def _build_advisory_scorecard() -> Path:
    """Violation: a canonical rule absent from the scorecard's Coverage Ledger.

    The rule carries a valid ``<!-- rule-version: -->`` marker (a missing marker
    is `--rule-version-markers`' finding and this scope deliberately skips it, so
    an unmarked fixture would be hollow), and the scorecard mentions the rule's
    filename stem *in prose* without a ledger row. That last detail is the point:
    stem presence was the entire pre-GHI-754 check, so a fixture whose stem was
    absent would pass the old implementation too and prove nothing about the
    proxy having been removed.
    """
    root = _mkroot("advisory-scorecard")
    _write(
        root / ".gzkit" / "rules" / "sample-rule.md",
        "<!-- rule-version: 1.2.3 -->\n\n"
        "> **Rule version:** `1.2.3` — fixture.\n\n"
        "## Invariant\n\n**Something binding.**\n",
    )
    _write(
        root / "docs" / "governance" / "advisory-rules-audit.md",
        "# Advisory Rules Audit\n\n"
        "## Coverage Ledger\n\n"
        "| Rule file | Scored at rule-version |\n|---|---|\n\n"
        "### Sample Rule (`.gzkit/rules/sample-rule.md`)\n\n"
        "| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
        "| 1 | Something binding | **Judgment** | prose only |\n",
    )
    return root


def _build_advisory_scorecard_counts() -> Path:
    """Violation: a Summary roll-up whose counts contradict the rows beneath it.

    The fixture plants **both** poles, because a control that only plants a wrong
    count passes equally well against an audit that flags every scorecard. The
    `Promotable` row is transcribed correctly (1, and one row scores it) and must
    NOT be flagged; the `Mechanical` row claims 9 where the rows show 1.

    One scored row deliberately carries an escaped pipe inside a code span, which
    is what shifted the Score column and silently dropped three real rows from
    the first cut of this count. A fixture without one cannot tell a correct
    parse from a three-row undercount.
    """
    root = _mkroot("advisory-scorecard-counts")
    _write(
        root / ".gzkit" / "rules" / "sample-rule.md",
        "<!-- rule-version: 1.2.3 -->\n\n"
        "> **Rule version:** `1.2.3` — fixture.\n\n"
        "## Invariant\n\n**Something binding.**\n",
    )
    _write(
        root / "docs" / "governance" / "advisory-rules-audit.md",
        "# Advisory Rules Audit\n\n"
        "## Coverage Ledger\n\n"
        "| Rule file | Scored at rule-version |\n|---|---|\n"
        "| `sample-rule.md` | `1.2.3` |\n\n"
        "## Scorecard\n\n"
        "### Sample Rule (`.gzkit/rules/sample-rule.md`)\n\n"
        "| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
        "| 1 | Use `str \\| None` not `Optional[str]` | **Mechanical** | ruff UP007 |\n"
        "| 2 | Something tractable | **Promotable** | no reader yet |\n\n"
        "## Summary\n\n"
        "| Score | Rows | % |\n|---|---|---|\n"
        "| **Mechanical** | 9 | 90% |\n"
        "| **Promotable** | 1 | 10% |\n",
    )
    return root


def _build_advisory_scorecard_ruff_reachability() -> Path:
    """Violation: a **Mechanical** row citing a ruff code ruff would not run.

    The fixture plants all three poles, because a control that only plants an
    unreachable citation passes equally well against an audit that flags every
    row naming ruff:

    * Row 1 is **Mechanical** and cites a SELECTED code — must NOT be flagged.
    * Row 2 is **Mechanical** and cites an unselected one — the violation, and
      row 44's exact shape before `S602` was added to the select list.
    * Row 3 is **Judgment** and cites the same unselected code — must NOT be
      flagged. Naming a code you are not claiming to enforce is the honest
      disclosure this whole family exists to produce (`pythonic.md` § Imports
      does it with PLC0415's measured violations); a control without this pole
      cannot tell the score gate from a keyword scan.

    A `pyproject.toml` must be planted: with no readable ruff configuration
    `_ruff_selection` returns None and the arm reports nothing, which would make
    an otherwise-correct fixture a hollow control.
    """
    root = _mkroot("advisory-scorecard-ruff-reachability")
    _write(
        root / ".gzkit" / "rules" / "sample-rule.md",
        "<!-- rule-version: 1.2.3 -->\n\n"
        "> **Rule version:** `1.2.3` — fixture.\n\n"
        "## Invariant\n\n**Something binding.**\n",
    )
    _write(root / "pyproject.toml", '[tool.ruff.lint]\nselect = ["E", "F", "BLE"]\n')
    _write(
        root / "docs" / "governance" / "advisory-rules-audit.md",
        "# Advisory Rules Audit\n\n"
        "## Coverage Ledger\n\n"
        "| Rule file | Scored at rule-version |\n|---|---|\n"
        "| `sample-rule.md` | `1.2.3` |\n\n"
        "## Scorecard\n\n"
        "### Sample Rule (`.gzkit/rules/sample-rule.md`)\n\n"
        "| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
        "| 1 | No bare except | **Mechanical** | enforced by ruff BLE001 |\n"
        "| 2 | No shell=True | **Mechanical** | enforced by ruff S602 |\n"
        "| 3 | No lazy imports | **Judgment** | ruff PLC0415 is not enabled |\n",
    )
    return root


def _build_adr_taxonomy() -> Path:
    """Violation: a `kind: foundation` ADR carrying a feature semver.

    ADR-0.0.17 pins `kind: foundation` to `0.0.x`, so a `0.9.0` foundation is
    the kind/semver incoherence the taxonomy scope exists to refuse. The ADR
    tree must be planted — `audit_adr_taxonomy` returns clean on an absent
    `docs/design/adr/`, which would make an empty fixture a hollow control.
    """
    root = _mkroot("adr-taxonomy")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.9.0-example"
        / "ADR-0.9.0-example.md",
        "---\nid: ADR-0.9.0-example\nlane: Lite\nkind: foundation\nsemver: 0.9.0\n---\n# Example\n",
    )
    return root


def _build_adversarial_validation() -> Path:
    """Violation: a post-cutover heavy completion with no verdict, in a brief with no 4b section.

    Trips BOTH halves of the audit (GHI #676) — a control that exercised only the
    brief scan would leave the ledger-coherence half unproven, which is the half
    the issue was actually about.
    """
    root = _mkroot("adversarial-validation")
    obpi_id = "OBPI-0.0.1-01-example"
    _write(
        root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1-x" / "obpis" / f"{obpi_id}.md",
        f"---\nid: {obpi_id}\nlane: heavy\nstatus: Completed\n---\n\n### Key Proof\n\nran it.\n",
    )
    _write_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "obpi_receipt_emitted",
                "id": obpi_id,
                "ts": "2030-01-01T00:00:00+00:00",
                "receipt_event": "completed",
            }
        ],
    )
    return root


def _build_red_parity() -> Path:
    """Violation: a completed heavy-lane BEHAVIOR REQ with no RED witness.

    The completion receipt is stamped past the GHI #642 cutover so the brief is in
    scope; no `red_receipt_emitted` event is written, which is the finding.
    """
    root = _mkroot("red-parity")
    obpi_id = "OBPI-0.0.1-01-example"
    _write(
        root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1-x" / "obpis" / f"{obpi_id}.md",
        f"---\nid: {obpi_id}\nlane: heavy\nstatus: Completed\n---\n\n"
        "## Acceptance Criteria\n\n"
        "- [x] REQ-0.0.1-01-01 [behavior]: the system does X when Y\n",
    )
    _write_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "obpi_receipt_emitted",
                "id": obpi_id,
                "ts": "2030-01-01T00:00:00+00:00",
                "receipt_event": "completed",
            }
        ],
    )
    return root


def _build_producer_field_parity() -> Path:
    """Violation: a producer writes a payload field neither contract declares.

    The exact shape GHI #877 missed — ``_book_aborted_exit`` wrote ``aborted``
    on ``airlock_out`` while both contracts were silent. The fixture producer has
    never fired, so no row exists to parse: a committed-row fence is green here by
    construction, which is why this control is bound to the PRODUCER-side audit.
    """
    root = _mkroot("producer-field-parity")
    _write(
        root / "src" / "gzkit" / "producer.py",
        "from gzkit.ledger import LedgerEvent\n\n\n"
        "def emit() -> LedgerEvent:\n"
        '    return LedgerEvent(event="airlock_out", id="OBPI-X", '
        'extra={"undeclared_field": True})\n',
    )
    _write(
        root / "src" / "gzkit" / "schemas" / "ledger.json",
        json.dumps({"events": {"airlock_out": {"required": [], "properties": {}}}}),
    )
    return root


def _build_rendition_freshness() -> Path:
    root = _mkroot("rendition-freshness")
    _write(
        root / ".gzkit" / "corpus" / "AGENTS.md.jsonl",
        json.dumps(
            {
                "id": "entry-1",
                "surface": "AGENTS.md",
                "section": "attestation",
                "text": "some corpus content",
                "tier": "compressible",
                "classification": "Judgment",
                "origin": "negative-control",
                "ts": "2026-01-01T00:00:00+00:00",
            }
        )
        + "\n",
    )
    # A committed rendition with NO provenance sidecar over a real corpus: the
    # rendition's derivation from the corpus is unproven, so the gate MUST flag it.
    _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "root.md", "old\n")
    return root


def _build_rendition_floor_coherence() -> Path:
    root = _mkroot("rendition-floor")
    _write(
        root / ".gzkit" / "corpus" / "AGENTS.md.jsonl",
        json.dumps(
            {
                "id": "invariant-entry",
                "surface": "AGENTS.md",
                "section": "attestation",
                "text": "MUST APPEAR VERBATIM",
                "tier": "invariant",
                "classification": "Judgment",
                "origin": "negative-control",
                "ts": "2026-01-01T00:00:00+00:00",
            }
        )
        + "\n",
    )
    # A committed rendition that drops an invariant-tier entry MUST be flagged.
    _write(root / ".gzkit" / "renditions" / "AGENTS.md" / "root.md", "missing\n")
    return root


def _build_wheel_path_literals() -> Path:
    """Plant a wheel-shipped skill doc naming a path rooted in one user's home.

    The pyproject declares the include block itself rather than reusing a
    canned one, because the property under control is that the audit reads
    THAT block: a witness scoped by a transcribed glob would pass here while
    missing the next tree added to a real wheel (GHI #900).

    The same literal is also planted OUTSIDE the include block, so the control
    cannot pass on a scan that simply walks every Markdown file it can find.
    """
    root = _mkroot("wheel-path-literals")
    _write(
        root / "pyproject.toml",
        "[project]\nname = 'gzkit-qc-nc'\nversion = '0.0.0'\n\n"
        "[tool.hatch.build.targets.wheel]\n"
        'packages = ["src/gzkit"]\n'
        "include = [\n"
        '    "src/gzkit/skills/**/*.md",\n'
        "]\n",
    )
    _write(
        root / "src" / "gzkit" / "skills" / "nc-demo" / "SKILL.md",
        "# NC demo\n\nOpen `/Users/someone/Archive/corpus.zip` before deciding.\n",
    )
    _write(root / "docs" / "not-shipped.md", "Open `/Users/someone/Archive/corpus.zip`.\n")
    return root


def _build_validate_default_scopes() -> Path:
    """Build a canonical rule whose version marker disagrees with its block quote.

    Deliberately the `--rule-version-markers` violation shape: that default-tier
    scope was registered but unreachable from `gz check`, so a real marker
    mismatch survived eight days of green commits (GHI #744). The frontmatter is
    well-formed on purpose — an invalid rule would trip the `surfaces` scope
    instead, and the control must fail for the marker reason, not a parse error.
    """
    root = _mkroot("validate-default-scopes")
    _write(
        root / ".gzkit" / "rules" / "drifted.md",
        "---\n"
        "id: drifted\n"
        "description: Negative-control rule whose version marker disagrees.\n"
        "paths:\n"
        '  - "src/**"\n'
        "---\n\n"
        "<!-- rule-version: 1.0.1 -->\n\n"
        "> **Rule version:** `1.0.0` - drifted on purpose.\n\n"
        "# Drifted\n",
    )
    return root


def _build_invariant_coherence() -> Path:
    root = _mkroot("invariant-coherence")
    # A committed rendition that plays back to a non-empty AGENTS.md, with NO
    # committed AGENTS.md on disk: playback != committed (b"") is genuine drift.
    _write(
        root / ".gzkit" / "renditions" / "AGENTS.md" / "root.md",
        "# Rendered AGENTS.md\n\nPlayback body the committed surface does not carry.\n",
    )
    return root


def _build_brief_structure() -> Path:
    """Build a LIVE brief with no structured frontmatter — the gate MUST fire (GHI #615).

    Status is `Draft`, so the terminal-status exemption cannot swallow it: this
    fixture fails only if the scope has stopped enforcing `BriefStructure` on the
    live corpus, which is the exact regression the flip exists to prevent.
    """
    root = _mkroot("brief-structure")
    _write(
        root / "docs" / "design" / "adr" / "pkg" / "obpis" / "OBPI-0.0.99-01-legacy.md",
        "---\n"
        "id: OBPI-0.0.99-01-legacy\n"
        "parent: ADR-0.0.99-negative-control\n"
        "lane: Lite\n"
        "status: Draft\n"
        "---\n\n"
        "# OBPI-0.0.99-01-legacy: No structured frontmatter\n\n"
        "## Allowed Paths\n\n"
        "- `src/gzkit/alpha.py`\n",
    )
    return root


def _build_closeout_proof() -> Path:
    root = _mkroot("closeout-proof")
    _write(
        root / ".gzkit" / "ceremonies" / "ADR-0.0.99.ceremony.json",
        json.dumps(
            {
                "adr_id": "ADR-0.0.99",
                "started_at": "2026-06-16T00:00:00+00:00",
                "updated_at": "2026-06-16T00:00:00+00:00",
                "completed_at": None,
            }
        )
        + "\n",
    )
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.99"
        / "obpis"
        / "OBPI-0.0.99-01-closeout.md",
        "---\nid: OBPI-0.0.99-01-closeout\nparent: ADR-0.0.99\n---\n"
        "# Brief\n\n## Acceptance Criteria\n\n"
        "- [ ] REQ-0.0.99-01-01 [BEHAVIOR]: must have a covering test\n",
    )
    return root


def _build_kind_invariance() -> Path:
    root = _mkroot("kind-invariance")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.1-missing"
        / "ADR-0.0.1-missing.md",
        "# ADR-0.0.1 Missing\n",
    )
    return root


def _build_persona_witness() -> Path:
    """ADR whose Persona body is unsubstituted `{persona}` template residue.

    The fixture uses the token shape rather than an absent section on purpose:
    absence was always catchable in principle, whereas residue is what actually
    shipped past Gate 5 forty-four times, because `SafeDict.__missing__` renders
    an omitted template variable as its own literal token and no substance test
    recognised braces as scaffolding (GHI #741). A negative control that only
    proved the easy half would leave the real failure mode unwitnessed.
    """
    root = _mkroot("persona-witness")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "pre-release"
        / "ADR-0.1.0-residue"
        / "ADR-0.1.0-residue.md",
        "---\nid: ADR-0.1.0-residue\nkind: feature\nlane: lite\n---\n"
        "# ADR-0.1.0: Residue\n\n## Persona\n\n{persona}\n\n## Intent\n\nX.\n",
    )
    return root


def _build_interview_transcripts() -> Path:
    root = _mkroot("interviews")
    adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.88-no-transcript"
    _write(
        adr_dir / "ADR-0.0.88-no-transcript.md",
        "---\nid: ADR-0.0.88-no-transcript\nkind: foundation\nlane: Lite\n---\n"
        "# ADR-0.0.88\n\n## Decision\n\nNo embedded transcript here.\n",
    )
    _write(
        adr_dir / "obpis" / "OBPI-0.0.88-01-demo.md",
        "---\nid: OBPI-0.0.88-01-demo\nparent: ADR-0.0.88-no-transcript\n---\n# Brief\n",
    )
    return root


def _build_receipt_shape() -> Path:
    root = _mkroot("receipt-shape")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.36-attestation"
        / "ADR-0.0.36-attestation.md",
        "---\ndate: 2026-01-01\n---\n# ADR-0.0.36\n",
    )
    _write_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "obpi_receipt_emitted",
                "id": "receipt-bad",
                "ts": "2026-01-02T00:00:00+00:00",
                "attestor": "agent:auto",
                "evidence": {
                    "attestation_requirement": "optional",
                    "obpi_completion": "completed",
                },
            }
        ],
    )
    return root


def _build_insights_shape() -> Path:
    root = _mkroot("insights-shape")
    _write(root / ".gzkit" / "insights" / "agent-insights.jsonl", "{not-json}\n")
    return root


def _build_instructions_files_budget() -> Path:
    """Trip the scope's surviving fail-closed arm: survival-declaration drift.

    Repointed 2026-08-17. The char-budget arm is advisory under the operator's
    stay-until-1.0 ruling and returns no findings, so the previous fixture (a
    3-char AGENTS.md budget) asserted enforcement that no longer happens — worse
    than no control, because it reports a scope as witnessed while it is blind.
    The scope still fail-closes through ``audit_surface_delivery_witness`` on a
    malformed survival declaration, and that is what this control now mutates.
    """
    root = _mkroot("instr-budget")
    _write(root / "data" / "agents_md_survival_declaration.json", '{"surfaces": "not-a-mapping"}\n')
    return root


def _build_agents_md_map_conformance() -> Path:
    root = _mkroot("agents-md-map")
    _write(root / "src" / "gzkit" / "templates" / "agents.md", "## Worked example\nbad\n")
    return root


def _build_complexity_doctrine_links() -> Path:
    root = _mkroot("complexity-links")
    _write(
        root / ".gzkit" / "rules" / "complexity-doctrine.md",
        "See docs/governance/complexity/distilled-characteristics-missing.md "
        "§ nope (corpus revision 1).\n",
    )
    return root


def _build_req_kind_discipline() -> Path:
    root = _mkroot("req-kind")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.1-parent"
        / "obpis"
        / "OBPI-0.0.1-01-demo.md",
        "---\nid: OBPI-0.0.1-01-demo\nparent: ADR-0.0.1-parent\n---\n"
        "# Brief\n\n## Allowed Paths\n\n- `src/demo.py`\n\n## Acceptance Criteria\n\n"
        "- [ ] REQ-0.0.1-01-01 [BEHAVIOR]: must be tested\n",
    )
    return root


def _build_tautological_test_audit() -> Path:
    root = _mkroot("tautological")
    _write(
        root / "tests" / "test_bad.py",
        "import unittest\n\nclass TestBad(unittest.TestCase):\n    def test_bad(self):\n"
        "        open('x.txt').read()\n        self.assertTrue(True)\n",
    )
    return root


def _build_task_envelope_coherence() -> Path:
    root = _mkroot("task-envelope")
    _write_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "task_started",
                "ts": "2026-06-01T00:00:00+00:00",
                "obpi_id": "OBPI-0.0.1-01",
                "task_id": "TASK-0.0.1-01-01-01",
            },
            # A worklog event under an active TASK with no task_id, which
            # signature (a) must flag. Was `artifact_edited` until GHI #947
            # removed that type from `_TASK_WORKLOG_TYPES` (its producers carry
            # no `task_id` parameter, so gating it could only fail forever);
            # `gate_checked` is still gated and carries one, so this control
            # keeps proving the gate has teeth.
            {
                "event": "gate_checked",
                "ts": "2026-06-01T00:00:01+00:00",
                "obpi_id": "OBPI-0.0.1-01",
            },
        ],
    )
    return root


def _build_lock_exchange_coupling() -> Path:
    root = _mkroot("lock-exchange")
    _write_jsonl(
        root / ".gzkit" / "ledger.jsonl",
        [
            {
                "event": "obpi_receipt_emitted",
                "id": "OBPI-0.0.41-03-cutover",
                "ts": "2026-06-01T00:00:00+00:00",
            },
            {
                "event": "obpi_lock_released",
                "id": "OBPI-0.0.1-01-demo",
                "ts": "2026-06-01T00:00:01+00:00",
                "agent": "agent-a",
            },
        ],
    )
    return root


def _build_handoff_documents() -> Path:
    root = _mkroot("handoff-docs")
    _write(
        root / ".gzkit" / "handoffs" / "bad.md",
        "---\n"
        "mode: CREATE\n"
        "adr_id: ADR-0.0.72\n"
        "branch: main\n"
        "timestamp: '2026-06-16T00:00:00+00:00'\n"
        "agent: agent:test\n"
        "---\n"
        "## Current State Summary\n\n"
        "This malformed post-cutover handoff is missing required sections.\n",
    )
    return root


def _build_preflight() -> Path:
    """Build a stale pipeline marker in an INITIALIZED project.

    The marker was always planted, but without `.gzkit.json` the command bailed at
    `ensure_initialized` with "gzkit not initialized" — exit 1, same as a real
    finding, so the marker was never inspected (GHI #699).
    """
    root = _mkroot("preflight")
    _write(root / ".gzkit.json", "{}\n")
    _write(root / ".gzkit" / "ledger.jsonl", "")
    marker = {
        "obpi_id": "OBPI-0.0.1-01-demo",
        "updated_at": "2000-01-01T00:00:00+00:00",
    }
    _write(
        root / ".claude" / "plans" / ".pipeline-active-OBPI-0.0.1-01-demo.json",
        json.dumps(marker) + "\n",
    )
    return root


def _build_surface_fidelity() -> Path:
    root = _mkroot("surface-fidelity")
    _write(root / "AGENTS.md", "> See [missing](docs/missing.md#required-section)\n")
    return root


def _build_fidelity_presence() -> Path:
    root = _mkroot("fidelity-presence")
    _write(
        root
        / "docs"
        / "design"
        / "adr"
        / "foundation"
        / "ADR-0.0.1-blockless"
        / "ADR-0.0.1-blockless.md",
        "---\nid: ADR-0.0.1-blockless\nkind: foundation\nlane: Lite\n---\n"
        "# ADR-0.0.1-blockless\n\n## Decision\n\nNo Fidelity Assertions block here.\n",
    )
    return root


def _build_waiver_ratchet() -> Path:
    root = _mkroot("waiver-ratchet")
    # A surface grown past its committed shrink-ratchet baseline: the audit MUST flag it.
    _write(
        root / "data" / "waiver_ratchet_registry.json",
        '{"surfaces":[{"data_file":"data/bad_waivers.json",'
        '"mechanism":"shrink-ratchet","entries_path":"waivers","baseline_count":0}]}',
    )
    _write(root / "data" / "bad_waivers.json", '{"waivers":["grew","past","baseline"]}')
    return root


def _build_config_registry() -> Path:
    root = _mkroot("config-registry")
    # A registry on disk that NO registry declares: neither config_registry.json
    # nor the waiver-ratchet globs claim it, so it is the silent bypass the gate
    # exists to catch. The declared entry is planted valid and self-consistent so
    # the fixture fails for the undeclared-surface reason and not for a phantom
    # or an unverified owner -- failing for the wrong reason would prove nothing
    # about THIS claim.
    _write(
        root / "data" / "config_registry.json",
        '{"registries":{"config_registry.json":{"owner":"m.py","kind":"code","purpose":"self"}}}',
    )
    _write(root / "src" / "m.py", "# reads config_registry.json\n")
    _write(root / "data" / "undeclared_thresholds.json", "{}")
    return root


def _build_exemption_controls() -> Path:
    root = _mkroot("exemption-controls")
    # An EMPTY disclosed-list against a claim that has declared nothing: the
    # audit MUST flag it. Planting the list is what makes the fixture a
    # violation of THIS claim rather than of the audit's unreadable-evidence
    # arm -- a missing file would fail for the wrong reason and prove nothing
    # about the undeclared-claim rule.
    _write(root / "data" / "exemption_control_grandfather.json", '{"accepted_claims":[]}')
    return root


def _build_gate_callers() -> Path:
    root = _mkroot("gate-callers")
    # A chore shipping a gate script that no automatic surface invokes, and an
    # EMPTY accepted-list: the audit MUST flag it. The chore population is used
    # rather than the validate-scope population so the control fails for THIS
    # claim's own reason -- an uncalled gate -- instead of incidentally tripping
    # on the live registry's 75 explicit scopes being absent from a bare fixture.
    _write(root / "data" / "uncalled_gate_grandfather.json", '{"accepted_gates":[]}')
    _write(root / ".gzkit" / "chores" / "orphan-gate" / "check_thing.py", "# gate script\n")
    _write(root / "src" / "gzkit" / "quality.py", "# no caller here\n")
    return root


def _nc_facade_ep(_v: object) -> int:
    """FACADE entrypoint for enforcement-floor NC probe — always returns 0 (does not catch)."""
    return 0


def _nc_probe_fixture() -> None:
    """Inert fixture for the enforcement-floor NC probe."""
    return None


def _build_enforcement_floor() -> list:
    """Build a synthetic registry with one FACADE claim for the enforcement-floor NC.

    The meta-validator must detect the FACADE (facade_count > 0 = PASS for this NC).
    If run_meta_validator is gutted to skip FACADE detection, this returns 0 = FACADE.
    """
    from gzkit.enforcement import EnforcementClaimRecord  # noqa: PLC0415

    return [
        EnforcementClaimRecord(
            claim_id="nc-probe",
            fixture=_nc_probe_fixture,
            entrypoint=_nc_facade_ep,
            source_fn="_qc_negative_controls._nc_facade_ep",
            source_file=None,
            source_line=None,
        )
    ]


def _build_theater_signature_scan() -> Path:
    """Violation: a content-named validator that reads mtime instead of content.

    Plants the REAL facade shape (the repudiated ``rendition_freshness`` mtime
    tautology), not a degenerate one — so PASS-on-violation means the analyzer
    catches the actual pattern class, not a synthetic stand-in (GHI #657).
    """
    root = _mkroot("theater-sig")
    _write(
        root / "src" / "gzkit" / "planted.py",
        "def verify_content_freshness(p):\n    return p.stat().st_mtime\n",
    )
    return root


# ---------------------------------------------------------------------------
# Claim registration table — (claim_id, fixture, production entrypoint)
# ---------------------------------------------------------------------------

# Each tuple registers one enforcement claim through the single @enforces primitive
# (Boundary Invariant #6). "qc-binding" is registered separately in qc_binding.py
# (its entrypoint is the theater-signature detector that lives there).
_QC_NEGATIVE_CONTROL_TABLE: tuple[tuple[Any, ...], ...] = (
    ("lint", _build_lint, _ep._ep_lint),
    ("format", _build_format, _ep._ep_format),
    ("typecheck", _build_typecheck, _ep._ep_typecheck),
    ("module-size", _build_module_size, _ep._ep_module_size),
    ("test", _build_test, _ep._ep_test),
    ("behave", _build_behave, _ep._ep_behave),
    ("docs-build", _build_docs_build, _ep._ep_docs_build),
    ("skill-audit", _build_skill_audit, _ep._ep_skill_audit),
    ("parity-check", _build_parity_check, _ep._ep_parity_check),
    ("readiness-audit", _build_readiness_audit, _ep._ep_readiness_audit),
    ("cli-audit", _build_cli_audit, _ep._ep_cli_audit),
    ("unscoped-rules", _build_unscoped_rules, _ep._ep_unscoped_rules),
    ("python-version-pins", _build_python_version_pins, _ep._ep_python_version_pins),
    ("adr-status-freshness", _build_adr_status_freshness, _ep._ep_adr_status_freshness),
    (
        "pool-interview-schema",
        _build_pool_interview_schema,
        _ep._ep_pool_interview_schema,
        "forcing_functions",
    ),
    ("advisory-scorecard-coverage", _build_advisory_scorecard, _ep._ep_advisory_scorecard),
    (
        "advisory-scorecard-summary-drift",
        _build_advisory_scorecard_counts,
        _ep._ep_advisory_scorecard,
        "Mechanical says 9, rows show 1",
    ),
    (
        "advisory-scorecard-ruff-reachability",
        _build_advisory_scorecard_ruff_reachability,
        _ep._ep_advisory_scorecard,
        "row 2 is scored **Mechanical** and cites ruff S602",
    ),
    (
        "wheel-path-literals",
        _build_wheel_path_literals,
        _ep._ep_wheel_path_literals,
        "ships an instruction naming",
    ),
    (
        "validate-default-scopes",
        _build_validate_default_scopes,
        _ep._ep_validate_default_scopes,
        "marker=1.0.1 disagrees with block quote=1.0.0",
    ),
    (
        "status-writer-coverage",
        _build_status_writer_coverage,
        _ep._ep_status_writer_coverage,
    ),
    (
        "transcribed-adr-counts",
        _build_transcribed_adr_counts,
        _ep._ep_transcribed_adr_counts,
    ),
    (
        "obpi-lifecycle-coherence",
        _build_obpi_lifecycle_coherence,
        _ep._ep_obpi_lifecycle_coherence,
    ),
    ("adr-taxonomy", _build_adr_taxonomy, _ep._ep_adr_taxonomy),
    ("adversarial-validation", _build_adversarial_validation, _ep._ep_adversarial_validation),
    ("red-parity", _build_red_parity, _ep._ep_red_parity),
    ("producer-field-parity", _build_producer_field_parity, _ep._ep_producer_field_parity),
    ("rendition-freshness", _build_rendition_freshness, _ep._ep_rendition_freshness),
    (
        "rendition-floor-coherence",
        _build_rendition_floor_coherence,
        _ep._ep_rendition_floor_coherence,
    ),
    ("invariant-coherence", _build_invariant_coherence, _ep._ep_invariant_coherence),
    ("corpus-retirement-witness", _cr.build_retirement_witness, _ep._ep_corpus_retirement_witness),
    ("brief-structure", _build_brief_structure, _ep._ep_brief_structure),
    (
        "session-green-gate",
        _build_session_green_gate,
        _ep._ep_session_green_gate,
        "No stages: [pre-push] hook running 'gz check' declared",
    ),
    ("closeout-proof", _build_closeout_proof, _ep._ep_closeout_proof),
    ("kind-invariance", _build_kind_invariance, _ep._ep_kind_invariance),
    ("persona-witness", _build_persona_witness, _ep._ep_persona_witness),
    ("interview-transcripts", _build_interview_transcripts, _ep._ep_interview_transcripts),
    ("receipt-shape", _build_receipt_shape, _ep._ep_receipt_shape),
    (
        "orientation-freshness",
        _build_orientation_freshness,
        _ep._ep_orientation_freshness,
        "SECTION_HEADINGS does not contain `Git remote state`",
    ),
    ("insights-shape", _build_insights_shape, _ep._ep_insights_shape),
    (
        "instructions-files-budget",
        _build_instructions_files_budget,
        _ep._ep_instructions_files_budget,
    ),
    (
        "agents-md-map-conformance",
        _build_agents_md_map_conformance,
        _ep._ep_agents_md_map_conformance,
    ),
    (
        "complexity-doctrine-links",
        _build_complexity_doctrine_links,
        _ep._ep_complexity_doctrine_links,
    ),
    (
        "complexity-thresholds",
        _build_complexity_thresholds,
        _ep._ep_complexity_thresholds,
        "missing per-metric bands for canonical metric(s): cohesion_lcom4",
    ),
    ("req-kind-discipline", _build_req_kind_discipline, _ep._ep_req_kind_discipline),
    ("tautological-test-audit", _build_tautological_test_audit, _ep._ep_tautological_test_audit),
    ("task-envelope-coherence", _build_task_envelope_coherence, _ep._ep_task_envelope_coherence),
    ("lock-exchange-coupling", _build_lock_exchange_coupling, _ep._ep_lock_exchange_coupling),
    ("handoff-documents", _build_handoff_documents, _ep._ep_handoff_documents),
    ("preflight", _build_preflight, _ep._ep_preflight),
    ("surface-fidelity", _build_surface_fidelity, _ep._ep_surface_fidelity),
    (
        "line-endings",
        _build_line_endings,
        _ep._ep_line_endings,
        "lacks the `* text=auto eol=lf` LF-normalization directive",
    ),
    (
        "authorship-policy",
        _build_authorship_policy,
        _ep._ep_authorship_policy,
        "Commit authorship policy requires an address ending",
    ),
    ("smoke-tier", _build_smoke_tier, _ep._ep_smoke_tier),
    (
        "dispatch-absorption-marker",
        _build_dispatch_absorption_marker,
        _ep._ep_dispatch_absorption_marker,
    ),
    ("fidelity-presence", _build_fidelity_presence, _ep._ep_fidelity_presence),
    ("waiver-ratchet", _build_waiver_ratchet, _ep._ep_waiver_ratchet),
    ("config-registry", _build_config_registry, _ep._ep_config_registry),
    ("gate-callers", _build_gate_callers, _ep._ep_gate_callers),
    ("exemption-controls", _build_exemption_controls, _ep._ep_exemption_controls),
    ("enforcement-floor", _build_enforcement_floor, _ep._ep_enforcement_floor),
    (
        "theater-signature-scan",
        _build_theater_signature_scan,
        _ep._ep_theater_signature_scan,
    ),
    # --- composite-claim decomposition (GHI #699 generator #4) -------------
    # Same production entrypoint as the parent claim; each row plants ONE of the
    # invariants the parent's single fixture never reached, pinned by `expect`.
    (
        "surface-fidelity-bullet-retention",
        _cx.build_bullet_retention,
        _ep._ep_surface_fidelity,
        "Bullet-retention violation: invariant-tier",
    ),
    (
        "surface-fidelity-surface-weight",
        _cx.build_surface_weight,
        _ep._ep_surface_fidelity,
        "Surface weight in red band",
    ),
    (
        "task-envelope-subdivision",
        _cx.build_task_envelope_subdivision,
        _ep._ep_task_envelope_coherence,
        "closed with only seq=01 TASKs",
    ),
    (
        "task-envelope-layer-drift",
        _cx.build_task_envelope_layer_drift,
        _ep._ep_task_envelope_coherence,
        "Signature (c): layer-drift across discovery channels",
    ),
    (
        "task-envelope-obpi-divergence",
        _cx.build_task_envelope_obpi_divergence,
        _ep._ep_task_envelope_coherence,
        "carries divergent obpi_id across lifecycle events",
    ),
    (
        "waiver-ratchet-closed-set-lock",
        _cx.build_waiver_closed_set_lock,
        _ep._ep_waiver_ratchet,
        "entries lack a non-empty 'added_under'",
    ),
    (
        "waiver-ratchet-dated-cutover",
        _cx.build_waiver_dated_cutover,
        _ep._ep_waiver_ratchet,
        "which is in the future (",
    ),
    (
        "waiver-ratchet-silent-bypass",
        _cx.build_waiver_silent_bypass,
        _ep._ep_waiver_ratchet,
        "exists on disk but is not declared in data/waiver_ratchet_registry.json",
    ),
    # handoff-documents composite: the parent fixture plants missing-sections;
    # this sibling plants the present-but-empty invariant validate_sections_populated
    # enforces, pinned so a missing-section failure cannot stand in for it (GHI #698).
    (
        "handoff-documents-populated-sections",
        _cx.build_handoff_populated_sections,
        _ep._ep_handoff_documents_populated,
        "Empty required section",
    ),
)

# The known-claims set the @enforces decorator validates against at decoration time.
# Includes every NC id above + "qc-binding" (registered in qc_binding.py). Defined
# BEFORE the registration loop so the re-entrant _load_known_claims() lookup resolves.
_KNOWN_QC_CLAIM_IDS: frozenset[str] = frozenset(
    {entry[0] for entry in _QC_NEGATIVE_CONTROL_TABLE} | {"qc-binding"}
)


def _register_marker() -> None:
    """Inert carrier for @enforces registration (the fixture/entrypoint are the contract)."""


def register_qc_negative_controls() -> None:
    """Register the qc negative-control claims via the @enforces primitive (idempotent).

    Called at import time and re-callable after ``reset_enforcement_registry()`` so the
    production claims survive test resets. Skips any claim already registered.
    """
    existing = {r.claim_id for r in get_enforcement_registry()}
    for entry in _QC_NEGATIVE_CONTROL_TABLE:
        claim_id, fixture, entrypoint = entry[0], entry[1], entry[2]
        expect = entry[3] if len(entry) > 3 else None
        if claim_id in existing:
            continue
        enforces(claim_id, fixture, entrypoint, expect, exempts=QC_CLAIM_EXEMPTS.get(claim_id))(
            _register_marker
        )


register_qc_negative_controls()
