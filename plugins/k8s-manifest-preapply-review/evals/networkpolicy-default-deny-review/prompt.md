---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We want default deny egress in the shop namespace. Is this NetworkPolicy OK?

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: deny-all, namespace: shop}
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```
