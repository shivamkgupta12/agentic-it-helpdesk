import logging
from typing import Any

from openai import AzureOpenAI, OpenAIError

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class AzureOpenAIConfigError(RuntimeError):
    """Raised when Azure OpenAI configuration is missing or invalid."""


class AzureOpenAIService:
    """
    Small wrapper around Azure OpenAI.

    Phase 2 purpose:
    - Validate environment config.
    - Send a simple chat request.
    - Return model output.

    Later phases:
    - LangGraph agents will reuse this service.
    - RAG will reuse embeddings config.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._validate_config()

        self.client = AzureOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
        )

    def _validate_config(self) -> None:
        missing_values: list[str] = []

        if not self.settings.azure_openai_endpoint:
            missing_values.append("AZURE_OPENAI_ENDPOINT")

        if not self.settings.azure_openai_api_key:
            missing_values.append("AZURE_OPENAI_API_KEY")

        if not self.settings.azure_openai_api_version:
            missing_values.append("AZURE_OPENAI_API_VERSION")

        if not self.settings.azure_openai_chat_deployment:
            missing_values.append("AZURE_OPENAI_CHAT_DEPLOYMENT")

        if missing_values:
            missing = ", ".join(missing_values)
            raise AzureOpenAIConfigError(
                f"Missing Azure OpenAI configuration values: {missing}"
            )

    def generate_chat_response(
        self,
        user_message: str,
        system_message: str | None = None,
    ) -> str:
        """
        Sends a simple chat completion request to Azure OpenAI.

        Args:
            user_message:
                The employee's message.
            system_message:
                Optional system instruction.

        Returns:
            The assistant response text.
        """

        messages: list[dict[str, str]] = []

        messages.append(
            {
                "role": "system",
                "content": system_message
                or (
                    "You are an enterprise IT support assistant. "
                    "Give clear, practical, safe IT troubleshooting guidance. "
                    "Do not claim to perform admin actions, password resets, "
                    "permission changes, or ticket creation unless a tool has done it."
                ),
            }
        )

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=self.settings.azure_openai_chat_deployment,
                messages=messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )

            content = response.choices[0].message.content

            if not content:
                return "I could not generate a response. Please try again."

            return content

        except OpenAIError as exc:
            logger.exception("Azure OpenAI request failed")
            raise RuntimeError(f"Azure OpenAI request failed: {exc}") from exc

    def health_check(self) -> dict[str, Any]:
        """
        Lightweight config health check.

        This does not call Azure. It only confirms that the backend
        has the values needed to make an Azure OpenAI request.
        """

        return {
            "provider": "azure_openai",
            "endpoint_configured": bool(self.settings.azure_openai_endpoint),
            "api_key_configured": bool(self.settings.azure_openai_api_key),
            "api_version": self.settings.azure_openai_api_version,
            "chat_deployment": self.settings.azure_openai_chat_deployment,
            "embedding_deployment_configured": bool(
                self.settings.azure_openai_embedding_deployment
            ),
        }


def get_azure_openai_service() -> AzureOpenAIService:
    return AzureOpenAIService()