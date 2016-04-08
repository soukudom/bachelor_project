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

#syntax test 1: simple interface config without group tag
print("\n\n\033[1mTest 1: Simple interface configuration\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])

#syntax test 2: simple interface config with group tag with simple name
print("\n\n\033[1mTest 2: Simple interface configuration with tag\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic2.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#syntax test 3: simple interface config with group tag with name
print("\n\n\033[1mTest 3: Simple interface configuration with composite tag\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test3","FAIL"])

#syntax test 4: simple interface config with group tag without name
print("\n\n\033[1mTest 4: Simple interface configuration with missing name\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic4.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 1:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])

#syntax test 5: simple config with more methods and with submethod
print("\n\n\033[1mTest 5: Composite interface configuration with submethod\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic5.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test5","OK"])
else:
    return_codes.append(["test5","FAIL"])

#syntax test 6: tests abbreviated values in id tag
print("\n\n\033[1mTest 6: Abbreviation test in id\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic6.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test6","OK"])
else:
    return_codes.append(["test6","FAIL"])


#syntax test 7: tests abbreviated values in method name tag
print("\n\n\033[1mTest 7: Abbreviation test in tag\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic7.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test7","OK"])
else:
    return_codes.append(["test7","FAIL"])

#syntax test 8: tests yaml indention 
print("\n\n\033[1mTest 8: YAML test\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic8.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test8","OK"])
else:
    return_codes.append(["test8","FAIL"])

#syntax test 9: tests abbreviated value in name key 
print("\n\n\033[1mTest 9: Abbreviation test in name\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic10.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test9","OK"])
else:
    return_codes.append(["test9","FAIL"])



printResult()
