"""
Narration parser for handling quoted narration text.

This parser handles quoted narration lines like:
- "留下。"
- "text"
"""

import re
from parsers.base import LineParser, ParserContext


class NarrationParser(LineParser):
    """Parser for quoted narration text.

    Recognizes patterns like:
    - "留下。"
    - "text"

    Renders narration with special formatting (Kai font, indented).
    """

    def __init__(self, enabled: bool = True, priority: int = 60):
        """Initialize the narration parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 60, low priority)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(r'^[""].+[""]$')

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line is quoted narration.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line is quoted narration
        """
        return self.pattern.match(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the narration line.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the narration was successfully handled
        """
        if not self.pattern.match(line):
            return False

        # Import the add_narration function
        from parse_text_to_docx import add_narration

        # Add narration
        add_narration(context.doc, line)

        return True
