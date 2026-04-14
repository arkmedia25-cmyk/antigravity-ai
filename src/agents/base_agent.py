from abc import ABC, abstractmethod
from src.core.logging import get_logger
from src.core.protocol import SwarmMessage


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self.logger.debug(f"Agent initialized: {name}")

    @abstractmethod
    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> SwarmMessage:
        """Process input and return a SwarmMessage.
        chat_id: Telegram chat ID — when provided, data is stored per-user.
        brand: The brand context (e.g., 'glowup', 'holisti').
        context: Memory/Conversation history provided by the orchestrator.
        """
        pass
