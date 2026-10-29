---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit this terraform show -json excerpt for IAM problems: aws_iam_policy.admin will be created with policy "{\"Version\":\"2012-10-17\",\"Statement\":{\"Effect\":\"Allow\",\"Action\":\"*\",\"Resource\":\"*\"}}" and aws_iam_role_policy.app will be created with after_unknown {"policy":true}. Also aws_iam_policy.guard has a Deny with Action "*".
