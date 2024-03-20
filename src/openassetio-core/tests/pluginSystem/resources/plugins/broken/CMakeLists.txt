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
# MacOS/Windows cannot catch static initialisation exceptions.

if (NOT APPLE AND NOT MSVC)

    #-------------------------------------------------------------------
    # A library that throws a std::exception during static
    # initialisation.

    add_library(
        openassetio-core-pluginSystem-test-staticthrow-exception
        MODULE
        staticThrowException.cpp
    )
    openassetio_set_default_target_properties(
        openassetio-core-pluginSystem-test-staticthrow-exception)
    openassetio_simplify_lib_name(
        openassetio-core-pluginSystem-test-staticthrow-exception staticthrow-exception)
    install(
        TARGETS openassetio-core-pluginSystem-test-staticthrow-exception
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
    )

    #-----------------------------------------------------------------------
    # A library that throws a non-std::exception during static
    # initialisation.

    add_library(
        openassetio-core-pluginSystem-test-staticthrow-nonexception
        MODULE
        staticThrowNonException.cpp
    )
    openassetio_set_default_target_properties(
        openassetio-core-pluginSystem-test-staticthrow-nonexception)
    openassetio_simplify_lib_name(
        openassetio-core-pluginSystem-test-staticthrow-nonexception staticthrow-nonexception)
    install(
        TARGETS openassetio-core-pluginSystem-test-staticthrow-nonexception
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
    )

endif ()

#-----------------------------------------------------------------------
# Windows cannot catch exceptions thrown from C linkage functions.
#
# This is a result of CMake's default MSVC flags. Exceptions across C
# linkage can be enabled using the /EHa flag, but that flag would have
# to be applied to openassetio-core as well as the plugin.

if (NOT MSVC)
    #-------------------------------------------------------------------
    # A plugin that throws a std::exception in the entrypoint.

    add_library(
        openassetio-core-pluginSystem-test-entrypointthrow-exception
        MODULE
        entrypointThrowException.cpp
    )
    openassetio_set_default_target_properties(
        openassetio-core-pluginSystem-test-entrypointthrow-exception)
    target_link_libraries(
        openassetio-core-pluginSystem-test-entrypointthrow-exception
        PRIVATE
        openassetio-core
    )
    generate_export_header(
        openassetio-core-pluginSystem-test-entrypointthrow-exception
        EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/entrypointthrow-exception-export.h
        EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
    )
    target_include_directories(
        openassetio-core-pluginSystem-test-entrypointthrow-exception
        PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}/include
    )
    openassetio_simplify_lib_name(
        openassetio-core-pluginSystem-test-entrypointthrow-exception entrypointthrow-exception)
    install(
        TARGETS openassetio-core-pluginSystem-test-entrypointthrow-exception
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
    )

    #-------------------------------------------------------------------
    # A plugin that throws a non-std::exception in the entrypoint.

    add_library(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        MODULE
        entrypointThrowNonException.cpp
    )
    openassetio_set_default_target_properties(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception)
    target_link_libraries(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        PRIVATE
        openassetio-core
    )
    generate_export_header(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/entrypointthrow-nonexception-export.h
        EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
    )
    target_include_directories(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        PRIVATE
        ${CMAKE_CURRENT_BINARY_DIR}/include
    )
    openassetio_simplify_lib_name(
        openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        entrypointthrow-nonexception)
    if (MSVC)
        target_compile_options(
            openassetio-core-pluginSystem-test-entrypointthrow-exception PRIVATE /EHsc-)
    endif ()
    install(
        TARGETS openassetio-core-pluginSystem-test-entrypointthrow-nonexception
        EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
        DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
    )
endif ()
