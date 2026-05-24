---
id: ADR-pool.captured-stdout-receipt-binding
status: Pool
lane: heavy
parent:
---

# ADR-0.46.0-captured-stdout-receipt-binding: Captured-Stdout Receipt Binding

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change to the
ARB receipt schema and the manpage-EXAMPLES verification surface.

## Intent

Bind ARB receipts to their captured stdout (and stderr) so manpage
EXAMPLES blocks, runbook command snippets, and any other doc surface
that claims "real CLI output" can be mechanically cross-checked against
the bytes the command actually produced.

AGENTS.md § Prime Directive item 2 already names the principle: *"ensure
manpage EXAMPLES section shows real CLI output, not placeholders."* But
the principle has no mechanical floor — there is no check that the bytes
in an EXAMPLES block came from a real run, and no way to bind a doc
example to the receipt that produced it. Today's `gz cli audit` verifies
manpage parity (every CLI verb has a manpage) but not example fidelity
(the manpage's EXAMPLES match real runtime output).

This is the same shape as ADR-0.0.24 (attestation receipt binding) one
layer earlier: the citation surface (attestation, EXAMPLES block, runbook
prose) makes a claim about a command's output; the binding gate verifies
the claim against the receipt. ADR-0.0.24 closed the gap on attestation
strings; this ADR closes the gap on doc-surface examples.

External evidence: GPT-5.5 § 9.2 (Apollo) reports 29% Impossible Coding
Task lying — the same shape applies to docs at smaller scale, where an
agent populating a manpage EXAMPLES block fabricates plausible output
rather than running the command. The Anthropic Prompt Engineering 101
talk's repeated "narrate this with the actual CLI output" framing is
the corroborating principle.

## Decision

1. **Receipt schema extension.** ARB receipts gain optional fields:
   - `captured_stdout_path: str | None` — relative path under
     `.gzkit/proofs/<receipt-id>/stdout.txt`
   - `captured_stdout_hash: str | None` — SHA-256 of the captured
     stdout
   - `captured_stderr_path: str | None`, `captured_stderr_hash: str | None`
     — same shape for stderr
2. **`gz arb step --capture` flag.** Opt-in capture; when set, the wrapped
   command's stdout and stderr are written to the proofs directory and
   the receipt is decorated with the path + hash fields. Capture is
   opt-in to avoid bloating the proofs tree with large outputs that
   aren't load-bearing for any doc surface.
3. **`gz validate --manpage-examples` scope.** New validator that:
   - Parses every manpage under `docs/user/manpages/**` for EXAMPLES
     blocks containing fenced code blocks tagged as command output.
   - For each EXAMPLES block, looks for an adjacent receipt-citation
     comment (e.g., `<!-- bound to receipt arb-step-… -->`).
   - Asserts the EXAMPLES block content hashes equal to the receipt's
     `captured_stdout_hash`.
   - Fails-closed (exit 3) on hash mismatch (manpage drifted from
     captured truth) or on unbound EXAMPLES block in heavy-lane manpage
     scope.
4. **Lite/heavy gating.** Heavy-lane manpages (CLI verbs registered in
   `parser_artifacts.py`) require receipt-bound EXAMPLES; lite-lane
   doc surfaces (governance prose, runbook narrative) are advisory and
   warn-only.
5. **Storage discipline.** `.gzkit/proofs/<receipt-id>/stdout.txt` is
   project-local and never canonical; mirrors the chores doctrine
   (ADR-0.0.21) where execution evidence is project-local-only. Proofs
   directory is gitignored *except* when explicitly committed as part
   of a manpage's binding (the receipt-citation comment is the bind).

## Comparator Uplift (2026-05-07)

Specmatic-style executable contracts belong beyond APIs. This ADR should make
CLI examples, runbook snippets, and workflow-stage output claims executable
contracts by binding them to captured stdout/stderr hashes. Borrowed workflows
that promise output must prove the bytes, not just describe the shape.

## Consequences

### Positive

- AGENTS.md item 2 ("real CLI output, not placeholders") gains a
  mechanical floor. Today the rule is discipline; tomorrow it's a
  validator.
- Pairs with ADR-0.0.24 — both close citation-surface fabrication at
  the same layer (claim about output bytes), one for attestation
  text, one for doc-surface examples.
- Foundation for ADR-pool.multimodal-evidence-binding (pool ADR being
  authored alongside this one) — the captured-stdout work is the
  text-tier; multimodal extends to image/video/screenshot bytes via
  the same hash-binding shape.
- Provides a primary signal source for ADR-0.0.26's
  evaluation-feedback-loop chore — manpage-example drift is a clear
  weak-dimension signal the loop can cluster on.

### Negative

- Adds complexity to ARB receipt emission (capture path management,
  hash computation). Mitigated by making capture opt-in.
- Storage cost: proofs tree grows for each captured receipt. Mitigated
  by opt-in capture and a periodic prune chore (out of scope for this
  ADR; tracked as a follow-up under `gz-tidy`).
- Backwards-compatibility: existing manpages with EXAMPLES blocks have
  no captured-stdout binding. They become advisory-warn until manually
  rebound. The ADR provides a rebind tool (`gz arb rebind-manpage
  <path>`) that runs the cited command and creates the binding —
  agents can sweep through existing manpages to bring them under the
  gate.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.46.0-01: Extend ARB receipt schema with optional `captured_stdout_path` / `captured_stdout_hash` / `captured_stderr_*` fields; implement `gz arb step --capture` opt-in flag with `.gzkit/proofs/<receipt-id>/` storage
- [ ] OBPI-0.46.0-02: Implement `gz validate --manpage-examples` scope; parse EXAMPLES blocks, locate receipt-citation comments, hash-match against captured stdout; heavy-lane fail-closed, lite-lane warn-only; `gz arb rebind-manpage <path>` rebind tool
- [ ] OBPI-0.46.0-03: BDD scenarios + manpage and doc updates; one-time corpus sweep to bind existing heavy-lane manpages, with a corpus-frozen waiver list for any binding deferred to follow-up GHIs

## Q&A Transcript

Authored 2026-04-25 from Anthropic Prompt Engineering 101 review session.
Talk's repeated framing — "this is the actual output, not placeholder" —
is the principle AGENTS.md item 2 already encodes. This ADR adds the
mechanical floor.

## Evidence

- [ ] Schema: `src/gzkit/arb/validator.py` — receipt model extension
- [ ] Capture: `src/gzkit/arb/middleware.py` — `--capture` flag and proofs storage
- [ ] Validator: `src/gzkit/governance/trust_audits.py` — `validate_manpage_examples`
- [ ] Rebind tool: `src/gzkit/commands/arb_rebind.py`
- [ ] Tests: `tests/arb/test_capture.py`, `tests/governance/test_manpage_examples.py`
- [ ] BDD: `features/manpage_example_binding.feature`
- [ ] Corpus-freeze: `data/manpage_example_waivers.json`
- [ ] Storage: `.gzkit/proofs/<receipt-id>/` (project-local, gitignored except where bound)

## Alternatives Considered

1. **Capture stdout for every ARB receipt by default** — rejected.
   Storage cost grows unbounded; many receipts have no doc-surface
   binding and capture is wasted bytes. Opt-in capture makes the cost
   proportional to value.
2. **Bind manpage examples to receipts by inline-pasting the receipt
   ID, no hash check** — rejected. Without a hash check, the binding
   is narrative — exactly the failure mode AGENTS.md item 2 names.
   Hash-equality is the cheap mechanical floor.
3. **Defer until a third doc surface needs binding (runbook, BDD
   feature files)** — rejected. The manpage surface alone is sufficient
   primary value; runbook/feature file bindings can extend the
   validator's scope under follow-up ADRs without re-architecting.
4. **Author as a docs-only "always paste real output" rule** —
   rejected. The rule already exists (AGENTS.md item 2); the gap is
   mechanical enforcement.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.46.0 | Pending | | | |
