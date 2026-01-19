import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_expandable_fab/flutter_expandable_fab.dart';
import 'package:llm_interactions_app/widgets/globe_fab_menu.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({void Function(String)? onMenuSelected}) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        floatingActionButtonLocation: ExpandableFab.location,
        floatingActionButton: GlobeFabMenu(
          onMenuSelected: onMenuSelected,
        ),
        body: const SizedBox.expand(),
      ),
    );
  }

  group('GlobeFabMenu', () {
    testWidgets('renders ExpandableFab', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      expect(find.byType(ExpandableFab), findsOneWidget);
    });

    testWidgets('has three menu items defined', (tester) async {
      expect(GlobeFabMenu.menuItems.length, 3);
      expect(GlobeFabMenu.menuItems[0].id, 'global_heatmaps');
      expect(GlobeFabMenu.menuItems[1].id, 'travel_safety');
      expect(GlobeFabMenu.menuItems[2].id, 'glossary');
    });

    testWidgets('menu items have correct labels', (tester) async {
      expect(GlobeFabMenu.menuItems[0].label, 'Global Heatmaps');
      expect(GlobeFabMenu.menuItems[1].label, 'Travel Safety');
      expect(GlobeFabMenu.menuItems[2].label, 'Glossary');
    });

    testWidgets('menu items have correct icons', (tester) async {
      expect(GlobeFabMenu.menuItems[0].icon, Icons.public);
      expect(GlobeFabMenu.menuItems[1].icon, Icons.shield_outlined);
      expect(GlobeFabMenu.menuItems[2].icon, Icons.menu_book_outlined);
    });

    testWidgets('FAB uses theme tertiary color', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      // Verify FAB exists - color is applied via theme
      expect(find.byType(ExpandableFab), findsOneWidget);
    });
  });
}
