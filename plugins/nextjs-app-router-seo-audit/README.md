# Next.js SEO Audit

Prioritised SEO audit for Next.js App Router apps covering metadata, canonicals, sitemaps, JSON-LD, rendering, images and hreflang, with code fixes.

> **Triggers on:** Audits SEO of a Next.js App Router project: metadata and generateMetadata, canonicals, hreflang, robots and sitemap routes, OG images, JSON-LD, rendering mode per route and next/image Core Web Vitals, then outputs prioritised fixes with code. Use when asked to audit, review or fix SEO in a Next.js app, layout.tsx, sitemap.ts, robots.ts, or indexing problems.

## What it does

Runs a structured SEO audit of a Next.js App Router project and returns prioritised findings (P0 to P3) with evidence and paste-ready code fixes. It covers metadata, canonicals, robots and sitemap routes, Open Graph images, JSON-LD, rendering mode per route, next/image with Core Web Vitals, and hreflang for i18n.

## When it triggers

- "Audit the SEO of my Next.js app"
- "Why is Google indexing the wrong canonical on my blog pages?"
- "Review my sitemap.ts and robots.ts"
- "Our product pages are slow and dynamic, is that hurting crawling?"
- "Check my hreflang setup with next-intl"

## What is inside

- `SKILL.md`: the audit procedure, priority rubric, output format and gotchas.
- `references/nextjs-seo-checklist.md`: version table, per-area checklists, curl verification commands.
- `scripts/seo_scan.py`: read-only inventory scanner (standard library, no network).

## Example output

```
## Summary
Next 15.3, App Router. 14 routes reviewed. P0: 1, P1: 2, P2: 1.

## P0
### F1. Whole site canonicalised to homepage
Evidence: app/layout.tsx:9 alternates: { canonical: '/' }
Fix: compute canonical per page in generateMetadata
```

## Customising it

Edit the priority rubric in `SKILL.md` to match your risk appetite, and add your own route conventions or CMS notes to the checklist. Add your production URL to the prompt so it can run the curl checks.

## Limits

The research behind the version-specific advice (Next 16 changes, `htmlLimitedBots`, Cache Components behaviour, Google's structured-data deprecations) was not verified live; the skill marks these as items to verify. It does not measure field Core Web Vitals; provide CrUX or Search Console data for that. It reports and proposes patches but does not edit files unless asked.

## Install

### Claude Code (as a plugin)

In Claude Code:

```
/plugin marketplace add skillmarkdown-net/skills
/plugin install nextjs-app-router-seo-audit@skillmarkdown
```

### Any app that reads Agent Skills

Copy `skills/nextjs-app-router-seo-audit/` into your app's skills folder:

| App | Personal | Project |
|---|---|---|
| Claude Code | `~/.claude/skills/nextjs-app-router-seo-audit/` | `.claude/skills/nextjs-app-router-seo-audit/` |
| OpenAI Codex | `~/.agents/skills/nextjs-app-router-seo-audit/` | `.agents/skills/nextjs-app-router-seo-audit/` |
| Cursor | `~/.cursor/skills/nextjs-app-router-seo-audit/` | `.cursor/skills/nextjs-app-router-seo-audit/` |
| Gemini CLI | `~/.gemini/skills/nextjs-app-router-seo-audit/` | `.gemini/skills/nextjs-app-router-seo-audit/` |
| Other Agent Skills apps | `~/.agents/skills/nextjs-app-router-seo-audit/` | `.agents/skills/nextjs-app-router-seo-audit/` |

Start a new session and ask for the task in your own words; the app loads the skill when your request matches its description.

## Test it

The `evals/` folder holds 8 test cases (6 that should trigger the skill, 2 that should not). With Claude Code installed:

```
claude plugin eval .
```

## License

MIT. See `LICENSE`.

---
Built with [SkillMarkdown](https://skillmarkdown.net).
