---
type: llm
---

PASS if Flags the removed extensions/v1beta1 API (removed in 1.22), shows a networking.k8s.io/v1 rewrite with pathType, ingressClassName and service.name/port.number, flags the snippet annotation and missing TLS, and mentions ingress-nginx retirement/Gateway API as something to verify.
FAIL if Leaves the old apiVersion and backend format in place or does not provide a v1 rewrite.
