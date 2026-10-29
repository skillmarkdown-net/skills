---
type: llm
---

PASS if Catches ::/0 on port 5432 as CRITICAL, does not flag the egress rule, verdict NO-GO.
FAIL if Only checks IPv4 and says GO, or flags the egress rule.
