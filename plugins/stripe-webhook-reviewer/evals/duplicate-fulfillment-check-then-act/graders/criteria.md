---
type: llm
---

PASS if Identifies check-then-act race with concurrent retries, proposes atomic INSERT ON CONFLICT DO NOTHING claim with status and lease, mentions marking done after success, dedupe on session id because separate events or the success page can also fulfill, and checks payment_status paid.
FAIL if Says the code is fine, or only suggests a longer-lived cache without an atomic claim.
