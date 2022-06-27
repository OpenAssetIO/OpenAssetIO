#-----------------------------------------------------------------------
# Test library
# Ensures inlining optimisations are not possible.

add_library(openassetio-perftest-lib SHARED lib.cpp)

set_default_target_properties(openassetio-perftest-lib)
install(TARGETS openassetio-perftest-lib EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

target_link_libraries(openassetio-perftest-lib
    PRIVATE
    openassetio-core)

if (UNIX)
    set_target_properties(
        openassetio-perftest-lib
        PROPERTIES
        # Allow RPATH in build tree so it can be executed there.
        SKIP_BUILD_RPATH FALSE
        # Fix RPATH in install tree.
        INSTALL_RPATH $ORIGIN
    )
endif ()

include(GenerateExportHeader)
generate_export_header(
    openassetio-perftest-lib
    EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/include/perftest/export.h
)

target_include_directories(openassetio-perftest-lib
    PUBLIC
    # For generated export.h header.
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>"
)

#-----------------------------------------------------------------------
# Test executable

add_executable(openassetio-perftest perftest.cpp)

set_default_target_properties(openassetio-perftest)
install(TARGETS openassetio-perftest EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS)

target_link_libraries(openassetio-perftest
    PRIVATE
    openassetio-core
    openassetio-perftest-lib)

if (UNIX)
    set_target_properties(
        openassetio-perftest
        PROPERTIES
        # Allow RPATH in build tree so it can be executed there.
        SKIP_BUILD_RPATH FALSE
        # Fix RPATH in install tree.
        INSTALL_RPATH $ORIGIN/../lib
    )
endif ()

