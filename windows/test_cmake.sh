#!/bin/bash
cd /home/tannim/hz/windows
mkdir -p build_test
cd build_test
cmake .. -DCMAKE_BUILD_TYPE=Debug -G "Ninja"
