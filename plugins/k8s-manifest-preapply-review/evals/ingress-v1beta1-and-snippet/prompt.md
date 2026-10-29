---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Pre-apply review of this Ingress for k8s 1.34 please:

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: site
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame: deny";
spec:
  rules:
  - host: site.example.com
    http:
      paths:
      - path: /
        backend:
          serviceName: site
          servicePort: 80
```
