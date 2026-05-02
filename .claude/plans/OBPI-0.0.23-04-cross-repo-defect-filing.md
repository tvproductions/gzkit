# Plan — OBPI-0.0.23-04 Cross-repo defect filing wrapper

**OBPI:** OBPI-0.0.23-04-cross-repo-defect-filing
**Parent ADR:** ADR-0.0.23-agent-failure-mode-taxonomy
**Lane:** Heavy (per ADR Decision §4 lift; brief frontmatter `lane: Heavy`)
**Kind:** foundation (parent ADR-0.0.23 ⇒ brief-level Gate 5 attestation required)

## Context

GHI #316 surfaced the `Safeguard circumvention` failure mode at the cross-repo
defect-filing surface: when an agent inside a consumer repo finds a defect in a
gzkit-owned artifact (the `gz` CLI, schemas, validators, ledger semantics,
`.gzkit/**`, `src/gzkit/**`), it must file the GHI at `tvproductions/gzkit` with
a provenance trailer — not at the consumer's tracker, not as an
`agent-insights.jsonl` entry.

This OBPI lands the doctrine subsection, the wrapper, the manpage, the BDD
scenario, the runbook entry, and the synced mirror surface in one Heavy-lane
patch.

### Design decisions (confirmed by operator: A1 + B1)

