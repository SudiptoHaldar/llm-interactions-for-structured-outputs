"""Tests for color_palette module."""

import pytest

from utilities.color_palette import (
    BAD_COLOR,
    GOOD_COLOR,
    NEUTRAL_COLOR,
    _hex_to_rgb,
    _interpolate_rgb,
    _rgb_to_hex,
    get_color_for_normalized_value,
    get_color_for_value,
)


class TestColorConstants:
    """Tests for color constant definitions."""

    def test_good_color_is_green(self) -> None:
        """Test that GOOD_COLOR is green."""
        assert GOOD_COLOR == "#00FF00"

    def test_bad_color_is_red(self) -> None:
        """Test that BAD_COLOR is red."""
        assert BAD_COLOR == "#FF0000"

    def test_neutral_color_is_off_white(self) -> None:
        """Test that NEUTRAL_COLOR is off-white."""
        assert NEUTRAL_COLOR == "#FFFFFA"


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_rgb_to_hex_red(self) -> None:
        """Test RGB to hex conversion for red."""
        assert _rgb_to_hex((255, 0, 0)) == "#FF0000"

    def test_rgb_to_hex_green(self) -> None:
        """Test RGB to hex conversion for green."""
        assert _rgb_to_hex((0, 255, 0)) == "#00FF00"

    def test_rgb_to_hex_blue(self) -> None:
        """Test RGB to hex conversion for blue."""
        assert _rgb_to_hex((0, 0, 255)) == "#0000FF"

    def test_rgb_to_hex_black(self) -> None:
        """Test RGB to hex conversion for black."""
        assert _rgb_to_hex((0, 0, 0)) == "#000000"

    def test_rgb_to_hex_white(self) -> None:
        """Test RGB to hex conversion for white."""
        assert _rgb_to_hex((255, 255, 255)) == "#FFFFFF"

    def test_hex_to_rgb_red(self) -> None:
        """Test hex to RGB conversion for red."""
        assert _hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_hex_to_rgb_green(self) -> None:
        """Test hex to RGB conversion for green."""
        assert _hex_to_rgb("#00FF00") == (0, 255, 0)

    def test_hex_to_rgb_without_hash(self) -> None:
        """Test hex to RGB conversion without hash prefix."""
        assert _hex_to_rgb("00FF00") == (0, 255, 0)

    def test_interpolate_rgb_start(self) -> None:
        """Test interpolation at start (t=0)."""
        result = _interpolate_rgb((255, 0, 0), (0, 255, 0), 0.0)
        assert result == (255, 0, 0)

    def test_interpolate_rgb_end(self) -> None:
        """Test interpolation at end (t=1)."""
        result = _interpolate_rgb((255, 0, 0), (0, 255, 0), 1.0)
        assert result == (0, 255, 0)

    def test_interpolate_rgb_middle(self) -> None:
        """Test interpolation at middle (t=0.5)."""
        result = _interpolate_rgb((255, 0, 0), (0, 255, 0), 0.5)
        assert result == (127, 127, 0)

    def test_interpolate_rgb_quarter(self) -> None:
        """Test interpolation at quarter (t=0.25)."""
        result = _interpolate_rgb((255, 0, 0), (0, 255, 0), 0.25)
        assert result == (191, 63, 0)


