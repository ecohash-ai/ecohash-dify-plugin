"""End-to-end test of the actual EcoHash plugin code against the live API."""
import importlib.util
import os

from dify_plugin.entities.model.message import UserPromptMessage

# plugin root = parent of this tests/ dir
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = os.environ["ECOHASH_API_KEY"]
CREDS = {"api_key": KEY}  # no endpoint_url -> plugin must default to production


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


llm_mod = load(BASE + "/models/llm/llm.py", "ec_llm")
emb_mod = load(BASE + "/models/text_embedding/text_embedding.py", "ec_emb")
rer_mod = load(BASE + "/models/rerank/rerank.py", "ec_rer")
prov_mod = load(BASE + "/provider/ecohash.py", "ec_prov")

llm = llm_mod.EcoHashLargeLanguageModel(model_schemas=[])
emb = emb_mod.EcoHashTextEmbeddingModel(model_schemas=[])
rer = rer_mod.EcoHashRerankModel(model_schemas=[])

ok = 0
total = 0


def check(name, cond, detail=""):
    global ok, total
    total += 1
    ok += 1 if cond else 0
    print(f"[{'PASS' if cond else 'FAIL'}] {name} — {detail}")


# 1. provider credential validation (the exact path Dify calls on save)
try:
    llm.validate_credentials("llama-3.1-8b-instruct", dict(CREDS))
    check("plugin LLM.validate_credentials (valid key)", True, "no error")
except Exception as e:
    check("plugin LLM.validate_credentials (valid key)", False, repr(e)[:200])

# 2. non-streaming chat through the plugin
try:
    r = llm._invoke("llama-3.1-8b-instruct", dict(CREDS),
                    [UserPromptMessage(content="Reply with exactly: OK")],
                    {"max_tokens": 16, "temperature": 0}, stream=False)
    content = r.message.content
    usage = getattr(r, "usage", None)
    check("plugin LLM non-stream", bool(content), f"content={content!r} total_tokens={getattr(usage,'total_tokens',None)}")
except Exception as e:
    check("plugin LLM non-stream", False, repr(e)[:200])

# 3. streaming chat through the plugin
try:
    gen = llm._invoke("llama-3.1-8b-instruct", dict(CREDS),
                      [UserPromptMessage(content="Count to three.")],
                      {"max_tokens": 64}, stream=True)
    pieces, last_usage = [], None
    for chunk in gen:
        d = chunk.delta
        if d.message and d.message.content:
            pieces.append(d.message.content)
        if getattr(d, "usage", None):
            last_usage = d.usage
    text = "".join(pieces)
    check("plugin LLM streaming", bool(text), f"text_len={len(text)} usage={getattr(last_usage,'total_tokens',None)}")
except Exception as e:
    check("plugin LLM streaming", False, repr(e)[:200])

# 4. embeddings through the plugin
try:
    er = emb._invoke("jina-embeddings-v3", dict(CREDS), ["hello world", "dify plugin"])
    dim = len(er.embeddings[0]) if er.embeddings else 0
    check("plugin embeddings", len(er.embeddings) == 2 and dim > 0,
          f"{len(er.embeddings)} vectors dim={dim} tokens={er.usage.tokens}")
except Exception as e:
    check("plugin embeddings", False, repr(e)[:200])

# 5. rerank through the plugin
try:
    rr = rer._invoke("bge-reranker-v2-m3", dict(CREDS),
                     "What is the capital of the US?",
                     ["Paris is in France.", "Washington, D.C. is the US capital."])
    top = rr.docs[0] if rr.docs else None
    check("plugin rerank", bool(rr.docs) and top.index == 1,
          f"{len(rr.docs)} docs top_index={getattr(top,'index',None)} score={getattr(top,'score',None):.3f}")
except Exception as e:
    check("plugin rerank", False, repr(e)[:200])

# 6. invalid key -> CredentialsValidateFailedError
try:
    llm.validate_credentials("llama-3.1-8b-instruct", {"api_key": "eco_bogus"})
    check("plugin invalid-key rejected", False, "no error raised")
except Exception as e:
    check("plugin invalid-key rejected", type(e).__name__.endswith("CredentialsValidateFailedError")
          or "Credential" in type(e).__name__, type(e).__name__)

print(f"\n==== plugin E2E: {ok}/{total} passed ====")
