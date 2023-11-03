@echo off
:: Install additional build tools.
pip3 install -r "%WORKSPACE%\resources\build\requirements.txt"
:: Use explicit predictable conan root path, where packages are cached.
set CONAN_HOME=%USERPROFILE%\conan
:: Install openassetio third-party dependencies from public Conan Center
:: package repo.
conan install ^
 --output-folder "%WORKSPACE%\.conan" ^
 --profile:host resources/build/vfx22.profile ^
 --profile:build resources/build/vfx22.profile ^
 "%WORKSPACE%\resources\build"
