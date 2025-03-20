# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 The Foundry Visionmongers Ltd

#-----------------------------------------------------------------------
# Test Plugins

# Create a test plugin with a particular path and id suffix.
function(openassetio_test_ui_pluginSystem_generate_plugin path_suffix id_suffix src_file)

    #-------------------------------------------------------------------
    # Create plugin

    add_library(openassetio-ui-pluginSystem-test-${path_suffix} MODULE)
    openassetio_set_default_target_properties(openassetio-ui-pluginSystem-test-${path_suffix})
    set_target_properties(
        openassetio-ui-pluginSystem-test-${path_suffix}
        PROPERTIES
        # Prevent conflict with manager test plugins (i.e. suffix "ui"
        # to the build dir path).
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/ui
        # Simplify library name.
        OUTPUT_NAME ${path_suffix}
        PREFIX ""
        SOVERSION ""
        VERSION ""
    )
    # Add to the set of installable targets.
    install(
        TARGETS openassetio-ui-pluginSystem-test-${path_suffix}
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/ui/${path_suffix}
    )

    #-------------------------------------------------------------------
    # Plugin identification

    target_compile_definitions(
        openassetio-ui-pluginSystem-test-${path_suffix}
        PRIVATE
        # Suffix for plugin identifier
        OPENASSETIO_CORE_PLUGINSYSTEM_TEST_PLUGIN_ID_SUFFIX="${id_suffix}"
    )

    #-------------------------------------------------------------------
    # Target dependencies

    target_sources(
        openassetio-ui-pluginSystem-test-${path_suffix}
        PRIVATE
        ${src_file}
    )

    target_link_libraries(
        openassetio-ui-pluginSystem-test-${path_suffix}
        PRIVATE
        # Core library
        openassetio-core
        # UI library
        openassetio-ui
    )

    target_include_directories(
        openassetio-ui-pluginSystem-test-${path_suffix}
        PRIVATE
        # For export header
        ${CMAKE_CURRENT_BINARY_DIR}/ui/${path_suffix}/include
    )

    #-------------------------------------------------------------------
    # API export header

    include(GenerateExportHeader)
    generate_export_header(
        openassetio-ui-pluginSystem-test-${path_suffix}
        EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/ui/${path_suffix}/include/export.h
        EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
    )

endfunction()

# Plugins for testing the CppPluginSystemUIDelegateImplementationFactory.
openassetio_test_ui_pluginSystem_generate_plugin(uiA pluginA uiDelegatePlugin.cpp)
openassetio_test_ui_pluginSystem_generate_plugin(uiB pluginB uiDelegatePlugin.cpp)

if (OPENASSETIO_ENABLE_PYTHON)
    # Plugin for testing the Python GIL is released
    openassetio_test_ui_pluginSystem_generate_plugin(
        python-gil-check python-gil-check pythonGilCheckUIDelegatePlugin.cpp)
    target_link_libraries(
        openassetio-ui-pluginSystem-test-python-gil-check
        PRIVATE
        $<BUILD_INTERFACE:pybind11::module>
    )
endif ()

