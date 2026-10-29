---
name: nextjs-app-router-seo-audit
description: "Audits SEO of a Next.js App Router project: metadata and generateMetadata, canonicals, hreflang, robots and sitemap routes, OG images, JSON-LD, rendering mode per route and next/image Core Web Vitals, then outputs prioritised fixes with code. Use when asked to audit, review or fix SEO in a Next.js app, layout.tsx, sitemap.ts, robots.ts, or indexing problems."
---

# Next.js App Router SEO Audit

Audit a Next.js App Router codebase (and, if a URL is given, its live HTML) for SEO defects. Produce findings ranked P0 to P3, each with evidence and a code fix.

Nothing in the reference notes was verified live. Where a finding depends on a version-specific behaviour marked "verify" in [references/nextjs-seo-checklist.md](references/nextjs-seo-checklist.md), tell the user to confirm it against the docs for their installed version rather than asserting it.

## Steps

1. **Detect the version and setup.** Read `package.json` for `next`, `next-intl`, `schema-dts`. Read `next.config.(js|mjs|ts)` for `trailingSlash`, `images`, `headers`, `htmlLimitedBots`, `cacheComponents`. Check for `middleware.ts` (Next 15) or `proxy.ts` (Next 16). Record the major version; it changes the advice (see the version table in the checklist). Confirm the project uses `app/`, not only `pages/`.

2. **Run the inventory scan.** If shell access exists, run `python3 scripts/seo_scan.py <project-root>`. It greps the codebase for the checklist targets and prints a JSON list of hits per category. If not, grep manually for: `generateMetadata`, `export const metadata`, `metadataBase`, `alternates`, `canonical`, `robots`, `export const dynamic`, `export const revalidate`, `cookies(`, `headers(`, `searchParams`, `dangerouslySetInnerHTML`, `<img`, `priority`, `next/image`, `matcher`. Treat scan output as leads, not proof; open each file.

3. **Metadata audit.** Check against the checklist section A:
   - `metadataBase` set once in the root layout from an env var. Missing means wrong absolute OG/canonical URLs: P0.
   - Every indexable route has a unique `title` and `description`. Root layout uses `title: { default, template }`. Templates do not apply to the same segment's own title.
   - Shallow merge: a page that sets `openGraph` or `alternates` replaces the parent's whole object for that key. Flag pages that lose `images`, `siteName`, `locale`.
   - A segment cannot export both `metadata` and `generateMetadata`. Neither works in `'use client'` files.
   - `viewport`/`themeColor` belong in `export const viewport`, not `metadata`.
   - DB calls in `generateMetadata` duplicating the page query need React `cache()`.
   - Missing entities must call `notFound()`, not return empty metadata.
   - On Next 15+, `params` and `searchParams` are Promises: `const { slug } = await params`.

4. **Canonical and indexing audit.** Flag: hard-coded `canonical: '/'` in a layout (canonicalises the site to the homepage, P0); canonical pointing to a redirected, noindexed or 404 URL; canonical disagreeing with `trailingSlash`, www/apex or http/https; filter/sort `searchParams` pages without a clean canonical or noindex; `robots: { index: false }` left on production layouts (P0); no noindex for preview deployments (use env-gated robots or an `X-Robots-Tag: noindex` header in `next.config` `headers()`). `alternates: { canonical: './' }` in a layout is reported to resolve per page; verify before recommending, safer to compute per page.

5. **robots and sitemap audit.** Read `app/robots.ts|txt` and `app/sitemap.ts|xml`:
   - `Disallow: /` from staging (P0). Disallowing `/_next/` or static assets blocks rendering.
   - robots.txt is not a deindexing tool; a blocked URL cannot show its `noindex`.
   - Sitemap limit 50,000 URLs or 50 MB uncompressed per file. `generateSitemaps()` does not create an index; add `app/sitemap.xml/route.ts` or list children in robots `sitemap`.
   - Google ignores `priority` and `changeFrequency`; `lastModified: new Date()` on every request is a finding. Use real content dates.
   - Sitemap URLs must be absolute, canonical, indexable and 200. Include `alternates.languages` for i18n.
   - A DB-backed sitemap that is dynamic on every crawl is a TTFB risk: use `revalidate` (or `use cache` in 16).
   - Google's sitemap ping endpoint is deprecated; submit via Search Console and the `Sitemap:` line.
   - i18n proxy/middleware `matcher` must exclude `sitemap.xml`, `robots.txt`, `_next`, `favicon.ico` and image files.

6. **Rendering mode per route.** Build a table of every indexable route: static, ISR or dynamic, and why. If you can run it, use `next build` and read the `○` static, `●` SSG, `ƒ` dynamic markers and the revalidate column. Otherwise infer from code. Rules:
   - Public SEO content (marketing, blog, product, category) that is dynamic is a P1. Move to static/ISR (`export const revalidate = N`, `generateStaticParams`) or `use cache` with `cacheLife` under Cache Components.
   - One `cookies()` or `headers()` in a shared layout makes every child dynamic: top regression, P1.
   - Reading `searchParams` in a page makes it dynamic; prefer path segments for indexable variants.
   - `revalidate` must be a literal. Price/stock pages need on-demand `revalidateTag`/`revalidatePath`, not long TTLs.
   - With `cacheComponents: true` on Next 16, `dynamic`, `revalidate`, `fetchCache` are replaced by `use cache`; verify whether the installed version errors or ignores them.
   - Soft-404s: once streaming starts, status is 200. Call `notFound()` before any `<Suspense>` boundary or in `generateMetadata`. Verify current wording in docs.
   - Content fetched only in `useEffect`, or links as `onClick` rather than `next/link`/`<a href>`, are findings.
   - Next 15.2+ streams metadata for non-bot agents; `htmlLimitedBots` controls which agents get blocking `<head>` metadata. Verify whether Googlebot is in the default list before claiming anything.

