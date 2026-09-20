# Evidence — doctrine-declared-without-mechanism share measurement, 2026-09-20

Re-run:

```
gh issue list --state all --limit 2000 \
  --json number,title,state,createdAt,closedAt,labels,body > issues.json
python3 measure.py
```

`measure.py` is read-only and writes nothing. It carries the two classification sets as
literals: they are one reader's judgment under the criterion stated in
[`../f1-family-share-measurement-2026-09-20.md`](../f1-family-share-measurement-2026-09-20.md),
not a computed result. The script's job is to make the **cohort reconstruction** and the
**arithmetic** mechanical, and to refuse a pass that contradicts itself.

Three asserts fail closed:

- every classified member must actually have been open in its cohort;
- every issue open at BOTH dates must be classified identically across the two passes;
- the stock must reconcile — survivors plus newly filed equals today's members.

The second assert caught a real error while this measurement was being taken: GHI #837 was
open at both dates with an unchanged body and had been classified differently in the two
passes. Re-deciding it once moved the 2026-09-02 figure from 27 to 28.

The classification input — each open issue's self-declared `Class of failure` section — is
read straight from the issue bodies in `issues.json`. Self-declaration is an input a reader
weighs, never the verdict; the measurement record explains where the two diverge.
