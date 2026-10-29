# IAM Least Privilege Review

Audit AWS IAM policies for least privilege, rank findings by severity, and return a tightened policy plus Access Analyzer validation steps.

> **Triggers on:** Reviews AWS IAM identity, resource, trust and permission boundary policies for least privilege and reports severity-ranked findings with a tightened policy JSON and IAM Access Analyzer validation commands. Use when asked to audit, review or tighten an IAM policy, check iam:PassRole, wildcards, NotAction, trust policy, cross-account, public S3 bucket policy or KMS key policy.

## What it does

Reviews AWS IAM policies for least privilege: identity policies, resource policies, role trust policies, permission boundaries and SCP/RCP documents. It returns findings ranked Critical to Low, a tightened policy JSON, a list of assumptions, and the IAM Access Analyzer commands to validate the result.

## When it triggers

- "Review this IAM policy, it feels too broad."
- "Is this role trust policy safe for a third-party vendor?"
- "Check this S3 bucket policy for public access."
- "Can anyone escalate privileges with iam:PassRole here?"
- "Tighten this KMS key policy and show me how to validate it with Access Analyzer."

## What is inside

- `SKILL.md`: workflow, severity rubric, output format, gotchas.
- `references/review-checklist.md`: wildcards, Not* elements, trust, conditions, S3, KMS, limits.
- `references/privilege-escalation.md`: escalation primitives and PassRole combinations.
- `references/access-analyzer-validation.md`: validate-policy, custom checks and analyzer commands.
- `scripts/iam_policy_scan.py`: standard-library pattern pre-scan for policy JSON files.

## Example output

```
### [HIGH] PassRole allowed on any role (Sid: Deploy)
- Issue: iam:PassRole on * lets the holder pass an admin role to Lambda or EC2.
- Fix: limit Resource to arn:aws:iam::111122223333:role/app/* and add iam:PassedToService.
```

Followed by a tightened policy block and `aws accessanalyzer validate-policy` and `check-no-new-access` commands.

## Customising it

- Add your organisation's approved account IDs and org ID to the checklist so external trust is judged against an allowlist.
- Edit the severity rubric in `SKILL.md` to match your risk appetite.
- Add your boundary policy ARN to `references/privilege-escalation.md`.

## Limits

- The script finds patterns only; context judgement is the agent's.
- Several limits and condition-key details come from memory-based notes and should be re-verified in AWS docs.
- Validation passing does not prove least privilege. Tightened identity policies should be tested against last-accessed data or CloudTrail before rollout.
- Check the CLI version: older builds lack the RESOURCE_CONTROL_POLICY policy type.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install iam-least-privilege-review@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/iam-least-privilege-review/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/iam-least-privilege-review/` | `.claude/skills/iam-least-privilege-review/` |
| OpenAI Codex | `~/.agents/skills/iam-least-privilege-review/` | `.agents/skills/iam-least-privilege-review/` |
| Cursor | `~/.cursor/skills/iam-least-privilege-review/` | `.cursor/skills/iam-least-privilege-review/` |
| Gemini CLI | `~/.gemini/skills/iam-least-privilege-review/` | `.gemini/skills/iam-least-privilege-review/` |
| Other Agent Skills apps | `~/.agents/skills/iam-least-privilege-review/` | `.agents/skills/iam-least-privilege-review/` |

Start a new session and ask for the task in your own words; the app loads the skill when your request matches its description.

## Test it

The `evals/` folder holds 8 test cases (5 that should trigger the skill, 3 that should not). With Claude Code installed:

```
claude plugin eval .
```

## License

MIT. See `LICENSE`.

---
Built with [SkillMarkdown](https://skillmarkdown.net).
