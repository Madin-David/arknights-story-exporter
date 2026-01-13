"""
Configuration loader for parser settings.

This module provides the ParserConfig class which handles loading
and merging configuration from various sources (YAML, JSON, dict).
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ParserConfig:
    """Configuration container for parser settings.

    This class manages configuration with a default configuration that can be
    overridden by:
    - YAML configuration files
    - JSON configuration files
    - Python dictionaries (code-based configuration)

    Configuration is hierarchically merged, with overrides taking precedence.
    """

    DEFAULT_CONFIG = {
        'document': {
            'page_size': 'A4',
            'margin_size': 'narrow',
            'add_page_numbers': True,
            'spacer_lines': 2
        },
        'parsers': {
            'control': {'enabled': True, 'priority': 5},
            'image': {'enabled': True, 'priority': 10},
            'decision': {'enabled': True, 'priority': 20},
            'predicate': {'enabled': True, 'priority': 21},
            'scene': {'enabled': True, 'priority': 30},
            'subtitle': {'enabled': True, 'priority': 35},
            'dialogue': {'enabled': True, 'priority': 40},
            'sound': {'enabled': True, 'priority': 45, 'skip_resource_ids': True},
            'narration': {'enabled': True, 'priority': 60},
        },
        'formatting': {
            'fonts': {},
            'paragraphs': {
                'line_spacing': 1.5,
                'narration_indent': 0.28
            }
        }
    }

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize configuration.

        Args:
            config_dict: Optional configuration dictionary to merge with defaults
        """
        self.config = self._merge_configs(
            self._deep_copy(self.DEFAULT_CONFIG),
            config_dict or {}
        )

    def _deep_copy(self, obj):
        """Deep copy a dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def _merge_configs(self, base: dict, override: dict) -> dict:
        """Deep merge two config dictionaries.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, path: str, default=None):
        """Get config value by dot-separated path.

        Args:
            path: Dot-separated path (e.g., 'parsers.image.enabled')
            default: Default value if path doesn't exist

        Returns:
            The configuration value or default

        Example:
            >>> config.get('parsers.image.enabled')
            True
            >>> config.get('parsers.image.priority')
            10
        """
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    @classmethod
    def from_yaml(cls, path: str) -> 'ParserConfig':
        """Load configuration from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            ParserConfig instance

        Raises:
            ImportError: If PyYAML is not installed
            FileNotFoundError: If file doesn't exist
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required to load YAML configuration files. "
                "Install it with: pip install pyyaml"
            )

        with open(path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(config_dict)

    @classmethod
    def from_json(cls, path: str) -> 'ParserConfig':
        """Load configuration from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            ParserConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls(config_dict)

    @classmethod
    def from_file(cls, path: str) -> 'ParserConfig':
        """Auto-detect file type and load configuration.

        Args:
            path: Path to configuration file (.yaml, .yml, or .json)

        Returns:
            ParserConfig instance

        Raises:
            ValueError: If file extension is not supported
        """
        path_obj = Path(path)
        if path_obj.suffix.lower() in ['.yaml', '.yml']:
            return cls.from_yaml(path)
        elif path_obj.suffix.lower() == '.json':
            return cls.from_json(path)
        else:
            raise ValueError(f"Unsupported config file format: {path_obj.suffix}")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ParserConfig':
        """Create configuration from dictionary (code-based config).

        Args:
            config_dict: Configuration dictionary

        Returns:
            ParserConfig instance
        """
        return cls(config_dict)
