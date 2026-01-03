import 'package:flutter_test/flutter_test.dart';
import 'package:llm_interactions_app/models/health_response.dart';

void main() {
  group('HealthResponse', () {
    test('fromJson creates valid instance', () {
      final json = {
        'status': 'healthy',
        'version': '1.0.0',
        'database_connected': true,
        'timestamp': '2026-01-02T12:00:00Z',
      };

      final health = HealthResponse.fromJson(json);

      expect(health.status, equals('healthy'));
      expect(health.version, equals('1.0.0'));
      expect(health.databaseConnected, isTrue);
      expect(health.timestamp, equals('2026-01-02T12:00:00Z'));
      expect(health.isHealthy, isTrue);
    });

    test('fromJson handles missing fields with defaults', () {
      final json = <String, dynamic>{};

      final health = HealthResponse.fromJson(json);

      expect(health.status, equals('unknown'));
      expect(health.version, equals('0.0.0'));
      expect(health.databaseConnected, isFalse);
      expect(health.timestamp, equals(''));
      expect(health.isHealthy, isFalse);
    });

    test('toJson produces correct map', () {
      const health = HealthResponse(
        status: 'healthy',
        version: '2.0.0',
        databaseConnected: true,
        timestamp: '2026-01-02T15:30:00Z',
      );

      final json = health.toJson();

      expect(json['status'], equals('healthy'));
      expect(json['version'], equals('2.0.0'));
      expect(json['database_connected'], isTrue);
      expect(json['timestamp'], equals('2026-01-02T15:30:00Z'));
    });

    test('isHealthy returns false for non-healthy status', () {
      const health = HealthResponse(
        status: 'degraded',
        version: '1.0.0',
        databaseConnected: true,
        timestamp: '',
      );

      expect(health.isHealthy, isFalse);
    });

    test('toString returns formatted string', () {
      const health = HealthResponse(
        status: 'healthy',
        version: '1.0.0',
        databaseConnected: true,
        timestamp: '2026-01-02',
      );

      final result = health.toString();

      expect(result, contains('status: healthy'));
      expect(result, contains('version: 1.0.0'));
      expect(result, contains('databaseConnected: true'));
    });
  });
}
