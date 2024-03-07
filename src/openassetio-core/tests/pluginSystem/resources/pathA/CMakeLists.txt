#-----------------------------------------------------------------------
# Plugin A

add_library(openassetio-core-pluginSystem-test-pathA MODULE)
openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-pathA)

set_target_properties(
    ${target_name}
    PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/share/plugins/test
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

