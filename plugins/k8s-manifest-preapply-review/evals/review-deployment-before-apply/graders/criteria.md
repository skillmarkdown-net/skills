---
type: llm
---

PASS if Gives a verdict of Block, flags privileged as Critical, :latest as High, missing resources/probes, runAsNonRoot, seccomp, capabilities drop ALL, single replica, with YAML fixes naming the object and path; notes port 80 needs NET_BIND_SERVICE or a move to 8080; lists what could not be determined.
FAIL if Generic advice with no severity ranking, no YAML patch, misses privileged or :latest, or declares it fine to apply.
