#!/usr/bin/env python3
from modules.connect import SNMP
import re

class Device:
    def __init__(self):
        pass

    def getDeviceName(self,ip_address,community,additional):
        #value = "sysDescr"
        #manufactor = snmp()._snmpGet(ip_address, community,value)
        #if manufactor  == None:
        #    print("device does not exist")
        #    return False

        #manufactor = manufactor.split()
        ##najdi vezi
        #for pos,i in enumerate(manufactor,start=0):
        #    if re.match("C[0-9][0-9][0-9][0-9]",i):
        #        return ["cisco","cisco"+str(i)]


        value = "sysDescr"
        obj = SNMP()
        try:
            conn = obj.connect(ip_address,community,None)
        except Exception as e:
            print(e)
            return None
        try:       
            manufactor = obj.doCommand(value,additional); 
        except Exception as e:
            print(e)
            return None
        #if manufactor == False:
        #    print("snmp problem")
        #    return False

        manufactor = manufactor.split()
        #najdi verzi
        for pos,i in enumerate(manufactor,start=0):
            if re.match("C[0-9][0-9][0-9][0-9]",i):
                return ["cisco","cisco"+str(i)]
    
