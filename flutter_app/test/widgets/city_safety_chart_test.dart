import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:llm_interactions_app/models/city.dart';
import 'package:llm_interactions_app/widgets/city_safety_chart.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({List<City>? cities}) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: CitySafetyChart(cities: cities ?? []),
      ),
    );
  }

  group('CitySafetyChart', () {
    testWidgets('shows empty state when no cities', (tester) async {
      await tester.pumpWidget(buildTestWidget(cities: []));
      expect(find.text('No city data available'), findsOneWidget);
      expect(find.byIcon(Icons.bar_chart_outlined), findsOneWidget);
    });

    testWidgets('shows empty state hint text', (tester) async {
      await tester.pumpWidget(buildTestWidget(cities: []));
      expect(
        find.text('Select a country with city safety data'),
        findsOneWidget,
      );
    });

    testWidgets('displays legend when cities provided', (tester) async {
      final cities = [
        const City(cityId: 1, name: 'Test City', sciScore: 80),
      ];
      await tester.pumpWidget(buildTestWidget(cities: cities));
      expect(find.text('SCI Score'), findsOneWidget);
      expect(find.text('Safety Index'), findsOneWidget);
      expect(find.text('Crime Index'), findsOneWidget);
    });

    testWidgets('displays BarChart when cities provided', (tester) async {
      final cities = [
        const City(
          cityId: 1,
          name: 'Test City',
          sciScore: 80,
          numbeoSi: 70,
          numbeoCi: 30,
        ),
      ];
      await tester.pumpWidget(buildTestWidget(cities: cities));
      expect(find.byType(BarChart), findsOneWidget);
    });

    testWidgets('shows capital indicator for capital cities', (tester) async {
      final cities = [
        const City(cityId: 1, name: 'Capital', isCapital: true, sciScore: 80),
      ];
      await tester.pumpWidget(buildTestWidget(cities: cities));
      expect(find.byIcon(Icons.star), findsWidgets);
    });

    testWidgets('displays legend interpretation hints', (tester) async {
      final cities = [
        const City(cityId: 1, name: 'Test City', sciScore: 80),
      ];
      await tester.pumpWidget(buildTestWidget(cities: cities));
      expect(find.text('(Higher is better)'), findsNWidgets(2));
      expect(find.text('(Lower is better)'), findsOneWidget);
    });

    testWidgets('handles multiple cities', (tester) async {
      final cities = [
        const City(cityId: 1, name: 'City A', sciScore: 80),
        const City(cityId: 2, name: 'City B', sciScore: 70),
        const City(cityId: 3, name: 'City C', sciScore: 60),
      ];
      await tester.pumpWidget(buildTestWidget(cities: cities));
      expect(find.byType(BarChart), findsOneWidget);
    });
  });
}
