---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Can you audit this RBAC for least privilege?

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: {name: app-role}
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata: {name: app-binding}
subjects:
- kind: ServiceAccount
  name: default
  namespace: payments
roleRef:
  kind: ClusterRole
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```
