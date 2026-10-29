# Privilege escalation primitives

Flag these as High (Critical when the result is full admin) when granted on `*` or on privileged roles/users, and when not constrained by a boundary or conditions. Catalogue to cross-check: Rhino Security Labs 'AWS IAM Privilege Escalation - Methods and Mitigation', Hacking The Cloud.

## Direct IAM manipulation
- `iam:CreatePolicyVersion` and `iam:SetDefaultPolicyVersion`
- `iam:AttachUserPolicy`, `iam:AttachGroupPolicy`, `iam:AttachRolePolicy`
- `iam:PutUserPolicy`, `iam:PutGroupPolicy`, `iam:PutRolePolicy`
- `iam:CreateAccessKey`, `iam:CreateLoginProfile`, `iam:UpdateLoginProfile` (on other users)
- `iam:AddUserToGroup`
- `iam:UpdateAssumeRolePolicy` (rewrite a role's trust) and `sts:AssumeRole` on `*`
- `iam:CreateServiceLinkedRole`, `organizations:*`
- Permission boundary tampering: `iam:DeleteUserPermissionsBoundary`, `iam:DeleteRolePermissionsBoundary`, `iam:PutUserPermissionsBoundary`, `iam:PutRolePermissionsBoundary`
- `iam:CreateRole` or `iam:CreateUser` without an `iam:PermissionsBoundary` condition

## PassRole plus a service that runs code
`iam:PassRole` alone changes nothing; the danger is PassRole plus one of:
| Combination | Path |
|---|---|
| `ec2:RunInstances` | start an instance with a powerful instance profile |
| `lambda:CreateFunction` + `lambda:InvokeFunction` or `lambda:CreateEventSourceMapping` | run code as the passed role |
| `cloudformation:CreateStack` | stack deploys resources with the passed role |
| `glue:CreateDevEndpoint` | shell as the passed role |
| `sagemaker:CreateNotebookInstance` | notebook as the passed role |
| `ecs:RegisterTaskDefinition` + `ecs:RunTask` | container as task role |
| `codebuild:CreateProject` | build commands as the passed role |
| `datapipeline:CreatePipeline` | pipeline as the passed role |

No PassRole needed: `lambda:UpdateFunctionCode` (code runs as the function's existing role), `ssm:SendCommand` / `ssm:StartSession` (run on instances with their profile), `ec2:ModifyInstanceAttribute` (change userData).

## Tightening PassRole
```json
{
  "Sid": "PassAppRolesToEcsOnly",
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::111122223333:role/app/*",
  "Condition": {"StringEquals": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}}
}
```
Validator names: Pass role with star in resource; with star in action and resource; with NotResource; with star in action and NotResource; with NotAction and NotResource; with star in resource and NotAction.

## Delegated admin guardrail
Allow `iam:CreateRole`, `iam:PutRolePolicy`, `iam:AttachRolePolicy` only with `StringEquals` `iam:PermissionsBoundary` set to the approved boundary ARN, and add a Deny on `iam:DeleteRolePermissionsBoundary`, `iam:PutRolePermissionsBoundary`, `iam:DeletePolicy`, `iam:DeletePolicyVersion`, `iam:CreatePolicyVersion` for the boundary policy ARN.
