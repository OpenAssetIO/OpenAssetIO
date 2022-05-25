# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

function(set_default_compiler_warnings target_name)

    set(CLANG_WARNINGS
        -Wall
        # Reasonable and standard.
        -Wextra
        # Warn the user if a variable declaration shadows one from a
        # parent context.
        -Wshadow
        # Warn the user if a class with virtual functions has a
        # non-virtual destructor. This helps catch hard to track down
        # memory errors.
        -Wnon-virtual-dtor
        # Warn for c-style casts.
        -Wold-style-cast
        # Warn for potential performance problem casts.
        -Wcast-align
        # Warn on anything being unused.
        -Wunused
        # Warn if you overload (not override) a virtual function.
        -Woverloaded-virtual
        # Warn if non-standard C++ is used.
        -Wpedantic
        # Warn on type conversions that may lose data.
        -Wconversion
        # Warn on sign conversions.
        -Wsign-conversion
        # Warn if a null dereference is detected.
        -Wnull-dereference
        # Warn if float is implicit promoted to double.
        -Wdouble-promotion
        # Warn on security issues around functions that format output
        # (ie printf).
        -Wformat=2
        # Warn on statements that fallthrough without an explicit
        # annotation.
        -Wimplicit-fallthrough)

    if (OPENASSETIO_WARNINGS_AS_ERRORS)
        set(CLANG_WARNINGS ${CLANG_WARNINGS} -Werror)
        set(MSVC_WARNINGS ${MSVC_WARNINGS} /WX)
    endif ()

    set(GCC_WARNINGS
        ${CLANG_WARNINGS}
        # Warn if indentation implies blocks where blocks do not exist.
        -Wmisleading-indentation
        # Warn if if / else chain has duplicated conditions.
        -Wduplicated-cond
        # Warn if if / else branches have duplicated code.
        -Wduplicated-branches
        # Warn about logical operations being used where bitwise were
        # probably wanted.
        -Wlogical-op
        # Warn if you perform a cast to the same type.
        -Wuseless-cast)

    if (MSVC)
        set(PROJECT_WARNINGS ${MSVC_WARNINGS})
        message(AUTHOR_WARNING
            "Compiler warnings need configuring for '${CMAKE_CXX_COMPILER_ID}' compiler.")
    elseif (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        set(PROJECT_WARNINGS ${CLANG_WARNINGS})
    elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        set(PROJECT_WARNINGS ${GCC_WARNINGS})
    else ()
        message(AUTHOR_WARNING "No compiler warnings set for '${CMAKE_CXX_COMPILER_ID}' compiler.")
    endif ()

    target_compile_options(${target_name} PRIVATE ${PROJECT_WARNINGS})

endfunction()
