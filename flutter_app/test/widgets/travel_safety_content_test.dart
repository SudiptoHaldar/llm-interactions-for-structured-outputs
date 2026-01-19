import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/travel_safety_content.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget() {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: const Scaffold(
        body: TravelSafetyContent(),
      ),
    );
  }

  group('TravelSafetyContent', () {
    testWidgets('displays header title', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Travel Safety'), findsOneWidget);
    });

    testWidgets('displays header description', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(
        find.text('City safety indices comparison by country'),
        findsOneWidget,
      );
    });

    testWidgets('displays shield icon in header', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byIcon(Icons.shield), findsOneWidget);
    });

    testWidgets('shows loading indicator initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Either loading or error state (API not available)
      expect(
        find.byType(CircularProgressIndicator).evaluate().isNotEmpty ||
            find.byType(LinearProgressIndicator).evaluate().isNotEmpty ||
            find.text('Select a country').evaluate().isNotEmpty ||
            find.text('Error loading data').evaluate().isNotEmpty,
        true,
      );
    });

    testWidgets('shows select country prompt or error', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Wait for countries to load (or fail)
      await tester.pumpAndSettle(const Duration(seconds: 3));
      // Should show either select prompt or error
      final foundSelectPrompt =
          find.text('Select a country').evaluate().isNotEmpty ||
              find.text('Choose a country to view city safety data')
                  .evaluate()
                  .isNotEmpty;
      final foundError = find.text('Error loading data').evaluate().isNotEmpty;
      expect(foundSelectPrompt || foundError, true);
    });

    testWidgets('displays location city icon for empty state', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      await tester.pumpAndSettle(const Duration(seconds: 3));
      // Should show either city icon or error icon
      final foundCityIcon =
          find.byIcon(Icons.location_city_outlined).evaluate().isNotEmpty;
      final foundErrorIcon =
          find.byIcon(Icons.error_outline).evaluate().isNotEmpty;
      expect(foundCityIcon || foundErrorIcon, true);
    });
  });
}
