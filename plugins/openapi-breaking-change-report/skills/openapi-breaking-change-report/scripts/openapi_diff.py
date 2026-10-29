#!/usr/bin/env python3
"""Minimal OpenAPI 3.x diff fallback (no network, standard library; PyYAML optional for YAML).

Usage:
    python scripts/openapi_diff.py BASE REVISION [--json]

Covers: removed/added paths and methods, parameter changes, request body required changes,
response status removal/addition, response property removal, nullable changes, enum changes,
required property changes. Does not resolve external refs; local #/components refs only.
Output: lines of 'CLASS | location | message'. Review manually; this is a floor, not a ceiling.
"""
import json
import sys

METHODS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]
out = []


def load(p):
    with open(p, encoding="utf-8") as f:
        t = f.read()
    if p.endswith(".json"):
        return json.loads(t)
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required for YAML input; or convert the spec to JSON.")
    return yaml.safe_load(t)


def add(c, loc, msg):
    out.append((c, loc, msg))


def resolve(spec, s, depth=0):
    while isinstance(s, dict) and "$ref" in s and depth < 20:
        r = s["$ref"]
        if not r.startswith("#/"):
            return {}
        n = spec
        for part in r[2:].split("/"):
            n = n.get(part.replace("~1", "/").replace("~0", "~"), {}) if isinstance(n, dict) else {}
        s = n
        depth += 1
    return s if isinstance(s, dict) else {}


def flat(spec, s, depth=0):
    s = resolve(spec, s)
    if depth > 10:
        return s
    if "allOf" in s:
        m = {k: v for k, v in s.items() if k != "allOf"}
        props, req = dict(m.get("properties", {})), list(m.get("required", []))
        for sub in s["allOf"]:
            f = flat(spec, sub, depth + 1)
            props.update(f.get("properties", {}))
            req += f.get("required", [])
            for k, v in f.items():
                m.setdefault(k, v)
        m["properties"], m["required"] = props, req
        return m
    return s


def nullable(s):
    t = s.get("type")
    return bool(s.get("nullable")) or (isinstance(t, list) and "null" in t) or any(
        isinstance(x, dict) and x.get("type") == "null" for x in s.get("oneOf", []) + s.get("anyOf", []))


def base_type(s):
    t = s.get("type")
    if isinstance(t, list):
        t = sorted(x for x in t if x != "null")
        return t[0] if len(t) == 1 else tuple(t)
    return t


def schema_diff(a_spec, b_spec, a, b, loc, request, depth=0):
    if depth > 8:
        return
    a, b = flat(a_spec, a), flat(b_spec, b)
    ta, tb = base_type(a), base_type(b)
    if ta and tb and ta != tb:
        widening = (ta, tb) == ("integer", "number")
        if request:
            add("safe" if widening else "breaking", loc, f"type {ta} -> {tb}")
        else:
            add("breaking", loc, f"type {ta} -> {tb}")
    ea, eb = a.get("enum"), b.get("enum")
    if ea and eb:
        removed, added = set(map(str, ea)) - set(map(str, eb)), set(map(str, eb)) - set(map(str, ea))
        if removed:
            add("breaking" if request else "safe", loc, f"enum values removed: {sorted(removed)}")
        if added:
            add("safe" if request else "risky", loc, f"enum values added: {sorted(added)}")
    if not request and not nullable(a) and nullable(b):
        add("breaking", loc, "now nullable")
    pa, pb = a.get("properties", {}), b.get("properties", {})
    ra, rb = set(a.get("required", [])), set(b.get("required", []))
    for k in pa:
        if k not in pb:
            closed = b.get("additionalProperties") is False
            add("breaking" if (not request or closed) and not (request and not closed) else "risky", f"{loc}.{k}", "property removed")
    for k in pb:
        ro = flat(b_spec, pb[k]).get("readOnly")
        if k not in pa:
            if request and k in rb and not ro:
                add("breaking", f"{loc}.{k}", "new required property")
            else:
                add("safe", f"{loc}.{k}", "new property")
    for k in pa:
        if k in pb:
            if request and k in rb and k not in ra:
                add("breaking", f"{loc}.{k}", "optional -> required")
            if not request and k in ra and k not in rb:
                add("breaking", f"{loc}.{k}", "required -> optional (may be absent)")
            schema_diff(a_spec, b_spec, pa[k], pb[k], f"{loc}.{k}", request, depth + 1)
    if a.get("items") and b.get("items"):
        schema_diff(a_spec, b_spec, a["items"], b["items"], loc + "[]", request, depth + 1)


def params(spec, item, op):
    r = {}
    for p in item.get("parameters", []) + op.get("parameters", []):
        p = resolve(spec, p)
        r[(p.get("name"), p.get("in"))] = p
    return r


def norm_path(p):
    import re
    return re.sub(r"\{[^}]+\}", "{}", p).rstrip("/") or "/"


