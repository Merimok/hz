# CMakeLists.txt stub for webview_windows plugin
cmake_minimum_required(VERSION 3.14)

# Create a stub plugin library to satisfy CMake requirements
add_library(webview_windows_plugin INTERFACE)

# Set up plugin interface
target_include_directories(webview_windows_plugin INTERFACE
  "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

# Define bundled libraries for this plugin (empty for stub)
set(webview_windows_bundled_libraries "" CACHE INTERNAL "webview_windows bundled libraries")

# Export the plugin library
set_target_properties(webview_windows_plugin PROPERTIES
  INTERFACE_POSITION_INDEPENDENT_CODE ON
)
