import 'dart:io';
import 'dart:convert';
import 'package:path/path.dart' as path;
import 'logger.dart';

class SingBoxManager {
  static Process? _singBoxProcess;
  static bool _isRunning = false;

  // Server information from config.json
  static String get currentServerAddress => '94.131.110.172';
  static int get currentServerPort => 23209;
  static String get localProxyAddress => '127.0.0.1';
  static int get localProxyPort => 1080;

  static Future<bool> startSingBox() async {
    try {
      AppLogger.info('Starting sing-box...');
      
      // Путь к sing-box исполняемому файлу
      final singBoxPath = path.join(Directory.current.path, 'sing-box', 'sing-box.exe');
      final configPath = path.join(Directory.current.path, 'sing-box', 'config.json');
      
      // Проверяем существование файлов
      if (!await File(singBoxPath).exists()) {
        AppLogger.error('sing-box executable not found at: $singBoxPath');
        return false;
      }
      
      if (!await File(configPath).exists()) {
        AppLogger.error('sing-box config not found at: $configPath');
        return false;
      }
      
      AppLogger.info('sing-box executable found: $singBoxPath');
      AppLogger.info('sing-box config found: $configPath');
      
      // Запускаем sing-box
      _singBoxProcess = await Process.start(
        singBoxPath,
        ['run', '-c', configPath],
        workingDirectory: Directory.current.path,
      );
      
      if (_singBoxProcess != null) {
        _isRunning = true;
        AppLogger.info('sing-box started with PID: ${_singBoxProcess!.pid}');
        
        // Слушаем stdout для логирования
        _singBoxProcess!.stdout.transform(utf8.decoder).listen((data) {
          AppLogger.info('sing-box stdout: ${data.trim()}');
        });
        
        // Слушаем stderr для ошибок
        _singBoxProcess!.stderr.transform(utf8.decoder).listen((data) {
          AppLogger.error('sing-box stderr: ${data.trim()}');
        });
        
        // Ждем небольшое время для инициализации
        await Future.delayed(const Duration(seconds: 3));
        
        AppLogger.logSingBoxStatus('started');
        return true;
      }
      
      return false;
    } catch (e) {
      AppLogger.error('Failed to start sing-box', e);
      return false;
    }
  }

  static Future<void> stopSingBox() async {
    if (_singBoxProcess != null && _isRunning) {
      try {
        AppLogger.info('Stopping sing-box...');
        _singBoxProcess!.kill();
        await _singBoxProcess!.exitCode;
        _isRunning = false;
        AppLogger.logSingBoxStatus('stopped');
      } catch (e) {
        AppLogger.error('Error stopping sing-box', e);
      }
    }
  }

  static bool get isRunning => _isRunning;

  static Future<bool> testConnection() async {
    try {
      AppLogger.info('Testing sing-box connection...');
      
      // Простой тест соединения через SOCKS5 прокси
      final socket = await Socket.connect('127.0.0.1', 1080);
      socket.destroy();
      
      AppLogger.info('sing-box connection test successful');
      return true;
    } catch (e) {
      AppLogger.warning('sing-box connection test failed: $e');
      return false;
    }
  }

  static void logConnectionStats() {
    AppLogger.info('sing-box running: $_isRunning');
    if (_singBoxProcess != null) {
      AppLogger.info('sing-box PID: ${_singBoxProcess!.pid}');
    }
  }
}
