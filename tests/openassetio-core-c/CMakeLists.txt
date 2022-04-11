#-----------------------------------------------------------------------
# C API test target

add_executable(openassetio-core-c-test-exe)
set_default_target_properties(openassetio-core-c-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-core-c-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-core-c-test-exe
    PRIVATE
    main.cpp
    private/errorsTest.cpp
    private/managerAPI/CManagerInterfaceTest.cpp)

target_link_libraries(
    openassetio-core-c-test-exe
    PRIVATE
    # Test framework.
    Catch2::Catch2
    # Mocking framework.
    trompeloeil::trompeloeil
    # Lib under test.
    openassetio-core-c
)

target_include_directories(
    openassetio-core-c-test-exe
    PRIVATE
    # Give access to private headers.
    # TODO(DF): This requires otherwise unnecessary symbol export, is
    #   there a neater way?
    ${PROJECT_SOURCE_DIR}/src/openassetio-core-c/private
)


#-----------------------------------------------------------------------
# Override RPATH to locate libs

if (UNIX)
    # Calculate relative path from site-packages to lib directory.
    file(RELATIVE_PATH
        install_dir_rel_to_lib
        ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}
        ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR})

    if (APPLE)
        # TODO(DF): handle RPATH on OSX - e.g. @rpath vs. @loader_path
    else ()
        set(rpath "$ORIGIN/${install_dir_rel_to_lib}")
    endif ()

    set_target_properties(openassetio-core-c-test-exe PROPERTIES INSTALL_RPATH "${rpath}")
endif ()


#-----------------------------------------------------------------------
# Create CTest target

add_custom_target(
    openassetio-core-c-test
    COMMAND
    ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/$<TARGET_FILE_NAME:openassetio-core-c-test-exe>
)
add_dependencies(openassetio-core-c-test openassetio-install)

add_test(
    NAME openassetio-core-c
    COMMAND
    ${CMAKE_COMMAND} --build "${PROJECT_BINARY_DIR}" --target openassetio-core-c-test
)

