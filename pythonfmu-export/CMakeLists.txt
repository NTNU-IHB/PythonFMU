cmake_minimum_required(VERSION 3.10)
project(pythonfmu-export VERSION 0.0.1)

# ==============================================================================
# Build settings
# ==============================================================================

set(BUILD_SHARED_LIBS ON)

# ==============================================================================
# Global internal configuration
# ==============================================================================

if (MSVC)
    # https://stackoverflow.com/questions/14172856/compile-with-mt-instead-of-md-using-cmake
    set(CompilerFlags
            CMAKE_CXX_FLAGS
            CMAKE_CXX_FLAGS_DEBUG
            CMAKE_CXX_FLAGS_RELEASE
            CMAKE_C_FLAGS
            CMAKE_C_FLAGS_DEBUG
            CMAKE_C_FLAGS_RELEASE
            )
    foreach(CompilerFlag ${CompilerFlags})
        string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
    endforeach()
endif()

# Automatically export all symbols in Windows DLLs.
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# ==============================================================================
# Dependencies
# ==============================================================================

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(src/main)
