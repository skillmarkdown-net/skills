---
name: terraform-plan-risk-review
description: "Reviews a saved Terraform or OpenTofu plan (tfplan, tfplan.json) before apply: flags destroyed or replaced resources, public S3 buckets, security groups open to 0.0.0.0/0 or ::/0 and IAM wildcards, then prints a risk table and a GO / NO-GO verdict. Use when asked to review, vet, audit or sanity-check a terraform plan, plan JSON or terraform show -json output before apply."
---

# Terraform Plan Risk Review

Review a saved Terraform/OpenTofu plan and give a risk table plus a GO / GO WITH REVIEW / NO-GO verdict. Review only: never run `terraform apply`.

## Steps

1. **Get the plan JSON.** If the user pasted or pointed to `tfplan.json`, use it. If only a binary `tfplan` exists, run:
   ```
   terraform show -json tfplan > tfplan.json
   ```
   (`tofu show -json tfplan` for OpenTofu). If there is no saved plan, tell the user to produce one so the reviewed plan is the applied plan:
   ```
   terraform init -input=false
   terraform plan -out=tfplan -input=false
   terraform show -json tfplan > tfplan.json
   ```
   Never parse human-readable plan text if JSON can be had. If only text is available, review it but state that the review is lower confidence.
2. **Run the scanner** for the deterministic checks:
   ```
   python3 scripts/plan_review.py tfplan.json
   ```
   It prints counts, findings as JSON lines and a verdict. Use `--format table` (default) or `--format json`. Exit code: 0 GO, 10 GO WITH REVIEW, 20 NO-GO, 2 could not parse. If you cannot run Python, apply the rules in [references/risk-rules.md](references/risk-rules.md) by hand with `jq`.
3. **Check the plan header.** `format_version` should start with `1.`; if not, warn that the format is unrecognised and the verdict is NO-GO (could not verify). If `errored` is true or the JSON is incomplete, verdict is NO-GO.
4. **Count actions** over `resource_changes` where `mode == "managed"` (exclude data sources). Classify by `change.actions`:
   - destroy: exactly `["delete"]`
   - replace: contains both `delete` and `create` (`["delete","create"]` destroy-first, `["create","delete"]` create-before-destroy)
   - create, update, no-op, forget as named. Report `forget` but treat as low risk.
   Include resources in child modules (`module_address`).
5. **Apply the rule families** in [references/risk-rules.md](references/risk-rules.md): destroys/replaces (stateful types HIGH, others MEDIUM), public S3, world-open ingress, IAM wildcards. Evaluate `after`, and also `after_unknown`: if a checked field is unknown at plan time, record an UNVERIFIED finding.
6. **Add the why.** For each destroy/replace put `action_reason` (e.g. `replace_because_cannot_update`) and `replace_paths` in the Reason column.
7. **Note drift.** If `resource_drift` is non-empty, add one line noting changes made outside Terraform.
8. **Decide the verdict:**
   - NO-GO: any CRITICAL or HIGH finding, any UNVERIFIED finding, unparseable or errored plan.
   - GO WITH REVIEW: only MEDIUM findings.
   - GO: no findings.
   Always list what a human must confirm to flip a NO-GO (for example, an intentional replace of a database with a verified backup).
9. **Suggest complements** only briefly: `checkov -f tfplan.json` (use `--framework terraform_plan` if needed), `trivy config .`, or OPA/Conftest for custom policy. These supplement, not replace, this review.

## Output format

Print, in this order: plan summary line, risk table (sorted CRITICAL, HIGH, MEDIUM, UNVERIFIED), notes, verdict.

```
Plan: terraform 1.9.8, format 1.2 | create 3, update 1, destroy 1, replace 1, forget 0

| Severity | Address | Action | Finding | Reason |
|---|---|---|---|---|
| CRITICAL | aws_vpc_security_group_ingress_rule.ssh | create | SSH 22 open to 0.0.0.0/0 | cidr_ipv4 |
| HIGH | module.db.aws_db_instance.main | replace | Stateful resource replaced | replace_because_cannot_update; engine_version |
| MEDIUM | aws_instance.batch | destroy | Resource destroyed | delete_because_no_resource_config |
| UNVERIFIED | aws_iam_policy.app | create | policy unknown at plan time | after_unknown |

Notes: resource_drift shows 1 change made outside Terraform.

VERDICT: NO-GO
To proceed: restrict SSH CIDR; confirm DB snapshot and intended replace; resolve unknown IAM policy.
```

## Gotchas

- A replace is a two-element array. Testing `actions == ["delete"]` misses replaces; test `"delete" in actions`.
- `plan -detailed-exitcode` returning 2 means changes exist, not failure.
- Check `::/0` and `ipv6_cidr_blocks` / `cidr_ipv6`, not just `0.0.0.0/0`. `cidr_ipv4` is a string; `cidr_blocks` is a list.
- `protocol = "-1"` means all ports; ignore `from_port`/`to_port`.
- IAM `policy` is a JSON string: parse it. `Statement`, `Action`, `Resource` may be a string or a list. `NotAction`/`NotResource` with Allow count as wildcards. Ignore Deny statements.
- Only judge S3 absence of a public access block by comparing with `configuration` or `prior_state`; otherwise say so.
- Never print values flagged in `before_sensitive` / `after_sensitive`. Quote only addresses, field names and CIDRs/actions.
- A failed plan caused by `prevent_destroy` is an informative result: report it rather than retrying.
- Egress to 0.0.0.0/0 is normal; flag ingress only.
- Do not say GO if you could not analyse the whole plan.
