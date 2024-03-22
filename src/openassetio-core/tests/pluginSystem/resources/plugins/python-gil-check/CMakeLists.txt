# Create a test plugin that asserts the Python GIL is released.

#-------------------------------------------------------------------
# Create plugin

add_library(openassetio-core-pluginSystem-test-python-gil MODULE)
openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-python-gil)
openassetio_simplify_lib_name(openassetio-core-pluginSystem-test-python-gil plugin)
# Add to the set of installable targets.
install(
    TARGETS openassetio-core-pluginSystem-test-python-gil
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/python-gil-check
)

#-------------------------------------------------------------------
# Plugin identification

target_compile_definitions(
    openassetio-core-pluginSystem-test-python-gil
    PRIVATE
    # Suffix for plugin path
    OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_PATH_SUFFIX="python-gil"
    # Suffix for plugin identifier
    OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX="${id_suffix}"
)

#-------------------------------------------------------------------
# Target dependencies

target_sources(
    openassetio-core-pluginSystem-test-python-gil
    PRIVATE
    plugin.cpp
)

target_link_libraries(
    openassetio-core-pluginSystem-test-python-gil
    PRIVATE
    # Mocking framework.
    trompeloeil::trompeloeil
    # Core library
    openassetio-core
    # So we can check the Python GIL
    $<BUILD_INTERFACE:pybind11::module>
)

target_include_directories(
    openassetio-core-pluginSystem-test-python-gil
    PRIVATE
    # For export header
    ${CMAKE_CURRENT_BINARY_DIR}/python-gil/include
)

#-------------------------------------------------------------------
# API export header

include(GenerateExportHeader)
generate_export_header(
    openassetio-core-pluginSystem-test-python-gil
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/python-gil/include/export.h
    EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
)
