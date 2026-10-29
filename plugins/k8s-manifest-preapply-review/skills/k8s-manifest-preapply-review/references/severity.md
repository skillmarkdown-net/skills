# Severity rubric

A synthesis of common practice, not an official standard. Cross-check with the Kubernetes security checklist, NSA/CISA hardening guide and CIS Kubernetes Benchmark when asked.

| Severity | Examples |
|---|---|
| Critical | `privileged: true`; hostPath to `/` or runtime socket; hostNetwork/hostPID/hostIPC; cluster-admin bound to a workload; wildcard RBAC; plaintext secrets committed |
| High | `allowPrivilegeEscalation` not false; runs as root; capabilities not dropped; `:latest` or untagged image; no memory limit; no NetworkPolicy on sensitive namespace; secret-reading RBAC; public LoadBalancer without source ranges |
| Medium | no seccomp RuntimeDefault; writable root filesystem; missing readiness/startup probe; no PDB with 2+ replicas; single replica in production; default ServiceAccount or token auto-mounted needlessly; missing CPU/memory requests |
| Low / Info | tag without digest; no topology spread; missing CPU limit; missing labels; legacy ingress controller |

## Verdict rule
- Any Critical: `Block`.
- Any High: `Fix before apply`.
- Only Medium and below: `OK to apply` with recommendations.

## Adjustments
- Dev/test namespaces: lower availability findings (replicas, PDB) by one level, never security Criticals.
- Init containers and Jobs: probes not required.
- Say "PSS violation (baseline)" or "PSS violation (restricted)" only for rules actually in the standards; otherwise "best practice".
- Items not provable from the manifests go under "cannot determine", not as findings.
