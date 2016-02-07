#!/usr/bin/env python3
from modules.connect import snmp
import re

class Device:
    def __init__(self):
        pass

    def getDeviceName(self,ip_address,community):
        value = "sysDescr"
        manufactor = snmp()._snmpGet(ip_address, community,value)
        if manufactor  == None:
            print("device does not exist")
            return False

        manufactor = manufactor.split()
        #najdi vezi
        for pos,i in enumerate(manufactor,start=0):
            if str(i).lower() == "software":
                return ["_3com","_3com"+str(manufactor[pos-2])]
