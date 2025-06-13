# Developer Documentation - Hz Browser

## 🔧 Technical Architecture

### Application Stack
- **Frontend:** Flutter 3.24.0+
- **Platform:** Windows 10/11 (x64)
- **WebView:** webview_windows plugin
- **VPN Backend:** sing-box
- **Build System:** CMake + MSBuild
- **Language:** Dart + C++ (native components)

## 📐 Project Structure Deep Dive

### Core Application (`lib/`)

#### `main.dart` - Application Entry Point
```dart
class MyApp extends StatelessWidget {
  // Main application widget with MaterialApp configuration
  // Theme setup and routing configuration
}

class WebViewScreen extends StatefulWidget {
  // Primary browser interface
  // WebView management and navigation controls
}
```

**Key Components:**
- WebView controller initialization
- Navigation delegate setup
- URL filtering and ad blocking
- VPN toggle integration

#### `app_constants.dart` - Configuration Hub
```dart
class AppConstants {
  // Blocked domains list (20+ entries)
  static const List<String> blockedDomains = [...];
  
  // Custom MaterialColor theme
  static const MaterialColor primaryMaterialColor = [...];
  
  // VPN configuration constants
  static const String singBoxPath = 'sing-box/sing-box.exe';
}
```

#### `singbox_manager.dart` - VPN Management
```dart
class SingBoxManager {
  static bool isRunning = false;
  
  static Future<void> startSingBox() async {
    // Process management for sing-box VPN
  }
  
  static Future<void> stopSingBox() async {
    // Graceful VPN disconnection
  }
}
```

### Windows Platform Integration (`windows/`)

#### CMake Build System
- **Main CMake:** `windows/CMakeLists.txt`
- **Flutter Integration:** `windows/flutter/CMakeLists.txt`
- **Runner Application:** `windows/runner/CMakeLists.txt`
- **Plugin Management:** `windows/flutter/generated_plugins.cmake`

#### Plugin Architecture
The webview_windows plugin stub provides:
```cpp
extern "C" {
  void webview_windows_plugin_register_with_registrar(void* registrar) {
    // Plugin registration for CI/CD compatibility
  }
}
```

## 🛠️ Development Workflow

### Setting Up Development Environment

#### Prerequisites Installation
```bash
# Windows requirements
# 1. Visual Studio 2019+ with C++ build tools
# 2. Windows 10 SDK
# 3. CMake 3.14+
# 4. Git for Windows

# Flutter setup
flutter doctor -v
flutter config --enable-windows-desktop
```

#### Project Setup
```bash
# Clone and setup
git clone <repository>
cd hz
flutter clean
flutter pub get
flutter pub deps
```

### Build Process

#### Debug Build
```bash
flutter run -d windows --debug
```

#### Release Build
```bash
flutter build windows --release
```

#### CMake Direct Build
```bash
cd windows
cmake -B build -S .
cmake --build build --config Release
```

### Testing Framework

#### Unit Tests
```dart
// test/unit/
test('VPN manager starts correctly', () async {
  await SingBoxManager.startSingBox();
  expect(SingBoxManager.isRunning, true);
});
```

#### Widget Tests
```dart
// test/widget/
testWidgets('Browser loads homepage', (WidgetTester tester) async {
  await tester.pumpWidget(MyApp());
  expect(find.byType(WebViewScreen), findsOneWidget);
});
```

#### Integration Tests
```dart
// integration_test/
testWidgets('Complete browser workflow', (WidgetTester tester) async {
  // Full user journey testing
});
```

## 🔍 Code Quality & Standards

### Dart Conventions
- **Naming:** camelCase for variables, PascalCase for classes
- **Documentation:** Dartdoc comments for public APIs
- **Formatting:** `dart format` with 80-character line limit
- **Analysis:** `dart analyze` with no warnings

### C++ Standards
- **Version:** C++17
- **Style:** Google C++ Style Guide
- **Memory Management:** RAII principles
- **Error Handling:** Exception-safe code

### CMake Best Practices
- **Version:** CMake 3.14+ features
- **Targets:** Modern target-based approach
- **Properties:** Generator expressions for configuration
- **Dependencies:** Proper target linking

## 🚀 Performance Optimization

### Flutter Performance
```dart
// Widget optimization
class WebViewScreen extends StatefulWidget {
  const WebViewScreen({super.key}); // Key parameter for widget identity
  
  @override
  State<WebViewScreen> createState() => _WebViewScreenState();
}

// Efficient setState usage
void _updateUrl(String url) {
  if (mounted) { // Check widget is still in tree
    setState(() {
      _currentUrl = url;
    });
  }
}
```

