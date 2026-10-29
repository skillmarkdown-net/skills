# Next.js App Router SEO checklist

Compiled from prior knowledge, not verified live. Items tagged (verify) must be confirmed against the docs for the installed version.

## Version table

| Topic | Next 14 | Next 15 | Next 16 |
|---|---|---|---|
| `params` / `searchParams` | sync | Promise (sync access temporarily allowed) | Promise only (verify) |
| fetch / GET handler cache default | cached | not cached | not cached |
| Middleware file | middleware.ts | middleware.ts | proxy.ts, export `proxy` (verify) |
| `next/image` LCP prop | priority | priority | `preload`, priority deprecated (verify) |
| `images.minimumCacheTTL` | 60 s | 60 s | 14400 s (verify) |
| Cache Components | no | no | `cacheComponents: true`, `use cache`, `cacheLife`, `cacheTag` |
| Streaming metadata | no | from 15.2 | yes |

## A. Metadata
- `metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL)` in root layout.
- `title: { default, template: '%s | Brand' }` in root; `absolute` to bypass.
- Unique title and description per indexable route.
- Metadata merge is shallow per key (`openGraph`, `alternates`, `twitter`). Extend using `(await parent).openGraph?.images`.
- `generateMetadata` and `metadata` are mutually exclusive per segment; Server Components only.
- Wrap DB calls in React `cache()`; identical `fetch` calls are memoised.
- `viewport` / `themeColor` in `export const viewport`.
- Missing entity: `notFound()`.

## B. Canonical and indexing
- Absolute URL, self-referencing on each indexable page.
- Match `trailingSlash`, www/apex, https. Next redirects `/path/` to `/path` (308) by default.
- Never canonical to noindexed, redirected or 404 URLs.
- Faceted or sorted URLs: canonical to clean URL or noindex.
- Canonical must be in initial HTML.
- Preview deployments: noindex via env-gated robots or `X-Robots-Tag`.

## C. robots and sitemap
- `app/robots.ts` returns `MetadataRoute.Robots`; served at `/robots.txt`. Limit 500 KiB (verify).
- Do not block `/_next/` or static assets.
- `app/sitemap.ts` returns `MetadataRoute.Sitemap` (`url`, `lastModified`, `alternates.languages`, `images`, `videos`).
- 50,000 URLs / 50 MB per file; `generateSitemaps()` gives `/sitemap/0.xml`; build index yourself. `id` may be a Promise in newer versions (verify).
- Accurate `lastModified` only.
- Proxy/middleware matcher excludes `sitemap.xml`, `robots.txt`, `_next`, `favicon.ico`, images.

## D. OG images
- `opengraph-image.tsx` exports `alt`, `size = { width: 1200, height: 630 }`, `contentType = 'image/png'`, default function returning `ImageResponse` from `next/og`.
- Satori: flexbox only, no grid, manual fonts, 500 KB bundle.
- Multiple images per segment: `generateImageMetadata`.

## E. JSON-LD
```tsx
const jsonLd = { '@context': 'https://schema.org', '@type': 'Article', headline: post.title }
<script type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
```
- Server-rendered, content matches page, `@id`/`@graph` to connect entities.
- FAQ limited to authoritative government/health sites; HowTo deprecated. Several lesser-used features were phased out in 2025: check Google's gallery (verify).

## F. Rendering and images
- Dynamic triggers: `cookies()`, `headers()`, `searchParams`, `connection()`, `draftMode()`, `no-store` fetch, `dynamic = 'force-dynamic'`.
- Segment config: `dynamic`, `revalidate` (literal), `dynamicParams`, `generateStaticParams`.
- ISR: time-based `revalidate`, on-demand `revalidatePath` / `revalidateTag`. `x-nextjs-cache`: HIT, MISS, STALE (self-hosted).
- CWV (p75): LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1.
- `next/image`: `alt`, dimensions or `fill` + `sizes`, `priority`/`preload` on LCP, `remotePatterns`, `formats` default webp (add avif if desired).
- `next/font`, `next/script`, `@next/third-parties`, `next/dynamic`, `useReportWebVitals`.

## G. Live verification commands
```
curl -sL https://SITE/path | grep -Ei '<title|rel="canonical"|hreflang|name="robots"|og:|application/ld\+json'
curl -sI https://SITE/path
curl -sL -A "Googlebot" https://SITE/path | grep -Ei '<title|rel="canonical"|name="robots"'
curl -s https://SITE/robots.txt
curl -s https://SITE/sitemap.xml
```
Check status, `x-robots-tag`, `cache-control`, `x-nextjs-cache`.

## H. hreflang
- Self + all alternates, reciprocal, absolute URLs, `x-default`.
- ISO 639-1 language, optional ISO 3166-1 alpha-2 region (`en-GB`).
- One method (HTML, header, or sitemap) consistently.
- Each locale canonicalises to itself.
- `<html lang>` from route param; `generateStaticParams` for locales.
- No Accept-Language/IP redirects on localised URLs.

## Sources (pointers, not confirmed)
nextjs.org/docs/app/api-reference/functions/generate-metadata; nextjs.org/docs/app/guides/json-ld; nextjs.org/docs/app/guides/internationalization; developers.google.com/search/docs/specialty/international/localized-versions; developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap; web.dev/articles/vitals.
