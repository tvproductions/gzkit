# Plan: OBPI-0.0.24-03-doc-updates

OBPI: `OBPI-0.0.24-03-doc-updates`
Parent ADR: `ADR-0.0.24-attestation-receipt-binding` (foundation, heavy)

## Context

OBPI-01 landed `gz validate --attestation-receipts` (parser, ledger lookup,
category match) and OBPI-02 wired the gate into `gz obpi complete` and
`gz adr emit-receipt` with the `arb-meta-receipt-bind-…` self-attesting
receipt family and lane/kind-conditional fail/warn behavior. Both are
`attested_completed` per `gz adr status ADR-0.0.24`.

This OBPI is the docs-side patch that aligns AGENTS.md, the ARB middleware
deep-dive, and the `gz validate` command page with the now-mechanical
contract — replacing the surviving narrative-trust language ("the citing
agent must verify the receipt exists and status matches the claim") with
references to the mechanical gate, and documenting the new `--attestation-
receipts` surface with real CLI output.

Inherits foundation-kind brief-level attestation (Heavy + Foundation =
TTY + `ATTEST` per § Lane & Kind & Sensitivity Attestation Matrix).

## Files

| Path | Change |
|------|--------|
| `AGENTS.md` | § Attestation prose: replace "Citing agent must verify…" sentence with mechanical-gate language naming `gz validate --attestation-receipts` and the `arb-meta-receipt-bind-…` family. Update § Lane behavior bullets so the heavy-lane line cites the gate as the enforcement surface. |
| `docs/governance/arb-middleware.md` | Add a new `## Receipt-binding gate` subsection documenting the gate's invocation point (called by `gz obpi complete` and `gz adr emit-receipt` pre-emission), the `arb-meta-receipt-bind-…` self-attesting receipt family, lane/kind behavior matrix, and the failure modes (missing receipt / status_mismatch / claim_mismatch). |
| `docs/user/commands/validate.md` | Expand the existing `--attestation-receipts` section: keep the current synopsis + `--lane`/`--kind` axes; add an `#### Examples` block with two real `gz validate --attestation-receipts` invocations (one heavy-PASS with a real receipt ID, one heavy-FAIL on missing receipts) showing actual CLI output captured from this session. |
| `docs/user/runbook.md` | Step 4b (Heavy-lane ARB receipts): add a one-line note that the receipt citations are mechanically verified by `gz validate --attestation-receipts` inside `gz obpi complete`/`gz adr emit-receipt` (heavy/foundation = fail-closed). |

> The brief allowlist names `docs/user/manpages/gz-validate.md` "or wherever
> manpages live"; the canonical home for `gz validate` documentation in this
> repo is `docs/user/commands/validate.md` (verified by Glob — no
> `manpages/gz-validate.md` exists). Edit that file.

> `docs/governance/governance_runbook.md` is in the brief allowlist but a
> grep shows no surviving attestation-flow language that drifts from the
> mechanical contract. No edit required there.

## Steps

1. **AGENTS.md § Attestation — receipt-IDs sentence (REQ-01, REQ-02).**
   Edit the line currently reading "Receipt IDs inline … Citing agent must
   verify receipt exists and status matches the claim — fabricating a receipt
   ID is the same failure as fabricating the claim." Replace the
   "Citing agent must verify…" half with mechanical-gate language naming
   `gz validate --attestation-receipts` (the verification is now mechanical;
   fabrication is still the failure mode but the gate enforces it). Mention
   the `arb-meta-receipt-bind-…` self-attesting receipt family written when
   the gate fires.

2. **AGENTS.md § Lane behavior (REQ-02).** Update the two bullets:
   - Heavy lane: explicitly cite `gz validate --attestation-receipts` as the
     gate that fires on receipt citation; "fail-closed" is now mechanical.
   - Lite lane: remains warn; cite the same gate as the surface that emits
     the warning.

3. **docs/governance/arb-middleware.md — `## Receipt-binding gate` subsection
   (REQ-03).** Insert a new subsection (placement: after `## Receipt schema
   and storage`, before subsequent middleware sections — preserves the
   schema → storage → enforcement → consumption flow). Content:
   - Invocation point: pre-emission inside `gz obpi complete --attestation-
     text …` and `gz adr emit-receipt … --attestor …` (cite OBPI-02 wiring).
   - The `arb-meta-receipt-bind-…` family: self-attesting evidence that the
     gate fired on the attestation it ratified; ledger entry shape; where it
     lives.
   - Failure modes table (or bulleted list): `missing` (receipt file not
     found), `status_mismatch` (receipt `exit_status != 0`), `claim_mismatch`
     (cited category does not match the receipt's canonical category from
     `CANONICAL_STEP_COMMANDS`).
   - Lane/kind behavior matrix matching ADR-0.0.24 Decision §3 (heavy →
     fail-closed exit 3; foundation regardless of lane → same; lite-non-
     foundation → warn).
   - Cross-link to `AGENTS.md` § Attestation Lane behavior and to `ADR-0.0.24`.

4. **docs/user/commands/validate.md — `--attestation-receipts` EXAMPLES
   (REQ-04, REQ-08).** Expand the existing `### --attestation-receipts`
   section: keep current synopsis prose; add `#### Examples` with two
   captured-from-session invocations, each with the real CLI output:
   - Heavy-lane PASS: pass an attestation string that cites a real
     `arb-ruff-…` receipt from `artifacts/receipts/`. Capture the exact
     stdout (`✓ 1 attestation receipt(s) resolved.` from the session probe).
   - Heavy-lane FAIL on missing receipts: pass a narrative-only string with
     no `arb-…` IDs. Capture the exact stdout (`❌ No ARB receipt IDs cited
     (heavy or foundation: fail-closed).` from the session probe).
   - Use `gh-cli`-style fenced blocks with the real command and real output —
     no placeholder `<...>` (REQ-08).
   - The receipt ID `arb-ruff-008dda0e47384e89bea69e3b8b5cb6d4` is confirmed
     present in `artifacts/receipts/` via session probe and is suitable for
     the PASS example.

5. **docs/user/runbook.md — step 4b note.** Locate step 4b in the heavy-lane
   ARB receipts block (~line 163). Append a one-line note: "Citation is
   mechanically verified by `gz validate --attestation-receipts` inside
   `gz obpi complete` / `gz adr emit-receipt` on heavy or foundation work
   (fail-closed); see ADR-0.0.24."

6. **Verify (REQ-05, REQ-06).** Run the brief verification block in order
   and capture output for the Stage 4 evidence table:
   - `uv run gz lint`
   - `uv run gz cli audit`
   - `uv run mkdocs build --strict`
   - `uv run gz validate --documents`
   - `grep -n "attestation-receipts" AGENTS.md docs/governance/arb-middleware.md docs/user/commands/validate.md`
   ARB-wrapped form per `AGENTS.md` § Attestation Canonical invocations:
   - `uv run gz arb ruff` (lint receipt)
   - `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
     (heavy-lane docs receipt)

7. **PII guard (REQ-07).** Before committing, grep all five edited files
   for the personal-email substring (per `AGENTS.md` § Local Agent Rules —
   Operator PII). If any hit lands, abort and fix.

## Verification

```bash
uv run gz lint
uv run gz cli audit
uv run mkdocs build --strict
uv run gz validate --documents
grep -n "attestation-receipts" AGENTS.md docs/governance/arb-middleware.md docs/user/commands/validate.md
```

ARB-wrapped (heavy-lane evidence):

```bash
uv run gz arb ruff
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Notes

- **Lane:** Heavy (per brief). Foundation-kind brief-level attestation fires
  at OBPI completion; TTY + `ATTEST` required.
- **No code, no tests:** Gate 2 is satisfied via `gz validate --documents`
  clean run (per brief Gate 2).
- **BDD coverage** lives in OBPI-0.0.24-04, not this OBPI.
- **Manpage location decision:** brief allowlist names `docs/user/manpages/gz-
  validate.md "or wherever manpages live"`; canonical home is
  `docs/user/commands/validate.md` per repo layout. Single edit there.
- **Destination-in-mind disclosure (Step 6a):** I had already concluded the
  three primary edits (AGENTS.md prose + Lane bullets, arb-middleware new
  subsection, validate.md EXAMPLES expansion) before drafting this plan,
  driven by direct reads of the brief Requirements list. Disclosure: the
  conclusion was reached from the brief itself, not from independent
  exploration of alternative shapes. **Rejected alternatives:** (a) creating
  a new `docs/user/manpages/gz-validate.md` to honor the brief's literal
  filename — rejected because the canonical home is `docs/user/commands/
  validate.md` and creating a parallel manpage file would itself be drift;
  (b) folding the receipt-binding-gate content into AGENTS.md inline rather
  than `arb-middleware.md` — rejected because AGENTS.md § Attestation
  explicitly delegates middleware deep-dive to `arb-middleware.md`, and
  inlining would inflate AGENTS.md against the instructions-files-budget
  audit (GHI #373).
