#!/bin/sh

rm -rf build/
mkdir -p build/
cd build/
cmake .. -DZ3_DIR=/opt/z3/lib/cmake/z3 -DCMAKE_BUILD_TYPE=Debug
make -j8
