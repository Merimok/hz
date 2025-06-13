# Minimal CMakeLists.txt for webview_windows plugin
cmake_minimum_required(VERSION 3.14)

# Create a minimal plugin library
add_library(webview_windows_plugin INTERFACE)

# Define empty bundled libraries for this plugin
set(webview_windows_bundled_libraries "" CACHE INTERNAL "")
