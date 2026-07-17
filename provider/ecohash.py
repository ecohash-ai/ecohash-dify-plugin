import logging

import httpx
from dify_plugin import ModelProvider
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://api.ecohash.com/v1"


class EcoHashProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials with a single authenticated GET /v1/models call.

        This performs no inference, so validation is free of model-invocation cost and
        does not depend on any individual model being available. Raises
        CredentialsValidateFailedError if the API key is missing or rejected.

        :param credentials: provider credentials, as defined in `provider_credential_schema`.
        """
        api_key = (credentials.get("api_key") or "").strip()
        if not api_key:
            raise CredentialsValidateFailedError("EcoHash API Key is required.")

        try:
            response = httpx.get(
                DEFAULT_ENDPOINT + "/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "X-EcoHash-Source": "dify-plugin",
                },
                timeout=15,
            )
        except httpx.HTTPError as ex:
            raise CredentialsValidateFailedError(
                f"Could not reach the EcoHash API to validate the key: {ex}"
            ) from ex

        if response.status_code in (401, 403):
            raise CredentialsValidateFailedError(
                f"Invalid or expired EcoHash API Key (HTTP {response.status_code})."
            )
        if response.status_code != 200:
            raise CredentialsValidateFailedError(
                f"EcoHash API returned HTTP {response.status_code} while validating the API Key."
            )
