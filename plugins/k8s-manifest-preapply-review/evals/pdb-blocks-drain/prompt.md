---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Please check these manifests before we apply them: a Deployment `api` with replicas: 1 and this PDB.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: {name: api, namespace: prod}
spec:
  minAvailable: 1
  selector:
    matchLabels: {app: api}
```
