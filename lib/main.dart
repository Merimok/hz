import 'package:flutter/material.dart';
import 'dart:io';
import 'package:webview_windows/webview_windows.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';

void main() {
  runApp(const FocusBrowserApp());
}

class FocusBrowserApp extends StatelessWidget {
  const FocusBrowserApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Focus Browser',
      theme: ThemeData.dark().copyWith(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF1A1A1A),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF2D2D2D),
          elevation: 0,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          filled: true,
          fillColor: Color(0xFF3D3D3D),
          border: OutlineInputBorder(
            borderSide: BorderSide.none,
            borderRadius: BorderRadius.all(Radius.circular(8)),
          ),
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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
  Process? _singBoxProcess;
  bool _vpnConnected = false;
  String _currentUrl = 'https://www.perplexity.ai';
  Uint8List? _favicon;

  @override
  void initState() {
    super.initState();
    _initializeVPN();
    _initializeWebView();
    
    // Auto-focus on address bar when app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _urlFocusNode.requestFocus();
    });
  }

  Future<void> _initializeVPN() async {
    try {
      final singBoxPath = '${Directory.current.path}/sing-box/sing-box.exe';
      final configPath = '${Directory.current.path}/sing-box/config.json';
      
      if (await File(singBoxPath).exists() && await File(configPath).exists()) {
        _singBoxProcess = await Process.start(
          singBoxPath,
          ['run', '-c', configPath],
        );
        
        setState(() {
          _vpnConnected = true;
        });
        
        // Give VPN time to connect
        await Future.delayed(const Duration(seconds: 2));
      }
    } catch (e) {
      print('VPN initialization error: $e');
    }
  }

  Future<void> _initializeWebView() async {
    await _controller.initialize();
    
    // Set up navigation delegate
    _controller.navigationDelegate = NavigationDelegate(
      onNavigationStart: (url) {
        _isLoading.value = true;
        _updateCurrentUrl(url);
        _fetchFavicon(url);
        return NavigationDecision.navigate;
      },
      onPageFinished: (url) {
        _isLoading.value = false;
        _updateCurrentUrl(url);
      },
    );
    
    _urlController.text = _currentUrl;
    await _controller.loadUrl(_currentUrl);
  }

  void _updateCurrentUrl(String url) {
    setState(() {
      _currentUrl = url;
      _urlController.text = url;
    });
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
      }
    } catch (e) {
      // Favicon fetch failed, use default icon
      setState(() {
        _favicon = null;
      });
    }
  }

  Future<void> _navigateToUrl(String url) async {
    _isLoading.value = true;
    
    String finalUrl = url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      if (url.contains('.') && !url.contains(' ')) {
        finalUrl = 'https://$url';
      } else {
        finalUrl = 'https://www.perplexity.ai/search?q=${Uri.encodeComponent(url)}';
      }
    }
    
    _urlController.text = finalUrl;
    _currentUrl = finalUrl;
    await _controller.loadUrl(finalUrl);
    
    // Remove focus from address bar after navigation
    _urlFocusNode.unfocus();
  }

  Future<void> _clearDataAndRestart() async {
    await _controller.clearCache();
    await _controller.clearCookies();
    await _navigateToUrl('https://www.perplexity.ai');
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🔥 Cache and cookies cleared'),
        backgroundColor: Colors.orange,
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _showSettings() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF2D2D2D),
        title: const Text('⚙ Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('VPN Status: ${_vpnConnected ? "🟢 Connected" : "🔴 Disconnected"}'),
            const SizedBox(height: 16),
            const Text('Focus Browser v1.0.2'),
            const Text('Minimalist browser with VPN support'),
            const SizedBox(height: 16),
            const Text('Features:'),
            const Text('• Loading indicators'),
            const Text('• Favicon support'),
            const Text('• Auto-focus address bar'),
            const Text('• sing-box VPN integration'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _urlFocusNode.dispose();
    _isLoading.dispose();
    _singBoxProcess?.kill();
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
              icon: const Icon(Icons.arrow_back_ios, size: 20),
              tooltip: 'Back',
            ),
            
            // Forward button
            IconButton(
              onPressed: () => _controller.goForward(),
              icon: const Icon(Icons.arrow_forward_ios, size: 20),
              tooltip: 'Forward',
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
                        hintText: 'Search or enter URL...',
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
                      ? const Icon(Icons.stop, size: 20)
                      : const Icon(Icons.refresh, size: 20),
                  tooltip: isLoading ? 'Stop' : 'Refresh',
                );
              },
            ),
            
            // Clear data button
            IconButton(
              onPressed: _clearDataAndRestart,
              icon: const Text('🔥', style: TextStyle(fontSize: 20)),
              tooltip: 'Clear cache & restart',
            ),
            
            // Settings button
            IconButton(
              onPressed: _showSettings,
              icon: const Text('⚙', style: TextStyle(fontSize: 20)),
              tooltip: 'Settings',
            ),
            
            // VPN status
            Container(
              margin: const EdgeInsets.only(left: 8),
              child: Text(
                _vpnConnected ? '🟢' : '🔴',
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
      body: Webview(_controller),
    );
  }
}
