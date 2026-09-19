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
| Reinstall the exact published artifact `dist/ecohash-0.0.3.difypkg` (sha256 `2c3bf840…`, built from commit be608cc) | installed, credentials accepted, 14 models exposed |
| Chat through a Dify app on that artifact, `qwen3-coder-30b-a3b-instruct` | answered; 28 tokens, $0.0000034, 0.245 s |
| Marketplace review checks, run locally from `langgenius/dify-marketplace-toolkit` | 12 of 13 pass; see the note below on `check-version-update` |

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
- `check-version-update` in the Marketplace toolkit reads the plugin version with
  `^\s*version\s*:` and takes the first match in the file. Our manifest listed `meta`
  first, so `meta.runner.version` (`3.12`) was read as the plugin version. The key order
  is fixed here, and eight other published plugins were checked to confirm the
  conventional order puts `version` first. The check still fails on this submission
  because the comparison reads the same field out of the already published 0.0.1 and
  0.0.2 packages, which cannot be changed from our side.

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