### Memory Management
- **WebView:** Proper controller disposal
- **Streams:** Subscription cancellation
- **File I/O:** Asynchronous operations
- **Process Management:** VPN process lifecycle

### Network Optimization
```dart
// Efficient URL filtering
bool _shouldBlockUrl(String url) {
  return AppConstants.blockedDomains.any((domain) => 
    url.toLowerCase().contains(domain.toLowerCase())
  );
}
```

## 🔐 Security Implementation

### Network Security
```dart
// URL validation
bool _isValidUrl(String url) {
  try {
    final uri = Uri.parse(url);
    return uri.hasScheme && (uri.scheme == 'http' || uri.scheme == 'https');
  } catch (e) {
    return false;
  }
}
```

### VPN Security
- **Configuration Validation:** JSON schema validation
- **Process Isolation:** Separate VPN process
- **Memory Protection:** Secure credential storage
- **Network Isolation:** Traffic routing verification

### Application Security
```dart
// Secure storage
class SecureStorage {
  static const _storage = FlutterSecureStorage();
  
  static Future<void> storeCredentials(String key, String value) async {
    await _storage.write(key: key, value: value);
  }
}
```

## 🐛 Debugging & Troubleshooting

### Debug Configuration
```json
// .vscode/launch.json
{
  "configurations": [
    {
      "name": "Hz Browser (Windows)",
      "request": "launch",
      "type": "dart",
      "args": ["-d", "windows"]
    }
  ]
}
```

### Logging Setup
```dart
// lib/logger.dart
class Logger {
  static void info(String message) {
    print('[INFO] ${DateTime.now()}: $message');
  }
  
  static void error(String message, [dynamic error]) {
    print('[ERROR] ${DateTime.now()}: $message');
    if (error != null) print('Details: $error');
  }
}
```

### Common Issues & Solutions

#### CMake Build Failures
```bash
# Clear CMake cache
rm -rf windows/build
cd windows && cmake -B build -S .
```

#### Plugin Errors
```dart
// Check plugin registration
void _checkPlugins() {
  if (kDebugMode) {
    print('Available plugins: ${Platform.environment}');
  }
}
```

#### VPN Connection Issues
```dart
// VPN diagnostics
Future<bool> _testVpnConnection() async {
  try {
    final result = await Process.run('ping', ['-n', '1', '8.8.8.8']);
    return result.exitCode == 0;
  } catch (e) {
    Logger.error('VPN test failed', e);
    return false;
  }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/build.yml
name: Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: flutter test
      - run: flutter build windows
```

### Build Artifacts
- **Executable:** `build/windows/x64/runner/Release/hz.exe`
- **Dependencies:** DLL files in release directory
- **Configuration:** Config files in expected locations

### Deployment Automation
```powershell
# deploy.ps1
$BuildPath = "build\windows\x64\runner\Release"
$DeployPath = "deploy\hz-browser"

Copy-Item -Recurse $BuildPath $DeployPath
Compress-Archive $DeployPath "hz-browser-release.zip"
```

## 📊 Metrics & Analytics

### Performance Metrics
```dart
// Performance monitoring
class PerformanceMonitor {
  static Stopwatch _loadTime = Stopwatch();
  
  static void startPageLoad() {
    _loadTime.start();
  }
  
  static void endPageLoad() {
    _loadTime.stop();
    Logger.info('Page load time: ${_loadTime.elapsedMilliseconds}ms');
    _loadTime.reset();
  }
}
```

### Memory Monitoring
```dart
// Memory usage tracking
void _checkMemoryUsage() {
  if (kDebugMode) {
    final info = ProcessInfo.currentRss;
    Logger.info('Memory usage: ${info ~/ 1024 ~/ 1024} MB');
  }
}
```

## 🔮 Future Enhancements

### Planned Architecture Changes
- **Multi-tab Support:** Tab management system
- **Extension API:** Plugin architecture for extensions
- **Advanced Caching:** Intelligent cache management
- **Performance Profiling:** Built-in performance tools

### Technical Debt
- **Code Coverage:** Increase to 90%+
- **Documentation:** Complete API documentation
- **Error Handling:** Comprehensive error recovery
- **Accessibility:** Full WCAG compliance

---

**Documentation Version:** 1.0.1  
**Target Audience:** Developers, Contributors  
**Maintenance:** Updated with each major release  
**Status:** ✅ Current and Complete
