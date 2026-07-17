import logging

from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)


class EcoHashProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials.

        Delegates to the LLM model's credential validation, which performs a lightweight
        authenticated call against EcoHash's OpenAI-compatible endpoint. Raises
        CredentialsValidateFailedError if the API key is missing or rejected.

        :param credentials: provider credentials, as defined in `provider_credential_schema`.
        """
        try:
            model_instance = self.get_model_instance(ModelType.LLM)
            if isinstance(model_instance, type):
                model_instance = model_instance(model_schemas=self.provider_schema.models)
            # A low-cost, always-on model used only to prove the key is valid.
            model_instance.validate_credentials(
                model="llama-3.1-8b-instruct", credentials=credentials
            )
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception("%s credentials validate failed", self.get_provider_schema().provider)
            raise ex
