find_package(Catch2 2 REQUIRED)
find_package(trompeloeil 42 REQUIRED)

# C API bindings tests.
add_subdirectory(openassetio-core-c)
