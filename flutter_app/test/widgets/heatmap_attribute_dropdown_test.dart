import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/heatmap_attribute_dropdown.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    HeatmapAttribute? selectedAttribute,
    ValueChanged<HeatmapAttribute>? onChanged,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: HeatmapAttributeDropdown(
          selectedAttribute:
              selectedAttribute ?? HeatmapAttributeDropdown.attributes.first,
          onChanged: onChanged ?? (_) {},
        ),
      ),
    );
  }

  group('HeatmapAttributeDropdown', () {
    testWidgets('displays Global Map label', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Global Map:'), findsOneWidget);
    });

    testWidgets('displays glossary reference', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // First attribute is GDP (PPP)
      expect(
        find.text('GDP: Gross Domestic Product at Purchasing Power Parity'),
        findsOneWidget,
      );
    });

    testWidgets('has 12 attributes defined', (tester) async {
      expect(HeatmapAttributeDropdown.attributes.length, 12);
    });

    testWidgets('first attribute is GDP (PPP)', (tester) async {
      expect(HeatmapAttributeDropdown.attributes.first.id, 'gdp');
      expect(HeatmapAttributeDropdown.attributes.first.higherIsBetter, true);
      expect(HeatmapAttributeDropdown.attributes.first.shortLabel, 'GDP');
      expect(HeatmapAttributeDropdown.attributes.first.medianVal, 65000000000);
    });

    testWidgets('GDP per Capita has correct median', (tester) async {
      final gdpPerCap = HeatmapAttributeDropdown.attributes.firstWhere(
        (a) => a.id == 'gdp_per_capita',
      );
      expect(gdpPerCap.medianVal, 20500);
      expect(gdpPerCap.higherIsBetter, true);
    });

    testWidgets('Gini Coefficient has median 37.5', (tester) async {
      final gini = HeatmapAttributeDropdown.attributes.firstWhere(
        (a) => a.id == 'gini_coefficient',
      );
      expect(gini.medianVal, 37.5);
      expect(gini.fixedMin, 0.0);
      expect(gini.fixedMax, 100.0);
    });

    testWidgets('attributes with medians have correct values', (tester) async {
      final attrs = HeatmapAttributeDropdown.attributes;

      final lifeExp = attrs.firstWhere((a) => a.id == 'life_expectancy');
      expect(lifeExp.medianVal, 73.5);

      final inflation = attrs.firstWhere((a) => a.id == 'inflation_rate');
      expect(inflation.medianVal, 4.0);

      final poverty = attrs.firstWhere((a) => a.id == 'poverty_rate');
      expect(poverty.medianVal, 20.0);

      final unemployment = attrs.firstWhere((a) => a.id == 'unemployment_rate');
      expect(unemployment.medianVal, 5.5);

      final govtDebt = attrs.firstWhere((a) => a.id == 'govt_debt');
      expect(govtDebt.medianVal, 50.0);

      final gdpGrowth = attrs.firstWhere((a) => a.id == 'gdp_growth_rate');
      expect(gdpGrowth.medianVal, 2.75);
    });

    testWidgets('PPP has no median (symmetric)', (tester) async {
      final ppp = HeatmapAttributeDropdown.attributes.firstWhere(
        (a) => a.id == 'ppp',
      );
      expect(ppp.medianVal, isNull);
    });

    testWidgets('Global Peace Index has fixed range and lower is better',
        (tester) async {
      final gpi = HeatmapAttributeDropdown.attributes.firstWhere(
        (a) => a.id == 'global_peace_index',
      );
      expect(gpi.fixedMin, 1.0);
      expect(gpi.fixedMax, 5.0);
      expect(gpi.higherIsBetter, false);
    });
  });
}
