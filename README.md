# SkillMarkdown Skills

Production-quality [Agent Skills](https://skillmarkdown.net/spec) for Claude Code, OpenAI Codex, Cursor, Gemini CLI and every app that reads `SKILL.md`.
Each skill was researched against current documentation, scores 100/100 in the [SkillMarkdown checker](https://skillmarkdown.net/checker) with no security
findings, and ships with references, scripts where useful, and trigger tests you can run with `claude plugin eval`.

## Install in Claude Code

```
/plugin marketplace add skillmarkdown-net/skills
```

Then install the skills you want:

| Skill | What it does | Install |
|---|---|---|
| [Dockerfile Hardening Audit](plugins/dockerfile-hardening-audit) | Reviews a Dockerfile and image, reports findings by severity, and returns a fixed Dockerfile, .dockerignore and scan commands. | `/plugin install dockerfile-hardening-audit@skillmarkdown` |
| [GitHub Actions Hardening Audit](plugins/github-actions-hardening) | Audit GitHub Actions workflows for supply-chain, injection and privilege issues and get a findings table with YAML diff fixes. | `/plugin install github-actions-hardening@skillmarkdown` |
| [IAM Least Privilege Review](plugins/iam-least-privilege-review) | Audit AWS IAM policies for least privilege, rank findings by severity, and return a tightened policy plus Access Analyzer validation steps. | `/plugin install iam-least-privilege-review@skillmarkdown` |
| [Kubernetes Manifest Pre-Apply Review](plugins/k8s-manifest-preapply-review) | Pre-apply review of Kubernetes YAML: security, resources, probes, images, PDB, NetworkPolicy and RBAC, with severity-ranked findings and fixes. | `/plugin install k8s-manifest-preapply-review@skillmarkdown` |
| [LLM App Security Review](plugins/llm-app-security-review) | Audits chatbot, RAG and agent code against OWASP LLM Top 10 2025 and reports ranked risks with fixes and canary test prompts. | `/plugin install llm-app-security-review@skillmarkdown` |
| [Next.js SEO Audit](plugins/nextjs-app-router-seo-audit) | Prioritised SEO audit for Next.js App Router apps covering metadata, canonicals, sitemaps, JSON-LD, rendering, images and hreflang, with code fixes. | `/plugin install nextjs-app-router-seo-audit@skillmarkdown` |
| [OpenAPI Breaking Change Report](plugins/openapi-breaking-change-report) | Diff two OpenAPI 3.x specs, classify each change as breaking, risky or safe, suggest a semver bump and write migration notes. | `/plugin install openapi-breaking-change-report@skillmarkdown` |
| [Postgres Slow Query Diagnosis](plugins/postgres-slow-query-diagnosis) | Reads PostgreSQL EXPLAIN ANALYZE plans, finds the real cause of slowness, and proposes indexes, rewrites and a safe way to verify them. | `/plugin install postgres-slow-query-diagnosis@skillmarkdown` |
| [Stripe Webhook Reviewer](plugins/stripe-webhook-reviewer) | Audits a Stripe webhook handler and returns ranked risks with concrete code fixes and Stripe CLI test steps. | `/plugin install stripe-webhook-reviewer@skillmarkdown` |
| [Terraform Plan Risk Review](plugins/terraform-plan-risk-review) | Scans a Terraform plan JSON for destroys, public S3, open security groups and IAM wildcards, and prints a risk table with a go/no-go verdict. | `/plugin install terraform-plan-risk-review@skillmarkdown` |

## Install with the open skills CLI

Works for Claude Code, Codex, Cursor and the other agents the CLI supports:

```
npx skills add skillmarkdown-net/skills --skill <name>
```

## Use in other apps

Each plugin folder contains `skills/<name>/`. Copy that folder into your app's skills directory (for example `.agents/skills/`, `.cursor/skills/`,
`.gemini/skills/` or `~/.claude/skills/`). See each skill's README for the exact paths.

## Test a skill

```
cd plugins/<name>
claude plugin eval .
```

Every plugin has an `evals/` folder with requests that should trigger the skill and near-misses that should not.

## Make your own

These were built with the [SkillMarkdown](https://skillmarkdown.net) Pro package builder. Describe a workflow and get a researched, tested,
GitHub-ready skill package. The [checker](https://skillmarkdown.net/checker) and [converter](https://skillmarkdown.net/converter) are free.

## License

MIT. See [LICENSE](LICENSE). Updated 2026-10-29.
