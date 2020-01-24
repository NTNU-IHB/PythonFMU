
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
