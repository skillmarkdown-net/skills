# Validating with IAM Access Analyzer

Run `aws --version` first. Older v2 builds (for example 2.9 and 2.18) list only IDENTITY_POLICY, RESOURCE_POLICY and SERVICE_CONTROL_POLICY for `--policy-type`; RESOURCE_CONTROL_POLICY needs a newer CLI. Confirm enum values with `aws accessanalyzer <command> help`. Custom checks need `access-analyzer:Check*` permissions and are billed per API call; check the pricing page. They need no analyzer.

## 1. Basic checks: validate-policy
```
aws accessanalyzer validate-policy \
  --policy-document file://tightened.json \
  --policy-type IDENTITY_POLICY
```
- `--policy-type`: `IDENTITY_POLICY`, `RESOURCE_POLICY`, `SERVICE_CONTROL_POLICY`, `RESOURCE_CONTROL_POLICY`.
- Role trust policies and S3 bucket policies are resource policies: use `--policy-type RESOURCE_POLICY`.
- `--validate-policy-resource-type` applies only with RESOURCE_POLICY; list valid values in the command help.
- Optional: `--locale EN` (also DE, ES, FR, IT, JA, KO, PT_BR, ZH_CN, ZH_TW).
- Findings have `findingType` (ERROR, SECURITY_WARNING, WARNING, SUGGESTION), `issueCode`, `findingDetails`, `learnMoreLink`, `locations`. Goal: no ERROR or SECURITY_WARNING.

## 2. Custom checks (prove specific properties)
No regression versus the original:
```
aws accessanalyzer check-no-new-access \
  --new-policy-document file://tightened.json \
  --existing-policy-document file://original.json \
  --policy-type IDENTITY_POLICY
```
Expected result `PASS`: the tightened policy grants nothing the original did not.

Must-never-allow actions (verify the `--access` shorthand in `aws accessanalyzer check-access-not-granted help`):
```
aws accessanalyzer check-access-not-granted \
  --policy-document file://tightened.json \
  --policy-type IDENTITY_POLICY \
  --access actions=iam:PassRole,iam:CreatePolicyVersion,s3:PutBucketPolicy
```
Note this fails if the policy still allows PassRole even when scoped; use it for policies that should have no PassRole at all.

Not public (resource policies):
```
aws accessanalyzer check-no-public-access \
  --policy-document file://bucket-policy.json \
  --resource-type AWS::S3::Bucket
```
Resource types are CloudFormation-style names such as `AWS::S3::Bucket`, `AWS::KMS::Key`, `AWS::IAM::AssumeRolePolicyDocument`. The list grows; get it from `aws accessanalyzer check-no-public-access help`.

All three return `result` of `PASS` or `FAIL` plus `message` and `reasons`. For CI gating use `--query result --output text` and fail the build unless it prints `PASS`.

## 3. Analyzers for deployed resources
```
aws accessanalyzer create-analyzer --analyzer-name org-external --type ORGANIZATION
```
Types: ACCOUNT, ORGANIZATION, ACCOUNT_UNUSED_ACCESS, ORGANIZATION_UNUSED_ACCESS. External access analyzers report public and cross-account access (S3, KMS, IAM role trust, Lambda, SQS, SNS, Secrets Manager and more). Unused access analyzers report unused roles, keys and permissions (default window 90 days; verify current defaults and pricing). Use `create-access-preview` to preview a proposed resource policy for supported resource types before deploying.

## 4. Supplements
- `aws iam simulate-custom-policy` / `simulate-principal-policy` test specific action and resource pairs; they ignore SCPs/RCPs and some resource-policy conditions.
- Usage-based tightening: `aws iam generate-service-last-accessed-details` (add `--granularity ACTION_LEVEL`), then `get-service-last-accessed-details`.
- Pipeline validators: awslabs cloudformation-iam-policy-validator and terraform-iam-policy-validator.

## What a pass means
PASS and a clean validate-policy mean grammar is sound and the specific properties asked for hold. They do not prove the policy is least privilege.
