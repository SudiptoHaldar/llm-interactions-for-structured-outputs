import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/country.dart';
import 'package:llm_interactions_app/widgets/continent_countries_panel.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    String continentName = 'Europe',
    List<Country>? countries,
    Country? selectedCountry,
    ValueChanged<Country>? onCountryTap,
    bool isLoading = false,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: ContinentCountriesPanel(
          continentName: continentName,
          countries: countries ?? [],
          selectedCountry: selectedCountry,
          onCountryTap: onCountryTap ?? (_) {},
          isLoading: isLoading,
        ),
      ),
    );
  }

  group('ContinentCountriesPanel', () {
    testWidgets('displays continent name in header', (tester) async {
      await tester.pumpWidget(buildTestWidget(continentName: 'Europe'));
      expect(find.text('Europe'), findsOneWidget);
    });

    testWidgets('displays country count', (tester) async {
      final countries = [
        const Country(countryId: 1, name: 'Germany'),
        const Country(countryId: 2, name: 'France'),
      ];
      await tester.pumpWidget(buildTestWidget(countries: countries));
      expect(find.text('2 countries'), findsOneWidget);
    });

    testWidgets('shows loading indicator when isLoading', (tester) async {
      await tester.pumpWidget(buildTestWidget(isLoading: true));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows empty state when no countries', (tester) async {
      await tester.pumpWidget(buildTestWidget(countries: []));
      expect(find.text('No countries found'), findsOneWidget);
    });

    testWidgets('displays country names', (tester) async {
      final countries = [
        const Country(countryId: 1, name: 'Germany'),
        const Country(countryId: 2, name: 'Croatia'),
      ];
      await tester.pumpWidget(buildTestWidget(countries: countries));
      expect(find.text('Germany'), findsOneWidget);
      expect(find.text('Croatia'), findsOneWidget);
    });

    testWidgets('calls onCountryTap when country tapped', (tester) async {
      Country? tappedCountry;
      final countries = [
        const Country(countryId: 1, name: 'Germany'),
      ];
      await tester.pumpWidget(buildTestWidget(
        countries: countries,
        onCountryTap: (country) => tappedCountry = country,
      ));
      await tester.tap(find.text('Germany'));
      expect(tappedCountry?.name, 'Germany');
    });

    testWidgets('highlights selected country', (tester) async {
      final germany = const Country(countryId: 1, name: 'Germany');
      final countries = [germany];
      await tester.pumpWidget(buildTestWidget(
        countries: countries,
        selectedCountry: germany,
      ));
      // Selected country should have filled flag icon
      expect(find.byIcon(Icons.flag), findsOneWidget);
    });

    testWidgets('shows outlined flag for unselected country', (tester) async {
      final countries = [
        const Country(countryId: 1, name: 'Germany'),
      ];
      await tester.pumpWidget(buildTestWidget(countries: countries));
      expect(find.byIcon(Icons.flag_outlined), findsOneWidget);
    });
  });
}
