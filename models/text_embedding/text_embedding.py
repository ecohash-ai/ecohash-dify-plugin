from typing import Optional

from dify_plugin import OAICompatEmbeddingModel
from dify_plugin.entities.model import EmbeddingInputType
from dify_plugin.entities.model.text_embedding import TextEmbeddingResult

DEFAULT_ENDPOINT = "https://api.ecohash.com/v1"


class EcoHashTextEmbeddingModel(OAICompatEmbeddingModel):
    """EcoHash text embedding (OpenAI-compatible /v1/embeddings)."""

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials)
        super().validate_credentials(model, credentials)

    def _invoke(
        self,
        model: str,
        credentials: dict,
        texts: list[str],
        user: Optional[str] = None,
        input_type: EmbeddingInputType = EmbeddingInputType.DOCUMENT,
    ) -> TextEmbeddingResult:
        self._add_custom_parameters(credentials)
        return super()._invoke(model, credentials, texts, user, input_type)

    def get_num_tokens(self, model: str, credentials: dict, texts: list[str]) -> int:
        self._add_custom_parameters(credentials)
        return super().get_num_tokens(model, credentials, texts)

    @staticmethod
    def _add_custom_parameters(credentials: dict) -> None:
        credentials["endpoint_url"] = DEFAULT_ENDPOINT
