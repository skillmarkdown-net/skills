---
type: llm
---

PASS if Flags disallowing /_next/ as blocking render assets, 120,000 URLs exceeding the 50,000 per-file limit so generateSitemaps plus a sitemap index is needed (noting Next does not create the index), lastModified new Date() as untrustworthy, priority/changeFrequency ignored by Google, DB call on every crawl needing revalidate or caching, with code.
FAIL if Misses the 50,000 limit or the /_next/ block, or recommends pinging Google.
