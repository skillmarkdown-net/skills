#!/usr/bin/env python3
"""Quick pattern scan of GitHub Actions workflows.

Usage:
    python3 scripts/scan_workflows.py [DIR_OR_FILE ...]

Defaults to .github/workflows. Prints one line per finding:
    SEVERITY file:line rule message
Exit code 1 if any Critical or High finding exists, else 0.
Pattern-based only (no YAML parsing); read the files to confirm each hit.
Standard library only, no network access.
"""
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)")
UNTRUSTED = re.compile(
    r"\$\{\{\s*(github\.event\.(issue\.(title|body)|pull_request\.(title|body|head\.ref|head\.label|head\.repo\.default_branch)"
    r"|comment\.body|review\.body|review_comment\.body|pages\.[^ ]*page_name|commits\.[^ ]*(message|email|name)"
    r"|head_commit\.(message|author\.(email|name))|workflow_run\.(head_branch|head_commit\.message))|github\.head_ref)"
)
PRT_REF = re.compile(r"(head\.sha|head\.ref|refs/pull/|head\.repo)")


def scan(path):
    out = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    text = "\n".join(lines)
    privileged = bool(re.search(r"\b(pull_request_target|workflow_run|issue_comment)\b", text))
    has_perm = re.search(r"^permissions:", text, re.M) is not None
    if not has_perm:
        out.append(("Medium", 1, "no-permissions", "no top-level permissions block"))
    if "timeout-minutes" not in text:
        out.append(("Low", 1, "no-timeout", "no timeout-minutes (default 360)"))
    if "concurrency:" not in text:
        out.append(("Low", 1, "no-concurrency", "no concurrency block"))
    in_run = False
    run_indent = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        m = USES.match(line)
        if m:
            ref = m.group(1)
            if not ref.startswith("./"):
                if ref.startswith("docker://"):
                    if "@sha256:" not in ref:
                        out.append(("High" if privileged else "Medium", i, "unpinned-docker", ref))
                else:
                    ver = ref.split("@", 1)[1] if "@" in ref else ""
                    if not SHA.match(ver):
                        out.append(("High" if privileged else "Medium", i, "unpinned-uses", ref))
        if "allow-unsafe-pr-checkout" in line and "true" in line:
            out.append(("Critical", i, "unsafe-pr-checkout", "allow-unsafe-pr-checkout: true"))
        if privileged and re.match(r"\s*(ref|repository):", line) and PRT_REF.search(line):
            out.append(("Critical", i, "pwn-request", "privileged trigger checks out PR code: " + stripped))
        if re.search(r"permissions:\s*write-all", line):
            out.append(("Medium", i, "write-all", "permissions: write-all"))
        if "secrets: inherit" in line:
            out.append(("Medium", i, "secrets-inherit", "secrets: inherit"))
        if "toJSON(secrets)" in line:
            out.append(("High", i, "dump-secrets", "toJSON(secrets)"))
        if re.search(r"runs-on:.*self-hosted", line) and privileged:
            out.append(("High", i, "self-hosted", "self-hosted runner on fork-reachable trigger"))
        if re.search(r"cancel-in-progress:\s*true", line) and re.search(r"(deploy|release|publish)", text, re.I):
            out.append(("Low", i, "cancel-deploy", "check cancel-in-progress is not applied to deploy/release"))
        # script injection: expression on a run line or inside a run block / github-script
        rm = re.match(r"^(\s*)-?\s*(run|script):\s*(.*)$", line)
        if rm:
            in_run = rm.group(3) in ("|", "|-", ">", ">-", "|+")
            run_indent = len(rm.group(1))
            if UNTRUSTED.search(rm.group(3)):
                out.append(("High", i, "script-injection", stripped))
            continue
        if in_run:
            indent = len(line) - len(line.lstrip())
            if stripped and indent <= run_indent:
                in_run = False
            elif UNTRUSTED.search(line):
                out.append(("High", i, "script-injection", stripped))
    return out


def main(argv):
    targets = [Path(a) for a in argv] or [Path(".github/workflows")]
    files = []
    for t in targets:
        if t.is_dir():
            files += sorted(list(t.glob("*.yml")) + list(t.glob("*.yaml")))
        elif t.is_file():
            files.append(t)
    bad = False
    for f in files:
        for sev, ln, rule, msg in scan(f):
            print(f"{sev} {f}:{ln} {rule} {msg}")
            if sev in ("Critical", "High"):
                bad = True
    if not files:
        print("no workflow files found", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
