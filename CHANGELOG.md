# Changelog

## 0.0.3 (2026-09-18)

Added

- Predefined models `qwen3.8-27b`, `qwen3.6-27b`, `qwen3.6-35b-a3b`, `qwen3.5-27b`.

Removed

- Predefined models `gemma-4-31b-it`, `qwen2.5-7b-instruct`, `qwen3-embedding-4b` and
  `qwen3-embedding-8b`. They are no longer in the EcoHash catalog, so selecting them in
  Dify returned an error.
- Python bytecode files that had been committed by mistake.

Changed

- `scripts/sync_models.py` now predefines only models EcoHash hosts itself. A catalog
  entry without `hf_model_id` is served through an external upstream provider, and those
  are reported as skipped instead of missing. Accounts with access can still add them in
  Dify as customizable models.
- README now links the Marketplace listing directly, documents the local package install
  path, and lists the models the plugin actually ships.
- `manifest.yaml` now carries `repo`, `contact`, `network.domains` and
  `meta.minimum_dify_version`, and lists `version` before `meta` as the other Marketplace
  plugins do. The Marketplace review checks require the first two and read the version
  with a regular expression that takes the first `version:` key in the file.
- `httpx` now has an upper bound, matching the `dify_plugin` pin.

## 0.0.2 (2026-07-28)

- Dropped externally served models from the predefined list, keeping only self-hosted ones.
- Aligned the plugin copy with the EcoHash site.

## 0.0.1 (2026-07)

- First release: LLM (chat and vision), text embedding, and rerank models through one API key.
