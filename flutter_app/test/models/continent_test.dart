import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/continent.dart';

void main() {
  group('Continent', () {
    test('fromJson parses all fields correctly', () {
      final json = {
        'continent_id': 9,
        'continent_name': 'Europe',
        'description': 'A continent',
        'area_sq_mile': 3860000.0,
        'area_sq_km': 10023000.0,
        'population': 746419440,
        'num_country': 44,
        'ai_model_id': 1,
        'created_at': '2026-01-03T10:35:19.312740Z',
        'updated_at': '2026-01-03T10:35:19.312740Z',
      };

      final continent = Continent.fromJson(json);

      expect(continent.continentId, 9);
      expect(continent.continentName, 'Europe');
      expect(continent.description, 'A continent');
      expect(continent.areaSqMile, 3860000.0);
      expect(continent.areaSqKm, 10023000.0);
      expect(continent.population, 746419440);
      expect(continent.numCountry, 44);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'continent_id': 1,
        'continent_name': 'Test',
      };

      final continent = Continent.fromJson(json);

      expect(continent.continentId, 1);
      expect(continent.continentName, 'Test');
      expect(continent.description, isNull);
      expect(continent.areaSqMile, isNull);
      expect(continent.population, isNull);
    });

    test('formattedArea formats millions correctly', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        areaSqMile: 3860000,
        areaSqKm: 10023000,
      );

      expect(continent.formattedArea,
          '3.9 Million Square Miles (10.0 Million Square KM)');
    });

    test('formattedArea handles null values', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
      );

      expect(continent.formattedArea, 'N/A');
    });

    test('formattedArea handles only sqMile', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
        areaSqMile: 5000000,
      );

      expect(continent.formattedArea, '5.0 Million Square Miles');
    });

    test('formattedArea handles only sqKm', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
        areaSqKm: 12000000,
      );

      expect(continent.formattedArea, '12.0 Million Square KM');
    });

    test('formattedPopulation formats millions correctly', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Europe',
        population: 746419440,
      );

      expect(continent.formattedPopulation, '746.4 Million');
    });

    test('formattedPopulation formats billions correctly', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Asia',
        population: 4700000000,
      );

      expect(continent.formattedPopulation, '4.7 Billion');
    });

    test('formattedPopulation formats thousands correctly', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
        population: 50000,
      );

      expect(continent.formattedPopulation, '50.0 Thousand');
    });

    test('formattedPopulation handles small numbers', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
        population: 500,
      );

      expect(continent.formattedPopulation, '500');
    });

    test('formattedPopulation handles null', () {
      const continent = Continent(
        continentId: 1,
        continentName: 'Test',
      );

      expect(continent.formattedPopulation, 'N/A');
    });
  });
}
