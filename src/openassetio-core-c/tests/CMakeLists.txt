#-----------------------------------------------------------------------
# C API test target

add_executable(openassetio-core-c-test-exe)
openassetio_set_default_target_properties(openassetio-core-c-test-exe)

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
    handlesTest.cpp
    errorsTest.cpp
    StringViewTest.cpp
    InfoDictionaryTest.cpp
    managerApi/CManagerInterfaceAdapterTest.cpp
    hostApi/ManagerTest.cpp
)

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
    ${PROJECT_SOURCE_DIR}/src/openassetio-core-c/src
)


#-----------------------------------------------------------------------
# Create CTest target

# Requires: openassetio.internal.install
add_custom_target(
    openassetio.internal.core-c-test
    COMMAND
    ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/$<TARGET_FILE_NAME:openassetio-core-c-test-exe>
)

openassetio_add_test_target(openassetio.internal.core-c-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.core-c-test
    openassetio.internal.install
)
