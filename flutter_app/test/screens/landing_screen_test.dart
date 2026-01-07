import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/screens/landing_screen.dart';
import 'package:llm_interactions_app/widgets/continent_carousel.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget() {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: const LandingScreen(),
    );
  }

  group('LandingScreen', () {
    testWidgets('displays continent carousel', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byType(ContinentCarousel), findsOneWidget);
    });

    testWidgets('displays globetrotter title initially', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.text('The Virtual Globetrotter'), findsOneWidget);
    });

    testWidgets('uses SafeArea for proper padding', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byType(SafeArea), findsOneWidget);
    });

    testWidgets('changes hero title when continent is tapped', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      // Initially shows globetrotter title
      expect(find.text('The Virtual Globetrotter'), findsOneWidget);

      // Tap Africa
      await tester.tap(find.text('Africa'));
      await tester.pumpAndSettle();

      // Title changes to Africa (appears in carousel and hero)
      expect(find.text('Africa'), findsAtLeast(1));
      expect(find.text('The Virtual Globetrotter'), findsNothing);
    });

    testWidgets('toggles selection when same continent tapped again',
        (tester) async {
      await tester.pumpWidget(buildTestWidget());

      // Tap Africa
      await tester.tap(find.text('Africa'));
      await tester.pumpAndSettle();

      // Hero shows Africa
      expect(find.text('The Virtual Globetrotter'), findsNothing);

      // Tap Africa again to deselect
      await tester.tap(find.text('Africa').first);
      await tester.pumpAndSettle();

      // Hero shows globetrotter again
      expect(find.text('The Virtual Globetrotter'), findsOneWidget);
    });

    testWidgets('uses AnimatedSwitcher for hero transitions', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byType(AnimatedSwitcher), findsOneWidget);
    });

    testWidgets('hero has dark overlay for image opacity', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      // Find the hero container with BoxDecoration
      final containers = tester.widgetList<Container>(find.byType(Container));
      final heroContainer = containers.firstWhere(
        (c) =>
            c.decoration is BoxDecoration &&
            (c.decoration as BoxDecoration).image != null,
        orElse: () => Container(),
      );

      expect(heroContainer, isNotNull);
      final decoration = heroContainer.decoration as BoxDecoration;
      expect(decoration.image?.colorFilter, isNotNull);
    });

    testWidgets('can select different continents', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      // Tap Europe
      await tester.tap(find.text('Europe'));
      await tester.pumpAndSettle();

      // Europe appears in hero title
      expect(find.text('Europe'), findsAtLeast(1));
    });

    testWidgets('has Scaffold as root widget', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byType(Scaffold), findsOneWidget);
    });

    testWidgets('contains hero section with Expanded', (tester) async {
      await tester.pumpWidget(buildTestWidget());

      expect(find.byType(Expanded), findsOneWidget);
    });
  });
}
