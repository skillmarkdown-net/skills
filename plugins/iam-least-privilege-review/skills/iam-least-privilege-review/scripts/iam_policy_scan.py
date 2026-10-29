#!/usr/bin/env python3
"""Pattern pre-scan for AWS IAM policy JSON. Standard library only, no network.

Usage:
    python3 scripts/iam_policy_scan.py policy.json [more.json ...]

Prints one line per finding: SEVERITY | Sid-or-index | message.
Exit code 1 if any CRITICAL or HIGH finding, else 0.
It finds patterns only; judge context yourself.
"""
import json
import sys

ESCALATION = {
    "iam:createpolicyversion", "iam:setdefaultpolicyversion",
    "iam:attachuserpolicy", "iam:attachgrouppolicy", "iam:attachrolepolicy",
    "iam:putuserpolicy", "iam:putgrouppolicy", "iam:putrolepolicy",
    "iam:createaccesskey", "iam:createloginprofile", "iam:updateloginprofile",
    "iam:addusertogroup", "iam:updateassumerolepolicy",
    "iam:deleteuserpermissionsboundary", "iam:deleterolepermissionsboundary",
    "iam:putuserpermissionsboundary", "iam:putrolepermissionsboundary",
}
SERVICE_PRINCIPALS_NEED_SOURCE = (".amazonaws.com",)


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def cond_keys(cond):
    keys = set()
    for op, body in (cond or {}).items():
        if isinstance(body, dict):
            for k in body:
                keys.add(k.lower())
    return keys


def principals(p):
    if p == "*":
        return ["*"]
    out = []
    if isinstance(p, dict):
        for k, v in p.items():
            for x in as_list(v):
                out.append((k, x))
    return out


def scan_statement(st, idx):
    f = []
    sid = st.get("Sid") or "#%d" % idx
    effect = st.get("Effect")
    actions = [a for a in as_list(st.get("Action"))]
    la = [a.lower() for a in actions]
    resources = as_list(st.get("Resource"))
    keys = cond_keys(st.get("Condition"))
    allow = effect == "Allow"

    if allow and "NotAction" in st:
        sev = "CRITICAL" if "*" in resources else "HIGH"
        f.append((sev, sid, "Allow with NotAction grants all other actions, including future ones"))
    if allow and "NotResource" in st:
        f.append(("HIGH", sid, "Allow with NotResource covers every other resource"))
    if allow and "NotPrincipal" in st:
        f.append(("HIGH", sid, "Allow with NotPrincipal is discouraged"))
    if allow:
        if "*" in la and "*" in resources:
            f.append(("CRITICAL", sid, "Action * on Resource *"))
        for a in la:
            if a.endswith("*") and a != "*":
                svc = a.split(":")[0]
                sev = "HIGH" if svc in ("iam", "sts", "organizations") else "MEDIUM"
                f.append((sev, sid, "Wildcard action %s" % a))
            if a in ESCALATION and ("*" in resources or not resources):
                f.append(("HIGH", sid, "Escalation primitive %s on *" % a))
        if "iam:passrole" in la or "iam:*" in la or "*" in la:
            if "*" in resources and "iam:passedtoservice" not in keys:
                f.append(("HIGH", sid, "iam:PassRole on * without iam:PassedToService"))
        if "sts:assumerole" in la and "*" in resources:
            f.append(("HIGH", sid, "sts:AssumeRole on *"))
        if "*" in resources and la and not any(a == "*" for a in la):
            f.append(("MEDIUM", sid, "Resource * - confirm the actions lack resource-level support"))

    if allow and "Principal" in st:
        for p in principals(st["Principal"]):
            kind, val = ("AWS", "*") if p == "*" else p
            if val == "*":
                restricting = {"aws:principalorgid", "aws:sourcevpce", "aws:sourcevpc",
                               "aws:sourcearn", "aws:sourceaccount", "aws:principalarn",
                               "kms:calleraccount", "aws:principalorgpaths"}
                if not (keys & restricting):
                    f.append(("CRITICAL", sid, "Public principal * with no restricting condition"))
                else:
                    f.append(("LOW", sid, "Principal * relies on conditions; verify with check-no-public-access"))
            elif val.endswith(":root"):
                f.append(("MEDIUM", sid, "Trusts whole account %s; check allowlist and ExternalId" % val))
            elif val.startswith(("AIDA", "AROA")):
                f.append(("LOW", sid, "Unique ID principal %s: deleted principal" % val))
            elif kind == "Service" and val.endswith(SERVICE_PRINCIPALS_NEED_SOURCE):
                if not (keys & {"aws:sourcearn", "aws:sourceaccount", "aws:sourceorgid"}):
                    f.append(("MEDIUM", sid, "Service principal %s without aws:SourceArn/SourceAccount" % val))
            elif kind == "Federated" and "token.actions.githubusercontent.com" in val:
                if not any(k.endswith(":sub") for k in keys):
                    f.append(("HIGH", sid, "GitHub OIDC trust without :sub condition"))
                if not any(k.endswith(":aud") for k in keys):
                    f.append(("HIGH", sid, "GitHub OIDC trust without :aud condition"))
    return f


def scan(doc):
    findings = []
    if doc.get("Version") != "2012-10-17":
        findings.append(("LOW", "policy", "Version should be 2012-10-17"))
    stmts = as_list(doc.get("Statement"))
    sids = [s.get("Sid") for s in stmts if s.get("Sid")]
    if len(sids) != len(set(sids)):
        findings.append(("LOW", "policy", "Duplicate Sid values"))
    for i, st in enumerate(stmts):
        findings.extend(scan_statement(st, i))
    return findings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    bad = False
    for path in argv[1:]:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        print("== %s" % path)
        for sev, sid, msg in sorted(scan(doc), key=lambda x: order[x[0]]):
            print("%s | %s | %s" % (sev, sid, msg))
            if sev in ("CRITICAL", "HIGH"):
                bad = True
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
