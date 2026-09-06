from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class AgentTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(
        self,
        db: Session,
        workspace_id,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError