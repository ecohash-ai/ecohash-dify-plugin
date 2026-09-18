#!/usr/bin/env python3
"""Sync predefined model YAMLs with the live EcoHash catalog.

The EcoHash catalog (GET /platform/models, public) is the source of truth for
which models this plugin should predefine. This script keeps models/*/ in sync:

    python3 scripts/sync_models.py --check   # report drift, exit 1 if any (CI-friendly)
    python3 scripts/sync_models.py           # generate YAMLs for missing models

Only Dify model-provider categories are synced: llm / llm_vision -> models/llm,
embedding -> models/text_embedding, reranker -> models/rerank. Image, video and
speech models are out of scope for a Dify model provider and are skipped.

Only self-hosted models are predefined. A catalog entry with no hf_model_id is
served through an external upstream provider; redistributing those under our own
plugin needs the upstream reseller terms and each model license cleared first, so
they are skipped here. Users who have access can still add them in Dify through
the customizable-model form.

Generated YAMLs take context size and pricing from the catalog; when the catalog
has no context_length, a conservative default (32768 for LLM, 8192 otherwise) is
used — adjust by hand if the served context differs. Dev-only; excluded from the
plugin package via .difyignore.
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

CATALOG_URL = "https://api.ecohash.com/platform/models"
ROOT = Path(__file__).resolve().parent.parent

CATEGORY_DIRS = {
    "llm": "llm",
    "llm_vision": "llm",
    "embedding": "text_embedding",
    "reranker": "rerank",
}

DEFAULT_LLM_CONTEXT = 32768
DEFAULT_EMBEDDING_CONTEXT = 8192
DEFAULT_RERANK_CONTEXT = 8192

LLM_TEMPLATE = """\
model: {model_id}
label:
  en_US: {label}
  zh_Hans: {label}
model_type: llm
{features}model_properties:
  mode: chat
  context_size: {context_size}
parameter_rules:
  - name: temperature
    use_template: temperature
  - name: top_p
    use_template: top_p
  - name: max_tokens
    use_template: max_tokens
    min: 1
    max: {max_tokens}
    default: 1024
  - name: frequency_penalty
    use_template: frequency_penalty
pricing:
  input: "{input_price}"
  output: "{output_price}"
  unit: "0.000001"
  currency: USD
"""

EMBEDDING_TEMPLATE = """\
model: {model_id}
label:
  en_US: {label}
  zh_Hans: {label}
model_type: text-embedding
model_properties:
  context_size: {context_size}
  max_chunks: 1
pricing:
  input: "{input_price}"
  unit: "0.000001"
  currency: USD
"""

RERANK_TEMPLATE = """\
model: {model_id}
label:
  en_US: {label}
  zh_Hans: {label}
model_type: rerank
model_properties:
  context_size: {context_size}
pricing:
  input: "{input_price}"
  unit: "0.000001"
  currency: USD
"""


def yaml_filename(model_id: str) -> str:
    return model_id.lower().replace(".", "-") + ".yaml"


def fmt_price(value) -> str:
    return f"{value:g}" if value is not None else "0"


def render(entry: dict) -> str:
    model_id = entry["model_id"]
    label = entry.get("display_name") or model_id
    category = entry["category"]
    input_price = fmt_price(entry.get("input_price_per_1m_tokens"))

    if category in ("llm", "llm_vision"):
        context_size = entry.get("context_length") or DEFAULT_LLM_CONTEXT
        features = ["agent-thought", "tool-call", "multi-tool-call", "stream-tool-call"] if entry.get("agent_capable") else []
        if category == "llm_vision":
            features.append("vision")
        features_block = ""
        if features:
            features_block = "features:\n" + "".join(f"  - {f}\n" for f in features)
        return LLM_TEMPLATE.format(
            model_id=model_id,
            label=label,
            features=features_block,
            context_size=context_size,
            max_tokens=min(context_size, 32768),
            input_price=input_price,
            output_price=fmt_price(entry.get("output_price_per_1m_tokens")),
        )
    if category == "embedding":
        return EMBEDDING_TEMPLATE.format(
            model_id=model_id,
            label=label,
            context_size=entry.get("context_length") or DEFAULT_EMBEDDING_CONTEXT,
            input_price=input_price,
        )
    return RERANK_TEMPLATE.format(
        model_id=model_id,
        label=label,
        context_size=entry.get("context_length") or DEFAULT_RERANK_CONTEXT,
        input_price=input_price,
    )


def existing_models(model_dir: Path) -> dict:
    """Map model id -> yaml path for every predefined model in a directory."""
    result = {}
    for path in sorted(model_dir.glob("*.yaml")):
        if path.name == "_position.yaml":
            continue
        for line in path.read_text().splitlines():
            if line.startswith("model:"):
                result[line.split(":", 1)[1].strip()] = path
                break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift and exit 1 without writing")
    args = parser.parse_args()

    with urllib.request.urlopen(CATALOG_URL, timeout=30) as resp:
        catalog = json.load(resp)

    wanted = {}  # model_id -> catalog entry
    skipped_external = []
    for entry in catalog:
        if entry.get("status") != "active":
            continue
        if entry["category"] not in CATEGORY_DIRS:
            continue
        if not entry.get("hf_model_id"):
            skipped_external.append(entry["model_id"])
            continue
        if True:
            wanted[entry["model_id"]] = entry

    drift = False
    for model_id, entry in sorted(wanted.items()):
        model_dir = ROOT / "models" / CATEGORY_DIRS[entry["category"]]
        if model_id in existing_models(model_dir):
            continue
        drift = True
        if args.check:
            print(f"MISSING  {model_dir.relative_to(ROOT)}/{yaml_filename(model_id)}  ({model_id})")
            continue
        yaml_path = model_dir / yaml_filename(model_id)
        yaml_path.write_text(render(entry))
        position = model_dir / "_position.yaml"
        position.write_text(position.read_text().rstrip("\n") + f"\n- {model_id}\n")
        print(f"CREATED  {yaml_path.relative_to(ROOT)}")

    if skipped_external:
        print("SKIPPED  %d externally served model(s) (no hf_model_id): %s"
              % (len(skipped_external), ", ".join(sorted(skipped_external))))
    for dir_name in set(CATEGORY_DIRS.values()):
        model_dir = ROOT / "models" / dir_name
        for model_id, path in existing_models(model_dir).items():
            if model_id not in wanted:
                drift = True
                print(f"ORPHAN   {path.relative_to(ROOT)}  ({model_id} not in catalog — remove by hand)")

    if not drift:
        print(f"OK: all {len(wanted)} catalog models are predefined")
    return 1 if (drift and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
