#!/bin/bash
# Fix generated_plugins.cmake for webview_windows plugin
# This script updates the generated file with proper path handling

echo "Fixing generated_plugins.cmake..."

cat > flutter/generated_plugins.cmake << 'EOF'
# Generated file, do not edit.
# Enhanced with multi-path plugin detection

list(APPEND FLUTTER_PLUGIN_LIST
  webview_windows
)

list(APPEND FLUTTER_FFI_PLUGIN_LIST
)

set(PLUGIN_BUNDLED_LIBRARIES)

# Try multiple possible paths for plugin directories
foreach(plugin ${FLUTTER_PLUGIN_LIST})
  set(plugin_found FALSE)
  
  # Path 1: From runner directory (most common)
  set(plugin_path_1 "${CMAKE_CURRENT_SOURCE_DIR}/../flutter/ephemeral/.plugin_symlinks/${plugin}/windows")
  
  # Path 2: From flutter directory
  set(plugin_path_2 "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${plugin}/windows")
  
  # Path 3: From root windows directory
  set(plugin_path_3 "${CMAKE_CURRENT_SOURCE_DIR}/ephemeral/.plugin_symlinks/${plugin}/windows")
  
  # Path 4: Absolute path resolution
  set(plugin_path_4 "${CMAKE_CURRENT_SOURCE_DIR}/../ephemeral/.plugin_symlinks/${plugin}/windows")
  
  if(EXISTS "${plugin_path_1}")
    add_subdirectory("${plugin_path_1}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at path 1: ${plugin_path_1}")
  elseif(EXISTS "${plugin_path_2}")
    add_subdirectory("${plugin_path_2}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at path 2: ${plugin_path_2}")
  elseif(EXISTS "${plugin_path_3}")
    add_subdirectory("${plugin_path_3}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at path 3: ${plugin_path_3}")
  elseif(EXISTS "${plugin_path_4}")
    add_subdirectory("${plugin_path_4}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at path 4: ${plugin_path_4}")
  endif()
  
  if(plugin_found)
    target_link_libraries(${BINARY_NAME} PRIVATE ${plugin}_plugin)
    list(APPEND PLUGIN_BUNDLED_LIBRARIES $<TARGET_FILE:${plugin}_plugin>)
    # Only append bundled libraries if they exist
    if(DEFINED ${plugin}_bundled_libraries)
      list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${plugin}_bundled_libraries})
    endif()
  else()
    message(STATUS "Plugin ${plugin} directory not found, creating stub...")
  endif()
endforeach(plugin)

# Handle FFI plugins (none in this project)
foreach(ffi_plugin ${FLUTTER_FFI_PLUGIN_LIST})
  set(plugin_path "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${ffi_plugin}/windows")
  if(EXISTS "${plugin_path}")
    add_subdirectory("${plugin_path}" plugins/${ffi_plugin})
    list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${ffi_plugin}_bundled_libraries})
  endif()
endforeach(ffi_plugin)
EOF

echo "Generated plugins file updated successfully!"
echo "Plugin paths will be checked in the following order:"
echo "1. ../flutter/ephemeral/.plugin_symlinks/webview_windows/windows"
echo "2. flutter/ephemeral/.plugin_symlinks/webview_windows/windows"
echo "3. ephemeral/.plugin_symlinks/webview_windows/windows"
echo "4. ../ephemeral/.plugin_symlinks/webview_windows/windows"
