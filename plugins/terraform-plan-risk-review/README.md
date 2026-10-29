# Terraform Plan Risk Review

Scans a Terraform plan JSON for destroys, public S3, open security groups and IAM wildcards, and prints a risk table with a go/no-go verdict.

> **Triggers on:** Reviews a saved Terraform or OpenTofu plan (tfplan, tfplan.json) before apply: flags destroyed or replaced resources, public S3 buckets, security groups open to 0.0.0.0/0 or ::/0 and IAM wildcards, then prints a risk table and a GO / NO-GO verdict. Use when asked to review, vet, audit or sanity-check a terraform plan, plan JSON or terraform show -json output before apply.

## What it does

Reviews a saved Terraform or OpenTofu plan before you apply it. It flags destroyed and replaced resources, public S3 buckets, security groups open to the world (IPv4 and IPv6) and IAM wildcards, then prints a risk table and a GO / GO WITH REVIEW / NO-GO verdict. It reads only the plan JSON and never runs apply.

## When it triggers

- "Review this terraform plan before I apply it"
- "Is tfplan.json safe to apply?"
- "Check terraform show -json output for open security groups"
- "Anything dangerous in this plan? Any resources being replaced?"

## What is inside

- `SKILL.md`: the review procedure, verdict rules, output format and gotchas.
- `references/risk-rules.md`: severity tables for destroys, S3, security groups and IAM.
- `scripts/plan_review.py`: standard-library scanner that prints the table and verdict and sets an exit code.

## Example output

```
Plan: terraform 1.9.8, format 1.2 | create 3, update 1, destroy 1, replace 1, forget 0

| Severity | Address | Action | Finding | Reason |
| CRITICAL | aws_vpc_security_group_ingress_rule.ssh | create | Sensitive/all ports open to world | cidr_ipv4 |
| HIGH | module.db.aws_db_instance.main | replace | Stateful resource replaced | replace_because_cannot_update |

VERDICT: NO-GO
```

## Customising it

Edit the stateful type list and sensitive ports in `scripts/plan_review.py` and `references/risk-rules.md`. Add your own resource types (for example Azure or GCP) as new rule families, and adjust severities to your policy.

## Limits

- Rules target the AWS provider; other providers get only destroy/replace checks.
- Values unknown at plan time cannot be checked and force NO-GO.
- Whether a bucket lacks a public access block is only visible with configuration or prior state.
- Pattern checks complement, not replace, Checkov, Trivy or OPA policy. Rules were written from provider documentation knowledge and not verified against the latest provider release.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install terraform-plan-risk-review@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/terraform-plan-risk-review/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/terraform-plan-risk-review/` | `.claude/skills/terraform-plan-risk-review/` |
| OpenAI Codex | `~/.agents/skills/terraform-plan-risk-review/` | `.agents/skills/terraform-plan-risk-review/` |
| Cursor | `~/.cursor/skills/terraform-plan-risk-review/` | `.cursor/skills/terraform-plan-risk-review/` |
| Gemini CLI | `~/.gemini/skills/terraform-plan-risk-review/` | `.gemini/skills/terraform-plan-risk-review/` |
| Other Agent Skills apps | `~/.agents/skills/terraform-plan-risk-review/` | `.agents/skills/terraform-plan-risk-review/` |

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
