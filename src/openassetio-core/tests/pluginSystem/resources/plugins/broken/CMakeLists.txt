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
# A plugin that returns a `nullptr` from the factory function.

add_library(
    openassetio-core-pluginSystem-test-factory-returnnull
    MODULE
    factoryReturnNull.cpp
)
openassetio_set_default_target_properties(
    openassetio-core-pluginSystem-test-factory-returnnull)
target_link_libraries(
    openassetio-core-pluginSystem-test-factory-returnnull
    PRIVATE
    openassetio-core
)
generate_export_header(
    openassetio-core-pluginSystem-test-factory-returnnull
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/factory-returnnull-export.h
    EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
)
target_include_directories(
    openassetio-core-pluginSystem-test-factory-returnnull
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
)
openassetio_simplify_lib_name(
    openassetio-core-pluginSystem-test-factory-returnnull factory-returnnull)
install(
    TARGETS openassetio-core-pluginSystem-test-factory-returnnull
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)


#-----------------------------------------------------------------------
# A plugin that throws a std::exception in the plugin's `identifier`
# function.

add_library(
    openassetio-core-pluginSystem-test-identifierthrow-exception
    MODULE
    identifierThrowException.cpp
)
openassetio_set_default_target_properties(
    openassetio-core-pluginSystem-test-identifierthrow-exception)
target_link_libraries(
    openassetio-core-pluginSystem-test-identifierthrow-exception
    PRIVATE
    openassetio-core
)
generate_export_header(
    openassetio-core-pluginSystem-test-identifierthrow-exception
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/identifierthrow-exception-export.h
    EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
)
target_include_directories(
    openassetio-core-pluginSystem-test-identifierthrow-exception
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
)
openassetio_simplify_lib_name(
    openassetio-core-pluginSystem-test-identifierthrow-exception identifierthrow-exception)
install(
    TARGETS openassetio-core-pluginSystem-test-identifierthrow-exception
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)


#-----------------------------------------------------------------------
# A plugin that throws a non-std::exception in the plugin's `identifier`
# function.

add_library(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception
    MODULE
    identifierThrowNonException.cpp
)
openassetio_set_default_target_properties(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception)
target_link_libraries(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception
    PRIVATE
    openassetio-core
)
generate_export_header(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception
    EXPORT_FILE_NAME ${CMAKE_CURRENT_BINARY_DIR}/include/identifierthrow-nonexception-export.h
    EXPORT_MACRO_NAME OPENASSETIO_CORE_PLUGINSYSTEM_TEST_EXPORT
)
target_include_directories(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception
    PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
)
openassetio_simplify_lib_name(
    openassetio-core-pluginSystem-test-identifierthrow-nonexception identifierthrow-nonexception)
install(
    TARGETS openassetio-core-pluginSystem-test-identifierthrow-nonexception
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
    DESTINATION ${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}/broken
)
