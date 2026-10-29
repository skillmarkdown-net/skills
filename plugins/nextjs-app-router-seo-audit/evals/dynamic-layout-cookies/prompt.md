---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our marketing and blog pages in Next.js 15 are slow with high TTFB and Search Console shows crawl rate dropping. app/layout.tsx does `const theme = (await cookies()).get('theme')?.value` and the blog page has `export const dynamic = 'force-dynamic'`. Can you review whether rendering mode is the problem and how to fix it?
