cmake_minimum_required(VERSION 3.14)

project(sygusparser)

find_package(BISON REQUIRED)
find_package(FLEX REQUIRED)

bison_target(sygusparser sygusparser.y sygusparser.y.cc
    DEFINES_FILE sygusparser.y.hh)

flex_target(sygusparser sygusparser.l ${CMAKE_BINARY_DIR}/sygusparser.l.cc)

include_directories(sygusparser ${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR})

add_executable(sygusparser
    ${BISON_sygusparser_OUTPUTS}
    ${FLEX_sygusparser_OUTPUTS}
    main.cc
    tree.h
    sygusparser_lexer.hh
    )
