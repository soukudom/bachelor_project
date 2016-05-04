#!/usr/bin/env python3

################################################
# Author: Dominik Soukup, soukudom@fit.cvut.cz #
################################################

import device_modules.cisco.ciscoC2950 as c
from lxml import etree

class DefaultConnection:
    def __init__(self):
        self.method = "NETCONF"
        self.connection = "auto"

def makeNetconf(commands):
    root = etree.Element("edit-config")
    child = etree.SubElement(root,"target")
    etree.SubElement(child,"running")
    child2 = etree.SubElement(root,"config")
    child21 = etree.SubElement(child2,"cli-config-data")
    for cmd in commands:
        if cmd == "configure terminal" or cmd == "end":
            continue
        child211 = etree.SubElement(child21,"cmd")
        child211.text = cmd

    res = (etree.tostring(root,encoding="utf-8").decode("utf-8"))
    return res


class vlan:
    def __init__(self):
        self.method = "NETCONF"

    def vlan(self,id="",description="",ip="",shutdown=""):
        self.result = ""
        return self.result 

class interface:
    def __init__(self):
        self.method = "NETCONF"
    
    def int(self, id="", description = "", shutdown="",):
        obj = c.interface()
        result = obj.int(id,description,shutdown)
        result = makeNetconf(result)
        return result

    
    def int_vlan(self,id="",mode="",allowed="", access=""):
        self.result = ""
        return self.result 
    
    def int_agregate(self,id="",protocol="",channel="",mode=""):
        self.result = ""
        return self.result 

    def default(self, id="", shutdown="", description=""):
        self.result = ""
        return self.result 
    
    def default_vlan(self,id="", mode="", access="", allowed=""):
        self.result = ""
        return self.result 

    def mac(self, id="", description = "", shutdown=""):
        self.result = ""
        return self.result 
    
    def mac_vlan(self, id="", mode="", allowed="", access=""):
        self.result = ""
        return self.result 

    def mac_agregate(self,id="",protocol="",channel="", mode=""):
        self.result = ""
        return self.result 
