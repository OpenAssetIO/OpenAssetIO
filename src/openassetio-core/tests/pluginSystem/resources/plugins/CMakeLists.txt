#-----------------------------------------------------------------------
# Common test plugin helpers

# Function to make installed library file name simpler and more
# predictable cross-platform.
function(openassetio_simplify_lib_name target_name lib_name)
    set_target_properties(
        ${target_name}
        PROPERTIES
        OUTPUT_NAME ${lib_name}
        PREFIX ""
        SOVERSION ""
        VERSION ""
    )
endfunction()

set(OPENASSETIO_TEST_PLUGINS_PATH ${CMAKE_INSTALL_LIBDIR}/${PROJECT_NAME}/plugins)

#-----------------------------------------------------------------------
# Plugin sets to build/install for tests.

add_subdirectory(working)
add_subdirectory(broken)
if (OPENASSETIO_ENABLE_PYTHON)
    add_subdirectory(python-gil-check)
endif()
