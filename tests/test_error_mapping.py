"""Offline tests for HTTP error mapping — no API key or network needed.

Simulates 401/429/500/400 responses and asserts each surfaces as the correct
InvokeError type (so Dify shows rate-limit/server errors instead of
"Incorrect model credentials").

    python3 tests/test_error_mapping.py
"""
import importlib.util
import os

import httpx
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rer_mod = load(BASE + "/models/rerank/rerank.py", "ec_rer_test")
prov_mod = load(BASE + "/provider/ecohash.py", "ec_prov_test")

rer = rer_mod.EcoHashRerankModel(model_schemas=[])

ok = 0
total = 0


def check(name, cond, detail=""):
    global ok, total
    total += 1
    ok += 1 if cond else 0
    print(f"[{'PASS' if cond else 'FAIL'}] {name} — {detail}")


def fake_response(status, body=b'{"error":"simulated"}'):
    return httpx.Response(status_code=status, content=body)


# --- rerank: HTTP status -> InvokeError type ---
RERANK_CASES = [
    (401, InvokeAuthorizationError),
    (403, InvokeAuthorizationError),
    (429, InvokeRateLimitError),
    (500, InvokeServerUnavailableError),
    (503, InvokeServerUnavailableError),
    (400, InvokeBadRequestError),
]

real_post = httpx.post
for status, expected in RERANK_CASES:
    httpx.post = lambda *a, _s=status, **k: fake_response(_s)
    try:
        rer._invoke("bge-reranker-v2-m3", {"api_key": "eco_test"}, "q", ["d1", "d2"])
        check(f"rerank HTTP {status}", False, "no error raised")
    except Exception as e:
        check(
            f"rerank HTTP {status} -> {expected.__name__}",
            type(e) is expected,
            f"got {type(e).__name__}: {e}"[:120],
        )
    finally:
        httpx.post = real_post

# 200 still parses normally
httpx.post = lambda *a, **k: fake_response(
    200, b'{"results":[{"index":1,"relevance_score":0.9},{"index":0,"relevance_score":0.1}]}'
)
try:
    result = rer._invoke("bge-reranker-v2-m3", {"api_key": "eco_test"}, "q", ["d1", "d2"])
    check("rerank HTTP 200 parses", len(result.docs) == 2, f"{len(result.docs)} docs")
except Exception as e:
    check("rerank HTTP 200 parses", False, repr(e)[:120])
finally:
    httpx.post = real_post

# timeout/connection exceptions route through the framework mapping
mapping = rer._invoke_error_mapping
check(
    "rerank timeout mapping",
    httpx.ReadTimeout in mapping[InvokeServerUnavailableError]
    and httpx.ConnectTimeout in mapping[InvokeConnectionError],
    "ReadTimeout->ServerUnavailable, ConnectTimeout->Connection",
)
check(
    "rerank no blanket HTTPStatusError->auth mapping",
    httpx.HTTPStatusError not in mapping[InvokeAuthorizationError],
    str(mapping[InvokeAuthorizationError]),
)

# --- provider: GET /v1/models validation, no inference ---
prov = prov_mod.EcoHashProvider.__new__(prov_mod.EcoHashProvider)

real_get = httpx.get
PROVIDER_CASES = [(401, True), (403, True), (500, True), (200, False)]
for status, should_fail in PROVIDER_CASES:
    httpx.get = lambda *a, _s=status, **k: fake_response(_s, b'{"data":[]}')
    try:
        prov.validate_provider_credentials({"api_key": "eco_test"})
        check(f"provider validate HTTP {status}", not should_fail, "accepted")
    except CredentialsValidateFailedError as e:
        check(f"provider validate HTTP {status}", should_fail, str(e)[:100])
    except Exception as e:
        check(f"provider validate HTTP {status}", False, f"wrong error {type(e).__name__}")
    finally:
        httpx.get = real_get

try:
    prov.validate_provider_credentials({"api_key": ""})
    check("provider validate empty key", False, "accepted empty key")
except CredentialsValidateFailedError as e:
    check("provider validate empty key", True, str(e)[:80])

print(f"\n{ok}/{total} passed")
raise SystemExit(0 if ok == total else 1)
