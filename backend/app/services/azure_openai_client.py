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

        GPT-5 / reasoning-style deployments use:
        - developer message instead of system message
        - max_completion_tokens instead of max_tokens
        - no temperature/top_p
        """

        deployment_name = self.settings.azure_openai_chat_deployment.lower()

        is_reasoning_model = (
            deployment_name.startswith("gpt-5")
            or deployment_name.startswith("o1")
            or deployment_name.startswith("o3")
            or deployment_name.startswith("o4")
        )

        instruction = system_message or (
            "You are an enterprise IT support assistant. "
            "Give a short, practical answer. "
            "Do not perform admin actions. "
            "Do not create tickets unless a tool has done it. "
            "For this response, provide only 3 concise troubleshooting steps."
        )

        if is_reasoning_model:
            messages: list[dict[str, str]] = [
                {
                    "role": "developer",
                    "content": instruction,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": instruction,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ]

        request_payload: dict[str, Any] = {
            "model": self.settings.azure_openai_chat_deployment,
            "messages": messages,
        }

        if is_reasoning_model:
            request_payload["max_completion_tokens"] = self.settings.llm_max_tokens
            request_payload["reasoning_effort"] = "minimal"
        else:
            request_payload["temperature"] = self.settings.llm_temperature
            request_payload["max_tokens"] = self.settings.llm_max_tokens

        try:
            response = self.client.chat.completions.create(**request_payload)

            choice = response.choices[0]
            content = choice.message.content
            finish_reason = choice.finish_reason

            logger.info("Azure OpenAI finish_reason: %s", finish_reason)
            logger.info("Azure OpenAI usage: %s", response.usage)

            if not content:
                return (
                    "Azure OpenAI returned an empty visible response. "
                    f"finish_reason={finish_reason}. "
                    f"usage={response.usage}. "
                    "Try increasing LLM_MAX_TOKENS or use a standard chat deployment "
                    "such as gpt-4o-mini for this project."
                )

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