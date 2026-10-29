---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

We use app/[lang]/ routing with locales en, de, fr. In app/[lang]/about/page.tsx we have:

export async function generateMetadata({ params }) {
  const { lang } = await params
  return { alternates: { canonical: '/en/about', languages: { 'en': '/en/about', 'de': '/de/about', 'en-UK': '/en-uk/about' } } }
}

Also our middleware redirects any request by Accept-Language, matcher is '/((?!_next).*)'. Check hreflang.
