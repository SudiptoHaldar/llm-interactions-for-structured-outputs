import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/utilities/number_formatter.dart';

void main() {
  group('NumberFormatter', () {
    group('formatValue', () {
      test('returns N/A for null values', () {
        expect(NumberFormatter.formatValue(null), 'N/A');
      });

      test('formats trillion values with T suffix', () {
        expect(NumberFormatter.formatValue(1000000000000), '1.00T');
        expect(NumberFormatter.formatValue(1500000000000), '1.50T');
        expect(NumberFormatter.formatValue(12345678901234), '12.35T');
      });

      test('formats billion values with B suffix', () {
        expect(NumberFormatter.formatValue(1000000000), '1.00B');
        expect(NumberFormatter.formatValue(2500000000), '2.50B');
        expect(NumberFormatter.formatValue(999999999999), '1000.00B');
      });

      test('formats million values with M suffix', () {
        expect(NumberFormatter.formatValue(1000000), '1.00M');
        expect(NumberFormatter.formatValue(5500000), '5.50M');
        expect(NumberFormatter.formatValue(999999999), '1000.00M');
      });

      test('formats values under million with thousand separators', () {
        expect(NumberFormatter.formatValue(1000), '1,000.00');
        expect(NumberFormatter.formatValue(12345.67), '12,345.67');
        expect(NumberFormatter.formatValue(999999.99), '999,999.99');
      });

      test('formats small values correctly', () {
        expect(NumberFormatter.formatValue(0), '0.00');
        expect(NumberFormatter.formatValue(1), '1.00');
        expect(NumberFormatter.formatValue(99.99), '99.99');
        expect(NumberFormatter.formatValue(123.456), '123.46');
      });

      test('handles negative values', () {
        expect(NumberFormatter.formatValue(-1000000000000), '-1.00T');
        expect(NumberFormatter.formatValue(-1000000000), '-1.00B');
        expect(NumberFormatter.formatValue(-1000000), '-1.00M');
        expect(NumberFormatter.formatValue(-12345.67), '-12,345.67');
      });

      test('handles edge cases at thresholds', () {
        // Just under trillion
        expect(NumberFormatter.formatValue(999999999999), '1000.00B');
        // Just under billion
        expect(NumberFormatter.formatValue(999999999), '1000.00M');
        // Just under million
        expect(NumberFormatter.formatValue(999999), '999,999.00');
      });
    });

    group('formatWithDecimals', () {
      test('returns N/A for null values', () {
        expect(NumberFormatter.formatWithDecimals(null), 'N/A');
      });

      test('formats with default 2 decimal places', () {
        expect(NumberFormatter.formatWithDecimals(1234.567), '1,234.57');
        expect(NumberFormatter.formatWithDecimals(1234.5), '1,234.50');
      });

      test('formats with custom decimal places', () {
        expect(
            NumberFormatter.formatWithDecimals(1234.5678, decimals: 0), '1,235');
        expect(NumberFormatter.formatWithDecimals(1234.5678, decimals: 1),
            '1,234.6');
        expect(NumberFormatter.formatWithDecimals(1234.5678, decimals: 3),
            '1,234.568');
      });
    });

    group('formatPercent', () {
      test('returns N/A for null values', () {
        expect(NumberFormatter.formatPercent(null), 'N/A');
      });

      test('formats percentage with default 2 decimal places', () {
        expect(NumberFormatter.formatPercent(12.345), '12.35%');
        expect(NumberFormatter.formatPercent(99.9), '99.90%');
        expect(NumberFormatter.formatPercent(0), '0.00%');
      });

      test('formats percentage with custom decimal places', () {
        expect(NumberFormatter.formatPercent(12.345, decimals: 0), '12%');
        expect(NumberFormatter.formatPercent(12.345, decimals: 1), '12.3%');
        expect(NumberFormatter.formatPercent(12.345, decimals: 3), '12.345%');
      });
    });
  });
}