7. **Open Graph and Twitter images.** Check `opengraph-image.(tsx|png|jpg)` and `twitter-image`. Standard size 1200x630, `alt`, `contentType`. `ImageResponse` comes from `next/og`, not `next/server`. Satori: flexbox only, no `display: grid`, fonts loaded manually, 500 KB bundle limit. A page-level `openGraph.images` overrides the file convention. Tell the user to re-scrape in Facebook Sharing Debugger / LinkedIn Post Inspector after fixes.

8. **Structured data.** Look for `application/ld+json`. Must be server-rendered, use `@context: https://schema.org`, link entities with `@id`/`@graph`, and match visible content. `dangerouslySetInnerHTML` must use `JSON.stringify(data).replace(/</g, '\\u003c')`; unescaped user fields are an XSS finding (P2, P1 if user-generated). FAQ rich results are restricted to authoritative government and health sites and HowTo is deprecated: do not recommend them for ordinary sites. Check the Google search gallery before recommending any type. Validate with Rich Results Test and Schema Markup Validator.

9. **next/image and Core Web Vitals.** Thresholds at the 75th percentile: LCP 2.5 s, INP 200 ms, CLS 0.1 (FID is retired). Flag: raw `<img>`; missing `alt`; no width/height or `fill` parent; `fill` without `sizes`; LCP image without `priority` (Next 15) or `preload` (Next 16; `priority` deprecated); lazy-loaded hero; `images.domains` instead of `remotePatterns`; fonts not via `next/font`; third-party scripts not via `next/script` or `@next/third-parties`; oversized `'use client'` boundaries; heavy widgets without `next/dynamic`. Lighthouse reports TBT, not INP; ask for CrUX or Search Console field data when judging.

10. **i18n and hreflang.** The `i18n` key in `next.config` is Pages Router only. Expect `app/[lang]/` with `generateStaticParams` for locales. Check:
    - `<html lang={lang}>` in the root layout.
    - `alternates.languages` on every localised page, including a self entry and `x-default`, plus self-canonical per locale.
    - Valid codes: `en-GB` not `en-UK`; no region-only codes.
    - Reciprocity, absolute URLs, and alternates that are indexable (not redirected, noindexed or blocked).
    - No hreflang for locales a page lacks.
    - No `Accept-Language`/IP redirects on localised URLs; redirect only at `/`, and provide real-link language switcher.
    - next-intl: `setRequestLocale(locale)` in layouts/pages to keep them static.

11. **Verify live if a URL is available.** Use the commands in [references/nextjs-seo-checklist.md](references/nextjs-seo-checklist.md) section G (curl for title, canonical, hreflang, robots meta, JSON-LD, `x-robots-tag`, `cache-control`, `x-nextjs-cache`, Googlebot UA diff). Only call a finding confirmed if you saw it in the raw HTML or headers.

12. **Prioritise and write the report.** Use the priority rubric below and the output format. Fixes must be code the user can paste, adapted to their file names and Next version.

## Priority rubric

- **P0:** wrong or leftover `noindex`; `Disallow: /`; canonical to wrong URL; soft-404s; missing `metadataBase`; redirect traps for bots.
- **P1:** accidental dynamic rendering of SEO routes; hreflang reciprocity; sitemap errors; missing/duplicate titles and descriptions; LCP image not prioritised.
- **P2:** JSON-LD coverage and XSS escaping; OG images; CLS and INP tuning.
- **P3:** polish (icons, manifest, alt text refinements).

## Output format

Start with a 3-line summary (Next version, routes reviewed, counts per priority). Then a rendering table, then findings grouped by priority. Each finding: ID, title, evidence (file:line or curl output), why it matters, fix code.

```
## Summary
Next 15.3, App Router, next-intl. 14 routes reviewed. P0: 1, P1: 2, P2: 1.

## Rendering
| Route | Mode | Reason | Verdict |
|---|---|---|---|
| /[lang]/blog/[slug] | Dynamic | cookies() in app/[lang]/layout.tsx:12 | Fix (F2) |

## P0
### F1. Whole site canonicalised to homepage
Evidence: app/layout.tsx:9 `alternates: { canonical: '/' }`
Fix:
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }) {
  const { slug } = await params
  return { alternates: { canonical: `/blog/${slug}` } }
}
```

End with "Not verified" listing anything inferred from code only, or version-dependent behaviour the user should check.

## Gotchas

- Do not claim Googlebot behaviour from memory about `htmlLimitedBots`; mark as verify.
- Do not recommend `rel=prev/next`, `priority`/`changefreq` tuning, or sitemap ping.
- A Rich Results Test pass does not guarantee a rich result.
- Canonical is a hint; do not pair it with conflicting `noindex`.
- File conventions (`opengraph-image`, `robots.ts`, `sitemap.ts`) override the `metadata` field for the same property.
- Next 16 renames `middleware.ts` to `proxy.ts`; point fixes at the file that exists.
- Never edit files without being asked; report first, offer patches.
