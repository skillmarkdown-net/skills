---
type: llm
---

PASS if Flags wildcard rules and cluster-wide grant to the default ServiceAccount as Critical/High, proposes a namespaced Role and RoleBinding with specific verbs/resources and a dedicated ServiceAccount, and mentions kubectl auth can-i verification.
FAIL if Only says to be careful with wildcards, gives no replacement YAML, or ignores the default ServiceAccount binding.
