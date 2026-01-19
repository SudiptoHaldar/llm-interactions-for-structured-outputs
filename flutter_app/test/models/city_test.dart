import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/city.dart';

void main() {
  group('City', () {
    test('fromJson parses all fields correctly', () {
      final json = {
        'city_id': 1,
        'country_id': 10,
        'name': 'Test City',
        'is_capital': true,
        'description': 'A test city',
        'interesting_fact': 'It is a test',
        'area_sq_mile': 100.5,
        'area_sq_km': 260.3,
        'population': 1500000,
        'sci_score': 85.5,
        'sci_rank': 10,
        'numbeo_si': 72.3,
        'numbeo_ci': 27.7,
        'airport_code': 'TST',
      };

      final city = City.fromJson(json);

      expect(city.cityId, 1);
      expect(city.countryId, 10);
      expect(city.name, 'Test City');
      expect(city.isCapital, true);
      expect(city.population, 1500000);
      expect(city.sciScore, 85.5);
      expect(city.numbeoSi, 72.3);
      expect(city.numbeoCi, 27.7);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'city_id': 1,
        'name': 'Minimal City',
      };

      final city = City.fromJson(json);

      expect(city.cityId, 1);
      expect(city.name, 'Minimal City');
      expect(city.isCapital, false);
      expect(city.sciScore, isNull);
      expect(city.numbeoSi, isNull);
    });

    test('formattedPopulation formats millions', () {
      const city = City(cityId: 1, name: 'Big City', population: 5500000);
      expect(city.formattedPopulation, '5.5M');
    });

    test('formattedPopulation formats thousands', () {
      const city = City(cityId: 1, name: 'Small City', population: 250000);
      expect(city.formattedPopulation, '250K');
    });

    test('formattedPopulation handles null', () {
      const city = City(cityId: 1, name: 'Unknown City');
      expect(city.formattedPopulation, 'N/A');
    });

    test('formattedPopulation handles small numbers', () {
      const city = City(cityId: 1, name: 'Tiny City', population: 500);
      expect(city.formattedPopulation, '500');
    });
  });

  group('CityListResponse', () {
    test('fromJson parses list correctly', () {
      final json = {
        'cities': [
          {'city_id': 1, 'name': 'City A'},
          {'city_id': 2, 'name': 'City B'},
        ],
        'count': 2,
      };

      final response = CityListResponse.fromJson(json);

      expect(response.count, 2);
      expect(response.cities.length, 2);
      expect(response.cities[0].name, 'City A');
      expect(response.cities[1].name, 'City B');
    });

    test('fromJson handles empty list', () {
      final json = {
        'cities': <Map<String, dynamic>>[],
        'count': 0,
      };

      final response = CityListResponse.fromJson(json);

      expect(response.count, 0);
      expect(response.cities.isEmpty, true);
    });
  });
}
