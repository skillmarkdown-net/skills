---
type: llm
---

PASS if Handles Statement as an object; flags Action '*' Allow as CRITICAL; reports app policy as UNVERIFIED (unknown at plan time); ignores the Deny; verdict NO-GO.
FAIL if Flags the Deny statement, misses the single-object Statement, or silently passes the unknown policy.
