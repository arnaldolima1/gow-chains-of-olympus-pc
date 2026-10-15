cmake_minimum_required(VERSION 3.20)
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" OLYMPUS_VERSION LIMIT_COUNT 1)
# C too: the SDL3 package for Visual Studio test-compiles a .c file to detect
# the target CPU.
project(Olympus VERSION ${OLYMPUS_VERSION} LANGUAGES C CXX)

# PortableKit brings the recompiler, the runtime and the system layer, and
# defines portablekit_add_game().
add_subdirectory(portablekit)

# The disc keeps no PGD data, so the framework's built-in keys are all the
# game needs.
portablekit_add_game(OlympusNative
    PROFILE_DIR "${CMAKE_CURRENT_SOURCE_DIR}"
    SOURCES host/olympus_profile.cpp)
