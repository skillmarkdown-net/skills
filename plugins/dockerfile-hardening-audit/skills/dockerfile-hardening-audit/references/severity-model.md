# Severity model

This is a consistent judgment model, not an official standard. Apply it the same way every time.

| Severity | Findings |
|---|---|
| CRITICAL | Secrets in `ARG`, `ENV` or `COPY`; credentials in URLs; a downloaded script piped straight into a shell; remote `ADD` with no checksum; mounting `docker.sock`; privileged mode |
| HIGH | Final user is root; `latest`, untagged or otherwise unpinned base; no `.dockerignore` combined with `COPY . .`; the `sudo` package or an SSH server installed; known fixable CRITICAL or HIGH CVEs in the image |
| MEDIUM | Tag without digest pin; single-stage build with build tools in the runtime image; `ADD` for local files; no `HEALTHCHECK` on a long-running service; apt lists not cleaned; unpinned or unneeded packages |
| LOW | Poor cache ordering; missing `LABEL` metadata; shell-form `CMD`/`ENTRYPOINT`; consecutive `RUN` instructions; avoidable image size |

## Rules of thumb
- When two patterns overlap, report the higher severity once and mention the other in the same line.
- A secret that was ever in a pushed image is CRITICAL even if the current Dockerfile no longer has it. Recommend rotation.
- Raise a MEDIUM to HIGH when the image is internet-facing and the finding widens attack surface (shell, package manager and build tools in runtime).
- Lower HEALTHCHECK to LOW for batch jobs or when an orchestrator probe is documented.
- CVE findings: use the scanner severity as reported. Severity comes from vendor data; UNKNOWN stays UNKNOWN and is reported separately.

## Each finding includes
1. ID (Hadolint or Trivy ID where one exists, else a short label).
2. Line number.
3. What is wrong and why it matters.
4. The fix, shown in the fixed Dockerfile.
