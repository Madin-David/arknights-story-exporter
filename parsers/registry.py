"""
Parser registry for managing and executing parsers.

The ParserRegistry maintains a collection of parsers and provides
methods for registering, enabling/disabling, and executing them.
"""

from typing import List, Optional, Type
from parsers.base import LineParser, ParserContext


class ParserRegistry:
    """Registry for managing all parsers.

    The registry maintains a list of parsers sorted by priority and
    provides methods for:
    - Registering and unregistering parsers
    - Enabling and disabling parsers
    - Initializing and finalizing all parsers
    - Parsing lines with the registered parsers
    """

    def __init__(self):
        """Initialize the parser registry."""
        self.parsers: List[LineParser] = []
        self.context = ParserContext()

    def register(self, parser: LineParser):
        """Register a parser.

        The parser will be inserted in priority order (lower number = higher priority).

        Args:
            parser: The parser to register
        """
        self.parsers.append(parser)
        # Sort by priority (lower number = higher priority)
        self.parsers.sort(key=lambda p: p.priority)

    def unregister(self, parser_class: Type[LineParser]):
        """Unregister all parsers of a given class.

        Args:
            parser_class: The parser class to unregister
        """
        self.parsers = [p for p in self.parsers if not isinstance(p, parser_class)]

    def get_parser(self, parser_class: Type[LineParser]) -> Optional[LineParser]:
        """Get a parser instance by class.

        Args:
            parser_class: The parser class to find

        Returns:
            The parser instance or None if not found
        """
        for parser in self.parsers:
            if isinstance(parser, parser_class):
                return parser
        return None

    def enable_parser(self, parser_class: Type[LineParser]):
        """Enable a specific parser.

        Args:
            parser_class: The parser class to enable
        """
        parser = self.get_parser(parser_class)
        if parser:
            parser.enabled = True

    def disable_parser(self, parser_class: Type[LineParser]):
        """Disable a specific parser.

        Args:
            parser_class: The parser class to disable
        """
        parser = self.get_parser(parser_class)
        if parser:
            parser.enabled = False

    def initialize_all(self):
        """Initialize all enabled parsers.

        This should be called once before parsing begins.
        """
        for parser in self.parsers:
            if parser.enabled:
                parser.initialize(self.context)

    def finalize_all(self):
        """Finalize all enabled parsers.

        This should be called once after all parsing is complete.
        """
        for parser in self.parsers:
            if parser.enabled:
                parser.finalize(self.context)

    def parse_line(self, line: str) -> bool:
        """Try to parse a line with registered parsers.

        Parsers are tried in priority order until one successfully handles the line.

        Args:
            line: The line to parse

        Returns:
            True if a parser handled the line, False otherwise
        """
        line = line.strip()
        if not line:
            return False

        for parser in self.parsers:
            if not parser.enabled:
                continue

            if parser.can_parse(line, self.context):
                return parser.parse(line, self.context)

        return False
