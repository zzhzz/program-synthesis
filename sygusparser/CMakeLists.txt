cmake_minimum_required(VERSION 3.14)

project(sygusparser)

find_package(BISON REQUIRED)
find_package(FLEX REQUIRED)
find_package(Z3 REQUIRED)

bison_target(sygusparser sygusparser.y sygusparser.y.cc
    DEFINES_FILE sygusparser.y.hh)

flex_target(sygusparser sygusparser.l ${CMAKE_BINARY_DIR}/sygusparser.l.cc)

target_include_directories(sygusparser PRIVATE ${Z3_CXX_INCLUDE_DIRS} ${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR})
target_link_libraries(sygusparser PRIVATE ${Z3_LIBRARIES})

add_executable(sygusparser
    ${BISON_sygusparser_OUTPUTS}
    ${FLEX_sygusparser_OUTPUTS}
    main.cc
    tree.h
    sygusparser_lexer.hh
    )
