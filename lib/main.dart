import 'package:flutter/material.dart';
import 'dart:io';
import 'package:webview_windows/webview_windows.dart';

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
  Process? _singBoxProcess;
  bool _isLoading = false;
  bool _vpnConnected = false;
  String _currentUrl = 'https://www.perplexity.ai';

  @override
  void initState() {
    super.initState();
    _initializeVPN();
    _initializeWebView();
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
        
        // Даем время на подключение VPN
        await Future.delayed(const Duration(seconds: 2));
      }
    } catch (e) {
      print('VPN initialization error: $e');
    }
  }

  Future<void> _initializeWebView() async {
    await _controller.initialize();
    _urlController.text = _currentUrl;
    await _controller.loadUrl(_currentUrl);
  }

  Future<void> _navigateToUrl(String url) async {
    setState(() {
      _isLoading = true;
    });
    
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
    
    setState(() {
      _isLoading = false;
    });
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
            const Text('Focus Browser v1.0.0'),
            const Text('Minimalist browser with VPN support'),
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
                child: TextField(
                  controller: _urlController,
                  onSubmitted: _navigateToUrl,
                  decoration: InputDecoration(
                    hintText: 'Search or enter URL...',
                    prefixIcon: _isLoading 
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: Padding(
                              padding: EdgeInsets.all(12),
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                          )
                        : const Icon(Icons.search, size: 20),
                    contentPadding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
            ),
            
            const SizedBox(width: 8),
            
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
