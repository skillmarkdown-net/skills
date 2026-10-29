#!/usr/bin/env python3
"""First-pass scanner for LLM app security leads.

Usage:
    python scripts/llm_scan.py <path> [--json]

Walks <path> and greps source files for risky sinks, missing-limit hints and
secret-like strings in prompt files. Hits are leads, not findings. Secret
values are masked. Standard library only, no network access.
"""
import json
import os
import re
import sys

EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".html", ".txt", ".md", ".yaml", ".yml", ".json", ".jinja", ".j2"}
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

RULES = [
    ("LLM05", "HTML sink", re.compile(r"innerHTML|dangerouslySetInnerHTML|v-html|\|\s*safe\b")),
    ("LLM05", "Code or shell execution", re.compile(r"\beval\(|\bexec\(|shell\s*=\s*True|os\.system\(")),
    ("LLM05", "String-built SQL", re.compile(r"(execute|query)\(\s*f?[\"'].*(SELECT|INSERT|UPDATE|DELETE).*(\{|%s|\+)", re.I)),
    ("LLM06", "Open-ended tool", re.compile(r"def\s+(run_shell|shell|fetch_url|http_get|execute_command)\b|name\s*[:=]\s*[\"'](shell|bash|fetch_url|run_command)[\"']")),
    ("LLM10", "Unbounded loop hint", re.compile(r"while\s+True\s*:")),
    ("LLM10", "logprobs or logit_bias exposed", re.compile(r"logprobs|logit_bias")),
    ("LLM10", "Model call (check max_tokens nearby)", re.compile(r"chat\.completions\.create|messages\.create|generate_content|\.invoke\(")),
]
SECRET = re.compile(r"(api[_-]?key|secret|password|token|postgres://|mongodb://)\s*[:=]?\s*['\"]?([A-Za-z0-9_\-:/@.]{8,})", re.I)
PROMPT_HINT = re.compile(r"prompt|system|instruction", re.I)


def mask(text):
    return SECRET.sub(lambda m: m.group(1) + "=****", text)


def scan(root):
    hits = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            if os.path.splitext(f)[1].lower() not in EXTS:
                continue
            p = os.path.join(d, f)
            try:
                lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
            except OSError:
                continue
            promptish = bool(PROMPT_HINT.search(f))
            for i, line in enumerate(lines, 1):
                for rid, title, rx in RULES:
                    if rx.search(line):
                        hit = {"id": rid, "title": title, "file": p, "line": i, "text": mask(line.strip())[:140]}
                        if title.startswith("Model call"):
                            window = "\n".join(lines[i - 1:i + 8])
                            if re.search(r"max_tokens|max_output_tokens|max_completion_tokens", window):
                                continue
                            hit["title"] = "Model call without max_tokens in next 8 lines"
                        hits.append(hit)
                if (promptish or PROMPT_HINT.search(line)) and SECRET.search(line):
                    hits.append({"id": "LLM07", "title": "Secret-like string near prompt", "file": p, "line": i, "text": mask(line.strip())[:140]})
    return hits


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    hits = scan(argv[1])
    if "--json" in argv:
        print(json.dumps(hits, indent=2))
    else:
        for h in hits:
            print(f"{h['id']} {h['file']}:{h['line']} {h['title']}: {h['text']}")
        print(f"{len(hits)} lead(s). Confirm each manually.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
