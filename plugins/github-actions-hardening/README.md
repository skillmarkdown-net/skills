# GitHub Actions Hardening Audit

Audit GitHub Actions workflows for supply-chain, injection and privilege issues and get a findings table with YAML diff fixes.

> **Triggers on:** Audits GitHub Actions workflow files and reports a severity-ranked findings table with YAML diff fixes: unpinned actions, broad permissions, pull_request_target and workflow_run misuse, script injection, secrets, self-hosted runners, missing timeouts. Use when reviewing .github/workflows/*.yml, hardening CI, pinning actions to SHAs, or checking a pwn request.

## What it does

Audits GitHub Actions workflow files and returns a severity-ranked findings table with a minimal YAML diff for every fix. It covers SHA pinning, least-privilege permissions, `pull_request_target` and `workflow_run` misuse, script injection, secret exposure, self-hosted runner risks, and missing timeouts and concurrency.

## When it triggers

- "Review my .github/workflows for security problems"
- "Pin all third-party actions to commit SHAs"
- "Is this pull_request_target workflow safe?"
- "Harden our CI permissions"
- "Can `${{ github.event.issue.title }}` be injected here?"

## What is inside

- `SKILL.md`: audit procedure, severity rules, output format, gotchas.
- `references/checks.md`: untrusted contexts, trigger trust table, permission grants, pinning and runner notes.
- `scripts/scan_workflows.py`: standard-library pattern scanner for a fast first pass.

## Example output

```
Verdict: 1 critical, 1 high, 1 medium, 1 low
| # | Sev | File:line | Finding | Fix |
| 1 | Critical | pr.yml:12 | pull_request_target checks out PR head | use pull_request |
```

Followed by a diff per finding and a Verify list.

## Customising it

Edit the severity mapping in `SKILL.md` to match your risk policy, add your internal reusable workflows to the trusted list, and adjust suggested timeouts in `references/checks.md`.

## Limits

The scanner is regex-based and cannot trace taint across steps. SHAs are never invented; without network access the skill gives a placeholder and the `git ls-remote` command. Several details (full permission scope list, default 360-minute timeout, settings checkbox names, the November 2026 default event policy date) were not verified against primary docs and are reported in a Verify list.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install github-actions-hardening@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/github-actions-hardening/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/github-actions-hardening/` | `.claude/skills/github-actions-hardening/` |
| OpenAI Codex | `~/.agents/skills/github-actions-hardening/` | `.agents/skills/github-actions-hardening/` |
| Cursor | `~/.cursor/skills/github-actions-hardening/` | `.cursor/skills/github-actions-hardening/` |
| Gemini CLI | `~/.gemini/skills/github-actions-hardening/` | `.gemini/skills/github-actions-hardening/` |
| Other Agent Skills apps | `~/.agents/skills/github-actions-hardening/` | `.agents/skills/github-actions-hardening/` |

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
