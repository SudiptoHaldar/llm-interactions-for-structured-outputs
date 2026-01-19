import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/glossary_entry.dart';

void main() {
  group('GlossaryEntry', () {
    test('fallbackEntries has entries', () {
      expect(GlossaryEntry.fallbackEntries.isNotEmpty, true);
    });

    test('Gini Coefficient in fallback has correct properties', () {
      final gini = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.entry == 'Gini Coefficient',
      );
      expect(gini.range, '0 - 100');
      expect(gini.interpretation, 'Lower is better');
      expect(gini.lowerIsBetter, true);
      expect(gini.higherIsBetter, false);
    });

    test('Happiness Index in fallback has correct properties', () {
      final happiness = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.entry == 'Happiness Index',
      );
      expect(happiness.range, '0 - 10');
      expect(happiness.interpretation, 'Higher is better');
      expect(happiness.higherIsBetter, true);
      expect(happiness.lowerIsBetter, false);
    });

    test('all fallback entries have entry and meaning', () {
      for (final entry in GlossaryEntry.fallbackEntries) {
        expect(entry.entry.isNotEmpty, true);
        expect(entry.meaning.isNotEmpty, true);
      }
    });

    test('all fallback entries have interpretation', () {
      for (final entry in GlossaryEntry.fallbackEntries) {
        expect(entry.interpretation != null, true);
        expect(
          entry.interpretation == 'Higher is better' ||
              entry.interpretation == 'Lower is better',
          true,
        );
      }
    });

    test('GDP (PPP) is higher is better', () {
      final gdp = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.entry == 'GDP (PPP)',
      );
      expect(gdp.higherIsBetter, true);
      expect(gdp.range, 'Numeric');
    });

    test('Poverty Rate is lower is better', () {
      final poverty = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.entry == 'Poverty Rate',
      );
      expect(poverty.lowerIsBetter, true);
      expect(poverty.range, '0 - 100');
    });

    test('fromJson parses correctly', () {
      final json = {
        'glossary_id': 1,
        'entry': 'Test Entry',
        'meaning': 'Test meaning',
        'range': '0 - 100',
        'interpretation': 'Higher is better',
      };
      final entry = GlossaryEntry.fromJson(json);
      expect(entry.glossaryId, 1);
      expect(entry.entry, 'Test Entry');
      expect(entry.meaning, 'Test meaning');
      expect(entry.range, '0 - 100');
      expect(entry.interpretation, 'Higher is better');
      expect(entry.higherIsBetter, true);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'entry': 'Test Entry',
        'meaning': 'Test meaning',
      };
      final entry = GlossaryEntry.fromJson(json);
      expect(entry.glossaryId, null);
      expect(entry.range, null);
      expect(entry.interpretation, null);
    });
  });

  group('GlossaryListResponse', () {
    test('fromJson parses list correctly', () {
      final json = {
        'glossary': [
          {'entry': 'Entry 1', 'meaning': 'Meaning 1'},
          {'entry': 'Entry 2', 'meaning': 'Meaning 2'},
        ],
        'count': 2,
      };
      final response = GlossaryListResponse.fromJson(json);
      expect(response.count, 2);
      expect(response.glossary.length, 2);
      expect(response.glossary[0].entry, 'Entry 1');
      expect(response.glossary[1].entry, 'Entry 2');
    });
  });

  group('GlossaryCache', () {
    setUp(() {
      GlossaryCache.clear();
    });

    test('returns fallback entries when cache is empty', () {
      expect(GlossaryCache.entries, GlossaryEntry.fallbackEntries);
      expect(GlossaryCache.hasApiEntries, false);
    });

    test('setEntries caches entries', () {
      final testEntries = [
        const GlossaryEntry(entry: 'Test', meaning: 'Test meaning'),
      ];
      GlossaryCache.setEntries(testEntries);
      expect(GlossaryCache.entries, testEntries);
      expect(GlossaryCache.hasApiEntries, true);
    });

    test('clear resets cache', () {
      final testEntries = [
        const GlossaryEntry(entry: 'Test', meaning: 'Test meaning'),
      ];
      GlossaryCache.setEntries(testEntries);
      GlossaryCache.clear();
      expect(GlossaryCache.entries, GlossaryEntry.fallbackEntries);
      expect(GlossaryCache.hasApiEntries, false);
    });
  });
}
