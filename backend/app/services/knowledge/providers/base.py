from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """
    Common interface for all NEXUS LLM providers.
    """

    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict[str, Any],
    ) -> dict:
        """
        Generate a structured response from an LLM.
        """
        raise NotImplementedError