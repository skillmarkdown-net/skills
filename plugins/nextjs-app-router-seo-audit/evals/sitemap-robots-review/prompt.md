---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review my SEO files for a Next.js App Router site.

app/robots.ts:
export default function robots() { return { rules: { userAgent: '*', allow: '/', disallow: ['/_next/', '/api/'] }, sitemap: 'https://shop.example.com/sitemap.xml' } }

app/sitemap.ts:
export default async function sitemap() {
  const products = await db.product.findMany()
  return products.map(p => ({ url: `https://shop.example.com/p/${p.slug}`, lastModified: new Date(), changeFrequency: 'daily', priority: 1 }))
}

We have about 120,000 products.
