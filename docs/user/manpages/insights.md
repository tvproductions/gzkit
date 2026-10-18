# gz insights

Governed authoring and reading over the append-only insights store.

---

## Overview

`.gzkit/insights/agent-insights.jsonl` holds four record kinds: `defect`,
`defect-resolution`, `improvement` and `discovery`. Each record also gets one
`insight_recorded` pointer in the ledger. The verbs:

| Verb | Purpose |
|------|---------|
| [`gz insights remember`](insights-remember.md) | Append one schema-valid record and its ledger pointer |
| [`gz insights recurrence`](insights-recurrence.md) | Check whether cited records qualify a failure to become a rule (maxim 13) |

---

## Usage

```
gz insights {remember,recurrence} ...
```
