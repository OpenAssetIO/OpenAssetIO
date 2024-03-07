#-----------------------------------------------------------------------
# Plugin A

add_library(openassetio-core-pluginSystem-test-pathA MODULE)
openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-pathA)
# Add to the set of installable targets.
install(
    TARGETS openassetio-core-pluginSystem-test-pathA
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION share/${PROJECT_NAME}/plugins
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-core-pluginSystem-test-pathA
    PRIVATE
    plugin.cpp
)

target_link_libraries(
    openassetio-core-pluginSystem-test-pathA
    PRIVATE
    # Mocking framework.
    trompeloeil::trompeloeil
    # Lib under test.
    openassetio-core
)

target_include_directories(
    openassetio-core-pluginSystem-test-pathA
    PRIVATE
    # For export header
    ${CMAKE_CURRENT_BINARY_DIR}/include
)

#-----------------------------------------------------------------------
# API export header

include(GenerateExportHeader)
generate_export_header(
    openassetio-core-pluginSystem-test-pathA
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/export.h
)

