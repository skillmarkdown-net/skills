---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Please review this IAM policy for least privilege and give me a tightened version:
{"Version":"2012-10-17","Statement":[{"Sid":"Deploy","Effect":"Allow","Action":["iam:PassRole","lambda:CreateFunction","lambda:UpdateFunctionCode","lambda:InvokeFunction"],"Resource":"*"}]}
It's attached to our CI deploy role. Functions run under roles in arn:aws:iam::111122223333:role/app/ .
