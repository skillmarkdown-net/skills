---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I ran helm template on our chart and the StatefulSet for redis looks like this. Check the securityContext and PSS compliance against restricted:

```yaml
kind: StatefulSet
apiVersion: apps/v1
metadata: {name: redis, namespace: data}
spec:
  serviceName: redis
  replicas: 3
  selector: {matchLabels: {app: redis}}
  template:
    metadata: {labels: {app: redis}}
    spec:
      initContainers:
      - name: init-perms
        image: busybox:1.36
        command: ["sh","-c","chown -R 999 /data"]
        securityContext: {runAsUser: 0}
      containers:
      - name: redis
        image: redis:7.2
        securityContext:
          runAsNonRoot: true
          runAsUser: 999
```
