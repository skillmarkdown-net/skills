# Dockerfile Hardening Audit

Reviews a Dockerfile and image, reports findings by severity, and returns a fixed Dockerfile, .dockerignore and scan commands.

> **Triggers on:** Audits a Dockerfile and the image it builds for security and size problems, then returns findings by severity and a fixed Dockerfile plus .dockerignore. Use when asked to harden, secure, review or slim a Dockerfile, add a non-root USER, pin base images by digest, remove secrets from layers, or scan with Trivy or Docker Scout.

## What it does
Audits a Dockerfile and, when available, its built image. It returns findings grouped by severity (CRITICAL to LOW), a fixed Dockerfile, a `.dockerignore`, and the build and scan commands to verify the result. It covers multi-stage builds, digest-pinned minimal bases, non-root USER, BuildKit secret mounts, COPY over ADD, HEALTHCHECK, layer cache order, image size, and Trivy or Docker Scout scanning.

## When it triggers
- "Harden this Dockerfile"
- "Why is my image 1.2 GB? Slim it down"
- "Is it OK to pass my npm token as a build arg?"
- "Make this container run as non-root and pin the base image"
- "How do I scan this image with Trivy and fail CI on criticals?"

## What is inside
- `SKILL.md`: the workflow, fix rules, output format and gotchas.
- `references/hardening-checklist.md`: the full checklist with Hadolint and Trivy rule IDs.
- `references/severity-model.md`: the severity model so findings are ranked consistently.
- `references/scan-commands.md`: Trivy, Docker Scout, lint and inspection commands with exit-code behaviour.
- `scripts/dockerfile_lint.py`: standard-library static pass that prints findings with line numbers.

## Example output
```
## Summary
1 CRITICAL, 2 HIGH, 2 MEDIUM. Verified with the lint script; no image scan was run.

## Findings
### CRITICAL
- [DS031 | line 5] NPM_TOKEN passed as ARG. Persists in docker history. Fix: secret mount.
```
Followed by the fixed Dockerfile, `.dockerignore` and verify commands.

## Customising it
Edit `references/severity-model.md` to match your policy, add your internal registry rules to the checklist, or extend the patterns in `scripts/dockerfile_lint.py`.

## Limits
The lint script is regex based and advisory. Digests are never invented; they are left as placeholders unless looked up. Rule IDs and base image tags should be confirmed against current Hadolint, Trivy and registry documentation. Scans only run if you ask for them and the tools are installed.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install dockerfile-hardening-audit@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/dockerfile-hardening-audit/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/dockerfile-hardening-audit/` | `.claude/skills/dockerfile-hardening-audit/` |
| OpenAI Codex | `~/.agents/skills/dockerfile-hardening-audit/` | `.agents/skills/dockerfile-hardening-audit/` |
| Cursor | `~/.cursor/skills/dockerfile-hardening-audit/` | `.cursor/skills/dockerfile-hardening-audit/` |
| Gemini CLI | `~/.gemini/skills/dockerfile-hardening-audit/` | `.gemini/skills/dockerfile-hardening-audit/` |
| Other Agent Skills apps | `~/.agents/skills/dockerfile-hardening-audit/` | `.agents/skills/dockerfile-hardening-audit/` |

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
