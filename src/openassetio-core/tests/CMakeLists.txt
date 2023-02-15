#-----------------------------------------------------------------------
# C++ API test target

add_executable(openassetio-core-cpp-test-exe)
openassetio_set_default_target_properties(openassetio-core-cpp-test-exe)

# Add to the set of installable targets.
install(
    TARGETS openassetio-core-cpp-test-exe
    EXPORT ${PROJECT_NAME}_EXPORTED_TARGETS
)


#-----------------------------------------------------------------------
# Target dependencies

target_sources(openassetio-core-cpp-test-exe
    PRIVATE
    main.cpp
    BatchElementErrorTest.cpp
    ContextTest.cpp
    TraitsDataTest.cpp
    hostApi/ManagerTest.cpp
    managerApi/HostTest.cpp
    managerApi/HostSessionTest.cpp
    managerApi/ManagerStateBaseTest.cpp
    trait/TraitBaseTest.cpp
)

target_link_libraries(
    openassetio-core-cpp-test-exe
    PRIVATE
    # Test framework.
    Catch2::Catch2
    # Mocking framework.
    trompeloeil::trompeloeil
    # Lib under test.
    openassetio-core
)


#-----------------------------------------------------------------------
# Create CTest target

# Requires: openassetio.internal.install
add_custom_target(
    openassetio.internal.core-cpp-test
    COMMAND
"${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/\
$<TARGET_FILE_NAME:openassetio-core-cpp-test-exe>"
)

openassetio_add_test_target(openassetio.internal.core-cpp-test)
openassetio_add_test_fixture_dependencies(
    openassetio.internal.core-cpp-test
    openassetio.internal.install
)
