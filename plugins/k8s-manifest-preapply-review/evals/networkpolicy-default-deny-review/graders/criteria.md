---
type: llm
---

PASS if Confirms it is a valid default deny but warns DNS will break, and supplies an allow-dns policy to kube-dns in kube-system on UDP and TCP 53; notes CNI must enforce NetworkPolicy (cannot determine from YAML).
FAIL if Says it is fine with no DNS warning, or forgets that enforcement depends on the CNI.
