#!/bin/bash

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

rm -f "device_modules/cisco/$1"
mv "device_modules/cisco/xxx.py" "device_modules/cisco/$1"
