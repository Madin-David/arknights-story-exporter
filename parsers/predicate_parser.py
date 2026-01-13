"""
Predicate parser for handling branch/predicate directives.

This parser handles [Predicate(references="...")] directives and displays
branch headers based on the current decision state.
"""

import re
from parsers.base import StatefulParser, ParserContext


class PredicateParser(StatefulParser):
    """Parser for predicate/branch directives.

    Recognizes patterns like:
    - [Predicate(references="1")]
    - [Predicate(references="1;2")]

    Uses the decision state from DecisionParser to display branch headers.
    """

    def __init__(self, enabled: bool = True, priority: int = 21):
        """Initialize the predicate parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 21, just after DecisionParser)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(r'Predicate\(references\s*=\s*"([^"]+)"', re.IGNORECASE)
        self.decision_parser_key = "DecisionParser_state"

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains a predicate directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains a predicate directive
        """
        return self.pattern.search(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the predicate directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the predicate was successfully handled
        """
        m = self.pattern.search(line)
        if not m:
            return False

        references = m.group(1).strip()

        # Get decision state
        decision_state = context.get_state(self.decision_parser_key, {})
        current_options = decision_state.get('current_decision_options', {})

        # Add predicate header if we have decision options
        if current_options:
            # Import the add_predicate_header function
            from parse_text_to_docx import add_predicate_header
            add_predicate_header(context.doc, references, current_options)

        # Update decision state with current predicate
        decision_state['current_predicate'] = references
        context.set_state(self.decision_parser_key, decision_state)

        return True
