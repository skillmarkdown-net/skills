#!/usr/bin/env python3
"""Static first-pass Dockerfile linter for the hardening audit.

Usage:
    python3 scripts/dockerfile_lint.py Dockerfile [--json]

Reads the file only. No network calls. Prints findings as
`SEVERITY [ID | line N] message`. Exit code 0 always; this is advisory.
It is a regex pass: it cannot judge stage structure or build context.
"""
import json
import re
import sys

SECRET_NAME = re.compile(r"(PASS(WORD)?|SECRET|TOKEN|API_?KEY|PRIVATE_?KEY|CREDENTIAL)", re.I)


def logical_lines(text):
    """Yield (line_number, instruction_text) joining backslash continuations."""
    buf, start = [], 0
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not buf:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            start = i
        if line.endswith("\\"):
            buf.append(line[:-1])
            continue
        buf.append(line)
        yield start, " ".join(p.strip() for p in buf)
        buf = []
    if buf:
        yield start, " ".join(p.strip() for p in buf)


def lint(text):
    out = []
    users = []
    has_health = False
    has_syntax = bool(re.match(r"\s*#\s*syntax=", text))
    stages = 0
    last_from_line = 0
    for n, ins in logical_lines(text):
        parts = ins.split(None, 1)
        op = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ""
        if op == "FROM":
            stages += 1
            last_from_line = n
            users = []
            m = re.match(r"(--\S+\s+)*(\S+)", arg)
            image = m.group(2) if m else ""
            if image.lower() != "scratch" and not image.startswith("$"):
                if "@sha256:" not in image:
                    last = image.rsplit("/", 1)[-1]
                    if ":" not in last:
                        out.append(("HIGH", "DL3006", n, "Base image has no tag or digest."))
                    elif last.endswith(":latest"):
                        out.append(("HIGH", "DL3007", n, "Base image uses the latest tag."))
                    else:
                        out.append(("MEDIUM", "NO-DIGEST", n, "Base image is not pinned by digest."))
        elif op in ("ARG", "ENV"):
            name = re.split(r"[=\s]", arg.strip(), 1)[0]
            if SECRET_NAME.search(name):
                out.append(("CRITICAL", "DS031", n, f"{op} {name} looks like a secret and persists in image metadata."))
        elif op == "ADD":
            if re.search(r"https?://", arg) and "--checksum" not in arg:
                out.append(("CRITICAL", "ADD-REMOTE", n, "ADD from a URL without --checksum."))
            else:
                out.append(("MEDIUM", "DL3020", n, "Use COPY instead of ADD."))
        elif op == "USER":
            users.append((n, arg.strip()))
        elif op == "HEALTHCHECK":
            has_health = True
        elif op in ("CMD", "ENTRYPOINT"):
            if not arg.strip().startswith("["):
                out.append(("LOW", "DL3025", n, f"{op} uses shell form; use a JSON array."))
        elif op == "COPY":
            if re.search(r"(^|\s)\.\s+\S+\s*$", arg) and "--from" not in arg:
                out.append(("LOW", "COPY-ALL", n, "COPY of the whole context; confirm a .dockerignore exists."))
            if re.search(r"\.(env|npmrc|netrc|pem|key)\b", arg):
                out.append(("CRITICAL", "COPY-CRED", n, "Copies a credential-like file into the image."))
        elif op == "RUN":
            if re.search(r"(curl|wget)[^|;&]*\|\s*(sudo\s+)?(ba|z)?sh\b", arg):
                out.append(("CRITICAL", "PIPE-TO-SHELL", n, "Download piped into a shell; download, verify checksum, then run."))
            if re.search(r"://[^/\s:@]+:[^/\s@]+@", arg):
                out.append(("CRITICAL", "URL-CRED", n, "Credentials embedded in a URL."))
            if "apt-get install" in arg:
                if "--no-install-recommends" not in arg:
                    out.append(("LOW", "DL3015", n, "apt-get install without --no-install-recommends."))
                if "/var/lib/apt/lists" not in arg:
                    out.append(("MEDIUM", "DL3009", n, "apt lists not removed in the same RUN."))
            if "apt-get update" in arg and "apt-get install" not in arg:
                out.append(("MEDIUM", "DS017", n, "apt-get update alone in a layer."))
            if "apk add" in arg and "--no-cache" not in arg:
                out.append(("LOW", "DL3019", n, "apk add without --no-cache."))
            if "pip install" in arg and "--no-cache-dir" not in arg and "type=cache" not in arg:
                out.append(("LOW", "DL3042", n, "pip install without --no-cache-dir."))
            if re.search(r"(^|[;&|]\s*)cd\s", arg):
                out.append(("LOW", "DS013", n, "Use WORKDIR instead of cd."))
            if re.search(r"\bsudo\b", arg):
                out.append(("HIGH", "SUDO", n, "sudo used in a build step; avoid it in images."))
        if op == "EXPOSE" and re.search(r"(^|\s)22(/|\s|$)", arg + " "):
            out.append(("HIGH", "DS004", n, "Port 22 exposed."))
    if stages == 0:
        out.append(("HIGH", "NO-FROM", 1, "No FROM instruction found."))
        return out
    final_user = users[-1] if users else None
    if final_user is None:
        out.append(("HIGH", "DS002", last_from_line, "No USER in the final stage; runs as root."))
    elif final_user[1].split(":")[0] in ("root", "0"):
        out.append(("HIGH", "DL3002", final_user[0], "Final USER is root."))
    if not has_health:
        out.append(("MEDIUM", "DS026", last_from_line, "No HEALTHCHECK (ignore for batch jobs or orchestrator probes)."))
    if stages == 1:
        out.append(("MEDIUM", "SINGLE-STAGE", 1, "Single-stage build; check for build tools in the runtime image."))
    if not has_syntax:
        out.append(("LOW", "NO-SYNTAX", 1, "Missing # syntax=docker/dockerfile:1 line."))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    path = argv[1]
    with open(path, encoding="utf-8") as fh:
        findings = lint(fh.read())
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings.sort(key=lambda f: (order[f[0]], f[2]))
    if "--json" in argv:
        print(json.dumps([{"severity": s, "id": i, "line": n, "message": m} for s, i, n, m in findings], indent=2))
    else:
        for s, i, n, m in findings:
            print(f"{s} [{i} | line {n}] {m}")
        if not findings:
            print("No findings from the static pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
