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
    return_codes["test1"] = "OK"
else:
    return_codes["test1"] = "FAIL"

