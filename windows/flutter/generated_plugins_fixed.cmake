# Generated file, do not edit.
# Enhanced with multi-path plugin detection for Windows builds

list(APPEND FLUTTER_PLUGIN_LIST
  webview_windows
)

list(APPEND FLUTTER_FFI_PLUGIN_LIST
)

set(PLUGIN_BUNDLED_LIBRARIES)

foreach(plugin ${FLUTTER_PLUGIN_LIST})
  # Try multiple paths for plugin directories
  set(plugin_found FALSE)
  
  # Path 1: From runner directory (GitHub Actions context)
  set(plugin_path_1 "${CMAKE_CURRENT_SOURCE_DIR}/../flutter/ephemeral/.plugin_symlinks/${plugin}/windows")
  # Path 2: From flutter directory (local development)
  set(plugin_path_2 "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${plugin}/windows")
  # Path 3: From windows root (alternative)
  set(plugin_path_3 "${CMAKE_CURRENT_SOURCE_DIR}/ephemeral/.plugin_symlinks/${plugin}/windows")
  
  if(EXISTS "${plugin_path_1}")
    add_subdirectory("${plugin_path_1}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at: ${plugin_path_1}")
  elseif(EXISTS "${plugin_path_2}")
    add_subdirectory("${plugin_path_2}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at: ${plugin_path_2}")
  elseif(EXISTS "${plugin_path_3}")
    add_subdirectory("${plugin_path_3}" plugins/${plugin})
    set(plugin_found TRUE)
    message(STATUS "Found plugin ${plugin} at: ${plugin_path_3}")
  endif()
  
  if(plugin_found)
    target_link_libraries(${BINARY_NAME} PRIVATE ${plugin}_plugin)
    list(APPEND PLUGIN_BUNDLED_LIBRARIES $<TARGET_FILE:${plugin}_plugin>)
    # Only add bundled libraries if they exist and are not empty
    if(DEFINED ${plugin}_bundled_libraries AND ${plugin}_bundled_libraries)
      list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${plugin}_bundled_libraries})
    endif()
  else()
    message(STATUS "Plugin ${plugin} not found in any expected location - will create stub if needed")
  endif()
endforeach(plugin)

foreach(ffi_plugin ${FLUTTER_FFI_PLUGIN_LIST})
  set(ffi_plugin_path "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${ffi_plugin}/windows")
  if(EXISTS "${ffi_plugin_path}")
    add_subdirectory("${ffi_plugin_path}" plugins/${ffi_plugin})
    if(DEFINED ${ffi_plugin}_bundled_libraries AND ${ffi_plugin}_bundled_libraries)
      list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${ffi_plugin}_bundled_libraries})
    endif()
  endif()
endforeach(ffi_plugin)
