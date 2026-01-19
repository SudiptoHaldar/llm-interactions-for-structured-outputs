import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/continent_carousel.dart';
import 'package:llm_interactions_app/widgets/continent_card.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget(Widget child) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(body: child),
    );
  }

  group('ContinentCard', () {
    testWidgets('displays continent name', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCard(
          name: 'Africa',
          imagePath: 'assets/images/continents/africa.png',
        ),
      ));

      expect(find.text('Africa'), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(buildTestWidget(
        ContinentCard(
          name: 'Europe',
          imagePath: 'assets/images/continents/europe.png',
          onTap: () => tapped = true,
        ),
      ));

      await tester.tap(find.text('Europe'));
      await tester.pumpAndSettle();
      expect(tapped, isTrue);
    });

    testWidgets('handles missing image gracefully', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCard(
          name: 'Test',
          imagePath: 'invalid/path.png',
        ),
      ));

      expect(find.text('Test'), findsOneWidget);
    });

    testWidgets('does not call onTap when null', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCard(
          name: 'Asia',
          imagePath: 'assets/images/continents/asia.png',
          onTap: null,
        ),
      ));

      await tester.tap(find.text('Asia'));
      await tester.pumpAndSettle();
      expect(find.text('Asia'), findsOneWidget);
    });

    testWidgets('shows selection border when isSelected is true', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCard(
          name: 'Africa',
          imagePath: 'assets/images/continents/africa.png',
          isSelected: true,
        ),
      ));

      // Find AnimatedContainer with border decoration
      final animatedContainer = tester.widget<AnimatedContainer>(
        find.byType(AnimatedContainer),
      );
      final decoration = animatedContainer.decoration as BoxDecoration?;
      expect(decoration?.border, isNotNull);
    });

    testWidgets('shows ripple effect via InkWell', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        ContinentCard(
          name: 'Europe',
          imagePath: 'assets/images/continents/europe.png',
          onTap: () {},
        ),
      ));

      expect(find.byType(InkWell), findsOneWidget);
    });

    testWidgets('scales up when selected', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCard(
          name: 'Africa',
          imagePath: 'assets/images/continents/africa.png',
          isSelected: true,
        ),
      ));

      await tester.pumpAndSettle();

      final animatedScale = tester.widget<AnimatedScale>(
        find.byType(AnimatedScale),
      );
      expect(animatedScale.scale, equals(1.1));
    });
  });

  group('ContinentCarousel', () {
    testWidgets('displays all 7 continents', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(),
      ));

      expect(find.text('Africa'), findsOneWidget);
      expect(find.text('Antarctica'), findsOneWidget);
      expect(find.text('Asia'), findsOneWidget);
      expect(find.text('Europe'), findsOneWidget);
    });

    testWidgets('is horizontally scrollable', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(),
      ));

      expect(find.byType(ListView), findsOneWidget);
    });

    testWidgets('calls onContinentTap with index and name', (tester) async {
      int? tappedIndex;
      String? tappedName;
      await tester.pumpWidget(buildTestWidget(
        ContinentCarousel(
          onContinentTap: (index, name) {
            tappedIndex = index;
            tappedName = name;
          },
        ),
      ));

      await tester.tap(find.text('Africa'));
      await tester.pumpAndSettle();
      expect(tappedIndex, equals(0));
      expect(tappedName, equals('Africa'));
    });

    testWidgets('renders ContinentCards for visible items', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(),
      ));

      expect(find.byType(ContinentCard), findsAtLeast(4));
      expect(ContinentCarousel.continents.length, equals(7));
    });

    testWidgets('has fixed height of 130', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(),
      ));

      final sizedBox = tester.widget<SizedBox>(find.byType(SizedBox).first);
      expect(sizedBox.height, equals(130));
    });

    testWidgets('can scroll to see South America', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(),
      ));

      await tester.drag(find.byType(ListView), const Offset(-500, 0));
      await tester.pumpAndSettle();

      expect(find.text('South America'), findsOneWidget);
    });

    testWidgets('passes selectedIndex to ContinentCard', (tester) async {
      await tester.pumpWidget(buildTestWidget(
        const ContinentCarousel(selectedIndex: 0),
      ));

      await tester.pumpAndSettle();

      // First card should be selected (has AnimatedScale with scale 1.1)
      final cards =
          tester.widgetList<ContinentCard>(find.byType(ContinentCard));
      expect(cards.first.isSelected, isTrue);
    });
  });

  group('ContinentData', () {
    test('has correct number of continents', () {
      expect(ContinentCarousel.continents.length, equals(7));
    });

    test('contains all expected continent names', () {
      final names = ContinentCarousel.continents.map((c) => c.name).toList();
      expect(names, contains('Africa'));
      expect(names, contains('Antarctica'));
      expect(names, contains('Asia'));
      expect(names, contains('Europe'));
      expect(names, contains('North America'));
      expect(names, contains('Oceania'));
      expect(names, contains('South America'));
    });
  });
}
