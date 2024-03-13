#-----------------------------------------------------------------------
# Common test plugin variables

set(OPENASSETIO_TEST_PLUGINS_PATH ${CMAKE_INSTALL_LIBDIR}/${PROJECT_NAME}/plugins)


#-----------------------------------------------------------------------
# Plugin sets to build/install for tests.

add_subdirectory(working)
add_subdirectory(broken)
