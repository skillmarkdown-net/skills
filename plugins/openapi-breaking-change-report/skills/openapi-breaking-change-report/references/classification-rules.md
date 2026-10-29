# Classification rules

Direction matters. Request side (consumer sends): stricter is breaking. Response side (consumer receives): looser or less predictable is breaking. For schemas shared by both, evaluate both and keep the worse class.

## Paths and operations

| Change | Class |
|---|---|
| Path or method removed | breaking |
| Removed after `deprecated: true` and passed sunset | risky |
| Path renamed | breaking |
| `operationId` or tag renamed | risky (generated SDKs only) |
| Path template parameter renamed, same URL shape | safe on the wire, risky for codegen |
| New path or operation | safe |
| `deprecated: true` added | safe, mention in migration notes |
| Server URL or basePath changed | risky or breaking |

## Parameters

| Change | Class |
|---|---|
| New required parameter (query, header, path, cookie) | breaking |
| New optional parameter | safe |
| Optional to required | breaking |
| Required to optional | safe |
| Parameter removed | risky |
| Parameter renamed | breaking |
| Location (`in`) changed | breaking |
| `style` / `explode` changed | breaking |
| Default value changed | risky |

## Request body

| Change | Class |
|---|---|
| Body added as required | breaking |
| Body added as optional | safe |
| Body `required` false to true | breaking |
| Media type removed | breaking |
| Media type added | safe |
| New required property | breaking |
| New optional property | safe |
| Optional property to required | breaking |
| Property removed | risky; breaking if `additionalProperties: false` |

## Types and constraints

| Direction | Change | Class |
|---|---|---|
| Request | Enum value removed | breaking |
| Request | Enum value added | safe |
| Request | Type narrowed (number to integer, string to enum) | breaking |
| Request | Type widened (integer to number) | safe |
| Request | maxLength/maximum/maxItems lowered, minLength/minimum raised | breaking |
| Request | Constraint relaxed | safe |
| Request | `pattern` or `format` changed | risky |
| Response | Enum value added | risky |
| Response | Enum value removed | safe |
| Response | Type changed | breaking |
| Response | Constraint loosened | risky |
| Response | `format` changed | risky |

## Response fields

| Change | Class |
|---|---|
| Property removed | breaking |
| Made nullable (`nullable: true` or `"null"` in type) | breaking |
| Made non-nullable | safe |
| Required to optional | breaking |
| Optional to required | safe |
| New property | safe; risky with `additionalProperties: false` or strict clients |
| New `oneOf`/`anyOf` variant | risky |
| Variant removed | safe |

## Status codes and responses

| Change | Class |
|---|---|
| 2xx removed | breaking |
| Non-success code removed | risky |
| New response code added | risky |
| Response media type removed | breaking |
| Response header removed | breaking |
| New response header | safe |

## Auth (use effective security per operation)

| Change | Class |
|---|---|
| Security added to an open operation | breaking |
| Scheme type changed | breaking |
| New required scope | breaking |
| Scope removed | risky |
| Security removed | safe, flag for security review |
| Alternative added to OR list | safe |
| Alternative removed from OR list | breaking |
| apiKey name or location changed | breaking |
| OAuth2 URLs or flow changed | breaking |

## Safe by default

`description`, `summary`, `example(s)`, `externalDocs`, `x-` extensions (wire-wise), `info.contact`, key order.

## 3.0 vs 3.1 normalisation

- `nullable: true` equals `type: [T, "null"]` equals `oneOf` with `{type: "null"}`.
- Boolean `exclusiveMinimum`/`exclusiveMaximum` (3.0) equals numeric form (3.1) with the same bound.
- `example` equals the first of `examples`.
- `format: binary`/`byte` equals `contentMediaType`/`contentEncoding`.
