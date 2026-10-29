---
type: llm
---

PASS if Computes effective security: GET /reports now inherits bearer auth, which is breaking; GET /health stays open so it is not a change for clients. Gives a MAJOR suggestion and migration note to send a bearer token.
FAIL if Only looks at operation-level keys and reports no change for /reports.
