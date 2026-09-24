# Plan — OBPI-0.35.0-14-meaning-preserving-landing

## Context

Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-14-meaning-preserving-landing.md`.
Parent: ADR-0.35.0 § Decision item 10, "NO LANDING LOSES MEANING WITHOUT AN APPROVED DROP" (operator rulings 2026-09-24; GHI #1090, #1091).

`gz content commit` (`src/gzkit/commands/content/commit.py`) promotes a staged candidate after three checks: candidate present, corpus present, attestation present when the corpus moved. Nothing compares the candidate with the prior committed rendition. That is how the 2026-09-17 compression landed 23 binding losses, measured in the 2026-09-24 compression sweep record (GHI #1091). This plan adds the retention gate between those checks and the first write.

## Files

- `src/gzkit/content/retention.py` — CREATE. Pure core: stdlib + Pydantic only, no subprocess, network or LLM.
- `src/gzkit/commands/content/commit.py` — call the gate, write or remove the sidecar
- `src/gzkit/commands/content/__init__.py` — `--retention-map` flag in the commit parser registration, help text and epilog, exit-3 documentation
- `tests/content/test_retention.py` — CREATE
- `tests/commands/test_content_commit.py` — extend
- `features/content_commit_retention.feature` — CREATE
- `features/steps/content_commit_retention_steps.py` — CREATE
- `docs/user/manpages/content.md` — commit section
- `.gzkit/skills/gz-content-compose/SKILL.md` — wielding skill. Its three mirrors are regenerated only by `uv run gz agent sync control-surfaces`.
- the brief itself (Evidence / Change Log only)

Read, never written: the ledger event module and schema, the rendition store, the corpus model, the remember, retire and compose commands, the lineage module, the corpus and rendition stores and root AGENTS.md.

## Steps

1. **Retention core (REQ-02, REQ-03, REQ-06 at the unit level; brief Requirements 2, 3, 6, 7).** In `src/gzkit/content/retention.py`:
   - a block splitter: headings, paragraphs, list items and table rows; a fenced code block is one block. LF-normalized, trailing whitespace stripped per line.
   - a removed-block delta: prior blocks whose normalized text is not a substring of the normalized candidate.
   - a sentence splitter, applied after list markers and heading hashes are stripped.
   - frozen, extra-forbid Pydantic models for the map, block, condition and non-binding declaration. Condition ids are unique within a map, and the disposition is a kept/dropped literal.
   - a validator returning EVERY violation (brief Requirement 3).
   - a sidecar path helper mirroring the lineage path helper.

   TDD: one behavior per test, and each red must be an assertion-level failure from a stub that imports cleanly.

2. **Commit integration (REQ-01, REQ-04, REQ-05, REQ-06 end to end; brief Requirements 1, 4, 5, 8).**
   - In `src/gzkit/commands/content/commit.py`, after the existing three checks and before the first write:
     - read the committed rendition when the file exists; the vacuous branch tests for the file's absence, and an unreadable file is exit 2;
     - compute the removed blocks;
     - if any exist, require `--retention-map`, load it (exit 1 on malformed JSON or a schema error), and validate it against the candidate and the effective attestation text;
     - on violations, exit 3 with every violation, the first line of each removed block and three-part recovery prose, writing nothing;
     - on success, write the sidecar in the write sequence; with no removed blocks, remove any stale sidecar.
   - In `src/gzkit/commands/content/__init__.py`: the flag, its help text and example, and exit 3 in the description.
   - Tests in `tests/commands/test_content_commit.py`:
     - refusal without a map, and nothing written, observed by the absence of the rendition, provenance, sidecar and ledger event;
     - every violation reported;
     - drop id absent from the attestation → 3; present → 0 with the sidecar written;
     - the vacuous cases: first commit, re-render, add-only, reorder, whitespace-only;
     - the #1090 replay fixture, built from line 234 of AGENTS.md at `c3582975f` and the compressed bullet, copied in as literals with their provenance cited;
     - existing refusals unchanged.

3. **BDD (Gate 4).** `features/content_commit_retention.feature` and `features/steps/content_commit_retention_steps.py`, with `@REQ-0.35.0-14-01`, `-04`, `-05` and `-06` scenarios: lossy candidate refused, approved drop lands, re-render unaffected, #1090 replay refused. They follow the conventions of the existing content step modules.

4. **Docs and skill (REQ-07, SUPPORT).**
   - `docs/user/manpages/content.md` commit section: flag, map schema, sidecar, exit 3, recovery.
   - `.gzkit/skills/gz-content-compose/SKILL.md`:
     - before commit, dispatch an independent reviewer (a different model from the author where one is available) to extract conditions from each removed block;
     - the author maps them;
     - present every DROPPED condition to the operator by id and obtain the operator's words before commit.
   - Then `uv run gz agent sync control-surfaces`.

5. **BI-10 (REQ-08, STRUCTURAL-FENCE).** Expose the gate as one function taking the root, surface, consumer, candidate text, map path and attestation text, so that OBPI-07's orchestrator can call it without the CLI. No unit test: the fence is audited at ADR closeout.

6. Record the Change Log and evidence in the brief. Stage 3 verification follows.

## Verification

```bash
uv run -m unittest tests.content.test_retention tests.commands.test_content_commit
uv run -m behave features/content_commit_retention.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz cli audit
uv run mkdocs build --strict
```

## Notes — Step 6a disclosures

- **Destination in mind before this plan:** a gate at `gz content commit` over the prior-rendition delta, with a JSON retention map checked byte-for-byte and a sidecar beside the lineage map. That was formed while amending the ADR, before this plan was written, and this plan reconstructs it. It was chosen over the corpus-retirement gate because the #1090 clause was never a corpus entry.
- **Rejected alternatives:**
  - a gate inside the retire or remember verbs — misses non-corpus losses, and BI-06 forbids refusing capture;
  - storing the map in the frozen provenance model — BI-03, § Alternatives O;
  - an LLM call inside the tool to extract conditions — § Alternatives L, non-determinism at the canon layer;
  - recording a retention digest on the rendition_committed ledger event — the ledger event module is a registered security surface, so this is deferred and disclosed;
  - a fuzzy similarity check between old and new blocks — it cannot tell a dropped qualifier from a rewording, which is the exact failure this gate exists to catch.
