---
type: llm
---

PASS if Flags iam:PassRole on * as High with the Lambda create/invoke escalation path, scopes PassRole to role/app/* with iam:PassedToService lambda.amazonaws.com, scopes lambda actions to function ARNs, gives tightened JSON, and includes validate-policy and check-no-new-access commands.
FAIL if Only says to avoid wildcards, omits PassRole scoping or the PassedToService condition, gives no tightened JSON or no Access Analyzer validation.
