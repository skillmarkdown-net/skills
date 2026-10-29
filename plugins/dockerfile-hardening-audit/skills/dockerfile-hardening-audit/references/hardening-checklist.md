# Hardening checklist

Work through every section. Items marked (ID) map to Hadolint or Trivy rules; confirm against the tool output before quoting an ID you are unsure of.

## 1. Secrets
- No `ARG` or `ENV` holding tokens, passwords or keys (DS031). They persist in `docker history --no-trunc` and in provenance attestations.
- No `COPY . .` without a `.dockerignore` (pulls in `.env`, `.git`, `*.pem`).
- No credentials in URLs: `git clone https://user:token@...`.
- No `.npmrc`, `pip.conf`, `.netrc`, `.aws`, `.ssh` copied into the image.
- Removing a secret in a later layer does not remove it from the earlier layer.
- Use `RUN --mount=type=secret,id=<id>` in only the one `RUN` that needs it. Optional flags: `required=true`, `target=`, `env=`.
- Private git: `RUN --mount=type=ssh`, build with `docker build --ssh default`.
- `docker build --check` runs build checks and may flag secret-looking `ARG`/`ENV` names (confirm the rule is present in the installed version).

## 2. Base image
- Not `latest` and not untagged (DL3006, DL3007, DS001).
- Pinned as `tag@sha256:<digest>` (multi-arch index digest). Automated bump PRs configured (Dependabot or Renovate).
- Smallest base that works: distroless `static` (Go, CGO off), `base`/`cc` (needs libc), `-slim` Debian (Python, Node native modules). Alpine uses musl; avoid for wheels and native addons unless tested.
- Not end of life. Check the registry and upstream support pages for current tags.
- Docker Hardened Images are an option; verify current availability, registry and tag scheme at https://docs.docker.com/dhi/ before recommending.

## 3. Stages
- Build tools, compilers, test dependencies live only in named build stages.
- Final stage last, copies only artifacts via `COPY --from=<stage>`.
- Optional `test` or `debug` stages selected with `--target`.

## 4. User
- Final `USER` is numeric and non-root, for example `10001:10001` (DL3002, DS002).
- Debian: `groupadd -r app --gid 10001 && useradd -r -g app --uid 10001 app`. Alpine: `addgroup -S -g 10001 app && adduser -S -u 10001 -G app app`.
- Files owned with `COPY --chown=10001:10001`. `USER` placed after root-only installs.
- Port is 1024 or above. No port 22 exposed (DS004). No SSH server and no `sudo` package installed.
- Runtime flags to mention: `--read-only`, `--cap-drop=ALL`, `--security-opt no-new-privileges`; Kubernetes `securityContext`.

## 5. COPY vs ADD
- `COPY` for local files (DL3020, DS005).
- Remote `ADD` only with `--checksum=sha256:<hash>`, or download and verify in a builder stage.
- Never pipe a downloaded script into a shell. Download to a file, verify the checksum, then execute.

## 6. HEALTHCHECK
- Present for long-running network services (DS026). Syntax: `HEALTHCHECK [--interval=30s] [--timeout=30s] [--start-period=0s] [--retries=3] CMD <cmd>`; confirm `--start-interval` support in the Dockerfile reference.
- Exit 0 healthy, 1 unhealthy. Only the last `HEALTHCHECK` counts. `HEALTHCHECK NONE` disables an inherited one.
- Distroless has no curl: use an app binary flag or orchestrator probes. Kubernetes ignores Dockerfile HEALTHCHECK.

## 7. Cache order
1. Base and system packages.
2. Dependency manifests only.
3. Install dependencies (cache mount where useful).
4. Copy source.
5. Build.

## 8. Packages
- `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` in one `RUN` (DL3009, DL3015, DS017, DS029).
- `apk add --no-cache` (DL3019). `pip install --no-cache-dir` unless a cache mount is used (DL3042).
- `SHELL ["/bin/bash","-o","pipefail","-c"]` when a `RUN` has a pipe (DL4006).
- `WORKDIR` with an absolute path instead of `cd` (DL3000, DL3003, DS013).
- Merge consecutive `RUN` lines where it does not hurt caching (DL3059).

## 9. .dockerignore
- At the context root; BuildKit also reads `<Dockerfile-name>.dockerignore` and prefers it.
- Allowlist style is safest: `*` then `!src`, `!package*.json`.
- Blocklist minimum: `.git`, `**/.env*`, `*.pem`, `*.key`, `**/node_modules`, `**/__pycache__`, `.venv`, `.aws`, `.ssh`, `.npmrc`, `docker-compose*`, `*.md`, test and CI directories.
- The last matching rule wins; `!` re-includes.

## 10. Entrypoint
- Exec-form JSON array for `CMD` and `ENTRYPOINT` (DL3025).
- PID 1 that does not reap children: `docker run --init` or tini.

## 11. Supply chain
- `docker buildx build --sbom=true --provenance=mode=max --push .` attaches an SBOM and provenance. `mode=max` can record build args, so never pass secrets as `ARG`.
- Sign with cosign and verify digests at deploy time.
- Rebuild regularly with `--pull` (and occasionally `--no-cache`) to pick up base fixes.
