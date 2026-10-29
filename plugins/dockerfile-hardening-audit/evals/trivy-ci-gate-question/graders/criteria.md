---
type: llm
---

PASS if Gives trivy image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed myapp:1.4.2 and docker scout cves --only-fixed --only-severity critical,high --exit-code (exit code 2), notes Trivy exits 0 by default and that ignore-unfixed/only-fixed change reporting not contents, mentions pinning scanner version.
FAIL if Omits --exit-code, claims Trivy fails by default, or invents flags.
