# End to end verification

What was run, on which versions, and what came back. Redo it with the commands below
when the plugin or the catalog changes.

## 0.0.3, 2026-09-18

Environment

- Dify 1.17.1, self-hosted with the official `docker/docker-compose.yaml`, 15 services
- Plugin 0.0.3, built with dify-plugin CLI v0.6.10, installed as a local package
- EcoHash API `https://api.ecohash.com/v1`, catalog read the same day
- API keys are redacted below and were never written to the repo

Results

| Step | Result |
| --- | --- |
| Install 0.0.2 from Marketplace (`ecohash/ecohash`) | success in under 5 s, `source=marketplace` |
| Credential validate and save | `result: success`, provider status `active` |
| Chat, `qwen3-coder-30b-a3b-instruct` | answered; 31 prompt + 32 completion tokens, $0.0000127, 0.49 s |
| Knowledge base index, `jina-embeddings-v3` | document indexed |
| Retrieval with rerank, `bge-reranker-v2-m3` | 1 hit, score 0.8912 |
| Install 0.0.3 from local package | success, `source=package` |
| Model list exposed by 0.0.3 | 14 models: 10 LLM, 3 embedding, 1 rerank |
| Chat, `qwen3.8-27b` (new in 0.0.3) | answered; 85 tokens, $0.0000339, 0.57 s |
| Chat, `qwen3.6-35b-a3b` (new in 0.0.3) | answered; 55 tokens, 0.38 s |
| Reinstall the exact published artifact `dist/ecohash-0.0.3.difypkg` (sha256 `78eab19e…`, built from commit 9d5c8f1) | installed, credentials accepted, 14 models exposed |
| Chat through a Dify app on that artifact, `qwen3-coder-30b-a3b-instruct` | answered; 25 prompt + 3 completion tokens, $0.0000034, 0.25 s |

Findings

- Published 0.0.2 still lists `qwen2.5-7b-instruct`, which the catalog no longer serves.
  Selecting it in Dify fails. 0.0.3 removes it along with three other delisted models.
- A default Dify deployment rejects local packages with `bad signature` because
  `FORCE_VERIFYING_SIGNATURE` defaults to true. Marketplace installs are unaffected.
  The README documents the setting for anyone installing a local build.
- `qwen3.6-35b-a3b` returns `<think>` reasoning blocks in its answer. Dify renders them
  as plain text today.
- The shipped package carries runtime files, the READMEs, the licence, the privacy
  policy and the changelog. `.difyignore` keeps `.gitignore`, `docs/`, `tests/`,
  `scripts/` and `dist/` out of it.

Known limits

- One workspace, one region, low request volume. This checks that the path works, not
  how it behaves under load.
- Run from a host in the same region as the API. Latency from a distant network is
  dominated by round trip time.

## How to repeat it

```bash
# 1. clean Dify
git clone --depth 1 -b 1.17.1 https://github.com/langgenius/dify.git && cd dify/docker
cp .env.example .env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -base64 42)|" .env   # empty by default
docker compose up -d

# 2. build the plugin package
curl -sL -o dify-cli https://github.com/langgenius/dify-plugin-daemon/releases/download/0.6.10/dify-plugin-linux-amd64
chmod +x dify-cli && ./dify-cli plugin package /path/to/ecohash-dify-plugin -o ecohash-0.0.3.difypkg

# 3. install it, set FORCE_VERIFYING_SIGNATURE=false first for a local package,
#    then configure the API key in Settings -> Model Provider -> EcoHash and send a message.
```