class TestGetColorForValue:
    """Tests for get_color_for_value function."""

    def test_max_value_is_green_when_higher_is_better(self) -> None:
        """Test that max value returns green when higher is better."""
        result = get_color_for_value(100, 0, 100, higher_is_better=True)
        assert result == "#00FF00"

    def test_min_value_is_red_when_higher_is_better(self) -> None:
        """Test that min value returns red when higher is better."""
        result = get_color_for_value(0, 0, 100, higher_is_better=True)
        assert result == "#FF0000"

    def test_middle_value_is_neutral(self) -> None:
        """Test that middle value returns neutral color."""
        result = get_color_for_value(50, 0, 100, higher_is_better=True)
        assert result == "#FFFFFA"

    def test_max_value_is_red_when_lower_is_better(self) -> None:
        """Test that max value returns red when lower is better."""
        result = get_color_for_value(100, 0, 100, higher_is_better=False)
        assert result == "#FF0000"

    def test_min_value_is_green_when_lower_is_better(self) -> None:
        """Test that min value returns green when lower is better."""
        result = get_color_for_value(0, 0, 100, higher_is_better=False)
        assert result == "#00FF00"

    def test_value_90_higher_is_better(self) -> None:
        """Test spec example: value=90, higher_is_better=True."""
        result = get_color_for_value(90, 0, 100, higher_is_better=True)
        # Should be mostly green with some neutral
        assert result.startswith("#")
        rgb = _hex_to_rgb(result)
        assert rgb[1] == 255  # Green channel at max
        assert rgb[0] < 100  # Red channel low

    def test_value_20_higher_is_better(self) -> None:
        """Test spec example: value=20, higher_is_better=True."""
        result = get_color_for_value(20, 0, 100, higher_is_better=True)
        # Should be mostly red with some neutral
        rgb = _hex_to_rgb(result)
        assert rgb[0] == 255  # Red channel at max
        assert rgb[1] < 150  # Green channel moderate

    def test_value_20_lower_is_better(self) -> None:
        """Test spec example: value=20, lower_is_better=True."""
        result = get_color_for_value(20, 0, 100, higher_is_better=False)
        # 20 with lower_is_better means 80% toward good
        rgb = _hex_to_rgb(result)
        assert rgb[1] == 255  # Green channel at max

    def test_custom_range(self) -> None:
        """Test with custom min/max range."""
        result = get_color_for_value(75, 50, 100, higher_is_better=True)
        # 75 is 50% of range 50-100, so should be neutral
        assert result == "#FFFFFA"

    def test_invalid_range_raises(self) -> None:
        """Test that invalid range raises ValueError."""
        with pytest.raises(ValueError, match="must be less than"):
            get_color_for_value(50, 100, 0)

    def test_equal_min_max_raises(self) -> None:
        """Test that equal min and max raises ValueError."""
        with pytest.raises(ValueError, match="must be less than"):
            get_color_for_value(50, 50, 50)

    def test_value_clamped_above_max(self) -> None:
        """Test that values above max are clamped."""
        result_over = get_color_for_value(150, 0, 100, higher_is_better=True)
        result_max = get_color_for_value(100, 0, 100, higher_is_better=True)
        assert result_over == result_max

    def test_value_clamped_below_min(self) -> None:
        """Test that values below min are clamped."""
        result_under = get_color_for_value(-50, 0, 100, higher_is_better=True)
        result_min = get_color_for_value(0, 0, 100, higher_is_better=True)
        assert result_under == result_min

    def test_default_parameters(self) -> None:
        """Test with default parameters."""
        result = get_color_for_value(50)
        assert result == "#FFFFFA"

    def test_quarter_value(self) -> None:
        """Test at 25% value."""
        result = get_color_for_value(25, 0, 100, higher_is_better=True)
        assert result.startswith("#")
        # Should be between red and neutral
        rgb = _hex_to_rgb(result)
        assert rgb[0] == 255  # Still in red zone

    def test_three_quarter_value(self) -> None:
        """Test at 75% value."""
        result = get_color_for_value(75, 0, 100, higher_is_better=True)
        assert result.startswith("#")
        # Should be between neutral and green
        rgb = _hex_to_rgb(result)
        assert rgb[1] == 255  # In green zone


class TestGetColorForNormalizedValue:
    """Tests for get_color_for_normalized_value function."""

    def test_zero_is_red(self) -> None:
        """Test that 0.0 returns red."""
        assert get_color_for_normalized_value(0.0) == "#FF0000"

    def test_one_is_green(self) -> None:
        """Test that 1.0 returns green."""
        assert get_color_for_normalized_value(1.0) == "#00FF00"

    def test_half_is_neutral(self) -> None:
        """Test that 0.5 returns neutral."""
        assert get_color_for_normalized_value(0.5) == "#FFFFFA"

    def test_clamped_below_zero(self) -> None:
        """Test that values below 0 are clamped."""
        assert get_color_for_normalized_value(-0.5) == "#FF0000"

    def test_clamped_above_one(self) -> None:
        """Test that values above 1 are clamped."""
        assert get_color_for_normalized_value(1.5) == "#00FF00"

    def test_quarter_normalized(self) -> None:
        """Test at 0.25 normalized value."""
        result = get_color_for_normalized_value(0.25)
        assert result.startswith("#")
        rgb = _hex_to_rgb(result)
        assert rgb[0] == 255  # Still in red zone

    def test_three_quarter_normalized(self) -> None:
        """Test at 0.75 normalized value."""
        result = get_color_for_normalized_value(0.75)
        assert result.startswith("#")
        rgb = _hex_to_rgb(result)
        assert rgb[1] == 255  # In green zone


class TestEdgeCases:
    """Tests for edge cases."""

    def test_very_small_range(self) -> None:
        """Test with a very small range."""
        result = get_color_for_value(0.5, 0, 1, higher_is_better=True)
        assert result == "#FFFFFA"

    def test_negative_range(self) -> None:
        """Test with negative values in range."""
        result = get_color_for_value(0, -100, 100, higher_is_better=True)
        # 0 is middle of -100 to 100, so neutral
        assert result == "#FFFFFA"

    def test_float_precision(self) -> None:
        """Test with floating point values."""
        result = get_color_for_value(33.33, 0, 100, higher_is_better=True)
        assert result.startswith("#")
        assert len(result) == 7

    def test_large_range(self) -> None:
        """Test with a large range."""
        result = get_color_for_value(500000, 0, 1000000, higher_is_better=True)
        assert result == "#FFFFFA"

    def test_decimal_range(self) -> None:
        """Test with decimal range."""
        result = get_color_for_value(0.5, 0.0, 1.0, higher_is_better=True)
        assert result == "#FFFFFA"

    def test_negative_value_in_negative_range(self) -> None:
        """Test negative value in negative range."""
        result = get_color_for_value(-50, -100, 0, higher_is_better=True)
        # -50 is middle of -100 to 0
        assert result == "#FFFFFA"


