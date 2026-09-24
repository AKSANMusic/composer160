"""Abstract base class for AI music generator prompt translators."""

from abc import ABC, abstractmethod
from typing import Any

from composer160.core.vector import ParameterVector


class GeneratorTranslator(ABC):
    """Abstract interface defining prompt generation from a ParameterVector."""

    @abstractmethod
    def translate(self, vec: ParameterVector, lyrics: str | None = None) -> Any:
        """Translate a ParameterVector into generator-specific prompt outputs.

        Args:
            vec: The source ParameterVector.
            lyrics: Optional raw or structured lyrics string.

        Returns:
            Generator-specific output dataclass.
        """
        pass
