# GitHub Actions Plugin Stub Creator
# Creates missing plugin directories and CMakeLists.txt files
# for GitHub Actions compatibility

Write-Host "🔧 Creating plugin stubs for GitHub Actions..." -ForegroundColor Green

# Define plugin list (from pubspec.yaml dependencies)
$plugins = @("webview_windows")

foreach ($plugin in $plugins) {
    $pluginDir = "flutter\ephemeral\.plugin_symlinks\$plugin\windows"
    
    Write-Host "📁 Creating directory: $pluginDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $pluginDir | Out-Null
    
    # Create CMakeLists.txt for the plugin
    $cmakeContent = @"
# GitHub Actions Compatible Plugin Stub for $plugin
cmake_minimum_required(VERSION 3.14)

# Create stub source file
set(PLUGIN_NAME "$plugin")
set(STUB_SOURCE_FILE "`${CMAKE_CURRENT_BINARY_DIR}/${plugin}_stub.cpp")

# Write stub C++ implementation
file(WRITE "`${STUB_SOURCE_FILE}" "
// Auto-generated stub for $plugin plugin
// GitHub Actions compatibility implementation

extern \"C\" {

__declspec(dllexport) void ${plugin}_plugin_register_with_registrar(void* registrar) {
  // Stub implementation for GitHub Actions build compatibility
}

}
")

# Create plugin library
add_library(${plugin}_plugin STATIC "`${STUB_SOURCE_FILE}")

# Set required properties
set_target_properties(${plugin}_plugin PROPERTIES
  POSITION_INDEPENDENT_CODE ON
  CXX_STANDARD 17
)

# Initialize bundled libraries (empty for stub)
set(${plugin}_bundled_libraries "" CACHE INTERNAL "$plugin bundled libraries")

message(STATUS "✅ $plugin stub plugin created for GitHub Actions")
"@

    $cmakeFile = Join-Path $pluginDir "CMakeLists.txt"
    Write-Host "📝 Writing CMakeLists.txt: $cmakeFile" -ForegroundColor Yellow
    $cmakeContent | Out-File -FilePath $cmakeFile -Encoding UTF8
    
    Write-Host "✅ Created stub for plugin: $plugin" -ForegroundColor Green
}

Write-Host "🎉 All plugin stubs created successfully!" -ForegroundColor Green
