# Scan commands

Only give or run these when an image, tarball or registry reference exists. Do not claim a scan ran if it did not.

## Trivy
```
trivy image myapp:tag
trivy image --severity HIGH,CRITICAL myapp:tag
trivy image --ignore-unfixed myapp:tag
trivy image --input myapp.tar
trivy image --scanners vuln,secret myapp:tag
trivy config .
trivy config --severity HIGH,CRITICAL --exit-code 1 .
trivy image --format json --output result.json myapp:tag
trivy image --format cyclonedx --output result.cdx myapp:tag
```
- Findings do not change the exit code by default (it is 0). CI gate: `trivy image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed myapp:tag`.
- `--exit-code` does not override operational errors such as pull or database failures.
- `--ignore-unfixed` hides vulnerabilities with no vendor fix. It changes reporting, not the image.
- Severity comes from vendor data; if none, UNKNOWN. `--vuln-severity-source auto,nvd` changes priority.
- `--scanners vuln,secret` finds secrets baked into layers.
- Use `--ignorefile .trivyignore.yaml` sparingly: no blanket package or severity exclusions, review entries on a schedule.
- For reproducibility scan by digest or from a tarball, and record scanner and database versions. Pin the scanner version in CI.
- Rate limits on the database download: `--skip-db-update` or `--db-repository <mirror>`.

## Docker Scout (needs a Docker login)
```
docker scout quickview myapp:tag
docker scout cves myapp:tag
docker scout cves --only-fixed --only-severity critical,high myapp:tag
docker scout cves myapp:tag --only-severity critical,high --exit-code
docker scout recommendations myapp:tag
docker scout compare myapp:v2 --to myapp:v1
```
- `--exit-code` returns 2 when vulnerabilities are detected.
- `--ignore-base` hides base-image CVEs; `--only-base` shows only those. Use both to separate base from app-layer findings.
- `--only-fixed` changes reporting, not image contents.

## Inspecting size and layers
```
docker image ls myapp
docker history --no-trunc myapp:tag
```
`docker history --no-trunc` also reveals leaked `ARG` and `ENV` values. `dive` is a third-party tool for layer inspection.

## Static lint
```
hadolint Dockerfile
hadolint --format sarif Dockerfile
docker build --check .
```

## Triage order
1. Fixable CRITICAL and HIGH in the base: rebase to a newer pinned digest.
2. Fixable CRITICAL and HIGH in app dependencies: upgrade them.
3. Unfixed findings: document, consider a smaller base, use VEX only with evidence.
