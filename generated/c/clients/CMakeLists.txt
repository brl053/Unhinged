# Generated CMakeLists.txt for Unhinged Proto Clients (C++)
cmake_minimum_required(VERSION 3.16)
project(unhinged-proto-clients VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

# Include directories
include_directories(include)

# Collect all source files
file(GLOB_RECURSE PROTO_SOURCES "src/*.cc")
file(GLOB_RECURSE PROTO_HEADERS "include/*.h")

# Create library
add_library(unhinged-proto-clients STATIC ${PROTO_SOURCES})

# Link libraries
target_link_libraries(unhinged-proto-clients
    protobuf::libprotobuf
    gRPC::grpc++
    gRPC::grpc++_reflection
)

# Set include directories for consumers
target_include_directories(unhinged-proto-clients PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Installation
install(TARGETS unhinged-proto-clients
    EXPORT unhinged-proto-clients-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)

install(EXPORT unhinged-proto-clients-targets
    FILE unhinged-proto-clients-config.cmake
    DESTINATION lib/cmake/unhinged-proto-clients
)

# Create example usage
add_executable(proto-client-example examples/example.cpp)
target_link_libraries(proto-client-example unhinged-proto-clients)
