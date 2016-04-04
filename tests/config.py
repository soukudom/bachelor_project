#!/usr/bin/env python3

import subprocess
import signal

return_codes = []

def printResult():
    for i in return_codes:
        if i[1] == "OK":
            print(i[0],":","\033[32m{}\033[0m".format(i[1]))
        else:
            print(i[0],":","\033[31m{}\033[0m".format(i[1]))


def signal_int(signal, frame):
    pass

#syntax test 1: simple interface config without group tag
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])

#syntax test 2: simple interface config with group tag with simple name
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic2.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#syntax test 3: simple interface config with group tag with name
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test3","FAIL"])

#syntax test 4: simple interface config with group tag without name
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic4.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 1:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])

#syntax test 5: simple config with more methods and with submethod
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic5.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test5","OK"])
else:
    return_codes.append(["test5","FAIL"])

#syntax test 6: test abbreviated values in id tag
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic6.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test6","OK"])
else:
    return_codes.append(["test6","FAIL"])


#syntax test 7: test abbreviated values in method name tag
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic7.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test7","OK"])
else:
    return_codes.append(["test7","FAIL"])
printResult()

#syntax test 8: test yaml indention 
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic8.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test8","OK"])
else:
    return_codes.append(["test8","FAIL"])

