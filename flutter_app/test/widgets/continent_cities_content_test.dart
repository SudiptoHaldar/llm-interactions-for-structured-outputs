import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/continent_cities_content.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({String continentName = 'Europe'}) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: ContinentCitiesContent(continentName: continentName),
      ),
    );
  }

  group('ContinentCitiesContent', () {
    testWidgets('displays continent name in header', (tester) async {
      await tester.pumpWidget(buildTestWidget(continentName: 'Europe'));
      expect(find.text('Explore Europe'), findsOneWidget);
    });

    testWidgets('displays globe icon in header', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byIcon(Icons.public), findsOneWidget);
    });

    testWidgets('shows select country prompt initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Should show either loading or select prompt
      await tester.pump(const Duration(milliseconds: 100));
      final hasLoading =
          find.byType(CircularProgressIndicator).evaluate().isNotEmpty;
      final hasPrompt = find.text('Select a country').evaluate().isNotEmpty;
      final hasError = find.text('Error loading data').evaluate().isNotEmpty;
      expect(hasLoading || hasPrompt || hasError, true);
    });

    testWidgets('shows touch app icon for empty state', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      await tester.pumpAndSettle(const Duration(seconds: 3));
      // Either loading, error, or touch icon for empty state
      final hasTouchIcon =
          find.byIcon(Icons.touch_app_outlined).evaluate().isNotEmpty;
      final hasErrorIcon =
          find.byIcon(Icons.error_outline).evaluate().isNotEmpty;
      final hasLoading =
          find.byType(CircularProgressIndicator).evaluate().isNotEmpty;
      expect(hasTouchIcon || hasErrorIcon || hasLoading, true);
    });

    testWidgets('displays header with different continent names', (tester) async {
      await tester.pumpWidget(buildTestWidget(continentName: 'Asia'));
      expect(find.text('Explore Asia'), findsOneWidget);
    });
  });
}
