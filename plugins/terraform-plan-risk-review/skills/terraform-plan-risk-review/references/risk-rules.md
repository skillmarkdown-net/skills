# Risk rules

Severity scale: CRITICAL > HIGH > MEDIUM > UNVERIFIED (treated as blocking). Only `mode == "managed"` entries in `resource_changes`, including child modules.

## 1. Destroy / replace

| Condition | Severity |
|---|---|
| delete or replace of a stateful type: `aws_db_instance`, `aws_rds_cluster`, `aws_s3_bucket`, `aws_ebs_volume`, `aws_kms_key`, `aws_dynamodb_table`, `aws_efs_file_system`, `aws_elasticache_*`, `aws_route53_zone`, `aws_instance` with data volumes | HIGH |
| any other delete or replace | MEDIUM |
| `forget` | report only |

Replace order: `["delete","create"]` means destroy first (downtime likely); `["create","delete"]` means create_before_destroy.

Reasons to show: `replace_because_cannot_update`, `replace_because_tainted`, `replace_by_request`, `delete_because_no_resource_config`, `delete_because_wrong_repetition`, `delete_because_count_index`, `delete_because_each_key`, `delete_because_no_module`. Add `replace_paths` for what forced it.

## 2. Public S3 (CRITICAL)

- `aws_s3_bucket_public_access_block`: any of `block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets` is false.
- `aws_s3_bucket_acl`: `acl` in `public-read`, `public-read-write` (CRITICAL); `authenticated-read` (HIGH, any AWS account). Also `access_control_policy` grants to `http://acs.amazonaws.com/groups/global/AllUsers` or `.../AuthenticatedUsers`.
- `aws_s3_bucket_policy`: parse `policy`; Allow with Principal `"*"` or `{"AWS":"*"}` and no Condition (`aws:SourceVpce`, `aws:PrincipalOrgID`, `aws:SourceAccount`) is CRITICAL. With a Condition: MEDIUM, review.
- `aws_s3_account_public_access_block` with any false: HIGH.
- Legacy `acl`/`policy` arguments on `aws_s3_bucket` (old provider code): same checks.
- Missing public access block for a bucket: judge only via `configuration`/`prior_state`; otherwise note it cannot be determined.

## 3. World-open ingress

World CIDRs: `0.0.0.0/0`, `::/0`. Optionally flag the split bypass `0.0.0.0/1` plus `128.0.0.0/1`.

Fields: `aws_security_group.ingress[]` (`cidr_blocks`, `ipv6_cidr_blocks`), `aws_security_group_rule` with `type=ingress` (same lists), `aws_vpc_security_group_ingress_rule` (`cidr_ipv4`, `cidr_ipv6` strings).

| Exposure | Severity |
|---|---|
| protocol `-1` or port range covering 22, 3389, 3306, 5432, 1433, 27017, 6379, 9200 | CRITICAL |
| any other port range open to world, not only 80/443 | HIGH |
| only 80 or 443 | MEDIUM (review; often an intentional load balancer) |

Not world-open: `prefix_list_ids`, `referenced_security_group_id`, `security_groups`, private CIDRs. Ignore egress.

## 4. IAM wildcards

Resources: `aws_iam_policy`, `aws_iam_role_policy`, `aws_iam_user_policy`, `aws_iam_group_policy`, `aws_iam_role` (`assume_role_policy`, `inline_policy`), `aws_iam_role_policy_attachment` / `aws_iam_policy_attachment` / `aws_iam_user_policy_attachment` / `aws_iam_group_policy_attachment` with an `AdministratorAccess` ARN.

Normalise: Statement to list; Action/Resource to lists. Only `Effect: Allow`.

| Pattern | Severity |
|---|---|
| Action `*` or `*:*` | CRITICAL |
| AdministratorAccess attachment | CRITICAL |
| Principal `*` in a trust policy without Condition | CRITICAL |
| `iam:PassRole` with Resource `*` | HIGH |
| service wildcard such as `s3:*`, `iam:*`, `sts:*` | HIGH |
| `NotAction` or `NotResource` with Allow | HIGH |
| Resource `*` with specific actions | MEDIUM |

If the policy field is in `after_unknown` (for example built from `aws_iam_policy_document` with unknown parts), emit UNVERIFIED.

## 5. Verdict

NO-GO: any CRITICAL, HIGH or UNVERIFIED; errored or unparseable plan; unknown `format_version` major.
GO WITH REVIEW: only MEDIUM. GO: none.
