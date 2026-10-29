---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Audit the SEO of my Next.js 15 App Router site. Here is app/layout.tsx:

export const metadata = {
  title: 'Acme',
  description: 'Acme store',
  alternates: { canonical: '/' },
  robots: { index: false, follow: false },
}

export default function RootLayout({ children }) { return <html><body>{children}</body></html> }

And app/blog/[slug]/page.tsx has export async function generateMetadata({ params }) { const { slug } = await params; return { title: slug } }
