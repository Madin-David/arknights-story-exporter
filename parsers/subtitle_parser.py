"""
Subtitle parser for handling subtitle directives.

This parser handles Subtitle(text="...") directives and renders them
as narration text.
"""

import re
from parsers.base import LineParser, ParserContext


class SubtitleParser(LineParser):
    """Parser for subtitle directives.

    Recognizes patterns like:
    - Subtitle(text="字幕文本")

    Renders subtitles as narration text.
    """

    def __init__(self, enabled: bool = True, priority: int = 35):
        """Initialize the subtitle parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 35)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(r'Subtitle\(text\s*=\s*"([^"]+)"')

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains a subtitle directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains a subtitle directive
        """
        return self.pattern.search(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the subtitle directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the subtitle was successfully handled
        """
        m = self.pattern.search(line)
        if not m:
            return False

        text = m.group(1)

        # Import the add_narration function
        from parse_text_to_docx import add_narration

        # Add subtitle as narration
        add_narration(context.doc, text)

        return True
