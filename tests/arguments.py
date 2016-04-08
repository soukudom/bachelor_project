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

#argument test 1: tests log filename creation
print("\n\n\033[1mTest 1: Log filename test\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])

#argument test 2: tests log name creation second time
print("\n\n\033[1mTest 2: Log filename test 2\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#argument test 3: tests process count
print("\n\n\033[1mTest 3: Process count test\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts.yml','-c','sin','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test3","FAIL"])

#argument test 4: tests file permission
print("\n\n\033[1mTest 4: File permission test\033[0m")
subprocess.call("chmod 000 tests/test_files/config_basic9.yml",shell=True)
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic9.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
subprocess.call("chmod 644 tests/test_files/config_basic9.yml",shell=True)
if ret == 2:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])

#argument test 5: test file permission
print("\n\n\033[1mTest 5: File permission test 2\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basicX.yml','-df','tests/test_files/hosts.yml','-c','sin','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test5","OK"])
else:
    return_codes.append(["test5","FAIL"])

#argument test 6: configration test with settings file and in debug mode
print("\n\n\033[1mTest 6: Settings file test with debug mode\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-sf','tests/test_files/settings.yml','-d']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test6","OK"])
else:
    return_codes.append(["test6","FAIL"])

#argument test 7: settings file bad name of configure files
print("\n\n\033[1mTest 7: Settings file mistake\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-sf','tests/test_files/settingsBad.yml']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test7","OK"])
else:
    return_codes.append(["test7","FAIL"])


#argument test 8: bad community string
print("\n\n\033[1mTest 8: Bad community string\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts.yml','-c','dej','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 4:
    return_codes.append(["test8","OK"])
else:
    return_codes.append(["test8","FAIL"])

#argument test 9: partial config
print("\n\n\033[1mTest 9: Partial argument test\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic14.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt','-p','cisco']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test9","OK"])
else:
    return_codes.append(["test9","FAIL"])


#argument test 10: bad partial config
print("\n\n\033[1mTest 10: Partial bad argument test\033[0m")
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic14.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt','-p','XXX']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 4:
    return_codes.append(["test10","OK"])
else:
    return_codes.append(["test10","FAIL"])

subprocess.call("rm -f log00*",shell=True)


printResult()
