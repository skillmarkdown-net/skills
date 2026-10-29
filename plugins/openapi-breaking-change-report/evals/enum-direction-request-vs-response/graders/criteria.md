---
type: llm
---

PASS if Explains direction: as a request filter, adding a value is safe; in the response it is risky since strict clients and generated enums may fail. Shared schema means the worse class wins (risky), recommends at least MINOR and mentions strict or generated clients.
FAIL if Says it is simply safe or simply breaking without distinguishing request and response direction.
