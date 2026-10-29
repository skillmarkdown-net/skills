# LLM App Security Review

Audits chatbot, RAG and agent code against OWASP LLM Top 10 2025 and reports ranked risks with fixes and canary test prompts.

> **Triggers on:** Reviews LLM applications (chatbots, RAG pipelines, tool-using agents) against the OWASP Top 10 for LLM Applications 2025 and reports risks by severity with code evidence, mitigations and test prompts. Use when asked to audit, threat-model or pen-test an LLM app, or to check for prompt injection, system prompt leakage, excessive agency, insecure output handling or unbounded consumption.

## What it does
Reviews a chatbot, RAG pipeline or tool-using agent against the OWASP Top 10 for LLM Applications 2025. It maps untrusted inputs, tools and output sinks, then reports findings ranked Critical to Info, each with file and line evidence, an attack scenario, a code-level mitigation and a non-destructive canary test prompt.

## When it triggers
- "Audit this agent for prompt injection."
- "Threat-model our RAG chatbot before launch."
- "Is it safe to render the model's markdown in our React app?"
- "Check our tool definitions for excessive agency."
- "Could someone run up our OpenAI bill?"

## What is inside
- `SKILL.md`: the review procedure, output format and gotchas.
- `references/owasp-llm-checklists.md`: per-risk checklists using 2025 IDs.
- `references/severity-model.md`: severity levels and the combination rule.
- `scripts/llm_scan.py`: standard-library first-pass scanner for risky sinks, missing limits and secret-like strings.

## Example output
A system summary, a findings table (for example `Critical | LLM01 + LLM06 | Indirect injection can trigger send_email`), then per-finding blocks with evidence, scenario, mitigation and a canary test prompt, and a Not assessed list.

## Customising it
Edit the severity table in `references/severity-model.md` to match your risk appetite. Add regex rules to `RULES` in `scripts/llm_scan.py` for your frameworks and internal tool names.

## Limits
It reviews code and prompts you own; it does not attack live third-party services. Prompt tests are probabilistic, so a pass is never proof of safety. Some checklist items are standard practice not re-verified against OWASP pages; check them before quoting as OWASP text. The scanner is regex-based and produces leads only.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install llm-app-security-review@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/llm-app-security-review/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/llm-app-security-review/` | `.claude/skills/llm-app-security-review/` |
| OpenAI Codex | `~/.agents/skills/llm-app-security-review/` | `.agents/skills/llm-app-security-review/` |
| Cursor | `~/.cursor/skills/llm-app-security-review/` | `.cursor/skills/llm-app-security-review/` |
| Gemini CLI | `~/.gemini/skills/llm-app-security-review/` | `.gemini/skills/llm-app-security-review/` |
| Other Agent Skills apps | `~/.agents/skills/llm-app-security-review/` | `.agents/skills/llm-app-security-review/` |

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
