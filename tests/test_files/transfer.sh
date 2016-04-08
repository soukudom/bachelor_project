#!/bin/bash

cp "tests/test_files/$1" "device_modules/cisco/$1"
mv "device_modules/cisco/$2" "device_modules/cisco/xxx.py" 
mv "device_modules/cisco/$1" "device_modules/cisco/$2"
