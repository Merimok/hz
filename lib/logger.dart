import 'dart:io';
import 'package:logging/logging.dart';
import 'package:path/path.dart' as path;

class AppLogger {
  static final Logger _logger = Logger('FocusBrowser');
  static File? _logFile;
  static bool _initialized = false;

  static Future<void> initialize() async {
    if (_initialized) return;

    // Создаем папку logs если не существует
    final logsDir = Directory('logs');
    if (!logsDir.existsSync()) {
      logsDir.createSync(recursive: true);
    }

    // Создаем файл лога с текущей датой
    final now = DateTime.now();
    final logFileName = 'focus_browser_${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}.log';
    _logFile = File(path.join('logs', logFileName));

    // Настраиваем логирование
    Logger.root.level = Level.INFO;
    Logger.root.onRecord.listen((record) {
      final message = '${record.time} [${record.level.name}] ${record.loggerName}: ${record.message}';
      
      // Записываем в файл
      _logFile?.writeAsStringSync('$message\n', mode: FileMode.append);
      
      // Выводим в консоль (для отладки)
      print(message);
      
      // Обрабатываем ошибки
      if (record.error != null) {
        final errorMessage = 'Error: ${record.error}';
        _logFile?.writeAsStringSync('$errorMessage\n', mode: FileMode.append);
        print(errorMessage);
      }
      
      if (record.stackTrace != null) {
        final stackMessage = 'Stack trace:\n${record.stackTrace}';
        _logFile?.writeAsStringSync('$stackMessage\n', mode: FileMode.append);
        print(stackMessage);
      }
    });

    _initialized = true;
    _logger.info('Logger initialized. Log file: ${_logFile?.path}');
  }

  static void info(String message) => _logger.info(message);
  static void warning(String message) => _logger.warning(message);
  static void severe(String message) => _logger.severe(message);
  static void error(String message, [Object? error, StackTrace? stackTrace]) {
    _logger.severe(message, error, stackTrace);
  }

  static void logVpnConnection(bool connected, String server, int port) {
    if (connected) {
      info('VPN connected to $server:$port');
    } else {
      warning('VPN disconnected from $server:$port');
    }
  }

  static void logNavigation(String url, bool success) {
    if (success) {
      info('Navigation successful: $url');
    } else {
      warning('Navigation failed: $url');
    }
  }

  static void logSingBoxStatus(String status) {
    info('sing-box status: $status');
  }
}
