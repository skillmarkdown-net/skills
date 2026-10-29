---
type: llm
---

PASS if Flags SSH 22 open to 0.0.0.0/0 as CRITICAL, prints a risk table and counts (1 create, 1 update), gives NO-GO verdict, and does not run apply.
FAIL if Gives GO, misses the open SSH rule, or omits the table/verdict.
