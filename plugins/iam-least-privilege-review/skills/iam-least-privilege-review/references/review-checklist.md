# IAM review checklist

Work through every statement. Source pages to re-verify specifics: the IAM User Guide policy reference and the Service Authorization Reference.

## Wildcards
- `Action: "*"` or `*:*` on `Resource: "*"`: Critical.
- Service wildcards: `iam:*`, `sts:*`, `kms:*`, `s3:*`, `organizations:*`. High for iam/sts/organizations; Medium to High for data services depending on resources.
- Prefix wildcards: `iam:Create*`, `iam:Put*`, `iam:Attach*`, `iam:Update*`. These include escalation actions. High.
- `Resource: "*"` on actions that support resource-level permissions: Medium. Some actions need `*` (`ec2:Describe*`, `s3:ListAllMyBuckets`); do not flag those.

## Not* elements
- `Allow` + `NotAction`: High, Critical with `Resource: "*"`. Includes future actions.
- `Allow` + `NotResource`: High. Includes resources created later. Validator flags PassRole with NotResource.
- `Allow` + `NotPrincipal`: validator security warning. Replace with explicit principals.
- `Deny` + `NotAction`: usually a guardrail (for example deny all except IAM self-service when no MFA). Verify intent.

## Principals and trust
- `Principal: "*"` or `{"AWS":"*"}` with Allow and no restricting condition: Critical.
- `arn:aws:iam::<acct>:root`: delegates to the whole account. Medium for known internal accounts, High for external accounts without ExternalId or MFA.
- Account IDs not on the user's allowlist: external trust. Ask for the allowlist or list them.
- Unique IDs `AIDA...` or `AROA...` as principals: deleted principal; remove.
- Third-party cross-account role: require `sts:ExternalId` with `StringEquals`, unique per customer. For human cross-account access prefer MFA or federation.
- Service principal (`lambda.amazonaws.com`, `sns.amazonaws.com`, `s3.amazonaws.com`, `cloudtrail.amazonaws.com`, `events.amazonaws.com`): require `aws:SourceArn` and/or `aws:SourceAccount`.
- OIDC (`sts:AssumeRoleWithWebIdentity`): GitHub Actions needs `token.actions.githubusercontent.com:aud` and `:sub`. Do not use `StringLike` with `repo:*`. Validator checks: Missing GitHub repo condition key, Missing condition key for OIDC principal.
- SAML: require `SAML:aud`.
- Trust policy size: default quota 2,048 characters, adjustable to 4,096.

## Conditions to look for
| Goal | Key and operator |
|---|---|
| Confused deputy | `aws:SourceArn` (`ArnEquals`/`ArnLike`) plus `aws:SourceAccount` (`StringEquals`) |
| Org scoping | `aws:PrincipalOrgID` (`StringEquals`), `aws:PrincipalOrgPaths`; for services `aws:SourceOrgID` |
| MFA in Allow/trust | `Bool` `aws:MultiFactorAuthPresent: "true"` |
| MFA in Deny | `BoolIfExists` `aws:MultiFactorAuthPresent: "false"` |
| Recent MFA | `NumericLessThan` `aws:MultiFactorAuthAge` (seconds) |
| PassRole scope | `StringEquals` `iam:PassedToService`; `iam:AssociatedResourceArn` for some services |
| Boundary enforcement | `StringEquals` `iam:PermissionsBoundary: <arn>` on CreateRole/CreateUser/Put*Policy |
| TLS only | Deny with `Bool` `aws:SecureTransport: "false"` |

Validator security warnings worth citing by name: Allow with NotPrincipal; Pass role with star in resource; Pass role with NotResource; Missing paired condition keys; Untrustworthy condition key; ForAllValues with single valued key; Restrict access to service principal; String like operator with ARN condition keys; S3 prefix in negative context.

## Permission boundaries, SCPs, RCPs
- A boundary caps identity-based permissions of users and roles (not groups) and grants nothing alone.
- Same-account resource policy naming a user or role ARN directly is not limited by the boundary; for assumed-role sessions it is.
- Delegated admins should only `iam:CreateRole` and `iam:PutRolePolicy` with `iam:PermissionsBoundary` equal to the approved ARN, and be denied deletion of the boundary and its policy versions.
- RCPs cap resource-side permissions for supported services; they do not apply to service-linked roles or the management account. Validate with `--policy-type RESOURCE_CONTROL_POLICY` on a recent CLI. Check the AWS docs for the current supported service list.

## Public S3
- Allow with `Principal: "*"` and no restricting condition: Critical.
- Acceptable restrictions: `aws:PrincipalOrgID`, `aws:SourceVpce`/`aws:SourceVpc`, `aws:SourceArn` with `aws:SourceAccount` for services, `aws:PrincipalArn`. Wide `aws:SourceIp` is not a restriction.
- Check Block Public Access at account and bucket level (all four settings: BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets):
  - `aws s3control get-public-access-block --account-id <id>`
  - `aws s3api get-public-access-block --bucket <bucket>`
- ListBucket uses the bucket ARN with `s3:prefix`; object actions use `arn:aws:s3:::bucket/*`. Bucket policy limit 20 KB.
- Recommend a Deny on `aws:SecureTransport` false.

## KMS key policies
- Without the account root statement ('Enable IAM User Permissions'), IAM policies do not grant access to the key.
- `Principal: "*"` needs `kms:CallerAccount` and `kms:ViaService`, otherwise it is public.
- Cross-account use needs both the key policy and the external account's IAM policy to allow.
- Use `kms:ViaService`, `kms:EncryptionContext:*`, `kms:GrantIsForAWSResource` for `kms:CreateGrant`.
- Separate key administrators (no Decrypt) from users. Avoid `kms:*` on `*` in identity policies. Do not use `BypassPolicyLockoutSafetyCheck`. Key policy limit 32 KB.

## Size and structure
- Managed policy 6,144 characters; inline totals: users 2,048, groups 5,120, roles 10,240 (whitespace excluded).
- Managed policies per role/user: 10 default (up to 20). Policy versions: 5.
- `Version` must be `2012-10-17`; `2008-10-17` lacks policy variables. Sids unique per policy.
