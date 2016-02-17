#!/usr/bin/env python3
from modules.connect import SNMP
import re

class Device:
    def __init__(self):
        pass

    def getDeviceName(self,protocol):
        value = ["sysDescr"]
        obj = SNMP(protocol)
        try:
            conn = obj.connect()
        except Exception as e:
            print(e)
            return None
        try:       
            manufactor = obj.doCommand(value); 
        except Exception as e:
            print("vyjimka")
            print(e)
            return None

        manufactor = manufactor.split()
        #najdi verzi
        for pos,i in enumerate(manufactor,start=0):
            if re.match("C[0-9][0-9][0-9][0-9]",i):
                return ["cisco","cisco"+str(i)]
    
