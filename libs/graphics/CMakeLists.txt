cmake_minimum_required(VERSION 3.16)
project(UnhingedGraphics VERSION 1.0.0 LANGUAGES C)

# Set C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Build options
option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(ENABLE_SIMD "Enable SIMD optimizations" ON)
option(ENABLE_TESTING "Enable testing" ON)
option(ENABLE_DRM "Enable DRM support" OFF)
option(ENABLE_WAYLAND "Enable Wayland support" OFF)
option(ENABLE_AVX2 "Enable AVX2 optimizations" OFF)
option(ENABLE_NEON "Enable NEON optimizations" OFF)

# Compiler flags
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g -O0 -Wall -Wextra -Wpedantic")
else()
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -DNDEBUG -Wall")
endif()

# Platform-specific flags
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
    if(ENABLE_DRM)
        add_definitions(-DENABLE_DRM=1)
    endif()
    if(ENABLE_WAYLAND)
        add_definitions(-DENABLE_WAYLAND=1)
    endif()
endif()

# SIMD flags
if(ENABLE_SIMD)
    if(ENABLE_AVX2)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mavx2 -mfma")
        add_definitions(-DENABLE_AVX2=1)
    endif()
    if(ENABLE_NEON)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mfpu=neon")
        add_definitions(-DENABLE_NEON=1)
    endif()
endif()

# Include directories
include_directories(include)
include_directories(src)

# Source files
set(CORE_SOURCES
    src/core/memory.c
    src/core/platform.c
    src/core/error.c
)

set(RASTER_SOURCES
    src/raster/primitives.c
    src/raster/line.c
    src/raster/circle.c
    src/raster/polygon.c
)

set(COLOR_SOURCES
    src/color/color_space.c
    src/color/blending.c
    src/color/conversion.c
)

set(TEXT_SOURCES
    src/text/bitmap_font.c
)

set(WINDOW_SOURCES
    src/platform/window.c
)

set(SIMD_SOURCES)
if(ENABLE_SIMD)
    if(ENABLE_AVX2)
        list(APPEND SIMD_SOURCES src/simd/avx2_ops.c)
    endif()
    if(ENABLE_NEON)
        list(APPEND SIMD_SOURCES src/simd/neon_ops.c)
    endif()
endif()

set(PLATFORM_SOURCES)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    list(APPEND PLATFORM_SOURCES src/platform/linux_drm.c)
    # Wayland support not implemented yet
    # if(ENABLE_WAYLAND)
    #     list(APPEND PLATFORM_SOURCES src/platform/wayland.c)
    # endif()
endif()

# All sources
set(ALL_SOURCES
    ${CORE_SOURCES}
    ${RASTER_SOURCES}
    ${COLOR_SOURCES}
    ${TEXT_SOURCES}
    ${WINDOW_SOURCES}
    ${SIMD_SOURCES}
    ${PLATFORM_SOURCES}
)

# Main graphics library
add_library(unhinged_graphics ${ALL_SOURCES})

# Set library properties
set_target_properties(unhinged_graphics PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER "include/unhinged_graphics.h"
)

# Link libraries
target_link_libraries(unhinged_graphics m)  # Math library

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    target_link_libraries(unhinged_graphics pthread)

    # Always link DRM for window support
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(DRM REQUIRED libdrm)
    target_link_libraries(unhinged_graphics ${DRM_LIBRARIES})
    target_include_directories(unhinged_graphics PRIVATE ${DRM_INCLUDE_DIRS})

    if(ENABLE_DRM)
        add_definitions(-DENABLE_DRM=1)
    endif()
endif()

# Install targets
install(TARGETS unhinged_graphics
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)

install(DIRECTORY include/ DESTINATION include
    FILES_MATCHING PATTERN "*.h"
)

# Testing (disabled for now due to missing test files)
# if(ENABLE_TESTING)
#     enable_testing()
#     add_subdirectory(tests)
# endif()

# Examples
add_subdirectory(examples)

# CFFI build script
configure_file(cffi_build.py.in cffi_build.py @ONLY)
