---
name: openapi-breaking-change-report
description: Compares two versions of an OpenAPI 3.x spec and reports breaking, risky and safe changes for API consumers, with a semver bump suggestion and migration notes. Use when asked to diff OpenAPI or Swagger specs, check for breaking changes, review an API PR, compare openapi.yaml files, or run oasdiff.
---

# OpenAPI Breaking Change Report

Compare a base and a revised OpenAPI 3.x spec, classify every change from the API consumer's point of view, suggest a semver bump for `info.version`, and write migration notes.

## Steps

1. **Identify the two inputs.** Base (old) and revision (new): file paths, pasted text, or git revisions. If only one file is given, ask for the other or use `git show REV:path` to fetch the previous version. Never guess which is newer.
2. **Validate both.** Confirm each parses and has an `openapi: 3.x` field. Do not confuse `openapi` (the spec version) with `info.version` (the API version). If either is `3.2.x`, warn that many diff tools only support up to 3.1 and verify tool output manually. A malformed spec gives silently wrong diffs, so stop and report parse errors.
3. **Detect tooling.** Run `command -v oasdiff` and `oasdiff --help`. Confirm flag spellings from `--help` before using them; do not assume.
   - If `oasdiff` exists, run `oasdiff changelog BASE REVISION` and `oasdiff breaking BASE REVISION`. Add `--format json` if you need to post-process. Map severity ERR to breaking, WARN to risky, INFO to safe. Run `oasdiff checks` to see rule IDs if needed.
   - If it is missing, run the bundled fallback: `python scripts/openapi_diff.py BASE REVISION` (needs PyYAML for YAML files; JSON works without). Do not install anything without the user's agreement.
   - Either way, you must still apply steps 4-8, because tools miss renames, effective-security inheritance and policy.
4. **Normalise before judging.** Compare parsed models, never raw text (key order, anchors, formatting cause false positives). Resolve external `$ref`s (or bundle first), merge `allOf`, and treat 3.0 `nullable: true` and 3.1 `type: [X, "null"]` or `oneOf` with null as the same thing. A 3.0 to 3.1 notation change alone is not a change. Ignore `servers`/`info` noise unless the base URL changed. Ignore trailing-slash and path-parameter-name differences when matching paths (`/u/{id}` equals `/u/{userId}` on the wire).
5. **Compute effective security per operation.** An operation-level `security` overrides root `security`; `security: []` means open; an absent key means inherit. Diff the effective result, not the raw keys.
6. **Classify each change with direction.** Use [references/classification-rules.md](references/classification-rules.md). Request-side: stricter is breaking. Response-side: looser or less predictable is breaking. A shared `components/schemas` entry used in both directions needs both evaluations; the worse class wins. Group by component with a "used by" list instead of repeating one change per usage.
7. **Detect likely renames.** A removed path plus an added path with the same method and a similar schema (or similar path text) is reported as one "likely rename" (breaking for paths; risky for `operationId`/tag renames, since they break generated SDKs, not the wire). Mark it as a heuristic.
8. **Apply deprecation context.** If a removed operation was `deprecated: true` in the base and a sunset (`x-sunset`, or a `Sunset`/`Deprecation` note in the description) has passed, downgrade removal to risky and say why. Otherwise removal is breaking.
9. **Suggest the semver bump.** See [references/semver-and-migration.md](references/semver-and-migration.md). Any breaking: MAJOR. Else any new feature, deprecation or risky change: MINOR. Else docs-only: PATCH. No change: none. If the current `0.y.z` version is below 1.0, say anything may change and suggest MINOR for breaking changes instead of forcing 1.0. If the API versions in the URL (`/v1/`) or a header, say a breaking change means a new version prefix, not an `info.version` bump; ask or detect which. Compare with the author's actual new `info.version` and flag an under-bump or an unchanged version.
10. **Write migration notes** for every breaking and risky item: pointer, who is affected, before/after, required action, mitigation.

## Output format

Use these sections in order: Summary, Breaking, Risky, Safe, Semver, Migration notes, Caveats. Always give JSON-pointer-style locations. Keep Safe to one line each.

```
## Summary
Base 2.3.1 -> revision 2.4.0 | 3 breaking, 2 risky, 4 safe | Suggested: MAJOR (3.0.0). Declared 2.4.0 is an under-bump.
Tool: oasdiff changelog (ERR/WARN/INFO mapped) + manual checks

## Breaking
1. paths./users/{id}.get.parameters: new required query param `tenant` (request, new-required-request-parameter)
2. paths./orders.get.responses.200 ... Order.discount: now nullable (response)
3. paths./pets: removed; likely rename to /animals (heuristic, same methods and schema)

## Risky
1. components.schemas.Status enum: added `paused` (response; strict clients may fail). Used by: GET /jobs, GET /jobs/{id}

## Migration notes
- GET /users/{id}: send `tenant=<id>`. Affected: all callers. Mitigation: server default for one release.
```

## Gotchas

- `readOnly` properties newly required in a request are not breaking; `writeOnly` properties in a response are irrelevant.
- A remaining `default` response softens, but does not erase, removal of specific status codes. Still risky.
- Request enum additions are safe; response enum additions are risky. Removals are the reverse.
- New optional response fields are safe unless the schema has `additionalProperties: false` or consumers deserialise strictly: then risky.
- Removed request properties are risky, or breaking when `additionalProperties: false`.
- `x-` extension, `description`, `summary` and `example` changes are safe (PATCH), though extensions may affect code generators.
- Removing security is safe for clients but flag it as a security review item.
- oasdiff does not detect renames. Do not report them as one add plus one remove without noting the likely link.
- Do not invent rule IDs. Quote only what `oasdiff checks` prints or label the item as your own classification.
- When something cannot be determined (unresolved external `$ref`, unsupported 3.2 feature), list it under Caveats rather than guessing.
