import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/status_card.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget(Widget child) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(body: child),
    );
  }

  group('StatusCard', () {
    testWidgets('displays label and value', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Test Label',
          value: 'Test Value',
        ),
      ));

      expect(find.text('Test Label'), findsOneWidget);
      expect(find.text('Test Value'), findsOneWidget);
    });

    testWidgets('displays icon when provided', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Server',
          value: 'Online',
          icon: Icons.dns,
        ),
      ));

      expect(find.byIcon(Icons.dns), findsOneWidget);
    });

    testWidgets('displays OK badge for positive status', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Database',
          value: 'Connected',
          status: true,
        ),
      ));

      expect(find.text('OK'), findsOneWidget);
    });

    testWidgets('displays Error badge for negative status', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Database',
          value: 'Disconnected',
          status: false,
        ),
      ));

      expect(find.text('Error'), findsOneWidget);
    });

    testWidgets('hides badge when status is null', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Version',
          value: '1.0.0',
          status: null,
        ),
      ));

      expect(find.text('OK'), findsNothing);
      expect(find.text('Error'), findsNothing);
    });

    testWidgets('is wrapped in a Card widget', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const StatusCard(
          label: 'Test',
          value: 'Value',
        ),
      ));

      expect(find.byType(Card), findsOneWidget);
    });
  });
}
