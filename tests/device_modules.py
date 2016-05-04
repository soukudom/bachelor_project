#!/usr/bin/env python3

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

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

#device_module test 1: change protocol in one class, other class will continue with defautl protocol
print("\n\n\033[1mTest 1: Change protocol test\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC2960S1.py ciscoC2960S.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic11.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt','-d']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2960S.py",shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])


#device_module test 2: missing compulsory argument self.connection in default class
print("\n\n\033[1mTest 2: Missing compulsory argument\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC2960S2.py ciscoC2960S.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic12.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2960S.py",shell=True)
if ret == 0:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#device_module test 3: protocol name wich is not exists
print("\n\n\033[1mTest 3: Protocol name mismatch\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC2960S3.py ciscoC2960S.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic12.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2960S.py",shell=True)
if ret == 0:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test3","FAIL"])

#device_module test 4: change configuring from auto to others 
print("\n\n\033[1mTest 4: Change connection method\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC29501.py ciscoC2950.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic13.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt',"-pc","2"]
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2950.py",shell=True)
if ret == 0:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])



#device_module test 5: change configuring from manual to others 
print("\n\n\033[1mTest 5: Change connection method  2\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC29502.py ciscoC2950.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic13.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt','-pc','2']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2950.py",shell=True)
if ret == 0:
    return_codes.append(["test5","OK"])
else:
    return_codes.append(["test5","OK"])

#device_module test 6: change configuring from hybrid to others 
print("\n\n\033[1mTest 6: Change connection method 3\033[0m")
subprocess.call("./tests/test_files/transfer.sh ciscoC29503.py ciscoC2950.py",shell=True)
args = ['printf "root\ntoor123\n"','|','./main.py','-cf','tests/test_files/config_basic13.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt','-pc','2']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("./tests/test_files/clean.sh ciscoC2950.py",shell=True)
if ret == 0:
    return_codes.append(["test6","OK"])
else:
    return_codes.append(["test6","FAIL"])


printResult()
