import json
from typing import Any

import requests

from app.services.knowledge.providers.base import (
    BaseLLMProvider,
)


class OllamaProvider(BaseLLMProvider):
    """
    Local LLM provider using Ollama.

    No external API or paid service is required.
    """

    BASE_URL = "http://localhost:11434"

    def __init__(
        self,
        model: str = "qwen3:1.7b",
    ) -> None:
        self.model = model

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict[str, Any],
    ) -> dict:
        """
        Generate structured JSON using a local Ollama model.
        """

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "format": output_schema,
            "options": {
                "temperature": 0,
            },
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/api/chat",
                json=payload,
                timeout=300,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                "Could not connect to Ollama. "
                "Make sure Ollama is running."
            ) from exc

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama returned HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        message = data.get("message", {})
        content = message.get("content")

        if not content:
            raise RuntimeError(
                "Ollama returned no model content."
            )

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc