#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

from modules.connect import SNMP
import re

class Device:
    def __init__(self):
        pass

    def getDeviceName(self, protocol):
        value = ["sysDescr"]
        obj = SNMP(protocol)
        try:
            conn = obj.connect()
        except Exception as e:
            #can not connect
            print("SNMP device module: can not connect to device")
            return None
        try:
            manufactor = obj.doCommand(value)
        except Exception as e:
            #can not do command
            print("SNMP device module: can not do command")
            return None

        manufactor = manufactor.split()
        #find version
        for pos, i in enumerate(manufactor, start=0):
            if re.match("C[0-9][0-9][0-9][0-9]", i):
                return ["cisco", "cisco" + str(i)]
