---
type: llm
---

PASS if Flags express.json before the route and re-serialized body, recommends express.raw on the route, flags the hardcoded whsec_ secret, flags 200 on verification failure (should be 400), and notes missing payment_status check and dedupe; gives code fixes.
FAIL if Only says to check the secret, misses the raw body issue or the 200 on failure, or gives no code fixes.
