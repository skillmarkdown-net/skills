---
name: iam-least-privilege-review
description: Reviews AWS IAM identity, resource, trust and permission boundary policies for least privilege and reports severity-ranked findings with a tightened policy JSON and IAM Access Analyzer validation commands. Use when asked to audit, review or tighten an IAM policy, check iam:PassRole, wildcards, NotAction, trust policy, cross-account, public S3 bucket policy or KMS key policy.
---

# IAM Least Privilege Review

Review AWS IAM policy documents (identity, resource, trust, permission boundary, SCP/RCP) for excess privilege. Produce findings by severity, a tightened policy, and commands to validate it with IAM Access Analyzer.

## Steps

1. **Identify the policy type and context.** Classify each document: identity policy, resource policy (S3 bucket, KMS key, SQS, SNS, Lambda...), role trust policy, permission boundary, SCP or RCP. Ask only if you cannot tell what the policy is attached to or what the workload does. If the intent is unknown, state your assumption in the report.
2. **Run the deterministic pre-scan** if the policy is in a file: `python3 scripts/iam_policy_scan.py policy.json`. It flags wildcards, NotAction/NotResource/NotPrincipal, PassRole, escalation primitives, public principals and missing conditions. It only finds patterns; you still judge context. Without a file, apply the same checklist by reading the JSON.
3. **Walk each statement** against [references/review-checklist.md](references/review-checklist.md). Check, in order:
   - Effect/Principal: `*` principal, `NotPrincipal`, account `:root` trust, unknown account IDs, deleted principals (`AIDA...`/`AROA...` unique IDs).
   - Action: `*`, service wildcards (`s3:*`, `iam:*`, `sts:*`), prefix wildcards (`iam:Create*`, `iam:Put*`, `iam:Attach*`), `NotAction`.
   - Resource: `*` on actions that support resource-level permissions, `NotResource`.
   - Escalation: see [references/privilege-escalation.md](references/privilege-escalation.md). Flag primitives on `*` or privileged roles, and PassRole paired with a compute action.
   - Conditions: confused deputy keys, org ID, MFA, ExternalId, OIDC/SAML audience and subject.
4. **Check the whole picture, not one statement.** An Allow can be neutralised by an explicit Deny elsewhere, and a boundary or SCP may cap it. Say so when you downgrade severity, and say when you cannot see those policies. A same-account resource policy naming a user or role ARN directly is not limited by the permission boundary.
5. **Assign severity** with the rubric below.
6. **Write the tightened policy.** Keep it functionally equivalent for the stated workload:
   - Replace wildcards with the specific actions needed. Check resource-level support in the Service Authorization Reference; some actions (`ec2:Describe*`, `s3:ListAllMyBuckets`) require `Resource: "*"`.
   - Scope PassRole to named role ARNs or a path and add `iam:PassedToService`.
   - Add the missing conditions. Give every statement a unique `Sid` and use `Version` `2012-10-17`.
   - If you must guess the required actions, say so and recommend last-accessed data or CloudTrail-based generation (step 8) before applying.
7. **Validate** using the commands in [references/access-analyzer-validation.md](references/access-analyzer-validation.md). Run `aws --version` first; older v2 builds lack `RESOURCE_CONTROL_POLICY` and newer values. Only run AWS CLI commands if the user asks and credentials exist; otherwise print them for the user.
8. **Tell the user how to confirm real usage** before they deploy a tightened identity policy: `aws iam generate-service-last-accessed-details` with `--granularity ACTION_LEVEL`, then `get-service-last-accessed-details`, or Access Analyzer policy generation from CloudTrail (`start-policy-generation`, `get-generated-policy`). Generated policies can contain wildcards and miss unlogged actions, so review them.

## Severity rubric

- **Critical**: public or unconditioned `*` principal with sensitive actions; `*:*` on `*`; trust policy assumable by anyone.
- **High**: `iam:PassRole` on `*`; escalation primitives on `*`; `Allow`+`NotAction` (Critical with `Resource: "*"`); permission-boundary tampering; third-party cross-account trust without `sts:ExternalId`; OIDC trust missing `aud` or `sub`.
- **Medium**: service principal without `aws:SourceArn`/`aws:SourceAccount`; no MFA on sensitive human roles; `Resource: "*"` on actions that support resource scoping; `:root` trust of a known internal account.
- **Low/Info**: style, unused Sids, missing `aws:SecureTransport` deny, validator `SUGGESTION` items.

Map validator output: `ERROR` and `SECURITY_WARNING` become High or Critical candidates, `WARNING` Medium, `SUGGESTION` Low.

## Output format

Use exactly this structure:

```
## Summary
One to three sentences: policy type, overall risk, count by severity.

## Findings
### [CRITICAL|HIGH|MEDIUM|LOW] <title> (Sid: <sid or statement index>)
- Issue: what is wrong and the attack or failure it enables
- Fix: the specific change

## Tightened policy
<json block>

## Assumptions and behaviour changes
- what may break, what you guessed

## Validate
<commands from the reference, with the real file names>
```

Example finding:

```
### [HIGH] PassRole allowed on any role (Sid: Deploy)
- Issue: `iam:PassRole` on `*` lets the holder pass an admin role to Lambda or EC2 and run code as it.
- Fix: limit Resource to `arn:aws:iam::111122223333:role/app/*` and add `iam:PassedToService = lambda.amazonaws.com`.
```

Order findings Critical first. Merge duplicates across statements into one finding listing all Sids.

## Gotchas

- Do not judge least privilege by searching for `*` only. Service and prefix wildcards are just as broad.
- `iam:PassRole` is a permission, not an API call, so CloudTrail has no PassRole event. The use shows in the consuming service call.
- `arn:aws:iam::<acct>:root` in a trust policy means the whole account, not the root user. The other account's IAM must still allow `sts:AssumeRole`.
- `Allow`+`NotAction` and `Allow`+`NotResource` cover future actions and resources. `Deny`+`NotAction` is a legitimate guardrail pattern; do not flag it as a defect.
- `NotPrincipal` with Allow is a validator security warning. Replace NotPrincipal+Deny with `Principal: "*"` and a Deny using `ArnNotLike` or `StringNotEquals` on `aws:PrincipalArn`. Use the role ARN, not the assumed-role ARN.
- MFA deny statements need `BoolIfExists` with `aws:MultiFactorAuthPresent` `false`. Plain `Bool` fails open for access-key calls because the key is absent.
- `aws:SourceArn` only exists when a service calls on behalf of a resource. For S3 buckets, whose ARNs hold no account ID, pair `aws:SourceArn` with `aws:SourceAccount`. Use `ArnLike` when the ARN has a wildcard.
- `aws:PrincipalOrgID` does not match service principals. Data-perimeter Denies need `BoolIfExists aws:PrincipalIsAWSService: false`.
- `aws:SourceIp`, `aws:SourceVpc` and `aws:SourceVpce` break for service-originated calls. A wide CIDR such as `0.0.0.0/0` is not a restriction.
- Validator checks policy grammar and best practice. A clean `validate-policy` result does not prove least privilege. The `check-*` commands prove only the specific property you ask about.
- `simulate-custom-policy` and `simulate-principal-policy` ignore SCPs/RCPs and some resource-policy conditions. Use them as a supplement.
- Do not invent account IDs, ARNs or condition values. Use clear placeholders such as `111122223333` and `<org-id>`, and list them in the assumptions section.
- Never include real credentials found in a pasted policy in your output; mask them.
