"""
Sound parser for handling sound and music directives.

This parser handles sound/music directives and stage directions:
- [PlaySound key="..."]
- [PlayMusic key="..."]
- <stage direction>
"""

import re
from parsers.base import LineParser, ParserContext


class SoundParser(LineParser):
    """Parser for sound/music directives and stage directions.

    Recognizes patterns like:
    - [PlaySound key="..."]
    - [PlayMusic key="..."]
    - <雷声> (stage directions)

    Can be configured to skip resource IDs (like $bgm_xxx).
    """

    def __init__(self, enabled: bool = True, priority: int = 45,
                 skip_resource_ids: bool = True):
        """Initialize the sound parser.

        Args:
            enabled: Whether this parser is enabled
            priority: Priority for parser execution (default: 45)
            skip_resource_ids: Whether to skip resource IDs (default: True)
        """
        super().__init__(enabled, priority)
        self.skip_resource_ids = skip_resource_ids
        self.skip_directives = {
            'stopsound', 'stopmusic', 'soundvolume', 'blocker', 'delay',
            'background', 'image', 'imagetween', 'curtain', 'camerashake',
            'cameraeffect', 'focusout', 'bgeffect', 'charslot', 'dialog',
            'subtitle', 'animtextclean', 'animtext', 'playsound', 'playmusic'
        }

    def can_parse(self, line: str, context: ParserContext) -> bool:
        """Check if this line contains a sound/music directive.

        Args:
            line: The line to check
            context: Shared parser context

        Returns:
            True if this line contains a sound/music directive
        """
        # Check for sound/music directives
        if line.startswith('[') and any(cmd in line for cmd in
            ['PlaySound', 'PlayMusic', 'StopSound', 'stopmusic', 'StopMusic',
             'playsound', 'playmusic']):
            return True

        # Check for stage directions <...>
        if line.startswith('<') and line.endswith('>'):
            return True

        return False

    def parse(self, line: str, context: ParserContext) -> bool:
        """Parse the sound/music directive.

        Args:
            line: The line to parse
            context: Shared parser context

        Returns:
            True if the directive was successfully handled
        """
        # Import the add_sound_effect function
        from parse_text_to_docx import add_sound_effect

        # Handle <stage direction>
        if line.startswith('<') and line.endswith('>'):
            text = line.strip('<>')
            add_sound_effect(context.doc, text)
            return True

        # Handle [PlaySound/PlayMusic/etc]
        if line.startswith('['):
            # Try to extract key
            m = re.search(r'key\s*=\s*"?([^",\)\]]+)"?', line)
            if m:
                key = m.group(1)
                add_sound_effect(context.doc, key)
            else:
                # Check if it's a known skip directive
                cmd_m = re.match(r'\[?\s*([A-Za-z_][A-Za-z0-9_]*)', line)
                if cmd_m:
                    cmd = cmd_m.group(1).lower()
                    if cmd in self.skip_directives:
                        # Recognized but not written
                        return True
                # Fallback: try to parse
                add_sound_effect(context.doc, line.strip('[]'))

            return True

        return False
