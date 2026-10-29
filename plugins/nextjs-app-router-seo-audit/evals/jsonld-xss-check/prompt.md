---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Please check the structured data in my Next.js App Router product page:

<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({ '@context': 'https://schema.org', '@type': 'Product', name: product.name, description: product.userReview }) }} />

It is inside a 'use client' component. Also I want to add FAQ rich results to the page.
