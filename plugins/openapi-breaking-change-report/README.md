# OpenAPI Breaking Change Report

Diff two OpenAPI 3.x specs, classify each change as breaking, risky or safe, suggest a semver bump and write migration notes.

> **Triggers on:** Compares two versions of an OpenAPI 3.x spec and reports breaking, risky and safe changes for API consumers, with a semver bump suggestion and migration notes. Use when asked to diff OpenAPI or Swagger specs, check for breaking changes, review an API PR, compare openapi.yaml files, or run oasdiff.

## What it does

Compares two versions of an OpenAPI 3.x spec and tells API consumers what will break. Every change is classified as breaking, risky or safe with the direction (request or response) taken into account. It then suggests a semver bump for `info.version` and writes migration notes with locations, before/after values and required actions.

## When it triggers

- "Diff these two openapi.yaml files and tell me if anything breaks"
- "Is this API PR a breaking change? What version should we release?"
- "Run oasdiff between main and my branch and summarise it"
- "Write migration notes for the v2 API changes"

## What is inside

- `SKILL.md`: the workflow (validate, normalise, classify, detect renames, semver, migration).
- `references/classification-rules.md`: tables of breaking/risky/safe rules by direction, plus 3.0 vs 3.1 normalisation.
- `references/semver-and-migration.md`: bump algorithm, migration note template, deprecation headers.
- `scripts/openapi_diff.py`: standard-library fallback diff for when `oasdiff` is not installed (PyYAML needed for YAML).

## Example output

```
Base 2.3.1 -> revision 2.4.0 | 3 breaking, 2 risky, 4 safe | Suggested: MAJOR (3.0.0)
BREAKING paths./users/{id}.get.parameters: new required query param `tenant`
RISKY components.schemas.Status: response enum added `paused`
```

## Customising it

- Edit the risky-to-bump policy in `references/semver-and-migration.md` (for example, treat risky as MAJOR).
- Add your own rules (internal `x-` extensions, sunset conventions) to `references/classification-rules.md`.
- Extend `scripts/openapi_diff.py` for checks you care about.

## Limits

- Flag spellings and rule IDs of `oasdiff` were not verified; the skill tells the agent to read `--help` first.
- The fallback script does not resolve external `$ref`s, `oneOf`/`anyOf` variants or 3.2-only features, and covers a subset of the rules.
- Rename detection is heuristic.
- Whether a change breaks you depends on your consumers; strict clients may turn risky into breaking.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install openapi-breaking-change-report@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/openapi-breaking-change-report/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/openapi-breaking-change-report/` | `.claude/skills/openapi-breaking-change-report/` |
| OpenAI Codex | `~/.agents/skills/openapi-breaking-change-report/` | `.agents/skills/openapi-breaking-change-report/` |
| Cursor | `~/.cursor/skills/openapi-breaking-change-report/` | `.cursor/skills/openapi-breaking-change-report/` |
| Gemini CLI | `~/.gemini/skills/openapi-breaking-change-report/` | `.gemini/skills/openapi-breaking-change-report/` |
| Other Agent Skills apps | `~/.agents/skills/openapi-breaking-change-report/` | `.agents/skills/openapi-breaking-change-report/` |

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
