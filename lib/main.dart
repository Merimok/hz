import 'package:flutter/material.dart';
import 'dart:io';
import 'package:webview_windows/webview_windows.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'logger.dart';
import 'singbox_manager.dart';
import 'app_constants.dart' as constants;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Инициализируем логгер
  await AppLogger.initialize();
  AppLogger.info(constants.logAppStart);
  
  runApp(const FocusBrowserApp());
}

class FocusBrowserApp extends StatelessWidget {
  const FocusBrowserApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: constants.appTitle,
      theme: ThemeData.dark().copyWith(
        primarySwatch: constants.primaryMaterialColor,
        scaffoldBackgroundColor: constants.scaffoldBackgroundColor,
        appBarTheme: AppBarTheme(
          backgroundColor: constants.appBarBackgroundColor,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: constants.inputFillColor,
          border: const OutlineInputBorder(
            borderSide: BorderSide.none,
            borderRadius: BorderRadius.all(Radius.circular(8)),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
      home: const BrowserPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class BrowserPage extends StatefulWidget {
  const BrowserPage({super.key});

  @override
  State<BrowserPage> createState() => _BrowserPageState();
}

class _BrowserPageState extends State<BrowserPage> {
  final WebviewController _controller = WebviewController();
  final TextEditingController _urlController = TextEditingController();
  final FocusNode _urlFocusNode = FocusNode();
  final ValueNotifier<bool> _isLoading = ValueNotifier<bool>(false);
  bool _vpnConnected = false;
  String _currentUrl = constants.defaultHomePageUrl; // Use constant
  Uint8List? _favicon;

  @override
  void initState() {
    super.initState();
    AppLogger.info(constants.logInitializingBrowser); // Use constant
    _initializeVPN();
    _initializeWebView();
    
    // Auto-focus on address bar when app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _urlFocusNode.requestFocus();
    });
  }

  Future<void> _initializeVPN() async {
    try {
      AppLogger.info(constants.logVpnInitialization); // Use constant
      
      // Запускаем sing-box
      final success = await SingBoxManager.startSingBox();
      
      setState(() {
        _vpnConnected = success;
      });
      
      if (success) {
        AppLogger.logVpnConnection(true, SingBoxManager.currentServerAddress, SingBoxManager.currentServerPort); // Use SingBoxManager for details
        
        // Тестируем соединение
        await Future.delayed(constants.vpnTestDelayDuration); // Use constant
        final connectionTest = await SingBoxManager.testConnection();
        AppLogger.info('${constants.logVpnConnectionTestResult} ${connectionTest ? 'PASSED' : 'FAILED'}'); // Use constant
      } else {
        AppLogger.logVpnConnection(false, SingBoxManager.currentServerAddress, SingBoxManager.currentServerPort); // Use SingBoxManager for details
      }
    } catch (e) {
      AppLogger.error(constants.logVpnError, e); // Use constant
      setState(() {
        _vpnConnected = false;
      });
    }
  }

  // Ad blocking function
  bool _shouldBlockUrl(String url) {
    for (final domain in constants.blockedDomains) {
      if (url.contains(domain)) {
        AppLogger.info('${constants.adBlockedMessage}: $url');
        return true;
      }
    }
    return false;
  }

  Future<void> _initializeWebView() async {
    try {
      AppLogger.info(constants.logWebViewInitialization); // Use constant
      await _controller.initialize();
      
      // Set up ad blocking navigation delegate
      _controller.setNavigationDelegate((navigation) {
        if (_shouldBlockUrl(navigation.url)) {
          return NavigationDecision.prevent;
        }
        return NavigationDecision.navigate;
      });
      
      // Set up webview callbacks
      _controller.loadingState.listen((state) {
        _isLoading.value = state == LoadingState.loading;
        AppLogger.info('${constants.logWebViewStateChange} $state'); // Use constant
      });
      
      _controller.url.listen((url) {
        if (url.isNotEmpty) {
          _updateCurrentUrl(url);
          _fetchFavicon(url);
          // AppLogger.logNavigation(url, true); // Logging handled in _navigateToUrl and _updateCurrentUrl
        }
      });
      
      _urlController.text = _currentUrl;
      await _controller.loadUrl(_currentUrl);
      AppLogger.info('WebView initialized successfully for: $_currentUrl');
    } catch (e) {
      AppLogger.error('WebView initialization failed for $_currentUrl', e);
    }
  }

  void _updateCurrentUrl(String url) {
    setState(() {
      _currentUrl = url;
      _urlController.text = url;
    });
    AppLogger.info('Current URL updated to: $url');
  }

  Future<void> _fetchFavicon(String url) async {
    try {
      final uri = Uri.parse(url);
      final faviconUrl = '${uri.scheme}://${uri.host}/favicon.ico';
      
      final response = await http.get(Uri.parse(faviconUrl));
      if (response.statusCode == 200) {
        setState(() {
          _favicon = response.bodyBytes;
        });
      } else {
        setState(() {
          _favicon = null;
        });
      }
    } catch (e) {
      // Favicon fetch failed, use default icon
      AppLogger.error('Favicon fetch failed for $url', e);
      setState(() {
        _favicon = null;
      });
    }
  }

  Future<void> _navigateToUrl(String url) async {
    AppLogger.info('${constants.logNavigation} $url'); // Use constant
    _isLoading.value = true;
    
    String finalUrl = url.trim(); // Trim whitespace
    
    try {
      // Try to parse the URL first to catch obvious errors
      Uri.parse(finalUrl); // This will throw FormatException if invalid

      if (!finalUrl.startsWith('http://') && !finalUrl.startsWith('https://')) {
        if (finalUrl.contains('.') && !finalUrl.contains(' ')) {
          finalUrl = 'https://$finalUrl';
        } else {
          finalUrl = '${constants.searchEngineUrl}${Uri.encodeComponent(finalUrl)}'; // Use constant
        }
      }
    } catch (e) {
      AppLogger.error('Invalid URL format: $finalUrl', e);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(constants.urlInvalidMessage), // Use constant
          backgroundColor: Colors.red,
          duration: constants.snackBarDuration, // Use constant
        ),
      );
      _isLoading.value = false;
      return;
    }
    
    _urlController.text = finalUrl;
    // _currentUrl = finalUrl; // Let the webview callback update _currentUrl via _updateCurrentUrl

    try {
      await _controller.loadUrl(finalUrl);
      AppLogger.info('${constants.logNavigationSuccess} $finalUrl'); // Use constant
    } catch (e) {
      AppLogger.error('${constants.logNavigationFailed} $finalUrl', e); // Use constant
      // Optionally, show error to user via SnackBar
    }
    
    // Remove focus from address bar after navigation
    _urlFocusNode.unfocus();
  }

