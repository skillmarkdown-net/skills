# Review checklist

Walk every workload's pod template (containers, initContainers, ephemeralContainers).

## 1. Workload security
- `privileged: true`: remove.
- `hostNetwork`, `hostPID`, `hostIPC`, `hostPort`, `hostPath` (esp. `/`, `/var/run/docker.sock`, container runtime sockets): remove or justify.
- `allowPrivilegeEscalation` must be `false`.
- `runAsNonRoot: true`, numeric `runAsUser` not 0.
- `capabilities.drop: ["ALL"]`; only add `NET_BIND_SERVICE` if needed. Anything else added = finding.
- `seccompProfile.type: RuntimeDefault` (or `Localhost`); `Unconfined` is a baseline violation.
- AppArmor: use the `appArmorProfile` securityContext field, not the deprecated `container.apparmor.security.beta.kubernetes.io/*` annotations (verify version support).
- `readOnlyRootFilesystem: true` (best practice, not PSS) with emptyDir mounts for writable paths.
- `automountServiceAccountToken: false` when the pod does not call the API.
- Volume types under restricted: configMap, csi, downwardAPI, emptyDir, ephemeral, persistentVolumeClaim, projected, secret only.
- Optional hardening: `hostUsers: false` (user namespaces) if cluster supports it.
- Pod Security Admission labels live on the Namespace: `pod-security.kubernetes.io/enforce|audit|warn` plus `-version`. If a Namespace is in the input, check them; otherwise "cannot determine".

## 2. Resources
- Memory request and limit on every container, ideally equal.
- CPU request always; CPU limit optional (Low/Info if missing).
- Only limits set: requests default to limits (fine). Nothing set: BestEffort, evicted first.
- Unit typos: `m` vs `M`/`Mi` on memory.
- Namespace LimitRange/ResourceQuota may supply defaults or reject omissions: cannot determine from the workload alone.
- JVM/Node: heap settings should track the memory limit.

## 3. Probes
- Readiness on anything behind a Service.
- Liveness checks only own process health.
- Startup probe for slow boots: budget is `failureThreshold x periodSeconds` (e.g. 30 x 10 = 300 s).
- Defaults: initialDelay 0, period 10, timeout 1, success 1, failure 3.
- httpGet/tcpSocket/grpc port must match a `containerPort` number or declared name.
- Same endpoint and thresholds for liveness and readiness = smell.
- Jobs usually need no probes.

## 4. Images
- No tag or `:latest`: High. Floating tags (`:1`, `:stable`): Medium. Tag without digest: Low/Medium for production.
- Digest form `repo/name@sha256:<64 hex>`; `name:1.2.3@sha256:...` allowed, digest wins.
- Default pullPolicy: Always for latest/untagged, else IfNotPresent.
- Private registry needs `imagePullSecrets`; check registry allowlist.
- Suggest Renovate/Dependabot to bump digests; signature policy via Kyverno `verifyImages` or sigstore policy-controller.

## 5. Availability
- Production: at least 2 replicas, 3 for zone-spread.
- PDB `policy/v1` with exactly one of `minAvailable`/`maxUnavailable`; selector must match pods; consider `unhealthyPodEvictionPolicy: AlwaysAllow` if unready pods block drains (verify version).
- `topologySpreadConstraints` (`maxSkew`, `topologyKey: topology.kubernetes.io/zone`, `whenUnsatisfiable`, `labelSelector`) or anti-affinity.
- StatefulSet: `serviceName` references an existing headless Service (`clusterIP: None`); check `volumeClaimTemplates`, `persistentVolumeClaimRetentionPolicy` (Retain/Delete), `podManagementPolicy`, `updateStrategy`.
- Defaults: maxSurge/maxUnavailable 25%, revisionHistoryLimit 10, terminationGracePeriodSeconds 30.

## 6. NetworkPolicy (`networking.k8s.io/v1`)
- Is there a default-deny for the namespace? If not, finding on sensitive namespaces.
- Enforced only if the CNI supports it (Calico, Cilium, Antrea yes; plain flannel no): cannot determine.
- Egress default-deny needs DNS allow.
- `ingress: [{}]` allows everything.
- Consider blocking `169.254.169.254` egress via `ipBlock.except` for ordinary workloads.
- No L7/FQDN rules in core API.

Default deny plus DNS:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: default-deny-all}
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: allow-dns}
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}
      podSelector: {matchLabels: {k8s-app: kube-dns}}
    ports:
    - {protocol: UDP, port: 53}
    - {protocol: TCP, port: 53}
```

## 7. RBAC
- Wildcard `*` in verbs/resources/apiGroups: High/Critical.
- cluster-admin or `system:masters` bound to workload SA: Critical.
- Bindings to `system:authenticated`, `system:unauthenticated`, or the `default` ServiceAccount.
- Verbs `escalate`, `bind`, `impersonate`.
- `get/list/watch` on `secrets` (list alone discloses contents).
- `create` on `pods`, `pods/exec`, `pods/attach`, `pods/portforward`, `serviceaccounts/token`, `nodes/proxy`.
- Write access to roles, rolebindings, clusterrolebindings, webhook configurations, CRDs.
- Prefer Role+RoleBinding over cluster-wide; use `resourceNames` where possible; dedicated ServiceAccount per workload.
- Flag `type: kubernetes.io/service-account-token` Secrets.
- Verify: `kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa> -n <ns>`.

## 8. Service and Ingress
- Service selector matches template labels exactly; `targetPort` matches a containerPort number/name.
- `LoadBalancer`/`NodePort` = exposure: check `loadBalancerSourceRanges`, `externalTrafficPolicy`, internal-LB annotations.
- `externalIPs` (CVE-2020-8554): flag.
- `Endpoints` objects deprecated in favour of EndpointSlice.
- Ingress `networking.k8s.io/v1`: `pathType` required; use `spec.ingressClassName` not the `kubernetes.io/ingress.class` annotation; `tls[].secretName` exists and hosts match; backend uses `service.name` + `service.port.number|name`.
- Snippet annotations (`configuration-snippet`, `server-snippet`) are a risk surface.
- Community ingress-nginx is announced as retiring (best-effort maintenance only until about March 2026; verify on kubernetes.io/blog). Flag new dependence as Info/Medium and suggest Gateway API (`HTTPRoute`) or another maintained controller.

## 9. Secrets and config
- Plaintext `Secret` `data:`/`stringData:` committed: Critical/High.
- Literal `value:` on env named `*PASSWORD*`, `*TOKEN*`, `*KEY*`: use `secretKeyRef`; prefer volume mounts.

## 10. Deprecated/removed APIs
- Ingress `extensions/v1beta1`, `networking.k8s.io/v1beta1`: removed 1.22.
- PodSecurityPolicy, `policy/v1beta1` PDB, `batch/v1beta1` CronJob: removed 1.25.
- `autoscaling/v2beta2`: removed 1.26.
- `flowcontrol.apiserver.k8s.io/v1beta3`: removed 1.32.
- Check the target version; `pluto detect-files -d .` automates this.
