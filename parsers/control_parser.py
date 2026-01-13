"""
Control parser for recognizing and ignoring control directives.

This parser handles control directives that should be recognized but not
written to the document output.
"""

from parsers.base import LineParser, ParserContext


class ControlParser(LineParser):
    """Parser for control directives that should be ignored.

    Recognizes directives like:
    - # (scene separator)
    - [Dialog]
    - [Charslot]
    - [Background]

    These are recognized to prevent them from being treated as unhandled lines,
    but they are not written to the document.
    """

    def __init__(self, enabled: bool = True, priority: int = 5):
        """Initialize the control parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 5, very high priority)
        """
        super().__init__(enabled, priority)

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this is a control directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this is a control directive
        """
        line_lower = line.lower()
        return (
            line == '#' or
            line_lower.startswith('[dialog]') or
            line_lower.startswith('[charslot]') or
            line_lower.startswith('[background]')
        )

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the control directive (do nothing).

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            False to indicate the line was recognized but not written
        """
        # Recognized but not written to document
        return False
