import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/breadcrumb.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    String currentSection = 'Test Section',
    VoidCallback? onTap,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        body: Breadcrumb(
          currentSection: currentSection,
          onTap: onTap,
        ),
      ),
    );
  }

  group('Breadcrumb', () {
    testWidgets('displays current section text', (tester) async {
      await tester.pumpWidget(buildTestWidget(currentSection: 'Travel HQ'));

      expect(find.text('Travel HQ'), findsOneWidget);
    });

    testWidgets('displays home icon', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byIcon(Icons.home_outlined), findsOneWidget);
    });

    testWidgets('displays chevron separator', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byIcon(Icons.chevron_right), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(buildTestWidget(
        onTap: () => tapped = true,
      ));

      await tester.tap(find.text('Test Section'));
      await tester.pump();

      expect(tapped, true);
    });
  });
}
