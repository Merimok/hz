# Temporary fix for missing plugin symlinks in GitHub Actions
# This file temporarily disables plugins to allow basic Windows build

list(APPEND FLUTTER_PLUGIN_LIST
)

list(APPEND FLUTTER_FFI_PLUGIN_LIST
)

set(PLUGIN_BUNDLED_LIBRARIES)

# Empty plugin lists - no plugins to process
