#!/bin/bash

echo "Press 'y' to run configuration file syntax test"
read line
if [ $line = "y" ]
then
    python3 tests/config.py
fi

echo "Press 'y' to run argument test"
read line
if [ $line = "y" ]
then
    python3 tests/arguments.py
fi

echo "Press 'y' to run device file syntax test"
read line
if [ $line = "y" ]
then
    python3 tests/device.py
fi

echo "Press 'y' to run device_modules test"
read line
if [ $line = "y" ]
then
    python3 tests/device_modules.py
fi
