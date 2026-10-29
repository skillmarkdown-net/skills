#!/usr/bin/env python3
"""Static scan for common Stripe webhook mistakes.

Usage:
    python scripts/scan_webhook.py <file-or-directory> [...]

Scans .js .ts .mjs .py .rb .go .php files and prints candidate findings as
file:line: [severity] message. Hints only; confirm by reading the code.
No network access; standard library only.
"""
import os
import re
import sys

EXTS = {'.js', '.ts', '.mjs', '.py', '.rb', '.go', '.php'}
SKIP = {'node_modules', '.git', 'vendor', 'venv', '__pycache__'}

RULES = [
    (r'whsec_[A-Za-z0-9]{8,}', 'Critical', 'Hardcoded webhook secret'),
    (r'express\.json\(\)', 'High', 'express.json() present; ensure the webhook route uses express.raw and is mounted before it'),
    (r'JSON\.parse\(\s*req\.body|json\.loads\(\s*request\.(data|body)', 'High', 'Body parsed; verify raw body reaches the SDK verifier'),
    (r'tolerance\s*[=:,(]\s*(0|None|null|nil)\b', 'High', 'Tolerance disabled'),
    (r'tolerance\s*[=:,(]\s*\d{4,}', 'High', 'Very large tolerance (default is 300 seconds)'),
    (r'createHmac|hmac\.new|OpenSSL::HMAC|hash_hmac', 'Medium', 'Hand-rolled HMAC; use the SDK verifier or confirm constant-time compare and timestamp check'),
    (r'==\s*(sig|signature|expected)|(sig|signature|expected)\s*==', 'High', 'Possible non-constant-time signature compare'),
    (r'invoice\.payment_succeeded', 'Medium', 'Check this is not combined with invoice.paid for access grants'),
    (r'checkout\.session\.completed', 'Medium', 'Check payment_status == paid and async_payment_* handling'),
    (r'\.created\b.*(sort|order|>|<)', 'Low', 'Possible ordering by created; use event ids and fresh fetches'),
    (r'console\.log\(.*(req\.body|event\))|print\(.*(payload|event)\)', 'Low', 'Logging full payload may leak PII'),
    (r'(status\(|status_code\s*=\s*)(4\d\d)', 'Low', 'Check 4xx is only for bad signature or malformed payload'),
]


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        else:
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP]
                for f in files:
                    if os.path.splitext(f)[1] in EXTS:
                        yield os.path.join(root, f)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    count = 0
    for path in iter_files(argv[1:]):
        try:
            with open(path, encoding='utf-8', errors='replace') as fh:
                lines = fh.readlines()
        except OSError:
            continue
        text = ''.join(lines)
        for i, line in enumerate(lines, 1):
            for pat, sev, msg in RULES:
                if re.search(pat, line):
                    print(f'{path}:{i}: [{sev}] {msg}')
                    count += 1
        if re.search(r'stripe', text, re.I) and not re.search(r'constructEvent|construct_event|Webhook\.construct|ConstructEvent|Webhook::constructEvent|parseThinEvent', text) and re.search(r'webhook', text, re.I):
            print(f'{path}:1: [High] Mentions Stripe webhooks but no SDK signature verification call found')
            count += 1
        if re.search(r'stripe', text, re.I) and not re.search(r'event\.id|event\[.id.\]|event_id|event\.Id', text) and re.search(r'webhook', text, re.I):
            print(f'{path}:1: [Medium] No event id use found; check idempotency')
            count += 1
    print(f'{count} candidate finding(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
