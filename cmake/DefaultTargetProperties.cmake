# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

set(exclude_all_libs_linker_flag "-Wl,--exclude-libs,ALL")


function(openassetio_set_default_target_properties target_name)
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
    if (IS_GCC_OR_CLANG AND NOT APPLE)
        # TODO(TC): Find a way to hide symbols on macOS
        target_link_options(${target_name} PRIVATE ${exclude_all_libs_linker_flag})
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
        get_target_property(target_type ${target_name} TYPE)
        if (${target_type} STREQUAL EXECUTABLE)
            file(RELATIVE_PATH
                install_dir_rel_to_lib
                ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}
                ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR})

            if (APPLE)
                set(rpath "@executable_path/${install_dir_rel_to_lib}")
            else ()
                set(rpath "$ORIGIN/${install_dir_rel_to_lib}")
            endif ()
        else ()
            if (APPLE)
                set(rpath "@loader_path")
            else ()
                set(rpath "$ORIGIN")
            endif ()
        endif ()

        set_target_properties(
            ${target_name}
            PROPERTIES
            # Control RPATH in build phase. We assume tests will only be
            # run against the install tree for internal development,
            # but external projects that include OpenAssetIO as a
            # subproject may wish to run against the build tree.
            SKIP_BUILD_RPATH FALSE
            BUILD_WITH_INSTALL_RPATH FALSE
            # Whether to add hardcoded directories to final runtime
            # search path.
            INSTALL_RPATH_USE_LINK_PATH FALSE
            # Runtime search path value
            INSTALL_RPATH "${rpath}"
            # Enable RPATH on OSX
            # TODO(TC): this produces seemingly innocuous
            # install_name_tool errors during re-builds when it attempts
            # to set the rpath in a previously installed target that
            # hasn't changed.
            MACOSX_RPATH TRUE
        )
    endif ()

    # CentOS 7 and below (i.e. VFX reference platform) compile gcc to
    # only set RPATH by default, whereas other Linux distros set RUNPATH
    # (if both are set then RPATH is ignored). They each cause different
    # runtime search path behavior. So be explicit to ensure we are
    # consistent across distros.
    if (IS_GCC_OR_CLANG AND NOT APPLE)
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


# Allow a target to re-export symbols from libraries that have been
# statically linked into it.
#
# This is disallowed by default in the above function
# openassetio_set_default_target_properties.
function(openassetio_allow_static_lib_symbol_export target_name)
    # TODO(DF): only works on Linux - see above related TODO(TC).
    if (IS_GCC_OR_CLANG AND NOT APPLE)
        get_target_property(_link_options ${target_name} LINK_OPTIONS)

        # Validate that the link option we're about to remove is
        # actually set.
        list(FIND _link_options ${exclude_all_libs_linker_flag} _option_idx)
        if (_option_idx EQUAL -1)
            message(WARNING
                "Attempting to allow linked static lib symbol exports in ${target_name} when it's"
                " already allowed. Current link options: ${_link_options}")
            return()
        endif ()

        # Remove link option previously set.
        list(REMOVE_ITEM _link_options ${exclude_all_libs_linker_flag})
        set_target_properties(${target_name} PROPERTIES LINK_OPTIONS "${_link_options}")
    endif ()
endfunction()
