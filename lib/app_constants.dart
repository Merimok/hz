import 'package:flutter/material.dart';

// Application Info
const String appTitle = 'Focus Browser';
const String appVersion = 'v1.0.5'; // Keep in sync with pubspec.yaml and main.dart logs/settings
const String appDescription = 'Minimalist browser with sing-box VPN';

// URLs
const String defaultHomePageUrl = 'https://www.perplexity.ai';
const String searchEngineUrl = 'https://www.perplexity.ai/search?q='; // {query} will be appended

// Ad Blocking & Tracking Protection
const List<String> blockedDomains = [
  'doubleclick.net',
  'googlesyndication.com',
  'googleadservices.com',
  'facebook.net',
  'connect.facebook.net',
  'analytics.google.com',
  'google-analytics.com',
  'googletagmanager.com',
  'googletagservices.com',
  'ads.yahoo.com',
  'adsystem.amazon.com',
  'amazon-adsystem.com',
  'bing.com/th',
  'outbrain.com',
  'taboola.com',
  'criteo.com',
  'adsafeprotected.com',
  'scorecardresearch.com',
  'quantserve.com',
  'addthis.com',
  'sharethis.com',
];

const String adBlockedMessage = '🛡️ Ad blocked';
const String trackerBlockedMessage = '🔒 Tracker blocked';

// UI Strings - AppBar
const String backButtonTooltip = 'Back';
const String forwardButtonTooltip = 'Forward';
const String urlBarHintText = 'Search or enter URL...';
const String refreshButtonTooltip = 'Refresh';
const String stopButtonTooltip = 'Stop';
const String clearDataButtonTooltip = 'Clear cache & restart';
const String settingsButtonTooltip = 'Settings';

// UI Strings - Settings Dialog
const String settingsDialogTitle = '⚙ Settings';
const String vpnStatusLabel = 'VPN Status:';
const String vpnConnectedText = '🟢 Connected';
const String vpnDisconnectedText = '🔴 Disconnected';
const String singboxStatusLabel = 'sing-box:';
const String singboxRunningText = 'Running';
const String singboxStoppedText = 'Stopped';
const String featuresLabel = 'Features:';
const List<String> featureList = [
  '• Advanced logging system',
  '• Pre-configured VLESS server',
  '• Loading indicators',
  '• Favicon support',
  '• Auto-focus address bar',
  '• sing-box VPN integration',
];
const String vlessServerLabel = 'VLESS Server:'; // Actual server details should come from SingBoxManager
const String localProxyLabel = 'Local Proxy:'; // Actual proxy details should come from SingBoxManager
const String testConnectionButtonLabel = 'Test Connection';
const String closeButtonLabel = 'Close';

// UI Strings - Messages
const String cacheClearedMessage = '🔥 Cache and cookies cleared';
const String urlInvalidMessage = 'Invalid URL entered';

// UI Icons & Sizes
const double appBarIconSize = 22.0; // Adjusted for better desktop visibility
const double appBarTextIconSize = 22.0;

// Colors (MaterialColor for primary color #4FC3F7)
const MaterialColor primaryMaterialColor = MaterialColor(
  0xFF4FC3F7,
  <int, Color>{
    50: Color(0xFFE8F7FE),
    100: Color(0xFFC5EBFC),
    200: Color(0xFF9FDDF9),
    300: Color(0xFF79CFF6),
    400: Color(0xFF5CC4F4),
    500: Color(0xFF4FC3F7), // Primary color
    600: Color(0xFF3FA9D9),
    700: Color(0xFF2F8CB8),
    800: Color(0xFF1F7096),
    900: Color(0xFF0F5474),
  },
);

const Color appBarBackgroundColor = Color(0xFF2D2D2D);
const Color scaffoldBackgroundColor = Color(0xFF1A1A1A);
const Color inputFillColor = Color(0xFF3D3D3D);
const Color vpnConnectedColor = Color(0xFF4CAF50);
const Color vpnDisconnectedColor = Color(0xFFF44336);

// Durations
const Duration snackBarDuration = Duration(seconds: 2);
const Duration vpnTestDelayDuration = Duration(seconds: 2);

// Logging
const String logAppStart = '=== \$appTitle \$appVersion Starting ===';
const String logInitializingBrowser = 'Initializing Focus Browser';
const String logVpnInitialization = 'Starting VPN initialization...';
const String logVpnConnectionTestResult = 'VPN connection test:'; // PASSED or FAILED will be appended
const String logVpnError = 'VPN initialization error';
const String logWebViewInitialization = 'Initializing WebView...';
const String logWebViewStateChange = 'WebView loading state:'; // state will be appended
const String logNavigation = 'Navigating to:'; // url will be appended
const String logNavigationSuccess = 'Navigation successful for:'; // url will be appended
const String logNavigationFailed = 'Navigation failed for:'; // url will be appended
const String logClearingData = 'Clearing browser data...';
const String logDataCleared = 'Browser data cleared successfully';
const String logFailedToClearData = 'Failed to clear browser data';
const String logOpeningSettings = 'Opening settings dialog';
const String logDisposingResources = 'Disposing Focus Browser resources';