def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    A, B = load(args[0]), load(args[1])
    for n, s in (("base", A), ("revision", B)):
        if not isinstance(s, dict) or not str(s.get("openapi", "")).startswith("3."):
            sys.exit(f"{n}: not an OpenAPI 3.x document")
        if str(s["openapi"]).startswith("3.2"):
            print(f"WARNING: {n} is OpenAPI 3.2; features beyond 3.1 are not analysed", file=sys.stderr)
    pa = {norm_path(k): (k, v) for k, v in A.get("paths", {}).items()}
    pb = {norm_path(k): (k, v) for k, v in B.get("paths", {}).items()}
    for k, (orig, _) in pa.items():
        if k not in pb:
            add("breaking", f"paths.{orig}", "path removed (check for a likely rename)")
    for k, (orig, _) in pb.items():
        if k not in pa:
            add("safe", f"paths.{orig}", "path added")
    for k, (orig, ia) in pa.items():
        if k not in pb:
            continue
        ib = pb[k][1]
        for m in METHODS:
            oa, ob = ia.get(m), ib.get(m)
            loc = f"paths.{orig}.{m}"
            if oa and not ob:
                dep = oa.get("deprecated")
                add("risky" if dep else "breaking", loc, "operation removed" + (" (was deprecated; confirm sunset passed)" if dep else ""))
                continue
            if ob and not oa:
                add("safe", loc, "operation added")
                continue
            if not oa:
                continue
            if ob.get("deprecated") and not oa.get("deprecated"):
                add("safe", loc, "marked deprecated")
            qa, qb = params(A, ia, oa), params(B, ib, ob)
            for key, p in qb.items():
                if key not in qa:
                    add("breaking" if p.get("required") else "safe", f"{loc}.parameters.{key[0]}", f"new {'required' if p.get('required') else 'optional'} {key[1]} parameter")
                elif p.get("required") and not qa[key].get("required"):
                    add("breaking", f"{loc}.parameters.{key[0]}", "optional -> required")
            for key in qa:
                if key not in qb:
                    add("risky", f"{loc}.parameters.{key[0]}", "parameter removed (or renamed: check additions)")
            ra, rb = resolve(A, oa.get("requestBody", {})), resolve(B, ob.get("requestBody", {}))
            if rb and not ra:
                add("breaking" if rb.get("required") else "safe", loc + ".requestBody", "request body added")
            elif ra and rb:
                if rb.get("required") and not ra.get("required"):
                    add("breaking", loc + ".requestBody", "request body now required")
                ca, cb = ra.get("content", {}), rb.get("content", {})
                for mt in ca:
                    if mt not in cb:
                        add("breaking", f"{loc}.requestBody.{mt}", "request media type removed")
                    else:
                        schema_diff(A, B, ca[mt].get("schema", {}), cb[mt].get("schema", {}), f"{loc}.requestBody.{mt}", True)
            sa, sb = oa.get("responses", {}), ob.get("responses", {})
            for code in sa:
                if code not in sb:
                    add("breaking" if str(code).startswith("2") else "risky", f"{loc}.responses.{code}", "response code removed")
                else:
                    xa, xb = resolve(A, sa[code]), resolve(B, sb[code])
                    for mt in xa.get("content", {}):
                        if mt not in xb.get("content", {}):
                            add("breaking", f"{loc}.responses.{code}.{mt}", "response media type removed")
                        else:
                            schema_diff(A, B, xa["content"][mt].get("schema", {}), xb["content"][mt].get("schema", {}), f"{loc}.responses.{code}.{mt}", False)
                    for h in xa.get("headers", {}):
                        if h not in xb.get("headers", {}):
                            add("breaking", f"{loc}.responses.{code}.headers.{h}", "response header removed")
            for code in sb:
                if code not in sa:
                    add("risky", f"{loc}.responses.{code}", "new response code (clients may lack a handler)")
            sec_a = oa.get("security", A.get("security"))
            sec_b = ob.get("security", B.get("security"))
            na, nb = json.dumps(sec_a, sort_keys=True), json.dumps(sec_b, sort_keys=True)
            if na != nb:
                if not sec_a and sec_b:
                    add("breaking", loc + ".security", "auth added to open operation")
                elif sec_a and not sec_b:
                    add("safe", loc + ".security", "auth removed (security review item)")
                else:
                    add("risky", loc + ".security", "effective security changed: review alternatives and scopes manually")
    order = {"breaking": 0, "risky": 1, "safe": 2}
    out.sort(key=lambda x: order[x[0]])
    if "--json" in sys.argv:
        print(json.dumps([{"class": c, "location": l, "message": m} for c, l, m in out], indent=2))
    else:
        for c, l, m in out:
            print(f"{c.upper()} | {l} | {m}")
    bump = "MAJOR" if any(c == "breaking" for c, _, _ in out) else "MINOR" if any(c in ("risky", "safe") for c, _, _ in out) else "NONE"
    print(f"\nSuggested bump (info.version {A.get('info', {}).get('version')} -> {B.get('info', {}).get('version')}): {bump}", file=sys.stderr)
    sys.exit(1 if bump == "MAJOR" else 0)


main()
