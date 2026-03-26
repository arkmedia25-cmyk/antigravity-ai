from abc import ABC, abstractmethod
from src.core.logging import get_logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self.logger.debug(f"Agent initialized: {name}")

    @abstractmethod
    def process(self, input_data: str, chat_id=None) -> str:
        """Process input and return a response.
        chat_id: Telegram chat ID — when provided, data is stored per-user.
        """
        pass
