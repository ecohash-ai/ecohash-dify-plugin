# EcoHash

Documentation in other languages: [Chinese (Simplified)](./readme/README_zh_Hans.md)

[EcoHash](https://ecohash.com) provides an OpenAI-compatible AI inference platform running on its own GPU cloud, with hosted LLM, text embedding, and rerank models that can be used directly from Dify.

## Features

- Provides LLM (chat & vision), text-embedding, and rerank models in Dify.
- Includes predefined LLM models such as GLM-5.2, GLM-5-Turbo, DeepSeek-V4-Flash, Kimi-K2.6, MiniMax-M2.7, Qwen3-235B-A22B, qwen3-coder-30b-a3b-instruct, and qwen3-vl-8b-instruct.
- Includes predefined text embedding models such as jina-embeddings-v3, jina-embeddings-v4, and the qwen3-embedding series, plus the bge-reranker-v2-m3 reranker for RAG pipelines.
- Supports predefined model and customizable model configuration — add any model id from the [EcoHash model catalog](https://docs.ecohash.com/platform-models/model-catalog) with just your API key.

## Setup

1. Install this plugin from the Dify Marketplace.
2. Get your API key from the [EcoHash console](https://docs.ecohash.com/getting-started/api-keys). Keys start with `eco_`.
3. In Dify, go to **Settings → Model Provider → EcoHash** and enter your API key.
4. Save the configuration.

The API key is the only credential required — the plugin connects to the EcoHash endpoint (`https://api.ecohash.com/v1`) automatically.

## Usage

Select **EcoHash** as the model provider in Dify, choose an available model, and use it in applications, agents, or workflows.

For RAG, choose an EcoHash embedding model (e.g. `jina-embeddings-v3`) and the `bge-reranker-v2-m3` reranker in your Knowledge Base settings.

## Privacy

This plugin sends the inputs required by the selected operation to the EcoHash API. API keys are stored by Dify and never written to logs. See [PRIVACY.md](./PRIVACY.md) and the [EcoHash privacy policy](https://ecohash.com/privacy) for details.

## Source & support

- Source repository: <https://github.com/ecohash-ai/ecohash-dify-plugin>
- Issues and questions: [GitHub Issues](https://github.com/ecohash-ai/ecohash-dify-plugin/issues) or the [EcoHash docs](https://docs.ecohash.com)
- Maintenance: the predefined model list is kept in sync with the live EcoHash catalog via `scripts/sync_models.py` (`--check` reports drift); catalog additions ship as patch releases of this plugin, and models not yet predefined can always be added immediately as customizable models.
