# CMakeLists.txt stub for webview_windows plugin - GitHub Actions compatible
cmake_minimum_required(VERSION 3.14)

# Create a stub plugin library to satisfy CMake requirements
add_library(webview_windows_plugin STATIC stub.cpp)

# Create a stub source file to make the library buildable
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/stub.cpp" 
  "// Stub implementation for webview_windows plugin in CI/CD environment\n"
  "extern \"C\" {\n"
  "  void webview_windows_plugin_register_with_registrar(void* registrar) {\n"
  "    // Stub implementation - no-op for build compatibility\n"
  "  }\n"
  "}\n"
)

# Set the source file
set_target_properties(webview_windows_plugin PROPERTIES
  SOURCES "${CMAKE_CURRENT_BINARY_DIR}/stub.cpp"
)

# Set up plugin interface
target_include_directories(webview_windows_plugin PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}"
)

# Define bundled libraries for this plugin (empty for stub)
set(webview_windows_bundled_libraries "" CACHE INTERNAL "webview_windows bundled libraries")

# Export the plugin library
set_target_properties(webview_windows_plugin PROPERTIES
  POSITION_INDEPENDENT_CODE ON
  INTERFACE_POSITION_INDEPENDENT_CODE ON
)
