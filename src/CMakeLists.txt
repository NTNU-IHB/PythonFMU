
set(headers

        "fmi/fmi2Functions.h"
        "fmi/fmi2FunctionTypes.h"
        "fmi/fmi2TypesPlatform.h"

        "pythonfmu/fmu_except.hpp"
        "pythonfmu/Logger.hpp"

        "pythonfmu/SlaveInstance.hpp"
        "pythonfmu/PyState.hpp"
        )

set(sources
        "pythonfmu/fmi2.cpp"
        "pythonfmu/PySlaveInstance.cpp"
        )

# Generate LogCategories.hpp from the canonical pythonfmu/log_categories_data.py
# so the native library and the Python package share a single source of truth.
set(GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(LOG_CATEGORIES_HEADER "${GENERATED_INCLUDE_DIR}/LogCategories.hpp")
add_custom_command(
        OUTPUT "${LOG_CATEGORIES_HEADER}"
        COMMAND Python3::Interpreter "${CMAKE_SOURCE_DIR}/tools/generate_log_categories_header.py" "${LOG_CATEGORIES_HEADER}"
        DEPENDS "${CMAKE_SOURCE_DIR}/pythonfmu/log_categories_data.py" "${CMAKE_SOURCE_DIR}/tools/generate_log_categories_header.py"
        COMMENT "Generating LogCategories.hpp from pythonfmu/log_categories_data.py"
        VERBATIM
)
add_custom_target(generate_log_categories DEPENDS "${LOG_CATEGORIES_HEADER}")

add_library(pythonfmu-export ${sources} ${headers})
add_dependencies(pythonfmu-export generate_log_categories)
target_compile_features(pythonfmu-export PUBLIC "cxx_std_17")

target_include_directories(pythonfmu-export PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")
target_include_directories(pythonfmu-export PRIVATE "${GENERATED_INCLUDE_DIR}")

target_link_libraries (pythonfmu-export PRIVATE Python3::Module)

if (WIN32)
  set_target_properties(pythonfmu-export
          PROPERTIES
          RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/pythonfmu/resources/binaries/${TARGET_PLATFORM}"
          )
else ()
  set_target_properties(pythonfmu-export
          PROPERTIES
          LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/pythonfmu/resources/binaries/${TARGET_PLATFORM}"
          )
endif ()
