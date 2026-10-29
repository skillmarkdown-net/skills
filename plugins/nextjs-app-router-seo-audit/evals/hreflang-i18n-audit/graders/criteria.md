---
type: llm
---

PASS if Finds canonical hard-coded to /en for all locales (should be self), missing fr and x-default, invalid en-UK (should be en-GB), missing metadataBase for absolute URLs, Accept-Language redirect trapping Googlebot on localised URLs, matcher catching sitemap.xml and robots.txt; provides corrected code.
FAIL if Misses the invalid en-UK code or the redirect trap, or leaves canonical pointing to English.
