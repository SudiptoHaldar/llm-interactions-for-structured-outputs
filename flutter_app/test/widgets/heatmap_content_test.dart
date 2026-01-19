import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/heatmap_content.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget() {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: const Scaffold(
        body: HeatmapContent(),
      ),
    );
  }

  group('HeatmapContent', () {
    testWidgets('shows loading indicator initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('is a StatefulWidget', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byType(HeatmapContent), findsOneWidget);
      final widget = tester.widget<HeatmapContent>(find.byType(HeatmapContent));
      expect(widget, isA<StatefulWidget>());
    });

    testWidgets('accepts optional onCountryTap callback', (tester) async {
      String? tappedCountry;
      String? tappedContinent;

      await tester.pumpWidget(MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: HeatmapContent(
            onCountryTap: (country, continent) {
              tappedCountry = country;
              tappedContinent = continent;
            },
          ),
        ),
      ));

      // Widget should render without error
      expect(find.byType(HeatmapContent), findsOneWidget);
      // Callback vars should be null (no tap occurred)
      expect(tappedCountry, isNull);
      expect(tappedContinent, isNull);
    });
  });
}
