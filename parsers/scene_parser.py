"""
Scene parser for handling scene title directives.

This parser handles scene titles with timestamps in the format:
<p=1>Title<p=2>Timestamp
"""

import re
from parsers.base import LineParser, ParserContext


class SceneParser(LineParser):
    """Parser for scene title directives.

    Recognizes patterns like:
    - <p=1>场景标题<p=2>时间戳

    Adds both the scene title and timestamp to the document.
    """

    def __init__(self, enabled: bool = True, priority: int = 30):
        """Initialize the scene parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 30)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(r'<p=1>([^<\n]+)<p=2>([^<\n]+)')

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains a scene title directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains a scene title directive
        """
        return self.pattern.search(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the scene title directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the scene title was successfully handled
        """
        m = self.pattern.search(line)
        if not m:
            return False

        title = m.group(1).strip()
        time = m.group(2).strip()

        # Import the functions
        from parse_text_to_docx import add_scene_title, add_scene_timestamp

        # Add scene title and timestamp
        add_scene_title(context.doc, title)
        add_scene_timestamp(context.doc, time)

        return True
