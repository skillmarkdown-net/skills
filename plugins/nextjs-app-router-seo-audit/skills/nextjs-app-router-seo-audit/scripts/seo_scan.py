#!/usr/bin/env python3
"""Inventory SEO-relevant patterns in a Next.js App Router project.

Usage:
    python3 seo_scan.py <project-root>

Prints JSON: next version, config files found, and file:line hits per category.
Read-only, standard library only, no network. Hits are leads to inspect, not verdicts.
"""
import json
import os
import re
import sys

SKIP = {"node_modules", ".next", ".git", "dist", "build", "out"}
EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs")
PATTERNS = {
    "generateMetadata": r"generateMetadata",
    "static_metadata": r"export\s+const\s+metadata",
    "metadataBase": r"metadataBase",
    "alternates": r"alternates\s*:",
    "canonical": r"canonical\s*:",
    "noindex": r"index\s*:\s*false|noindex",
    "dynamic_config": r"export\s+const\s+dynamic\b",
    "revalidate_config": r"export\s+const\s+revalidate\b",
    "dynamic_apis": r"\b(cookies|headers|draftMode|connection)\s*\(",
    "searchParams": r"searchParams",
    "jsonld_inject": r"dangerouslySetInnerHTML",
    "jsonld_script": r"application/ld\+json",
    "raw_img": r"<img[\s>]",
    "image_priority": r"\b(priority|preload)\b",
    "next_image_import": r"from\s+['\"]next/image['\"]",
    "matcher": r"matcher\s*:",
    "generateStaticParams": r"generateStaticParams",
    "og_from_server": r"ImageResponse.*next/server",
    "use_client": r"^['\"]use client['\"]",
}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    root = sys.argv[1]
    out = {"next_version": None, "config_files": [], "hits": {k: [] for k in PATTERNS}}
    pkg = os.path.join(root, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg, encoding="utf-8") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            out["next_version"] = deps.get("next")
        except (OSError, ValueError):
            pass
    compiled = {k: re.compile(v, re.M) for k, v in PATTERNS.items()}
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if re.match(r"(next\.config\.|middleware\.|proxy\.)", name) and dirpath == root or name in ("middleware.ts", "proxy.ts", "robots.ts", "sitemap.ts"):
                out["config_files"].append(rel)
            if not name.endswith(EXT):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    lines = f.read().splitlines()
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(lines, 1):
                for key, rx in compiled.items():
                    if rx.search(line):
                        if len(out["hits"][key]) < 100:
                            out["hits"][key].append(f"{rel}:{i}: {line.strip()[:120]}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
