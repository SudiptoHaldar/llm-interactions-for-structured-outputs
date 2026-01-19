import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/glossary_entry.dart';
import 'package:llm_interactions_app/widgets/glossary_content.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget() {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: const Scaffold(
        body: GlossaryContent(),
      ),
    );
  }

  setUp(() {
    // Clear cache before each test
    GlossaryCache.clear();
  });

  group('GlossaryContent', () {
    testWidgets('displays header title', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(
          find.text('Economic & Quality-of-Life Indicators'), findsOneWidget);
    });

    testWidgets('shows loading indicator initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Initially shows loading
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('displays higher is better legend item', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Legend has "Higher is better" text
      expect(find.text('Higher is better'), findsWidgets);
    });

    testWidgets('displays lower is better legend item', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Legend has "Lower is better" text
      expect(find.text('Lower is better'), findsWidgets);
    });

    testWidgets('displays trending up icon in legend', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Legend has trending icons
      expect(find.byIcon(Icons.trending_up), findsWidgets);
    });

    testWidgets('displays trending down icon in legend', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byIcon(Icons.trending_down), findsWidgets);
    });

    testWidgets('displays fallback entries after loading fails', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Wait for async loading to complete (will use fallback on failure)
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should show fallback entries count
      expect(
        find.text('${GlossaryEntry.fallbackEntries.length} definitions'),
        findsOneWidget,
      );
    });

    testWidgets('shows ListView after loading', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Wait for loading to complete
      await tester.pumpAndSettle(const Duration(seconds: 3));
      expect(find.byType(ListView), findsOneWidget);
    });
  });
}
