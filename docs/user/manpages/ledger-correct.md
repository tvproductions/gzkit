# gz ledger correct

Append a corrective action against one prior ledger row. The original row is
never edited or removed.

Operator intent this discharges, verbatim: *"we need the power to UNDO agent
(or human) error"*, *"not to erase the ledger, but to provide subsequent
corrective actions."*

---

## Usage

```bash
gz ledger correct --subject-event EVENT --subject-id ID --subject-ts TS \
  --disposition {void,discharged,reinstated} \
  --cause {agent-error,operator-error,runtime-error,condition-resolved} \
  --reason TEXT --attestor NAME [--dry-run]
```

---

## Why this exists

`AGENTS.md` § Behavior Rules — Never #2 forbids modifying the ledger, and that
prohibition is what makes the ledger trustworthy. Before this verb, the only
governed reversals were per-error-class point solutions —
`gz obpi repudiate` (a Gate-5), `gz obpi withdraw` (an OBPI), the
`obpi_parked`/`obpi_unparked` and `obpi_blocked_on_operator`/`obpi_unblocked`
pairs. Anything without its own verb could not be corrected at all: a
wrongly-started pipeline, a TASK blocker whose reason the operator had already
resolved, a factually-false evidentiary row.

ADR-0.0.71 named repudiation a **port** — *"an erroneously- or
fraudulently-attested completion can be governed-reversed ... leaving an honest
audit trail"* — with its event as the *first adapter*. This verb is that port,
generalized to every event type.

---

## Naming the subject

A correction names one prior row by the triple `(event, id, ts)`. There is no
per-row identifier in the ledger: `id` carries the *artifact*, so an artifact's
tenth event and its first share it, and the timestamp is what separates them.

Read the exact values off the row itself:

```bash
grep -F OBPI-0.35.0-08 .gzkit/ledger.jsonl
```

A reference that resolves to no row is refused (exit 1) and nothing is written.
A dangling correction would sit in the ledger asserting a repair no reader can
apply.

---

## Dispositions

| Disposition | Claim | Effect on readers |
|---|---|---|
| `void` | The row records something that was not true, or that should never have been recorded. | Dropped from **both** derived readings — state derivation *and* evidence selection. |
| `discharged` | The row was true when written; its condition has since been resolved. | Dropped from the **liveness** reading only. It remains evidence, because discharging never claims the finding was false. |
| `reinstated` | A prior correction on this row was itself mistaken. | Clears the correction; the row is live again. |

The `void`/`discharged` split is load-bearing. An erroneous record and a
correctly-recorded-then-superseded one have different premises, and collapsing
them would force one to be filed as the other.

`reinstated` is the in-family reversal, and it is the **only** way to undo a
correction: a correction may not name another `ledger_event_corrected` row as
its subject (refused, exit 1), because that would make the netting resolve
itself recursively and leave *what is live* dependent on evaluation order.

Corrections compose by **last-correction-wins**, the same netting rule
`obpi_parked`/`obpi_unparked` already use. `void → reinstated → void` resolves
to `void`; repeating a correction is inert and recorded for provenance only.

---

## Causes

`--cause` is a closed vocabulary, mirroring ADR-0.0.71 Boundary Invariant 4's
ruling that a cause is *"extensible only by amendment ADR, never free-form"* —
a free-text cause can be read but never censused.

| Cause | Use |
|---|---|
| `agent-error` | An agent recorded something it should not have. |
| `operator-error` | A human recorded the wrong thing. |
| `runtime-error` | gzkit itself wrote the row wrong; no actor erred. |
| `condition-resolved` | Nothing was wrong; the condition the row records has ended. Pairs with `discharged`. |

---

## PASS/FAIL Contract

Exits 0 having appended one `ledger_event_corrected` row.

Exits 1, writing nothing, when:

- `--attestor` is empty or whitespace — undoing a recorded fact is human-gated
  on the same terms as `gz obpi repudiate` (ADR-0.0.71 Boundary Invariant 1)
- `--reason` is empty or whitespace
- the `(event, id, ts)` triple matches no row
- `--subject-event` is `ledger_event_corrected`
- `--disposition reinstated` is given for a row carrying no correction

---

## Example

Review before applying — `--dry-run` prints the resolved subject row, its
current disposition, and the resulting one, and writes nothing:

```bash
uv run gz ledger correct \
  --subject-event pipeline_launched \
  --subject-id OBPI-0.35.0-08-remember-post-append-advisory \
  --subject-ts 2026-08-23T13:12:21.832251+00:00 \
  --disposition void --cause agent-error \
  --reason "pipeline launched without operator initiation (IRON LAW)" \
  --attestor g0 --dry-run
```

```
Subject rows resolved: 1
  pipeline_launched  id=OBPI-0.35.0-08-remember-post-append-advisory  ts=2026-08-23T13:12:21.832251+00:00
Current disposition: none (live)
Resulting disposition: void
Dry run: no ledger event will be written.
```

Discharging a TASK blocker the operator has already ruled on:

```bash
uv run gz ledger correct \
  --subject-event task_blocked \
  --subject-id TASK-0.35.0-08-05-01 \
  --subject-ts 2026-08-23T14:27:39.933308+00:00 \
  --disposition discharged --cause condition-resolved \
  --reason "operator ruled 2026-08-24; REQ reworded the same day" \
  --attestor g0
```

---

## Options

| Option | Description |
|--------|-------------|
| `--subject-event` | Event type of the row being corrected (required) |
| `--subject-id` | The row's `id` field (required) |
| `--subject-ts` | The row's `ts` field (required) |
| `--disposition` | `void`, `discharged`, or `reinstated` (required) |
| `--cause` | `agent-error`, `operator-error`, `runtime-error`, or `condition-resolved` (required) |
| `--reason` | Why the correction is warranted; fails closed when empty (required) |
| `--attestor` | Human recording the correction; fails closed when empty (required) |
| `--dry-run` | Print the resolved subject and planned event; write nothing |

---

## Related

- [`gz ledger corrections`](ledger-corrections.md) — census of corrections in force
- [`gz obpi repudiate`](obpi-repudiate.md) — the Gate-5-specific reversal this generalizes
