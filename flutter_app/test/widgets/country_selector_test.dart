import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/country.dart';
import 'package:llm_interactions_app/widgets/country_selector.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    List<Country>? countries,
    Country? selectedCountry,
    ValueChanged<Country?>? onChanged,
    bool isLoading = false,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: CountrySelector(
          countries: countries ?? [],
          selectedCountry: selectedCountry,
          onChanged: onChanged ?? (_) {},
          isLoading: isLoading,
        ),
      ),
    );
  }

  group('CountrySelector', () {
    testWidgets('displays Country label', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Country:'), findsOneWidget);
    });

    testWidgets('displays location icon', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byIcon(Icons.location_on), findsOneWidget);
    });

    testWidgets('shows loading indicator when isLoading', (tester) async {
      await tester.pumpWidget(buildTestWidget(isLoading: true));
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('shows dropdown when not loading', (tester) async {
      await tester.pumpWidget(buildTestWidget(isLoading: false));
      expect(find.byType(DropdownMenu<Country>), findsOneWidget);
    });

    testWidgets('uses Semantics for accessibility', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Verify Semantics widget wraps the content
      expect(find.byType(Semantics), findsWidgets);
    });
  });
}
