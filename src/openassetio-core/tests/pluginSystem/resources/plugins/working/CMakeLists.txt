#-----------------------------------------------------------------------
# Test Plugins

set(_plugins_path ${CMAKE_INSTALL_LIBDIR}/${PROJECT_NAME}/plugins)

# Create a test plugin with a particular path and id suffix.
function (openassetio_test_pluginSystem_generate_plugin path_suffix id_suffix)

    #-------------------------------------------------------------------
    # Create plugin

    add_library(openassetio-core-pluginSystem-test-${path_suffix} MODULE)
    openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-${path_suffix})
    # Add to the set of installable targets.
    install(
        TARGETS openassetio-core-pluginSystem-test-${path_suffix}
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${_plugins_path}/${path_suffix}
    )

    #-------------------------------------------------------------------
    # Plugin identification

    target_compile_definitions(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        # Suffix for plugin path
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_PATH_SUFFIX="${path_suffix}"
        # Suffix for plugin identifier
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX="${id_suffix}"
    )

    #-------------------------------------------------------------------
    # Target dependencies

    target_sources(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        plugin.cpp
    )

    target_link_libraries(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        # Mocking framework.
        trompeloeil::trompeloeil
        # Lib under test.
        openassetio-core
    )

    target_include_directories(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        # For export header
        ${CMAKE_CURRENT_BINARY_DIR}/${path_suffix}/include
    )

    #-------------------------------------------------------------------
    # API export header

    include(GenerateExportHeader)
    generate_export_header(
        openassetio-core-pluginSystem-test-${path_suffix}
        EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/${path_suffix}/include/export.h
        EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
    )

endfunction()

# Path/ID chosen to mirror Python plugin system test plugins.
openassetio_test_pluginSystem_generate_plugin(pathA modulePlugin)
openassetio_test_pluginSystem_generate_plugin(pathB packagePlugin)
openassetio_test_pluginSystem_generate_plugin(pathC modulePlugin)


#-----------------------------------------------------------------------
# Create symlinks in install tree for symlink plugin loading test.
#
# See Test_CppPluginSystem_scan
# test_when_path_contains_symlinks_then_plugins_are_loaded

# cmake-lint: disable=C0301
install(CODE "
    file(MAKE_DIRECTORY \"$<INSTALL_PREFIX>/${_plugins_path}/symlinkPath\")

    file(
        CREATE_LINK
        \"$<INSTALL_PREFIX>/${_plugins_path}/pathA/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathA>\"
        \"$<INSTALL_PREFIX>/${_plugins_path}/symlinkPath/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathA>\"
        SYMBOLIC
    )
    file(
        CREATE_LINK
        \"$<INSTALL_PREFIX>/${_plugins_path}/pathB/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathB>\"
        \"$<INSTALL_PREFIX>/${_plugins_path}/symlinkPath/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathB>\"
        SYMBOLIC
    )
")
