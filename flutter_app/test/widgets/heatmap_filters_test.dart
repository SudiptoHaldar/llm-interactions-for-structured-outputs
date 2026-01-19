import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/heatmap_filters.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    Set<String>? selectedContinents,
    Set<String>? selectedLLMs,
    ValueChanged<Set<String>>? onContinentsChanged,
    ValueChanged<Set<String>>? onLLMsChanged,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: HeatmapFilters(
          selectedContinents:
              selectedContinents ?? Set.from(HeatmapFilters.continents),
          selectedLLMs: selectedLLMs ?? Set.from(HeatmapFilters.llmProviders),
          onContinentsChanged: onContinentsChanged ?? (_) {},
          onLLMsChanged: onLLMsChanged ?? (_) {},
        ),
      ),
    );
  }

  group('HeatmapFilters', () {
    testWidgets('displays Filters title', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Filters'), findsOneWidget);
    });

    testWidgets('displays Continents section', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Continents'), findsOneWidget);
    });

    testWidgets('displays LLM Providers section', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('LLM Providers'), findsOneWidget);
    });

    testWidgets('has 6 continents defined', (tester) async {
      expect(HeatmapFilters.continents.length, 6);
      expect(HeatmapFilters.continents, contains('Africa'));
      expect(HeatmapFilters.continents, isNot(contains('Antarctica')));
    });

    testWidgets('has 8 LLM providers defined', (tester) async {
      expect(HeatmapFilters.llmProviders.length, 8);
      expect(HeatmapFilters.llmProviders, contains('OpenAI'));
      expect(HeatmapFilters.llmProviders, contains('Anthropic'));
    });

    testWidgets('shows all continents as checkboxes', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      for (final continent in HeatmapFilters.continents) {
        expect(find.text(continent), findsOneWidget);
      }
    });

    testWidgets('shows all LLMs as checkboxes', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      for (final llm in HeatmapFilters.llmProviders) {
        expect(find.text(llm), findsOneWidget);
      }
    });
  });
}
