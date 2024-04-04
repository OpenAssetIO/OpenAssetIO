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


#-----------------------------------------------------------------------
# Plugin sets to build/install for tests.

add_subdirectory(working)
add_subdirectory(broken)
