import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/continent.dart';
import 'package:llm_interactions_app/widgets/continent_info_panel.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    Continent? continent,
    bool isLoading = false,
    String? error,
    VoidCallback? onRetry,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: ContinentInfoPanel(
          continent: continent,
          isLoading: isLoading,
          error: error,
          onRetry: onRetry,
        ),
      ),
    );
  }

  group('ContinentInfoPanel', () {
    testWidgets('shows loading indicator when isLoading', (tester) async {
      await tester.pumpWidget(buildTestWidget(isLoading: true));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows error message when error provided', (tester) async {
      await tester.pumpWidget(buildTestWidget(error: 'Test error'));
      expect(find.text('Error loading continent data'), findsOneWidget);
      expect(find.text('Test error'), findsOneWidget);
    });

    testWidgets('shows retry button when error and onRetry provided',
        (tester) async {
      bool retried = false;
      await tester.pumpWidget(buildTestWidget(
        error: 'Test error',
        onRetry: () => retried = true,
      ));
      await tester.tap(find.text('Retry'));
      expect(retried, true);
    });

    testWidgets('shows no data message when continent is null', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('No continent data'), findsOneWidget);
    });

    testWidgets('displays continent description', (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        description: 'A test description',
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));
      expect(find.text('A test description'), findsOneWidget);
    });

    testWidgets('displays area label and icon', (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        areaSqMile: 3860000,
        areaSqKm: 10023000,
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));
      expect(find.text('Area:'), findsOneWidget);
      expect(find.byIcon(Icons.square_foot), findsOneWidget);
    });

    testWidgets('displays population label and icon', (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        population: 746000000,
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));
      expect(find.text('Population:'), findsOneWidget);
      expect(find.byIcon(Icons.people), findsOneWidget);
    });

    testWidgets('displays countries label and value', (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        numCountry: 44,
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));
      expect(find.text('Countries:'), findsOneWidget);
      expect(find.text('44'), findsOneWidget);
      expect(find.byIcon(Icons.flag), findsOneWidget);
    });

    testWidgets('displays all continent info together', (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        description: 'Europe is known for its rich history',
        areaSqMile: 3860000,
        areaSqKm: 10023000,
        population: 746000000,
        numCountry: 44,
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));

      expect(find.text('Europe is known for its rich history'), findsOneWidget);
      expect(find.text('Area:'), findsOneWidget);
      expect(find.text('Population:'), findsOneWidget);
      expect(find.text('Countries:'), findsOneWidget);
      expect(find.text('44'), findsOneWidget);
    });

    testWidgets('does not show description box when description is null',
        (tester) async {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
        numCountry: 10,
      );
      await tester.pumpWidget(buildTestWidget(continent: continent));

      // Should still show stats
      expect(find.text('Countries:'), findsOneWidget);
      expect(find.text('10'), findsOneWidget);
    });
  });
}
