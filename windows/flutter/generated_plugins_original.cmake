# Generated file, do not edit.
#

list(APPEND FLUTTER_PLUGIN_LIST
  webview_windows
)

list(APPEND FLUTTER_FFI_PLUGIN_LIST
)

set(PLUGIN_BUNDLED_LIBRARIES)

foreach(plugin ${FLUTTER_PLUGIN_LIST})
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${plugin}/windows")
    add_subdirectory(flutter/ephemeral/.plugin_symlinks/${plugin}/windows plugins/${plugin})
    target_link_libraries(${BINARY_NAME} PRIVATE ${plugin}_plugin)
    list(APPEND PLUGIN_BUNDLED_LIBRARIES $<TARGET_FILE:${plugin}_plugin>)
    list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${plugin}_bundled_libraries})
  else()
    message(WARNING "Plugin ${plugin} directory not found, skipping...")
  endif()
endforeach(plugin)

foreach(ffi_plugin ${FLUTTER_FFI_PLUGIN_LIST})
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/flutter/ephemeral/.plugin_symlinks/${ffi_plugin}/windows")
    add_subdirectory(flutter/ephemeral/.plugin_symlinks/${ffi_plugin}/windows plugins/${ffi_plugin})
    list(APPEND PLUGIN_BUNDLED_LIBRARIES ${${ffi_plugin}_bundled_libraries})
  else()
    message(WARNING "FFI Plugin ${ffi_plugin} directory not found, skipping...")
  endif()
endforeach(ffi_plugin)
