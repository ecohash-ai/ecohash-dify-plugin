# EcoHash

[EcoHash](https://ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-intro) provides RTX Pro 6000 GPU cloud infrastructure and OpenAI-compatible inference APIs for open models across text, vision, image, speech, and video. This Dify Model Provider plugin exposes chat and vision LLMs, text embeddings, and reranking.

## Install

From the Dify Marketplace: **[EcoHash](https://marketplace.dify.ai/plugin/ecohash/ecohash)**, published by `ecohash` as plugin id `ecohash/ecohash`. In Dify, open **Plugins → Marketplace**, search for EcoHash, and click Install.

To install without the Marketplace, download a `.difypkg` from [dist/](./dist) and use **Plugins → Install plugin → Local Package File** in Dify.

## Configure

1. Create an API key in the [EcoHash console](https://console.ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-console). Keys start with `eco_`. See [the key guide](https://docs.ecohash.com/getting-started/api-keys?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-apikey) if you need the walkthrough.
2. In Dify, go to **Settings → Model Provider → EcoHash** and paste the key.
3. Save.

The API key is the only credential. The plugin calls `https://api.ecohash.com/v1` for you.

## Models

Predefined models are kept in sync with the live EcoHash catalog. As of 2026-09-18 the plugin ships 14:

- **LLM (10)**: `qwen3.8-27b`, `qwen3.6-27b`, `qwen3.6-35b-a3b`, `qwen3.5-27b`, `qwen3.5-35b-a3b`, `qwen3-coder-30b-a3b-instruct`, `qwen3-vl-8b-instruct`, `qwen3-omni-30b-a3b-instruct`, `gpt-oss-20b`, `llama-3.1-8b-instruct`
- **Text embedding (3)**: `jina-embeddings-v3`, `jina-embeddings-v4`, `qwen3-embedding-0.6b`
- **Rerank (1)**: `bge-reranker-v2-m3`

Only models EcoHash hosts itself are predefined. Some catalog models are served through an external upstream provider and are left out of the predefined list. If your account has access to one, add it in Dify as a customizable model using its id from the [model catalog](https://docs.ecohash.com/platform-models/model-catalog?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-catalog).

## Usage

Select **EcoHash** as the model provider, pick a model, and use it in applications, agents, or workflows.

For RAG, choose an EcoHash embedding model such as `jina-embeddings-v3` together with the `bge-reranker-v2-m3` reranker in your Knowledge Base settings.

## Privacy

This plugin sends the inputs required by the selected operation to the EcoHash API. API keys are stored by Dify and never written to logs. See [PRIVACY.md](./PRIVACY.md) and the [EcoHash privacy policy](https://ecohash.com/privacy?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-privacy).

## Maintenance

`scripts/sync_models.py --check` reports drift between the predefined list and the live catalog and exits non-zero when they differ. Running it without `--check` writes YAML files for catalog models that are missing. Catalog additions ship as patch releases; anything not yet predefined can be used right away as a customizable model.

Version history is in [CHANGELOG.md](./CHANGELOG.md).

## Source and support

- Source: <https://github.com/ecohash-ai/ecohash-dify-plugin>
- Issues: [GitHub Issues](https://github.com/ecohash-ai/ecohash-dify-plugin/issues)
- Docs: [docs.ecohash.com](https://docs.ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-docs)
