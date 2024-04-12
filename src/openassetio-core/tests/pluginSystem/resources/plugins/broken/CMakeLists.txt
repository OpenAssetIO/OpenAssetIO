# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Foundry Visionmongers Ltd

include(GenerateExportHeader)
#-----------------------------------------------------------------------
# A non-library file with a non-library extension.

file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/not-a-lib.txt "Not a lib")
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/not-a-lib.txt
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)

#-----------------------------------------------------------------------
# A non-library file masquerading as a library.

file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/fake-lib${CMAKE_SHARED_MODULE_SUFFIX} "Fake lib")
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/fake-lib${CMAKE_SHARED_MODULE_SUFFIX}
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)

#-----------------------------------------------------------------------
# A directory (i.e. std::filesystem::is_regular_file is false).

file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/a-directory${CMAKE_SHARED_MODULE_SUFFIX})
install(
    DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/a-directory${CMAKE_SHARED_MODULE_SUFFIX}
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)

#-----------------------------------------------------------------------
# A library that doesn't expose the required entrypoint.

add_library(openassetio-core-pluginSystem-test-nonplugin MODULE nonPlugin.cpp)
openassetio_set_default_target_properties(openassetio-core-pluginSystem-test-nonplugin)
openassetio_simplify_lib_name(openassetio-core-pluginSystem-test-nonplugin nonplugin)
install(
    TARGETS openassetio-core-pluginSystem-test-nonplugin
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)

#-----------------------------------------------------------------------
# Broken plugins

# Create a test plugin..
function(openassetio_test_pluginSystem_generate_broken_plugin target_suffix src_file)

    #-------------------------------------------------------------------
    # Create plugin

    add_library(openassetio-core-pluginSystem-test-broken-${target_suffix} MODULE)
    openassetio_set_default_target_properties(
        openassetio-core-pluginSystem-test-broken-${target_suffix})
    openassetio_simplify_lib_name(
        openassetio-core-pluginSystem-test-broken-${target_suffix} ${target_suffix})
    # Add to the set of installable targets.
    install(
        TARGETS openassetio-core-pluginSystem-test-broken-${target_suffix}
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
    )

    #-------------------------------------------------------------------
    # Target dependencies

    target_sources(
        openassetio-core-pluginSystem-test-broken-${target_suffix}
        PRIVATE
        ${src_file}
    )

    target_link_libraries(
        openassetio-core-pluginSystem-test-broken-${target_suffix}
        PRIVATE
        # Core library
        openassetio-core
    )

    target_include_directories(
        openassetio-core-pluginSystem-test-broken-${target_suffix}
        PRIVATE
        # For export header
        ${CMAKE_CURRENT_BINARY_DIR}/${target_suffix}/include
    )

    #-------------------------------------------------------------------
    # API export header

    generate_export_header(
        openassetio-core-pluginSystem-test-broken-${target_suffix}
        EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/${target_suffix}/include/export.h
        EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
    )

endfunction()

# A plugin that returns a `nullptr` from the factory function.
openassetio_test_pluginSystem_generate_broken_plugin(factory-return-null factoryReturnNull.cpp)
# A plugin that throws a std::exception in the plugin's `identifier`
# function.
openassetio_test_pluginSystem_generate_broken_plugin(
    identifier-throw-exception identifierThrowException.cpp)
# A plugin that throws a non-std::exception in the plugin's `identifier`
# function.
openassetio_test_pluginSystem_generate_broken_plugin(
    identifier-throw-nonexception identifierThrowNonException.cpp)
