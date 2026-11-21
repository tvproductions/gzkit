# gz wp discrepancy clear

Clear a line on the list of discrepancies on its evidence, the coordinator's call.

## Usage

```bash
gz wp discrepancy clear <DSC-id> [--entry <ENT-id>] [--tag <TAG-id>] [--ghi <n>] \
  [--root-cause <text>] [--corrective-action <text>] [--recurs <cite>]... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `DSC-id` | The line's id, `DSC-<NN>-<slug>`. Required |
| `--entry` | An entry of the line's package |
| `--tag` | A cleared tag of the line's package |
| `--ghi` | The open issue the line was filed as |
| `--root-cause` | The line's root cause |
| `--corrective-action` | The line's corrective action |
| `--recurs` | An insight record's `ts` or a `#GHI` of the same failure; repeatable |
| `--json` | Output the booked `discrepancy_cleared` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A line of the list of discrepancies is cleared by one `discrepancy_cleared` event
with its evidence (RP-12 ruling 9). `docs/governance/harbor-ro12-contractor-kit.md`
§ Rulings holds the rulings cited here.

- The coordinator's unstamped call alone clears a line; a subagent's call is
  refused (rulings 114 and 172). The open MX session is recorded with the clear.
- The clear cites evidence the ledger resolves, at least one of: an entry of the
  line's package (`--entry`), a tag of the line's package its `Restoration`
  dispatch has cleared (`--tag`), or the issue the line was filed as (`--ghi`)
  (ruling 172). Work in another package does not clear the line; a line that
  leaves its package is filed as an issue through `ghi-author` (ruling 9).
- An issue is confirmed open through `gh` at the clear, and the clearing event
  cites it, so the line leaves the list as an open problem report and return to
  service reads the ledger alone (ruling 180). Every check the ledger answers runs
  first; `gh` is asked last. An issue the GitHub API says does not exist (404,
  410, or a pull request's number) is refused, exit 3; when the API gives no
  answer, about `--ghi` or a GHI cited by `--recurs`, the clear exits 2. Either
  way nothing is written (ruling 182).
- A line that blocks return to service carries `--root-cause` and
  `--corrective-action`. A `due-by-event` line may cite `--recurs`, read by the
  same check as `gz insights recurrence` against
  `data/recurrence_threshold.json`: met, both fields are required; short, the
  citation is refused naming the shortfall. A record is read by its label, as that
  check reads it, so `1412` and `#1412` are one record, counted and stored once
  as `#1412`. Otherwise the fields are optional, and
  a field given is never blank (rulings 9 and 181). `--recurs` on a blocking line
  is refused.
- A line an order's acceptance carried a tag on (the accepted move's `carried`,
  rulings 171 and 184) stays on the list while the surface is isolated: it is
  cleared only by that tag's clear, citing it with `--tag` once its
  `Restoration` dispatch has cleared it. An entry, another tag or `--ghi` is
  refused (ruling 185).
- A line is cleared once.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-20 in the scratch project of
[`gz wp discrepancy record`](wp-discrepancy-record.md), with
`DSC-01-hook-left-off` recorded blocking and `DSC-02-stale-cache` due by an event,
and `ENT-01-stamp-import` booked on the order by its `Restoration` dispatch.

From the dispatch's stamped call, exit 3:

```console
$ uv run gz wp discrepancy clear DSC-01-hook-left-off --entry ENT-01-stamp-import
A discrepancy is cleared by the coordinator's unstamped call alone, and this
call is a subagent's (RP-12 rulings 114 and 172). Report the evidence in the
handback; the coordinator clears the line from the main session.
```

A blocking line with no root cause, exit 3:

```console
$ uv run gz wp discrepancy clear DSC-01-hook-left-off --entry ENT-01-stamp-import
--root-cause and --corrective-action are required: the line blocks return to
service, and such a line carries the fuller record (RP-12 rulings 9 and 181;
JFMM I-9.3.1.a). Clear it again with both written out.
```

With both written out, exit 0:

```console
$ uv run gz wp discrepancy clear DSC-01-hook-left-off --entry ENT-01-stamp-import \
    --root-cause 'The hook was disabled for the repair.' \
    --corrective-action 'The order restores it before close.'
Cleared DSC-01-hook-left-off on ORD-01-import.
```

A citation that names nothing, exit 3:

```console
$ uv run gz wp discrepancy clear DSC-02-stale-cache --entry ENT-01-stamp-import --recurs '#999999999'
--recurs #999999999 names no insight record or resolvable GHI, so the recurrence
check cannot read it (RP-12 ruling 181; `gz insights recurrence`).
```

With no `gh` on the path, exit 2:

```console
$ uv run gz wp discrepancy clear DSC-02-stale-cache --ghi 1412
Issue #1412 could not be read through `gh`, so the clear cannot confirm the line
was filed as it (RP-12 ruling 180). Check `gh auth status` and the network, then
clear it again; nothing was written.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Cleared |
| 1 | The project is not initialized, or `--recurs` was given and `data/recurrence_threshold.json` is missing or malformed |
| 2 | Usage or System/IO error, or the GitHub API gave no answer about the issue `--ghi` cites or a GHI `--recurs` cites; nothing booked |
| 3 | Refused: a subagent's call, no MX session open or a marker present but not on (its repair named), a line not recorded or already cleared, no evidence, an entry or tag not of the line's package or a tag not cleared, a carrying line cleared by anything but its carried tag's clear, an issue number below 1, an issue the API says does not exist or an issue closed, a blank field, root cause and corrective action missing where the line blocks return to service or recurs, `--recurs` on a blocking line, short of the threshold or naming nothing, or an entry or tag row the clear reads that does not parse (its void named); nothing booked |

## See also

[`gz wp discrepancy record`](wp-discrepancy-record.md), [`gz wp entry book`](wp-entry-book.md),
[`gz wp tag clear`](wp-tag-clear.md), [`gz insights recurrence`](insights-recurrence.md)
