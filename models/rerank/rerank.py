from typing import Optional

import httpx
from dify_plugin.entities.model.rerank import RerankDocument, RerankResult
from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from dify_plugin.interfaces.model.rerank_model import RerankModel

DEFAULT_ENDPOINT = "https://api.ecohash.com/v1"


class EcoHashRerankModel(RerankModel):
    """EcoHash reranker (OpenAI-compatible /v1/rerank)."""

    def _invoke(
        self,
        model: str,
        credentials: dict,
        query: str,
        docs: list[str],
        score_threshold: Optional[float] = None,
        top_n: Optional[int] = None,
        user: Optional[str] = None,
    ) -> RerankResult:
        if len(docs) == 0:
            return RerankResult(model=model, docs=[])

        base_url = DEFAULT_ENDPOINT
        payload: dict = {
            "model": model,
            "query": query,
            "documents": docs,
            "return_documents": True,
        }
        if top_n is not None:
            payload["top_n"] = top_n

        response = httpx.post(
            base_url + "/rerank",
            json=payload,
            headers={
                "Authorization": f"Bearer {credentials.get('api_key')}",
                "X-EcoHash-Source": "dify-plugin",
            },
            timeout=60,
        )
        self._raise_invoke_error(response)
        results = response.json()

        rerank_documents: list[RerankDocument] = []
        for result in results.get("results", []):
            index = result["index"]
            document = result.get("document")
            if isinstance(document, dict):
                text = document.get("text", docs[index])
            elif isinstance(document, str):
                text = document
            else:
                text = docs[index]
            score = result.get("relevance_score", result.get("score", 0.0))
            if score_threshold is None or score >= score_threshold:
                rerank_documents.append(RerankDocument(index=index, text=text, score=score))

        return RerankResult(model=model, docs=rerank_documents)

    @staticmethod
    def _raise_invoke_error(response: httpx.Response) -> None:
        """Map HTTP error statuses to the matching InvokeError so Dify shows
        an accurate message (auth vs rate limit vs server error)."""
        status = response.status_code
        if status < 400:
            return
        detail = f"EcoHash rerank API returned HTTP {status}: {response.text[:200]}"
        if status in (401, 403):
            raise InvokeAuthorizationError(detail)
        if status == 429:
            raise InvokeRateLimitError(detail)
        if status >= 500:
            raise InvokeServerUnavailableError(detail)
        raise InvokeBadRequestError(detail)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        try:
            self._invoke(
                model=model,
                credentials=credentials,
                query="What is the capital of the United States?",
                docs=[
                    "Carson City is the capital city of the American state of Nevada.",
                    "Washington, D.C. is the capital of the United States.",
                ],
                score_threshold=None,
            )
        except InvokeError as ex:
            raise CredentialsValidateFailedError(str(ex))
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex))

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        return {
            InvokeConnectionError: [httpx.ConnectError, httpx.ConnectTimeout],
            InvokeServerUnavailableError: [httpx.RemoteProtocolError, httpx.ReadTimeout],
            InvokeRateLimitError: [],
            InvokeAuthorizationError: [],
            InvokeBadRequestError: [httpx.RequestError],
        }
