from abc import ABC, abstractmethod


class Command(ABC):
    intent: str = ""

    @abstractmethod
    def execute(self, entities: dict, sc) -> str | None:
        """Execute the command. Return a response string or None to use the LLM response."""
