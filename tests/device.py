#!/usr/bin/env python3

import subprocess
import signal
import sys

return_codes = []

def printResult():
    for i in return_codes:
        if i[1] == "OK":
            print(i[0],":","\033[32m{}\033[0m".format(i[1]))
        else:
            print(i[0],":","\033[31m{}\033[0m".format(i[1]))

def signal_int(signal, frame):
    print("\033[91m\033[1mInterupted\033[0m")
    sys.exit(3)

signal.signal(signal.SIGINT, signal_int)

#device test 1: tests sequece abbreviation in octet
print("\n\n\033[1mTest 1: Abbreviation test in octet\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts2.yml','-c','sin','-l','log.txt','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])

#device test 2: vendor name mismatch
print("\n\n\033[1mTest 2: Vendor name mismatch\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts3.yml','-c','sin','-l','log.txt','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 4:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#device test 3: bad group name
print("\n\n\033[1mTest 3: Group name mismatch\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts4.yml','-c','sin','-l','log.txt','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 1:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test4","FAIL"])


#device test 4: unknow vendor name
print("\n\n\033[1mTest 4: Unknown vendor name\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts5.yml','-c','sin','-l','log.txt','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 4:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])



printResult()
