---
name: dockerfile-hardening-audit
description: Audits a Dockerfile and the image it builds for security and size problems, then returns findings by severity and a fixed Dockerfile plus .dockerignore. Use when asked to harden, secure, review or slim a Dockerfile, add a non-root USER, pin base images by digest, remove secrets from layers, or scan with Trivy or Docker Scout.
---

# Dockerfile Hardening Audit

Review a Dockerfile (and the image it builds, if available), report findings ranked by severity, and deliver a fixed Dockerfile, a `.dockerignore` and the commands to verify the result.

## Steps

1. **Collect inputs.** Read the Dockerfile, any `.dockerignore` or `<Dockerfile-name>.dockerignore`, the build command or CI file, the app language and the runtime port. If something is missing, say so and continue. Never run builds, pushes or scans the user did not ask for; propose the commands instead.
2. **Static pass.** Run `python3 scripts/dockerfile_lint.py Dockerfile` for a deterministic first list (line numbers, rule IDs, severities). It is a starting point only. Read the file yourself for what a regex cannot see: stage structure, what the final stage copies, what the build context contains.
3. **Optional tools.** If `hadolint` or `trivy` is installed, run `hadolint Dockerfile` and `trivy config --severity HIGH,CRITICAL .`. Reuse their IDs (DLxxxx, DSxxx). If not installed, never claim they were run.
4. **Walk the checklist** in [references/hardening-checklist.md](references/hardening-checklist.md): secrets, base image, stages, user, COPY/ADD, HEALTHCHECK, cache order, packages, `.dockerignore`, entrypoint form.
5. **Assign severity** using [references/severity-model.md](references/severity-model.md). The same pattern always gets the same severity.
6. **Write the fixed Dockerfile.** Apply every fix that does not change app behaviour. For risky changes (switch to Alpine or distroless, port change, dropped packages) pick the safest option and flag the risk in a comment and in the report.
7. **Write or fix `.dockerignore`.** Prefer an allowlist (`*` then `!path`) when build inputs are clear; otherwise use the blocklist in the checklist. Check it against every `COPY` line so nothing the build needs is excluded.
8. **Image scan (only if an image or registry reference exists).** Give the commands from [references/scan-commands.md](references/scan-commands.md). Interpret results by severity, separate base-image CVEs from app-layer CVEs, and prefer rebasing over suppressing.
9. **Report** in the format below, stating what was verified by tool output versus judged by reading.

## Fix rules that matter

- **Digest pin.** `FROM image:tag@sha256:<digest>`. Keep the tag for humans; only the digest is enforced. Look it up with `docker buildx imagetools inspect image:tag` or `crane digest image:tag` and pin the multi-arch index digest. Never invent a digest: write `<digest>` as a placeholder and tell the user how to fill it. Pinning needs Dependabot or Renovate, otherwise the base stops getting security fixes.
- **Secrets.** Replace `ARG`/`ENV` secrets and copied credential files with a secret mount used only in the one `RUN` that needs it: `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci`, built with `docker build --secret id=npmrc,src=$HOME/.npmrc .`. The default mount path is `/run/secrets/<id>`; `env=` exposes it as an environment variable for that `RUN` only. For private git use `RUN --mount=type=ssh` with `docker build --ssh default`. Deleting a secret in a later layer does not remove it from the earlier layer. If a secret was ever in a pushed image, tell the user to rotate it.
- **Syntax line.** Start with `# syntax=docker/dockerfile:1`.
- **Multi-stage.** Name stages (`AS build`), final stage last, copy only artifacts with `COPY --from=build`. The runtime stage has no compilers, package manager caches or test dependencies.
- **Base choice.** Go with `CGO_ENABLED=0`: distroless `static` or `scratch`. Needs libc: distroless `base` or `cc`, or `-slim` Debian. Python and Node with native modules: prefer `-slim` over Alpine (musl breaks wheels and native addons). Distroless has no shell, so use exec-form `CMD` and troubleshoot with the `:debug` tag or `docker debug`. Check the registry for current tags and supported versions rather than trusting memory; do not recommend an end-of-life base.
- **USER.** Numeric: `USER 10001:10001`, created earlier with `groupadd`/`useradd` (Debian) or `addgroup`/`adduser` (Alpine). Distroless offers `:nonroot` (uid 65532). Use `COPY --chown=10001:10001`. Put `USER` after installs that need root. Non-root cannot bind ports below 1024, so `EXPOSE 8080`.
- **COPY not ADD.** If a remote `ADD` is unavoidable, use `ADD --checksum=sha256:<hash> <url> <dest>`, or download and verify the checksum in a builder stage. Never pipe a download into a shell; download the file, verify its checksum, then run it.
- **HEALTHCHECK.** For long-running network services add one, for example `HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD ["/app","--healthcheck"]`. Without curl or a shell the check must be a binary in the image; otherwise say to rely on orchestrator probes. Kubernetes ignores Dockerfile HEALTHCHECK and uses liveness and readiness probes. Do not add one to batch jobs.
- **Cache order.** Base, system packages, copy only manifests (`package*.json`, `requirements.txt`, `go.mod go.sum`), install dependencies, copy source, build. Use cache mounts: `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`.
- **Packages.** One `RUN` for `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`. Use `apk add --no-cache`. Use `pip install --no-cache-dir` unless a cache mount is used. Add `SHELL ["/bin/bash","-o","pipefail","-c"]` when a `RUN` uses a pipe.
- **Entrypoint.** Exec form (JSON array) for `CMD` and `ENTRYPOINT` so signals reach the process; suggest `docker run --init` or tini if the app does not reap children.

## Output format

Use exactly this structure.

````
## Summary
<one or two sentences: overall risk, counts per severity, what was verified>

## Findings
### CRITICAL
- [DS031 | line 4] Secret passed via ARG. Persists in `docker history` and provenance. Fix: BuildKit secret mount (see fixed file).
### HIGH
- [DL3002 | line 12] Final user is root. A container escape or app bug runs as uid 0. Fix: numeric non-root USER.
### MEDIUM
...
### LOW
...
(omit empty severities; write `none` only if there are no findings at all)

## Fixed Dockerfile
```dockerfile
...
```

## .dockerignore
```
...
```

## Verify
<build command with --secret, scan commands, manual follow-up such as rotating a leaked secret>

## Not verified / assumptions
<digests left as placeholders, port assumed, tools not run>
````

Each finding line: `[ID | line N] what is wrong. Why it matters. Fix.` Use the Hadolint or Trivy ID when one exists, otherwise a short label such as `NO-DOCKERIGNORE`.

## Gotchas

- `--ignore-unfixed` (Trivy) and `--only-fixed` (Scout) change reporting, not image contents. Say so when used for a gate.
- Trivy exits 0 on findings unless `--exit-code 1` is set. Scout `--exit-code` returns 2 when vulnerabilities are found.
- `ARG` values appear in `docker history` and, with `--provenance=mode=max`, in attestations. Secrets can also land in an exported `--cache-to` cache.
- A `.dockerignore` excluding `Dockerfile*` is fine, but excluding a lockfile or `src` breaks the build; check against the `COPY` lines.
- Pin the multi-arch index digest, not a per-platform one, or builds break on other architectures.
- Do not quote rule IDs from memory if unsure; use the label form instead.
- Do not invent CVE numbers, digests or image sizes. Give sizes only as approximate and prefer measuring with `docker image ls` and `docker history --no-trunc`.
- Keep app behaviour intact: preserve ports, non-secret runtime env, entrypoint semantics and working directory unless a finding requires a change, and say when you changed one.
