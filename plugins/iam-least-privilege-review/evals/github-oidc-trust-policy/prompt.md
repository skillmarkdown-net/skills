---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit this role trust policy, we use it for GitHub Actions deploys:
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Federated":"arn:aws:iam::111122223333:oidc-provider/token.actions.githubusercontent.com"},"Action":"sts:AssumeRoleWithWebIdentity","Condition":{"StringLike":{"token.actions.githubusercontent.com:sub":"repo:*"}}}]}
