#!/usr/bin/env python3
"""Review a Terraform/OpenTofu plan JSON for risky changes.

Usage:
    terraform show -json tfplan > tfplan.json
    python3 scripts/plan_review.py tfplan.json [--format table|json]

Exit codes: 0 GO, 10 GO WITH REVIEW, 20 NO-GO, 2 unreadable input.
Standard library only. Never prints sensitive values; no network access.
"""
import json
import sys

STATEFUL = ("aws_db_instance", "aws_rds_cluster", "aws_s3_bucket", "aws_ebs_volume",
            "aws_kms_key", "aws_dynamodb_table", "aws_efs_file_system",
            "aws_elasticache_", "aws_route53_zone")
RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "UNVERIFIED": 3}
WORLD = ("0.0.0.0/0", "::/0")
SENSITIVE_PORTS = (22, 3389, 3306, 5432, 1433, 27017, 6379, 9200)
IAM_POLICY_FIELDS = {
    "aws_iam_policy": ["policy"], "aws_iam_role_policy": ["policy"],
    "aws_iam_user_policy": ["policy"], "aws_iam_group_policy": ["policy"],
    "aws_iam_role": ["assume_role_policy"],
}
ADMIN_ATTACH = ("aws_iam_role_policy_attachment", "aws_iam_policy_attachment",
                "aws_iam_user_policy_attachment", "aws_iam_group_policy_attachment")


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def classify(actions):
    if actions == ["delete"]:
        return "destroy"
    if "delete" in actions and "create" in actions:
        return "replace"
    for a in ("create", "update", "forget", "read"):
        if actions == [a]:
            return a
    return "no-op"


def unknown(rc, field):
    au = rc["change"].get("after_unknown") or {}
    return bool(au.get(field)) if isinstance(au, dict) else False


