#!/usr/bin/bash

mkdir -p build && cd build
make BR2_EXTERNAL=../config O=$PWD --c ../buildroot raspberrypi3_defconfig
make -j4