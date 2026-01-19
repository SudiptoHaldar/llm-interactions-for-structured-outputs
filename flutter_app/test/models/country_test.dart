import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/country.dart';

void main() {
  group('Country', () {
    test('fromJson parses all fields correctly', () {
      final json = {
        'country_id': 1,
        'name': 'Test Country',
        'description': 'A test country',
        'ppp': 50000.50,
        'life_expectancy': 75.5,
        'global_peace_index_score': 2.5,
        'global_peace_index_rank': 50,
        'happiness_index_score': 7.5,
        'happiness_index_rank': 25,
        'gdp': 1000000.0,
        'gdp_growth_rate': 3.5,
        'inflation_rate': 2.0,
        'unemployment_rate': 5.5,
        'govt_debt': 45.0,
        'poverty_rate': 10.0,
        'gini_coefficient': 35.0,
        'continent_id': 1,
        'ai_model_id': 2,
      };

      final country = Country.fromJson(json);

      expect(country.countryId, 1);
      expect(country.name, 'Test Country');
      expect(country.ppp, 50000.50);
      expect(country.lifeExpectancy, 75.5);
      expect(country.globalPeaceIndexScore, 2.5);
      expect(country.happinessIndexScore, 7.5);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'country_id': 1,
        'name': 'Minimal Country',
      };

      final country = Country.fromJson(json);

      expect(country.countryId, 1);
      expect(country.name, 'Minimal Country');
      expect(country.ppp, isNull);
      expect(country.lifeExpectancy, isNull);
    });

    test('fromJson parses gdpPerCapita correctly', () {
      final json = {
        'country_id': 1,
        'name': 'Test Country',
        'gdp': 1000000000000.0,
        'gdp_per_capita': 45000.0,
      };

      final country = Country.fromJson(json);

      expect(country.gdp, 1000000000000.0);
      expect(country.gdpPerCapita, 45000.0);
    });

    test('fromJson handles null gdpPerCapita', () {
      final json = {
        'country_id': 1,
        'name': 'Test Country',
        'gdp': 500000000000.0,
      };

      final country = Country.fromJson(json);

      expect(country.gdp, 500000000000.0);
      expect(country.gdpPerCapita, isNull);
    });
  });

  group('CountryListResponse', () {
    test('fromJson parses list correctly', () {
      final json = {
        'countries': [
          {'country_id': 1, 'name': 'Country A'},
          {'country_id': 2, 'name': 'Country B'},
        ],
        'count': 2,
      };

      final response = CountryListResponse.fromJson(json);

      expect(response.count, 2);
      expect(response.countries.length, 2);
      expect(response.countries[0].name, 'Country A');
      expect(response.countries[1].name, 'Country B');
    });
  });
}
