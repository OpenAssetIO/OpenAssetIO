find_package(Catch2 2 REQUIRED)
find_package(trompeloeil 42 REQUIRED)

add_subdirectory(openassetio-core)

# C API bindings tests.
if (OPENASSETIO_ENABLE_C)
    add_subdirectory(openassetio-core-c)
endif ()

# Python tests.
if (OPENASSETIO_ENABLE_PYTHON)
    add_subdirectory(openassetio-python)
endif ()
