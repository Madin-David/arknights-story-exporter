"""
Base classes for the modular parser system.

This module defines the core abstractions for the parser architecture:
- ParserContext: Shared context for all parsers
- LineParser: Abstract base class for all line parsers
- StatefulParser: Base class for parsers that maintain state
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from docx import Document


class ParserContext:
    """Shared context for all parsers.

    This context is passed to all parsers and provides access to:
    - The document being built
    - The DocumentAssembler instance
    - Shared state dictionary for inter-parser communication
    """

    def __init__(self):
        self.doc: Optional['Document'] = None
        self.assembler: Optional[Any] = None  # DocumentAssembler instance
        self.state: dict = {}  # Shared state dictionary

    def get_state(self, key: str, default=None):
        """Get a value from the shared state dictionary."""
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any):
        """Set a value in the shared state dictionary."""
        self.state[key] = value


class LineParser(ABC):
    """Abstract base class for all line parsers.

    Each parser is responsible for:
    1. Detecting if it can parse a line (can_parse)
    2. Parsing the line and updating the document (parse)
    3. Optional initialization and finalization hooks

    Parsers are executed in priority order (lower number = higher priority).
    """

    def __init__(self, enabled: bool = True, priority: int = 50):
        """Initialize the parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (lower = higher priority)
        """
        self.enabled = enabled
        self.priority = priority

    @abstractmethod
    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this parser can handle the given line.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this parser can handle the line
        """
        pass

    @abstractmethod
    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the line and update the document.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the line was successfully handled
        """
        pass

    def initialize(self, context: ParserContext):
        """Called once before parsing starts.

        Override this method to perform initialization tasks.

        Args:
            context: Shared parser context
        """
        pass

    def finalize(self, context: ParserContext):
        """Called once after all parsing is complete.

        Override this method to perform cleanup or finalization tasks.

        Args:
            context: Shared parser context
        """
        pass


class StatefulParser(LineParser):
    """Base class for parsers that maintain state.

    This class provides convenience methods for storing and retrieving
    parser-specific state in the shared context.
    """

    def __init__(self, enabled: bool = True, priority: int = 50):
        """Initialize the stateful parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (lower = higher priority)
        """
        super().__init__(enabled, priority)
        self.state_key = self.__class__.__name__ + "_state"

    def get_parser_state(self, context: ParserContext, default=None):
        """Get this parser's state from the context.

        Args:
            context: Shared parser context
            default: Default value if state doesn't exist

        Returns:
            The parser's state or default value
        """
        return context.get_state(self.state_key, default)

    def set_parser_state(self, context: ParserContext, value: Any):
        """Set this parser's state in the context.

        Args:
            context: Shared parser context
            value: The state value to store
        """
        context.set_state(self.state_key, value)
