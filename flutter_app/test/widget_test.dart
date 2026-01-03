import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/main.dart';

void main() {
  testWidgets('App shows loading indicator initially', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    // Initially should show loading indicator
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('App has correct title in AppBar', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    expect(find.text('Server Health'), findsOneWidget);
  });

  testWidgets('App has refresh button in AppBar', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    expect(find.byIcon(Icons.refresh), findsOneWidget);
  });
}
