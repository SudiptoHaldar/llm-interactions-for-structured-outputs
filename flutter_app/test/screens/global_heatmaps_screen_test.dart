import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/screens/global_heatmaps_screen.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget() {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: const GlobalHeatmapsScreen(),
    );
  }

  group('GlobalHeatmapsScreen', () {
    testWidgets('displays app bar with title', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.text('Global Heatmaps'), findsOneWidget);
    });

    testWidgets('shows loading indicator initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
