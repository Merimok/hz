#!/bin/bash
# GitHub Actions CMake Test Script
# This script tests that the CMake fix for GitHub Actions works correctly

# Set to exit on error
set -e

echo "🔍 Testing GitHub Actions CMake Fix..."
echo "========================================"

# Create test directory
TEST_DIR=$(mktemp -d)
echo "📁 Created test directory: $TEST_DIR"

# Determine repo root dynamically
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Copy relevant CMake files
echo "📋 Copying CMake files for testing..."
cp "$REPO_ROOT/windows/flutter/generated_plugins_github_actions_fixed.cmake" "$TEST_DIR/"
cp "$REPO_ROOT/windows/CMakeLists.txt" "$TEST_DIR/"
cp "$REPO_ROOT/windows/runner/CMakeLists.txt" "$TEST_DIR/runner_cmake.txt"

# Create a minimal test CMakeLists.txt
cat > $TEST_DIR/test_cmake.txt << 'EOF'
cmake_minimum_required(VERSION 3.14)
project(test_project LANGUAGES CXX)

set(BINARY_NAME "test_app")
set(FLUTTER_MANAGED_DIR "${CMAKE_CURRENT_SOURCE_DIR}")

# Test that the GitHub Actions compatible file is loaded without errors
include(generated_plugins_github_actions_fixed.cmake)

message(STATUS "🎯 Test completed successfully!")
EOF

# Change to test directory
cd $TEST_DIR

# Run CMake test
echo "🧪 Running CMake test..."
cmake -P test_cmake.txt

echo "✅ GitHub Actions CMake Fix test completed successfully!"
echo "Test directory: $TEST_DIR (you can safely delete this)"
