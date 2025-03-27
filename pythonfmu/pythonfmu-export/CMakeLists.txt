cmake_minimum_required(VERSION 3.18)
project(pythonfmu-export VERSION 0.2.0)

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
  foreach (CompilerFlag ${CompilerFlags})
    string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
  endforeach ()
endif ()

# Automatically export all symbols in Windows DLLs.
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# ==============================================================================
# Dependencies
# ==============================================================================

# Force to use stable Python ABI https://docs.python.org/3/c-api/stable.html
option (USE_PYTHON_SABI "Use Python stable ABI" ON)
if (USE_PYTHON_SABI AND CMAKE_VERSION VERSION_GREATER_EQUAL 3.26)
  add_compile_definitions(Py_LIMITED_API)
  find_package(Python3 REQUIRED COMPONENTS Development.SABIModule)
  add_library (Python3::Module ALIAS Python3::SABIModule)
else ()
  find_package(Python3 REQUIRED COMPONENTS Development.Module)
endif ()

if (WIN32)
  set(TARGET_PLATFORM win)
elseif (APPLE)
  set(TARGET_PLATFORM darwin)
else ()
  set(TARGET_PLATFORM linux)
endif ()

if ("${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
  set(TARGET_PLATFORM ${TARGET_PLATFORM}64)
else ()
  set(TARGET_PLATFORM ${TARGET_PLATFORM}32)
endif ()

message("Building pythonfmu-export for platform ${TARGET_PLATFORM}")

add_subdirectory(src)
