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

#syntax test 1: test log name creation
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test1","OK"])
else:
    return_codes.append(["test1","FAIL"])

#syntax test 2: test log name creation second time
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic3.yml','-df','tests/test_files/hosts.yml','-c','sin']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test2","OK"])
else:
    return_codes.append(["test2","FAIL"])

#syntax test 3: test process count
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic.yml','-df','tests/test_files/hosts.yml','-c','sin','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test3","OK"])
else:
    return_codes.append(["test3","FAIL"])

#syntax test 4: test file permission
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basic9.yml','-df','tests/test_files/hosts.yml','-c','sin','-l','log.txt']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test4","OK"])
else:
    return_codes.append(["test4","FAIL"])

#syntax test 5: test file permission
args = ['printf "root\nMazohi10\n"','|','./main.py','-cf','tests/test_files/config_basicX.yml','-df','tests/test_files/hosts.yml','-c','sin','-pc','10']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test5","OK"])
else:
    return_codes.append(["test5","FAIL"])

#syntax test 6: configration test with settings file and in debug mode
args = ['printf "root\nMazohi10\n"','|','./main.py','-sf','tests/test_files/settings.yml','-d']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 0:
    return_codes.append(["test6","OK"])
else:
    return_codes.append(["test6","FAIL"])

#syntax test 7: settings file bad name of configure files
args = ['printf "root\nMazohi10\n"','|','./main.py','-sf','tests/test_files/settingsBad.yml']
ret = subprocess.call(' '.join(args),shell=True)
if ret == 2:
    return_codes.append(["test7","OK"])
else:
    return_codes.append(["test7","FAIL"])

printResult()
