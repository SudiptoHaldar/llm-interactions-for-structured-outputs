"""Color palette utility for mapping values to bad-neutral-good colors.

This module provides functions to convert numeric values into hex color codes
on a red-white-green scale, useful for visualizing quality metrics.

Example:
    >>> from utilities.color_palette import get_color_for_value
    >>> get_color_for_value(90, 0, 100, higher_is_better=True)
    '#33FF32'
"""


# Color constants
GOOD_COLOR = "#00FF00"
NEUTRAL_COLOR = "#FFFFFA"
BAD_COLOR = "#FF0000"

# RGB tuples for interpolation
GOOD_RGB: tuple[int, int, int] = (0, 255, 0)
NEUTRAL_RGB: tuple[int, int, int] = (255, 255, 250)
BAD_RGB: tuple[int, int, int] = (255, 0, 0)


def _interpolate_rgb(
    color1: tuple[int, int, int],
    color2: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    """Linearly interpolate between two RGB colors.

    Args:
        color1: Starting RGB tuple.
        color2: Ending RGB tuple.
        t: Interpolation factor (0.0 to 1.0).

    Returns:
        Interpolated RGB tuple.
    """
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t),
    )


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string.

    Args:
        rgb: RGB tuple with values 0-255.

    Returns:
        Hex color string (e.g., "#FF0000").
    """
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "FF0000").

    Returns:
        RGB tuple with values 0-255.
    """
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def get_color_for_value(
    value: float,
    min_val: float = 0.0,
    max_val: float = 100.0,
    higher_is_better: bool = True,
    median_val: float | None = None,
) -> str:
    """Get hex color for a value on the bad-neutral-good scale.

    Maps a numeric value to a color on a three-point scale:
    - Bad (red): #FF0000
    - Neutral (off-white): #FFFFFA
    - Good (green): #00FF00

    Supports asymmetric gradients where median is not at the midpoint.

    Args:
        value: The value to map to a color.
        min_val: Minimum value of the range (default 0.0).
        max_val: Maximum value of the range (default 100.0).
        higher_is_better: If True, max_val maps to good (green).
                         If False, min_val maps to good (green).
        median_val: Optional median value for asymmetric gradients.
                   If None, defaults to (min_val + max_val) / 2.

    Returns:
        Hex color string (e.g., "#FF6664").

    Raises:
        ValueError: If min_val >= max_val or median_val outside range.

    Example:
        >>> # Symmetric (default): median at 50
        >>> get_color_for_value(75, 0, 100)
        '#80FF7D'

        >>> # Asymmetric: median at 70
        >>> get_color_for_value(94, 0, 100, median_val=70)
        '#33FF32'
        >>> get_color_for_value(28, 0, 100, median_val=70)
        '#FF6664'
    """
    if min_val >= max_val:
        raise ValueError(
            f"min_val ({min_val}) must be less than max_val ({max_val})"
        )

    # Default median to midpoint if not specified
    if median_val is None:
        median_val = (min_val + max_val) / 2

    # Validate median is within range
    if not (min_val <= median_val <= max_val):
        raise ValueError(
            f"median_val ({median_val}) must be between min_val ({min_val}) "
            f"and max_val ({max_val})"
        )

    # Clamp value to range
    value = max(min_val, min(max_val, value))

    # Determine which zone the value is in and interpolate
    if higher_is_better:
        if value <= median_val:
            # Bad zone: min_val → median_val maps to BAD → NEUTRAL
            if median_val == min_val:
                t = 0.0
            else:
                t = (value - min_val) / (median_val - min_val)
            rgb = _interpolate_rgb(BAD_RGB, NEUTRAL_RGB, t)
        else:
            # Good zone: median_val → max_val maps to NEUTRAL → GOOD
            if max_val == median_val:
                t = 1.0
            else:
                t = (value - median_val) / (max_val - median_val)
            rgb = _interpolate_rgb(NEUTRAL_RGB, GOOD_RGB, t)
    else:
        # Lower is better
        if value <= median_val:
            # Good zone: min_val → median_val maps to GOOD → NEUTRAL
            if median_val == min_val:
                t = 0.0
            else:
                t = (value - min_val) / (median_val - min_val)
            rgb = _interpolate_rgb(GOOD_RGB, NEUTRAL_RGB, t)
        else:
            # Bad zone: median_val → max_val maps to NEUTRAL → BAD
            if max_val == median_val:
                t = 1.0
            else:
                t = (value - median_val) / (max_val - median_val)
            rgb = _interpolate_rgb(NEUTRAL_RGB, BAD_RGB, t)

    return _rgb_to_hex(rgb)


def get_color_for_normalized_value(normalized: float) -> str:
    """Get hex color for a pre-normalized value (0.0 to 1.0).

    Useful when you've already normalized your value and just need
    the color mapping.

    Args:
        normalized: Value between 0.0 (bad) and 1.0 (good).

    Returns:
        Hex color string.

    Example:
        >>> get_color_for_normalized_value(0.0)
        '#FF0000'
        >>> get_color_for_normalized_value(0.5)
        '#FFFFFA'
        >>> get_color_for_normalized_value(1.0)
        '#00FF00'
    """
    # Clamp to valid range
    normalized = max(0.0, min(1.0, normalized))

    if normalized < 0.5:
        t = normalized * 2
        rgb = _interpolate_rgb(BAD_RGB, NEUTRAL_RGB, t)
    else:
        t = (normalized - 0.5) * 2
        rgb = _interpolate_rgb(NEUTRAL_RGB, GOOD_RGB, t)

    return _rgb_to_hex(rgb)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Get color for a value on bad-neutral-good scale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utilities.color_palette 90                    # Symmetric, 90/100
  python -m utilities.color_palette 94 --median 70        # Asymmetric, median=70
  python -m utilities.color_palette 20 --lower-is-better  # Lower values are better
  python -m utilities.color_palette 10 --median 20 --lower-is-better
        """,
    )
    parser.add_argument("value", type=float, help="Value to convert to color")
    parser.add_argument(
        "--min", type=float, default=0.0, help="Minimum value (default: 0)"
    )
    parser.add_argument(
        "--max", type=float, default=100.0, help="Maximum value (default: 100)"
    )
    parser.add_argument(
        "--median",
        type=float,
        default=None,
        help="Median value for asymmetric gradients (default: midpoint)",
    )
    parser.add_argument(
        "--lower-is-better",
        action="store_true",
        help="If set, lower values are better (green)",
    )

    args = parser.parse_args()

    color = get_color_for_value(
        args.value,
        min_val=args.min,
        max_val=args.max,
        higher_is_better=not args.lower_is_better,
        median_val=args.median,
    )

    median_display = (
        args.median if args.median is not None else (args.min + args.max) / 2
    )
    print(f"Value: {args.value}")
    print(f"Range: {args.min} to {args.max}")
    print(f"Median: {median_display}")
    print(f"Scale: {'Lower is better' if args.lower_is_better else 'Higher is better'}")
    print(f"Color: {color}")
