cmake_minimum_required(VERSION 3.10)
project(pythonfmu-export VERSION 0.1.0)

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

# ==============================================================================
# Sources
# ==============================================================================

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/headers)

set(sources
        cpp/cppfmu_cs.cpp
        cpp/fmi_functions.cpp
        cpp/PyObjectWrapper.cpp
        cpp/SlaveInstance.cpp
        cpp/thread_worker.cpp
        )

add_library(pythonfmu-export ${sources})
target_compile_features(pythonfmu-export PUBLIC "cxx_std_17")
target_include_directories(pythonfmu-export
        PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>"
        PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}"
        )

target_link_libraries(pythonfmu-export
        PRIVATE
        Python3::Python
        )
