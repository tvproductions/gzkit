# Exchange records

The OBPI token block's register entries (ADR-0.0.41). An **exchange record**
notes one block's vacation — the token holder surrendering its claim, plus an
observation report of what happened during the traversal.

**These are not session handoffs.** Operator canon, 2026-08-06: *transit* is
entry to and exit from the ecosystem (`gz airlock`, ADR-0.33.0); *exchange* is
one block's occupancy (here); *handoff* is one session's memory refresh
(`.gzkit/handoffs/`, ADR-0.0.65). Three systems, one word they used to share.

Written mechanically by `gz obpi complete`, by
`gz obpi lock release --abandon <category>:<reason>`, and by TTL reaping. Do
not hand-author one to discharge a lock — take the completion or abandon path.

Tracked on purpose: the sibling `.gzkit/locks/` tree is gitignored runtime
state, but `gz validate --lock-exchange-coupling` fails closed on any cited
record that is not in git's index (GHI #759), so these must be committable.
