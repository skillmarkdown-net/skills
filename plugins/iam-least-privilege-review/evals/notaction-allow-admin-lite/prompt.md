---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our security team says this managed policy is a problem but the dev team says it just blocks IAM. Who is right?
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","NotAction":["iam:*","organizations:*"],"Resource":"*"}]}
