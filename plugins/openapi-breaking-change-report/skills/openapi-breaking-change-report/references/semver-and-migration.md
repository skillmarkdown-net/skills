# Semver and migration notes

## Bump algorithm (applies to `info.version`)

1. Any breaking change: MAJOR.
2. Else new endpoint, new optional field, deprecation, or any risky change: MINOR.
3. Else docs, examples, descriptions only: PATCH.
4. Else no change: no bump.

Risky changes: recommend at least MINOR; say MAJOR is arguably warranted when consumers include strict or generated clients. Let the user pick the policy and state which one you applied.

SemVer 2.0.0 details: `0.y.z` is initial development, so say anything may change instead of forcing a major. Pre-release (`-rc.1`) is allowed; build metadata (`+build`) is ignored in precedence. Compare numerically per field.

If the API is versioned in the URL (`/v1/`) or a header, a breaking change means a new prefix (`/v2/`) rather than an `info.version` major bump, so ask or detect.

Also report: declared version unchanged despite changes; declared bump smaller than suggested.

## Migration note template

For each breaking or risky item:

- Where: JSON pointer, e.g. `paths./users/{id}.get.responses.200`
- Who is affected: request senders, response parsers, or generated SDK users
- Before / after values
- Action required
- Mitigation: e.g. server-side default, accept both names for one release, keep old path as alias

## Deprecation signalling before removal

- `Sunset` response header, RFC 8594.
- `Deprecation` response header, RFC 9745 (structured-field date such as `@1688169599`); confirm the current RFC status before citing.
- Optional `Link: <url>; rel="deprecation"` pointing at migration docs.
- Mark the operation `deprecated: true` in the spec and release as MINOR first.
