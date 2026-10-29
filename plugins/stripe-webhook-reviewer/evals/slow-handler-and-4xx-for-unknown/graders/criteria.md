---
type: llm
---

PASS if Recommends verify, claim event id, enqueue, return 2xx fast and process in a worker; unknown types should return 2xx; 400 only for bad signature or malformed payload; 5xx only for transient errors; mentions retries up to 3 days in live mode and that invoice.created stalls can block billing; does not quote an invented timeout number.
FAIL if Gives a made-up exact timeout, or tells them to keep processing synchronously.
