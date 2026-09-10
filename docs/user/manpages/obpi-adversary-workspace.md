# gz obpi adversary-workspace

Materialize a disposable writable checkout of the reviewed source so the Step-4b
independent adversary can replay proofs without touching the active checkout.

---

## Usage

```bash
gz obpi adversary-workspace <OBPI-ID>
gz obpi adversary-workspace <OBPI-ID> --destination <path>
gz obpi adversary-workspace <OBPI-ID> --json
```

## Why this exists

Step 4b judges executed proof. Judging it by reading is weaker than judging it by
running it, and the mandated `adversarial-review` transport pins
`sandbox: "read-only"` — so a reviewer dispatched that way could audit a recorded
mutation sweep but never reproduce one. A gate in that position cannot distinguish
*"I verified this works"* from *"I could not check"* (GHI #961).

The repair is not a writable active checkout. It is a **disposable** one: this
command copies the reviewed source into a throwaway tree, and the reviewer is
dispatched with `--cwd` pointed there. `workspace-write` then supplies genuine
execution while the operator's tree stays protected by the sandbox boundary
itself rather than by convention.

## Runtime Behavior

The checkout carries tracked content at `HEAD` plus any uncommitted tracked
modifications, because the reviewed source is the working tree the proof executed
against, not the last commit. Ignored paths are not copied; the reviewer runs the
copy with the active environment's interpreter under a `PYTHONPATH` that redirects
imports into it, so a substitution applied inside the checkout is the code the
tests import.

The command reports a `source_digest` over the materialized file set. Every replay
record cites that digest, which is what binds a claimed replay to the exact bytes
the reviewer was handed; a record naming a different digest is refused at import
as a replay against another tree.

An unreproducible checkout is refused rather than half-built (exit 2). A partial
tree would let a replay report against source nobody reviewed.

## Options

| Flag | Behavior |
|------|----------|
| `--destination <path>` | Materialize at an explicit path (default: a temp directory) |
| `--json` | Emit the workspace record and dispatch command as JSON |

## Example

```text
$ uv run gz obpi adversary-workspace OBPI-0.1.0-01
Adversary workspace: /tmp/gz-adversary-OBPI-0.1.0-01-ab12cd
  reviewed source:   81b548cc6d2db3328e563f3892ee42979c33cdfb +uncommitted
  files:             7456
  source digest:     3f9a...
  interpreter:       /repo/.venv/bin/python
  PYTHONPATH:        /tmp/gz-adversary-OBPI-0.1.0-01-ab12cd/src
```

It then prints the interpreter invocation the reviewer uses for selectors, and the
mandated tier-1 dispatch wrapped in `gz arb step`.

## Replay evidence

A reviewer that replays reports it in the `replay` block of its
`gzkit.acceptance.review.v1` object. Each record names the obligation, the proof it
reproduces, the workspace digest, the executed selectors, the substitution applied,
and three runs — baseline, mutated, restored — plus the source digest before and
after the edit.

Ingestion refuses a claim the record does not support: a baseline that was not
green, a substitution whose failure was an execution `error` rather than an
`assertion`, a selector that executed zero tests, a record with no substitution at
all, or a source not restored byte-identically. Absence of a `replay` block claims
nothing and is left alone — silence is honest; only a claim is checked.

## Exit Codes

- `0`: the checkout was materialized.
- `2`: the reviewed source could not be reproduced.

## See Also

- [OBPI acceptance](obpi-acceptance.md) — where a replay record is imported
- [OBPI pipeline skill](../skills/gz-obpi-pipeline.md) — Step 4b's dispatch contract
