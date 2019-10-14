cmake_minimum_required(VERSION 3.10)
project(pythonfmu-export VERSION 0.0.1)

# ==============================================================================
# Build settings
# ==============================================================================

set(BUILD_SHARED_LIBS ON)

# ==============================================================================
# Global internal configuration
# ==============================================================================

# Automatically export all symbols in Windows DLLs.
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# ==============================================================================
# Dependencies
# ==============================================================================

find_package(JNI REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(src/main)