def parse_policy(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return None


def principal_is_star(p):
    if p == "*":
        return True
    if isinstance(p, dict):
        return any("*" in as_list(v) for v in p.values())
    return False


def check_policy(doc, trust, add):
    for st in as_list(doc.get("Statement")):
        if st.get("Effect") != "Allow":
            continue
        acts = [str(a) for a in as_list(st.get("Action"))]
        res = [str(r) for r in as_list(st.get("Resource"))]
        if any(a in ("*", "*:*") for a in acts):
            add("CRITICAL", "Allow Action '*'")
        elif any(a.endswith(":*") for a in acts):
            add("HIGH", "Service-wide wildcard action")
        if "NotAction" in st:
            add("HIGH", "Allow with NotAction")
        if "NotResource" in st:
            add("HIGH", "Allow with NotResource")
        if any(a.lower() == "iam:passrole" for a in acts) and "*" in res:
            add("HIGH", "iam:PassRole on Resource '*'")
        elif "*" in res and acts and not any(a in ("*", "*:*") for a in acts):
            add("MEDIUM", "Resource '*' with specific actions")
        if trust and principal_is_star(st.get("Principal")) and not st.get("Condition"):
            add("CRITICAL", "Principal '*' without Condition in trust policy")


def port_hit(frm, to, proto):
    if str(proto) == "-1":
        return "all"
    try:
        frm, to = int(frm), int(to)
    except (TypeError, ValueError):
        return "all"
    return [p for p in SENSITIVE_PORTS if frm <= p <= to]


def sg_rule(rule, cidrs, add):
    if not any(c in WORLD for c in cidrs):
        return
    hit = port_hit(rule.get("from_port"), rule.get("to_port"), rule.get("ip_protocol", rule.get("protocol")))
    if hit:
        add("CRITICAL", "Sensitive/all ports open to world: %s" % (hit,))
    else:
        try:
            web = {int(rule.get("from_port")), int(rule.get("to_port"))} <= {80, 443}
        except (TypeError, ValueError):
            web = False
        add("MEDIUM" if web else "HIGH", "Ports %s-%s open to world" % (rule.get("from_port"), rule.get("to_port")))


def review(plan):
    findings = []
    counts = {k: 0 for k in ("create", "update", "destroy", "replace", "forget")}
    if not str(plan.get("format_version", "")).startswith("1."):
        findings.append(("UNVERIFIED", "(plan)", "-", "Unrecognised format_version", "format_version"))
    if plan.get("errored"):
        findings.append(("UNVERIFIED", "(plan)", "-", "Plan marked errored", "errored"))
    for rc in plan.get("resource_changes") or []:
        if rc.get("mode") != "managed":
            continue
        ch = rc.get("change", {})
        act = classify(ch.get("actions", []))
        if act in counts:
            counts[act] += 1
        addr, typ = rc.get("address"), rc.get("type", "")
        after = ch.get("after") or {}

        def add(sev, msg, reason="", _a=addr, _act=act):
            findings.append((sev, _a, _act, msg, reason))

        if act in ("destroy", "replace"):
            reason = str(rc.get("action_reason", ""))
            paths = ch.get("replace_paths")
            if paths:
                reason += "; paths " + json.dumps(paths)
            sev = "HIGH" if typ.startswith(STATEFUL) else "MEDIUM"
            add(sev, ("Stateful resource " if sev == "HIGH" else "Resource ") + act + "d", reason.strip("; "))
        if act in ("delete", "destroy", "no-op", "read", "forget"):
            continue
        if typ == "aws_s3_bucket_public_access_block":
            for f in ("block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets"):
                if after.get(f) is False:
                    add("CRITICAL", "S3 public access block disabled: " + f, f)
                elif unknown(rc, f):
                    add("UNVERIFIED", f + " unknown at plan time", "after_unknown")
        elif typ == "aws_s3_bucket_acl":
            if after.get("acl") in ("public-read", "public-read-write"):
                add("CRITICAL", "Public S3 ACL " + str(after.get("acl")), "acl")
            elif after.get("acl") == "authenticated-read":
                add("HIGH", "S3 ACL readable by any AWS account", "acl")
            elif unknown(rc, "acl"):
                add("UNVERIFIED", "acl unknown at plan time", "after_unknown")
        elif typ == "aws_s3_bucket_policy":
            if unknown(rc, "policy"):
                add("UNVERIFIED", "bucket policy unknown at plan time", "after_unknown")
            else:
                doc = parse_policy(after.get("policy"))
                if doc is None:
                    add("UNVERIFIED", "bucket policy not parseable", "policy")
                else:
                    for st in as_list(doc.get("Statement")):
                        if st.get("Effect") == "Allow" and principal_is_star(st.get("Principal")):
                            add("MEDIUM" if st.get("Condition") else "CRITICAL",
                                "Bucket policy allows Principal '*'" + (" with Condition" if st.get("Condition") else ""), "policy")
        elif typ == "aws_security_group":
            for r in as_list(after.get("ingress")):
                sg_rule(r, as_list(r.get("cidr_blocks")) + as_list(r.get("ipv6_cidr_blocks")), add)
            if unknown(rc, "ingress"):
                add("UNVERIFIED", "ingress unknown at plan time", "after_unknown")
        elif typ == "aws_security_group_rule" and after.get("type") == "ingress":
            sg_rule(after, as_list(after.get("cidr_blocks")) + as_list(after.get("ipv6_cidr_blocks")), add)
        elif typ == "aws_vpc_security_group_ingress_rule":
            sg_rule(after, [after.get("cidr_ipv4"), after.get("cidr_ipv6")], add)
            if unknown(rc, "cidr_ipv4") or unknown(rc, "cidr_ipv6"):
                add("UNVERIFIED", "CIDR unknown at plan time", "after_unknown")
        elif typ in IAM_POLICY_FIELDS:
            for f in IAM_POLICY_FIELDS[typ]:
                if unknown(rc, f):
                    add("UNVERIFIED", f + " unknown at plan time", "after_unknown")
                elif after.get(f):
                    doc = parse_policy(after[f])
                    if doc is None:
                        add("UNVERIFIED", f + " not parseable", f)
                    else:
                        check_policy(doc, f == "assume_role_policy", lambda s, m, _f=f: add(s, m, _f))
        elif typ in ADMIN_ATTACH:
            if str(after.get("policy_arn", "")).endswith("/AdministratorAccess"):
                add("CRITICAL", "AdministratorAccess attached", "policy_arn")
    findings.sort(key=lambda f: RANK[f[0]])
    if any(f[0] in ("CRITICAL", "HIGH", "UNVERIFIED") for f in findings):
        verdict, code = "NO-GO", 20
    elif findings:
        verdict, code = "GO WITH REVIEW", 10
    else:
        verdict, code = "GO", 0
    return counts, findings, verdict, code


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    fmt = "json" if "--format" in argv and argv[argv.index("--format") + 1] == "json" else "table"
    if fmt == "json":
        args = [a for a in args if a != "json"]
    if not args:
        print(__doc__)
        return 2
    try:
        with open(args[0]) as fh:
            plan = json.load(fh)
    except Exception as exc:
        print("Cannot read plan: %s\nVERDICT: NO-GO (could not verify)" % exc)
        return 2
    counts, findings, verdict, code = review(plan)
    if fmt == "json":
        print(json.dumps({"counts": counts, "verdict": verdict, "findings": [
            dict(zip(("severity", "address", "action", "finding", "reason"), f)) for f in findings]}, indent=2))
        return code
    print("Plan: terraform %s, format %s | %s" % (plan.get("terraform_version", "?"), plan.get("format_version", "?"),
          ", ".join("%s %d" % kv for kv in counts.items())))
    print("\n| Severity | Address | Action | Finding | Reason |\n|---|---|---|---|---|")
    for f in findings:
        print("| " + " | ".join(f) + " |")
    if plan.get("resource_drift"):
        print("\nNotes: resource_drift shows %d change(s) made outside Terraform." % len(plan["resource_drift"]))
    print("\nVERDICT: " + verdict)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
