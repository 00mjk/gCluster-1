cmake_minimum_required(VERSION 3.0)

project (grid-clustering)

set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_CXX_FLAGS "-std=c++11 -g")

#Bring headers
include_directories(include csv-reader point graphs)

#Define sources
file(GLOB SOURCES "src/*.cpp" "csv-reader/*.cpp" "point/*.cpp" "graphs/*.cpp")

add_executable(gcluster ${SOURCES})