  Future<void> _clearDataAndRestart() async {
    AppLogger.info(constants.logClearingData); // Use constant
    try {
      // Clear browser cache and cookies
      await _controller.clearCache();
      await _controller.clearCookies();
      
      // Clear localStorage, sessionStorage, and cookies via JavaScript
      try {
        await _controller.executeScript('''
          // Clear localStorage
          if (typeof(Storage) !== "undefined") {
            localStorage.clear();
            sessionStorage.clear();
          }
          
          // Clear cookies via JavaScript
          document.cookie.split(";").forEach(function(c) { 
            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
          });
          
          console.log("🔥 Browser data cleared via JavaScript");
        ''');
      } catch (jsError) {
        AppLogger.error('JavaScript cleanup failed', jsError);
      }
      
      // Navigate to home page
      await _navigateToUrl(constants.defaultHomePageUrl); // Use constant
      
      AppLogger.info(constants.logDataCleared); // Use constant
      
      if (mounted) { // Check if widget is still in the tree
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(constants.cacheClearedMessage), // Use constant
            backgroundColor: Colors.orange,
            duration: constants.snackBarDuration, // Use constant
          ),
        );
      }
    } catch (e) {
      AppLogger.error(constants.logFailedToClearData, e); // Use constant
    }
  }

  Future<void> _toggleVPN() async {
    try {
      if (SingBoxManager.isRunning) {
        await SingBoxManager.stopSingBox();
        setState(() {
          _vpnConnected = false;
        });
        AppLogger.info('VPN disconnected');
      } else {
        final success = await SingBoxManager.startSingBox();
        setState(() {
          _vpnConnected = success;
        });
        if (success) {
          AppLogger.info('VPN connected successfully');
          // Test connection after a short delay
          await Future.delayed(constants.vpnTestDelayDuration);
          final connectionTest = await SingBoxManager.testConnection();
          AppLogger.info('${constants.logVpnConnectionTestResult} ${connectionTest ? 'PASSED' : 'FAILED'}');
        } else {
          AppLogger.error('Failed to connect VPN', null);
        }
      }
    } catch (e) {
      AppLogger.error('VPN toggle failed', e);
      setState(() {
        _vpnConnected = false;
      });
    }
  }

  void _showSettings() {
    AppLogger.info(constants.logOpeningSettings); // Use constant
    SingBoxManager.logConnectionStats();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF2D2D2D),
        title: const Text(constants.settingsDialogTitle), // Use constant
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // VPN Status and Toggle
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${constants.vpnStatusLabel} ${SingBoxManager.isRunning ? constants.vpnConnectedText : constants.vpnDisconnectedText}'), // Use constants
                Switch(
                  value: SingBoxManager.isRunning,
                  onChanged: (value) async {
                    Navigator.pop(context); // Close dialog first
                    await _toggleVPN();
                  },
                  activeColor: constants.primaryMaterialColor,
                ),
              ],
            ),
            Text('${constants.singboxStatusLabel} ${SingBoxManager.isRunning ? constants.singboxRunningText : constants.singboxStoppedText}'), // Use constants
            Text('${constants.vlessServerLabel} ${SingBoxManager.currentServerAddress}:${SingBoxManager.currentServerPort}'), // Use SingBoxManager for details
            Text('${constants.localProxyLabel} ${SingBoxManager.localProxyAddress}:${SingBoxManager.localProxyPort}'), // Use SingBoxManager for details
            const SizedBox(height: 16),
            Text('${constants.featuresLabel}'), // Use constant
            ...constants.featureList.map((feature) => Text(feature)), // Use constant list
            const SizedBox(height: 16),
            // Test Connection Button
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                final testResult = await SingBoxManager.testConnection();
                AppLogger.info('${constants.logVpnConnectionTestResult} ${testResult ? 'PASSED' : 'FAILED'}');
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Connection test: ${testResult ? 'PASSED' : 'FAILED'}'),
                    backgroundColor: testResult ? Colors.green : Colors.red,
                  ),
                );
              },
              child: const Text(constants.testConnectionButtonLabel), // Use constant
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(constants.closeButtonLabel), // Use constant
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    AppLogger.info(constants.logDisposingResources); // Use constant
    _controller.dispose();
    _urlController.dispose();
    _urlFocusNode.dispose();
    _isLoading.dispose();
    
    // Останавливаем sing-box
    SingBoxManager.stopSingBox();
    
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 60,
        title: Row(
          children: [
            // Back button
            IconButton(
              onPressed: () => _controller.goBack(),
              icon: const Icon(Icons.arrow_back_ios, size: constants.appBarIconSize), // Use constant
              tooltip: constants.backButtonTooltip, // Use constant
            ),
            
            // Forward button
            IconButton(
              onPressed: () => _controller.goForward(),
              icon: const Icon(Icons.arrow_forward_ios, size: constants.appBarIconSize), // Use constant
              tooltip: constants.forwardButtonTooltip, // Use constant
            ),
            
            const SizedBox(width: 8),
            
            // URL bar
            Expanded(
              child: Container(
                height: 40,
                child: ValueListenableBuilder<bool>(
                  valueListenable: _isLoading,
                  builder: (context, isLoading, child) {
                    return TextField(
                      controller: _urlController,
                      focusNode: _urlFocusNode,
                      onSubmitted: _navigateToUrl,
                      autofocus: true,
                      decoration: InputDecoration(
                        hintText: constants.urlBarHintText, // Use constant
                        prefixIcon: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const SizedBox(width: 12),
                            if (isLoading)
                              const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            else if (_favicon != null)
                              Image.memory(
                                _favicon!,
                                width: 16,
                                height: 16,
                                errorBuilder: (context, error, stackTrace) {
                                  // Consider logging favicon error here if needed
                                  return const Icon(Icons.web, size: 16);
                                },
                              )
                            else
                              const Icon(Icons.web, size: 16),
                            const SizedBox(width: 8),
                          ],
                        ),
                        contentPadding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
                      ),
                    );
                  },
                ),
              ),
            ),
            
            const SizedBox(width: 8),
            
            // Refresh button
            ValueListenableBuilder<bool>(
              valueListenable: _isLoading,
              builder: (context, isLoading, child) {
                return IconButton(
                  onPressed: isLoading ? null : () => _controller.reload(),
                  icon: isLoading 
                      ? const Icon(Icons.stop, size: constants.appBarIconSize) // Use constant
                      : const Icon(Icons.refresh, size: constants.appBarIconSize), // Use constant
                  tooltip: isLoading ? constants.stopButtonTooltip : constants.refreshButtonTooltip, // Use constants
                );
              },
            ),
            
            // Clear data button
            IconButton(
              onPressed: _clearDataAndRestart,
              icon: const Text('🔥', style: TextStyle(fontSize: constants.appBarTextIconSize)), // Use constant
              tooltip: constants.clearDataButtonTooltip, // Use constant
            ),
            
            // Settings button
            IconButton(
              onPressed: _showSettings,
              icon: const Text('⚙', style: TextStyle(fontSize: constants.appBarTextIconSize)), // Use constant
              tooltip: constants.settingsButtonTooltip, // Use constant
            ),
            
            // VPN toggle button
            Container(
              margin: const EdgeInsets.only(left: 8),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  borderRadius: BorderRadius.circular(8),
                  onTap: _toggleVPN,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: SingBoxManager.isRunning ? constants.vpnConnectedColor : constants.vpnDisconnectedColor,
                        width: 1,
                      ),
                    ),
                    child: Text(
                      SingBoxManager.isRunning ? constants.vpnConnectedText : constants.vpnDisconnectedText, // Use constants
                      style: TextStyle(
                        fontSize: 14,
                        color: SingBoxManager.isRunning ? constants.vpnConnectedColor : constants.vpnDisconnectedColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
      body: Webview(_controller),
    );
  }
}
