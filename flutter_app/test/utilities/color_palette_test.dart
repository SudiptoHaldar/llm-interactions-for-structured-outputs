import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/utilities/color_palette.dart';

void main() {
  group('ColorPalette', () {
    test('returns grey for null values', () {
      final color = ColorPalette.getColorForValue(
        null,
        minVal: 0,
        maxVal: 100,
      );
      expect(color, Colors.grey.shade300);
    });

    test('returns good color for max value when higher is better', () {
      final color = ColorPalette.getColorForValue(
        100,
        minVal: 0,
        maxVal: 100,
        higherIsBetter: true,
      );
      expect(color, ColorPalette.goodColor);
    });

    test('returns bad color for min value when higher is better', () {
      final color = ColorPalette.getColorForValue(
        0,
        minVal: 0,
        maxVal: 100,
        higherIsBetter: true,
      );
      expect(color, ColorPalette.badColor);
    });

    test('returns neutral color for midpoint value', () {
      final color = ColorPalette.getColorForValue(
        50,
        minVal: 0,
        maxVal: 100,
        higherIsBetter: true,
      );
      expect(color, ColorPalette.neutralColor);
    });

    test('inverts scale when lower is better', () {
      final colorHigherBetter = ColorPalette.getColorForValue(
        100,
        minVal: 0,
        maxVal: 100,
        higherIsBetter: true,
      );
      final colorLowerBetter = ColorPalette.getColorForValue(
        100,
        minVal: 0,
        maxVal: 100,
        higherIsBetter: false,
      );
      expect(colorHigherBetter, ColorPalette.goodColor);
      expect(colorLowerBetter, ColorPalette.badColor);
    });

    test('getTextColorForBackground returns black for light backgrounds', () {
      final textColor = ColorPalette.getTextColorForBackground(Colors.white);
      expect(textColor, Colors.black87);
    });

    test('getTextColorForBackground returns white for dark backgrounds', () {
      final textColor = ColorPalette.getTextColorForBackground(Colors.black);
      expect(textColor, Colors.white);
    });

    group('asymmetric gradients (medianVal parameter)', () {
      test('returns neutral color at median value', () {
        final color = ColorPalette.getColorForValue(
          70,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: true,
          medianVal: 70,
        );
        expect(color, ColorPalette.neutralColor);
      });

      test('spec example 1: value 94 with median 70 is in good zone', () {
        final color = ColorPalette.getColorForValue(
          94,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: true,
          medianVal: 70,
        );
        // Should be in good zone - Flutter uses muted colors so check
        // that green is dominant (higher than red)
        expect(color.green, greaterThan(color.red));
      });

      test('spec example 1: value 28 with median 70 is in bad zone', () {
        final color = ColorPalette.getColorForValue(
          28,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: true,
          medianVal: 70,
        );
        // Should be in bad zone, reddish
        expect(color.red, greaterThan(150));
      });

      test('spec example 2: value 20 at median (lower is better)', () {
        final color = ColorPalette.getColorForValue(
          20,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: false,
          medianVal: 20,
        );
        expect(color, ColorPalette.neutralColor);
      });

      test('spec example 2: value 10 in good zone (lower is better)', () {
        final color = ColorPalette.getColorForValue(
          10,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: false,
          medianVal: 20,
        );
        // Should be in good zone, greenish
        expect(color.green, greaterThan(100));
      });

      test('spec example 2: value 60 in bad zone (lower is better)', () {
        final color = ColorPalette.getColorForValue(
          60,
          minVal: 0,
          maxVal: 100,
          higherIsBetter: false,
          medianVal: 20,
        );
        // Should be in bad zone, reddish
        expect(color.red, greaterThan(150));
      });

      test('null medianVal defaults to midpoint (backward compatibility)', () {
        final colorWithNull = ColorPalette.getColorForValue(
          50,
          minVal: 0,
          maxVal: 100,
          medianVal: null,
        );
        final colorWithExplicit = ColorPalette.getColorForValue(
          50,
          minVal: 0,
          maxVal: 100,
          medianVal: 50,
        );
        expect(colorWithNull, colorWithExplicit);
      });

      test('extremes still return bad/good with asymmetric median', () {
        // Min value should still be bad
        final minColor = ColorPalette.getColorForValue(
          0,
          minVal: 0,
          maxVal: 100,
          medianVal: 70,
        );
        expect(minColor, ColorPalette.badColor);

        // Max value should still be good
        final maxColor = ColorPalette.getColorForValue(
          100,
          minVal: 0,
          maxVal: 100,
          medianVal: 70,
        );
        expect(maxColor, ColorPalette.goodColor);
      });

      test('handles null value with medianVal', () {
        final color = ColorPalette.getColorForValue(
          null,
          minVal: 0,
          maxVal: 100,
          medianVal: 70,
        );
        expect(color, Colors.grey.shade300);
      });

      test('handles invalid median (below min) gracefully', () {
        final color = ColorPalette.getColorForValue(
          50,
          minVal: 0,
          maxVal: 100,
          medianVal: -10, // Invalid
        );
        expect(color, ColorPalette.neutralColor);
      });

      test('handles invalid median (above max) gracefully', () {
        final color = ColorPalette.getColorForValue(
          50,
          minVal: 0,
          maxVal: 100,
          medianVal: 110, // Invalid
        );
        expect(color, ColorPalette.neutralColor);
      });
    });
  });
}
