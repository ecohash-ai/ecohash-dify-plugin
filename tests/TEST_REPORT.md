# EcoHash Plugin — Test Report

> Status legend: ✅ pass · ❌ fail · ⚠️ partial/known-limitation · ⏳ pending.
> Reproduce: `export ECOHASH_API_KEY=eco_xxx` then
> `python3 tests/smoke_test.py` (raw API) and `python3 tests/e2e_plugin.py` (plugin code).

## Environment

| Field | Value |
|-------|-------|
| Plugin version | 0.0.1 |
| Dify plugin SDK | dify_plugin 0.9.1 |
| Dify plugin CLI | 0.6.3 (package build) |
| Dify Cloud version | ⏳ pending (needs a Cloud workspace install) |
| Dify self-hosted version | ✅ 1.16.0-rc1 (docker compose, local) |
| API base URL | https://api.ecohash.com/v1 |
| Test date | 2026-07-16 |
| Method | Live API smoke test + plugin-code E2E harness |

## Install & configure

| Step | Result |
|------|--------|
| `.difypkg` builds & passes CLI schema validation | ✅ (25 KB, 38 files) |
| All 22 YAMLs parse; all SDK symbols resolve; modules import | ✅ |
| Plugin `validate_credentials` accepts a valid `eco_` key | ✅ (via GET /v1/models, HTTP 200) |
| Plugin `validate_credentials` rejects a bad key | ✅ (raises CredentialsValidateFailedError) |
| Self-hosted install: `.difypkg` upload + install + venv build + runtime ready | ✅ (plugin_daemon: `Installed model: ecohash`, `local runtime ready`) |
| Provider registered in workspace | ✅ `ecohash/ecohash/ecohash` |
| Models exposed in Dify | ✅ 18 total — llm:12, text-embedding:5, rerank:1 |
| Live in-Dify calls (Dify→plugin_daemon→plugin→EcoHash) | ✅ GLM-5.2, llama-3.1-8b-instruct (llm), jina-embeddings-v3 (embedding), bge-reranker-v2-m3 (rerank) all `result: success` |
| Dify Cloud UI install | ⏳ pending (needs a Cloud workspace) |
| New-workspace install→config→first call < 10 min | ⏳ pending (Cloud) |

## Representative model calls

Verified live via `smoke_test.py` (raw API) **and** `e2e_plugin.py` (through the plugin's
own `OAICompat` subclasses).

| Model | Type | Non-stream | Stream | Tool calling | JSON output | Usage tokens |
|-------|------|-----------|--------|--------------|-------------|--------------|
| qwen3-coder-30b-a3b-instruct | LLM (coding/agent) | ✅ (`OK`, 15 tok) | ✅ (11 chunks) | ✅ (via `tool_choice=required`) | ✅ | ✅ |
| llama-3.1-8b-instruct | LLM (general) | ✅ (`OK`, 17 tok) | ✅ (11 chunks) | n/a | ✅ | ✅ |
| GLM-5.2 | LLM (premium/agent, reasoning) | ✅ (usage incl. reasoning_tokens) | ✅ | ✅ (via `tool_choice=auto`) | ✅ (`{"ok": true}`) | ✅ |
| jina-embeddings-v3 | Embedding | ✅ (2 vectors, dim 1024) | n/a | n/a | n/a | ✅ (10 tok) |
| bge-reranker-v2-m3 | Rerank | ✅ (top_index=1, score 0.999) | n/a | n/a | n/a | n/a |

**Plugin-code E2E (`e2e_plugin.py`): 6/6 passed** — validate_credentials, non-stream,
streaming, embeddings, rerank, invalid-key rejection, all through the plugin classes with
`endpoint_url` defaulted to production.

### Capability tag verification (all feature tags confirmed live)

- **Tool/function calling** — all 4 `agent_capable` models emit valid `tool_calls`:
  DeepSeek-V4-Flash, GLM-5.2, Kimi-K2.6 under `tool_choice=auto`; qwen3-coder-30b-a3b
  under `tool_choice=required` (declines under `auto`, but capable).
- **Vision** — all 5 `llm_vision` models correctly describe a 256px test image:
  qwen3-vl-8b-instruct, qwen3-omni-30b-a3b-instruct, gemma-4-31b-it, qwen3.5-35b-a3b,
  Kimi-K2.6.

## Error scenarios

| Scenario | Expected | Observed |
|----------|----------|----------|
| Invalid API key | 401, clear message | ✅ 401 → CredentialsValidateFailedError |
| Rate limit (429) | 429, clear message | ⏳ not triggered this run; mapped by SDK to InvokeRateLimitError |
| Timeout | connection/server error, retryable | ⏳ not triggered; httpx timeout + SDK mapping in place |
| 5xx | server-unavailable, retryable | ⏳ not triggered; mapped to InvokeServerUnavailableError |
| Insufficient credit (402) | 402, clear message | ⏳ not triggered (funded test key) |

## Known limitations

- Context sizes for the MoE models the catalog reports with `null` `context_length`
  (GLM-5.2, Kimi-K2.6, DeepSeek-V4-Flash, Qwen3-235B-A22B, qwen3.5-35b-a3b, qwen3-omni)
  use a conservative provisional default of 32768. The authenticated `GET /v1/models` also
  omits context for these, so this cannot be tightened from the API today.
- STT/TTS and image/video categories are served by EcoHash but not included in this
  model-provider version.
- In-Dify UI install smoke tests (Dify Cloud + self-hosted) are pending a running instance.
