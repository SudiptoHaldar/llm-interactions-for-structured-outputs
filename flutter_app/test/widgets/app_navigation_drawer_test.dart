import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/widgets/app_navigation_drawer.dart';
import 'package:llm_interactions_app/theme/app_theme.dart';

void main() {
  Widget buildTestWidget({
    String? selectedId,
    void Function(String)? onItemSelected,
  }) {
    return MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(
        drawer: AppNavigationDrawer(
          selectedId: selectedId,
          onItemSelected: onItemSelected,
        ),
        body: Builder(
          builder: (context) => ElevatedButton(
            onPressed: () => Scaffold.of(context).openDrawer(),
            child: const Text('Open Drawer'),
          ),
        ),
      ),
    );
  }

  group('AppNavigationDrawer', () {
    testWidgets('has three navigation items defined', (tester) async {
      expect(AppNavigationDrawer.navItems.length, 3);
    });

    testWidgets('shows Travel HQ header', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      await tester.tap(find.text('Open Drawer'));
      await tester.pumpAndSettle();

      expect(find.text('Travel HQ'), findsOneWidget);
    });

    testWidgets('shows Global Heatmaps item', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      await tester.tap(find.text('Open Drawer'));
      await tester.pumpAndSettle();

      expect(find.text('Global Heatmaps'), findsOneWidget);
    });

    testWidgets('shows Travel Safety item', (tester) async {
      await tester.pumpWidget(buildTestWidget());
      await tester.tap(find.text('Open Drawer'));
      await tester.pumpAndSettle();

      expect(find.text('Travel Safety'), findsOneWidget);
    });

    testWidgets('calls onItemSelected when item tapped', (tester) async {
      String? selectedItem;
      await tester.pumpWidget(buildTestWidget(
        onItemSelected: (id) => selectedItem = id,
      ));

      await tester.tap(find.text('Open Drawer'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Global Heatmaps'));
      await tester.pumpAndSettle();

      expect(selectedItem, 'global_heatmaps');
    });
  });
}
