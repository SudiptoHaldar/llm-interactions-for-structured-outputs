import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/glossary_entry.dart';
import 'package:llm_interactions_app/widgets/glossary_card.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget(GlossaryEntry entry) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: SingleChildScrollView(
          child: GlossaryCard(entry: entry),
        ),
      ),
    );
  }

  group('GlossaryCard', () {
    testWidgets('displays entry name', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.first;
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.text(entry.entry), findsOneWidget);
    });

    testWidgets('displays range when available', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.range == '0 - 100',
      );
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.text('0 - 100'), findsOneWidget);
    });

    testWidgets('displays interpretation badge', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.interpretation == 'Higher is better',
      );
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.text('Higher is better'), findsOneWidget);
    });

    testWidgets('shows trending up icon for higher is better', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.higherIsBetter,
      );
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.byIcon(Icons.trending_up), findsOneWidget);
    });

    testWidgets('shows trending down icon for lower is better', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.firstWhere(
        (e) => e.lowerIsBetter,
      );
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.byIcon(Icons.trending_down), findsOneWidget);
    });

    testWidgets('expands to show meaning', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.first;
      await tester.pumpWidget(buildTestWidget(entry));

      // Initially meaning may be hidden
      await tester.tap(find.byType(ExpansionTile));
      await tester.pumpAndSettle();

      // After expansion, meaning should be visible
      expect(find.text(entry.meaning), findsOneWidget);
    });

    testWidgets('uses Card widget', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.first;
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.byType(Card), findsOneWidget);
    });

    testWidgets('uses ExpansionTile for expandable content', (tester) async {
      final entry = GlossaryEntry.fallbackEntries.first;
      await tester.pumpWidget(buildTestWidget(entry));
      expect(find.byType(ExpansionTile), findsOneWidget);
    });
  });
}
