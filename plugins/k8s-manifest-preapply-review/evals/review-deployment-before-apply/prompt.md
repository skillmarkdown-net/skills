---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this before I kubectl apply it to prod:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: prod
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
      - name: web
        image: myorg/web:latest
        ports:
        - containerPort: 80
        securityContext:
          privileged: true
```