class TestAsymmetricGradients:
    """Tests for asymmetric gradient support (median_val parameter)."""

    def test_spec_example1_median_value(self) -> None:
        """Test spec example 1: value=70 at median returns neutral."""
        result = get_color_for_value(70, 0, 100, higher_is_better=True, median_val=70)
        assert result == "#FFFFFA"

    def test_spec_example1_value_94(self) -> None:
        """Test spec example 1: value=94 in good zone."""
        result = get_color_for_value(94, 0, 100, higher_is_better=True, median_val=70)
        assert result == "#33FF32"

    def test_spec_example1_value_28(self) -> None:
        """Test spec example 1: value=28 in bad zone."""
        result = get_color_for_value(28, 0, 100, higher_is_better=True, median_val=70)
        assert result == "#FF6664"

    def test_spec_example2_median_value(self) -> None:
        """Test spec example 2: value=20 at median returns neutral."""
        result = get_color_for_value(20, 0, 100, higher_is_better=False, median_val=20)
        assert result == "#FFFFFA"

    def test_spec_example2_value_10(self) -> None:
        """Test spec example 2: value=10 in good zone (lower is better)."""
        result = get_color_for_value(10, 0, 100, higher_is_better=False, median_val=20)
        # t = 0.5, lerp(GOOD, NEUTRAL, 0.5) -> int(127.5) = 127 = 0x7F
        assert result == "#7FFF7D"

    def test_spec_example2_value_60(self) -> None:
        """Test spec example 2: value=60 in bad zone (lower is better)."""
        result = get_color_for_value(60, 0, 100, higher_is_better=False, median_val=20)
        # t = 0.5, lerp(NEUTRAL, BAD, 0.5) -> int(127.5) = 127 = 0x7F
        assert result == "#FF7F7D"

    def test_default_median_is_midpoint(self) -> None:
        """Test that None median defaults to midpoint (backward compatibility)."""
        result_with_none = get_color_for_value(50, 0, 100, median_val=None)
        result_explicit = get_color_for_value(50, 0, 100, median_val=50)
        assert result_with_none == result_explicit == "#FFFFFA"

    def test_backward_compatibility(self) -> None:
        """Test that existing calls without median_val still work."""
        # These should produce same results as before
        assert get_color_for_value(0, 0, 100) == "#FF0000"
        assert get_color_for_value(50, 0, 100) == "#FFFFFA"
        assert get_color_for_value(100, 0, 100) == "#00FF00"

    def test_median_at_min_edge(self) -> None:
        """Test median at minimum (all values in good zone)."""
        result = get_color_for_value(50, 0, 100, higher_is_better=True, median_val=0)
        # Value 50 is in good zone (0-100), t = 50/100 = 0.5
        # lerp(NEUTRAL, GOOD, 0.5) -> int(127.5) = 127 = 0x7F
        assert result == "#7FFF7D"

    def test_median_at_max_edge(self) -> None:
        """Test median at maximum (all values in bad zone)."""
        result = get_color_for_value(50, 0, 100, higher_is_better=True, median_val=100)
        # Value 50 is in bad zone (0-100), t = 50/100 = 0.5
        # lerp(BAD, NEUTRAL, 0.5) -> int(127.5) = 127 = 0x7F
        assert result == "#FF7F7D"

    def test_invalid_median_below_min_raises(self) -> None:
        """Test that median below min raises ValueError."""
        with pytest.raises(ValueError, match="median_val"):
            get_color_for_value(50, 0, 100, median_val=-10)

    def test_invalid_median_above_max_raises(self) -> None:
        """Test that median above max raises ValueError."""
        with pytest.raises(ValueError, match="median_val"):
            get_color_for_value(50, 0, 100, median_val=110)

    def test_extremes_with_asymmetric_median_higher_is_better(self) -> None:
        """Test that min and max still return bad/good colors (higher is better)."""
        # higher_is_better=True, median=70
        assert get_color_for_value(0, 0, 100, median_val=70) == "#FF0000"
        assert get_color_for_value(100, 0, 100, median_val=70) == "#00FF00"

    def test_extremes_with_asymmetric_median_lower_is_better(self) -> None:
        """Test that min and max still return good/bad colors (lower is better)."""
        # higher_is_better=False, median=20
        result_min = get_color_for_value(
            0, 0, 100, higher_is_better=False, median_val=20
        )
        result_max = get_color_for_value(
            100, 0, 100, higher_is_better=False, median_val=20
        )
        assert result_min == "#00FF00"
        assert result_max == "#FF0000"
