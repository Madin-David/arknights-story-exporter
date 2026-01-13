"""
Dialogue parser for handling character dialogue.

This parser handles dialogue lines in various formats:
- [name="Character"]text
- name="Character"]text (without opening bracket)
"""

import re
from parsers.base import LineParser, ParserContext


class DialogueParser(LineParser):
    """Parser for character dialogue.

    Recognizes patterns like:
    - [name="角色"]对话内容
    - name="角色"]对话内容

    Renders dialogue with character name in bold followed by the text.
    """

    def __init__(self, enabled: bool = True, priority: int = 40):
        """Initialize the dialogue parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 40)
        """
        super().__init__(enabled, priority)
        self.pattern1 = re.compile(r'\[name="([^"]+)"\](.*)')
        self.pattern2 = re.compile(r'name\s*=\s*"([^"]+)"\]\s*(.*)')

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains dialogue.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains dialogue
        """
        return (self.pattern1.match(line) is not None or
                self.pattern2.search(line) is not None)

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the dialogue line.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the dialogue was successfully handled
        """
        # Import the add_dialogue function
        from parse_text_to_docx import add_dialogue

        # Try pattern 1: [name="Character"]text
        m = self.pattern1.match(line)
        if m:
            character = m.group(1).strip()
            text = m.group(2).strip()
            add_dialogue(context.doc, character, text)
            return True

        # Try pattern 2: name="Character"]text
        m = self.pattern2.search(line)
        if m:
            character = m.group(1).strip()
            text = m.group(2).strip()
            add_dialogue(context.doc, character, text)
            return True

        return False
