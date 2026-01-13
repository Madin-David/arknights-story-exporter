"""
Modular parser system for story text parsing.

This package provides a pluggable parser architecture where each parsing
type is implemented as a separate parser class following the strategy pattern.
"""

from parsers.base import LineParser, StatefulParser, ParserContext
from parsers.registry import ParserRegistry

__all__ = [
    'LineParser',
    'StatefulParser',
    'ParserContext',
    'ParserRegistry',
]
