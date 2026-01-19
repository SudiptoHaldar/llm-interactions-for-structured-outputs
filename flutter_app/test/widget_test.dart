import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/main.dart';
import 'package:llm_interactions_app/widgets/continent_carousel.dart';

void main() {
  testWidgets('App shows continent carousel on landing screen', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    // LandingScreen should show continent carousel
    expect(find.byType(ContinentCarousel), findsOneWidget);
  });

  testWidgets('App displays globetrotter title', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    expect(find.text('The Virtual Globetrotter'), findsOneWidget);
  });

  testWidgets('App uses SafeArea for content', (tester) async {
    await tester.pumpWidget(const LlmInteractionsApp());

    expect(find.byType(SafeArea), findsOneWidget);
  });
}
