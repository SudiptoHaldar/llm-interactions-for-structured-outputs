# LLM Interactions Flutter App

Flutter frontend for the LLM Interactions application.

## Features

- Health check screen displaying backend server status
- Navy Blue theme with Material Design 3
- Dark mode support
- Pull-to-refresh functionality

## Project Structure

```
flutter_app/
├── lib/
│   ├── config/
│   │   └── api_config.dart      # API configuration
│   ├── models/
│   │   └── health_response.dart # Health response DTO
│   ├── screens/
│   │   └── health_screen.dart   # Health status screen
│   ├── services/
│   │   └── api_client.dart      # HTTP client for backend
│   ├── theme/
│   │   ├── app_colors.dart      # Color constants
│   │   └── app_theme.dart       # Material 3 theme
│   ├── widgets/
│   │   └── status_card.dart     # Reusable status card
│   └── main.dart                # App entry point
└── test/
    ├── models/
    │   └── health_response_test.dart
    ├── widgets/
    │   └── status_card_test.dart
    └── widget_test.dart
```

## Getting Started

### Prerequisites

- Flutter SDK 3.10.4 or later
- Backend server running on port 8017

### Installation

```bash
cd flutter_app
flutter pub get
```

### Running the App

```bash
# Run on default device
flutter run

# Run on web
flutter run -d chrome

# Run on specific device
flutter devices  # List available devices
flutter run -d <device-id>
```

### Running Tests

```bash
flutter test
```

## Configuration

The API base URL is configured in `lib/config/api_config.dart`:

```dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8017';
  // ...
}
```

## Theme

The app uses a Navy Blue theme with Teal accents:

| Color | Hex | Usage |
|-------|-----|-------|
| Navy Blue | `#1A237E` | Primary color, AppBar |
| Teal | `#008B8B` | Accent color, FAB |
| Sea Green | `#2E8B57` | Tertiary color |
| Positive | `#2E7D32` | Success states |
| Negative | `#C62828` | Error states |

## Backend API

The app expects the backend to be running at `http://localhost:8017` with the following endpoint:

- `GET /api/v1/health` - Returns server health status

### Health Response Schema

```json
{
  "status": "healthy",
  "version": "0.5.0",
  "database_connected": true,
  "timestamp": "2026-01-02T12:00:00Z"
}
```
