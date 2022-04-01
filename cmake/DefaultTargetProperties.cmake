# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

function(set_default_target_properties target_name)
    #-------------------------------------------------------------------
    # C++ standard

    # Minimum C++ standard as per current VFX reference platform CY21+.
    target_compile_features(${target_name} PRIVATE cxx_std_17)

    set_target_properties(
        ${target_name}
        PROPERTIES
        # Ensure the proposed compiler supports our minimum C++
        # standard.
        CXX_STANDARD_REQUIRED ON
        # Disable compiler extensions. E.g. use -std=c++11  instead of
        # -std=gnu++11.  Helps limit cross-platform issues.
        CXX_EXTENSIONS OFF
    )

    #-------------------------------------------------------------------
    # Compiler warnings

    include(CompilerWarnings)
    set_default_compiler_warnings(${target_name})


    #-------------------------------------------------------------------
    # Interprocedural Optimization

    if (OPENASSETIO_ENABLE_IPO)
        include(CheckIPOSupported)
        check_ipo_supported(RESULT result OUTPUT output)
        if (result)
            set_target_properties(
                ${target_name}
                PROPERTIES
                INTERPROCEDURAL_OPTIMIZATION ON
            )
        else ()
            message(WARNING "OPENASSETIO_ENABLE_IPO is not supported, option ignored: ${output}")
        endif ()
    endif ()


    #-------------------------------------------------------------------
    # Symbol visibility

    # Hide symbols from this library by default.
    set_target_properties(
        ${target_name}
        PROPERTIES
        C_VISIBILITY_PRESET hidden
        CXX_VISIBILITY_PRESET hidden
        VISIBILITY_INLINES_HIDDEN YES
    )

    # Hide all symbols from external statically linked libraries.
    if (IS_GCC_OR_CLANG)
        target_link_options(${target_name} PRIVATE -Wl,--exclude-libs,ALL)
    endif ()

    # Whether to use the old or new C++ ABI with gcc.
    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND
        CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 5.0)
        if (OPENASSETIO_GLIBCXX_USE_CXX11_ABI)
            target_compile_definitions(${target_name} PRIVATE _GLIBCXX_USE_CXX11_ABI=1)
        else ()
            target_compile_definitions(${target_name} PRIVATE _GLIBCXX_USE_CXX11_ABI=0)
        endif ()
    endif ()

    # Whether to enable position independent code, even for static libs.
    set_target_properties(
        ${target_name}
        PROPERTIES
        POSITION_INDEPENDENT_CODE ${OPENASSETIO_ENABLE_POSITION_INDEPENDENT_CODE}
    )


    #-------------------------------------------------------------------
    # RPATH wrangling.

    if (UNIX)
        if (APPLE)
            # TODO(DF): handle RPATH on OSX - e.g. @rpath vs. @loader_path
            message(AUTHOR_WARNING "OSX RPATH not configured")
        else ()
            set(rpath "$ORIGIN")
        endif ()

        set_target_properties(
            ${target_name}
            PROPERTIES
            # Control RPATH in build phase. We assume tests will only be
            # run against the install tree, so disable for build tree.
            SKIP_BUILD_RPATH TRUE
            BUILD_WITH_INSTALL_RPATH FALSE
            # Whether to add hardcoded directories to final runtime
            # search path.
            INSTALL_RPATH_USE_LINK_PATH FALSE
            # Runtime search path value
            INSTALL_RPATH "${rpath}"
            # Enable RPATH on OSX
            # TODO(DF): See above re. OSX RPATH
            # MACOSX_RPATH ON
        )
    endif ()

    # CentOS 7 and below (i.e. VFX reference platform) compile gcc to
    # only set RPATH by default, whereas other Linux distros set RUNPATH
    # (if both are set then RPATH is ignored). They each cause different
    # runtime search path behavior. So be explicit to ensure we are
    # consistent across distros.
    if (IS_GCC_OR_CLANG)
        if (OPENASSETIO_ENABLE_NEW_DTAGS)
            target_link_options(${target_name} PRIVATE "-Wl,--enable-new-dtags")
        else ()
            target_link_options(${target_name} PRIVATE "-Wl,--disable-new-dtags")
        endif ()
    endif ()


    #-------------------------------------------------------------------
    # Build tree directory structure.

    set_target_properties(
        ${target_name}
        PROPERTIES
        # Make the build area layout look a bit more like the final dist
        # layout
        LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}
        ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}
        RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}
    )


    #-------------------------------------------------------------------
    # Library version

    get_target_property(target_type ${target_name} TYPE)

    if (NOT ${target_type} STREQUAL EXECUTABLE)
        # When building or installing appropriate symlinks are created, if
        # supported.
        set_target_properties(
            ${target_name}
            PROPERTIES
            VERSION ${PROJECT_VERSION}
            SOVERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
        )
    endif ()

    #-------------------------------------------------------------------
    # Coverage reports and/or sanitizers, useful for tests.

    if (IS_GCC_OR_CLANG)
        if (OPENASSETIO_ENABLE_COVERAGE)
            message(NOTICE "!!! Coverage reports are enabled - forcing debug build !!!")
            target_compile_options(${target_name} PRIVATE --coverage -O0 -g)
            target_link_libraries(${target_name} PRIVATE --coverage)
        endif ()

        if (OPENASSETIO_ENABLE_SANITIZER_ADDRESS)
            list(APPEND sanitizers "address")
        endif ()

        if (OPENASSETIO_ENABLE_SANITIZER_LEAK)
            list(APPEND sanitizers "leak")
        endif ()

        if (OPENASSETIO_ENABLE_SANITIZER_UNDEFINED_BEHAVIOR)
            list(APPEND sanitizers "undefined")
        endif ()

        if (OPENASSETIO_ENABLE_SANITIZER_THREAD)
            list(APPEND sanitizers "thread")
        endif ()

        if (OPENASSETIO_ENABLE_SANITIZER_MEMORY)
            list(APPEND sanitizers "memory")
        endif ()

        list(JOIN sanitizers "," sanitize_arg)

        if (sanitize_arg AND NOT "${sanitize_arg}" STREQUAL "")
            # Add sanitizers, including
            # * -fno-omit-frame-pointer to enable stack traces on
            #   failure.
            # * -fno-sanitize-recover=all to force the program to exit
            #   with an error code on failure.
            target_compile_options(${target_name}
                PRIVATE
                -fno-sanitize-recover=all
                -fsanitize=${sanitize_arg}
                -fno-omit-frame-pointer)
            target_link_options(${target_name}
                PRIVATE
                -fno-sanitize-recover=all
                -fsanitize=${sanitize_arg}
                -fno-omit-frame-pointer)
        endif ()
    endif ()


    #-------------------------------------------------------------------
    # Linters/analyzers

    if (TARGET openassetio-cpplint)
        add_dependencies(${target_name} openassetio-cpplint)
    endif ()

    if (TARGET openassetio-clangformat)
        add_dependencies(${target_name} openassetio-clangformat)
    endif ()


    #-------------------------------------------------------------------
    # IDE helpers

    # For supported IDEs, add targets to a folder.
    set_target_properties(
        ${target_name}
        PROPERTIES
        FOLDER ${PROJECT_NAME}
    )


endfunction()