- **Body validation (REQ-06): hard-reject (exit 1).** Closes the misrouting
  failure class structurally — agent cannot file a misrouted issue even by
  accident. One BDD path. (DO IT RIGHT #3 — prefer the more thorough fix.)
- **`--dry-run` affordance: yes.** Emits composed body + target repo + label to
  stdout, skips `gh issue create`. Honors the brief's verification list
  verbatim and lets operators preview before live filing.

### Out-of-scope notes

- ADR-0.0.23 frontmatter says `lane: lite` while §4 lifts this item to heavy.
  Internally consistent (Decision text is canon); not a defect to fix here.
- `tests/commands/test_issue_cmd.py`, `src/gzkit/commands/issue_cmd.py`,
  `docs/user/manpages/gz-issue.md` are listed as `contested` by 255 paper
  overlaps from never-started ADR-0.31.x / ADR-0.34.x OBPIs. None are active
  locks. Disposition: advisory; this OBPI claims the paths first.
- Operator email never enters auto-stamped trailer (REQ-08): trailer composes
  only `<owner>/<repo>` slug + `gz vX.Y.Z` — no email surface to leak.

## Files

### Created

- `src/gzkit/commands/issue_cmd.py` — `issue_file_cmd` handler:
  - `derive_consumer_slug(cwd: Path) -> str` — read `git remote -v`, pick
    `origin` (fallback: first remote), parse SSH (`git@github.com:owner/repo.git`)
    and HTTPS (`https://github.com/owner/repo.git`) forms, strip `.git`, return
    `owner/repo`. Raise `ValueError` with diagnostic when no remote exists.
  - `derive_gzkit_version() -> str` — read `gz --version` from `importlib.metadata`
    (or the existing version-resolving helper used by `gz roles`/`gz cli audit`).
  - `compose_body(user_body: str, slug: str, version: str) -> str` — prepend
    `Filed from <slug> running gz vX.Y.Z\n\n` to the user body.
  - `validate_gzkit_surface_reference(body: str) -> None` — hard-reject (exit 1)
    when no marker matches `\bgz\s+\w`, `\.gzkit/`, `src/gzkit/`, `gzkit\.`. Raise
    `IssueValidationError` with diagnostic naming all checked markers.
  - `file_issue(title, body, label, dry_run)` — compose body, validate, then
    either dry-run to stdout (composed body + `Target: tvproductions/gzkit` +
    `Label: <defect|enhancement>`) or invoke
    `subprocess.run(["gh", "issue", "create", "--repo", "tvproductions/gzkit",
    "--title", title, "--body", composed, "--label", label], check=False,
    capture_output=True, text=True, encoding="utf-8")` and propagate exit code.
  - Use Pydantic `BaseModel` (`frozen=True, extra="forbid"`) for the internal
    request/response shapes per `.claude/rules/models.md`.
  - Module size ≤600 lines, function size ≤50 lines per `.claude/rules/pythonic.md`.

- `tests/commands/test_issue_cmd.py` — `unittest.TestCase` suites:
  - `TestDeriveConsumerSlug` — SSH form, HTTPS form, `.git` suffix stripping,
    multi-remote (origin precedence), missing-remote error, `git` not on PATH.
  - `TestComposeBody` — trailer shape, blank line separation, body preserved
    verbatim, no email leakage when body contains `Co-Authored-By` etc.
  - `TestValidateGzkitSurfaceReference` — hits each marker (`gz `, `.gzkit/`,
    `src/gzkit/`, `gzkit.`), miss case raises with diagnostic.
  - `TestFileIssueDryRun` — composed body + target + label printed; `gh` never
    invoked (assert via `mock.patch("subprocess.run")` call count == 0).
  - `TestFileIssueLive` — `subprocess.run` mocked; assert correct argv
    (`--repo tvproductions/gzkit`, label flag, composed body); non-zero `gh`
    exit propagates to the wrapper exit code.
  - All tests carry `@covers("REQ-0.0.23-04-NN")` decorators per the
    Stage 3 Phase 1b parity gate (`.gzkit/rules/tests.md`).
  - Each REQ has at least one assertion.

- `docs/user/manpages/gz-issue.md` — manpage per `.claude/rules/cli.md` Heavy
  Lane § New Subcommand:
  - DESCRIPTION, USAGE, OPTIONS (`--title`, `--body`, `--enhancement`,
    `--defect`, `--dry-run`), EXIT CODES (0/1/2/3 per `.claude/rules/cli.md`),
  - Documents the hard-reject behavior for non-gzkit-surface bodies.
  - At least one EXAMPLES entry showing dry-run preview output.

- `docs/user/commands/issue-file.md` — command-doc parallel to other
  `docs/user/commands/*.md` entries (mirrors manpage shape; required by
  `gz cli audit`).

- `features/issue_file.feature` — BDD scenarios:
  - `@REQ-0.0.23-04-04` — provenance auto-stamp end-to-end (composed body,
    correct slug, correct version) using a fixture git remote.
  - `@REQ-0.0.23-04-05` — issue is routed to `tvproductions/gzkit` regardless
    of the consumer's `git remote`.
  - `@REQ-0.0.23-04-06` — body lacking gzkit-surface markers is hard-rejected
    with exit 1 and diagnostic naming the markers.
  - All scenarios use `--dry-run` to avoid live tracker contact.

- `features/steps/issue_file_steps.py` — step definitions consuming the
  fixture `git remote` and the `gh` subprocess mock.

### Modified

- `src/gzkit/cli/parser_artifacts.py` — register top-level `issue` verb
  (alongside existing `adr`, `obpi`, `task`, `justify`):
  - `p_issue = commands.add_parser("issue", help="...", description="...",
    epilog=build_epilog([...]))` (target ~line 188, before
    `_register_adr_parsers`); add `issue_commands = p_issue.add_subparsers(...)`,
    `required=True`.
  - `p_issue_file = issue_commands.add_parser("file", ...)` with
    `--title` (required), `--body` (required), mutually-exclusive
    `--enhancement` / `--defect` group (default `--defect`), `--dry-run` flag.
  - `p_issue_file.set_defaults(func=lambda a: _lazy("issue_cmd")(...))`.
  - Add a new top-level registrar `_register_issue_parsers(commands)` callable
    invoked from the existing top-level `register_artifact_parsers` entry.

- `.gzkit/rules/gh-cli.md` — author § "Cross-repo filing" subsection per
  REQ-01; bump body-level `<!-- rule-version: -->` marker AND visible
  `> **Rule version:**` block quote (minor bump 0.x.0 → 0.x+1.0) per
  `.claude/rules/skill-surface-sync.md` § Version discipline.

- `docs/user/commands/index.md` (or canonical command index file —
  `gz cli audit` will name the right path if I miss) — add `gz issue file`
  entry per `.claude/rules/cli.md` § Consistency.

- `docs/user/runbook.md` — add cross-repo filing flow entry routing operators
  through `gz issue file` for gzkit-surface defects.

### Generated mirrors (touched only by `gz agent sync control-surfaces`)

- `.claude/rules/gh-cli.md`
- `.github/instructions/gh-cli.md`

## Steps

1. **TDD red.** Author `tests/commands/test_issue_cmd.py` covering REQs 04, 05,
   06, 07. Run `uv run -m unittest tests.commands.test_issue_cmd -v` — confirm
   tests fail with "module not found" (red).
2. **Implement command module.** Author `src/gzkit/commands/issue_cmd.py` with
   the five helpers above. Wire `IssueValidationError` to exit 1.
3. **Register CLI verb.** Edit `parser_artifacts.py` to add `issue` /
   `issue file` parser group. Run `uv run gz issue file --help` — confirm exit 0
   and option list.
4. **TDD green.** Re-run `uv run -m unittest tests.commands.test_issue_cmd -v`.
   Confirm all REQs pass. Run `uv run gz arb step --name unittest -- uv run -m
   unittest tests.commands.test_issue_cmd -v` to mint receipts.
5. **Author manpage and command doc.** Write `docs/user/manpages/gz-issue.md`
   and `docs/user/commands/issue-file.md`. Add index entry. Run
   `uv run gz cli audit` — confirm exit 0.
6. **Author rule subsection.** Add § "Cross-repo filing" to
   `.gzkit/rules/gh-cli.md`. Bump body marker + block quote (minor bump). Add
   front-matter `paths:` entry covering `src/gzkit/commands/issue_cmd.py` if
   the rule schema requires it (verify by reading existing rule frontmatter).
7. **Sync mirrors.** Run `uv run gz agent sync control-surfaces`. Verify
   `.claude/rules/gh-cli.md` and `.github/instructions/gh-cli.md` mirror the
   new subsection and bumped version.
8. **Author BDD feature + steps.** Write `features/issue_file.feature` and
   `features/steps/issue_file_steps.py` covering REQs 04, 05, 06. Run
   `uv run -m behave features/issue_file.feature` — green.
9. **Update runbook.** Add cross-repo filing flow entry to
   `docs/user/runbook.md`.
10. **Verify all gates.** Run baseline ARB-wrapped sweep (lint, typecheck,
    unittest, mkdocs, behave). Run `uv run gz validate --documents
    --surfaces --brief-headings --behave-req-tags`. Run `uv run gz covers
    OBPI-0.0.23-04-cross-repo-defect-filing --json` and confirm
    `uncovered_reqs == 0`.

## Verification

Per the brief's Verification section:

```bash
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz validate --brief-headings
uv run gz validate --behave-req-tags
uv run gz cli audit
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
test -f .gzkit/rules/gh-cli.md
test -f src/gzkit/commands/issue_cmd.py
test -f docs/user/manpages/gz-issue.md
test -f features/issue_file.feature
test -f tests/commands/test_issue_cmd.py
```

Plus the unlanded-verb checks (post-implementation):

```bash
uv run gz --help | grep -E '^\s+issue\b'
uv run gz issue --help
uv run gz issue file --help
uv run -m behave features/issue_file.feature
uv run gz issue file --title "smoke" --body "gzkit surface: validator scope X" --enhancement --dry-run
```

REQ-level dispatch (Stage 3 Phase 2): each REQ maps to one or more tests in
`tests/commands/test_issue_cmd.py` and one BDD scenario in
`features/issue_file.feature`. Test paths are non-overlapping → parallel
verification subagent dispatch is safe per the OBPI-pipeline Phase 2 rules.

## Notes

### Destination-in-mind (Step 6a disclosure)

I had a fully-formed approach before authoring this plan: (1) hard-reject
validation closes the failure class, (2) `--dry-run` mirrors the brief's
verification command verbatim, (3) the verb registers in `parser_artifacts.py`
because it's an artifact-domain verb (issue authorship), (4) `subprocess.run`
list-form invocation of `gh` per `.claude/rules/cross-platform.md`. The
operator confirmed A1+B1 in the prior turn, which matched the recommendation.

### Rejected alternatives considered during exploration

- **Warn-and-confirm validation (REQ-06 alt B).** Rejected because warn-and-
  confirm leaves the misrouting class open — an operator can suppress the
  warning. Hard-reject is the more thorough fix per DO IT RIGHT #3.
- **Use `requests` or PyGitHub directly instead of the `gh` binary.** Rejected
  because `gh` is already on PATH, handles auth, and Stdlib-First doctrine
  forbids new runtime deps without ADR-attested rationale.
- **Register `issue` under `parser_governance.py` next to `register-adrs`.**
  Rejected because governance verbs handle artifact-graph operations
  (closeout, attest, gates), while `issue` is artifact authorship — fits
  naturally beside `adr` / `obpi` / `task` in `parser_artifacts.py`.
- **Skip `--dry-run` and rely solely on BDD assertions (B2).** Rejected
  because the brief's verification command list explicitly invokes
  `--dry-run` and a preview affordance is operationally useful; B2 was
  acceptable per the brief but B1 is the higher-value path.
- **Lift the ADR frontmatter from `lite` to `heavy` in this OBPI.** Rejected
  as out-of-scope — ADR Decision §4 already names the lift; frontmatter
  reconciliation belongs in a separate `fix(adr-0.0.23): ...` commit if
  defect-fix routing thresholds support it.

### Files outside the brief allowlist

None planned. Mirror files are touched by `gz agent sync control-surfaces`,
not hand-edited.
