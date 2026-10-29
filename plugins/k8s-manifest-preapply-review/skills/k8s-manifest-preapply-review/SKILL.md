---
name: k8s-manifest-preapply-review
description: Reviews Kubernetes manifests (Deployments, StatefulSets, Services, Ingress, RBAC, NetworkPolicy, Helm-rendered YAML) before kubectl apply and reports findings by severity with YAML fixes. Use when asked to review, audit or harden k8s YAML, check securityContext, probes, resource limits, image tags, PDB, NetworkPolicy, RBAC or Pod Security Standards.
---

# Kubernetes Manifest Pre-Apply Review

Review Kubernetes manifests before `kubectl apply` and return findings ranked by severity, each with a copy-pasteable YAML fix. Works by reading YAML directly; tools are optional extras.

## Steps

1. **Collect the input.** Get the manifest files, a directory, or pasted YAML. For Helm charts, render first: `helm template <release> <chart> --namespace <ns> -f values.yaml --include-crds` (no cluster access; `lookup` returns empty, so say so). Ask for or note the target Kubernetes version; do not assume one. If unknown, state "version not given" in the report.
2. **Inventory.** Run `python scripts/k8s_inventory.py <file-or-dir>` (see [scripts/k8s_inventory.py](scripts/k8s_inventory.py)) to list every object as kind/name/namespace and get a first-pass list of mechanical flags (missing securityContext fields, `:latest`, missing probes, missing limits, privileged, host namespaces). Treat its output as leads, not the verdict. If Python is unavailable, read the YAML manually.
3. **Run optional tools if installed** (check with `command -v`; never install anything without asking). Useful: `kubeconform -strict -summary -kubernetes-version <ver> -ignore-missing-schemas <path>`, `kube-linter lint <path>`, `kube-score score <file>`, `trivy config <dir>`, `pluto detect-files -d .`. If the user has cluster access and consents, `kubectl apply --dry-run=server -f <file>` runs admission (including PSA warnings); `--dry-run=client` does not. List which checks you did NOT run.
4. **Check the pod template, not just the controller.** For Deployment, StatefulSet, DaemonSet, Job, CronJob (`spec.jobTemplate.spec.template`) and bare Pods, walk `containers`, `initContainers` and `ephemeralContainers`. Hardening only the main container is the most common miss. PSA `enforce` only acts on Pods, so a Deployment can apply cleanly and then have its pods rejected.
5. **Apply the checklists** in [references/checklist.md](references/checklist.md): workload security, resources, probes, images, availability, NetworkPolicy, RBAC, Service/Ingress, Secrets, deprecated APIs. Use the severity rubric in [references/severity.md](references/severity.md).
6. **Separate standards from best practice.** Pod Security Standards (baseline/restricted) cover privileged, host namespaces, hostPath, capabilities, seccomp, runAsNonRoot, allowPrivilegeEscalation, volume types. `readOnlyRootFilesystem`, resources, probes, PDBs and image digests are NOT in PSS; label them "best practice", never "PSS violation".
7. **Mark what cannot be determined** from the manifests: namespace PSA labels (`pod-security.kubernetes.io/enforce`), whether the CNI enforces NetworkPolicy, existing LimitRange/ResourceQuota, whether a referenced Secret/ConfigMap/ServiceAccount exists elsewhere, an HPA managing replicas. Report these as "cannot determine" with the command that would answer it.
8. **Write the report** in the format below. Every finding names the object (kind/name/namespace), the YAML path, why it matters, and a patch. Merge duplicates: if five Deployments share one flaw, list one finding with all objects.
9. **Do not edit files** unless asked. Offer to apply the fixes afterwards, and suggest `kubectl diff -f <file>` (exit 1 = differences, 0 = none, >1 = error) before apply.

## Output format

Start with a one-line verdict (`Block`, `Fix before apply`, or `OK to apply`), a count per severity, then findings from Critical down to Info, then "Not checked / cannot determine".

```markdown
**Verdict: Block** - 1 Critical, 2 High, 3 Medium, 1 Low

### Critical
**C1. Privileged container** - Deployment/agent/monitoring
Path: `spec.template.spec.containers[0].securityContext.privileged: true`
Why: full host access; overrides capability drops; fails PSS baseline.
Fix:
```yaml
securityContext:
  privileged: false
  allowPrivilegeEscalation: false
  capabilities: {drop: ["ALL"]}
```

### High
**H1. Image uses :latest** - Deployment/web/prod (`containers[0].image: nginx:latest`)
Fix: pin a version, ideally with digest: `nginx:1.27.2@sha256:<64-hex>`

### Not checked / cannot determine
- NetworkPolicy enforcement depends on the CNI: `kubectl get pods -n kube-system`.
- Namespace PSA labels: `kubectl get ns prod --show-labels`.
- Tools not run: kubeconform, kube-linter (not installed).
```

Never invent digests: write `sha256:<digest>` as a placeholder and tell the user to resolve it from their registry.

## Canonical hardened fix

Use this as the base patch for security findings (matches PSS restricted):

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile: {type: RuntimeDefault}
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: {drop: ["ALL"]}
    volumeMounts:
    - {name: tmp, mountPath: /tmp}
  volumes:
  - name: tmp
    emptyDir: {sizeLimit: 64Mi}
```

## Gotchas

- `capabilities`, `privileged`, `allowPrivilegeEscalation`, `readOnlyRootFilesystem` exist only at container level; `runAsNonRoot`, `seccompProfile` may be pod level or container level. Container values override pod values.
- `runAsNonRoot: true` fails with "non-numeric user" if the image `USER` is a name; always set a numeric `runAsUser`.
- `readOnlyRootFilesystem: true` breaks apps writing to `/tmp`, `/var/run`, caches, logs. Add `emptyDir` mounts in the same patch so the fix does not crash the app.
- Ports below 1024 need `NET_BIND_SERVICE`. Prefer moving to 8080 and keeping `drop: ["ALL"]`; `NET_BIND_SERVICE` is the only add permitted by restricted.
- `replicas: 1` plus a PDB with `minAvailable: 1` (or `maxUnavailable: 0`), or `minAvailable` equal to replicas, blocks node drains forever.
- If an HPA manages the Deployment, `spec.replicas` should be omitted or each apply resets it.
- Default-deny egress breaks DNS; always include a DNS allow (UDP and TCP 53 to `k8s-app: kube-dns` in `kube-system`) in the fix.
- In NetworkPolicy `from`/`to`, `namespaceSelector` and `podSelector` in ONE list item = AND; separate `-` items = OR. Check indentation.
- Memory `128Mi` vs `128M` differ; lowercase `m` on memory means milli-bytes (typo).
- Missing CPU limit is Low/Info (throttling debate); missing memory limit is High/Medium.
- Liveness probes must not check downstream dependencies (DB, other APIs); that causes restart cascades. Use a startupProbe instead of a large `initialDelaySeconds`. `successThreshold` must be 1 for liveness and startup.
- Selectors on Deployments and most StatefulSet fields are immutable; flag changes that will be rejected on update.
- Base64 in a `Secret` is not encryption. Suggest External Secrets, Sealed Secrets or SOPS; do not paste decoded values into the report.
- Version-sensitive facts (GA releases, ingress-nginx retirement dates, current Kubernetes version) change; state them as "verify against kubernetes.io" rather than asserting exact dates.
