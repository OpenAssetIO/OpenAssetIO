# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# Test Plugins

# Create a test plugin with a particular path and id suffix.
function(openassetio_test_pluginSystem_generate_plugin path_suffix id_suffix src_file)

    #-------------------------------------------------------------------
    # Create plugin

    add_library(openassetio-core-pluginSystem-test-${path_suffix} MODULE)
    openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-${path_suffix})
    openassetio_simplify_lib_name(openassetio-core-pluginSystem-test-${path_suffix} ${path_suffix})
    # Add to the set of installable targets.
    install(
        TARGETS openassetio-core-pluginSystem-test-${path_suffix}
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/${path_suffix}
    )

    #-------------------------------------------------------------------
    # Plugin identification

    target_compile_definitions(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        # Suffix for plugin identifier
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX="${id_suffix}"
    )

    #-------------------------------------------------------------------
    # Target dependencies

    target_sources(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        ${src_file}
    )

    target_link_libraries(
        openassetio-core-pluginSystem-test-${path_suffix}
        PRIVATE
        # Core library
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

# Plugins for testing the CppPluginSystem
#
# Path/ID chosen to mirror Python plugin system test plugins.
openassetio_test_pluginSystem_generate_plugin(pathA pluginA genericPlugin.cpp)
openassetio_test_pluginSystem_generate_plugin(pathB pluginB genericPlugin.cpp)
openassetio_test_pluginSystem_generate_plugin(pathC pluginA genericPlugin.cpp)

if (OPENASSETIO_ENABLE_PYTHON)
    # Plugin for testing the Python GIL is released
    openassetio_test_pluginSystem_generate_plugin(
        python-gil-check python-gil-check pythonGilCheckManagerPlugin.cpp)
    target_link_libraries(
        openassetio-core-pluginSystem-test-python-gil-check
        PRIVATE
        $<BUILD_INTERFACE:pybind11::module>
    )
endif ()

# Plugins for testing the CppPluginSystemManagerImplementationFactory.
openassetio_test_pluginSystem_generate_plugin(managerA pluginA managerPlugin.cpp)
openassetio_test_pluginSystem_generate_plugin(managerB pluginB managerPlugin.cpp)


#-----------------------------------------------------------------------
# Create symlinks in install tree for symlink plugin loading test.
#
# See Test_CppPluginSystem_scan
# test_when_path_contains_symlinks_then_plugins_are_loaded

# cmake-lint: disable=C0301
install(CODE "
    file(
        CREATE_LINK
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/pathA\"
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/pathASymlink\"
        SYMBOLIC
    )

    file(MAKE_DIRECTORY \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/symlinkPath\")
    file(
        CREATE_LINK
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/pathA/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathA>\"
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/symlinkPath/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathA>\"
        SYMBOLIC
    )
    file(
        CREATE_LINK
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/pathB/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathB>\"
        \"$<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/symlinkPath/$<TARGET_FILE_NAME:openassetio-core-pluginSystem-test-pathB>\"
        SYMBOLIC
    )
")
