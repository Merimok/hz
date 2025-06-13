import 'dart:io';
import 'dart:convert';
import 'package:path/path.dart' as path;
import 'logger.dart';

//           i        AppLogger.info('sing-box started with PID: ${_singBoxProcess!.pid}'); (_singBoxProcess != null) {
        _isRunning = true;
        AppLogger.info('sing-box started with PID: ${_singBoxProcess!.pid}');

        // Improved output buffering
        _singBoxProcess!.stdout.transform(utf8.decoder).listen((data) {singBoxProcess != null) {
        _isRunning = true;
        AppLogger.info('sing-box started with PID: ${_singBoxProcess!.pid}');

        // Improved output buffering
        _singBoxProcess!.stdout.transform(utf8.decoder).listen((data) {nager class for controlling the sing-box proxy service
class SingBoxManager {
  static Process? _singBoxProcess;
  static bool _isRunning = false;

  // Server information
  // Configuration loaded from JSON (defaults provided if config loading fails)
  static String _serverAddress = '94.131.110.172';
  static int _serverPort = 23209;
  static String _localProxyAddress = '127.0.0.1';
  static int _localProxyPort = 1080;
  
  // Getters for server information
  static String get currentServerAddress => _serverAddress;
  static int get currentServerPort => _serverPort;
  static String get localProxyAddress => _localProxyAddress;
  static int get localProxyPort => _localProxyPort;
  
  /// Loads server configuration from config file
  static Future<bool> loadServerConfig() async {
    try {
      final configPath = path.join(Directory.current.path, 'sing-box', 'config.json');
      if (await File(configPath).exists()) {
        final configContent = await File(configPath).readAsString();
        final config = json.decode(configContent);
        
        // Update server information if available in config
        // This assumes a specific structure in your config.json
        if (config.containsKey('outbounds') && config['outbounds'] is List) {
          for (var outbound in config['outbounds']) {
            if (outbound['type'] == 'direct' && outbound.containsKey('server')) {
              _serverAddress = outbound['server'];
              if (outbound.containsKey('server_port')) {
                _serverPort = outbound['server_port'];
              }
            }
            if (outbound['type'] == 'socks' && outbound.containsKey('listen')) {
              _localProxyAddress = outbound['listen'];
              if (outbound.containsKey('listen_port')) {
                _localProxyPort = outbound['listen_port'];
              }
            }
          }
        }
        
        AppLogger.info('Server configuration loaded successfully');
        return true;
      }
    } catch (e) {
      AppLogger.error('Error loading server configuration: $e');
    }
    
    AppLogger.warning('Using default server configuration');
    return false;
  }

  /// Starts the sing-box proxy service
  ///
  /// Returns true if the service started successfully, false otherwise
  static Future<bool> startSingBox() async {
    try {
      AppLogger.info('Starting sing-box...');

      // Path to sing-box executable file
      final singBoxPath = path.join(Directory.current.path, 'sing-box', 
          Platform.isWindows ? 'sing-box.exe' : 'sing-box');
      final configPath = path.join(Directory.current.path, 'sing-box', 'config.json');

      // Check if files exist
      if (!await File(singBoxPath).exists()) {
        AppLogger.error('sing-box executable not found at: $singBoxPath');
        return false;
      }

      if (!await File(configPath).exists()) {
        AppLogger.error('sing-box config not found at: $configPath');
        return false;
      }

      // Validate config file format
      try {
        final configContent = await File(configPath).readAsString();
        json.decode(configContent); // Validate JSON format
      } catch (e) {
        AppLogger.error('Invalid config file format: $e');
        return false;
      }

      AppLogger.info('sing-box executable found: $singBoxPath');
      AppLogger.info('sing-box config found: $configPath');

      // Load server configuration before starting
      await loadServerConfig();
      
      // Start sing-box process
      _singBoxProcess = await Process.start(
        singBoxPath,
        ['run', '-c', configPath],
        workingDirectory: Directory.current.path,
        runInShell: true, // Run through shell for better compatibility
      );

      if (_singBoxProcess != null) {
        _isRunning = true;
        AppLogger.info('sing-box started with PID: [32m[1m${_singBoxProcess!.pid}[0m'); // Цветной PID

        // Improved output buffering
        _singBoxProcess!.stdout.transform(utf8.decoder).listen((data) {
          for (final line in data.split('\n')) {
            if (line.trim().isNotEmpty) {
              AppLogger.info('sing-box stdout: ${line.trim()}');
            }
          }
        });

        _singBoxProcess!.stderr.transform(utf8.decoder).listen((data) {
          for (final line in data.split('\n')) {
            if (line.trim().isNotEmpty) {
              AppLogger.error('sing-box stderr: ${line.trim()}');
            }
          }
        });

        // Wait a short time for initialization
        await Future.delayed(const Duration(seconds: 3));
        
        // Set up process watcher to handle unexpected terminations
        setupProcessWatcher();

        AppLogger.logSingBoxStatus('started');
        return true;
      }

      return false;
    } catch (e, st) {
      AppLogger.error('Failed to start sing-box', e);
      AppLogger.error('StackTrace', st);
      return false;
    }
  }

  /// Stops the sing-box proxy service
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

  /// Gets the current running state of the service
  static bool get isRunning => _isRunning;

  /// Tests the connection to the proxy server with retry logic
  ///
  /// Returns true if connection is successful, false otherwise
  /// [maxRetries] - Maximum number of connection attempts
  /// [retryDelay] - Delay in seconds between retries
  static Future<bool> testConnection({int maxRetries = 3, int retryDelay = 2}) async {
    int attempts = 0;
    
    while (attempts < maxRetries) {
      try {
        attempts++;
        AppLogger.info('Testing sing-box connection (attempt $attempts of $maxRetries)...');

        // Add timeout to connection test
        final socket = await Socket.connect(
          localProxyAddress,
          localProxyPort,
          timeout: const Duration(seconds: 5),
        );
        await socket.close();

        AppLogger.info('sing-box connection test successful');
        return true;
      } catch (e) {
        if (attempts >= maxRetries) {
          AppLogger.warning('sing-box connection test failed after $maxRetries attempts: $e');
          return false;
        }
        
        AppLogger.info('Connection attempt $attempts failed, retrying in $retryDelay seconds...');
        await Future.delayed(Duration(seconds: retryDelay));
      }
    }
    
    return false;
  }

  static void logConnectionStats() {
    AppLogger.info('sing-box running: $_isRunning');
    if (_singBoxProcess != null) {
      AppLogger.info('sing-box PID: ${_singBoxProcess!.pid}');
    }
  }
  
  /// Sets up a process exit handler to detect unexpected terminations
  static void setupProcessWatcher() {
    if (_singBoxProcess != null) {
      _singBoxProcess!.exitCode.then((exitCode) {
        if (_isRunning) {
          // Process terminated unexpectedly while we thought it was running
          _isRunning = false;
          AppLogger.warning('sing-box process terminated unexpectedly with exit code: $exitCode');
          AppLogger.logSingBoxStatus('terminated unexpectedly');
        }
      }).catchError((error) {
        AppLogger.error('Error watching sing-box process: $error');
      });
    }
  }
}
