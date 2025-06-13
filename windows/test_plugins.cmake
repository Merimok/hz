# Test file to verify plugin syntax
message(STATUS "🧪 Test message from test_plugins.cmake")
message(STATUS "🔍 Test BINARY_NAME = ${BINARY_NAME}")

list(APPEND FLUTTER_PLUGIN_LIST
  webview_windows
)

foreach(plugin ${FLUTTER_PLUGIN_LIST})
  message(STATUS "🔍 Processing plugin: ${plugin}")
endforeach()

message(STATUS "✅ Test completed successfully")
