#-----------------------------------------------------------------------
# Python test target for creating test-only bindings.
#
# This is a static library to be consumed by the _openassetio Python
# extension module at build time for adding test-specific bindings.

add_library(openassetio-python-module-test STATIC)
openassetio_set_default_target_properties(openassetio-python-module-test)

target_sources(
    openassetio-python-module-test
    PRIVATE
    _testutils.cpp
    PyRetainingSharedPtrTest.cpp
    errorsTest.cpp
    gilTest.cpp
    HostInterfaceTest.cpp
    UIDelegateTest.cpp
)

# Give access to private headers.
target_include_directories(openassetio-python-module-test
    PRIVATE ${PROJECT_SOURCE_DIR}/src/openassetio-python/cmodule/src)

target_link_libraries(
    openassetio-python-module-test
    PRIVATE
    # Mocking framework.
    trompeloeil::trompeloeil
    # Core C++ library.
    openassetio-core
    # UI delegation C++ library.
    openassetio-ui
    # Python C++ bridge library.
    openassetio-python-bridge
    # pybind, including its handy transitive Python-specific properties.
    pybind11::module pybind11::windows_extras
)
