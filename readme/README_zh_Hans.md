# EcoHash

[EcoHash](https://ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-intro-zh) 提供 RTX Pro 6000 GPU 云与 OpenAI 兼容的推理 API，覆盖文本、视觉、图像、语音和视频的开源模型。本 Dify 模型供应商插件提供对话与视觉 LLM、文本嵌入和重排序能力。

## 安装

从 Dify Marketplace 安装：**[EcoHash](https://marketplace.dify.ai/plugin/ecohash/ecohash)**，发布者 `ecohash`，插件 id `ecohash/ecohash`。在 Dify 中打开 **插件 → Marketplace**，搜索 EcoHash 并安装。

若不经 Marketplace 安装，可从 [dist/](../dist) 下载 `.difypkg`，在 Dify 中通过 **插件 → 安装插件 → 本地插件包** 安装。

## 配置

1. 在 [EcoHash 控制台](https://console.ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-console-zh)创建 API Key，密钥以 `eco_` 开头。步骤见[密钥文档](https://docs.ecohash.com/getting-started/api-keys?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-apikey-zh)。
2. 在 Dify 中进入 **设置 → 模型供应商 → EcoHash**，填入 API Key。
3. 保存。

API Key 是唯一需要的凭据，插件会自动连接 `https://api.ecohash.com/v1`。

## 模型

预定义模型与 EcoHash 线上目录保持同步。截至 2026-09-18 共 14 个：

- **LLM（10）**：`qwen3.8-27b`、`qwen3.6-27b`、`qwen3.6-35b-a3b`、`qwen3.5-27b`、`qwen3.5-35b-a3b`、`qwen3-coder-30b-a3b-instruct`、`qwen3-vl-8b-instruct`、`qwen3-omni-30b-a3b-instruct`、`gpt-oss-20b`、`llama-3.1-8b-instruct`
- **文本嵌入（3）**：`jina-embeddings-v3`、`jina-embeddings-v4`、`qwen3-embedding-0.6b`
- **重排序（1）**：`bge-reranker-v2-m3`

仅 EcoHash 自托管的模型会进入预定义列表。目录中由外部上游供应商提供的模型不在其中；如果你的账号有权限，可在 Dify 中以自定义模型方式填入其模型 id，id 见[模型目录](https://docs.ecohash.com/platform-models/model-catalog?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-catalog-zh)。

## 使用

在 Dify 中选择 **EcoHash** 作为模型供应商，选定模型后即可用于应用、Agent 与工作流。

做 RAG 时，在知识库设置中选择 EcoHash 的嵌入模型（如 `jina-embeddings-v3`）配合 `bge-reranker-v2-m3` 重排序模型。

## 隐私

插件只向 EcoHash API 发送所选操作需要的输入内容。API Key 由 Dify 保存，不会写入日志。详见 [PRIVACY.md](../PRIVACY.md) 与 [EcoHash 隐私政策](https://ecohash.com/privacy?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-privacy-zh)。

## 维护

`scripts/sync_models.py --check` 会比对预定义列表与线上目录，有差异时以非零码退出；不带 `--check` 运行会为缺失的模型生成 YAML。目录新增的模型以补丁版本发布；尚未预定义的模型可随时以自定义模型方式使用。

版本历史见 [CHANGELOG.md](../CHANGELOG.md)。

## 源码与支持

- 源码：<https://github.com/ecohash-ai/ecohash-dify-plugin>
- 问题反馈：[GitHub Issues](https://github.com/ecohash-ai/ecohash-dify-plugin/issues)
- 文档：[docs.ecohash.com](https://docs.ecohash.com?utm_source=github&utm_medium=referral&utm_campaign=devrel&utm_content=dify-plugin-docs-zh)
