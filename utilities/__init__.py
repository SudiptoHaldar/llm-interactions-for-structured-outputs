"""Utility functions for LLM Interactions project."""

__version__ = "0.1.0"

from utilities.color_palette import (
    BAD_COLOR,
    GOOD_COLOR,
    NEUTRAL_COLOR,
    get_color_for_normalized_value,
    get_color_for_value,
)

__all__ = [
    "GOOD_COLOR",
    "NEUTRAL_COLOR",
    "BAD_COLOR",
    "get_color_for_value",
    "get_color_for_normalized_value",
]
