"""
Decision parser for handling choice/decision directives.

This parser handles [Decision(options="...", values="...")] directives
and maintains the state of available choices.
"""

import re
from parsers.base import StatefulParser, ParserContext


class DecisionParser(StatefulParser):
    """Parser for decision/choice directives.

    Recognizes patterns like:
    - [Decision(options="选项1;选项2;...", values="1;2;...")]

    Maintains a mapping of option values to option text for use by
    PredicateParser.
    """

    def __init__(self, enabled: bool = True, priority: int = 20):
        """Initialize the decision parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 20)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(
            r'Decision\(options\s*=\s*"([^"]+)".*?values\s*=\s*"([^"]+)"',
            re.IGNORECASE
        )

    def initialize(self, context: ParserContext):
        """Initialize decision state.

        Args:
            context: Shared parser context
        """
        self.set_parser_state(context, {
            'current_decision_options': {},
            'current_predicate': None
        })

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains a decision directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains a decision directive
        """
        return self.pattern.search(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the decision directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the decision was successfully handled
        """
        m = self.pattern.search(line)
        if not m:
            return False

        options_str = m.group(1)
        values_str = m.group(2)
        options = options_str.split(';')
        values = values_str.split(';')

        # Update state
        state = self.get_parser_state(context)
        state['current_decision_options'] = {
            v.strip(): o.strip() for v, o in zip(values, options)
        }
        state['current_predicate'] = None

        # Import the add_decision function
        from parse_text_to_docx import add_decision

        # Add decision to document (currently does nothing)
        add_decision(context.doc, options)

        return True
