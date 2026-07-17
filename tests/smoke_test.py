#!/usr/bin/env python3
"""EcoHash plugin smoke test — exercises the live OpenAI-compatible API.

Runs the same request shapes the Dify plugin uses, so a green run here is strong
evidence the plugin will work in Dify. Dev-only; not required at runtime.

Usage:
    export ECOHASH_API_KEY=eco_xxx
    python3 smoke_test.py                 # default base https://api.ecohash.com/v1
    ECOHASH_BASE_URL=... python3 smoke_test.py

Covers the acceptance matrix: credential check, 3 representative LLMs
(coding/agent, general chat, premium tier) in streaming + non-streaming, tool
calling, JSON output, usage tokens, embeddings, rerank, and a 401 error case.
No secrets are printed.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("ECOHASH_BASE_URL", "https://api.ecohash.com/v1").rstrip("/")
KEY = os.environ.get("ECOHASH_API_KEY", "")

CODING_MODEL = os.environ.get("ECOHASH_CODING_MODEL", "qwen3-coder-30b-a3b-instruct")
CHAT_MODEL = os.environ.get("ECOHASH_CHAT_MODEL", "llama-3.1-8b-instruct")
PREMIUM_MODEL = os.environ.get("ECOHASH_PREMIUM_MODEL", "GLM-5.2")
EMBED_MODEL = os.environ.get("ECOHASH_EMBED_MODEL", "jina-embeddings-v3")
RERANK_MODEL = os.environ.get("ECOHASH_RERANK_MODEL", "bge-reranker-v2-m3")

results = []


def record(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")


def _req(path, payload=None, key=KEY, method=None, stream=False):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Authorization", f"Bearer {key}")
    if data:
        req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req, timeout=120)


def test_credentials():
    try:
        resp = _req("/models")
        record("credential check (GET /v1/models, valid key)", resp.status == 200, f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        record("credential check (GET /v1/models, valid key)", False, f"HTTP {e.code}")


def test_bad_key_401():
    try:
        _req("/models", key="eco_invalid_key_for_test")
        record("error scenario: invalid key -> 401", False, "expected 401, got 200")
    except urllib.error.HTTPError as e:
        record("error scenario: invalid key -> 401", e.code == 401, f"HTTP {e.code}")


def test_chat_nonstream(model):
    try:
        resp = _req("/chat/completions", {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
            "max_tokens": 16, "stream": False,
        })
        body = json.loads(resp.read())
        usage = body.get("usage", {})
        content = body["choices"][0]["message"].get("content", "")
        ok = bool(content) and "total_tokens" in usage
        record(f"non-stream chat [{model}]", ok, f"usage={usage} content={content!r}")
    except urllib.error.HTTPError as e:
        record(f"non-stream chat [{model}]", False, f"HTTP {e.code}: {e.read()[:200]!r}")


def test_chat_stream(model):
    try:
        resp = _req("/chat/completions", {
            "model": model,
            "messages": [{"role": "user", "content": "Count to 3."}],
            "max_tokens": 32, "stream": True,
        }, stream=True)
        chunks = 0
        for raw in resp:
            line = raw.decode(errors="ignore").strip()
            if line.startswith("data:") and "[DONE]" not in line:
                chunks += 1
        record(f"streaming chat [{model}]", chunks > 0, f"{chunks} SSE chunks")
    except urllib.error.HTTPError as e:
        record(f"streaming chat [{model}]", False, f"HTTP {e.code}: {e.read()[:200]!r}")


def test_tool_calling(model):
    tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        },
    }
    # Some capable models decline under tool_choice=auto; retry with "required" to
    # confirm the capability rather than the model's momentary preference.
    for choice in ("auto", "required"):
        try:
            resp = _req("/chat/completions", {
                "model": model,
                "messages": [{"role": "user", "content": "What's the weather in Paris? Use the tool."}],
                "tools": [tool], "tool_choice": choice, "max_tokens": 128, "stream": False,
            })
            body = json.loads(resp.read())
            tool_calls = body["choices"][0]["message"].get("tool_calls")
            if tool_calls:
                record(f"tool/function calling [{model}]", True, f"tool_calls via tool_choice={choice}")
                return
        except urllib.error.HTTPError as e:
            record(f"tool/function calling [{model}]", False, f"HTTP {e.code}: {e.read()[:200]!r}")
            return
    record(f"tool/function calling [{model}]", False, "no tool_calls under auto or required")


def test_json_output(model):
    try:
        resp = _req("/chat/completions", {
            "model": model,
            "messages": [{"role": "user", "content": 'Return JSON {"ok": true}. Only JSON.'}],
            "response_format": {"type": "json_object"},
            "max_tokens": 64, "stream": False,
        })
        body = json.loads(resp.read())
        content = body["choices"][0]["message"].get("content", "")
        json.loads(content)
        record(f"JSON output [{model}]", True, f"content={content!r}")
    except Exception as e:
        record(f"JSON output [{model}]", False, str(e)[:200])


def test_embeddings(model):
    try:
        resp = _req("/embeddings", {"model": model, "input": ["hello world", "dify plugin"]})
        body = json.loads(resp.read())
        n = len(body.get("data", []))
        dim = len(body["data"][0]["embedding"]) if n else 0
        record(f"embeddings [{model}]", n == 2 and dim > 0, f"{n} vectors, dim={dim}, usage={body.get('usage')}")
    except urllib.error.HTTPError as e:
        record(f"embeddings [{model}]", False, f"HTTP {e.code}: {e.read()[:200]!r}")


def test_rerank(model):
    try:
        resp = _req("/rerank", {
            "model": model,
            "query": "What is the capital of the US?",
            "documents": ["Paris is in France.", "Washington, D.C. is the US capital."],
            "return_documents": True,
        })
        body = json.loads(resp.read())
        rr = body.get("results", [])
        record(f"rerank [{model}]", len(rr) > 0, f"{len(rr)} results, top_index={rr[0].get('index') if rr else None}")
    except urllib.error.HTTPError as e:
        record(f"rerank [{model}]", False, f"HTTP {e.code}: {e.read()[:200]!r} (verify /v1/rerank path)")


def main():
    if not KEY:
        print("ERROR: set ECOHASH_API_KEY (an eco_ key) first.")
        sys.exit(2)
    print(f"Base URL: {BASE}\n")
    test_credentials()
    test_bad_key_401()
    for m in (CODING_MODEL, CHAT_MODEL, PREMIUM_MODEL):
        test_chat_nonstream(m)
        test_chat_stream(m)
    test_tool_calling(CODING_MODEL)
    test_tool_calling(PREMIUM_MODEL)
    test_json_output(PREMIUM_MODEL)
    test_embeddings(EMBED_MODEL)
    test_rerank(RERANK_MODEL)

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n==== {passed}/{len(results)} checks passed ====")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
