"""
This script is used by the Notebook to get (and build) dependencies,
i.e.
- OpenAssetIO
- OpenAssetIO-MediaCreation (+ OpenAssetIO-TraitGen)
- OpenAssetIO-Manager-BAL

The script is initiated in a `tox`-configured virtual environment - see
tox.ini - which is itself initiated by the Notebook running in a Conda
environment.

TODO(DF): This is fairly self-contained, but not scalable, and not
 suitable for CI, since it clones and builds the current `main` of
 OpenAssetIO.  More thought needed here.
"""

import os
import subprocess
import pathlib
import sys
import tempfile


def main():

    test_path = pathlib.Path(sys.prefix) / "include" / "openassetio_mediacreation"
    if test_path.exists():
        print(f"Dependencies already installed. Remove {sys.prefix} to force a reinstall")
        return

    print(f"Installing dependencies to {sys.prefix}")

    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    print(f"Placing temporary artifacts in {tmp_dir}")

    deps_dir = tmp_dir / "deps"
    deps_dir.mkdir(exist_ok=True)

    openassetio_dir = deps_dir / "openassetio"
    openassetio_dir.mkdir(exist_ok=True)
    openasssetio_conan_dir = openassetio_dir / "conan"
    openasssetio_conan_dir.mkdir(exist_ok=True)

    print(f"Placing Conan packages in {openasssetio_conan_dir}")

    mediacreation_dir = deps_dir / "mediacreation"
    mediacreation_dir.mkdir(exist_ok=True)

    env = os.environ.copy()

    # Work around Conan not understanding the default symlink for the compiler in Conda env.
    env["CC"] = pathlib.Path(env["CC"]).resolve().as_posix()
    env["CXX"] = pathlib.Path(env["CXX"]).resolve().as_posix()

    env["CONAN_USER_HOME"] = openasssetio_conan_dir.as_posix()
    env["CMAKE_PREFIX_PATH"] = openasssetio_conan_dir.as_posix()
    env["OPENASSETIO_CONAN_SKIP_CPYTHON"] = "1"

    # OpenAssetIO

    subprocess.check_call(
        ["git", "clone", "https://github.com/OpenAssetIO/OpenAssetIO.git", "src"],
        cwd=openassetio_dir,
        env=env,
    )

    subprocess.check_call(
        [
            "conan",
            "install",
            "-if",
            openasssetio_conan_dir.as_posix(),
            "src/resources/build",
        ],
        cwd=openassetio_dir,
        env=env,
    )
    subprocess.check_call(
        [
            "cmake",
            "-S",
            "src",
            "-B",
            "build",
            "--install-prefix",
            sys.prefix,
            "-DOPENASSETIO_GLIBCXX_USE_CXX11_ABI=ON",  # TODO(DF): Possibly not necessary
            # f"-DPython_EXECUTABLE={sys.executable}",  # TODO(DF): Possibly not necessary
        ],
        cwd=openassetio_dir,
        env=env,
    )
    subprocess.check_call(
        ["cmake", "--build", "build", "--config", "Release", "--parallel"],
        cwd=openassetio_dir,
        env=env,
    )
    subprocess.check_call(
        ["cmake", "--install", "build", "--config", "Release"], cwd=openassetio_dir, env=env
    )

    # MediaCreation

    subprocess.check_call(
        [
            "git",
            "clone",
            "https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation.git",
            "src",
        ],
        cwd=mediacreation_dir,
        env=env,
    )

    subprocess.check_call(
        [
            "cmake",
            "-S",
            "src",
            "-B",
            "build",
            "-G",
            "Ninja",
            "--install-prefix",
            sys.prefix,
        ],
        cwd=mediacreation_dir,
        env=env,
    )
    subprocess.check_call(
        ["cmake", "--build", "build", "--parallel", "--config", "Release"],
        cwd=mediacreation_dir,
        env=env,
    )
    subprocess.check_call(
        ["cmake", "--install", "build", "--config", "Release"],
        cwd=mediacreation_dir,
        env=env,
    )


if __name__ == "__main__":
    main()
