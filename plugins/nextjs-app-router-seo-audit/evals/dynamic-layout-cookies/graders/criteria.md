---
type: llm
---

PASS if Explains that cookies() in a shared layout makes every child route dynamic, that force-dynamic on blog is a P1 finding, proposes moving theme to client-side or CSS and using static/ISR with revalidate and generateStaticParams, mentions verifying with next build markers (○ ● ƒ) and x-nextjs-cache header.
FAIL if Does not link cookies() in the layout to site-wide dynamic rendering, or recommends caching without removing the dynamic API.
