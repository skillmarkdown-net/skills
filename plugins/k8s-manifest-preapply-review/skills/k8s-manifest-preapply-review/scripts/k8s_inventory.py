#!/usr/bin/env python3
"""First-pass Kubernetes manifest scanner (standard library only, no network).

Usage:
    python k8s_inventory.py <file-or-dir> [more paths...]

Reads .yaml/.yml files, splits documents on lines that are exactly '---',
and uses line-based heuristics (no YAML parser available in the stdlib) to
print each object as kind/name/namespace plus mechanical flags. Output is a
lead list for a human or agent review, not a verdict: nested or unusual
layouts (anchors, flow style, Helm templates) can be missed.
"""
import os
import re
import sys

WORKLOADS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Pod", "ReplicaSet"}


def files(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for n in sorted(names):
                    if n.endswith((".yaml", ".yml")):
                        yield os.path.join(root, n)
        elif os.path.isfile(p):
            yield p


def first(pattern, text, default="?"):
    m = re.search(pattern, text, re.M)
    return m.group(1).strip().strip('"\'') if m else default


def analyse(doc):
    kind = first(r"^kind:\s*(\S+)", doc)
    name = first(r"^  name:\s*(\S+)", doc)
    ns = first(r"^  namespace:\s*(\S+)", doc, "(none)")
    api = first(r"^apiVersion:\s*(\S+)", doc)
    flags = []
    if kind == "?":
        return None
    if api in ("extensions/v1beta1", "networking.k8s.io/v1beta1", "policy/v1beta1",
               "batch/v1beta1", "autoscaling/v2beta2", "flowcontrol.apiserver.k8s.io/v1beta3"):
        flags.append("removed/deprecated apiVersion " + api)
    if kind in WORKLOADS:
        if re.search(r"privileged:\s*true", doc):
            flags.append("CRITICAL privileged: true")
        for h in ("hostNetwork", "hostPID", "hostIPC"):
            if re.search(h + r":\s*true", doc):
                flags.append("CRITICAL " + h)
        if "hostPath:" in doc:
            flags.append("hostPath volume")
        if not re.search(r"allowPrivilegeEscalation:\s*false", doc):
            flags.append("allowPrivilegeEscalation not false")
        if not re.search(r"runAsNonRoot:\s*true", doc):
            flags.append("runAsNonRoot not true")
        if not re.search(r"readOnlyRootFilesystem:\s*true", doc):
            flags.append("readOnlyRootFilesystem not true")
        if not re.search(r"drop:\s*\[?\s*\"?ALL", doc) and not re.search(r"drop:\s*\n\s*-\s*\"?ALL", doc):
            flags.append("capabilities drop ALL missing")
        if not re.search(r"seccompProfile", doc):
            flags.append("seccompProfile missing")
        for img in re.findall(r"^\s*-?\s*image:\s*(\S+)", doc, re.M):
            img = img.strip('"\'')
            if "@sha256:" in img:
                continue
            last = img.rsplit("/", 1)[-1]
            if ":" not in last:
                flags.append("image without tag: " + img)
            elif last.endswith(":latest"):
                flags.append("image :latest: " + img)
            else:
                flags.append("image tag without digest: " + img)
        if not re.search(r"limits:", doc):
            flags.append("no resources.limits")
        if not re.search(r"requests:", doc):
            flags.append("no resources.requests")
        if kind in ("Deployment", "StatefulSet", "DaemonSet", "Pod"):
            if not re.search(r"readinessProbe:", doc):
                flags.append("no readinessProbe")
            if not re.search(r"livenessProbe:", doc):
                flags.append("no livenessProbe")
        if kind in ("Deployment", "StatefulSet"):
            rep = first(r"^  replicas:\s*(\d+)", doc, "")
            if rep == "1":
                flags.append("replicas: 1")
        if not re.search(r"automountServiceAccountToken:\s*false", doc):
            flags.append("automountServiceAccountToken not false")
    if kind in ("Role", "ClusterRole"):
        if re.search(r"-\s*['\"]?\*['\"]?\s*$|\[\s*['\"]?\*['\"]?\s*\]", doc, re.M):
            flags.append("wildcard in rules")
        if re.search(r"secrets", doc):
            flags.append("rule touches secrets")
    if kind in ("RoleBinding", "ClusterRoleBinding") and re.search(r"name:\s*cluster-admin", doc):
        flags.append("CRITICAL binds cluster-admin")
    if kind == "Secret" and re.search(r"^(data|stringData):", doc, re.M):
        flags.append("Secret with inline data")
    if kind == "Ingress":
        if "pathType" not in doc:
            flags.append("pathType missing")
        if "kubernetes.io/ingress.class" in doc:
            flags.append("deprecated ingress.class annotation")
        if re.search(r"snippet", doc):
            flags.append("snippet annotation")
    if kind == "Service":
        t = first(r"^  type:\s*(\S+)", doc, "ClusterIP")
        if t in ("LoadBalancer", "NodePort"):
            flags.append("exposed Service type " + t)
        if "externalIPs" in doc:
            flags.append("externalIPs set")
    return kind, name, ns, flags


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    total = 0
    for path in files(sys.argv[1:]):
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for doc in re.split(r"^---\s*$", text, flags=re.M):
            res = analyse(doc)
            if not res:
                continue
            kind, name, ns, flags = res
            total += 1
            print("%s/%s/%s  (%s)" % (kind, name, ns, path))
            for f in flags:
                print("    - " + f)
    print("\n%d objects scanned. Heuristic output: verify each lead in the YAML." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
