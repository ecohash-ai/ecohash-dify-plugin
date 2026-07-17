# EcoHash

其他语言：[English](../README.md)

[EcoHash](https://ecohash.com) 提供基于自有 GPU 云的 OpenAI 兼容 AI 推理平台，托管的 LLM、文本嵌入和重排序模型可以直接在 Dify 中使用。

## 功能

- 在 Dify 中提供 LLM（对话与视觉）、文本嵌入和重排序模型。
- 内置预定义 LLM 模型，如 GLM-5.2、DeepSeek-V4-Flash、Kimi-K2.6、Qwen3-235B-A22B、qwen3-coder-30b-a3b-instruct、qwen3-vl-8b-instruct。
- 内置预定义文本嵌入模型，如 jina-embeddings-v3、jina-embeddings-v4、qwen3-embedding 系列，以及用于 RAG 的 bge-reranker-v2-m3 重排序模型。
- 支持预定义模型和自定义模型两种配置方式——只需 API Key，即可添加 [EcoHash 模型目录](https://docs.ecohash.com/platform-models/model-catalog)中的任意模型 ID。

## 安装配置

1. 从 Dify Marketplace 安装本插件。
2. 在 [EcoHash 控制台](https://docs.ecohash.com/getting-started/api-keys)获取 API Key（以 `eco_` 开头）。
3. 在 Dify 中进入 **设置 → 模型供应商 → EcoHash**，填入 API Key。
4. 保存配置。

只需填写 API Key——插件会自动连接 EcoHash 端点（`https://api.ecohash.com/v1`），无需配置 Base URL。

## 使用

在 Dify 中选择 **EcoHash** 作为模型供应商，选取可用模型，即可在应用、Agent 或工作流中使用。

RAG 场景下，在知识库设置中选择 EcoHash 的嵌入模型（如 `jina-embeddings-v3`）和 `bge-reranker-v2-m3` 重排序模型。

## 隐私

本插件仅将所选操作必需的输入发送至 EcoHash API。API Key 由 Dify 存储，不会写入任何日志。详见 [PRIVACY.md](../PRIVACY.md) 与 [EcoHash 隐私政策](https://ecohash.com/privacy)。

## 源码与支持

- 源码仓库：<https://github.com/ecohash-ai/ecohash-dify-plugin>
- 问题反馈：[GitHub Issues](https://github.com/ecohash-ai/ecohash-dify-plugin/issues) 或 [EcoHash 文档](https://docs.ecohash.com)
