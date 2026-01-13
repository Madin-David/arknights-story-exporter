"""
Image parser for handling image directives.

This parser handles [Image(image="...")] directives and manages
image references and deferred image appending.
"""

import re
from parsers.base import StatefulParser, ParserContext


class ImageParser(StatefulParser):
    """Parser for image directives.

    Recognizes patterns like:
    - [Image(image="27_i01")]

    Images are referenced in the text and queued for appending at the end
    of the document.
    """

    def __init__(self, enabled: bool = True, priority: int = 10):
        """Initialize the image parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 10, high priority)
        """
        super().__init__(enabled, priority)
        self.pattern = re.compile(r'Image\(image\s*=\s*"([^"]+)"', re.IGNORECASE)

    def initialize(self, context: ParserContext):
        """Initialize image state.

        Args:
            context: Shared parser context
        """
        self.set_parser_state(context, {
            'image_counter': 0,
            'image_reference_runs': {},
            'images_to_append': []
        })

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains an image directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains an image directive
        """
        return self.pattern.search(line) is not None

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the image directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the image was successfully handled
        """
        m = self.pattern.search(line)
        if not m:
            return False

        image_id = m.group(1).strip()
        state = self.get_parser_state(context)

        # Get image_map from assembler
        image_map = context.assembler.image_map if context.assembler else {}

        if image_id in image_map:
            state['image_counter'] += 1
            image_url = image_map[image_id]

            # Import the add_image_reference function
            from parse_text_to_docx import add_image_reference

            # Add image reference to document
            run = add_image_reference(context.doc, state['image_counter'])
            state['image_reference_runs'][state['image_counter']] = run

            # Queue image for appending
            state['images_to_append'].append((state['image_counter'], image_url))

        return True

    def finalize(self, context: ParserContext):
        """Finalize image processing by appending images to document.

        Args:
            context: Shared parser context
        """
        state = self.get_parser_state(context)
        if state and state.get('images_to_append') and context.assembler:
            # Delegate to assembler's append_images method
            # We'll need to update the assembler's state for compatibility
            context.assembler.image_counter = state['image_counter']
            context.assembler.image_reference_runs = state['image_reference_runs']
            context.assembler.images_to_append = state['images_to_append']
            context.assembler.append_images()
