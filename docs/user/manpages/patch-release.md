# gz patch release(1) -- GHI-driven patch release ceremony

## SYNOPSIS

```
gz patch release [--dry-run] [--json] [--full]
```

## DESCRIPTION

Execute the GHI-driven patch release ceremony. Discovers two release
qualifiers since the last tag — behavior-level GHIs (cross-validated by
runtime label AND source diff) and foundation-ADR closeouts (Gate-5
`validated` receipts in the ledger) — bumps the patch version, and writes
a dual-format release manifest. With `--full`, also drafts release notes,
commits, pushes behind lint/test gates, and creates the GitHub release.

Both qualifiers carry equal weight: per the hexagonal port/adapter
doctrine, foundation ADRs (ports) ship code surfaces just as feature ADRs
(adapters) do, so a foundation closeout is a release-worthy event in its
own right.

## QUALIFICATION BUCKETS

Every discovered GHI lands in exactly one bucket. The first four are
computed from the `runtime` label and the `src/gzkit/` diff; the last two
report a state rather than a verdict.

| Bucket | Meaning |
|---|---|
| `qualified` | `runtime` label AND src diff in range, closed upstream — release content |
| `label_only` | `runtime` label, no src diff in range |
| `diff_only` | src diff in range, no `runtime` label — adjudicate per skill § Step 1a |
| `open_upstream` | Would qualify, but still OPEN on GitHub — adjudicate per skill § Step 1b |
| `unclassified_reference` | Cited in range by a commit whose Conventional-Commits type is not a closure type, and claimed by no closure commit — adjudicate per skill § Step 1c |
| `excluded` | Neither label nor src diff — not release content |

`unclassified_reference` is **disclosure, not qualification** (GHI #794).
Closure detection keys on the commit type, so a GHI whose only remedy
landed as `chore(deps): … (GHI #N)` — a dependency upgrade is its own
remedy, with no separate code commit — was previously absent from every
bucket rather than mis-bucketed, and nothing warned. The bucket does not
decide whether such a commit shipped release content; it makes the
question visible. Body-prose citations are not admitted, and a GHI a
closure commit already claims is not reported.

## OPTIONS

`--dry-run`
:   Show planned actions without executing.

`--json`
:   Emit machine-readable JSON to stdout.

`--full`
:   Execute the full ceremony in one transaction: bump, draft release notes, commit, push (with lint/test gates), and create the GitHub release.

## MX HANGAR LOCKOUT

No normal release ships while an MX maintenance hangar is open (ADR-0.0.74). If
the marker (`.gzkit/mx.json`) is present, the executing path is refused before
any GitHub/network work with exit `3` and the message `Release refused: an MX
maintenance hangar is open; exit it (gz mx exit) before releasing`. Exit the
hangar (`gz mx exit`) first. `--dry-run` preview is unaffected.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success (or dry-run preview) |
| 1 | User/config error |
| 2 | System/IO error |
| 3 | Policy breach (includes a refused release while an MX hangar is open) |

## EXAMPLES

Preview what the patch release would do:

```bash
uv run gz patch release --dry-run
```

```
Patch Release Discovery (dry run)
  Latest tag: v0.26.5 (2026-05-17T17:32:41-05:00)
  Version: 0.26.5 -> 0.26.6 (proposed)
  GHIs discovered: 17
  Foundation closeouts: 1

  #483    kind-invariance: 10 legacy foundation ADRs ...   qualified
  ...

Foundation-ADR closeouts
  ADR-0.0.36-universal-obpi-attestation        validated  (2026-05-18)
```

Machine-readable output:

```bash
uv run gz patch release --json
```

## SEE ALSO

`gz closeout`(1)
